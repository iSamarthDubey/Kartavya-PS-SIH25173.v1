"""
Elasticsearch SIEM Connector
Handles connections and queries to Elasticsearch SIEM platforms.
"""

import os
from elasticsearch import Elasticsearch
from typing import Dict, List, Any, Optional
import logging

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
    
    def _connect(self) -> Elasticsearch:
        """Establish connection to Elasticsearch."""
        try:
            if self.username and self.password:
                client = Elasticsearch(
                    [{'host': self.host, 'port': self.port}],
                    basic_auth=(self.username, self.password),
                    verify_certs=False
                )
            else:
                client = Elasticsearch([{'host': self.host, 'port': self.port}])
            
            # Test connection
            if client.ping():
                logger.info(f"Connected to Elasticsearch at {self.host}:{self.port}")
                return client
            else:
                raise ConnectionError("Failed to ping Elasticsearch")
                
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise
    
    def execute_query(self, query: Dict[str, Any], size: int = 100) -> Dict[str, Any]:
        """Execute a query against Elasticsearch."""
        try:
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
            indices = self.client.indices.get_alias(index="*")
            return list(indices.keys())
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            return []
    
    def get_field_mappings(self, index: Optional[str] = None) -> Dict[str, Any]:
        """Get field mappings for an index."""
        target_index = index or self.index
        try:
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