from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
import operator
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from src.guardrails.content_guard import ContentGuard, RiskLevel
from src.hitl.review_manager import ReviewManager
from src.core.config import settings



from src.agents.tools import (
    EmailTools,
    SearchTools,
    CalendarTools,
    FileTools,
)

# State definition
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    email_data: Dict[str, Any]
    context: Dict[str, Any]
    next_step: str
    metadata: Dict[str, Any]
    # Guardrail & HITL fields
    guardrail_result: Optional[Dict[str, Any]]   # Output of ContentGuard.check()
    requires_human_review: bool                   # True when HITL is needed
    review_status: Optional[str]                  # pending / approved / rejected
    review_id: Optional[str]                      # ID in hitl_reviews table

class EmailAssistantAgent:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.guard = ContentGuard(
            confidence_threshold=getattr(settings, "GUARDRAIL_CONFIDENCE_THRESHOLD", 0.6),
            max_draft_length=getattr(settings, "GUARDRAIL_MAX_DRAFT_LENGTH", 5000),
            auto_block_keywords=getattr(settings, "GUARDRAIL_AUTO_BLOCK_KEYWORDS", []),
            auto_approve_risk=RiskLevel(
                getattr(settings, "HITL_AUTO_APPROVE_RISK", "low")
            ),
        )
        self.review_manager = ReviewManager(
            db_path=getattr(settings, "database_url", "./email_assistant.db").replace(
                "sqlite:///", ""
            )
        )
        self.agent = self._build_agent_graph()
        
    def _initialize_llm(self):
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1,
            streaming=True
        )
    
    def _initialize_tools(self):
        return [
            EmailTools.send_email,
            EmailTools.draft_email,
            EmailTools.get_unread_emails,
            EmailTools.search_emails,
            SearchTools.web_search,
            SearchTools.internal_knowledge_search,
            CalendarTools.check_availability,
            CalendarTools.schedule_meeting,
            FileTools.read_attachment,
            FileTools.save_draft,
        ]
    
    def _build_agent_graph(self):
        """Build the LangGraph workflow with guardrail and HITL nodes."""
        workflow = StateGraph(AgentState)

        # Core nodes
        workflow.add_node("analyze_email", self._analyze_email)
        workflow.add_node("gather_context", self._gather_context)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("execute_actions", self._execute_actions)
        workflow.add_node("review_and_finalize", self._review_and_finalize)

        # Safety nodes (new)
        workflow.add_node("guardrail_check", self._guardrail_check)
        workflow.add_node("human_review_gate", self._human_review_gate)

        # Entry point
        workflow.set_entry_point("analyze_email")

        # analyze → gather_context
        workflow.add_edge("analyze_email", "gather_context")

        # gather_context → execute_actions OR generate_response
        workflow.add_conditional_edges(
            "gather_context",
            self._should_execute_actions,
            {
                "execute": "execute_actions",
                "respond": "generate_response",
            },
        )

        # execute_actions → generate_response
        workflow.add_edge("execute_actions", "generate_response")

        # generate_response → guardrail_check → human_review_gate
        workflow.add_edge("generate_response", "guardrail_check")
        workflow.add_edge("guardrail_check", "human_review_gate")

        # human_review_gate → review_and_finalize OR END (awaiting review)
        workflow.add_conditional_edges(
            "human_review_gate",
            self._should_proceed_after_review,
            {
                "proceed": "review_and_finalize",
                "halt": END,
            },
        )

        workflow.add_edge("review_and_finalize", END)

        return workflow.compile()
    
    def _analyze_email(self, state: AgentState) -> AgentState:
        """Analyze incoming email to determine intent and priority"""
        messages = state["messages"]
        email_data = state["email_data"]
        
        system_prompt = """You are an expert email analyst. Analyze the email to determine:
        1. Intent (question, request, complaint, scheduling, etc.)
        2. Urgency (low, medium, high, critical)
        3. Required actions
        4. Context needed for response
        5. Suggested response type"""
        
        analysis_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze this email:\n\nSubject: {email_data.get('subject')}\n\nBody: {email_data.get('body')}")
        ])
        
        chain = analysis_prompt | self.llm
        analysis = chain.invoke({})
        
        state["metadata"]["analysis"] = analysis.content
        state["next_step"] = "gather_context"
        
        return state
    
    def _gather_context(self, state: AgentState) -> AgentState:
        """Gather additional context using all relevant tools."""
        email_data = state["email_data"]
        query = (email_data.get("subject", "") + " " + email_data.get("body", "")).strip() or "email context"
        analysis = state["metadata"].get("analysis", "").lower()

        # 1. Internal knowledge search
        try:
            state["context"]["search_results"] = internal_knowledge_search.invoke({
                "query": query,
                "max_results": 5,
            })
        except Exception as e:
            state["context"]["search_results"] = [{"error": str(e)}]

        # 2. Web search (when we need external info)
        if self._needs_external_info(state):
            try:
                state["context"]["web_search"] = web_search.invoke({
                    "query": query,
                    "max_results": 5,
                })
            except Exception as e:
                state["context"]["web_search"] = [{"error": str(e)}]

        # 3. Calendar availability (if meeting/scheduling mentioned)
        if "meeting" in analysis or "schedule" in analysis:
            try:
                state["context"]["availability"] = check_availability.invoke({
                    "duration": 60,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
            except Exception as e:
                state["context"]["availability"] = [{"error": str(e)}]

        # 4. Unread emails (inbox context)
        try:
            state["context"]["unread_emails"] = get_unread_emails.invoke({
                "limit": 5,
                "folder": "inbox",
            })
        except Exception as e:
            state["context"]["unread_emails"] = []

        # 5. Search emails
        try:
            state["context"]["email_search"] = search_emails.invoke({
                "query": query,
                "limit": 5,
            })
        except Exception as e:
            state["context"]["email_search"] = []

        # 6. Read attachments if paths provided
        attachments = email_data.get("attachments") or []
        if isinstance(attachments, list):
            attachment_contents = []
            for att in attachments:
                path = att.get("path") or att.get("file_path") if isinstance(att, dict) else att
                if isinstance(path, str):
                    try:
                        content = read_attachment.invoke({"file_path": path})
                        attachment_contents.append({"path": path, "content_preview": (content or "")[:500]})
                    except Exception as e:
                        attachment_contents.append({"path": path, "error": str(e)})
            if attachment_contents:
                state["context"]["attachment_contents"] = attachment_contents

        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate email response using gathered context (including tool outputs)."""
        messages = state["messages"]
        email_data = state["email_data"]
        context = state["context"]
        draft_guidance = context.get("draft_prompt") or ""

        response_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a professional email assistant. Write a clear, concise, and appropriate response."),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content=f"""
            Original Email:
            Subject: {email_data.get('subject')}
            From: {email_data.get('from_email', email_data.get('from', ''))}
            Body: {email_data.get('body')}

            Gathered context (search, calendar, attachments, etc.): {context}

            {f"Draft guidance from preparation: {draft_guidance}" if draft_guidance else ""}

            Write a response that addresses all points in the original email.
            """)
        ])

        chain = response_prompt | self.llm
        response = chain.invoke({"chat_history": messages})

        state["metadata"]["draft_response"] = response.content
        return state
    
    def _execute_actions(self, state: AgentState) -> AgentState:
        """Execute required actions using tools: schedule_meeting, draft_email."""
        email_data = state["email_data"]
        analysis = state["metadata"].get("analysis", "") or ""
        actions_taken = state["metadata"].get("actions", []) or []

        # Schedule meeting if analysis suggests it
        if any(kw in analysis.lower() for kw in ["schedule", "meeting", "book", "calendar"]):
            try:
                to_emails = email_data.get("to_emails") or ["recipient@example.com"]
                recipient = to_emails[0] if to_emails else "recipient@example.com"
                schedule_result = schedule_meeting.invoke({
                    "attendees": to_emails if isinstance(to_emails, list) else [recipient],
                    "subject": email_data.get("subject", "Meeting"),
                    "duration": 60,
                    "preferred_times": [datetime.now().strftime("%Y-%m-%dT%H:00")],
                })
                actions_taken.append({"tool": "schedule_meeting", "result": schedule_result})
            except Exception as e:
                actions_taken.append({"tool": "schedule_meeting", "error": str(e)})

        # Draft email (key points from analysis) for later use in generate_response
        try:
            to_emails = email_data.get("to_emails") or ["recipient@example.com"]
            recipient = to_emails[0] if to_emails else "recipient@example.com"
            key_points = [
                "Acknowledge the email",
                "Address the main request or question",
                "Provide clear next steps if needed",
            ]
            draft_prompt = draft_email.invoke({
                "recipient": recipient,
                "subject": email_data.get("subject", "Reply"),
                "key_points": key_points,
                "tone": "professional",
            })
            state["context"]["draft_prompt"] = draft_prompt
        except Exception as e:
            state["context"]["draft_prompt"] = f"Draft preparation note: {e}"

        state["metadata"]["actions"] = actions_taken
        return state
    
    def _review_and_finalize(self, state: AgentState) -> AgentState:
        """Review and finalize; save draft via save_draft; optionally send via send_email."""
        email_data = state["email_data"]
        draft = state["metadata"].get("draft_response") or ""
        actions_taken = state["metadata"].get("actions", []) or []

        # Save draft using save_draft tool
        if draft.strip():
            try:
                save_result = save_draft.invoke({
                    "content": draft,
                    "metadata": {
                        "subject": email_data.get("subject"),
                        "to_emails": email_data.get("to_emails"),
                        "from_email": email_data.get("from_email"),
                    },
                })
                actions_taken.append({"tool": "save_draft", "result": save_result})
            except Exception as e:
                actions_taken.append({"tool": "save_draft", "error": str(e)})

        # Optionally send email when request has auto_send (e.g. from API/UI)
        if email_data.get("auto_send") and draft.strip():
            to_list = email_data.get("to_emails") or []
            if to_list and email_data.get("from_email"):
                try:
                    send_result = send_email.invoke({
                        "to": to_list if isinstance(to_list, list) else [to_list],
                        "subject": email_data.get("subject", "Reply"),
                        "body": draft,
                        "cc": email_data.get("cc_emails") or None,
                    })
                    actions_taken.append({"tool": "send_email", "result": send_result})
                except Exception as e:
                    actions_taken.append({"tool": "send_email", "error": str(e)})

        state["metadata"]["actions"] = actions_taken
        return state
    
    def _guardrail_check(self, state: AgentState) -> AgentState:
        """Run ContentGuard on the generated draft and annotate state."""
        draft = state["metadata"].get("draft_response", "")
        confidence = float(state["metadata"].get("confidence_score", 1.0))

        result = self.guard.check(
            draft=draft,
            confidence_score=confidence,
            original_email=state.get("email_data"),
        )

        state["guardrail_result"] = {
            "passed": result.passed,
            "violations": result.violations,
            "risk_level": result.risk_level.value,
            "requires_human_review": result.requires_human_review,
            "details": result.details,
        }
        state["requires_human_review"] = result.requires_human_review

        if result.violations:
            logger.warning(
                f"Guardrail violations detected [{result.risk_level.value}]: "
                f"{result.violations}"
            )
        else:
            logger.info("Guardrail check passed — no violations.")

        return state

    def _human_review_gate(self, state: AgentState) -> AgentState:
        """If review is required, create a review record and halt execution."""
        if not state.get("requires_human_review"):
            # All clear — no review needed.
            state["review_status"] = None
            state["review_id"] = None
            return state

        draft = state["metadata"].get("draft_response", "")
        gr = state.get("guardrail_result", {})

        review_id = self.review_manager.create_review(
            email_data=state["email_data"],
            draft=draft,
            violations=gr.get("violations", []),
            risk_level=gr.get("risk_level", "medium"),
        )

        state["review_id"] = review_id
        state["review_status"] = "pending"
        state["metadata"]["review_id"] = review_id

        logger.info(
            f"Email draft queued for human review (review_id={review_id}, "
            f"risk={gr.get('risk_level')})"
        )
        return state

    def _should_proceed_after_review(self, state: AgentState) -> str:
        """Routing: proceed to finalize if no human review needed, else halt."""
        if state.get("requires_human_review"):
            return "halt"
        return "proceed"

    def _should_execute_actions(self, state: AgentState) -> str:
        """Determine if actions need to be executed before responding."""
        analysis = state["metadata"].get("analysis", "")
        if any(action in analysis.lower() for action in ["schedule", "confirm", "book", "send"]):
            return "execute"
        return "respond"
    
    def _needs_external_info(self, state: AgentState) -> bool:
        """Check if external information is needed"""
        analysis = state["metadata"].get("analysis", "")
        # Simple heuristic - can be enhanced
        question_words = ["what", "when", "where", "who", "why", "how", "?"]
        return any(word in analysis.lower() for word in question_words)
    
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for processing an email."""
        initial_state: AgentState = {
            "messages": [],
            "email_data": email_data,
            "context": {},
            "next_step": "analyze",
            "metadata": {},
            # Guardrail / HITL defaults
            "guardrail_result": None,
            "requires_human_review": False,
            "review_status": None,
            "review_id": None,
        }

        # Execute the agent graph
        result = await self.agent.ainvoke(initial_state)

        return {
            "response": result["metadata"].get("draft_response"),
            "actions_taken": result["metadata"].get("actions", []),
            "analysis": result["metadata"].get("analysis"),
            "context_used": result["context"],
            # Guardrail / HITL metadata
            "guardrail_result": result.get("guardrail_result"),
            "requires_human_review": result.get("requires_human_review", False),
            "review_id": result.get("review_id"),
            "review_status": result.get("review_status"),
        }


# Export a module-level graph instance for LangGraph dev server
email_graph = EmailAssistantAgent()._build_agent_graph()