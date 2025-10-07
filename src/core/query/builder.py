"""
Query Builder
Builds Elasticsearch DSL queries from NLP components
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class QueryBuilder:
    """
    Builds SIEM queries from intent, entities, and field mappings
    """
    
    def __init__(self):
        """Initialize query builder"""
        self.query_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load query templates for common patterns"""
        return {
            "authentication_failure": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"event.action": "authentication_failure"}},
                            {"match": {"event.outcome": "failure"}}
                        ]
                    }
                }
            },
            "malware_detection": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"event.category": "malware"}}
                        ]
                    }
                }
            },
            "network_activity": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"event.category": "network"}}
                        ]
                    }
                }
            }
        }
    
    async def build(
        self,
        intent: str,
        entities: List[Dict[str, Any]],
        field_mappings: Dict[str, List[str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a SIEM query from components
        
        Args:
            intent: Query intent
            entities: Extracted entities
            field_mappings: Field mappings from schema mapper
            context: Conversation context
            
        Returns:
            SIEM query dictionary
        """
        # Start with base query structure
        query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            },
            "size": 100,
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        # Add intent-based clauses
        self._add_intent_clauses(query, intent)
        
        # Add entity-based clauses
        self._add_entity_clauses(query, entities, field_mappings)
        
        # Add time range
        time_range = self._extract_time_range(entities)
        if time_range:
            query["query"]["bool"]["filter"].append({
                "range": {
                    "@timestamp": time_range
                }
            })
        
        # Add context filters if available
        if context and context.get("filters"):
            self._apply_context_filters(query, context["filters"])
        
        # Clean up empty clauses
        query = self._clean_query(query)
        
        # Add aggregations if needed
        if self._should_aggregate(intent):
            query["aggs"] = self._build_aggregations(intent, entities)
        
        return query
    
    def _add_intent_clauses(self, query: Dict, intent: str) -> None:
        """Add clauses based on intent"""
        intent_mappings = {
            "failed_login": [
                {"match": {"event.action": "authentication_failure"}},
                {"match": {"event.outcome": "failure"}}
            ],
            "successful_login": [
                {"match": {"event.action": "authentication_success"}},
                {"match": {"event.outcome": "success"}}
            ],
            "malware": [
                {"match": {"event.category": "malware"}}
            ],
            "threat": [
                {"exists": {"field": "threat.indicator"}}
            ],
            "network": [
                {"match": {"event.category": "network"}}
            ],
            "vpn": [
                {"match": {"service.name": "vpn"}}
            ],
            "anomaly": [
                {"match": {"event.action": "anomaly"}}
            ]
        }
        
        # Find matching intent
        for key, clauses in intent_mappings.items():
            if key in intent.lower():
                query["query"]["bool"]["must"].extend(clauses)
                break
    
    def _add_entity_clauses(
        self,
        query: Dict,
        entities: List[Dict[str, Any]],
        field_mappings: Dict[str, List[str]]
    ) -> None:
        """Add clauses based on extracted entities"""
        for entity in entities:
            entity_type = entity.get("type")
            entity_value = entity.get("value")
            
            if not entity_value:
                continue
            
            # Skip time entities (handled separately)
            if entity_type == "time_range":
                continue
            
            # Get field mappings for this entity
            if entity_value in field_mappings:
                fields = field_mappings[entity_value]
                
                if len(fields) == 1:
                    # Single field match
                    field = fields[0]
                    if ":" in field:
                        # Field has value specified
                        field_name, field_value = field.split(":", 1)
                        query["query"]["bool"]["must"].append({
                            "match": {field_name: field_value}
                        })
                    else:
                        # Use entity value
                        query["query"]["bool"]["must"].append({
                            "match": {field: entity_value}
                        })
                elif len(fields) > 1:
                    # Multiple fields - use should clause
                    should_clauses = []
                    for field in fields:
                        if ":" in field:
                            field_name, field_value = field.split(":", 1)
                            should_clauses.append({
                                "match": {field_name: field_value}
                            })
                        else:
                            should_clauses.append({
                                "match": {field: entity_value}
                            })
                    
                    query["query"]["bool"]["must"].append({
                        "bool": {"should": should_clauses, "minimum_should_match": 1}
                    })
    
    def _extract_time_range(self, entities: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Extract time range from entities"""
        for entity in entities:
            if entity.get("type") == "time_range":
                value = entity.get("value")
                if isinstance(value, dict):
                    return value
                elif isinstance(value, str):
                    # Parse time string
                    return self._parse_time_string(value)
        
        # Default to last 24 hours if no time specified
        return {"gte": "now-24h", "lte": "now"}
    
    def _parse_time_string(self, time_str: str) -> Dict[str, str]:
        """Parse natural language time string"""
        time_lower = time_str.lower()
        
        if "hour" in time_lower:
            if "1" in time_lower or "one" in time_lower:
                return {"gte": "now-1h", "lte": "now"}
            elif "24" in time_lower:
                return {"gte": "now-24h", "lte": "now"}
        elif "day" in time_lower:
            if "1" in time_lower or "one" in time_lower or "yesterday" in time_lower:
                return {"gte": "now-1d", "lte": "now"}
            elif "7" in time_lower or "week" in time_lower:
                return {"gte": "now-7d", "lte": "now"}
        elif "month" in time_lower:
            return {"gte": "now-30d", "lte": "now"}
        
        # Default
        return {"gte": "now-24h", "lte": "now"}
    
    def _apply_context_filters(self, query: Dict, filters: Dict[str, Any]) -> None:
        """Apply filters from context"""
        for field, value in filters.items():
            if field == "severity":
                query["query"]["bool"]["filter"].append({
                    "match": {"event.severity": value}
                })
            elif field == "host":
                query["query"]["bool"]["filter"].append({
                    "match": {"host.name": value}
                })
    
    def _clean_query(self, query: Dict) -> Dict:
        """Remove empty clauses from query"""
        bool_query = query["query"]["bool"]
        
        # Remove empty arrays
        for clause in ["must", "filter", "should", "must_not"]:
            if clause in bool_query and not bool_query[clause]:
                del bool_query[clause]
        
        # If no clauses, add match_all
        if not any(bool_query.get(c) for c in ["must", "filter", "should", "must_not"]):
            query["query"] = {"match_all": {}}
        
        return query
    
    def _should_aggregate(self, intent: str) -> bool:
        """Check if aggregations should be added"""
        aggregate_intents = [
            "report", "summary", "statistics", "count", "top", "trend"
        ]
        return any(term in intent.lower() for term in aggregate_intents)
    
    def _build_aggregations(self, intent: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build aggregations based on intent"""
        aggs = {}
        
        if "top" in intent.lower():
            # Top N aggregation
            aggs["top_items"] = {
                "terms": {
                    "field": "source.ip",
                    "size": 10
                }
            }
        elif "trend" in intent.lower() or "time" in intent.lower():
            # Time series aggregation
            aggs["time_series"] = {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "1h"
                }
            }
        else:
            # Default: count by severity
            aggs["severity_breakdown"] = {
                "terms": {
                    "field": "event.severity",
                    "size": 5
                }
            }
        
        return aggs
    
    def build_simple_search(self, search_string: str) -> Dict[str, Any]:
        """Build a simple text search query"""
        return {
            "query": {
                "query_string": {
                    "query": search_string,
                    "default_field": "message",
                    "default_operator": "AND"
                }
            },
            "size": 100,
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
