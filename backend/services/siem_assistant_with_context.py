"""
Integration example showing how to use the Enhanced Context Manager
in your SIEM NLP Assistant backend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_context_manager import SIEMContextManager
import hashlib
import json
from datetime import datetime, timedelta

class SIEMAssistantWithContext:
    """SIEM Assistant enhanced with persistent context management."""
    
    def __init__(self):
        self.context_manager = SIEMContextManager("siem_assistant.db")
    
    def handle_user_query(self, user_id: str, query: str) -> dict:
        """Process user query with context awareness."""
        
        # Get user session context
        session = self.context_manager.get_user_session(user_id) or {}
        
        # Generate query hash for caching
        query_hash = hashlib.md5(f"{query}_{user_id}".encode()).hexdigest()
        
        # Check if we have cached results
        cached_results = self.context_manager.get_query_cache(query_hash)
        if cached_results:
            print(f"🚀 Returning cached results for: {query}")
            return cached_results
        
        # Process new query (simulate your existing NLP pipeline)
        processed_results = self._process_query(query, session)
        
        # Cache the results
        self.context_manager.set_query_cache(query_hash, processed_results, ttl=1800)  # 30 min
        
        # Update user session
        session['last_query'] = query
        session['last_query_time'] = datetime.now().isoformat()
        session['query_count'] = session.get('query_count', 0) + 1
        self.context_manager.set_user_session(user_id, session)
        
        return processed_results
    
    def start_investigation(self, user_id: str, investigation_name: str, initial_indicators: dict) -> str:
        """Start a new security investigation with context tracking."""
        
        investigation_id = f"inv_{int(datetime.now().timestamp())}"
        
        investigation_data = {
            "name": investigation_name,
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "indicators": initial_indicators,
            "timeline": [],
            "related_queries": []
        }
        
        # Store investigation with 7-day TTL
        self.context_manager.set_investigation(investigation_id, investigation_data, ttl=7*24*3600)
        
        print(f"🔍 Started investigation: {investigation_id}")
        return investigation_id
    
    def add_to_investigation(self, investigation_id: str, findings: dict):
        """Add findings to an existing investigation."""
        
        investigation = self.context_manager.get_investigation(investigation_id)
        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")
        
        # Add to timeline
        investigation["timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "findings": findings
        })
        
        # Update indicators
        if "indicators" in findings:
            for key, value in findings["indicators"].items():
                if key in investigation["indicators"]:
                    if isinstance(investigation["indicators"][key], list):
                        investigation["indicators"][key].extend(value)
                    else:
                        investigation["indicators"][key] = [investigation["indicators"][key], value]
                else:
                    investigation["indicators"][key] = value
        
        # Save updated investigation
        self.context_manager.set_investigation(investigation_id, investigation, ttl=7*24*3600)
        
        print(f"📝 Updated investigation: {investigation_id}")
    
    def generate_contextual_elasticsearch_query(self, investigation_id: str) -> dict:
        """Generate Elasticsearch query based on investigation context."""
        
        investigation = self.context_manager.get_investigation(investigation_id)
        if not investigation:
            return {"match_all": {}}
        
        # Use the enhanced context manager to build ES query
        es_query = self.context_manager.build_elasticsearch_context_query(
            "investigations", [investigation_id]
        )
        
        return es_query
    
    def get_related_investigations(self, current_investigation_id: str) -> list:
        """Find related investigations based on indicators."""
        
        current = self.context_manager.get_investigation(current_investigation_id)
        if not current:
            return []
        
        # Search for investigations with similar indicators
        related = []
        for indicator_type, values in current.get("indicators", {}).items():
            if isinstance(values, list):
                for value in values:
                    results = self.context_manager.search("investigations", str(value), limit=10)
                    related.extend(results)
            else:
                results = self.context_manager.search("investigations", str(values), limit=10)
                related.extend(results)
        
        # Remove current investigation and deduplicate
        related_ids = set()
        filtered_related = []
        for item in related:
            if item["key"] != current_investigation_id and item["key"] not in related_ids:
                related_ids.add(item["key"])
                filtered_related.append(item)
        
        return filtered_related[:5]  # Return top 5 related
    
    def _process_query(self, query: str, session_context: dict) -> dict:
        """Simulate your existing NLP query processing."""
        
        # This would integrate with your existing nlp_parser, query_generator, etc.
        return {
            "query": query,
            "processed_at": datetime.now().isoformat(),
            "elasticsearch_query": {"match": {"message": query}},
            "results_count": 42,  # Simulated
            "session_context_used": bool(session_context)
        }
    
    def get_dashboard_data(self, user_id: str) -> dict:
        """Get dashboard data with user context."""
        
        session = self.context_manager.get_user_session(user_id) or {}
        
        # Get user's recent investigations
        user_investigations = self.context_manager.search("investigations", user_id, limit=10)
        
        # Get recent queries
        recent_queries = session.get('recent_queries', [])
        
        # Context manager stats
        stats = self.context_manager.get_stats()
        
        return {
            "user_session": session,
            "active_investigations": user_investigations,
            "recent_queries": recent_queries,
            "system_stats": stats
        }


# Demo usage
if __name__ == "__main__":
    print("🛡️ SIEM Assistant with Enhanced Context Demo")
    
    assistant = SIEMAssistantWithContext()
    
    # Simulate user interactions
    user_id = "analyst_john"
    
    # First query
    result1 = assistant.handle_user_query(user_id, "show failed login attempts")
    print("Query 1 Result:", json.dumps(result1, indent=2))
    
    # Start investigation
    investigation_id = assistant.start_investigation(
        user_id, 
        "Suspicious Login Activity",
        {
            "ip_addresses": ["192.168.1.100", "10.0.0.50"],
            "usernames": ["admin_temp"],
            "time_range": {"gte": "2024-10-03T10:00:00Z"}
        }
    )
    
    # Add findings
    assistant.add_to_investigation(investigation_id, {
        "indicators": {
            "ip_addresses": ["172.16.1.25"],
            "processes": ["suspicious.exe"]
        },
        "severity": "high"
    })
    
    # Generate contextual ES query
    es_query = assistant.generate_contextual_elasticsearch_query(investigation_id)
    print("Generated ES Query:", json.dumps(es_query, indent=2))
    
    # Get dashboard data
    dashboard = assistant.get_dashboard_data(user_id)
    print("Dashboard Data:", json.dumps(dashboard, indent=2))
    
    print("Demo complete! 🎉")