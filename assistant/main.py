"""
FastAPI Application for Conversational Assistant
Provides REST API endpoints for the SIEM NLP Assistant chatbot interface.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports when running standalone
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .pipeline import ConversationalPipeline
    from .router import assistant_router
except ImportError:
    from assistant.pipeline import ConversationalPipeline
    from assistant.router import assistant_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SIEM NLP Conversational Assistant",
    description="Natural language interface for SIEM data analysis and querying",
    version="1.0.0",
    docs_url="/assistant/docs",
    redoc_url="/assistant/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline: Optional[ConversationalPipeline] = None

# Pydantic models for API
class QueryRequest(BaseModel):
    """Request model for conversational queries."""
    query: str = Field(..., description="Natural language query", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional user context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me failed login attempts in the last hour",
                "conversation_id": "conv_12345",
                "user_context": {"user_role": "security_analyst"}
            }
        }

class QueryResponse(BaseModel):
    """Response model for conversational queries."""
    conversation_id: str
    user_query: str
    intent: str
    entities: List[Dict[str, Any]]
    query_type: str
    siem_query: str
    results: List[Dict[str, Any]]
    visualizations: List[Dict[str, Any]]
    summary: str
    metadata: Dict[str, Any]
    status: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    components: Dict[str, bool]
    health_score: str
    is_initialized: bool
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""
    conversation_id: str
    history: List[Dict[str, Any]]
    total_messages: int

# Dependency to get pipeline instance
async def get_pipeline() -> ConversationalPipeline:
    """Dependency to get the initialized pipeline instance."""
    global pipeline
    if not pipeline:
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
    return pipeline

@app.on_event("startup")
async def startup_event():
    """Initialize the conversational pipeline on startup."""
    global pipeline
    logger.info("Starting SIEM NLP Conversational Assistant...")
    
    try:
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
        logger.info("✅ Conversational Assistant initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Conversational Assistant: {e}")
        # Don't raise exception to allow app to start even if some components fail

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Conversational Assistant...")

@app.get("/assistant/health", response_model=HealthResponse)
async def health_check(pipeline: ConversationalPipeline = Depends(get_pipeline)):
    """
    Check the health status of the conversational assistant pipeline.
    Returns status of all components and overall health score.
    """
    try:
        health_status = pipeline.get_health_status()
        return HealthResponse(
            status=health_status['status'],
            components=health_status['components'],
            health_score=health_status['health_score'],
            is_initialized=health_status['is_initialized'],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/assistant/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    pipeline: ConversationalPipeline = Depends(get_pipeline)
):
    """
    Process a natural language query through the conversational assistant pipeline.
    
    This endpoint:
    1. Analyzes the natural language input
    2. Generates appropriate SIEM queries
    3. Executes queries against available SIEM platforms
    4. Formats and summarizes the results
    5. Updates conversation context
    """
    try:
        logger.info(f"Processing query: '{request.query}'")
        
        # Process the query through the pipeline
        result = await pipeline.process_query(
            user_input=request.query,
            conversation_id=request.conversation_id,
            user_context=request.user_context
        )
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        
        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/assistant/conversation/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    pipeline: ConversationalPipeline = Depends(get_pipeline)
):
    """
    Retrieve the conversation history for a given conversation ID.
    Useful for maintaining context across multiple queries.
    """
    try:
        history = await pipeline.get_conversation_history(conversation_id)
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            history=history,
            total_messages=len(history)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation history: {str(e)}")

@app.delete("/assistant/conversation/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    pipeline: ConversationalPipeline = Depends(get_pipeline)
):
    """
    Clear the conversation history for a given conversation ID.
    """
    try:
        # This would need to be implemented in the context manager
        if hasattr(pipeline.context_manager, 'clear_conversation'):
            await pipeline.context_manager.clear_conversation(conversation_id)
        
        return {"message": f"Conversation {conversation_id} cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")

@app.get("/assistant/")
async def root():
    """Root endpoint for the conversational assistant."""
    return {
        "message": "SIEM NLP Conversational Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/assistant/health",
            "ask": "/assistant/ask",
            "history": "/assistant/conversation/{conversation_id}/history",
            "docs": "/assistant/docs"
        }
    }

# Include the router for additional endpoints
app.include_router(assistant_router, prefix="/assistant")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,  # Pass app directly instead of string
        host="0.0.0.0",
        port=8001,  # Different port from main backend
        reload=False,  # Disable reload for stability
        log_level="info"
    )