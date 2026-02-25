"""
Human-in-the-Loop (HITL) package for the Email Assistant.
Provides review queue management for flagged email drafts.
"""

from src.hitl.review_manager import ReviewManager, ReviewStatus, ReviewRecord

__all__ = ["ReviewManager", "ReviewStatus", "ReviewRecord"]
