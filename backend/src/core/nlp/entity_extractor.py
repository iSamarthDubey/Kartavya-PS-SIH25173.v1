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
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute value with dict-like interface for backwards compatibility."""
        return getattr(self, key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "value": self.value,
            "confidence": self.confidence,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos
        }


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
                # Enhanced patterns for smart defaults
                r'\b(recent|recently|latest|current|now)\b',
                r'\b(immediate|urgent|asap)\b',
                r'\b(in the (last|past))\s*(\w+)\b'
            ],
            
            'severity': [
                r'\b(critical|high|medium|low|info|warning|error|debug)\s+(?:level|severity|priority)\b',
                r'\b(?:level|severity|priority)[:\s]+(critical|high|medium|low|info|warning|error|debug)\b',
            ],
            
            'log_source': [
                r'\bfrom\s+(windows|linux|apache|nginx|iis|firewall|router|switch)\b',
                r'\bsource[:\s]+(windows|linux|apache|nginx|iis|firewall|router|switch)\b',
                r'\b(syslog|eventlog|audit|firewall)\s+(?:logs?|events?)\b',
            ],
            
            'security_context': [
                r'\b(incident|breach|attack|compromise|threat)\b',
                r'\b(urgent|immediate|critical|emergency)\b',
                r'\b(investigate|hunt|analyze|review)\b',
                r'\b(compliance|audit|policy|regulation)\b'
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