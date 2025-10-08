"""
Assistant Router
Handles chat and conversation endpoints for the NLP assistant
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., description="Natural language query", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional user context")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")
    limit: Optional[int] = Field(100, description="Max results to return", ge=1, le=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me failed login attempts in the last hour",
                "conversation_id": "conv_12345",
                "filters": {"severity": "high"}
            }
        }

class ChatResponse(BaseModel):
    """Chat response model"""
    conversation_id: str
    query: str
    intent: str
    confidence: float
    entities: List[Dict[str, Any]]
    siem_query: Dict[str, Any]
    results: List[Dict[str, Any]]
    summary: str
    visualizations: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    metadata: Dict[str, Any]
    status: str
    error: Optional[str] = None

class ClarificationRequest(BaseModel):
    """Request model for clarifying ambiguous queries"""
    conversation_id: str
    original_query: str
    clarification_choice: str
    
class ConversationHistoryRequest(BaseModel):
    """Request for conversation history"""
    conversation_id: str
    limit: Optional[int] = Field(10, ge=1, le=100)

# Routes
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks
):
    """
    Main chat endpoint for processing natural language queries
    """
    try:
        # Import dependencies here to avoid circular imports
        from ..main import get_pipeline, get_context_manager, get_siem_connector, get_schema_mapper
        
        # Get dependencies
        pipeline = get_pipeline()
        context_manager = get_context_manager()
        siem_connector = get_siem_connector()
        schema_mapper = get_schema_mapper()
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Processing chat request: {request.query[:100]}...")
        
        # Get conversation context
        context = await context_manager.get_context(conversation_id)
        
        # Process the query through the pipeline
        result = await pipeline.process(
            query=request.query,
            context=context,
            user_context=request.user_context,
            filters=request.filters
        )
        
        # Check if clarification is needed
        if result.get("needs_clarification"):
            return ChatResponse(
                conversation_id=conversation_id,
                query=request.query,
                intent="clarification_needed",
                confidence=0.0,
                entities=[],
                siem_query={},
                results=[],
                summary="Your query contains ambiguous terms. Please clarify.",
                metadata={
                    "clarifications": result.get("clarifications", {}),
                    "timestamp": datetime.now().isoformat()
                },
                status="clarification_needed",
                error=None
            )
        
        # Map entities to SIEM schema
        field_mappings = await schema_mapper.map_entities(result["entities"])
        
        # Build SIEM query
        siem_query = await pipeline.build_query(
            intent=result["intent"],
            entities=result["entities"],
            field_mappings=field_mappings,
            context=context
        )
        
        # Validate query
        is_valid, validation_error = await pipeline.validate_query(siem_query)
        if not is_valid:
            return ChatResponse(
                conversation_id=conversation_id,
                query=request.query,
                intent=result["intent"],
                confidence=result["confidence"],
                entities=result["entities"],
                siem_query=siem_query,
                results=[],
                summary=f"Query blocked for safety: {validation_error}",
                metadata={"timestamp": datetime.now().isoformat()},
                status="blocked",
                error=validation_error
            )
        
        # Execute query
        search_results = await siem_connector.execute_query(
            query=siem_query,
            size=request.limit
        )
        
        # Format results
        formatted_results = await pipeline.format_results(
            results=search_results,
            query_type=result["intent"]
        )
        
        # Generate summary
        summary = await pipeline.generate_summary(
            results=formatted_results,
            query=request.query,
            intent=result["intent"]
        )
        
        # Generate visualizations if applicable
        visualizations = None
        if formatted_results and len(formatted_results) > 0:
            visualizations = await pipeline.create_visualizations(
                data=formatted_results,
                query_type=result["intent"]
            )
        
        # Generate follow-up suggestions
        suggestions = await pipeline.generate_suggestions(
            current_query=request.query,
            results=formatted_results,
            context=context
        )
        
        # Update context for future queries
        await context_manager.update_context(
            conversation_id=conversation_id,
            query=request.query,
            response={
                "intent": result["intent"],
                "entities": result["entities"],
                "results_count": len(formatted_results),
                "siem_query": siem_query
            }
        )
        
        # Background task to log the interaction
        background_tasks.add_task(
            log_interaction,
            conversation_id,
            request.query,
            result["intent"],
            len(formatted_results)
        )
        
        return ChatResponse(
            conversation_id=conversation_id,
            query=request.query,
            intent=result["intent"],
            confidence=result["confidence"],
            entities=result["entities"],
            siem_query=siem_query,
            results=formatted_results[:request.limit],
            summary=summary,
            visualizations=visualizations,
            suggestions=suggestions,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "processing_time": result.get("processing_time", 0),
                "total_results": len(formatted_results),
                "returned_results": min(len(formatted_results), request.limit)
            },
            status="success",
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        return ChatResponse(
            conversation_id=request.conversation_id or "error",
            query=request.query,
            intent="error",
            confidence=0.0,
            entities=[],
            siem_query={},
            results=[],
            summary=f"An error occurred while processing your request: {str(e)}",
            metadata={"timestamp": datetime.now().isoformat()},
            status="error",
            error=str(e)
        )

@router.post("/clarify")
async def clarify(request: ClarificationRequest):
    """
    Handle clarification for ambiguous queries
    """
    try:
        from ..main import get_pipeline, get_context_manager
        
        pipeline = get_pipeline()
        context_manager = get_context_manager()
        
        # Get context
        context = await context_manager.get_context(request.conversation_id)
        
        # Process clarification
        result = await pipeline.process_clarification(
            original_query=request.original_query,
            clarification=request.clarification_choice,
            context=context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing clarification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{conversation_id}")
async def get_history(
    conversation_id: str,
    limit: int = 10
):
    """
    Get conversation history
    """
    try:
        from ..main import get_context_manager
        
        context_manager = get_context_manager()
        history = await context_manager.get_history(conversation_id, limit)
        
        return {
            "conversation_id": conversation_id,
            "history": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{conversation_id}")
async def clear_history(conversation_id: str):
    """
    Clear conversation history
    """
    try:
        from ..main import get_context_manager
        
        context_manager = get_context_manager()
        await context_manager.clear_context(conversation_id)
        
        return {
            "status": "success",
            "message": f"Conversation {conversation_id} cleared"
        }
        
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_query_suggestions():
    """
    Get query suggestions/templates
    """
    suggestions = [
        {
            "category": "Authentication",
            "queries": [
                "Show me failed login attempts in the last hour",
                "Which users had the most authentication failures today?",
                "Are there any brute force attempts detected?",
                "Show successful logins from unusual locations"
            ]
        },
        {
            "category": "Threats",
            "queries": [
                "Any malware detected in the last 24 hours?",
                "Show critical security alerts from today",
                "What are the top threat indicators?",
                "Show potential data exfiltration attempts"
            ]
        },
        {
            "category": "Network",
            "queries": [
                "Show unusual network traffic patterns",
                "Which IPs generated the most traffic?",
                "Any connections to known malicious IPs?",
                "Show VPN connection anomalies"
            ]
        },
        {
            "category": "Reports",
            "queries": [
                "Generate security summary for last week",
                "Create incident report for critical alerts",
                "Show compliance violations report",
                "Generate executive dashboard"
            ]
        }
    ]
    
    return {"suggestions": suggestions}

# Helper functions
async def log_interaction(
    conversation_id: str,
    query: str,
    intent: str,
    results_count: int
):
    """
    Log interaction for audit purposes
    """
    try:
        logger.info(f"Interaction logged - Conv: {conversation_id}, Intent: {intent}, Results: {results_count}")
        # TODO: Implement actual audit logging to database
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
