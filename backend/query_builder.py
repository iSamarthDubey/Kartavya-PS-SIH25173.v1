"""
Query Builder for SIEM NLP
Converts natural language queries to Elasticsearch DSL/KQL queries.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
import os
from pathlib import Path
import yaml

# Import NLP components with error handling
try:
    from nlp.intent_classifier import QueryIntent, IntentClassifier
    from nlp.entity_extractor import EntityExtractor, Entity
except ImportError:
    # Fallback for different import contexts
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from nlp.intent_classifier import QueryIntent, IntentClassifier
    from nlp.entity_extractor import EntityExtractor, Entity

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Converts natural language to Elasticsearch queries."""
    
    def __init__(self):
        """Initialize the query builder."""
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()

        # Optional index class hint and external field mappings
        self.index_class = os.getenv('INDEX_CLASS', '').strip().lower()
        self.external_mappings = self._load_index_mappings()
        
        # Event ID mappings for common security events
        self.event_id_mappings = {
            # Windows Security Events
            '4624': 'successful_login',
            '4625': 'failed_login', 
            '4634': 'logoff',
            '4648': 'explicit_login',
            '4720': 'account_created',
            '4726': 'account_deleted',
            '4740': 'account_locked',
            '4767': 'account_unlocked',
            '4771': 'kerberos_preauth_failed',
            '4776': 'credential_validation',
            '5156': 'network_connection_allowed',
            '5157': 'network_connection_blocked',
            
            # System Events
            '7034': 'service_crashed',
            '7035': 'service_control',
            '7036': 'service_state_change',
            '1074': 'system_shutdown',
            
            # Application Events
            '1000': 'application_error',
            '1001': 'application_hang',
        }
        
        # Field mappings for different log sources
        self.field_mappings = {
            'windows': {
                'username': ['winlog.event_data.TargetUserName', 'user.name', 'winlog.user.name'],
                'source_ip': ['source.ip', 'winlog.event_data.IpAddress'],
                'event_id': ['winlog.event_id', 'event.code'],
                'timestamp': ['@timestamp', 'winlog.time_created'],
                'hostname': ['host.name', 'winlog.computer_name'],
                'process': ['process.name', 'winlog.event_data.ProcessName'],
                'message': ['message', 'winlog.event_data.Message']
            },
            'linux': {
                'username': ['user.name', 'system.auth.user'],
                'source_ip': ['source.ip'],
                'timestamp': ['@timestamp'],
                'hostname': ['host.name'],
                'process': ['process.name', 'system.process.name'],
                'message': ['message']
            },
            'network': {
                'source_ip': ['source.ip'],
                'dest_ip': ['destination.ip'],
                'source_port': ['source.port'],
                'dest_port': ['destination.port'],
                'protocol': ['network.protocol'],
                'timestamp': ['@timestamp']
            }
        }
    
    async def build_query(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert natural language query to Elasticsearch DSL.
        
        Args:
            query_params: Dictionary containing:
                - raw_text: Natural language query string
                - intent: Optional pre-classified intent
                - entities: Optional pre-extracted entities
            
        Returns:
            Elasticsearch DSL query dictionary
        """
        # Extract params
        natural_query = query_params.get('raw_text', '')
        pre_intent = query_params.get('intent')
        pre_entities = query_params.get('entities', [])
        index_pattern = query_params.get('index_pattern', 'logs-*')
        
        # Use pre-classified intent or classify now
        if pre_intent and isinstance(pre_intent, str):
            intent_str = pre_intent
            # Try to get enum value
            try:
                from backend.nlp.intent_classifier import QueryIntent
                intent = QueryIntent(intent_str) if hasattr(QueryIntent, intent_str.upper()) else None
            except:
                intent = None
            confidence = query_params.get('confidence', 0.5)
        else:
            intent, confidence = self.intent_classifier.classify_intent(natural_query)
        
        # Use pre-extracted entities or extract now
        if pre_entities and isinstance(pre_entities, list):
            entities = pre_entities
        else:
            entities = self.entity_extractor.extract_entities(natural_query)
        
        entity_summary = self.entity_extractor.get_entity_summary(entities)
        
        # Extract time range
        time_range = self.entity_extractor.extract_time_range(natural_query)
        
        # Get intent string safely
        intent_str = intent.value if (intent and hasattr(intent, 'value')) else (pre_intent or 'unknown')
        
        logger.info(f"Building query for intent: {intent_str}, entities: {entity_summary}")
        
        # Build base query structure
        query = {
            "query": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": [],
                    "must_not": []
                }
            },
            "sort": [
                {"@timestamp": {"order": "desc"}}
            ],
            "size": 100
        }
        
        # Add intent-specific query components
        self._add_intent_filters(query, intent, entities, entity_summary)
        
        # Add entity-based filters
        self._add_entity_filters(query, entities, entity_summary)
        
        # Add time range filter (with fallback default)
        if time_range and time_range.get('start_time'):
            self._add_time_filter(query, time_range)
        else:
            # Fallback default window (e.g., now-1d)
            default_window = os.getenv('ASSISTANT_DEFAULT_TIME_WINDOW', 'now-1d')
            query['query']['bool'].setdefault('filter', []).append({
                'range': {
                    '@timestamp': {
                        'gte': default_window
                    }
                }
            })
        
        # Apply pagination/size caps
        max_size = int(os.getenv('ASSISTANT_MAX_RESULTS', '200'))
        requested_size = int(query_params.get('limit', query.get('size', 100)))
        query['size'] = min(requested_size, max_size)
        if 'offset' in query_params:
            try:
                offset = max(0, int(query_params.get('offset', 0)))
                query['from'] = offset
            except Exception:
                pass
        
        # Add aggregations for relevant intents
        self._add_aggregations(query, intent, entities)
        
        # Clean up empty bool clauses
        self._cleanup_bool_query(query)
        
        return query
    
    def _add_intent_filters(self, query: Dict[str, Any], intent: QueryIntent, 
                           entities: List[Entity], entity_summary: Dict[str, List[str]]):
        """Add filters based on classified intent."""
        bool_query = query["query"]["bool"]
        
        if intent == QueryIntent.SHOW_FAILED_LOGINS:
            # Add failed login specific filters
            bool_query["should"].extend([
                {"term": {"winlog.event_id": "4625"}},
                {"term": {"event.code": "4625"}},
                {"match": {"message": "authentication failed"}},
                {"match": {"message": "login failed"}},
                {"match": {"event.action": "logon-failed"}},
                {"term": {"event.outcome": "failure"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.SHOW_SUCCESSFUL_LOGINS:
            bool_query["should"].extend([
                {"term": {"winlog.event_id": "4624"}},
                {"term": {"event.code": "4624"}},
                {"match": {"message": "authentication successful"}},
                {"match": {"message": "login successful"}},
                {"match": {"event.action": "logon"}},
                {"term": {"event.outcome": "success"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.SECURITY_ALERTS:
            bool_query["should"].extend([
                {"range": {"event.severity": {"gte": 7}}},
                {"terms": {"event.type": ["alert", "security", "threat"]}},
                {"match": {"message": "security"}},
                {"match": {"message": "alert"}},
                {"match": {"tags": "security"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.SYSTEM_ERRORS:
            bool_query["should"].extend([
                {"terms": {"log.level": ["ERROR", "CRITICAL", "FATAL"]}},
                {"match": {"message": "error"}},
                {"match": {"message": "crash"}},
                {"match": {"message": "exception"}},
                {"term": {"event.outcome": "failure"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.NETWORK_TRAFFIC:
            bool_query["should"].extend([
                {"exists": {"field": "source.ip"}},
                {"exists": {"field": "destination.ip"}},
                {"exists": {"field": "network.protocol"}},
                {"match": {"event.category": "network"}}
            ])
            bool_query["minimum_should_match"] = 1
            
        elif intent == QueryIntent.MALWARE_DETECTION:
            bool_query["should"].extend([
                {"match": {"message": "malware"}},
                {"match": {"message": "virus"}},
                {"match": {"message": "trojan"}},
                {"match": {"message": "threat"}},
                {"match": {"event.type": "malware"}},
                {"match": {"tags": "malware"}}
            ])
            bool_query["minimum_should_match"] = 1
    
    def _add_entity_filters(self, query: Dict[str, Any], entities: List[Entity], 
                           entity_summary: Dict[str, List[str]]):
        """Add filters based on extracted entities."""
        bool_query = query["query"]["bool"]
        
        # Helper: return preferred fields from external mappings (if provided) or sensible defaults
        def preferred(kind: str, defaults: List[str]) -> List[str]:
            # kind examples: 'username', 'source_ip', 'dest_ip', 'event_id', 'process', 'file.path'
            results = []
            if self.external_mappings and self.index_class:
                cls = self.external_mappings.get(self.index_class, {})
                if kind in cls:
                    results.extend([f for f in cls.get(kind, []) if isinstance(f, str)])
            # Append defaults ensuring uniqueness
            for f in defaults:
                if f not in results:
                    results.append(f)
            return results

        # IP Address filters
        if 'ip_address' in entity_summary:
            ip_filters = []
            # gather candidate ip fields
            ip_fields = (
                preferred('source_ip', ['source.ip', 'client.ip', 'host.ip'])
                + preferred('destination_ip', ['destination.ip', 'server.ip'])
            )
            for ip in entity_summary['ip_address']:
                for f in ip_fields:
                    ip_filters.append({"term": {f: ip}})
            if ip_filters:
                bool_query.setdefault("should", []).extend(ip_filters)
                if not bool_query.get("minimum_should_match"):
                    bool_query["minimum_should_match"] = 1
        
        # Username filters
        if 'username' in entity_summary:
            username_filters = []
            user_fields = preferred('username', ['user.name', 'winlog.event_data.TargetUserName', 'system.auth.user'])
            for username in entity_summary['username']:
                for f in user_fields:
                    # exact via .keyword if applicable, else wildcard
                    username_filters.append({"term": {f + (".keyword" if not f.endswith('.keyword') else ""): username}})
                    username_filters.append({"wildcard": {f: f"*{username}*"}})
                username_filters.append({"match": {"message": username}})
            if username_filters:
                bool_query.setdefault("should", []).extend(username_filters)
                if not bool_query.get("minimum_should_match"):
                    bool_query["minimum_should_match"] = 1
        
        # Event ID filters
        if 'event_id' in entity_summary:
            for event_id in entity_summary['event_id']:
                bool_query["must"].extend([
                    {
                        "bool": {
                            "should": [
                                {"term": {"winlog.event_id": event_id}},
                                {"term": {"event.code": event_id}},
                                {"term": {"event.id": event_id}}
                            ]
                        }
                    }
                ])
        
        # Port filters
        if 'port' in entity_summary:
            port_filters = []
            for port in entity_summary['port']:
                port_filters.extend([
                    {"term": {"source.port": int(port)}},
                    {"term": {"destination.port": int(port)}},
                    {"term": {"network.port": int(port)}}
                ])
            
            if port_filters:
                bool_query["should"].extend(port_filters)
                if not bool_query.get("minimum_should_match"):
                    bool_query["minimum_should_match"] = 1
        
        # Domain filters
        if 'domain' in entity_summary:
            domain_filters = []
            domain_fields = preferred('domain', ['url.domain', 'dns.question.name'])
            for domain in entity_summary['domain']:
                for f in domain_fields:
                    domain_filters.append({"match": {f: domain}})
                domain_filters.append({"match": {"message": domain}})
            
            if domain_filters:
                bool_query.setdefault("should", []).extend(domain_filters)
        
        # Process name filters
        if 'process_name' in entity_summary:
            process_filters = []
            process_fields = preferred('process', ['process.name', 'winlog.event_data.ProcessName', 'process.executable'])
            for process in entity_summary['process_name']:
                for f in process_fields:
                    matcher = {"wildcard": {f: f"*{process}*"}} if f.endswith('executable') else {"match": {f: process}}
                    process_filters.append(matcher)
            
            if process_filters:
                bool_query.setdefault("should", []).extend(process_filters)
        
        # File path filters
        if 'file_path' in entity_summary:
            file_filters = []
            file_fields = preferred('file.path', ['file.path', 'winlog.event_data.ObjectName'])
            for file_path in entity_summary['file_path']:
                for f in file_fields:
                    file_filters.append({"match": {f: file_path}})
                file_filters.append({"wildcard": {"file.path.keyword": f"*{file_path}*"}})
            
            if file_filters:
                bool_query.setdefault("should", []).extend(file_filters)
        
        # Severity filters
        if 'severity' in entity_summary:
            for severity in entity_summary['severity']:
                severity_map = {
                    'critical': 10,
                    'high': 8, 
                    'medium': 5,
                    'low': 3,
                    'info': 1
                }
                
                if severity.lower() in severity_map:
                    bool_query["filter"].append({
                        "range": {
                            "event.severity": {
                                "gte": severity_map[severity.lower()]
                            }
                        }
                    })
    
    def _add_time_filter(self, query: Dict[str, Any], time_range: Dict[str, Any]):
        """Add time range filter to query."""
        if not time_range:
            return
        
        time_filter = {"range": {"@timestamp": {}}}
        
        if time_range.get('start_time'):
            if time_range.get('relative', False):
                # Use relative time for better performance
                if 'Last' in time_range.get('description', ''):
                    desc = time_range['description'].lower()
                    if 'hour' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1h"
                    elif 'day' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1d"
                    elif 'week' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1w"
                    elif 'month' in desc:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1M"
                    else:
                        time_filter["range"]["@timestamp"]["gte"] = "now-1h"
                elif time_range['description'].lower() == 'today':
                    time_filter["range"]["@timestamp"]["gte"] = "now/d"
                elif time_range['description'].lower() == 'yesterday':
                    time_filter["range"]["@timestamp"]["gte"] = "now-1d/d"
                    time_filter["range"]["@timestamp"]["lte"] = "now/d"
            else:
                # Use absolute timestamp
                time_filter["range"]["@timestamp"]["gte"] = time_range['start_time'].isoformat()
        
        if time_range.get('end_time') and not time_range.get('relative', False):
            time_filter["range"]["@timestamp"]["lte"] = time_range['end_time'].isoformat()
        
        query["query"]["bool"]["filter"].append(time_filter)
    
    def _add_aggregations(self, query: Dict[str, Any], intent: QueryIntent, entities: List[Entity]):
        """Add aggregations for summary statistics."""
        aggs = {}
        
        if intent in [QueryIntent.SHOW_FAILED_LOGINS, QueryIntent.SHOW_SUCCESSFUL_LOGINS]:
            aggs["users"] = {
                "terms": {
                    "field": "user.name.keyword",
                    "size": 20
                }
            }
            aggs["source_ips"] = {
                "terms": {
                    "field": "source.ip",
                    "size": 20
                }
            }
            aggs["timeline"] = {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "hour"
                }
            }
        
        elif intent == QueryIntent.NETWORK_TRAFFIC:
            aggs["protocols"] = {
                "terms": {
                    "field": "network.protocol",
                    "size": 10
                }
            }
            aggs["top_source_ips"] = {
                "terms": {
                    "field": "source.ip",
                    "size": 20
                }
            }
            aggs["top_dest_ports"] = {
                "terms": {
                    "field": "destination.port",
                    "size": 20
                }
            }
        
        elif intent == QueryIntent.SECURITY_ALERTS:
            aggs["severity_breakdown"] = {
                "terms": {
                    "field": "event.severity",
                    "size": 10
                }
            }
            aggs["alert_types"] = {
                "terms": {
                    "field": "event.type",
                    "size": 20
                }
            }
        
        if aggs:
            query["aggs"] = aggs
    
    def _load_index_mappings(self) -> Dict[str, Any]:
        """Load optional external index mappings YAML (config/index_mappings.yaml)."""
        try:
            cfg_path = Path(__file__).resolve().parents[1] / 'config' / 'index_mappings.yaml'
            if cfg_path.exists():
                with cfg_path.open('r', encoding='utf-8') as fh:
                    return yaml.safe_load(fh) or {}
        except Exception as e:
            logger.warning(f"Index mappings load failed: {e}")
        return {}

    def _cleanup_bool_query(self, query: Dict[str, Any]):
        """Remove empty bool clauses."""
        bool_query = query["query"]["bool"]
        
        # Remove empty clauses
        for clause in ["must", "should", "filter", "must_not"]:
            if not bool_query.get(clause):
                bool_query.pop(clause, None)
        
        # If no clauses, add a match_all query
        if not any(bool_query.get(clause) for clause in ["must", "should", "filter", "must_not"]):
            query["query"] = {"match_all": {}}
    
    def build_kql_query(self, natural_query: str) -> str:
        """
        Convert natural language to KQL (Kibana Query Language).
        
        Args:
            natural_query: Natural language query
            
        Returns:
            KQL query string
        """
        # Classify intent and extract entities
        intent, _ = self.intent_classifier.classify_intent(natural_query)
        entities = self.entity_extractor.extract_entities(natural_query)
        entity_summary = self.entity_extractor.get_entity_summary(entities)
        
        kql_parts = []
        
        # Intent-based KQL
        if intent == QueryIntent.SHOW_FAILED_LOGINS:
            kql_parts.append("(winlog.event_id:4625 OR event.code:4625 OR event.outcome:failure)")
            
        elif intent == QueryIntent.SHOW_SUCCESSFUL_LOGINS:
            kql_parts.append("(winlog.event_id:4624 OR event.code:4624 OR event.outcome:success)")
            
        elif intent == QueryIntent.SECURITY_ALERTS:
            kql_parts.append("(event.type:alert OR event.type:security OR tags:security)")
            
        elif intent == QueryIntent.SYSTEM_ERRORS:
            kql_parts.append("(log.level:ERROR OR log.level:CRITICAL OR event.outcome:failure)")
        
        # Entity-based KQL
        if 'ip_address' in entity_summary:
            ip_conditions = []
            for ip in entity_summary['ip_address']:
                ip_conditions.append(f"(source.ip:{ip} OR destination.ip:{ip} OR client.ip:{ip})")
            kql_parts.append(f"({' OR '.join(ip_conditions)})")
        
        if 'username' in entity_summary:
            user_conditions = []
            for username in entity_summary['username']:
                user_conditions.append(f"user.name:{username}")
            kql_parts.append(f"({' OR '.join(user_conditions)})")
        
        if 'event_id' in entity_summary:
            event_conditions = []
            for event_id in entity_summary['event_id']:
                event_conditions.append(f"(winlog.event_id:{event_id} OR event.code:{event_id})")
            kql_parts.append(f"({' OR '.join(event_conditions)})")
        
        # Combine with AND
        if kql_parts:
            return " AND ".join(kql_parts)
        else:
            return "*"  # Match all if no specific conditions


# Example usage and testing
if __name__ == "__main__":
    builder = QueryBuilder()
    
    test_queries = [
        "Show failed logins from user admin in the last hour",
        "Find security alerts with high severity from 192.168.1.100",
        "Get network traffic on port 443 from yesterday",
        "Show successful logins for john.doe@company.com",
        "Find malware detections in the last 24 hours",
        "List system errors from server.example.com"
    ]
    
    print("Query Builder Test:")
    print("=" * 70)
    
    for natural_query in test_queries:
        print(f"\nNatural Query: {natural_query}")
        
        # Build Elasticsearch DSL
        es_query = builder.build_query(natural_query)
        print("Elasticsearch DSL:")
        import json
        print(json.dumps(es_query, indent=2))
        
        # Build KQL
        kql_query = builder.build_kql_query(natural_query)
        print(f"KQL: {kql_query}")
        
        print("-" * 70)