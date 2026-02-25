"""
Human Review API Routes.

Exposes CRUD-like endpoints for the HITL review queue so human reviewers can
inspect, approve, reject, or edit-and-approve pending email drafts that were
flagged by the guardrail system.
"""

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.hitl.review_manager import ReviewManager, ReviewStatus

router = APIRouter()

# Shared manager instance (reuses existing DB)
_review_manager = ReviewManager(db_path="./email_assistant.db")


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ApproveRequest(BaseModel):
    pass  # No body needed


class RejectRequest(BaseModel):
    reason: Optional[str] = ""


class EditAndApproveRequest(BaseModel):
    edited_draft: str


class ReviewSummary(BaseModel):
    review_id: str
    status: str
    risk_level: str
    created_at: str
    updated_at: str
    violations: List[str]
    email_subject: Optional[str] = None
    email_from: Optional[str] = None


class ReviewDetail(ReviewSummary):
    original_draft: str
    final_draft: Optional[str] = None
    reject_reason: Optional[str] = None
    email_data: Dict[str, Any]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_summary(record) -> ReviewSummary:
    return ReviewSummary(
        review_id=record.review_id,
        status=record.status.value,
        risk_level=record.risk_level,
        created_at=record.created_at,
        updated_at=record.updated_at,
        violations=record.violations,
        email_subject=record.email_data.get("subject"),
        email_from=record.email_data.get("from_email") or record.email_data.get("from"),
    )


def _to_detail(record) -> ReviewDetail:
    return ReviewDetail(
        review_id=record.review_id,
        status=record.status.value,
        risk_level=record.risk_level,
        created_at=record.created_at,
        updated_at=record.updated_at,
        violations=record.violations,
        email_subject=record.email_data.get("subject"),
        email_from=record.email_data.get("from_email") or record.email_data.get("from"),
        original_draft=record.original_draft,
        final_draft=record.final_draft,
        reject_reason=record.reject_reason,
        email_data=record.email_data,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/pending", response_model=List[ReviewSummary])
async def list_pending_reviews():
    """List all email drafts awaiting human review."""
    records = _review_manager.get_pending()
    return [_to_summary(r) for r in records]


@router.get("/all", response_model=List[ReviewSummary])
async def list_all_reviews(limit: int = 100):
    """List all reviews (any status), newest first."""
    records = _review_manager.get_all(limit=limit)
    return [_to_summary(r) for r in records]


@router.get("/{review_id}", response_model=ReviewDetail)
async def get_review(review_id: str):
    """Get full details for a single review record."""
    record = _review_manager.get_review(review_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Review '{review_id}' not found.")
    return _to_detail(record)


@router.post("/{review_id}/approve", response_model=ReviewDetail)
async def approve_review(review_id: str):
    """
    Approve a pending review.

    The original LLM-generated draft will be used for save/send actions.
    """
    try:
        record = _review_manager.approve(review_id)
        return _to_detail(record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{review_id}/reject", response_model=ReviewDetail)
async def reject_review(review_id: str, body: RejectRequest = RejectRequest()):
    """
    Reject a pending review — the draft is discarded.
    """
    try:
        record = _review_manager.reject(review_id, reason=body.reason or "")
        return _to_detail(record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{review_id}/edit", response_model=ReviewDetail)
async def edit_and_approve_review(review_id: str, body: EditAndApproveRequest):
    """
    Replace the draft with an edited version and approve it.
    """
    if not body.edited_draft.strip():
        raise HTTPException(status_code=422, detail="edited_draft must not be empty.")
    try:
        record = _review_manager.edit_and_approve(review_id, body.edited_draft)
        return _to_detail(record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
