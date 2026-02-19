from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import json
import time
from src.agents.email_agent import EmailAssistantAgent


router = APIRouter()

class EmailRequest(BaseModel):
    subject: str
    body: str
    from_email: EmailStr
    to_emails: List[EmailStr]
    cc_emails: Optional[List[EmailStr]] = []
    attachments: Optional[List[Dict[str, Any]]] = None
    priority: Optional[str] = "normal"
    metadata: Optional[Dict[str, Any]] = {}

class EmailResponse(BaseModel):
    success: bool
    draft: Optional[str] = None
    actions: List[Dict[str, Any]] = []
    analysis: Optional[Dict[str, Any]] = None
    processing_time: float

@router.post("/process")
async def process_email(
    request: EmailRequest,
    background_tasks: BackgroundTasks
) -> EmailResponse:
    """Process an incoming email and generate response/actions"""
    try:
        start_time = time.time()
        
        # For testing, return mock response without agent
        return EmailResponse(
            success=True,
            draft="Thank you for your email. I will get back to you shortly.",
            actions=[],
            analysis={"intent": "general inquiry"},
            processing_time=0.5
        )
        
        # Create agent instance 
        agent = EmailAssistantAgent()
        
        # Process email using the agent
        result = await agent.process_email(request.dict())
        
        processing_time = time.time() - start_time
        
        return EmailResponse(
            success=True,
            draft=result.get("response"),
            actions=result.get("actions_taken", []),
            analysis={"intent": result.get("analysis", "general inquiry")},
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft")
async def draft_email(
    request: EmailRequest,
    tone: str = "professional"
) -> Dict[str, Any]:
    """Draft an email response"""
    try:
        # Simple mock response
        return {
            "draft": f"Thank you for your email regarding: {request.subject}",
            "suggested_subject": f"Re: {request.subject}",
            "tone_analysis": tone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream")
async def stream_response(email_id: str):
    """Stream the email processing response"""
    async def event_generator():
        yield f"data: Analyzing email...\n\n"
        yield f"data: Generating response...\n\n"
        yield f"data: DONE\n\n"
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
