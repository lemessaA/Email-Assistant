from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
import operator
from datetime import datetime
from src.core.config import settings

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
        self.agent = self._build_agent_graph()
        
    def _initialize_llm(self):
        # Use Ollama for local LLM
        try:
            return ChatOllama(
                model=settings.PRIMARY_LLM.split("/")[-1],  # Get model name (e.g., "llama2" from "ollama/llama2")
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.1
            )
        except Exception as e:
            # Create a mock LLM for fallback
            class MockLLM:
                def __init__(self):
                    self.model = "mock"
                    self.temperature = 0.1
                
                def invoke(self, input_data):
                    class MockResponse:
                        def __init__(self):
                            self.content = f"This is a mock response. Ollama error: {str(e)}. Please ensure Ollama is running on {settings.OLLAMA_BASE_URL}"
                    return MockResponse()
            
            return MockLLM()
    
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
        # Simple implementation
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
        return state
    
    def _review_and_finalize(self, state: AgentState) -> AgentState:
        """Review and finalize the response"""
        return state
    
    def _should_execute_actions(self, state: AgentState) -> str:
        """Determine if actions need to be executed before responding"""
        analysis = state["metadata"].get("analysis", "")
        email_data = state.get("email_data", {})
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        
        # Check both analysis and original email content for action keywords
        combined_text = f"{analysis} {subject} {body}"
        
        if any(keyword in combined_text for keyword in ["schedule", "meeting", "appointment", "call"]):
            return "execute"
        return "respond"
    
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
