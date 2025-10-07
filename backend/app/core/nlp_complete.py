"""
Kartavya SIEM NLP Module - Complete Implementation
Consolidated from intent_classifier.py and entity_extractor.py
"""

import re
from typing import List, Dict, Tuple, Optional
from enum import Enum
from datetime import datetime, timedelta
import dateparser


# --- Intent Classification ---
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
                r'\bbrute\s?force\b'
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
                r'\b(ids|ips)\s+(alert|trigger)\b'
            ],
            
            QueryIntent.USER_ACTIVITY: [
                r'\buser\s+(activity|behavior|action)\b',
                r'\b(privilege|permission)\s+(escalation|change)\b',
                r'\baccount\s+(creation|deletion|modification)\b',
                r'\bfile\s+(access|modification|deletion)\b',
                r'\badmin\s+(activity|action)\b'
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

# --- Entity Extraction ---
"""
Entity Extraction for SIEM NLP Queries
Extracts entities like IP addresses, usernames, time ranges, etc.
"""

import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import os

# Optional spaCy support (flag-gated)
_USE_SPACY = os.environ.get('ASSISTANT_USE_SPACY', 'false').lower() in ('1', 'true', 'yes')
try:
    import spacy  # noqa: F401
    _SPACY_AVAILABLE = True
except Exception:
    _SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity."""
    type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int


class EntityExtractor:
    """Extracts entities from natural language SIEM queries."""
    
    def __init__(self):
        """Initialize entity extraction patterns."""
        self.patterns = {
            'ip_address': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',  # IPv6
                r'\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b',  # IPv6 compressed
            ],
            
            'username': [
                r'\buser(?:name)?[:\s]+([a-zA-Z0-9_.-]+)\b',
                r'\baccount[:\s]+([a-zA-Z0-9_.-]+)\b',
                r'\blogin[:\s]+([a-zA-Z0-9_.-]+)\b',
                r'\b(?:for|by|from)\s+user\s+([a-zA-Z0-9_.-]+)\b',
                r'\b([a-zA-Z0-9_.-]+)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',  # Email
            ],
            
            'domain': [
                r'\b([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b',
                r'\bdomain[:\s]+([a-zA-Z0-9.-]+)\b',
            ],
            
            'file_path': [
                r'\b[C-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*\b',  # Windows
                r'\b/(?:[^/\s]+/)*[^/\s]*\b',  # Unix/Linux
                r'\b\\\\[^\\]+\\[^\\]+(?:\\[^\\]+)*\b',  # UNC path
            ],
            
            'port': [
                r'\bport[:\s]+([0-9]{1,5})\b',
                r'\b:([0-9]{1,5})\b',
                r'\b([0-9]{1,5})/(?:tcp|udp)\b',
            ],
            
            'process_name': [
                r'\bprocess[:\s]+([a-zA-Z0-9_.-]+(?:\.exe)?)\b',
                r'\bservice[:\s]+([a-zA-Z0-9_.-]+)\b',
                r'\b([a-zA-Z0-9_.-]+\.exe)\b',
            ],
            
            'event_id': [
                r'\bevent[:\s]*(?:id|code)[:\s]*([0-9]+)\b',
                r'\bcode[:\s]*([0-9]+)\b',
                r'\bid[:\s]*([0-9]+)\b',
            ],
            
            'hash': [
                r'\b[a-fA-F0-9]{32}\b',  # MD5
                r'\b[a-fA-F0-9]{40}\b',  # SHA1
                r'\b[a-fA-F0-9]{64}\b',  # SHA256
            ],
            
            'url': [
                r'\bhttps?://[^\s<>"{}|\\^`\[\]]+\b',
                r'\bftp://[^\s<>"{}|\\^`\[\]]+\b',
            ],
            
            'time_range': [
                r'\b(?:last|past|previous)\s+(\d+)\s+(minute|hour|day|week|month|year)s?\b',
                r'\b(today|yesterday|tomorrow)\b',
                r'\b(this|last)\s+(hour|day|week|month|year)\b',
                r'\bfrom\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+to\s+(\d{1,2}/\d{1,2}/\d{2,4})\b',
                r'\bsince\s+(\d{1,2}/\d{1,2}/\d{2,4})\b',
                r'\bbetween\s+(.+?)\s+and\s+(.+?)\b',
            ],
            
            'severity': [
                r'\b(critical|high|medium|low|info|warning|error|debug)\s+(?:level|severity|priority)\b',
                r'\b(?:level|severity|priority)[:\s]+(critical|high|medium|low|info|warning|error|debug)\b',
            ],
            
            'log_source': [
                r'\bfrom\s+(windows|linux|apache|nginx|iis|firewall|router|switch)\b',
                r'\bsource[:\s]+(windows|linux|apache|nginx|iis|firewall|router|switch)\b',
                r'\b(syslog|eventlog|audit|firewall)\s+(?:logs?|events?)\b',
            ]
        }
        
        # Time range parsing helpers
        self.time_units = {
            'minute': 'minutes',
            'minutes': 'minutes', 
            'hour': 'hours',
            'hours': 'hours',
            'day': 'days',
            'days': 'days',
            'week': 'weeks',
            'weeks': 'weeks',
            'month': 'months',
            'months': 'months',
            'year': 'years',
            'years': 'years'
        }
    
    def extract_entities(self, query: str) -> List[Entity]:
        """
        Extract all entities from a query string.
        
        Args:
            query: Natural language query
            
        Returns:
            List of extracted entities
        """
        entities = []

        # Optional spaCy enrichment first (adds hints, regex remains source of truth)
        if _USE_SPACY and _SPACY_AVAILABLE:
            try:
                nlp = spacy.load('en_core_web_sm')
                doc = nlp(query)
                # Heuristic: PERSON → username candidate; ORG/GPE often noisy, skip
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        val = ent.text.strip()
                        if val and 2 <= len(val) <= 32:
                            entities.append(Entity(type='username', value=val, confidence=0.6, start_pos=ent.start_char, end_pos=ent.end_char))
                    # DATE entities contribute to time phrase; leave regex to parse semantics
                    if ent.label_ == 'DATE':
                        entities.append(Entity(type='time_phrase', value=ent.text.strip(), confidence=0.5, start_pos=ent.start_char, end_pos=ent.end_char))
            except Exception:
                pass
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    # Get the captured group or full match
                    if match.groups():
                        value = match.group(1)
                        start = match.start(1)
                        end = match.end(1)
                    else:
                        value = match.group(0)
                        start = match.start()
                        end = match.end()
                    
                    # Validate and clean the entity
                    cleaned_value = self._clean_entity_value(entity_type, value)
                    if cleaned_value and self._validate_entity(entity_type, cleaned_value):
                        confidence = self._calculate_confidence(entity_type, cleaned_value, query)
                        
                        entity = Entity(
                            type=entity_type,
                            value=cleaned_value,
                            confidence=confidence,
                            start_pos=start,
                            end_pos=end
                        )
                        entities.append(entity)
        
        # Remove duplicates and overlapping entities
        entities = self._remove_duplicates(entities)
        
        # Sort by position in text
        entities.sort(key=lambda x: x.start_pos)
        
        logger.info(f"Extracted {len(entities)} entities from query")
        return entities
    
    def extract_time_range(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract and parse time range from query.
        
        Returns:
            Dictionary with 'start_time', 'end_time', and 'relative' fields
        """
        query_lower = query.lower()
        
        # Relative time patterns
        relative_patterns = [
            (r'\b(?:last|past|previous)\s+(\d+)\s+(minute|hour|day|week|month|year)s?\b', 'relative'),
            (r'\b(today|yesterday)\b', 'keyword'),
            (r'\b(this|last)\s+(hour|day|week|month|year)\b', 'relative_keyword'),
        ]
        
        for pattern, time_type in relative_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return self._parse_relative_time(match, time_type)
        
        # Absolute time patterns
        absolute_patterns = [
            r'\bfrom\s+(\d{1,2}/\d{1,2}/\d{2,4})\s+to\s+(\d{1,2}/\d{1,2}/\d{2,4})\b',
            r'\bsince\s+(\d{1,2}/\d{1,2}/\d{2,4})\b',
        ]
        
        for pattern in absolute_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return self._parse_absolute_time(match)
        
        return None
    
    def _clean_entity_value(self, entity_type: str, value: str) -> str:
        """Clean and normalize entity values."""
        if not value:
            return ""
            
        value = value.strip()
        
        if entity_type == 'username':
            # Remove common prefixes/suffixes
            value = re.sub(r'^(user|account|login)[:\s]*', '', value, flags=re.IGNORECASE)
            
        elif entity_type == 'port':
            # Extract just the port number
            port_match = re.search(r'(\d+)', value)
            if port_match:
                value = port_match.group(1)
                
        elif entity_type == 'event_id':
            # Extract just the numeric ID
            id_match = re.search(r'(\d+)', value)
            if id_match:
                value = id_match.group(1)
        
        return value
    
    def _validate_entity(self, entity_type: str, value: str) -> bool:
        """Validate extracted entities."""
        if not value:
            return False
            
        if entity_type == 'ip_address':
            # Validate IP address ranges
            if '.' in value:  # IPv4
                parts = value.split('.')
                return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts if part.isdigit())
            
        elif entity_type == 'port':
            try:
                port_num = int(value)
                return 1 <= port_num <= 65535
            except ValueError:
                return False
                
        elif entity_type == 'username':
            # Basic username validation
            return len(value) >= 2 and not value.isdigit()
            
        elif entity_type == 'domain':
            # Basic domain validation
            return '.' in value and not value.startswith('.') and not value.endswith('.')
        
        return True
    
    def _calculate_confidence(self, entity_type: str, value: str, context: str) -> float:
        """Calculate confidence score for extracted entity."""
        base_confidence = 0.7
        
        # Boost confidence based on context
        context_lower = context.lower()
        
        if entity_type == 'ip_address':
            if any(keyword in context_lower for keyword in ['ip', 'address', 'host', 'server']):
                base_confidence += 0.2
                
        elif entity_type == 'username':
            if any(keyword in context_lower for keyword in ['user', 'account', 'login', 'auth']):
                base_confidence += 0.2
                
        elif entity_type == 'port':
            if any(keyword in context_lower for keyword in ['port', 'service', 'connection']):
                base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _remove_duplicates(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate and overlapping entities."""
        if not entities:
            return entities
        
        # Sort by start position
        entities.sort(key=lambda x: x.start_pos)
        
        filtered = []
        last_end = -1
        
        for entity in entities:
            # Skip if overlapping with previous entity
            if entity.start_pos < last_end:
                # Keep the one with higher confidence
                if filtered and entity.confidence > filtered[-1].confidence:
                    filtered[-1] = entity
                continue
            
            filtered.append(entity)
            last_end = entity.end_pos
        
        return filtered
    
    def _parse_relative_time(self, match, time_type: str) -> Dict[str, Any]:
        """Parse relative time expressions."""
        now = datetime.now()
        
        if time_type == 'relative':
            amount = int(match.group(1))
            unit = self.time_units.get(match.group(2).lower(), 'hours')
            
            if unit == 'minutes':
                start_time = now - timedelta(minutes=amount)
            elif unit == 'hours':
                start_time = now - timedelta(hours=amount)
            elif unit == 'days':
                start_time = now - timedelta(days=amount)
            elif unit == 'weeks':
                start_time = now - timedelta(weeks=amount)
            elif unit == 'months':
                start_time = now - timedelta(days=amount * 30)  # Approximate
            elif unit == 'years':
                start_time = now - timedelta(days=amount * 365)  # Approximate
            else:
                start_time = now - timedelta(hours=1)  # Default
                
            return {
                'start_time': start_time,
                'end_time': now,
                'relative': True,
                'description': f"Last {amount} {unit}"
            }
            
        elif time_type == 'keyword':
            keyword = match.group(1)
            if keyword == 'today':
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                return {
                    'start_time': start_time,
                    'end_time': now,
                    'relative': True,
                    'description': 'Today'
                }
            elif keyword == 'yesterday':
                start_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                return {
                    'start_time': start_time,
                    'end_time': end_time,
                    'relative': True,
                    'description': 'Yesterday'
                }
        
        return None
    
    def _parse_absolute_time(self, match) -> Dict[str, Any]:
        """Parse absolute time expressions."""
        # This is a simplified implementation
        # In production, you'd want more robust date parsing
        return {
            'start_time': None,
            'end_time': None,
            'relative': False,
            'description': 'Absolute time range'
        }
    
    def get_entity_summary(self, entities: List[Entity]) -> Dict[str, List[str]]:
        """Get a summary of extracted entities by type."""
        summary = {}
        for entity in entities:
            if entity.type not in summary:
                summary[entity.type] = []
            if entity.value not in summary[entity.type]:
                summary[entity.type].append(entity.value)
        return summary


# Example usage and testing
if __name__ == "__main__":
    extractor = EntityExtractor()
    
    test_queries = [
        "Show failed logins from user john.doe@company.com on 192.168.1.100",
        "Find malware on port 443 in the last 24 hours",
        "Get system metrics for server.example.com from yesterday",
        "Search for event ID 4625 from domain controllers",
        "Show network traffic to 10.0.0.1 on port 80/tcp",
        "Find file access to C:\\Windows\\System32\\config\\sam",
        "List security alerts with high severity from last week"
    ]
    
    print("Entity Extraction Test:")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        entities = extractor.extract_entities(query)
        
        if entities:
            print("Extracted entities:")
            for entity in entities:
                print(f"  {entity.type}: {entity.value} (confidence: {entity.confidence:.2f})")
        else:
            print("  No entities found")
        
        # Test time range extraction
        time_range = extractor.extract_time_range(query)
        if time_range:
            print(f"Time range: {time_range['description']}")
        
        print("-" * 60)