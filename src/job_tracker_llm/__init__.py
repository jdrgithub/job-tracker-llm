"""
Job Tracker LLM - A comprehensive job search tracking tool with AI-powered insights.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .models import JobOpportunity, Interaction, InteractionType, ContactMethod, SearchFilters, SearchResult
from .storage import JobStorage
from .vector_store import JobVectorStore
from .cli import main

__all__ = [
    "JobOpportunity",
    "Interaction", 
    "InteractionType",
    "ContactMethod",
    "SearchFilters",
    "SearchResult",
    "JobStorage",
    "JobVectorStore",
    "main"
]
