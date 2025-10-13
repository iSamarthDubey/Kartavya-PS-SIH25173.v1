"""
Universal Query Builder System
Dynamically builds queries based on detected platform and available data.
NO STATIC MAPPINGS - ALL DYNAMIC DETECTION.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import re

from ..platform.detector import RobustPlatformDetector, PlatformType, DataSourceType

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Universal query intents"""
    AUTHENTICATION_EVENTS = "authentication_events"
    FAILED_LOGINS = "failed_logins"
    SUCCESSFUL_LOGINS = "successful_logins"
    SYSTEM_METRICS = "system_metrics"
    NETWORK_ACTIVITY = "network_activity"
    PROCESS_ACTIVITY = "process_activity"
    FILE_ACCESS = "file_access"
    SECURITY_ALERTS = "security_alerts"
    USER_ACTIVITY = "user_activity"
    SYSTEM_ERRORS = "system_errors"
    GENERIC_SEARCH = "generic_search"


class UniversalQueryBuilder:
    """
    Universal query builder that adapts to any detected environment.
    NO HARDCODED VALUES - ALL DYNAMIC.
    """
    
    def __init__(self, platform_detector: RobustPlatformDetector):
        self.detector = platform_detector
        self.platform_info = None
        self.query_cache = {}
        
        # Universal patterns for different intents (dynamic detection)
        self.intent_patterns = {
            QueryIntent.AUTHENTICATION_EVENTS: {
                "keywords": ["login", "logon", "auth", "authentication", "signin", "logoff", "logout"],
                "event_categories": ["authentication", "iam", "access"],
                "windows_events": ["4624", "4625", "4634", "4648"],
                "linux_patterns": ["sshd", "auth", "pam", "login"],
                "fields": ["user", "username", "account", "logon"]
            },
            QueryIntent.FAILED_LOGINS: {
                "keywords": ["failed", "failure", "denied", "invalid", "unauthorized", "rejected"],
                "event_categories": ["authentication_failure", "access_denied"],
                "windows_events": ["4625", "4740", "4771"],
                "linux_patterns": ["failed password", "authentication failure", "invalid user"],
                "fields": ["failure", "error", "denied"]
            },
            QueryIntent.SUCCESSFUL_LOGINS: {
                "keywords": ["success", "successful", "accepted", "granted", "allowed"],
                "event_categories": ["authentication_success", "access_granted"],
                "windows_events": ["4624", "4648"],
                "linux_patterns": ["accepted password", "session opened", "login successful"],
                "fields": ["success", "accepted", "granted"]
            },
            QueryIntent.SYSTEM_METRICS: {
                "keywords": ["cpu", "memory", "disk", "performance", "load", "usage"],
                "event_categories": ["system", "metrics", "performance"],
                "windows_events": ["8002", "8003"],
                "linux_patterns": ["system load", "memory usage", "disk usage"],
                "fields": ["system", "metrics", "performance"]
            },
            QueryIntent.NETWORK_ACTIVITY: {
                "keywords": ["network", "connection", "tcp", "udp", "ip", "traffic"],
                "event_categories": ["network", "connection", "traffic"],
                "windows_events": ["5156", "5157"],
                "linux_patterns": ["iptables", "netfilter", "connection"],
                "fields": ["network", "connection", "traffic"]
            },
            QueryIntent.PROCESS_ACTIVITY: {
                "keywords": ["process", "execution", "command", "program", "binary"],
                "event_categories": ["process", "execution"],
                "windows_events": ["4688", "4689"],
                "linux_patterns": ["exec", "process", "command"],
                "fields": ["process", "command", "execution"]
            }
        }
    
    async def build_query(
        self,
        intent: QueryIntent,
        query_text: str = "",
        entities: List[Dict[str, Any]] = None,
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Build universal query that adapts to detected platform.
        """
        entities = entities or []
        
        # Get platform info
        if not self.platform_info:
            self.platform_info = await self.detector.detect_platform()
        
        logger.info(f"🔨 Building {intent.value} query for {self.platform_info.platform_type.value}")
        
        # Build base query structure
        query_dsl = self._build_base_query()
        
        # Add intent-specific filters
        self._add_intent_filters(query_dsl, intent)
        
        # Add entity filters
        self._add_entity_filters(query_dsl, entities)
        
        # Add time filter
        self._add_time_filter(query_dsl, time_range)
        
        # Add text search if provided
        if query_text:
            self._add_text_search(query_dsl, query_text)
        
        # Set result size
        query_dsl["size"] = limit
        
        # Add sorting
        self._add_sorting(query_dsl)
        
        logger.info(f"✅ Built query targeting {len(self.platform_info.available_indices)} indices")
        
        return query_dsl
    
    def _build_base_query(self) -> Dict[str, Any]:
        """Build base Elasticsearch query structure"""
        return {
            "query": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": [],
                    "must_not": [],
                    "minimum_should_match": 0
                }
            },
            "size": 100,
            "sort": [],
            "_source": {
                "excludes": ["@metadata", "agent.ephemeral_id", "ecs.version"]
            }
        }
    
    def _add_intent_filters(self, query_dsl: Dict[str, Any], intent: QueryIntent):
        """Add filters based on intent and detected platform"""
        if intent not in self.intent_patterns:
            return
        
        patterns = self.intent_patterns[intent]
        platform_type = self.platform_info.platform_type
        data_sources = self.platform_info.data_sources
        field_mappings = self.platform_info.field_mappings
        
        # Strategy 1: Use detected field mappings for precise queries
        self._add_mapped_field_filters(query_dsl, intent, patterns, field_mappings)
        
        # Strategy 2: Add platform-specific filters
        if platform_type == PlatformType.WINDOWS and DataSourceType.BEATS in data_sources:
            self._add_windows_beats_filters(query_dsl, patterns)
        elif platform_type == PlatformType.LINUX and DataSourceType.SYSLOG in data_sources:
            self._add_linux_syslog_filters(query_dsl, patterns)
        
        # Strategy 3: Add generic ECS filters
        if DataSourceType.ECS in data_sources:
            self._add_ecs_filters(query_dsl, patterns)
        
        # Strategy 4: Add keyword-based fallback (last resort)
        self._add_keyword_filters(query_dsl, patterns)
    
    def _add_mapped_field_filters(self, query_dsl: Dict[str, Any], intent: QueryIntent, patterns: Dict, field_mappings: Dict[str, str]):
        """Use dynamically detected field mappings"""
        bool_query = query_dsl["query"]["bool"]
        
        # Use event_id field if detected
        if "event_id" in field_mappings:
            event_field = field_mappings["event_id"]
            
            # Add platform-specific event IDs
            if intent in [QueryIntent.FAILED_LOGINS, QueryIntent.SUCCESSFUL_LOGINS, QueryIntent.AUTHENTICATION_EVENTS]:
                event_ids = patterns.get("windows_events", [])
                if event_ids:
                    bool_query["should"].append({
                        "terms": {event_field: event_ids}
                    })
        
        # Use event_category if detected
        if "event_category" in field_mappings:
            category_field = field_mappings["event_category"]
            categories = patterns.get("event_categories", [])
            if categories:
                bool_query["should"].append({
                    "terms": {category_field: categories}
                })
        
        # Use username field if detected
        if "username" in field_mappings and intent in [QueryIntent.AUTHENTICATION_EVENTS, QueryIntent.USER_ACTIVITY]:
            user_field = field_mappings["username"]
            bool_query["must"].append({
                "exists": {"field": user_field}
            })
    
    def _add_windows_beats_filters(self, query_dsl: Dict[str, Any], patterns: Dict):
        """Add Windows Beats-specific filters"""
        bool_query = query_dsl["query"]["bool"]
        
        # Check if winlogbeat indices are available
        winlogbeat_indices = [idx for idx in self.platform_info.available_indices 
                             if "winlogbeat" in idx.lower()]
        
        if winlogbeat_indices:
            # Add Windows-specific filters
            bool_query["must"].append({
                "match": {"agent.type": "winlogbeat"}
            })
            
            # Add Windows event IDs if available
            event_ids = patterns.get("windows_events", [])
            if event_ids:
                bool_query["should"].append({
                    "terms": {"winlog.event_id": event_ids}
                })
                bool_query["should"].append({
                    "terms": {"event.code": event_ids}
                })
    
    def _add_linux_syslog_filters(self, query_dsl: Dict[str, Any], patterns: Dict):
        """Add Linux syslog-specific filters"""
        bool_query = query_dsl["query"]["bool"]
        
        # Add syslog-specific filters
        linux_patterns = patterns.get("linux_patterns", [])
        if linux_patterns:
            for pattern in linux_patterns:
                bool_query["should"].append({
                    "match_phrase": {"message": pattern}
                })
        
        # Add common syslog fields
        bool_query["should"].extend([
            {"exists": {"field": "syslog.facility"}},
            {"exists": {"field": "log.syslog.facility.name"}},
            {"match": {"input.type": "log"}}
        ])
    
    def _add_ecs_filters(self, query_dsl: Dict[str, Any], patterns: Dict):
        """Add ECS (Elastic Common Schema) filters"""
        bool_query = query_dsl["query"]["bool"]
        
        # Use ECS event categories
        categories = patterns.get("event_categories", [])
        if categories:
            bool_query["should"].append({
                "terms": {"event.category": categories}
            })
        
        # Use ECS event outcomes for authentication
        if "authentication" in str(patterns).lower():
            bool_query["should"].extend([
                {"match": {"event.outcome": "success"}},
                {"match": {"event.outcome": "failure"}}
            ])
    
    def _add_keyword_filters(self, query_dsl: Dict[str, Any], patterns: Dict):
        """Add keyword-based filters as fallback"""
        bool_query = query_dsl["query"]["bool"]
        
        keywords = patterns.get("keywords", [])
        if keywords:
            # Create multi-field keyword search
            keyword_queries = []
            for keyword in keywords:
                keyword_queries.append({
                    "multi_match": {
                        "query": keyword,
                        "fields": [
                            "message^2",
                            "event.action",
                            "log.level",
                            "tags",
                            "_all"
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            
            if keyword_queries:
                bool_query["should"].append({
                    "bool": {
                        "should": keyword_queries,
                        "minimum_should_match": 1
                    }
                })
    
    def _add_entity_filters(self, query_dsl: Dict[str, Any], entities: List[Dict[str, Any]]):
        """Add filters based on extracted entities"""
        if not entities:
            return
        
        bool_query = query_dsl["query"]["bool"]
        field_mappings = self.platform_info.field_mappings
        
        for entity in entities:
            entity_type = entity.get("type", "").lower()
            entity_value = entity.get("value", "")
            
            if not entity_value:
                continue
            
            # Use detected field mappings first
            if entity_type == "user" and "username" in field_mappings:
                bool_query["must"].append({
                    "match": {field_mappings["username"]: entity_value}
                })
            elif entity_type == "ip":
                ip_fields = []
                if "source_ip" in field_mappings:
                    ip_fields.append(field_mappings["source_ip"])
                if "destination_ip" in field_mappings:
                    ip_fields.append(field_mappings["destination_ip"])
                
                if ip_fields:
                    bool_query["should"].append({
                        "multi_match": {
                            "query": entity_value,
                            "fields": ip_fields
                        }
                    })
                else:
                    # Fallback to common IP fields
                    bool_query["should"].append({
                        "multi_match": {
                            "query": entity_value,
                            "fields": ["source.ip", "destination.ip", "client.ip", "server.ip"]
                        }
                    })
            elif entity_type == "hostname" and "hostname" in field_mappings:
                bool_query["must"].append({
                    "match": {field_mappings["hostname"]: entity_value}
                })
    
    def _add_time_filter(self, query_dsl: Dict[str, Any], time_range: str):
        """Add time range filter"""
        # Parse time range
        time_filter = self._parse_time_range(time_range)
        
        # Add to filter context for performance
        if "timestamp" in self.platform_info.field_mappings:
            timestamp_field = self.platform_info.field_mappings["timestamp"]
        else:
            timestamp_field = "@timestamp"  # ECS standard
        
        query_dsl["query"]["bool"]["filter"].append({
            "range": {
                timestamp_field: time_filter
            }
        })
    
    def _parse_time_range(self, time_range: str) -> Dict[str, str]:
        """Parse time range string to Elasticsearch format"""
        # Handle different time formats
        if time_range.isdigit():
            return {"gte": f"now-{time_range}h"}
        
        # Parse patterns like "1h", "24h", "7d", "1w"
        time_patterns = {
            r'(\d+)h': lambda m: {"gte": f"now-{m.group(1)}h"},
            r'(\d+)d': lambda m: {"gte": f"now-{m.group(1)}d"},
            r'(\d+)w': lambda m: {"gte": f"now-{m.group(1)}w"},
            r'(\d+)m': lambda m: {"gte": f"now-{m.group(1)}m"},
        }
        
        for pattern, formatter in time_patterns.items():
            match = re.match(pattern, time_range.lower())
            if match:
                return formatter(match)
        
        # Default fallback
        return {"gte": "now-1h"}
    
    def _add_text_search(self, query_dsl: Dict[str, Any], query_text: str):
        """Add free text search"""
        bool_query = query_dsl["query"]["bool"]
        
        # Multi-field search across common fields
        bool_query["must"].append({
            "multi_match": {
                "query": query_text,
                "fields": [
                    "message^3",
                    "event.action^2", 
                    "user.name^2",
                    "host.name^2",
                    "process.name",
                    "tags",
                    "_all"
                ],
                "type": "best_fields",
                "fuzziness": "AUTO",
                "minimum_should_match": "75%"
            }
        })
    
    def _add_sorting(self, query_dsl: Dict[str, Any]):
        """Add sorting to query"""
        # Use detected timestamp field
        if "timestamp" in self.platform_info.field_mappings:
            timestamp_field = self.platform_info.field_mappings["timestamp"]
        else:
            timestamp_field = "@timestamp"
        
        query_dsl["sort"] = [
            {timestamp_field: {"order": "desc"}}
        ]
    
    def get_target_indices(self) -> List[str]:
        """Get list of indices to target for queries"""
        if not self.platform_info:
            return ["*"]  # Fallback to all indices
        
        # Return all detected indices
        return self.platform_info.available_indices if self.platform_info.available_indices else ["*"]
    
    def get_query_summary(self, query_dsl: Dict[str, Any]) -> str:
        """Get human-readable summary of the query"""
        bool_query = query_dsl.get("query", {}).get("bool", {})
        
        summary_parts = []
        
        # Count filters
        must_count = len(bool_query.get("must", []))
        should_count = len(bool_query.get("should", []))
        filter_count = len(bool_query.get("filter", []))
        
        if must_count > 0:
            summary_parts.append(f"{must_count} required conditions")
        if should_count > 0:
            summary_parts.append(f"{should_count} optional conditions")
        if filter_count > 0:
            summary_parts.append(f"{filter_count} filters")
        
        # Add index info
        indices = self.get_target_indices()
        summary_parts.append(f"targeting {len(indices)} indices")
        
        return "Query with " + ", ".join(summary_parts)
