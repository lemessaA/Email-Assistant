from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EmailIntent(str, Enum):
    QUESTION = "question"
    REQUEST = "request"
    COMPLAINT = "complaint"
    SCHEDULING = "scheduling"
    INSTRUCTIONS = "instructions"
    SPAM = "spam"
    SOCIAL = "social"
    PROMOTIONAL = "promotional"
    OTHER = "other"

class EmailAnalysisSchema(BaseModel):
    intent: EmailIntent = Field(..., description="Primary intent of the email")
    urgency: UrgencyLevel = Field(..., description="Urgency of the email")
    priority_score: int = Field(..., ge=1, le=10, description="Priority score from 1 (lowest) to 10 (highest)")
    is_spam: bool = Field(..., description="Whether the email is likely spam")
    is_low_priority: bool = Field(..., description="Whether the email is fundamentally low priority/automated")
    summary: str = Field(..., description="Concise summary of the email")
    required_actions: List[str] = Field(default_factory=list, description="List of actions required to address the email")
    context_needed: List[str] = Field(default_factory=list, description="Context clues or missing info needed for a full response")

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
    analysis: Optional[EmailAnalysisSchema] = None
    processing_time: float


class EvaluationRequest(BaseModel):
    email: Dict[str, Any]
    generated_response: str
    ground_truth: Optional[str] = None

class BatchEvaluationRequest(BaseModel):
    test_cases: List[Dict[str, Any]]
