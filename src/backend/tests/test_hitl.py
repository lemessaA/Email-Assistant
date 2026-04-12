"""
Tests for the Human-in-the-Loop ReviewManager.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.hitl.review_manager import ReviewManager, ReviewStatus


@pytest.fixture
def mgr(tmp_path):
    """Create a ReviewManager backed by a temporary SQLite database."""
    db_path = str(tmp_path / "test_reviews.db")
    return ReviewManager(db_path=db_path)


@pytest.fixture
def sample_email():
    return {
        "subject": "Test Email",
        "body": "This email may contain a lawsuit.",
        "from_email": "sender@example.com",
        "to_emails": ["recipient@example.com"],
    }


# ---------------------------------------------------------------------------
# create_review
# ---------------------------------------------------------------------------

def test_create_review_returns_id(mgr, sample_email):
    review_id = mgr.create_review(
        email_data=sample_email,
        draft="Thank you for reaching out.",
        violations=["legal_threat"],
        risk_level="medium",
    )
    assert isinstance(review_id, str)
    assert len(review_id) > 0


def test_create_review_is_pending(mgr, sample_email):
    review_id = mgr.create_review(
        email_data=sample_email,
        draft="Draft text.",
        violations=["legal_threat"],
        risk_level="medium",
    )
    record = mgr.get_review(review_id)
    assert record is not None
    assert record.status == ReviewStatus.PENDING


def test_get_pending_shows_new_review(mgr, sample_email):
    mgr.create_review(sample_email, "Draft.", ["pii"], "high")
    pending = mgr.get_pending()
    assert len(pending) >= 1


# ---------------------------------------------------------------------------
# approve
# ---------------------------------------------------------------------------

def test_approve_changes_status(mgr, sample_email):
    review_id = mgr.create_review(sample_email, "Draft.", ["pii"], "high")
    updated = mgr.approve(review_id)
    assert updated.status == ReviewStatus.APPROVED


def test_approve_nonexistent_raises(mgr):
    with pytest.raises(ValueError, match="not found"):
        mgr.approve("nonexistent-id")


def test_approve_already_approved_raises(mgr, sample_email):
    review_id = mgr.create_review(sample_email, "Draft.", [], "low")
    mgr.approve(review_id)
    with pytest.raises(ValueError, match="not pending"):
        mgr.approve(review_id)


# ---------------------------------------------------------------------------
# reject
# ---------------------------------------------------------------------------

def test_reject_changes_status(mgr, sample_email):
    review_id = mgr.create_review(sample_email, "Draft.", ["pii"], "high")
    updated = mgr.reject(review_id, reason="Contains sensitive data.")
    assert updated.status == ReviewStatus.REJECTED
    assert updated.reject_reason == "Contains sensitive data."


def test_rejected_not_in_pending(mgr, sample_email):
    review_id = mgr.create_review(sample_email, "Draft.", ["pii"], "high")
    mgr.reject(review_id)
    pending_ids = [r.review_id for r in mgr.get_pending()]
    assert review_id not in pending_ids


# ---------------------------------------------------------------------------
# edit_and_approve
# ---------------------------------------------------------------------------

def test_edit_and_approve(mgr, sample_email):
    review_id = mgr.create_review(sample_email, "Bad draft.", ["pii"], "high")
    updated = mgr.edit_and_approve(review_id, "Corrected, safe draft.")
    assert updated.status == ReviewStatus.EDITED_AND_APPROVED
    assert updated.final_draft == "Corrected, safe draft."
    assert updated.original_draft == "Bad draft."


def test_edit_preserves_original_draft(mgr, sample_email):
    review_id = mgr.create_review(sample_email, "Original draft.", ["pii"], "high")
    updated = mgr.edit_and_approve(review_id, "Edited draft.")
    assert updated.original_draft == "Original draft."


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------

def test_get_all_returns_all_statuses(mgr, sample_email):
    r1 = mgr.create_review(sample_email, "D1.", [], "low")
    r2 = mgr.create_review(sample_email, "D2.", ["pii"], "high")
    mgr.approve(r1)
    mgr.reject(r2)
    all_records = mgr.get_all()
    statuses = {r.review_id: r.status for r in all_records}
    assert statuses[r1] == ReviewStatus.APPROVED
    assert statuses[r2] == ReviewStatus.REJECTED
