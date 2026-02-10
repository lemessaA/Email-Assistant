"""
Email Agent Graph Module for LangGraph

This module defines the LangGraph workflow for email processing.
It creates a StateGraph with nodes for analyzing, processing,
and responding to emails using LangGraph's state management.
"""

# Import type hints for better code documentation and IDE support
from typing import TypedDict, Annotated, List, Dict, Any
# Import LangGraph components for building state graphs
from langgraph.graph import StateGraph, END
# Import operator for state annotations
import operator
# Import tools for actual functionality
from src.agents.tools import EmailTools, SearchTools, CalendarTools, FileTools
from datetime import datetime

# State definition for LangGraph workflow
class AgentState(TypedDict):
    """State definition for email processing workflow"""
    messages: Annotated[List, operator.add]  # List of messages with append operation
    email_data: Dict[str, Any]  # Email information dictionary
    context: Dict[str, Any]  # Additional context gathered during processing
    next_step: str  # Next step in the workflow
    metadata: Dict[str, Any]  # Metadata storage for analysis results

def analyze_email(state: AgentState) -> AgentState:
    """
    Analyze incoming email to determine intent and priority
    
    Args:
        state: Current workflow state containing email data
        
    Returns:
        Updated state with analysis results
    """
    email_data = state.get("email_data", {})  # Get email data from state, default to empty dict
    
    # Initialize metadata if not present in state
    if "metadata" not in state:
        state["metadata"] = {}  # Create metadata dictionary if it doesn't exist
    
    # Simple analysis for demonstration
    # In production, this would use AI/NLP for sophisticated analysis
    analysis = f"Email analysis for: {email_data.get('subject', 'No subject')}"
    
    # Store analysis results in metadata
    state["metadata"]["analysis"] = analysis  # Save analysis to metadata
    state["next_step"] = "gather_context"  # Set next workflow step
    
    return state  # Return updated state

def gather_context(state: AgentState) -> AgentState:
    """
    Gather additional context needed for response generation
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with gathered context
    """
    # Initialize metadata if not present in state
    if "metadata" not in state:
        state["metadata"] = {}  # Create metadata dictionary if it doesn't exist
    
    email_data = state.get("email_data", {})
    
    # Initialize search tools
    search_tools = SearchTools()
    
    # Extract key terms from email for context gathering
    subject = email_data.get('subject', '')
    body = email_data.get('body', '')
    
    # Search for relevant context based on email content
    context_data = {}
    
    try:
        # Internal knowledge base search
        internal_results = search_tools.internal_knowledge_search(
            query=subject + " " + body[:100],  # Use subject and first 100 chars of body
            max_results=3
        )
        if internal_results:
            context_data["internal_knowledge"] = internal_results
            
    except Exception as e:
        context_data["internal_knowledge_error"] = str(e)
    
    try:
        # Web search for additional context if needed
        if len(body) > 50:  # Only search for substantial emails
            web_results = search_tools.web_search(
                query=subject,
                max_results=2
            )
            if web_results:
                context_data["web_search"] = web_results
                
    except Exception as e:
        context_data["web_search_error"] = str(e)
    
    # Store gathered context in state
    state["context"] = context_data
    
    return state  # Return updated state

def generate_response(state: AgentState) -> AgentState:
    """
    Generate email response using gathered context and analysis
    
    Args:
        state: Current workflow state with analysis and context
        
    Returns:
        Updated state with generated response
    """
    email_data = state.get("email_data", {})  # Get email data from state, default to empty dict
    
    # Initialize metadata if not present in state
    if "metadata" not in state:
        state["metadata"] = {}  # Create metadata dictionary if it doesn't exist
    
    # Use EmailTools to generate a proper draft
    email_tools = EmailTools()
    
    # Extract key points from email body for better response generation
    email_body = email_data.get('body', '')
    key_points = [email_body] if email_body else ["No specific content provided"]
    
    # Generate email draft using the tool
    draft_prompt = email_tools.draft_email(
        recipient=email_data.get('from_email', 'unknown@example.com'),
        subject=email_data.get('subject', 'No Subject'),
        key_points=key_points,
        tone="professional"
    )
    
    # Store the generated prompt as the response (in production, this would be sent to LLM)
    response = f"Thank you for your email regarding: {email_data.get('subject', 'No subject')}"
    
    # Store generated response in metadata
    state["metadata"]["draft_response"] = response  # Save response to metadata
    state["metadata"]["draft_prompt"] = draft_prompt  # Save the detailed prompt for reference
    
    return state  # Return updated state

def execute_actions(state: AgentState) -> AgentState:
    """
    Execute required actions (send emails, schedule meetings, etc.)
    
    Args:
        state: Current workflow state with analysis results
        
    Returns:
        Updated state with executed actions
    """
    # Initialize metadata if not present in state
    if "metadata" not in state:
        state["metadata"] = {}  # Create metadata dictionary if it doesn't exist
    
    # Initialize actions list
    if "actions" not in state["metadata"]:
        state["metadata"]["actions"] = []
    
    email_data = state.get("email_data", {})
    analysis = state["metadata"].get("analysis", "")
    
    # Initialize tools
    email_tools = EmailTools()
    calendar_tools = CalendarTools()
    search_tools = SearchTools()
    
    # Check if email needs to be sent
    if "send" in analysis.lower() or "reply" in analysis.lower():
        try:
            # Extract recipients from email data
            to_emails = email_data.get('to_emails', [])
            if to_emails:
                # Send the generated response
                send_result = email_tools.send_email(
                    to=to_emails,
                    subject=f"Re: {email_data.get('subject', 'No Subject')}",
                    body=state["metadata"].get("draft_response", "Automated response")
                )
                state["metadata"]["actions"].append({
                    "action": "send_email",
                    "result": send_result,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            state["metadata"]["actions"].append({
                "action": "send_email",
                "result": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    # Check if meeting needs to be scheduled
    if any(keyword in analysis.lower() for keyword in ["schedule", "meeting", "appointment", "call"]):
        try:
            # Check availability
            availability = calendar_tools.check_availability()
            state["metadata"]["actions"].append({
                "action": "check_availability",
                "result": availability,
                "timestamp": datetime.now().isoformat()
            })
            
            # If specific times mentioned, try to schedule
            if "tomorrow" in analysis.lower() or "next week" in analysis.lower():
                meeting_result = calendar_tools.schedule_meeting(
                    attendees=[email_data.get('from_email', '')],
                    subject=email_data.get('subject', 'Meeting Request'),
                    duration=60,
                    preferred_times=["tomorrow 10:00", "tomorrow 14:00"]
                )
                state["metadata"]["actions"].append({
                    "action": "schedule_meeting",
                    "result": meeting_result,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            state["metadata"]["actions"].append({
                "action": "calendar_operations",
                "result": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    # Check if web search is needed for context
    if any(keyword in analysis.lower() for keyword in ["research", "information", "details", "lookup"]):
        try:
            # Extract search terms from email subject/body
            search_query = email_data.get('subject', '')
            search_results = search_tools.web_search(search_query, max_results=3)
            state["metadata"]["actions"].append({
                "action": "web_search",
                "result": search_results,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            state["metadata"]["actions"].append({
                "action": "web_search",
                "result": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    return state  # Return updated state

def review_and_finalize(state: AgentState) -> AgentState:
    """
    Review and finalize the response before sending
    
    Args:
        state: Current workflow state with generated response
        
    Returns:
        Updated state with finalized response
    """
    # Initialize metadata if not present in state
    if "metadata" not in state:
        state["metadata"] = {}  # Create metadata dictionary if it doesn't exist
    
    # Simple implementation - no review process for now
    # In production, this would check for tone, completeness, accuracy, etc.
    return state  # Return unchanged state

def should_execute_actions(state: AgentState) -> str:
    """
    Determine if actions need to be executed before responding
    
    Args:
        state: Current workflow state with analysis results
        
    Returns:
        String indicating next step: "execute" or "respond"
    """
    metadata = state.get("metadata", {})  # Get metadata from state, default to empty dict
    analysis = metadata.get("analysis", "")  # Get analysis results, default to empty string
    
    # Check if analysis contains action-oriented keywords
    if any(action in analysis.lower() for action in ["schedule", "confirm", "book", "send"]):
        return "execute"  # Execute actions first
    return "respond"  # Go directly to response generation

def build_graph():
    """
    Build email agent graph for LangGraph
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create StateGraph with AgentState schema
    workflow = StateGraph(AgentState)
    
    # Add nodes to the workflow
    workflow.add_node("analyze_email", analyze_email)  # Email analysis node
    workflow.add_node("gather_context", gather_context)  # Context gathering node
    workflow.add_node("generate_response", generate_response)  # Response generation node
    workflow.add_node("execute_actions", execute_actions)  # Action execution node
    workflow.add_node("review_and_finalize", review_and_finalize)  # Review and finalization node
    
    # Define workflow edges (connections between nodes)
    workflow.set_entry_point("analyze_email")  # Set starting node
    workflow.add_edge("analyze_email", "gather_context")  # Connect analysis to context gathering
    
    # Add conditional edge from context gathering
    workflow.add_conditional_edges(
        "gather_context",  # Source node
        should_execute_actions,  # Condition function
        {
            "execute": "execute_actions",  # If true, go to action execution
            "respond": "generate_response"  # If false, go to response generation
        }
    )
    
    # Connect remaining nodes in sequence
    workflow.add_edge("execute_actions", "generate_response")  # Actions to response
    workflow.add_edge("generate_response", "review_and_finalize")  # Response to review
    workflow.add_edge("review_and_finalize", END)  # Review to end of workflow
    
    # Compile the workflow into executable graph
    compiled_graph = workflow.compile()
    return compiled_graph

# Create graph at module level for LangGraph
# This allows LangGraph to import the graph directly
graph = build_graph()
