"""
Content Guardrails for the Email Assistant.

This module provides automated safety checks on generated email drafts before
they are finalized, saved, or sent. Checks include:
  - PII detection (emails, phone numbers, SSNs, credit cards)
  - Sensitive topic filtering (legal, financial, medical, etc.)
  - Confidence gate (flags low-confidence outputs for human review)
  - Content length guard (blocks runaway generation)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GuardrailResult:
    """Result of running all guardrail checks on a draft."""
    passed: bool                       # True if no blocking violations
    violations: List[str] = field(default_factory=list)   # Descriptions of violations
    risk_level: RiskLevel = RiskLevel.LOW
    requires_human_review: bool = False
    details: dict = field(default_factory=dict)           # Extra info per check


# ---------------------------------------------------------------------------
# PII Patterns
# ---------------------------------------------------------------------------

_PII_PATTERNS = {
    "email_address": re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    ),
    "phone_number": re.compile(
        r"\b(\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)[\d\s.\-]{7,}\d\b"
    ),
    "ssn": re.compile(
        r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"
    ),
    "credit_card": re.compile(
        r"\b(?:\d[ -]?){13,16}\b"
    ),
    "passport": re.compile(
        r"\b[A-Z]{1,2}\d{6,9}\b"
    ),
}

# ---------------------------------------------------------------------------
# Sensitive Topic Keywords
# ---------------------------------------------------------------------------

_SENSITIVE_TOPICS: dict[str, List[str]] = {
    "legal_threat": [
        "lawsuit", "legal action", "sue you", "sue us", "litigation",
        "court order", "attorney", "lawyer", "subpoena", "injunction",
        "breach of contract", "arbitration", "settlement", "damages",
    ],
    "financial_commitment": [
        "guarantee payment", "wire transfer", "refund of", "reimburse",
        "compensation of", "pay you", "will pay", "owe you",
        "financial commitment", "invoice", "billing error",
    ],
    "medical_advice": [
        "you should take", "dosage", "prescription", "diagnose",
        "medical advice", "treatment for", "symptoms of",
        "you have", "you are suffering",
    ],
    "political_sensitive": [
        "political party", "election fraud", "vote rigging",
        "government conspiracy", "classified information",
    ],
    "security_sensitive": [
        "password is", "your pin", "secret key", "api key",
        "access token", "private key", "credentials are",
    ],
}


class ContentGuard:
    """
    Runs all guardrail checks on an email draft.

    Usage:
        guard = ContentGuard(
            confidence_threshold=0.6,
            max_draft_length=5000,
            auto_block_keywords=["confidential"],
            auto_approve_risk=RiskLevel.LOW,
        )
        result = guard.check(draft_text, confidence_score=0.75)
    """

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        max_draft_length: int = 5000,
        auto_block_keywords: Optional[List[str]] = None,
        auto_approve_risk: RiskLevel = RiskLevel.LOW,
    ):
        self.confidence_threshold = confidence_threshold
        self.max_draft_length = max_draft_length
        self.auto_block_keywords = [kw.lower() for kw in (auto_block_keywords or [])]
        self.auto_approve_risk = auto_approve_risk

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(
        self,
        draft: str,
        confidence_score: float = 1.0,
        original_email: Optional[dict] = None,
    ) -> GuardrailResult:
        """
        Run all checks on the given draft.

        Args:
            draft: The generated email response text.
            confidence_score: Agent's self-reported confidence (0–1).
            original_email: The original email dict (for context in future checks).

        Returns:
            GuardrailResult describing whether the draft passed all checks.
        """
        violations: List[str] = []
        details: dict = {}
        risk = RiskLevel.LOW

        # 1. Length guard
        len_result = self._check_length(draft)
        if len_result:
            violations.append(len_result)
            risk = self._escalate(risk, RiskLevel.HIGH)
            details["length"] = len(draft)

        # 2. Auto-block keywords
        blocked = self._check_auto_block(draft)
        if blocked:
            violations.append(f"Draft contains blocked keyword(s): {blocked}")
            risk = self._escalate(risk, RiskLevel.CRITICAL)
            details["blocked_keywords"] = blocked

        # 3. PII detection
        pii_found = self._check_pii(draft)
        if pii_found:
            violations.append(f"PII detected in draft: {', '.join(pii_found)}")
            risk = self._escalate(risk, RiskLevel.HIGH)
            details["pii"] = pii_found

        # 4. Sensitive topics
        topics_found = self._check_sensitive_topics(draft)
        if topics_found:
            violations.append(f"Sensitive topics detected: {', '.join(topics_found)}")
            risk = self._escalate(risk, RiskLevel.MEDIUM)
            details["sensitive_topics"] = topics_found

        # 5. Confidence gate
        if confidence_score < self.confidence_threshold:
            violations.append(
                f"Low confidence score ({confidence_score:.2f} < {self.confidence_threshold})"
            )
            risk = self._escalate(risk, RiskLevel.MEDIUM)
            details["confidence_score"] = confidence_score

        # Determine if this is an outright block or just needs human review
        passed = len(violations) == 0 or (
            risk not in (RiskLevel.CRITICAL,) and len(violations) == 0
        )

        # Critical or high with violations → always fail
        if violations and risk in (RiskLevel.CRITICAL, RiskLevel.HIGH):
            passed = False
        elif violations and risk == RiskLevel.MEDIUM:
            passed = False  # Still not "passed", but not outright blocked

        # Does it need human review?
        requires_human_review = (not passed) or (
            risk != RiskLevel.LOW and risk != self.auto_approve_risk
        )

        return GuardrailResult(
            passed=passed,
            violations=violations,
            risk_level=risk,
            requires_human_review=requires_human_review,
            details=details,
        )

    def redact_sensitive_data(self, draft: str) -> str:
        """
        Redact or mask sensitive data in the draft.

        Args:
            draft: The email draft text to redact.

        Returns:
            The draft with sensitive data redacted.
        """
        redacted = draft

        # Redact PII - order matters, more specific patterns first
        # SSN first (more specific)
        ssn_pattern = _PII_PATTERNS["ssn"]
        redacted = ssn_pattern.sub("[SSN REDACTED]", redacted)

        # Email
        email_pattern = _PII_PATTERNS["email_address"]
        redacted = email_pattern.sub("[EMAIL REDACTED]", redacted)

        # Phone (after SSN to avoid conflicts)
        phone_pattern = _PII_PATTERNS["phone_number"]
        redacted = phone_pattern.sub("[PHONE REDACTED]", redacted)

        # Credit card
        credit_pattern = _PII_PATTERNS["credit_card"]
        redacted = credit_pattern.sub("[CREDIT CARD REDACTED]", redacted)

        # Passport
        passport_pattern = _PII_PATTERNS["passport"]
        redacted = passport_pattern.sub("[PASSPORT REDACTED]", redacted)

        # Redact sensitive topics (mask keywords)
        for category, keywords in _SENSITIVE_TOPICS.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                redacted = pattern.sub("[REDACTED]", redacted)

        return redacted

    # ------------------------------------------------------------------
    # Individual Checks
    # ------------------------------------------------------------------

    def _check_length(self, draft: str) -> Optional[str]:
        if len(draft) > self.max_draft_length:
            return (
                f"Draft exceeds maximum length "
                f"({len(draft)} chars > {self.max_draft_length} allowed)."
            )
        return None

    def _check_auto_block(self, draft: str) -> List[str]:
        lower = draft.lower()
        return [kw for kw in self.auto_block_keywords if kw in lower]

    def _check_pii(self, draft: str) -> List[str]:
        found = []
        for pii_type, pattern in _PII_PATTERNS.items():
            if pattern.search(draft):
                found.append(pii_type)
        return found

    def _check_sensitive_topics(self, draft: str) -> List[str]:
        lower = draft.lower()
        found = []
        for category, keywords in _SENSITIVE_TOPICS.items():
            if any(kw in lower for kw in keywords):
                found.append(category)
        return found

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _escalate(current: RiskLevel, candidate: RiskLevel) -> RiskLevel:
        """Return the higher of two risk levels."""
        order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        return candidate if order.index(candidate) > order.index(current) else current
