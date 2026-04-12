"""
Tests for the content guardrail system.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.guardrails.content_guard import ContentGuard, GuardrailResult, RiskLevel


@pytest.fixture
def guard():
    return ContentGuard(
        confidence_threshold=0.6,
        max_draft_length=5000,
        auto_block_keywords=["confidential", "top secret"],
        auto_approve_risk=RiskLevel.LOW,
    )


# ---------------------------------------------------------------------------
# Clean draft — should pass
# ---------------------------------------------------------------------------

def test_clean_draft_passes(guard):
    draft = "Thank you for reaching out. I will get back to you shortly."
    result = guard.check(draft, confidence_score=0.9)
    assert result.passed is True
    assert result.violations == []
    assert result.risk_level == RiskLevel.LOW
    assert result.requires_human_review is False


# ---------------------------------------------------------------------------
# PII detection
# ---------------------------------------------------------------------------

def test_pii_detection_email_address(guard):
    draft = "Please reach me at john.doe@example.com for further details."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert "email_address" in " ".join(result.violations)
    assert result.requires_human_review is True


def test_pii_detection_phone_number(guard):
    draft = "Call me at +1 (555) 123-4567 anytime."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert any("phone_number" in v for v in result.violations)
    assert result.requires_human_review is True


def test_pii_detection_ssn(guard):
    draft = "Your SSN 123-45-6789 has been verified."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert any("ssn" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Sensitive topics
# ---------------------------------------------------------------------------

def test_sensitive_topic_legal(guard):
    draft = "We might consider a lawsuit if this issue is not resolved."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert any("legal_threat" in v for v in result.violations)


def test_sensitive_topic_financial(guard):
    draft = "We guarantee payment of $5000 by next Friday."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert any("financial_commitment" in v for v in result.violations)


def test_sensitive_topic_security(guard):
    draft = "Your password is admin123, please change it."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert any("security_sensitive" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Max length guard
# ---------------------------------------------------------------------------

def test_max_length_guard(guard):
    draft = "a" * 5001
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert any("exceeds maximum length" in v for v in result.violations)
    assert result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)


# ---------------------------------------------------------------------------
# Confidence gate
# ---------------------------------------------------------------------------

def test_low_confidence_flagged(guard):
    draft = "This is a normal response without any obvious issues."
    result = guard.check(draft, confidence_score=0.4)
    assert not result.passed
    assert any("Low confidence" in v for v in result.violations)
    assert result.requires_human_review is True


def test_exact_threshold_passes(guard):
    """Score exactly at threshold should NOT trigger the gate (< not <=)."""
    draft = "This is a normal response without any obvious issues."
    result = guard.check(draft, confidence_score=0.6)
    assert result.passed is True


# ---------------------------------------------------------------------------
# Auto-block keywords
# ---------------------------------------------------------------------------

def test_auto_block_keyword(guard):
    draft = "This document is confidential and not for distribution."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.requires_human_review is True


# ---------------------------------------------------------------------------
# Risk escalation
# ---------------------------------------------------------------------------

def test_risk_escalates_with_multiple_violations(guard):
    draft = "Call me at 555-123-4567, your password is secret123, and we may face a lawsuit."
    result = guard.check(draft, confidence_score=0.9)
    assert not result.passed
    assert len(result.violations) >= 2
    assert result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
