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
        """Gather additional context needed for response"""
        messages = state["messages"]
        email_data = state["email_data"]
        
        # Check if we need external information
        if self._needs_external_info(state):
            # Use search tools to gather context
            search_tool = internal_knowledge_search
            search_results = search_tool.invoke({
                "query": email_data.get("subject", "") + " " + email_data.get("body", ""),
                "max_results": 5
            })
            state["context"]["search_results"] = search_results
        
        # Check calendar if scheduling is involved
        if "meeting" in state["metadata"].get("analysis", "").lower():
            calendar_tool = check_availability
            availability = calendar_tool.invoke({
                "duration": 60,
                "date": datetime.now().date()
            })
            state["context"]["availability"] = availability
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate email response using gathered context"""
        messages = state["messages"]
        email_data = state["email_data"]
        context = state["context"]
        
        response_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a professional email assistant. Write a clear, concise, and appropriate response."),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content=f"""
            Original Email:
            Subject: {email_data.get('subject')}
            From: {email_data.get('from')}
            Body: {email_data.get('body')}
            
            Context: {context}
            
            Write a response that addresses all points in the original email.
            """)
        ])
        
        chain = response_prompt | self.llm
        response = chain.invoke({"chat_history": messages})
        
        state["metadata"]["draft_response"] = response.content
        return state
    
    def _execute_actions(self, state: AgentState) -> AgentState:
        """Execute required actions (send emails, schedule meetings, etc.)"""
        # This would execute tools based on analysis
        # For example: send confirmation email, schedule meeting, etc.
        return state
    
    def _review_and_finalize(self, state: AgentState) -> AgentState:
        """Review and finalize the response"""
        # Add final review step before sending
        review_prompt = """Review this email response for:
        1. Tone and professionalism
        2. Completeness
        3. Accuracy
        4. Action items clearly stated
        """
        # Implementation would include final checks
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