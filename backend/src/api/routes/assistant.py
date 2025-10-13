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

# Import standardized visual payload types
from ...types.visual_responses import (
    VisualPayload, 
    create_chart_payload, 
    create_table_payload, 
    create_summary_card_payload
)

# Import Redis caching
from ...core.caching.redis_manager import get_redis_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model"""
    query: Optional[str] = Field(None, description="Natural language query", min_length=1)
    message: Optional[str] = Field(None, description="Natural language message (alias for query)", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional user context")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")
    limit: Optional[int] = Field(100, description="Max results to return", ge=1, le=1000)
    
    def __init__(self, **data):
        # Handle backward compatibility: if message is provided but query is not, use message as query
        if data.get('message') and not data.get('query'):
            data['query'] = data['message']
        elif data.get('query') and not data.get('message'):
            data['message'] = data['query']
        
        # Ensure at least one is provided
        if not data.get('query') and not data.get('message'):
            raise ValueError("Either 'query' or 'message' field must be provided")
        
        super().__init__(**data)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me failed login attempts in the last hour",
                "conversation_id": "conv_12345",
                "filters": {"severity": "high"}
            }
        }

class ChatResponse(BaseModel):
    """Chat response model with standardized visual payload"""
    conversation_id: str
    query: str
    intent: str
    confidence: float
    entities: List[Dict[str, Any]]
    siem_query: Dict[str, Any]
    results: List[Dict[str, Any]]
    summary: str
    visualizations: Optional[List[VisualPayload]] = None  # Standardized format
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
    Main chat endpoint for processing natural language queries with Redis caching
    """
    try:
        # Import dependencies here to avoid circular imports
        from ..main import get_pipeline, get_context_manager, get_siem_connector, get_schema_mapper
        
        # Get dependencies
        pipeline = get_pipeline()
        context_manager = get_context_manager()
        siem_connector = get_siem_connector()  # Can be None in offline mode
        schema_mapper = get_schema_mapper()  # Can be None in offline mode
        redis_manager = await get_redis_manager()
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Processing chat request: {request.query[:100]}...")
        
        # Check cache first for identical queries
        cache_params = {
            "conversation_id": conversation_id,
            "user_context": request.user_context,
            "filters": request.filters,
            "limit": request.limit
        }
        
        cached_result = await redis_manager.get_cached_query_result(request.query, cache_params)
        if cached_result:
            logger.info(f"Returning cached result for query: {request.query[:50]}...")
            # Update conversation context with cached response
            await context_manager.update_context(
                conversation_id=conversation_id,
                query=request.query,
                response=cached_result.get("metadata", {})
            )
            return ChatResponse(**cached_result)
        
        # Get conversation context (try cache first)
        context = await redis_manager.get_conversation_context(conversation_id)
        if not context:
            context = await context_manager.get_context(conversation_id)
        
        # Prepare enhanced user context for AI improvements
        enhanced_user_context = {
            "user_id": request.user_id,
            "conversation_id": conversation_id,
            "role": "security_analyst",  # Default role - could be from auth/session
            "urgency": "normal",  # Could be detected from query keywords
            "preferences": {
                "default_time_window": "24h",
                "preferred_severity": ["high", "critical"]
            }
        }
        
        # Merge with provided user context
        if request.user_context:
            enhanced_user_context.update(request.user_context)
        
        # Detect urgency from query for smarter defaults
        urgent_keywords = ["urgent", "immediate", "critical", "alert", "breach", "attack"]
        if any(keyword in request.query.lower() for keyword in urgent_keywords):
            enhanced_user_context["urgency"] = "high"
        
        # Process the query through the enhanced pipeline
        result = await pipeline.process(
            query=request.query,
            context=context,
            user_context=enhanced_user_context,  # Use enhanced context
            filters=request.filters
        )
        
        # Handle pipeline processing errors
        if not result or "error" in result:
            return ChatResponse(
                conversation_id=conversation_id,
                query=request.query,
                intent="error",
                confidence=0.0,
                entities=[],
                siem_query={},
                results=[],
                summary="I apologize, but I'm experiencing technical difficulties processing your request. Please try again or rephrase your question.",
                metadata={"timestamp": datetime.now().isoformat(), "error": result.get("error", "Unknown pipeline error") if result else "Pipeline returned no result"},
                status="error",
                error=result.get("error", "Pipeline processing failed") if result else "No pipeline result"
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
        
        # Ensure entities exist
        entities = result.get("entities", [])
        intent = result.get("intent", "unknown")
        confidence = result.get("confidence", 0.0)
        
        # Handle offline mode
        if not siem_connector:
            return ChatResponse(
                conversation_id=conversation_id,
                query=request.query,
                intent=intent,
                confidence=confidence,
                entities=entities,
                siem_query={},
                results=[],
                summary="I'm currently running in offline mode. To process security queries, please connect to a SIEM platform like Elasticsearch, Splunk, or QRadar.",
                metadata={"timestamp": datetime.now().isoformat(), "mode": "offline"},
                status="offline",
                error=None
            )
        
        # Map entities to SIEM schema (skip if no schema mapper)
        field_mappings = {}
        if schema_mapper:
            field_mappings = await schema_mapper.map_entities(entities)
        else:
            # Basic fallback mapping
            field_mappings = {entity.get("type", "field"): entity.get("value", "") for entity in entities if isinstance(entity, dict)}
        
        # Build SIEM query
        siem_query = await pipeline.build_query(
            intent=intent,
            entities=entities,
            field_mappings=field_mappings,
            context=context
        )
        
        # Validate query
        is_valid, validation_error = await pipeline.validate_query(siem_query)
        if not is_valid:
            return ChatResponse(
                conversation_id=conversation_id,
                query=request.query,
                intent=intent,
                confidence=confidence,
                entities=entities,
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
            query_type=intent
        )
        
        # Generate summary (include AI enhancement info)
        base_summary = await pipeline.generate_summary(
            results=formatted_results,
            query=request.query,
            intent=intent
        )
        
        # Enhance summary with AI improvements info
        ai_enhancements = result.get("ai_enhancements", {})
        if ai_enhancements.get("enhanced"):
            applied_defaults = ai_enhancements.get("applied_defaults", [])
            enhancement_info = f" (Applied smart defaults: {', '.join(applied_defaults)})"
            summary = base_summary + enhancement_info
        else:
            summary = base_summary
        
        # Generate standardized visualizations if applicable
        visualizations = None
        if formatted_results and len(formatted_results) > 0:
            visualizations = await create_standardized_visualizations(
                data=formatted_results,
                query_type=intent,
                query=request.query
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
                "intent": intent,
                "entities": entities,
                "results_count": len(formatted_results),
                "siem_query": siem_query
            }
        )
        
        # Create response object
        response_data = {
            "conversation_id": conversation_id,
            "query": request.query,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "siem_query": siem_query,
            "results": formatted_results[:request.limit],
            "summary": summary,
            "visualizations": visualizations,
            "suggestions": suggestions,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "processing_time": result.get("processing_time", 0),
                "total_results": len(formatted_results),
                "returned_results": min(len(formatted_results), request.limit),
                "cache_hit": False,
                "ai_enhancements": result.get("ai_enhancements", {}),  # Include AI improvements
                "processed_query": result.get("processed_query", request.query)  # Show enhanced query
            },
            "status": "success",
            "error": None
        }
        
        # Cache the response for future identical queries (background task)
        background_tasks.add_task(
            cache_successful_response,
            redis_manager,
            request.query,
            response_data,
            cache_params
        )
        
        # Cache conversation context (background task)
        updated_context = context.copy()
        updated_context.update({
            "last_query": request.query,
            "last_intent": intent,
            "last_results_count": len(formatted_results),
            "message_count": updated_context.get("message_count", 0) + 1
        })
        background_tasks.add_task(
            redis_manager.cache_conversation_context,
            conversation_id,
            updated_context
        )
        
        # Background task to log the interaction
        background_tasks.add_task(
            log_interaction,
            conversation_id,
            request.query,
            result["intent"],
            len(formatted_results)
        )
        
        return ChatResponse(**response_data)
        
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
async def create_standardized_visualizations(
    data: List[Dict[str, Any]], 
    query_type: str, 
    query: str
) -> List[VisualPayload]:
    """
    Create standardized visualizations that match frontend expectations
    """
    visualizations = []
    
    try:
        # Always create a table view for the raw data
        table_viz = create_table_payload(
            title=f"Query Results: {query}",
            data=data[:50],  # Limit to first 50 rows for performance
            query_type=query_type,
            data_source="siem"
        )
        visualizations.append(table_viz)
        
        # Create intent-specific visualizations
        if query_type in ["search_logs", "authentication", "network_analysis"]:
            # Create a summary card with total count
            summary_viz = create_summary_card_payload(
                title="Total Results Found",
                value=len(data),
                status="normal" if len(data) < 100 else "warning" if len(data) < 500 else "critical",
                query_type=query_type
            )
            visualizations.append(summary_viz)
            
        # Create charts based on data patterns
        if len(data) > 0:
            # Look for timestamp field for time series
            timestamp_fields = ['@timestamp', 'timestamp', 'time', 'created_at']
            timestamp_field = None
            for field in timestamp_fields:
                if field in data[0]:
                    timestamp_field = field
                    break
            
            # Look for count/numeric fields
            numeric_fields = []
            for key, value in data[0].items():
                if isinstance(value, (int, float)) and key not in ['id', '_id']:
                    numeric_fields.append(key)
            
            # Create time series chart if timestamp found
            if timestamp_field and len(data) > 1:
                chart_viz = create_chart_payload(
                    title="Activity Over Time",
                    data=data[:100],  # Limit for performance
                    chart_type="line",
                    x_field=timestamp_field,
                    y_field="count",  # Default count aggregation
                    query_type=query_type,
                    data_source="siem"
                )
                visualizations.append(chart_viz)
                
        logger.info(f"Created {len(visualizations)} standardized visualizations for {query_type}")
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")
        # Fallback: at least return a basic table
        visualizations = [
            create_table_payload(
                title="Query Results",
                data=data[:50],
                query_type=query_type
            )
        ]
    
    return visualizations

async def cache_successful_response(
    redis_manager,
    query: str,
    response_data: Dict[str, Any],
    cache_params: Dict[str, Any]
):
    """
    Cache successful response for future identical queries
    """
    try:
        # Only cache successful responses with results
        if (response_data.get("status") == "success" and 
            response_data.get("results") and 
            len(response_data["results"]) > 0):
            
            # Mark as cached for future responses
            cached_response = response_data.copy()
            cached_response["metadata"]["cache_hit"] = True
            cached_response["metadata"]["cached_at"] = datetime.now().isoformat()
            
            await redis_manager.cache_query_result(
                query=query,
                result=cached_response,
                params=cache_params,
                ttl=1800  # 30 minutes cache for query results
            )
            logger.info(f"Cached successful response for query: {query[:50]}...")
    except Exception as e:
        logger.error(f"Error caching response: {e}")

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
