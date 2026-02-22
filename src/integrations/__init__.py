"""
Integrations Package

This package contains external service integrations for Email Assistant.
"""

from .google_calendar import GoogleCalendarIntegration
from .web_search import WebSearchIntegration, SearchEngine

__all__ = ['GoogleCalendarIntegration', 'WebSearchIntegration', 'SearchEngine']
