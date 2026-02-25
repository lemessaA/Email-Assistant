"""
Guardrails package for the Email Assistant.
Provides content safety checks before email responses are finalized.
"""

from src.guardrails.content_guard import ContentGuard, GuardrailResult, RiskLevel

__all__ = ["ContentGuard", "GuardrailResult", "RiskLevel"]
