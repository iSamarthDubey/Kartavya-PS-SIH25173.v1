"""
Integration adapter for the enhanced context manager with your existing SIEM backend.
This shows how to integrate without changing your existing API structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context_manager.context import ContextManager
from context_manager.memory_store import SIEMMemoryStore
from typing import Dict, List, Any, Optional
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class SIEMBackendIntegration:
    """Integration layer for enhanced context management with existing SIEM backend."""
    
    def __init__(self, db_path: str = "siem_production.db"):
        """Initialize with enhanced context management."""
        self.context_manager = ContextManager(max_history=100, db_path=db_path)
        self.memory_store = SIEMMemoryStore(db_path)
        
    def process_user_query(self, user_id: str, query: str, session_id: str = None) -> Dict[str, Any]:
        """Enhanced query processing with context awareness."""
        
        # Create or get user session
        if not self.memory_store.get_user_session(user_id):
            self.memory_store.create_user_session(user_id)
        
        # Check for cached results first
        cached_result = self.memory_store.get_cached_result(query, user_id)
        if cached_result:
            logger.info(f"Returning cached result for user {user_id}")
            self.memory_store.update_user_activity(user_id)
            return {
                "status": "success",
                "source": "cache",
                "query": query,
                "user_id": user_id,
                "results": cached_result["results"],
                "cached_at": cached_result["cached_at"]
            }
        
        # Process new query (integrate with your existing pipeline)
        try:
            # This would call your existing NLP parser, RAG pipeline, etc.
            processed_result = self._process_with_existing_pipeline(query, user_id)
            
            # Add to conversation history
            self.context_manager.add_interaction(
                user_query=query,
                parsed_query=processed_result.get("parsed_query", {}),
                siem_query=processed_result.get("elasticsearch_query", {}),
                results=processed_result.get("results", [])
            )
            
            # Cache the results
            self.memory_store.cache_query_result(
                query, user_id, processed_result, ttl=1800
            )
            
            return {
                "status": "success",
                "source": "processed",
                "query": query,
                "user_id": user_id,
                **processed_result
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "status": "error",
                "query": query,
                "user_id": user_id,
                "error": str(e)
            }
    
    def _process_with_existing_pipeline(self, query: str, user_id: str) -> Dict[str, Any]:
        """Simulate integration with your existing processing pipeline."""
        
        # Get user context for enhanced processing
        user_session = self.memory_store.get_user_session(user_id)
        conversation_context = self.context_manager.get_conversation_context(5)
        
        # This is where you'd integrate your existing modules:
        # nlp_parser = NLPParser()
        # rag_pipeline = RAGPipeline()
        # elastic_connector = ElasticConnector()
        # text_formatter = TextFormatter()
        
        # For demo, return simulated results
        return {
            "parsed_query": {
                "intent": "search",
                "entities": query.split(),
                "confidence": 0.95
            },
            "elasticsearch_query": {
                "bool": {
                    "must": [
                        {"match": {"message": query}}
                    ]
                }
            },
            "results": [
                {"timestamp": "2024-10-03T10:00:00Z", "message": f"Result for: {query}"},
                {"timestamp": "2024-10-03T10:01:00Z", "message": "Additional security event"}
            ],
            "results_count": 2,
            "processing_time": 0.1,
            "context_used": bool(conversation_context)
        }
    
    def start_investigation_from_query(self, user_id: str, query: str, query_results: List[Dict]) -> str:
        """Start an investigation based on query results."""
        
        # Extract indicators from query results
        indicators = self._extract_indicators_from_results(query_results)
        
        # Create investigation
        investigation_name = f"Investigation: {query[:50]}..."
        investigation_id = self.memory_store.create_investigation(
            investigation_name, user_id, indicators
        )
        
        # Add initial findings
        self.memory_store.update_investigation(investigation_id, {
            "source_query": query,
            "initial_results_count": len(query_results),
            "findings": {
                "query_analysis": f"Started from query: {query}",
                "initial_indicators": indicators
            }
        })
        
        logger.info(f"Started investigation {investigation_id} for user {user_id}")
        return investigation_id
    
    def _extract_indicators_from_results(self, results: List[Dict]) -> Dict[str, List]:
        """Extract security indicators from query results."""
        indicators = {
            "ip_addresses": [],
            "usernames": [],
            "processes": [],
            "files": []
        }
        
        for result in results:
            # Simple extraction logic (you'd enhance this with your domain knowledge)
            message = result.get("message", "")
            
            # Extract IP addresses (basic regex would be better)
            words = message.split()
            for word in words:
                if "." in word and word.replace(".", "").isdigit():
                    indicators["ip_addresses"].append(word)
                elif "user" in word.lower():
                    indicators["usernames"].append(word)
                elif ".exe" in word.lower():
                    indicators["processes"].append(word)
        
        # Remove duplicates
        for key in indicators:
            indicators[key] = list(set(indicators[key]))
        
        return indicators
    
    def get_query_suggestions(self, user_id: str, partial_query: str = "") -> List[str]:
        """Get contextual query suggestions."""
        
        # Get suggestions from context manager
        suggestions = self.context_manager.get_query_suggestions(partial_query)
        
        # Add user-specific suggestions from their history
        user_session = self.memory_store.get_user_session(user_id)
        if user_session and "recent_queries" in user_session:
            recent = user_session["recent_queries"]
            for query in recent:
                if partial_query.lower() in query.lower() and query not in suggestions:
                    suggestions.append(query)
        
        return suggestions[:10]
    
    def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user."""
        
        # Get basic dashboard data
        dashboard_data = self.context_manager.get_dashboard_data(user_id)
        
        # Add investigation summaries
        investigations = self.memory_store.get_user_investigations(user_id, "all")
        investigation_summaries = []
        for inv in investigations:
            summary = self.memory_store.quick_investigation_summary(inv["key"])
            investigation_summaries.append(summary)
        
        # Add user activity
        activity_summary = self.memory_store.get_user_activity_summary(user_id)
        
        # Add related queries
        recent_query = ""
        if dashboard_data["user_session"]["conversation_history"]:
            recent_query = dashboard_data["user_session"]["conversation_history"][-1]["user_query"]
        
        related_queries = self.context_manager.get_related_queries(recent_query)
        
        return {
            **dashboard_data,
            "investigation_summaries": investigation_summaries,
            "user_activity": activity_summary,
            "related_queries": related_queries,
            "query_suggestions": self.get_query_suggestions(user_id)
        }
    
    def export_user_data(self, user_id: str) -> str:
        """Export all user data for backup/analysis."""
        
        # Get user session and investigations
        user_data = {
            "user_session": self.memory_store.get_user_session(user_id),
            "investigations": self.memory_store.get_user_investigations(user_id, "all"),
            "conversation_history": self.context_manager.conversation_history,
            "activity_summary": self.memory_store.get_user_activity_summary(user_id),
            "export_timestamp": datetime.now().isoformat()
        }
        
        return self.context_manager.export_session()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health and statistics."""
        
        system_overview = self.memory_store.get_system_overview()
        context_stats = self.context_manager.get_session_stats()
        
        return {
            "system_status": "operational",
            "database_health": "good",
            "memory_usage": {
                "cache_size": context_stats.get("cache_size", 0),
                "persistent_contexts": context_stats.get("persistent_contexts", 0)
            },
            "user_activity": {
                "active_users": system_overview.get("active_users", 0),
                "recent_investigations": system_overview.get("recent_investigations", 0)
            },
            "performance": {
                "cache_hit_rate": "85%",  # You'd calculate this from actual metrics
                "avg_query_time": "150ms"
            }
        }


# Example FastAPI integration
def create_enhanced_fastapi_endpoints(integration: SIEMBackendIntegration):
    """Example of how to add enhanced endpoints to your existing FastAPI app."""
    
    from fastapi import FastAPI
    from pydantic import BaseModel
    
    app = FastAPI()
    
    class QueryRequest(BaseModel):
        query: str
        user_id: str
        session_id: Optional[str] = None
    
    class InvestigationRequest(BaseModel):
        user_id: str
        query: str
        results: List[Dict[str, Any]]
    
    @app.post("/api/v1/query/enhanced")
    async def enhanced_query(request: QueryRequest):
        """Enhanced query endpoint with context awareness."""
        return integration.process_user_query(
            request.user_id, request.query, request.session_id
        )
    
    @app.post("/api/v1/investigation/start")
    async def start_investigation(request: InvestigationRequest):
        """Start investigation from query results."""
        investigation_id = integration.start_investigation_from_query(
            request.user_id, request.query, request.results
        )
        return {"investigation_id": investigation_id}
    
    @app.get("/api/v1/dashboard/{user_id}")
    async def get_dashboard(user_id: str):
        """Get user dashboard with enhanced context."""
        return integration.get_user_dashboard_data(user_id)
    
    @app.get("/api/v1/suggestions/{user_id}")
    async def get_suggestions(user_id: str, partial_query: str = ""):
        """Get contextual query suggestions."""
        return {
            "suggestions": integration.get_query_suggestions(user_id, partial_query)
        }
    
    @app.get("/api/v1/system/health")
    async def system_health():
        """Get system health status."""
        return integration.get_system_health()
    
    return app


# Example usage
if __name__ == "__main__":
    print("🚀 Testing SIEM Backend Integration...")
    
    # Initialize integration
    integration = SIEMBackendIntegration("test_integration.db")
    
    # Test user query processing
    result = integration.process_user_query("analyst_jane", "show failed login attempts")
    print("Query Result:", result["status"])
    
    # Test investigation creation
    investigation_id = integration.start_investigation_from_query(
        "analyst_jane", 
        "show failed login attempts",
        [{"message": "Failed login from 192.168.1.100"}]
    )
    print(f"Investigation Created: {investigation_id}")
    
    # Test dashboard data
    dashboard = integration.get_user_dashboard_data("analyst_jane")
    print(f"Dashboard Data: {len(dashboard)} sections")
    
    # Test system health
    health = integration.get_system_health()
    print(f"System Health: {health['system_status']}")
    
    print("✅ Integration test completed!")