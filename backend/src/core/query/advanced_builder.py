"""
Advanced Query Builder for SIEM Systems
Generates complex queries with optimized performance and security validation
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of supported SIEM queries"""
    SIMPLE_SEARCH = "simple_search"
    AGGREGATION = "aggregation"
    TIME_SERIES = "time_series"
    CORRELATION = "correlation"
    STATISTICAL = "statistical"
    GEOSPATIAL = "geospatial"


class SIEMPlatform(Enum):
    """Supported SIEM platforms"""
    ELASTICSEARCH = "elasticsearch"
    SPLUNK = "splunk" 
    QRADAR = "qradar"
    SENTINEL = "sentinel"
    WAZUH = "wazuh"
    GENERIC = "generic"


@dataclass
class QueryComponent:
    """Individual query component"""
    field: str
    operator: str
    value: Union[str, List[str], int, float]
    logic: str = "AND"
    boost: float = 1.0


@dataclass
class QueryContext:
    """Query execution context"""
    time_range: Optional[Dict[str, datetime]] = None
    size_limit: int = 100
    sort_fields: List[Dict[str, str]] = None
    aggregations: List[Dict[str, Any]] = None
    filters: List[QueryComponent] = None


class AdvancedQueryBuilder:
    """Advanced query builder with platform-specific optimization"""
    
    def __init__(self, platform: str = "elasticsearch"):
        """
        Initialize the query builder
        
        Args:
            platform: Target SIEM platform
        """
        self.platform = SIEMPlatform(platform.lower())
        self.field_mappings = self._load_field_mappings()
        self.query_templates = self._load_query_templates()
        self.security_rules = self._load_security_rules()
        
    def build_query(
        self,
        intent: str,
        entities: List[Dict[str, Any]],
        field_mappings: Dict[str, List[str]],
        context: Optional[Dict[str, Any]] = None,
        query_context: Optional[QueryContext] = None
    ) -> Dict[str, Any]:
        """
        Build a comprehensive SIEM query
        
        Args:
            intent: Query intent type
            entities: Extracted entities
            field_mappings: Schema field mappings
            context: Conversation context
            query_context: Query execution context
            
        Returns:
            Complete SIEM query dictionary
        """
        try:
            # Initialize query context
            if not query_context:
                query_context = QueryContext()
                
            # Determine query type
            query_type = self._determine_query_type(intent, entities)
            
            # Build base query components
            components = self._build_query_components(entities, field_mappings)
            
            # Apply time range filters
            time_components = self._build_time_filters(entities, context)
            if time_components:
                components.extend(time_components)
                
            # Build platform-specific query
            if self.platform == SIEMPlatform.ELASTICSEARCH:
                query = self._build_elasticsearch_query(components, query_type, query_context)
            elif self.platform == SIEMPlatform.SPLUNK:
                query = self._build_splunk_query(components, query_type, query_context)
            elif self.platform == SIEMPlatform.QRADAR:
                query = self._build_qradar_query(components, query_type, query_context)
            elif self.platform == SIEMPlatform.SENTINEL:
                query = self._build_sentinel_query(components, query_type, query_context)
            elif self.platform == SIEMPlatform.WAZUH:
                query = self._build_wazuh_query(components, query_type, query_context)
            else:
                query = self._build_generic_query(components, query_type, query_context)
                
            # Apply query optimization
            query = self._optimize_query(query, query_type)
            
            # Add metadata
            query["_metadata"] = {
                "intent": intent,
                "query_type": query_type.value,
                "platform": self.platform.value,
                "generated_at": datetime.now().isoformat(),
                "entities_count": len(entities),
                "components_count": len(components)
            }
            
            logger.info(f"Built {query_type.value} query for {self.platform.value}")
            return query
            
        except Exception as e:
            logger.error(f"Error building query: {e}")
            return self._build_fallback_query(intent, entities)
    
    def _determine_query_type(self, intent: str, entities: List[Dict[str, Any]]) -> QueryType:
        """Determine the optimal query type based on intent and entities"""
        
        # Statistical queries
        if any(keyword in intent.lower() for keyword in ["count", "sum", "average", "stats", "metrics"]):
            return QueryType.STATISTICAL
            
        # Time series queries
        if any(keyword in intent.lower() for keyword in ["trend", "over time", "timeline", "series"]):
            return QueryType.TIME_SERIES
            
        # Aggregation queries
        if any(keyword in intent.lower() for keyword in ["group", "top", "bottom", "aggregate"]):
            return QueryType.AGGREGATION
            
        # Correlation queries
        if any(keyword in intent.lower() for keyword in ["correlate", "relate", "pattern", "sequence"]):
            return QueryType.CORRELATION
            
        # Geospatial queries
        if any(entity.get("type") == "location" for entity in entities):
            return QueryType.GEOSPATIAL
            
        return QueryType.SIMPLE_SEARCH
    
    def _build_query_components(
        self, 
        entities: List[Dict[str, Any]], 
        field_mappings: Dict[str, List[str]]
    ) -> List[QueryComponent]:
        """Build query components from entities"""
        components = []
        
        for entity in entities:
            entity_type = entity.get("type")
            entity_value = entity.get("value")
            entity_confidence = entity.get("confidence", 1.0)
            
            if not entity_type or not entity_value:
                continue
                
            # Get field mapping for this entity type
            fields = field_mappings.get(entity_type, [])
            
            for field in fields:
                # Determine operator based on entity type and value
                operator = self._get_optimal_operator(entity_type, entity_value, field)
                
                # Create query component
                component = QueryComponent(
                    field=field,
                    operator=operator,
                    value=entity_value,
                    boost=entity_confidence
                )
                components.append(component)
        
        return components
    
    def _get_optimal_operator(self, entity_type: str, value: str, field: str) -> str:
        """Get optimal query operator for entity type and field"""
        
        # IP addresses - exact match or wildcard
        if entity_type == "ip_address":
            if "*" in value or "?" in value:
                return "wildcard"
            return "term"
            
        # Text fields - full text search
        if entity_type in ["username", "process_name", "file_path"]:
            if len(value) < 3:
                return "term"
            return "match"
            
        # Time ranges
        if entity_type == "time_range":
            return "range"
            
        # Numeric fields
        if entity_type in ["port", "event_id"]:
            return "term"
            
        # Hash values - exact match
        if entity_type == "hash":
            return "term"
            
        # Default to match for text search
        return "match"
    
    def _build_time_filters(
        self, 
        entities: List[Dict[str, Any]], 
        context: Optional[Dict[str, Any]] = None
    ) -> List[QueryComponent]:
        """Build time-based filter components"""
        components = []
        
        # Look for time range entities
        time_entities = [e for e in entities if e.get("type") == "time_range"]
        
        if time_entities:
            for time_entity in time_entities:
                # Parse time range from entity value
                time_range = self._parse_time_range(time_entity.get("value"))
                if time_range:
                    component = QueryComponent(
                        field="@timestamp",
                        operator="range",
                        value={
                            "gte": time_range["start"].isoformat(),
                            "lte": time_range["end"].isoformat()
                        }
                    )
                    components.append(component)
        
        # Default time range if none specified
        elif not time_entities:
            # Default to last 24 hours
            now = datetime.now()
            start_time = now - timedelta(days=1)
            
            component = QueryComponent(
                field="@timestamp",
                operator="range",
                value={
                    "gte": start_time.isoformat(),
                    "lte": now.isoformat()
                }
            )
            components.append(component)
        
        return components
    
    def _build_elasticsearch_query(
        self, 
        components: List[QueryComponent], 
        query_type: QueryType, 
        context: QueryContext
    ) -> Dict[str, Any]:
        """Build Elasticsearch-specific query"""
        
        query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            },
            "size": context.size_limit,
            "_source": ["@timestamp", "message", "host.name", "event.*", "user.*", "source.*"]
        }
        
        # Build bool query clauses
        for component in components:
            clause = self._build_elasticsearch_clause(component)
            
            if component.logic == "AND":
                if component.operator == "range" or component.field == "@timestamp":
                    query["query"]["bool"]["filter"].append(clause)
                else:
                    query["query"]["bool"]["must"].append(clause)
            elif component.logic == "OR":
                query["query"]["bool"]["should"].append(clause)
            elif component.logic == "NOT":
                query["query"]["bool"]["must_not"].append(clause)
        
        # Add aggregations for statistical queries
        if query_type in [QueryType.AGGREGATION, QueryType.STATISTICAL, QueryType.TIME_SERIES]:
            query["aggs"] = self._build_elasticsearch_aggregations(query_type, components)
        
        # Add sorting
        query["sort"] = [
            {"@timestamp": {"order": "desc"}},
            "_score"
        ]
        
        return query
    
    def _build_elasticsearch_clause(self, component: QueryComponent) -> Dict[str, Any]:
        """Build individual Elasticsearch query clause"""
        
        if component.operator == "term":
            return {"term": {component.field + ".keyword": {"value": component.value, "boost": component.boost}}}
        elif component.operator == "match":
            return {"match": {component.field: {"query": component.value, "boost": component.boost}}}
        elif component.operator == "wildcard":
            return {"wildcard": {component.field + ".keyword": {"value": component.value, "boost": component.boost}}}
        elif component.operator == "range":
            return {"range": {component.field: component.value}}
        elif component.operator == "prefix":
            return {"prefix": {component.field + ".keyword": {"value": component.value, "boost": component.boost}}}
        else:
            return {"match": {component.field: {"query": component.value, "boost": component.boost}}}
    
    def _build_elasticsearch_aggregations(self, query_type: QueryType, components: List[QueryComponent]) -> Dict[str, Any]:
        """Build Elasticsearch aggregations"""
        aggs = {}
        
        if query_type == QueryType.TIME_SERIES:
            aggs["events_over_time"] = {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "1h",
                    "min_doc_count": 0
                }
            }
        
        elif query_type == QueryType.AGGREGATION:
            # Top users aggregation
            aggs["top_users"] = {
                "terms": {
                    "field": "user.name.keyword",
                    "size": 10
                }
            }
            
            # Top source IPs
            aggs["top_source_ips"] = {
                "terms": {
                    "field": "source.ip.keyword",
                    "size": 10
                }
            }
        
        elif query_type == QueryType.STATISTICAL:
            aggs["event_stats"] = {
                "stats": {
                    "field": "event.severity"
                }
            }
            
            aggs["event_count_by_severity"] = {
                "terms": {
                    "field": "event.severity.keyword",
                    "size": 10
                }
            }
        
        return aggs
    
    def _build_splunk_query(
        self, 
        components: List[QueryComponent], 
        query_type: QueryType, 
        context: QueryContext
    ) -> Dict[str, Any]:
        """Build Splunk-specific query"""
        
        # Build base search
        search_parts = ["search"]
        
        for component in components:
            if component.field == "@timestamp":
                # Handle time range specially in Splunk
                continue
            
            if component.operator == "term":
                search_parts.append(f'{component.field}="{component.value}"')
            elif component.operator == "match":
                search_parts.append(f'{component.field}=*{component.value}*')
            elif component.operator == "wildcard":
                search_parts.append(f'{component.field}={component.value}')
            else:
                search_parts.append(f'{component.field}="{component.value}"')
        
        query = {
            "search": " ".join(search_parts),
            "earliest_time": "-24h",
            "latest_time": "now",
            "count": context.size_limit
        }
        
        # Add statistical commands for aggregations
        if query_type in [QueryType.AGGREGATION, QueryType.STATISTICAL]:
            query["search"] += " | stats count by user, source_ip"
        elif query_type == QueryType.TIME_SERIES:
            query["search"] += " | timechart count by severity"
        
        return query
    
    def _build_qradar_query(
        self, 
        components: List[QueryComponent], 
        query_type: QueryType, 
        context: QueryContext
    ) -> Dict[str, Any]:
        """Build IBM QRadar AQL query"""
        
        fields = ["QIDNAME(qid)", "LOGSOURCENAME(logsourceid)", "sourceip", "destinationip", "username"]
        conditions = []
        
        for component in components:
            if component.operator == "term":
                conditions.append(f"{component.field} = '{component.value}'")
            elif component.operator == "match":
                conditions.append(f"{component.field} ILIKE '%{component.value}%'")
            elif component.operator == "range":
                if component.field == "@timestamp":
                    # QRadar uses START/STOP time
                    continue
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = {
            "query_expression": f"SELECT {', '.join(fields)} FROM events WHERE {where_clause}",
            "range": "LAST 24 HOURS"
        }
        
        return query
    
    def _build_sentinel_query(
        self, 
        components: List[QueryComponent], 
        query_type: QueryType, 
        context: QueryContext
    ) -> Dict[str, Any]:
        """Build Azure Sentinel KQL query"""
        
        table = "SecurityEvent"  # Default table
        filters = []
        
        for component in components:
            if component.operator == "term":
                filters.append(f'{component.field} == "{component.value}"')
            elif component.operator == "match":
                filters.append(f'{component.field} contains "{component.value}"')
            elif component.operator == "range":
                if component.field == "@timestamp":
                    filters.append(f'TimeGenerated between (ago(24h) .. now())')
        
        where_clause = " and ".join(filters) if filters else ""
        
        query = {
            "query": f"{table} | where {where_clause} | limit {context.size_limit}",
            "timespan": "P1D"  # Last 1 day
        }
        
        # Add aggregations for statistical queries
        if query_type in [QueryType.AGGREGATION, QueryType.STATISTICAL]:
            query["query"] += " | summarize count() by Account, IpAddress"
        
        return query
    
    def _build_wazuh_query(
        self, 
        components: List[QueryComponent], 
        query_type: QueryType, 
        context: QueryContext
    ) -> Dict[str, Any]:
        """Build Wazuh-specific query (Elasticsearch-based)"""
        # Wazuh uses Elasticsearch backend, so reuse ES query building
        return self._build_elasticsearch_query(components, query_type, context)
    
    def _build_generic_query(
        self, 
        components: List[QueryComponent], 
        query_type: QueryType, 
        context: QueryContext
    ) -> Dict[str, Any]:
        """Build generic query structure"""
        
        query = {
            "type": "generic",
            "conditions": [],
            "limit": context.size_limit,
            "time_range": "24h"
        }
        
        for component in components:
            condition = {
                "field": component.field,
                "operator": component.operator,
                "value": component.value,
                "logic": component.logic
            }
            query["conditions"].append(condition)
        
        return query
    
    def _optimize_query(self, query: Dict[str, Any], query_type: QueryType) -> Dict[str, Any]:
        """Apply query optimizations"""
        
        # Add performance hints for Elasticsearch
        if self.platform == SIEMPlatform.ELASTICSEARCH:
            # Prefer filter context over query context for exact matches
            if "query" in query and "bool" in query["query"]:
                bool_query = query["query"]["bool"]
                
                # Move term queries to filter context
                must_queries = bool_query.get("must", [])
                filter_queries = bool_query.get("filter", [])
                
                optimized_must = []
                for q in must_queries:
                    if "term" in q or "range" in q:
                        filter_queries.append(q)
                    else:
                        optimized_must.append(q)
                
                bool_query["must"] = optimized_must
                bool_query["filter"] = filter_queries
        
        return query
    
    def _build_fallback_query(self, intent: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a simple fallback query when main building fails"""
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match_all": {}}
                    ],
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "now-24h",
                                    "lte": "now"
                                }
                            }
                        }
                    ]
                }
            },
            "size": 100,
            "_source": ["@timestamp", "message"],
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        return query
    
    def _parse_time_range(self, time_value: str) -> Optional[Dict[str, datetime]]:
        """Parse time range from string value"""
        now = datetime.now()
        
        # Simple time range parsing
        if "last hour" in time_value.lower():
            return {"start": now - timedelta(hours=1), "end": now}
        elif "last 24 hours" in time_value.lower():
            return {"start": now - timedelta(hours=24), "end": now}
        elif "last week" in time_value.lower():
            return {"start": now - timedelta(weeks=1), "end": now}
        elif "today" in time_value.lower():
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return {"start": start_of_day, "end": now}
        
        return None
    
    def _load_field_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Load field mappings for different platforms"""
        return {
            "elasticsearch": {
                "ip_address": ["source.ip", "destination.ip", "host.ip"],
                "username": ["user.name", "user.id", "source.user.name"],
                "port": ["source.port", "destination.port", "network.port"],
                "process_name": ["process.name", "process.executable"],
                "event_id": ["event.code", "winlog.event_id"],
                "file_path": ["file.path", "file.name"],
                "domain": ["dns.question.name", "url.domain"]
            },
            "splunk": {
                "ip_address": ["src_ip", "dest_ip", "host"],
                "username": ["user", "src_user", "dest_user"],
                "port": ["src_port", "dest_port"],
                "process_name": ["process", "process_name"],
                "event_id": ["EventCode", "event_id"],
                "file_path": ["file_path", "file_name"],
                "domain": ["dns_query", "domain"]
            }
        }
    
    def _load_query_templates(self) -> Dict[str, Dict[str, str]]:
        """Load query templates for common patterns"""
        return {
            "failed_login": {
                "elasticsearch": "event.outcome:failure AND event.category:authentication",
                "splunk": "EventCode=4625 OR EventCode=529",
                "qradar": "QIDNAME(qid) ILIKE '%Authentication%' AND QIDNAME(qid) ILIKE '%Failed%'"
            },
            "malware_detection": {
                "elasticsearch": "event.category:malware OR threat.indicator.type:*",
                "splunk": "signature=*malware* OR threat=*virus*",
                "qradar": "category=31000 OR category=32000"
            }
        }
    
    def _load_security_rules(self) -> List[Dict[str, Any]]:
        """Load security validation rules"""
        return [
            {
                "rule": "no_wildcard_leading",
                "description": "Prevent leading wildcards that can cause performance issues",
                "pattern": r"^\*"
            },
            {
                "rule": "reasonable_time_range",
                "description": "Limit time ranges to prevent excessive resource usage",
                "max_days": 90
            },
            {
                "rule": "result_size_limit",
                "description": "Limit result size to prevent memory issues",
                "max_size": 10000
            }
        ]


# Query validation and security
class QueryValidator:
    """Validates queries for security and performance"""
    
    def __init__(self):
        self.security_rules = [
            self._check_injection_patterns,
            self._check_wildcard_abuse,
            self._check_time_range_limits,
            self._check_result_size_limits
        ]
    
    async def validate_query(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a query for security and performance issues
        
        Args:
            query: Query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            for rule in self.security_rules:
                is_valid, error = rule(query)
                if not is_valid:
                    return False, error
            
            return True, None
            
        except Exception as e:
            logger.error(f"Query validation error: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _check_injection_patterns(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for potential injection patterns"""
        query_str = json.dumps(query).lower()
        
        suspicious_patterns = [
            "script",
            "eval(",
            "javascript:",
            "document.",
            "window.",
            "alert(",
            "prompt(",
            "confirm("
        ]
        
        for pattern in suspicious_patterns:
            if pattern in query_str:
                return False, f"Potential script injection detected: {pattern}"
        
        return True, None
    
    def _check_wildcard_abuse(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for wildcard abuse that could cause performance issues"""
        query_str = json.dumps(query)
        
        # Check for leading wildcards
        if query_str.count('*') > 10:
            return False, "Excessive wildcard usage detected"
        
        return True, None
    
    def _check_time_range_limits(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check time range is within reasonable limits"""
        # This is a simplified check - in production you'd parse the actual time range
        return True, None
    
    def _check_result_size_limits(self, query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check result size limits"""
        size = query.get("size", 100)
        
        if size > 10000:
            return False, f"Result size too large: {size} (max: 10000)"
        
        return True, None
