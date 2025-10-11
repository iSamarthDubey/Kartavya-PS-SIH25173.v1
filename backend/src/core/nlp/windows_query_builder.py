"""
Windows Security Query Builder for Elasticsearch
Builds optimized queries for Windows Security events from Beats data.
"""

import re
from typing import Dict, List, Any, Optional
from enum import Enum
import logging
from datetime import datetime, timedelta

from .intent_classifier import QueryIntent

logger = logging.getLogger(__name__)


class WindowsEventType(Enum):
    """Common Windows Security Event types."""
    LOGON_SUCCESS = "4624"
    LOGON_FAILURE = "4625"
    LOGOFF = "4634" 
    PROCESS_CREATION = "4688"
    PRIVILEGE_ASSIGNED = "4672"
    ACCOUNT_LOCKOUT = "4740"
    PASSWORD_CHANGE = "4723"
    USER_ACCOUNT_CREATED = "4720"
    USER_ACCOUNT_DELETED = "4726"
    SERVICE_START = "7034"
    SERVICE_STOP = "7035"


class WindowsQueryBuilder:
    """Builds Elasticsearch queries optimized for Windows Security logs via Beats."""
    
    def __init__(self):
        """Initialize Windows query builder."""
        self.default_time_range = "1h"
        
        # Windows Event ID mappings
        self.event_mappings = {
            QueryIntent.SHOW_FAILED_LOGINS: [
                WindowsEventType.LOGON_FAILURE.value,
                WindowsEventType.ACCOUNT_LOCKOUT.value
            ],
            QueryIntent.SHOW_SUCCESSFUL_LOGINS: [
                WindowsEventType.LOGON_SUCCESS.value
            ],
            QueryIntent.USER_ACTIVITY: [
                WindowsEventType.PROCESS_CREATION.value,
                WindowsEventType.PRIVILEGE_ASSIGNED.value,
                WindowsEventType.USER_ACCOUNT_CREATED.value,
                WindowsEventType.USER_ACCOUNT_DELETED.value,
                WindowsEventType.PASSWORD_CHANGE.value
            ],
            QueryIntent.SYSTEM_ERRORS: [
                WindowsEventType.SERVICE_START.value,
                WindowsEventType.SERVICE_STOP.value
            ]
        }
    
    def build_query(
        self,
        intent: QueryIntent,
        entities: List[Dict[str, Any]],
        query_text: str,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build Elasticsearch query for Windows Security events.
        
        Args:
            intent: Detected query intent
            entities: Extracted entities (user, IP, time, etc.)
            query_text: Original query text
            time_range: Time range filter
            
        Returns:
            Elasticsearch DSL query optimized for Windows Beats data
        """
        try:
            # Base query structure for winlogbeat data
            query_dsl = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"beat.name": "winlogbeat"}},
                            {"match": {"event.provider": "Microsoft-Windows-Security-Auditing"}}
                        ],
                        "filter": [],
                        "should": [],
                        "minimum_should_match": 0
                    }
                },
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": 100
            }
            
            # Add intent-specific filters
            self._add_intent_filters(query_dsl, intent)
            
            # Add entity filters
            self._add_entity_filters(query_dsl, entities)
            
            # Add time range filter
            self._add_time_filter(query_dsl, time_range or self.default_time_range)
            
            # Add keyword search if no specific intent
            if intent == QueryIntent.UNKNOWN or intent == QueryIntent.SEARCH_LOGS:
                self._add_keyword_search(query_dsl, query_text)
            
            logger.info(f"Built Windows query for intent: {intent.value}")
            return query_dsl
            
        except Exception as e:
            logger.error(f"Failed to build Windows query: {e}")
            return self._build_fallback_query(query_text, time_range)
    
    def _add_intent_filters(self, query_dsl: Dict[str, Any], intent: QueryIntent) -> None:
        """Add Windows event ID filters based on intent."""
        event_ids = self.event_mappings.get(intent)
        if event_ids:
            query_dsl["query"]["bool"]["must"].append({
                "terms": {"event.code": event_ids}
            })
        
        # Add specific intent logic
        if intent == QueryIntent.SHOW_FAILED_LOGINS:
            # Also check for common failure reasons
            query_dsl["query"]["bool"]["should"].extend([
                {"match": {"winlog.event_data.Status": "0xC000006D"}},  # Bad username
                {"match": {"winlog.event_data.Status": "0xC000006A"}},  # Bad password
                {"match": {"winlog.event_data.SubStatus": "0xC0000064"}}, # User does not exist
                {"match": {"winlog.event_data.SubStatus": "0xC000006A"}}, # Bad password
            ])
            
        elif intent == QueryIntent.USER_ACTIVITY:
            # Add process and user-related events
            query_dsl["query"]["bool"]["should"].extend([
                {"exists": {"field": "winlog.event_data.ProcessName"}},
                {"exists": {"field": "winlog.event_data.TargetUserName"}},
                {"match": {"event.category": "process"}}
            ])
            
        elif intent == QueryIntent.GET_SYSTEM_METRICS:
            # Switch to metricbeat for system metrics
            query_dsl["query"]["bool"]["must"] = [
                {"match": {"beat.name": "metricbeat"}},
                {"exists": {"field": "system.cpu"}}
            ]
    
    def _add_entity_filters(self, query_dsl: Dict[str, Any], entities: List[Dict[str, Any]]) -> None:
        """Add filters based on extracted entities."""
        for entity in entities:
            entity_type = entity.get("type", "").lower()
            entity_value = entity.get("value", "")
            
            if not entity_value:
                continue
                
            if entity_type == "user" or entity_type == "username":
                query_dsl["query"]["bool"]["should"].extend([
                    {"match": {"user.name": entity_value}},
                    {"match": {"winlog.event_data.TargetUserName": entity_value}},
                    {"match": {"winlog.event_data.SubjectUserName": entity_value}},
                    {"wildcard": {"user.name": f"*{entity_value}*"}}
                ])
                query_dsl["query"]["bool"]["minimum_should_match"] = 1
                
            elif entity_type == "ip" or entity_type == "ip_address":
                query_dsl["query"]["bool"]["should"].extend([
                    {"match": {"source.ip": entity_value}},
                    {"match": {"destination.ip": entity_value}},
                    {"match": {"client.ip": entity_value}},
                    {"match": {"winlog.event_data.IpAddress": entity_value}}
                ])
                query_dsl["query"]["bool"]["minimum_should_match"] = 1
                
            elif entity_type == "hostname" or entity_type == "computer":
                query_dsl["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": entity_value,
                        "fields": ["host.name", "agent.hostname", "winlog.computer_name"]
                    }
                })
                
            elif entity_type == "process":
                query_dsl["query"]["bool"]["should"].extend([
                    {"match": {"process.name": entity_value}},
                    {"match": {"winlog.event_data.ProcessName": entity_value}},
                    {"wildcard": {"process.name": f"*{entity_value}*"}}
                ])
                query_dsl["query"]["bool"]["minimum_should_match"] = 1
    
    def _add_time_filter(self, query_dsl: Dict[str, Any], time_range: str) -> None:
        """Add time range filter to query."""
        # Parse different time formats
        time_patterns = {
            r'(\d+)\s*(hour|hr|h)s?': lambda m: f"now-{m.group(1)}h",
            r'(\d+)\s*(day|d)s?': lambda m: f"now-{m.group(1)}d", 
            r'(\d+)\s*(week|w)s?': lambda m: f"now-{m.group(1)}w",
            r'(\d+)\s*(minute|min|m)s?': lambda m: f"now-{m.group(1)}m",
            r'last\s+(\d+)\s*(hour|hr|h)s?': lambda m: f"now-{m.group(1)}h",
            r'last\s+(\d+)\s*(day|d)s?': lambda m: f"now-{m.group(1)}d",
            r'today': lambda m: "now/d",
            r'yesterday': lambda m: "now-1d/d"
        }
        
        gte_value = f"now-{time_range}"
        
        # Try to parse human-readable time
        for pattern, converter in time_patterns.items():
            match = re.search(pattern, time_range.lower())
            if match:
                gte_value = converter(match)
                break
        
        query_dsl["query"]["bool"]["filter"].append({
            "range": {
                "@timestamp": {
                    "gte": gte_value,
                    "lte": "now"
                }
            }
        })
    
    def _add_keyword_search(self, query_dsl: Dict[str, Any], query_text: str) -> None:
        """Add keyword search for general queries."""
        # Clean query text
        cleaned_query = re.sub(r'\b(show|find|search|list|get|display)\b', '', query_text, flags=re.IGNORECASE)
        cleaned_query = cleaned_query.strip()
        
        if cleaned_query:
            query_dsl["query"]["bool"]["should"].extend([
                {
                    "multi_match": {
                        "query": cleaned_query,
                        "fields": [
                            "message^2",
                            "winlog.event_data.*",
                            "event.original",
                            "user.name",
                            "process.name",
                            "host.name"
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                {
                    "query_string": {
                        "query": f"*{cleaned_query}*",
                        "fields": ["message", "winlog.event_data.*"]
                    }
                }
            ])
            query_dsl["query"]["bool"]["minimum_should_match"] = 1
    
    def _build_fallback_query(self, query_text: str, time_range: Optional[str]) -> Dict[str, Any]:
        """Build fallback query when main query building fails."""
        return {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"beat.name": "winlogbeat"}}
                    ],
                    "should": [
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["message", "winlog.event_data.*", "event.original"]
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": f"now-{time_range or '1h'}",
                                    "lte": "now"
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 100
        }

    def build_aggregation_query(
        self,
        intent: QueryIntent,
        entities: List[Dict[str, Any]],
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Build aggregation query for dashboard widgets."""
        base_query = self.build_query(intent, entities, "", time_range)
        
        # Add aggregations based on intent
        aggregations = {}
        
        if intent == QueryIntent.SHOW_FAILED_LOGINS:
            aggregations = {
                "failed_logins_over_time": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "1h"
                    }
                },
                "top_source_ips": {
                    "terms": {
                        "field": "source.ip.keyword",
                        "size": 10
                    }
                },
                "failed_users": {
                    "terms": {
                        "field": "winlog.event_data.TargetUserName.keyword",
                        "size": 10
                    }
                }
            }
        elif intent == QueryIntent.GET_SYSTEM_METRICS:
            aggregations = {
                "avg_cpu": {
                    "avg": {"field": "system.cpu.total.pct"}
                },
                "avg_memory": {
                    "avg": {"field": "system.memory.used.pct"}
                },
                "cpu_over_time": {
                    "date_histogram": {
                        "field": "@timestamp", 
                        "calendar_interval": "5m"
                    },
                    "aggs": {
                        "avg_cpu": {"avg": {"field": "system.cpu.total.pct"}}
                    }
                }
            }
        
        base_query["aggs"] = aggregations
        base_query["size"] = 0  # No hits needed for aggregation-only query
        
        return base_query
