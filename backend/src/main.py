"""
Main entry point for the SIEM NLP Assistant API
Re-exports the FastAPI app from api.main for uvicorn compatibility
"""

from .api.main import app

# Re-export the app for uvicorn
__all__ = ['app']
