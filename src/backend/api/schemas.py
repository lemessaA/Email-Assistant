from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

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


class EvaluationRequest(BaseModel):
    email: Dict[str, Any]
    generated_response: str
    ground_truth: str = None

class BatchEvaluationRequest(BaseModel):
    test_cases: List[Dict[str, Any]]
