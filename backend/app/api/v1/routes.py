"""
API Routes for Kartavya SIEM Assistant
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import logging

from app.models.schemas import (
    QueryRequest, QueryResponse, HealthCheck, ErrorResponse
)
from app.services.pipeline import QueryPipeline
from app.services.context import ContextManager
from app.core.siem import SIEMConnector
from app.core.nlp import NLPProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
nlp_processor = NLPProcessor()
context_manager = ContextManager()
query_pipeline = QueryPipeline()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language SIEM query"""
    try:
        # Process NLP
        nlp_result = nlp_processor.process_query(request.query)
        
        # Get or create session context
        context = await context_manager.get_context(request.session_id)
        
        # Execute pipeline
        result = await query_pipeline.execute(
            query=request.query,
            intent=nlp_result["intent"],
            entities=nlp_result["entities"],
            context=context
        )
        
        # Update context
        await context_manager.update_context(
            session_id=request.session_id,
            query=request.query,
            result=result
        )
        
        return QueryResponse(
            success=True,
            query=request.query,
            intent=nlp_result["intent"],
            entities=nlp_result["entities"],
            results=result["data"],
            summary=result.get("summary"),
            charts=result.get("charts"),
            dsl_query=result.get("dsl_query"),
            execution_time_ms=result.get("execution_time_ms")
        )
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Check service health"""
    from datetime import datetime
    from app.core.config import settings
    
    # Check Elasticsearch connection
    siem = SIEMConnector()
    es_connected = await siem.check_connection()
    
    return HealthCheck(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        elasticsearch_connected=es_connected,
        timestamp=datetime.utcnow()
    )

@router.post("/clear-context")
async def clear_context(session_id: str = Query(...)):
    """Clear conversation context"""
    await context_manager.clear_context(session_id)
    return {"message": "Context cleared successfully"}

@router.get("/intents")
async def list_intents():
    """List available query intents"""
    return {
        "intents": [
            {
                "name": "authentication",
                "description": "Login attempts, authentication failures, password resets",
                "examples": ["Show failed logins", "Authentication errors today"]
            },
            {
                "name": "malware_detection",
                "description": "Malware, virus, trojan detections",
                "examples": ["Malware detections this week", "Show virus alerts"]
            },
            {
                "name": "network_security",
                "description": "Network traffic, firewall, connections",
                "examples": ["Suspicious network activity", "Blocked connections"]
            }
        ]
    }
