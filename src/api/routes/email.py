from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import json
import asyncio

from src.agents.email_agent import EmailAssistantAgent
from src.services.email_sender import send_email as send_email_smtp

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
        email_data = request.model_dump()
        # Process email asynchronously
        result = await agent.process_email(email_data)
        
        return EmailResponse(
            success=True,
            draft=result.get("response"),
            actions=result.get("actions_taken", []),
            analysis={"content": result.get("analysis")} if isinstance(result.get("analysis"), str) else result.get("analysis"),
            processing_time=0.0  # Would calculate actual time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft")
async def draft_email(
    request: EmailRequest,
    agent: EmailAssistantAgent = Depends(lambda: EmailAssistantAgent())
) -> Dict[str, Any]:
    """Draft an email response"""
    try:
        # Use the agent to draft response
        result = await agent.process_email(request.model_dump())
        
        analysis = result.get("analysis")
        if isinstance(analysis, str):
            tone_analysis = analysis
        elif isinstance(analysis, dict):
            tone_analysis = analysis.get("content", "professional")
        else:
            tone_analysis = "professional"
        
        return {
            "draft": result.get("response"),
            "suggested_subject": f"Re: {request.subject}",
            "tone_analysis": tone_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_email(
    request: EmailRequest,
) -> Dict[str, Any]:
    """Send an email to recipients via SMTP. Requires SMTP_* configured in .env."""
    try:
        attachment_paths = []
        if request.attachments:
            for att in request.attachments:
                path = att.get("path") or att.get("file_path")
                if path:
                    attachment_paths.append(path)

        success, message = send_email_smtp(
            from_email=request.from_email,
            to_emails=list(request.to_emails),
            subject=request.subject,
            body=request.body,
            cc_emails=list(request.cc_emails) if request.cc_emails else None,
            attachment_paths=attachment_paths if attachment_paths else None,
        )

        if success:
            return {
                "success": True,
                "message": message,
                "to": list(request.to_emails),
            }
        else:
            raise HTTPException(status_code=502, detail=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/unread")
async def get_unread_emails(
    email_user: Optional[str] = None,
    email_password: Optional[str] = None,
    imap_server: Optional[str] = None
):
    """Get unread emails for processing"""
    try:
        from src.agents.tools import EmailTools
        from src.core.config import settings
        
        # Use provided credentials or fall back to settings
        emails = EmailTools.get_unread_emails.invoke({
            "limit": 10,
            "folder": "inbox",
            "imap_server": imap_server or settings.imap_server,
            "username": email_user or settings.email_user or "your-email@gmail.com",
            "password": email_password or settings.email_password or "your-app-password"
        })
        
        return {
            "success": True,
            "emails": emails,
            "total": len(emails),
            "source": "real_imap"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emails: {str(e)}")
    except HTTPException:
        raise
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