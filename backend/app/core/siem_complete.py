"""
Kartavya SIEM Connector Module - Complete Implementation
Unified interface for Elasticsearch and Wazuh SIEM platforms
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging


# --- Elasticsearch Connector ---
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
                    verify_certs=False
                )
            else:
                client = Elasticsearch(hosts)

            client = client.options(
                request_timeout=2,
                max_retries=0,
                retry_on_timeout=False,
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
            response = self.client.search(
                index=self.index,
                body=query,
                size=size
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

# --- Wazuh Connector ---
"""
Wazuh SIEM Connector
Handles connections and queries to Wazuh SIEM platforms.
"""

import asyncio
import base64
import logging
import os
from typing import Dict, List, Any, Optional

import requests

logger = logging.getLogger(__name__)


class WazuhConnector:
    """Connector for Wazuh SIEM platforms."""
    
    def __init__(self):
        """Initialize Wazuh connection."""
        self.host = os.getenv('WAZUH_HOST', 'localhost')
        self.port = int(os.getenv('WAZUH_PORT', 55000))
        self.username = os.getenv('WAZUH_USERNAME')
        self.password = os.getenv('WAZUH_PASSWORD')
        self.base_url = f"https://{self.host}:{self.port}"
        
        self.session = requests.Session()
        self.token = self._authenticate()

    def is_available(self) -> bool:
        """Return True when authentication succeeded."""
        return self.token is not None

    async def search(self, query: str, limit: int = 50) -> Dict[str, Any]:
        """Return recent alerts matching the provided query parameters."""
        if not self.is_available():
            return {"hits": [], "total": 0}

        try:
            return await asyncio.to_thread(self._search_alerts, limit)
        except Exception as exc:
            logger.warning("Wazuh search failed: %s", exc)
            return {"hits": [], "total": 0}

    def _search_alerts(self, limit: int) -> Dict[str, Any]:
        alerts = self.get_alerts(limit=limit)
        return {"hits": alerts, "total": len(alerts)}
    
    def _authenticate(self) -> str:
        """Authenticate with Wazuh API."""
        try:
            if not self.username or not self.password:
                raise ValueError("Wazuh credentials not provided")

            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.base_url}/security/user/authenticate",
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                token = response.json()['data']['token']
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                logger.info("Successfully authenticated with Wazuh")
                return token
            else:
                raise Exception(f"Authentication failed: {response.text}")
                
        except Exception as e:
            logger.warning(
                "Wazuh authentication failed for %s:%s (%s). Proceeding without Wazuh integration.",
                self.host,
                self.port,
                e,
            )
            return None
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of Wazuh agents."""
        try:
            if not self.token:
                return []
            response = self.session.get(
                f"{self.base_url}/agents",
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()['data']['affected_items']
            else:
                raise Exception(f"Failed to get agents: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []
    
    def get_alerts(self, **filters) -> List[Dict[str, Any]]:
        """Get alerts with optional filters."""
        try:
            if not self.token:
                return []
            params = {}
            if 'limit' in filters:
                params['limit'] = filters['limit']
            if 'agent_id' in filters:
                params['agent_id'] = filters['agent_id']
            if 'rule_id' in filters:
                params['rule_id'] = filters['rule_id']
            
            response = self.session.get(
                f"{self.base_url}/security/alerts",
                params=params,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()['data']['affected_items']
            else:
                raise Exception(f"Failed to get alerts: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def get_rules(self, **filters) -> List[Dict[str, Any]]:
        """Get Wazuh rules."""
        try:
            if not self.token:
                return []
            params = {}
            if 'limit' in filters:
                params['limit'] = filters['limit']
            
            response = self.session.get(
                f"{self.base_url}/rules",
                params=params,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()['data']['affected_items']
            else:
                raise Exception(f"Failed to get rules: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get rules: {e}")
            return []