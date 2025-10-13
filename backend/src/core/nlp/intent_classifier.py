"""
Intent Classification for SIEM NLP Queries
Detects user intent from natural language queries.
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Supported query intents."""
    SEARCH_LOGS = "search_logs"
    SHOW_FAILED_LOGINS = "show_failed_logins" 
    SHOW_SUCCESSFUL_LOGINS = "show_successful_logins"
    GET_SYSTEM_METRICS = "get_system_metrics"
    NETWORK_TRAFFIC = "network_traffic"
    SECURITY_ALERTS = "security_alerts"
    USER_ACTIVITY = "user_activity"
    SYSTEM_ERRORS = "system_errors"
    MALWARE_DETECTION = "malware_detection"
    THREAT_HUNTING = "threat_hunting"
    COMPLIANCE_CHECK = "compliance_check"
    UNKNOWN = "unknown"


class IntentClassifier:
    """Classifies user intent from natural language queries."""
    
    def __init__(self):
        """Initialize the intent classifier with pattern rules."""
        self.intent_patterns = {
            QueryIntent.SHOW_FAILED_LOGINS: [
                r'\b(failed|unsuccessful|denied|blocked)\s+(login|logon|authentication|signin|sign-in)\b',
                r'\bauth(entication)?\s+(fail|error|denied)\b',
                r'\blogin\s+(fail|error|attempt)\b',
                r'\b(4625|528|529|530|531|532|533|534|535|536|537|538|539)\b',  # Windows event codes
                r'\bssh\s+(fail|error|denied)\b',
                r'\bbrute\s?force\b',
                r'\b(bad|wrong|incorrect|invalid)\s+(password|credential)\b',
                r'\baccount\s+(lock|disabled|expired)\b',
                r'\b(winlogbeat|windows)\s+.*\s+(fail|error)\b',
                # Enhanced patterns for time-sensitive authentication queries
                r'\b(recent|latest|current)\s+(failed|unsuccessful)\s+(login|authentication)\b',
                r'\b(urgent|immediate)\s+(login|auth)\s+(fail|error)\b'
            ],
            
            QueryIntent.SHOW_SUCCESSFUL_LOGINS: [
                r'\b(successful|completed|accepted)\s+(login|logon|authentication|signin|sign-in)\b',
                r'\bauth(entication)?\s+(success|complete|accept)\b',
                r'\blogin\s+(success|complete)\b',
                r'\b(4624|540)\b',  # Windows successful login codes
                r'\bssh\s+(success|accept)\b'
            ],
            
            QueryIntent.GET_SYSTEM_METRICS: [
                r'\b(system|server|host)\s+(metric|performance|stat|health)\b',
                r'\b(cpu|memory|disk|network)\s+(usage|utilization|performance)\b',
                r'\bperformance\s+(counter|data|metric)\b',
                r'\bsystem\s+(load|health|status)\b'
            ],
            
            QueryIntent.NETWORK_TRAFFIC: [
                r'\bnetwork\s+(traffic|activity|connection|flow)\b',
                r'\b(bandwidth|throughput|packet)\b',
                r'\bfirewall\s+(log|rule|block|allow)\b',
                r'\b(tcp|udp|http|https)\s+(connection|traffic)\b',
                r'\bport\s+(scan|connect|open|closed)\b'
            ],
            
            QueryIntent.SECURITY_ALERTS: [
                r'\b(security|threat)\s+(alert|warning|event)\b',
                r'\b(malware|virus|trojan|ransomware)\b',
                r'\bintrusion\s+(detect|attempt)\b',
                r'\b(suspicious|malicious)\s+(activity|behavior)\b',
                r'\b(ids|ips)\s+(alert|trigger)\b',
                # Enhanced patterns for recent/urgent security events
                r'\b(recent|latest|current)\s+(security|threat|alert)\b',
                r'\b(urgent|immediate|critical)\s+(security|alert)\b',
                r'\bsecurity\s+(events?|incidents?)\b',
                r'\balert\s+(from|in|during)\b'
            ],
            
            QueryIntent.USER_ACTIVITY: [
                r'\buser\s+(activity|behavior|action)\b',
                r'\b(privilege|permission)\s+(escalation|change)\b',
                r'\baccount\s+(creation|deletion|modification)\b',
                r'\bfile\s+(access|modification|deletion)\b',
                r'\badmin\s+(activity|action)\b',
                r'\bprocess\s+(creation|start|launch)\b',
                r'\b4688\b',  # Windows process creation event
                r'\b(suspicious|unusual)\s+(process|executable)\b',
                r'\b(powershell|cmd|wscript|cscript)\s+(execution|run)\b'
            ],
            
            QueryIntent.SYSTEM_ERRORS: [
                r'\b(system|application|service)\s+(error|crash|fail)\b',
                r'\b(blue\s?screen|bsod)\b',
                r'\bservice\s+(stop|start|restart)\b',
                r'\berror\s+(code|event|log)\b',
                r'\b(critical|fatal)\s+(error|event)\b'
            ],
            
            QueryIntent.MALWARE_DETECTION: [
                r'\b(malware|virus|trojan|worm|rootkit)\s+(detect|found|quarantine)\b',
                r'\bantivirus\s+(alert|scan|detect)\b',
                r'\b(signature|heuristic)\s+(match|detect)\b',
                r'\bmalicious\s+(file|process|url)\b'
            ],
            
            QueryIntent.THREAT_HUNTING: [
                r'\bthreat\s+(hunt|search|investigation)\b',
                r'\b(ioc|indicator)\s+(compromise|threat)\b',
                r'\b(apt|advanced\s+persistent\s+threat)\b',
                r'\bhunt\s+(for|malware|threat)\b',
                r'\binvestigat(e|ion)\b'
            ],
            
            QueryIntent.COMPLIANCE_CHECK: [
                r'\bcompliance\s+(check|audit|report)\b',
                r'\b(gdpr|hipaa|pci|sox)\s+(compliance|audit)\b',
                r'\bpolicy\s+(violation|enforcement)\b',
                r'\baudit\s+(log|trail|report)\b'
            ]
        }
        
        # Keywords for general log search
        self.search_keywords = [
            'show', 'find', 'search', 'list', 'get', 'display', 'retrieve',
            'logs', 'events', 'records', 'entries', 'data'
        ]
    
    def classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """
        Classify the intent of a natural language query.
        
        Args:
            query: Natural language query string
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        query_lower = query.lower().strip()
        
        if not query_lower:
            return QueryIntent.UNKNOWN, 0.0
        
        # Check patterns for each intent
        best_intent = QueryIntent.UNKNOWN
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = self._calculate_pattern_score(query_lower, patterns)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # If no specific intent found but contains search keywords, classify as general search
        if best_intent == QueryIntent.UNKNOWN and best_score < 0.3:
            if any(keyword in query_lower for keyword in self.search_keywords):
                return QueryIntent.SEARCH_LOGS, 0.6
        
        # Minimum confidence threshold
        if best_score < 0.2:
            return QueryIntent.UNKNOWN, best_score
        
        logger.info(f"Classified intent: {best_intent.value} (confidence: {best_score:.2f})")
        return best_intent, best_score
    
    def _calculate_pattern_score(self, query: str, patterns: List[str]) -> float:
        """Calculate matching score for patterns."""
        scores = []
        
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                # Boost score for exact matches
                if re.search(r'\b' + re.escape(pattern.replace(r'\b', '')) + r'\b', query, re.IGNORECASE):
                    scores.append(1.0)
                else:
                    scores.append(0.7)
        
        # Return the MAXIMUM score - if ANY pattern matches strongly, intent is confident
        # This fixes the bug where having many patterns diluted the score
        if scores:
            return max(scores)
        
        return 0.0
    
    def get_intent_suggestions(self, query: str) -> List[Tuple[QueryIntent, float]]:
        """Get all possible intents with their confidence scores."""
        query_lower = query.lower().strip()
        suggestions = []
        
        for intent, patterns in self.intent_patterns.items():
            score = self._calculate_pattern_score(query_lower, patterns)
            if score > 0.1:  # Only include reasonable matches
                suggestions.append((intent, score))
        
        # Sort by confidence score
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions


def get_intent_description(intent: QueryIntent) -> str:
    """Get human-readable description of an intent."""
    descriptions = {
        QueryIntent.SEARCH_LOGS: "General log search and retrieval",
        QueryIntent.SHOW_FAILED_LOGINS: "Failed login attempts and authentication failures",
        QueryIntent.SHOW_SUCCESSFUL_LOGINS: "Successful login events and authentication",
        QueryIntent.GET_SYSTEM_METRICS: "System performance metrics and health data",
        QueryIntent.NETWORK_TRAFFIC: "Network traffic analysis and firewall logs",
        QueryIntent.SECURITY_ALERTS: "Security alerts and threat notifications",
        QueryIntent.USER_ACTIVITY: "User behavior and account activity",
        QueryIntent.SYSTEM_ERRORS: "System errors and application failures",
        QueryIntent.MALWARE_DETECTION: "Malware detection and antivirus alerts",
        QueryIntent.THREAT_HUNTING: "Threat hunting and security investigation",
        QueryIntent.COMPLIANCE_CHECK: "Compliance auditing and policy enforcement",
        QueryIntent.UNKNOWN: "Unknown or unsupported query type"
    }
    return descriptions.get(intent, "Unknown intent")


# Example usage and testing
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    test_queries = [
        "Show me failed login attempts from last hour",
        "Find malware detections in the system",
        "Get system performance metrics",
        "List all successful authentications today", 
        "Search for network traffic anomalies",
        "Show me security alerts",
        "Find user activity for admin accounts",
        "Display system errors from yesterday"
    ]
    
    print("Intent Classification Test:")
    print("=" * 50)
    
    for query in test_queries:
        intent, confidence = classifier.classify_intent(query)
        print(f"Query: {query}")
        print(f"Intent: {intent.value} (confidence: {confidence:.2f})")
        print(f"Description: {get_intent_description(intent)}")
        print("-" * 50)