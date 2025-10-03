"""
Context Manager for maintaining conversation state.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages conversation context and session state."""
    
    def __init__(self, max_history: int = 50):
        """Initialize context manager."""
        self.max_history = max_history
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_data: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {
            'default_time_range': 'last_hour',
            'max_results': 100,
            'preferred_format': 'table'
        }
    
    def add_interaction(self, user_query: str, parsed_query: Dict[str, Any], 
                       siem_query: Dict[str, Any], results: List[Dict[str, Any]]):
        """Add an interaction to the conversation history."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_query': user_query,
            'parsed_query': parsed_query,
            'siem_query': siem_query,
            'results_count': len(results),
            'results_summary': self._summarize_results(results)
        }
        
        self.conversation_history.append(interaction)
        
        # Keep only recent interactions
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_conversation_context(self, num_interactions: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return self.conversation_history[-num_interactions:]
    
    def get_related_queries(self, current_query: str) -> List[Dict[str, Any]]:
        """Find related queries from conversation history."""
        related = []
        current_words = set(current_query.lower().split())
        
        for interaction in self.conversation_history:
            query_words = set(interaction['user_query'].lower().split())
            overlap = len(current_words.intersection(query_words))
            
            if overlap > 1:  # At least 2 words in common
                related.append({
                    'query': interaction['user_query'],
                    'timestamp': interaction['timestamp'],
                    'similarity_score': overlap / len(current_words.union(query_words))
                })
        
        # Sort by similarity score
        related.sort(key=lambda x: x['similarity_score'], reverse=True)
        return related[:3]  # Return top 3 related queries
    
    def update_session_data(self, key: str, value: Any):
        """Update session data."""
        self.session_data[key] = value
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        return self.session_data.get(key, default)
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference."""
        self.user_preferences[key] = value
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference."""
        return self.user_preferences.get(key, default)
    
    def get_query_suggestions(self, partial_query: str = "") -> List[str]:
        """Get query suggestions based on history and partial input."""
        suggestions = []
        
        # Add suggestions from recent queries
        for interaction in self.conversation_history[-10:]:
            query = interaction['user_query']
            if partial_query.lower() in query.lower():
                suggestions.append(query)
        
        # Add common query patterns
        common_patterns = [
            "Show me failed login attempts from the last hour",
            "Find all high severity alerts today",
            "Count security events from IP 192.168.1.100",
            "Search for malware detection in the last 24 hours",
            "Display network anomalies this week",
            "Show user authentication failures",
            "Find DNS queries to suspicious domains",
            "Analyze traffic patterns for unusual activity"
        ]
        
        for pattern in common_patterns:
            if not partial_query or partial_query.lower() in pattern.lower():
                if pattern not in suggestions:
                    suggestions.append(pattern)
        
        return suggestions[:5]
    
    def _summarize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of query results."""
        if not results:
            return {'count': 0}
        
        summary = {
            'count': len(results),
            'sample_fields': list(results[0].keys()) if results else [],
            'has_timestamps': any('@timestamp' in str(result) for result in results),
            'has_ip_addresses': any('ip' in str(result).lower() for result in results)
        }
        
        return summary
    
    def clear_session(self):
        """Clear current session data."""
        self.conversation_history = []
        self.session_data = {}
    
    def export_session(self) -> str:
        """Export session data as JSON."""
        export_data = {
            'conversation_history': self.conversation_history,
            'session_data': self.session_data,
            'user_preferences': self.user_preferences,
            'export_timestamp': datetime.now().isoformat()
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_session(self, session_json: str):
        """Import session data from JSON."""
        try:
            data = json.loads(session_json)
            self.conversation_history = data.get('conversation_history', [])
            self.session_data = data.get('session_data', {})
            self.user_preferences.update(data.get('user_preferences', {}))
            logger.info("Session data imported successfully")
        except Exception as e:
            logger.error(f"Failed to import session data: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_queries = len(self.conversation_history)
        
        if total_queries == 0:
            return {'total_queries': 0}
        
        # Calculate average results per query
        total_results = sum(interaction['results_count'] for interaction in self.conversation_history)
        avg_results = total_results / total_queries if total_queries > 0 else 0
        
        # Find most common query types
        query_types = [interaction['parsed_query'].get('intent', 'unknown') 
                      for interaction in self.conversation_history]
        
        return {
            'total_queries': total_queries,
            'average_results_per_query': round(avg_results, 2),
            'session_duration': self._calculate_session_duration(),
            'most_common_intents': self._get_most_common(query_types)
        }
    
    def _calculate_session_duration(self) -> str:
        """Calculate session duration."""
        if len(self.conversation_history) < 2:
            return "0 minutes"
        
        start_time = datetime.fromisoformat(self.conversation_history[0]['timestamp'])
        end_time = datetime.fromisoformat(self.conversation_history[-1]['timestamp'])
        duration = end_time - start_time
        
        return f"{duration.total_seconds() / 60:.1f} minutes"
    
    def _get_most_common(self, items: List[str], top_n: int = 3) -> List[Dict[str, Any]]:
        """Get most common items in a list."""
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{'item': item, 'count': count} for item, count in sorted_items[:top_n]]