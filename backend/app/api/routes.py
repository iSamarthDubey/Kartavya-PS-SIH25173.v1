"""
Assistant Router
Additional routing logic for conversational assistant endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from .pipeline import ConversationalPipeline

logger = logging.getLogger(__name__)

# Create router for assistant-specific endpoints
assistant_router = APIRouter(
    prefix="/v1",
    tags=["conversational-assistant"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get pipeline instance (will be injected by main app)
async def get_pipeline() -> ConversationalPipeline:
    """Dependency to get the pipeline instance from main app."""
    # This will be overridden by the main app
    pass

@assistant_router.get("/status")
async def get_detailed_status():
    """Get detailed status information about the assistant."""
    try:
        return {
            "service": "SIEM NLP Conversational Assistant",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": "Available",
            "features": [
                "Natural Language Processing",
                "Intent Classification",
                "Entity Extraction", 
                "Multi-SIEM Query Generation",
                "Response Formatting",
                "Conversation Context Management"
            ],
            "supported_siem_platforms": [
                "Elasticsearch",
                "Wazuh",
                "Splunk (via Universal Connector)",
                "Custom Log Sources"
            ]
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.get("/capabilities")
async def get_capabilities():
    """Get information about assistant capabilities and supported queries."""
    return {
        "natural_language_support": {
            "supported_languages": ["English"],
            "query_types": [
                "Security incident investigation",
                "Log analysis and filtering",
                "Threat hunting queries",
                "Performance monitoring",
                "Alert investigation",
                "Compliance reporting"
            ]
        },
        "intent_categories": [
            "search_logs",
            "analyze_alerts", 
            "investigate_incident",
            "monitor_performance",
            "generate_report",
            "hunt_threats"
        ],
        "entity_types": [
            "ip_address",
            "hostname", 
            "user_account",
            "file_path",
            "process_name",
            "timestamp",
            "event_type",
            "severity_level"
        ],
        "output_formats": [
            "structured_data",
            "visualizations",
            "summaries",
            "recommendations"
        ]
    }

@assistant_router.get("/examples")
async def get_query_examples():
    """Get example queries that users can try."""
    return {
        "security_queries": [
            "Show me failed login attempts in the last hour",
            "Find all alerts with high severity from yesterday", 
            "What processes were started by user admin today?",
            "Show me network connections to external IPs",
            "Find all file modifications in /etc/ directory"
        ],
        "investigation_queries": [
            "Investigate incident ID 12345",
            "What happened around 2023-10-01 15:30:00?",
            "Show me all events related to IP 192.168.1.100",
            "Find suspicious process executions on server01",
            "What files were accessed by compromised user account?"
        ],
        "monitoring_queries": [
            "Show system performance metrics",
            "What are the top 10 most frequent log sources?", 
            "Display network traffic patterns",
            "Show memory usage trends",
            "Find systems with high error rates"
        ]
    }

@assistant_router.post("/feedback")
async def submit_feedback(feedback_data: Dict[str, Any]):
    """Submit feedback about query results or assistant performance."""
    try:
        # Log feedback for analysis
        logger.info(f"User feedback received: {feedback_data}")
        
        # In a production system, this would store feedback in a database
        # for improving the assistant's performance
        
        return {
            "message": "Feedback submitted successfully",
            "timestamp": datetime.now().isoformat(),
            "feedback_id": f"fb_{int(datetime.now().timestamp())}"
        }
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.get("/conversations")
async def list_recent_conversations(
    limit: int = Query(10, ge=1, le=100, description="Number of conversations to return"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back")
):
    """List recent conversations (if context manager supports it)."""
    try:
        # This would typically query the context manager for recent conversations
        # For now, return a placeholder response
        return {
            "conversations": [],
            "total": 0,
            "timeframe": f"Last {hours} hours",
            "limit": limit,
            "message": "Conversation listing requires context manager implementation"
        }
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.get("/analytics")
async def get_usage_analytics():
    """Get usage analytics and statistics (if available)."""
    try:
        # This would typically pull from analytics storage
        # For now, return basic information
        return {
            "total_queries_processed": 0,
            "average_response_time": "0.0s",
            "most_common_intents": [],
            "success_rate": "0%",
            "active_conversations": 0,
            "message": "Analytics require implementation of usage tracking"
        }
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.post("/suggest")
async def suggest_queries(context: Dict[str, Any]):
    """Suggest relevant queries based on current context or recent activity."""
    try:
        # This would analyze context and suggest relevant queries
        # For now, return static suggestions
        suggestions = [
            "Show recent security alerts",
            "Check system health status", 
            "Find login anomalies",
            "Review network activity",
            "Analyze error patterns"
        ]
        
        return {
            "suggestions": suggestions,
            "context_analyzed": bool(context),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to generate suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Merged from assistant/router.py ---
"""
Assistant Router
Additional routing logic for conversational assistant endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from .pipeline import ConversationalPipeline

logger = logging.getLogger(__name__)

# Create router for assistant-specific endpoints
assistant_router = APIRouter(
    prefix="/v1",
    tags=["conversational-assistant"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get pipeline instance (will be injected by main app)
async def get_pipeline() -> ConversationalPipeline:
    """Dependency to get the pipeline instance from main app."""
    # This will be overridden by the main app
    pass

@assistant_router.get("/status")
async def get_detailed_status():
    """Get detailed status information about the assistant."""
    try:
        return {
            "service": "SIEM NLP Conversational Assistant",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": "Available",
            "features": [
                "Natural Language Processing",
                "Intent Classification",
                "Entity Extraction", 
                "Multi-SIEM Query Generation",
                "Response Formatting",
                "Conversation Context Management"
            ],
            "supported_siem_platforms": [
                "Elasticsearch",
                "Wazuh",
                "Splunk (via Universal Connector)",
                "Custom Log Sources"
            ]
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.get("/capabilities")
async def get_capabilities():
    """Get information about assistant capabilities and supported queries."""
    return {
        "natural_language_support": {
            "supported_languages": ["English"],
            "query_types": [
                "Security incident investigation",
                "Log analysis and filtering",
                "Threat hunting queries",
                "Performance monitoring",
                "Alert investigation",
                "Compliance reporting"
            ]
        },
        "intent_categories": [
            "search_logs",
            "analyze_alerts", 
            "investigate_incident",
            "monitor_performance",
            "generate_report",
            "hunt_threats"
        ],
        "entity_types": [
            "ip_address",
            "hostname", 
            "user_account",
            "file_path",
            "process_name",
            "timestamp",
            "event_type",
            "severity_level"
        ],
        "output_formats": [
            "structured_data",
            "visualizations",
            "summaries",
            "recommendations"
        ]
    }

@assistant_router.get("/examples")
async def get_query_examples():
    """Get example queries that users can try."""
    return {
        "security_queries": [
            "Show me failed login attempts in the last hour",
            "Find all alerts with high severity from yesterday", 
            "What processes were started by user admin today?",
            "Show me network connections to external IPs",
            "Find all file modifications in /etc/ directory"
        ],
        "investigation_queries": [
            "Investigate incident ID 12345",
            "What happened around 2023-10-01 15:30:00?",
            "Show me all events related to IP 192.168.1.100",
            "Find suspicious process executions on server01",
            "What files were accessed by compromised user account?"
        ],
        "monitoring_queries": [
            "Show system performance metrics",
            "What are the top 10 most frequent log sources?", 
            "Display network traffic patterns",
            "Show memory usage trends",
            "Find systems with high error rates"
        ]
    }

@assistant_router.post("/feedback")
async def submit_feedback(feedback_data: Dict[str, Any]):
    """Submit feedback about query results or assistant performance."""
    try:
        # Log feedback for analysis
        logger.info(f"User feedback received: {feedback_data}")
        
        # In a production system, this would store feedback in a database
        # for improving the assistant's performance
        
        return {
            "message": "Feedback submitted successfully",
            "timestamp": datetime.now().isoformat(),
            "feedback_id": f"fb_{int(datetime.now().timestamp())}"
        }
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.get("/conversations")
async def list_recent_conversations(
    limit: int = Query(10, ge=1, le=100, description="Number of conversations to return"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back")
):
    """List recent conversations (if context manager supports it)."""
    try:
        # This would typically query the context manager for recent conversations
        # For now, return a placeholder response
        return {
            "conversations": [],
            "total": 0,
            "timeframe": f"Last {hours} hours",
            "limit": limit,
            "message": "Conversation listing requires context manager implementation"
        }
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.get("/analytics")
async def get_usage_analytics():
    """Get usage analytics and statistics (if available)."""
    try:
        # This would typically pull from analytics storage
        # For now, return basic information
        return {
            "total_queries_processed": 0,
            "average_response_time": "0.0s",
            "most_common_intents": [],
            "success_rate": "0%",
            "active_conversations": 0,
            "message": "Analytics require implementation of usage tracking"
        }
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@assistant_router.post("/suggest")
async def suggest_queries(context: Dict[str, Any]):
    """Suggest relevant queries based on current context or recent activity."""
    try:
        # This would analyze context and suggest relevant queries
        # For now, return static suggestions
        suggestions = [
            "Show recent security alerts",
            "Check system health status", 
            "Find login anomalies",
            "Review network activity",
            "Analyze error patterns"
        ]
        
        return {
            "suggestions": suggestions,
            "context_analyzed": bool(context),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to generate suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))