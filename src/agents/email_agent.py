from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
import operator
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()



from src.agents.tools import (
    send_email,
    draft_email,
    get_unread_emails,
    search_emails,
    web_search,
    internal_knowledge_search,
    check_availability,
    schedule_meeting,
    read_attachment,
    save_draft,
)

# State definition
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    email_data: Dict[str, Any]
    context: Dict[str, Any]
    next_step: str
    metadata: Dict[str, Any]

class EmailAssistantAgent:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.agent = self._build_agent_graph()
        
    def _initialize_llm(self):
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1,
            streaming=True
        )
    
    def _initialize_tools(self):
        return [
            send_email,
            draft_email,
            get_unread_emails,
            search_emails,
            web_search,
            internal_knowledge_search,
            check_availability,
            schedule_meeting,
            read_attachment,
            save_draft,
        ]
    
    def _build_agent_graph(self):
        # Define nodes
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_email", self._analyze_email)
        workflow.add_node("gather_context", self._gather_context)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("execute_actions", self._execute_actions)
        workflow.add_node("review_and_finalize", self._review_and_finalize)
        
        # Define edges
        workflow.set_entry_point("analyze_email")
        workflow.add_edge("analyze_email", "gather_context")
        workflow.add_conditional_edges(
            "gather_context",
            self._should_execute_actions,
            {
                "execute": "execute_actions",
                "respond": "generate_response"
            }
        )
        workflow.add_edge("execute_actions", "generate_response")
        workflow.add_edge("generate_response", "review_and_finalize")
        workflow.add_edge("review_and_finalize", END)
        
        # Compile graph
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
    
    def _should_execute_actions(self, state: AgentState) -> str:
        """Determine if actions need to be executed before responding"""
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
        """Main entry point for processing an email"""
        initial_state: AgentState = {
            "messages": [],
            "email_data": email_data,
            "context": {},
            "next_step": "analyze",
            "metadata": {}
        }
        
        # Execute the agent graph
        result = await self.agent.ainvoke(initial_state)
        
        return {
            "response": result["metadata"].get("draft_response"),
            "actions_taken": result["metadata"].get("actions", []),
            "analysis": result["metadata"].get("analysis"),
            "context_used": result["context"]
        }


# Export a module-level graph instance for LangGraph dev server
email_graph = EmailAssistantAgent()._build_agent_graph()