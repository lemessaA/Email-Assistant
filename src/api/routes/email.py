from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import json

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
    background_tasks: BackgroundTasks,
    agent: EmailAssistantAgent = Depends(lambda: EmailAssistantAgent())
) -> EmailResponse:
    """Process an incoming email and generate response/actions"""
    try:
        email_data = request.dict()
        
        # Process email asynchronously
        result = await agent.process_email(email_data)
        
        return EmailResponse(
            success=True,
            draft=result.get("response"),
            actions=result.get("actions_taken", []),
            analysis=result.get("analysis"),
            processing_time=0.0  # Would calculate actual time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft")
async def draft_email(
    request: EmailRequest,
    tone: str = "professional",
    agent: EmailAssistantAgent = Depends(lambda: EmailAssistantAgent())
) -> Dict[str, Any]:
    """Draft an email response"""
    try:
        # Use the agent to draft response
        result = await agent.process_email(request.dict())
        
        return {
            "draft": result.get("response"),
            "suggested_subject": f"Re: {request.subject}",
            "tone_analysis": result.get("analysis", {}).get("tone")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream")
async def stream_response(
    email_id: str,
    agent: EmailAssistantAgent = Depends(lambda: EmailAssistantAgent())
):
    """Stream the email processing response"""
    async def event_generator():
        # Simulate streaming response
        yield f"data: Analyzing email...\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: Gathering context...\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: Generating response...\n\n"
        await asyncio.sleep(1)
        
        yield f"data: Finalizing...\n\n"
        yield f"data: DONE\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )