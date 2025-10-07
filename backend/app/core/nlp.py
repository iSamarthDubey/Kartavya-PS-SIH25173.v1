"""
Kartavya SIEM NLP Module
Consolidated NLP processing for intent classification and entity extraction
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
import re
from datetime import datetime, timedelta
import dateparser

class QueryIntent(Enum):
    """Query intent types"""
    SEARCH_LOGS = "search_logs"
    AUTHENTICATION = "authentication"
    NETWORK_SECURITY = "network_security"
    MALWARE_DETECTION = "malware_detection"
    USER_ACTIVITY = "user_activity"
    SYSTEM_HEALTH = "system_health"
    THREAT_HUNTING = "threat_hunting"
    COMPLIANCE_CHECK = "compliance_check"
    INCIDENT_INVESTIGATION = "incident_investigation"
    REPORT_GENERATION = "report_generation"

class NLPProcessor:
    """Unified NLP processor for SIEM queries"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        
    def process_query(self, query: str) -> Dict:
        """Process natural language query"""
        intent = self.classify_intent(query)
        entities = self.extract_entities(query)
        
        return {
            "intent": intent,
            "entities": entities,
            "original_query": query,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Classify query intent with confidence score"""
        # Implementation will be merged from intent_classifier.py
        pass
        
    def extract_entities(self, query: str) -> List[Dict]:
        """Extract entities from query"""
        # Implementation will be merged from entity_extractor.py
        pass
        
    def _load_intent_patterns(self) -> Dict:
        """Load intent classification patterns"""
        return {
            QueryIntent.AUTHENTICATION: [
                r"(failed|successful)?\s*(login|logon|auth|authentication)",
                r"(password|credential)\s*(reset|change|expire)",
                r"mfa|multi.?factor|two.?factor"
            ],
            QueryIntent.MALWARE_DETECTION: [
                r"malware|virus|trojan|ransomware",
                r"(suspicious|malicious)\s*(file|process|activity)",
                r"threat\s*detect"
            ],
            # Add more patterns
        }
        
    def _load_entity_patterns(self) -> Dict:
        """Load entity extraction patterns"""
        return {
            "ip_address": r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}",
            "username": r"user[:\s]+([a-zA-Z0-9_.-]+)",
            "domain": r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}",
            "time_range": r"(last|past|previous)\s+(\d+)\s+(hour|day|week|month)s?",
            # Add more patterns
        }
