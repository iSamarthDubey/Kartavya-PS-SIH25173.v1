"""
Conversational Assistant Module
Core integration pipeline that orchestrates the complete NLP → SIEM workflow.
"""

from .pipeline import ConversationalPipeline
from .main import app
from .router import assistant_router

__version__ = "1.0.0"
__author__ = "SIEM NLP Assistant Team"

__all__ = [
    'ConversationalPipeline',
    'app',
    'assistant_router'
]