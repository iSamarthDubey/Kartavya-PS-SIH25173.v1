"""
Elasticsearch SIEM Connector
Handles connections and queries to Elasticsearch SIEM platforms.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


class ElasticConnector:
    """Connector for Elasticsearch SIEM platforms."""
    
    def __init__(self):
        """Initialize Elasticsearch connection."""
        self.host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        self.port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
        self.username = os.getenv('ELASTICSEARCH_USERNAME')
        self.password = os.getenv('ELASTICSEARCH_PASSWORD')
        self.index = os.getenv('ELASTICSEARCH_INDEX', 'security-logs')

        self.client = self._connect()
        self._available = self.client is not None
    
    def _connect(self) -> Elasticsearch:
        """Establish connection to Elasticsearch."""
        try:
            hosts = [f'http://{self.host}:{self.port}']
            if self.username and self.password:
                client = Elasticsearch(
                    hosts,
                    basic_auth=(self.username, self.password),
                    verify_certs=False,
                    request_timeout=10,
                    max_retries=2,
                    retry_on_timeout=True,
                    headers={'Accept': 'application/json'}
                )
            else:
                client = Elasticsearch(
                    hosts,
                    request_timeout=10,
                    max_retries=2,
                    retry_on_timeout=True,
                    headers={'Accept': 'application/json'}
                )

            # Test connection
            if client.ping():
                logger.info(f"Connected to Elasticsearch at {self.host}:{self.port}")
                return client
            else:
                logger.warning(
                    "Elasticsearch ping failed for %s:%s. Proceeding without a live cluster.",
                    self.host,
                    self.port,
                )
                return None
                
        except Exception as e:
            logger.warning(
                "Failed to connect to Elasticsearch at %s:%s (%s). Running in mock-data mode.",
                self.host,
                self.port,
                e,
            )
            return None

    def is_available(self) -> bool:
        """Return True if a live Elasticsearch client is available."""
        return self.client is not None

    async def search(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute a keyword search and return normalized hits."""
        if not self.is_available():
            return {"hits": [], "total": 0, "aggregations": {}}

        try:
            return await asyncio.to_thread(self._search_sync, query or "*", limit)
        except Exception as exc:
            logger.warning(f"Elasticsearch search failed: {exc}")
            return {"hits": [], "total": 0, "aggregations": {}}
    
    async def query_windows_security_events(self, query_params: Dict[str, Any], size: int = 100) -> Dict[str, Any]:
        """Query Windows Security events from winlogbeat indices."""
        if not self.is_available():
            return {"hits": [], "total": 0, "aggregations": {}}
            
        # Build Windows Security specific query
        query_dsl = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"beat.name": "winlogbeat"}},
                        {"match": {"event.provider": "Microsoft-Windows-Security-Auditing"}}
                    ]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        # Add specific filters based on query params
        if event_id := query_params.get("event_id"):
            query_dsl["query"]["bool"]["must"].append({"match": {"event.code": event_id}})
        
        if user := query_params.get("user"):
            query_dsl["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": user,
                    "fields": ["user.name", "user.domain", "winlog.event_data.SubjectUserName"]
                }
            })
        
        if source_ip := query_params.get("source_ip"):
            query_dsl["query"]["bool"]["must"].append({"match": {"source.ip": source_ip}})
            
        if time_range := query_params.get("time_range"):
            query_dsl["query"]["bool"]["filter"] = {
                "range": {
                    "@timestamp": {
                        "gte": time_range.get("gte", "now-1h"),
                        "lte": time_range.get("lte", "now")
                    }
                }
            }
        
        try:
            return await asyncio.to_thread(self._execute_windows_query, query_dsl, size)
        except Exception as exc:
            logger.warning(f"Windows security query failed: {exc}")
            return {"hits": [], "total": 0, "aggregations": {}}
    
    async def query_failed_logins(self, time_range: str = "1h", size: int = 100) -> Dict[str, Any]:
        """Query failed login attempts from Windows Security logs."""
        query_params = {
            "event_id": 4625,  # Windows failed logon event
            "time_range": {"gte": f"now-{time_range}", "lte": "now"}
        }
        return await self.query_windows_security_events(query_params, size)
    
    async def query_successful_logins(self, time_range: str = "1h", size: int = 100) -> Dict[str, Any]:
        """Query successful login attempts from Windows Security logs."""
        query_params = {
            "event_id": 4624,  # Windows successful logon event
            "time_range": {"gte": f"now-{time_range}", "lte": "now"}
        }
        return await self.query_windows_security_events(query_params, size)
    
    async def query_process_creation(self, time_range: str = "1h", size: int = 100) -> Dict[str, Any]:
        """Query process creation events from Windows Security logs."""
        query_params = {
            "event_id": 4688,  # Windows process creation event
            "time_range": {"gte": f"now-{time_range}", "lte": "now"}
        }
        return await self.query_windows_security_events(query_params, size)
    
    async def query_system_metrics(self, time_range: str = "1h", size: int = 100) -> Dict[str, Any]:
        """Query system metrics from metricbeat indices."""
        if not self.is_available():
            return {"hits": [], "total": 0, "aggregations": {}}
            
        query_dsl = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"beat.name": "metricbeat"}},
                        {"exists": {"field": "system.cpu.total.pct"}}
                    ],
                    "filter": {
                        "range": {
                            "@timestamp": {
                                "gte": f"now-{time_range}",
                                "lte": "now"
                            }
                        }
                    }
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        try:
            return await asyncio.to_thread(self._execute_windows_query, query_dsl, size)
        except Exception as exc:
            logger.warning(f"System metrics query failed: {exc}")
            return {"hits": [], "total": 0, "aggregations": {}}
    
    def _execute_windows_query(self, query_dsl: Dict[str, Any], size: int) -> Dict[str, Any]:
        """Execute Windows-specific query and normalize response."""
        try:
            # Use the Windows-specific indices
            security_index = os.getenv('ELASTICSEARCH_SECURITY_INDEX', 'winlogbeat-*')
            
            response = self.client.search(
                index=security_index,
                body=query_dsl,
                size=size
            )
            
            return self.normalize_windows_response(response)
        except Exception as e:
            logger.error(f"Windows query execution failed: {e}")
            return {"hits": [], "total": 0, "aggregations": {}}

    def _search_sync(self, query: Any, limit: int) -> Dict[str, Any]:
        if isinstance(query, dict):
            query_dsl = query
        else:
            query_dsl = {
                "query": {
                    "query_string": {
                        "query": query or "*",
                        "default_operator": "AND",
                    }
                }
            }

        normalized = self.send_query_to_elastic(query_dsl, size=limit)
        hits = normalized.get("hits", [])
        metadata = normalized.get("metadata", {})
        return {
            "hits": hits,
            "total": metadata.get("total_hits", len(hits)),
            "aggregations": normalized.get("aggregations", {}),
        }
    
    def execute_query(self, query: Dict[str, Any], size: int = 100) -> Dict[str, Any]:
        """Execute a query against Elasticsearch."""
        try:
            if not self.client:
                logger.info("Elasticsearch client unavailable; execute_query returning empty result")
                return {'hits': [], 'aggregations': {}, 'metadata': {'total_hits': 0}}
            
            # Add size to query body if not already present to avoid parameter conflict
            if 'size' not in query:
                query['size'] = size
            
            response = self.client.search(
                index=self.index,
                body=query
            )
            return response
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_kql(self, kql_query: str, size: int = 100) -> Dict[str, Any]:
        """Execute a KQL query."""
        # Convert KQL to Elasticsearch DSL
        query = {
            "query": {
                "query_string": {
                    "query": kql_query
                }
            }
        }
        return self.execute_query(query, size)
    
    def get_indices(self) -> List[str]:
        """Get list of available indices."""
        try:
            if not self.client:
                logger.info("Elasticsearch client unavailable; no indices to list")
                return []
            indices = self.client.indices.get_alias(index="*")
            return list(indices.keys())
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            return []
    
    def get_field_mappings(self, index: Optional[str] = None) -> Dict[str, Any]:
        """Get field mappings for an index."""
        target_index = index or self.index
        try:
            if not self.client:
                logger.info("Elasticsearch client unavailable; no field mappings available")
                return {}
            mappings = self.client.indices.get_mapping(index=target_index)
            return mappings
        except Exception as e:
            logger.error(f"Failed to get mappings: {e}")
            return {}
    
    def send_query_to_elastic(self, query_dsl: Dict[str, Any], index: Optional[str] = None, 
                             size: int = 100) -> Dict[str, Any]:
        """
        Send DSL query to Elasticsearch and return normalized response.
        
        Args:
            query_dsl: Elasticsearch DSL query dictionary
            index: Target index (defaults to configured index)
            size: Maximum number of results to return
            
        Returns:
            Normalized response with hits, aggregations, and metadata
        """
        try:
            target_index = index or self.index
            if not self.client:
                logger.info("Elasticsearch client unavailable; returning empty query response")
                return {
                    'hits': [],
                    'aggregations': {},
                    'metadata': {
                        'total_hits': 0,
                        'error': 'client_unavailable'
                    }
                }
            
            logger.info(f"Executing query on index '{target_index}' with size {size}")
            
            response = self.client.search(
                index=target_index,
                body=query_dsl,
                size=size
            )
            
            # Normalize response
            normalized_response = self.normalize_response(response)
            
            logger.info(f"Query executed successfully: {normalized_response['metadata']['total_hits']} hits")
            return normalized_response
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def fetch_alerts(self, severity: Optional[str] = None, time_range: Optional[str] = "last_hour",
                    size: int = 100) -> Dict[str, Any]:
        """
        Fetch security alerts from Elasticsearch.
        
        Args:
            severity: Alert severity filter (low, medium, high, critical)
            time_range: Time range for alerts (last_hour, last_day, last_week)
            size: Maximum number of alerts to return
            
        Returns:
            Normalized alerts response
        """
        try:
            # Build alerts query
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"event.kind": "alert"}},
                        ],
                        "filter": []
                    }
                },
                "sort": [
                    {"@timestamp": {"order": "desc"}}
                ]
            }
            
            # Add severity filter
            if severity:
                severity_map = {
                    "low": [1, 2, 3],
                    "medium": [4, 5, 6],
                    "high": [7, 8, 9],
                    "critical": [10, 11, 12]
                }
                if severity.lower() in severity_map:
                    query["query"]["bool"]["should"] = [
                        {"terms": {"rule.level": severity_map[severity.lower()]}},
                        {"terms": {"signal.rule.severity": [severity.lower()]}}
                    ]
                    query["query"]["bool"]["minimum_should_match"] = 1
            
            # Add time range filter
            if time_range:
                time_filter = self._build_time_filter(time_range)
                if time_filter:
                    query["query"]["bool"]["filter"].append(time_filter)
            
            return self.send_query_to_elastic(query, size=size)
            
        except Exception as e:
            logger.error(f"Failed to fetch alerts: {e}")
            raise
    
    def fetch_logs(self, log_type: Optional[str] = None, time_range: Optional[str] = "last_hour",
                  source_ip: Optional[str] = None, size: int = 100) -> Dict[str, Any]:
        """
        Fetch logs from Elasticsearch with optional filters.
        
        Args:
            log_type: Type of logs (auth, network, system, etc.)
            time_range: Time range for logs
            source_ip: Filter by source IP address
            size: Maximum number of logs to return
            
        Returns:
            Normalized logs response
        """
        try:
            # Build logs query
            query = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": []
                    }
                },
                "sort": [
                    {"@timestamp": {"order": "desc"}}
                ]
            }
            
            # Add log type filter
            if log_type:
                log_type_filters = {
                    "auth": [
                        {"match": {"event.category": "authentication"}},
                        {"match": {"log.file.path": "*auth*"}},
                        {"terms": {"winlog.event_id": ["4624", "4625", "4634"]}}
                    ],
                    "network": [
                        {"match": {"event.category": "network"}},
                        {"exists": {"field": "source.ip"}},
                        {"exists": {"field": "destination.ip"}}
                    ],
                    "system": [
                        {"match": {"event.category": "system"}},
                        {"match": {"log.file.path": "*system*"}}
                    ]
                }
                
                if log_type.lower() in log_type_filters:
                    query["query"]["bool"]["should"] = log_type_filters[log_type.lower()]
                    query["query"]["bool"]["minimum_should_match"] = 1
            
            # Add source IP filter
            if source_ip:
                query["query"]["bool"]["must"].append({
                    "bool": {
                        "should": [
                            {"term": {"source.ip": source_ip}},
                            {"term": {"client.ip": source_ip}},
                            {"term": {"host.ip": source_ip}}
                        ],
                        "minimum_should_match": 1
                    }
                })
            
            # Add time range filter
            if time_range:
                time_filter = self._build_time_filter(time_range)
                if time_filter:
                    query["query"]["bool"]["filter"].append(time_filter)
            
            return self.send_query_to_elastic(query, size=size)
            
        except Exception as e:
            logger.error(f"Failed to fetch logs: {e}")
            raise
    
    def normalize_windows_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Windows Beats response to SYNRGY format.
        Maps Windows Event Log fields to standardized security event format.
        """
        try:
            hits = response.get('hits', {})
            total_hits = hits.get('total', {})
            
            # Handle different Elasticsearch versions
            if isinstance(total_hits, dict):
                total_count = total_hits.get('value', 0)
            else:
                total_count = total_hits
            
            # Extract and normalize Windows log entries
            normalized_hits = []
            for hit in hits.get('hits', []):
                source = hit.get('_source', {})
                
                # Map Windows fields to SYNRGY standard format
                normalized_hit = {
                    '@timestamp': source.get('@timestamp'),
                    'message': self._extract_windows_message(source),
                    'severity': self._map_windows_severity(source),
                    'source': {
                        'ip': source.get('source', {}).get('ip', source.get('winlog', {}).get('event_data', {}).get('IpAddress', '')),
                        'name': source.get('host', {}).get('name', source.get('agent', {}).get('hostname', ''))
                    },
                    'destination': {
                        'ip': source.get('destination', {}).get('ip', ''),
                        'port': source.get('destination', {}).get('port', '')
                    },
                    'user': {
                        'name': self._extract_windows_user(source)
                    },
                    'event': {
                        'action': self._map_windows_action(source),
                        'category': source.get('event', {}).get('category', ''),
                        'outcome': self._map_windows_outcome(source),
                        'id': source.get('event', {}).get('code', source.get('winlog', {}).get('event_id', ''))
                    },
                    'network': {
                        'protocol': source.get('network', {}).get('protocol', '')
                    },
                    'process': {
                        'name': source.get('process', {}).get('name', source.get('winlog', {}).get('event_data', {}).get('ProcessName', '')),
                        'pid': source.get('process', {}).get('pid', source.get('winlog', {}).get('event_data', {}).get('ProcessId', ''))
                    },
                    'raw': source  # Keep original Windows log data
                }
                
                normalized_hits.append(normalized_hit)
            
            return {
                'hits': normalized_hits,
                'aggregations': response.get('aggregations', {}),
                'metadata': {
                    'total_hits': total_count,
                    'took': response.get('took'),
                    'timed_out': response.get('timed_out', False),
                    'source': 'windows_beats'
                }
            }
            
        except Exception as e:
            logger.error(f"Windows response normalization failed: {e}")
            return {
                'hits': [],
                'aggregations': {},
                'metadata': {
                    'total_hits': 0,
                    'error': str(e),
                    'source': 'windows_beats'
                }
            }
    
    def _extract_windows_message(self, source: Dict[str, Any]) -> str:
        """Extract meaningful message from Windows log entry."""
        # Try different message fields in order of preference
        message_fields = [
            'message',
            'event.original',
            'winlog.event_data.Message',
            'log.level'
        ]
        
        for field in message_fields:
            if '.' in field:
                # Handle nested fields
                value = source
                for key in field.split('.'):
                    value = value.get(key, {})
                    if not isinstance(value, dict):
                        break
                if isinstance(value, str) and value:
                    return value
            else:
                value = source.get(field)
                if isinstance(value, str) and value:
                    return value
        
        # Fallback to event description
        event_id = source.get('winlog', {}).get('event_id', '')
        if event_id:
            event_descriptions = {
                '4624': 'Successful logon',
                '4625': 'Failed logon attempt',
                '4634': 'User logoff',
                '4688': 'Process creation',
                '4672': 'Special privileges assigned',
                '4698': 'Scheduled task created'
            }
            return event_descriptions.get(str(event_id), f'Windows Event ID {event_id}')
        
        return 'Windows security event'
    
    def _extract_windows_user(self, source: Dict[str, Any]) -> str:
        """Extract username from Windows log entry."""
        user_fields = [
            'user.name',
            'winlog.event_data.TargetUserName',
            'winlog.event_data.SubjectUserName',
            'winlog.user.name'
        ]
        
        for field in user_fields:
            value = source
            for key in field.split('.'):
                value = value.get(key, {})
                if not isinstance(value, dict):
                    break
            if isinstance(value, str) and value and value != '-':
                return value
        
        return ''
    
    def _map_windows_severity(self, source: Dict[str, Any]) -> str:
        """Map Windows log level to SYNRGY severity."""
        level = source.get('log', {}).get('level', '').lower()
        event_id = str(source.get('winlog', {}).get('event_id', ''))
        
        # Map based on event ID (Windows Security Events)
        critical_events = ['4625', '4648', '4719', '4964']  # Failed logins, privilege abuse
        high_events = ['4624', '4634', '4672']  # Successful logins, privilege assignments
        medium_events = ['4688', '4698']  # Process creation, scheduled tasks
        
        if event_id in critical_events:
            return 'high'  # Treat failed logins as high severity
        elif event_id in high_events:
            return 'medium'
        elif event_id in medium_events:
            return 'low'
        
        # Map based on log level
        level_map = {
            'critical': 'critical',
            'error': 'high',
            'warning': 'medium',
            'info': 'low',
            'information': 'low'
        }
        
        return level_map.get(level, 'unknown')
    
    def _map_windows_action(self, source: Dict[str, Any]) -> str:
        """Map Windows event to action description."""
        event_id = str(source.get('winlog', {}).get('event_id', ''))
        
        action_map = {
            '4624': 'user_login_success',
            '4625': 'user_login_failed',
            '4634': 'user_logout',
            '4688': 'process_created',
            '4672': 'privilege_assigned',
            '4698': 'scheduled_task_created',
            '4719': 'system_audit_policy_changed'
        }
        
        return action_map.get(event_id, source.get('event', {}).get('action', 'windows_event'))
    
    def _map_windows_outcome(self, source: Dict[str, Any]) -> str:
        """Map Windows event outcome."""
        event_id = str(source.get('winlog', {}).get('event_id', ''))
        
        # Failed events
        if event_id in ['4625', '4648', '4656']:
            return 'failure'
        # Successful events
        elif event_id in ['4624', '4634', '4688', '4672']:
            return 'success'
        
        return source.get('event', {}).get('outcome', 'unknown')
    
    def normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Elasticsearch response to standard format.
        
        Args:
            response: Raw Elasticsearch response
            
        Returns:
            Normalized response with consistent structure
        """
        try:
            hits = response.get('hits', {})
            total_hits = hits.get('total', {})
            
            # Handle different Elasticsearch versions
            if isinstance(total_hits, dict):
                total_count = total_hits.get('value', 0)
                relation = total_hits.get('relation', 'eq')
            else:
                total_count = total_hits
                relation = 'eq'
            
            # Extract and normalize hit documents
            normalized_hits = []
            for hit in hits.get('hits', []):
                normalized_hit = {
                    'id': hit.get('_id'),
                    'index': hit.get('_index'),
                    'score': hit.get('_score'),
                    'source': hit.get('_source', {}),
                    'highlight': hit.get('highlight', {})
                }
                normalized_hits.append(normalized_hit)
            
            # Extract aggregations
            aggregations = response.get('aggregations', {})
            
            # Build normalized response
            normalized = {
                'hits': normalized_hits,
                'aggregations': aggregations,
                'metadata': {
                    'total_hits': total_count,
                    'relation': relation,
                    'max_score': hits.get('max_score'),
                    'took': response.get('took'),
                    'timed_out': response.get('timed_out', False),
                    'shards': response.get('_shards', {})
                }
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Response normalization failed: {e}")
            # Return basic structure on error
            return {
                'hits': [],
                'aggregations': {},
                'metadata': {
                    'total_hits': 0,
                    'error': str(e)
                }
            }
    
    def _build_time_filter(self, time_range: str) -> Optional[Dict[str, Any]]:
        """Build time range filter for queries."""
        time_mappings = {
            'last_hour': 'now-1h',
            'last_day': 'now-1d', 
            'last_week': 'now-1w',
            'last_month': 'now-1M',
            'today': 'now/d',
            'yesterday': 'now-1d/d'
        }
        
        range_value = time_mappings.get(time_range.lower())
        if range_value:
            return {
                "range": {
                    "@timestamp": {
                        "gte": range_value
                    }
                }
            }
        
        return None
    
    def count_documents(self, query: Dict[str, Any], index: Optional[str] = None) -> int:
        """Count documents matching the query."""
        try:
            target_index = index or self.index
            if not self.client:
                logger.info("Elasticsearch client unavailable; count_documents returning 0")
                return 0
            
            count_response = self.client.count(
                index=target_index,
                body={"query": query.get("query", {"match_all": {}})}
            )
            
            return count_response.get('count', 0)
            
        except Exception as e:
            logger.error(f"Count operation failed: {e}")
            return 0
    
    def get_cluster_health(self) -> Dict[str, Any]:
        """Get Elasticsearch cluster health information."""
        try:
            if not self.client:
                logger.info("Elasticsearch client unavailable; cluster health unknown")
                return {'status': 'unknown', 'error': 'client_unavailable'}
            health = self.client.cluster.health()
            return {
                'status': health.get('status'),
                'cluster_name': health.get('cluster_name'),
                'number_of_nodes': health.get('number_of_nodes'),
                'active_primary_shards': health.get('active_primary_shards'),
                'active_shards': health.get('active_shards'),
                'unassigned_shards': health.get('unassigned_shards')
            }
        except Exception as e:
            logger.error(f"Failed to get cluster health: {e}")
            return {'status': 'unknown', 'error': str(e)}