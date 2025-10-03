"""
Memory Store utilities for the enhanced SIEM Context Manager.
Provides high-level interfaces for common operations.
"""

from .context import ContextManager
from typing import Dict, List, Any, Optional
import hashlib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SIEMMemoryStore:
    """High-level interface for SIEM context operations."""
    
    def __init__(self, db_path: str = "siem_contexts.db"):
        self.context_manager = ContextManager(db_path=db_path)
    
    # User Session Management
    def create_user_session(self, user_id: str, session_data: Dict[str, Any] = None) -> str:
        """Create a new user session."""
        session_data = session_data or {}
        session_data.update({
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "query_count": 0,
            "active_investigations": []
        })
        
        self.context_manager.set_persistent_context(
            "user_sessions", user_id, session_data, ttl=3600
        )
        return user_id
    
    def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp."""
        session = self.context_manager.get_persistent_context("user_sessions", user_id, {})
        session["last_activity"] = datetime.now().isoformat()
        session["query_count"] = session.get("query_count", 0) + 1
        
        self.context_manager.set_persistent_context(
            "user_sessions", user_id, session, ttl=3600
        )
    
    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data."""
        return self.context_manager.get_persistent_context("user_sessions", user_id)
    
    # Investigation Management
    def create_investigation(self, name: str, user_id: str, indicators: Dict[str, Any] = None) -> str:
        """Create a new investigation."""
        investigation_id = self.context_manager.start_investigation(name, indicators or {}, user_id)
        
        # Add to user's active investigations
        session = self.get_user_session(user_id) or {}
        active_invs = session.get("active_investigations", [])
        if investigation_id not in active_invs:
            active_invs.append(investigation_id)
            session["active_investigations"] = active_invs
            self.context_manager.set_persistent_context("user_sessions", user_id, session, ttl=3600)
        
        return investigation_id
    
    def update_investigation(self, investigation_id: str, findings: Dict[str, Any]):
        """Add findings to an investigation."""
        self.context_manager.add_to_investigation(investigation_id, findings)
    
    def close_investigation(self, investigation_id: str, user_id: str, resolution: str = ""):
        """Close an investigation."""
        investigation = self.context_manager.get_investigation(investigation_id)
        if investigation:
            investigation["status"] = "closed"
            investigation["closed_at"] = datetime.now().isoformat()
            investigation["resolution"] = resolution
            
            self.context_manager.set_persistent_context(
                "investigations", investigation_id, investigation, ttl=30*24*3600  # Keep for 30 days
            )
            
            # Remove from user's active investigations
            session = self.get_user_session(user_id) or {}
            active_invs = session.get("active_investigations", [])
            if investigation_id in active_invs:
                active_invs.remove(investigation_id)
                session["active_investigations"] = active_invs
                self.context_manager.set_persistent_context("user_sessions", user_id, session, ttl=3600)
    
    def get_user_investigations(self, user_id: str, status: str = "active") -> List[Dict[str, Any]]:
        """Get user's investigations by status."""
        all_investigations = self.context_manager.list_investigations(user_id)
        if status == "all":
            return all_investigations
        return [inv for inv in all_investigations if inv["value"].get("status") == status]
    
    # Query Caching
    def cache_query_result(self, query: str, user_id: str, results: Dict[str, Any], ttl: int = 1800):
        """Cache query results."""
        self.context_manager.cache_query_result(query, results, user_id, ttl)
        self.update_user_activity(user_id)
    
    def get_cached_result(self, query: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached query result."""
        return self.context_manager.get_cached_query_result(query, user_id)
    
    # Threat Intelligence Context
    def add_threat_indicator(self, indicator_type: str, value: str, metadata: Dict[str, Any] = None):
        """Add a threat indicator to context."""
        indicator_id = f"{indicator_type}_{hashlib.md5(value.encode()).hexdigest()[:8]}"
        
        indicator_data = {
            "type": indicator_type,
            "value": value,
            "added_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.context_manager.set_persistent_context(
            "threat_intel", indicator_id, indicator_data, ttl=7*24*3600
        )
    
    def get_threat_indicators(self, indicator_type: str = None) -> List[Dict[str, Any]]:
        """Get threat indicators."""
        results = self.context_manager.search_context("threat_intel", "", limit=1000)
        if indicator_type:
            results = [r for r in results if r["value"].get("type") == indicator_type]
        return results
    
    def check_against_threat_intel(self, value: str) -> List[Dict[str, Any]]:
        """Check if value matches any threat indicators."""
        return self.context_manager.search_context("threat_intel", value, limit=10)
    
    # Alert Context
    def store_alert_context(self, alert_id: str, alert_data: Dict[str, Any], ttl: int = 24*3600):
        """Store alert context."""
        self.context_manager.set_persistent_context(
            "alerts", alert_id, alert_data, ttl=ttl,
            metadata={"severity": alert_data.get("severity", "unknown")}
        )
    
    def get_related_alerts(self, indicators: List[str]) -> List[Dict[str, Any]]:
        """Find alerts related to given indicators."""
        related_alerts = []
        for indicator in indicators:
            results = self.context_manager.search_context("alerts", indicator, limit=20)
            related_alerts.extend(results)
        
        # Remove duplicates and sort by timestamp
        seen_ids = set()
        unique_alerts = []
        for alert in related_alerts:
            if alert["key"] not in seen_ids:
                seen_ids.add(alert["key"])
                unique_alerts.append(alert)
        
        return sorted(unique_alerts, 
                     key=lambda x: x["value"].get("timestamp", ""), reverse=True)[:10]
    
    # System Utilities
    def get_system_overview(self) -> Dict[str, Any]:
        """Get system overview and statistics."""
        stats = self.context_manager.get_session_stats()
        
        # Active users in last hour
        active_users = []
        user_sessions = self.context_manager.search_context("user_sessions", "", limit=100)
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        for session in user_sessions:
            last_activity = session["value"].get("last_activity")
            if last_activity:
                try:
                    activity_time = datetime.fromisoformat(last_activity)
                    if activity_time > cutoff_time:
                        active_users.append(session["key"])
                except ValueError:
                    pass
        
        # Recent investigations
        recent_investigations = self.context_manager.search_context("investigations", "", limit=10)
        
        return {
            "database_stats": stats,
            "active_users": len(active_users),
            "active_user_ids": active_users,
            "recent_investigations": len(recent_investigations),
            "system_health": "operational"
        }
    
    def cleanup_expired_data(self):
        """Manually trigger cleanup of expired data."""
        self.context_manager._cleanup_expired()
        logger.info("Manual cleanup completed")
    
    def backup_data(self, backup_path: str):
        """Backup all context data."""
        namespaces = ["user_sessions", "investigations", "query_cache", "threat_intel", "alerts"]
        
        for namespace in namespaces:
            export_path = f"{backup_path}_{namespace}.json"
            try:
                self.context_manager.export_namespace(namespace, export_path)
                logger.info(f"Backed up {namespace} to {export_path}")
            except Exception as e:
                logger.error(f"Failed to backup {namespace}: {e}")
    
    # Quick access methods for common operations
    def quick_investigation_summary(self, investigation_id: str) -> Dict[str, Any]:
        """Get a quick summary of an investigation."""
        investigation = self.context_manager.get_investigation(investigation_id)
        if not investigation:
            return {}
        
        return {
            "id": investigation_id,
            "name": investigation.get("name", "Unknown"),
            "status": investigation.get("status", "unknown"),
            "created_at": investigation.get("created_at", ""),
            "indicator_count": len(investigation.get("indicators", {})),
            "timeline_events": len(investigation.get("timeline", [])),
            "created_by": investigation.get("created_by", "unknown")
        }
    
    def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user activity summary."""
        session = self.get_user_session(user_id)
        if not session:
            return {"user_id": user_id, "status": "not_found"}
        
        investigations = self.get_user_investigations(user_id, "all")
        
        return {
            "user_id": user_id,
            "query_count": session.get("query_count", 0),
            "last_activity": session.get("last_activity", "unknown"),
            "active_investigations": len(session.get("active_investigations", [])),
            "total_investigations": len(investigations),
            "session_created": session.get("created_at", "unknown")
        }


# Global instance for easy access
memory_store = SIEMMemoryStore()


# Convenience functions
def get_store() -> SIEMMemoryStore:
    """Get the global memory store instance."""
    return memory_store


def init_store(db_path: str = "siem_contexts.db") -> SIEMMemoryStore:
    """Initialize memory store with custom database path."""
    global memory_store
    memory_store = SIEMMemoryStore(db_path)
    return memory_store