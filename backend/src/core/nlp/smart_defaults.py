"""
Smart Defaults and Context-Aware AI Improvements
Reduces clarification requests by making intelligent assumptions
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SecurityContext(Enum):
    """Security context for queries"""
    INCIDENT_RESPONSE = "incident_response"
    THREAT_HUNTING = "threat_hunting"  
    ROUTINE_MONITORING = "routine_monitoring"
    COMPLIANCE_AUDIT = "compliance_audit"


class SmartDefaultsEngine:
    """AI engine that makes intelligent assumptions to reduce clarification requests"""
    
    def __init__(self):
        # Smart time window defaults based on query intent and security context
        self.time_defaults = {
            "security_alerts": {
                SecurityContext.INCIDENT_RESPONSE: "1h",
                SecurityContext.THREAT_HUNTING: "24h", 
                SecurityContext.ROUTINE_MONITORING: "24h",
                SecurityContext.COMPLIANCE_AUDIT: "7d"
            },
            "failed_logins": {
                SecurityContext.INCIDENT_RESPONSE: "30m",
                SecurityContext.THREAT_HUNTING: "6h",
                SecurityContext.ROUTINE_MONITORING: "1h", 
                SecurityContext.COMPLIANCE_AUDIT: "24h"
            },
            "show_failed_logins": {  # Add this intent mapping
                SecurityContext.INCIDENT_RESPONSE: "30m",
                SecurityContext.THREAT_HUNTING: "6h",
                SecurityContext.ROUTINE_MONITORING: "1h", 
                SecurityContext.COMPLIANCE_AUDIT: "24h"
            },
            "malware_detection": {
                SecurityContext.INCIDENT_RESPONSE: "1h",
                SecurityContext.THREAT_HUNTING: "24h",
                SecurityContext.ROUTINE_MONITORING: "6h",
                SecurityContext.COMPLIANCE_AUDIT: "30d"
            },
            "network_traffic": {
                SecurityContext.INCIDENT_RESPONSE: "30m",
                SecurityContext.THREAT_HUNTING: "2h",
                SecurityContext.ROUTINE_MONITORING: "1h",
                SecurityContext.COMPLIANCE_AUDIT: "24h"
            }
        }
        
        # Severity mapping for ambiguous terms
        self.severity_mapping = {
            "critical": ["critical", "high"],
            "important": ["high", "medium"], 
            "serious": ["high"],
            "minor": ["medium", "low"]
        }
        
        # Smart field suggestions
        self.field_suggestions = {
            "authentication": ["user", "source_ip", "event_id", "timestamp"],
            "network": ["src_ip", "dst_ip", "port", "protocol", "bytes"],
            "malware": ["file_hash", "file_path", "process_name", "user"]
        }

    def resolve_time_ambiguity(
        self, 
        query: str, 
        intent: str, 
        user_context: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Resolve time-related ambiguities with smart defaults
        
        Args:
            query: Original query
            intent: Detected intent
            user_context: User context and history
            
        Returns:
            Smart time window or None if clarification still needed
        """
        # Determine security context from query urgency indicators
        security_context = self._detect_security_context(query, user_context)
        
        # Check for time-related keywords
        time_keywords = {
            "recent": True,
            "latest": True,
            "current": True,
            "now": True,
            "immediate": True,
            "urgent": True
        }
        
        has_time_keyword = any(keyword in query.lower() for keyword in time_keywords)
        
        if has_time_keyword and intent in self.time_defaults:
            default_time = self.time_defaults[intent].get(
                security_context, 
                self.time_defaults[intent][SecurityContext.ROUTINE_MONITORING]
            )
            
            logger.info(f"Applied smart default time window: {default_time} for intent: {intent}")
            return default_time
            
        return None

    def resolve_severity_ambiguity(self, query: str) -> Optional[List[str]]:
        """Resolve severity-related ambiguities"""
        query_lower = query.lower()
        
        for ambiguous_term, mapped_severities in self.severity_mapping.items():
            if ambiguous_term in query_lower:
                logger.info(f"Mapped '{ambiguous_term}' to severities: {mapped_severities}")
                return mapped_severities
                
        return None

    def suggest_missing_fields(self, intent: str, entities: List[Dict]) -> List[str]:
        """Suggest useful fields that might be missing from the query"""
        if intent in self.field_suggestions:
            suggested = self.field_suggestions[intent]
            
            # Filter out fields that are already covered by entities
            entity_types = {entity.get("type") for entity in entities}
            missing_fields = [field for field in suggested if field not in entity_types]
            
            return missing_fields[:3]  # Limit to top 3 suggestions
            
        return []

    def enhance_query_with_defaults(
        self, 
        query: str, 
        intent: str, 
        entities: List[Dict],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Enhance query with smart defaults to reduce clarification needs
        
        Returns enhanced query parameters
        """
        enhancements = {
            "original_query": query,
            "enhanced": False,
            "applied_defaults": []
        }
        
        # Apply time defaults
        time_default = self.resolve_time_ambiguity(query, intent, user_context)
        if time_default:
            enhancements["time_window"] = time_default
            enhancements["enhanced"] = True
            enhancements["applied_defaults"].append(f"time_window: {time_default}")
        
        # Apply severity defaults  
        severity_default = self.resolve_severity_ambiguity(query)
        if severity_default:
            enhancements["severity_levels"] = severity_default
            enhancements["enhanced"] = True
            enhancements["applied_defaults"].append(f"severity: {severity_default}")
        
        # Suggest useful fields
        field_suggestions = self.suggest_missing_fields(intent, entities)
        if field_suggestions:
            enhancements["suggested_fields"] = field_suggestions
        
        return enhancements

    def _detect_security_context(
        self, 
        query: str, 
        user_context: Optional[Dict] = None
    ) -> SecurityContext:
        """Detect the security context from query and user context"""
        query_lower = query.lower()
        
        # Incident response indicators
        incident_keywords = ["urgent", "immediate", "alert", "breach", "attack", "compromise"]
        if any(keyword in query_lower for keyword in incident_keywords):
            return SecurityContext.INCIDENT_RESPONSE
        
        # Threat hunting indicators  
        hunting_keywords = ["hunt", "investigate", "suspicious", "anomal", "unusual"]
        if any(keyword in query_lower for keyword in hunting_keywords):
            return SecurityContext.THREAT_HUNTING
            
        # Compliance indicators
        compliance_keywords = ["compliance", "audit", "report", "policy", "regulation"]
        if any(keyword in query_lower for keyword in compliance_keywords):
            return SecurityContext.COMPLIANCE_AUDIT
            
        # Check user context for additional hints
        if user_context:
            user_role = user_context.get("role", "").lower()
            if "incident" in user_role or "soc" in user_role:
                return SecurityContext.INCIDENT_RESPONSE
            elif "audit" in user_role or "compliance" in user_role:
                return SecurityContext.COMPLIANCE_AUDIT
        
        # Default to routine monitoring
        return SecurityContext.ROUTINE_MONITORING


class AdvancedQueryPreprocessor:
    """Preprocesses queries to add context and reduce ambiguity"""
    
    def __init__(self):
        self.smart_defaults = SmartDefaultsEngine()
        
    def preprocess_query(
        self, 
        query: str, 
        intent: str, 
        entities: List[Dict],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Preprocess query to add intelligence and reduce clarification requests
        """
        # Apply smart defaults
        enhancements = self.smart_defaults.enhance_query_with_defaults(
            query, intent, entities, user_context
        )
        
        # Add contextual information
        processed = {
            "original_query": query,
            "processed_query": self._enhance_query_text(query, enhancements),
            "enhancements": enhancements,
            "needs_clarification": self._still_needs_clarification(enhancements),
            "confidence_boost": 0.2 if enhancements["enhanced"] else 0.0
        }
        
        return processed
    
    def _enhance_query_text(self, query: str, enhancements: Dict) -> str:
        """Enhance the query text with applied defaults"""
        enhanced_query = query
        
        if "time_window" in enhancements:
            enhanced_query += f" (time: {enhancements['time_window']})"
            
        if "severity_levels" in enhancements:
            enhanced_query += f" (severity: {', '.join(enhancements['severity_levels'])})"
            
        return enhanced_query
    
    def _still_needs_clarification(self, enhancements: Dict) -> bool:
        """Determine if clarification is still needed after applying defaults"""
        # If we successfully applied defaults, clarification is likely not needed
        return not enhancements.get("enhanced", False)


# Example usage in your pipeline:
"""
preprocessor = AdvancedQueryPreprocessor()

# Before classification
processed = preprocessor.preprocess_query(
    query="Show me recent security events",
    intent="security_alerts", 
    entities=[],
    user_context={"role": "SOC Analyst", "urgency": "high"}
)

if not processed["needs_clarification"]:
    # Use enhanced query with smart defaults
    enhanced_query = processed["processed_query"]
    time_window = processed["enhancements"].get("time_window", "24h")
    
    # Proceed with search using defaults
    # No clarification request needed!
else:
    # Still need clarification for complex cases
    pass
"""
