"""
Elasticsearch Client Wrapper
Provides high-level interface for Elasticsearch operations.
"""

from elasticsearch import Elasticsearch
import logging
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ElasticClient:
    """High-level Elasticsearch client wrapper."""
    
    def __init__(self, host: str = "localhost", port: int = 9200, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """Initialize Elasticsearch client."""
        self.host = host
        self.port = port
        
        # Build connection configuration
        config = {
            'hosts': [{'host': host, 'port': port, 'scheme': 'http'}],
            'timeout': 30,
            'max_retries': 3,
            'retry_on_timeout': True
        }
        
        # Add authentication if provided
        if username and password:
            config['http_auth'] = (username, password)
        
        try:
            self.client = Elasticsearch(**config)
            self.connected = self._test_connection()
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {e}")
            self.client = None
            self.connected = False
    
    def _test_connection(self) -> bool:
        """Test Elasticsearch connection."""
        try:
            info = self.client.info()
            logger.info(f"Connected to Elasticsearch: {info['version']['number']}")
            return True
        except Exception as e:
            logger.error(f"Elasticsearch connection test failed: {e}")
            return False
    
    def search(self, index: str, query: Dict[str, Any], 
               size: int = 100) -> List[Dict[str, Any]]:
        """Execute search query."""
        if not self.connected:
            raise ConnectionError("Not connected to Elasticsearch")
        
        try:
            response = self.client.search(
                index=index,
                body=query,
                size=size
            )
            
            # Extract hits from response
            hits = response.get('hits', {}).get('hits', [])
            results = []
            
            for hit in hits:
                result = hit.get('_source', {})
                result['_score'] = hit.get('_score', 0)
                result['_index'] = hit.get('_index', '')
                results.append(result)
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def search_logs(self, query_string: str, time_range: Optional[str] = None,
                   index_pattern: str = "logs-*") -> List[Dict[str, Any]]:
        """Search logs with natural language query string."""
        # Build Elasticsearch query
        es_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": query_string,
                                "default_field": "message"
                            }
                        }
                    ]
                }
            },
            "sort": [
                {"@timestamp": {"order": "desc"}}
            ]
        }
        
        # Add time range filter if specified
        if time_range:
            time_filter = self._build_time_filter(time_range)
            if time_filter:
                es_query["query"]["bool"]["filter"] = [time_filter]
        
        return self.search(index_pattern, es_query)
    
    def _build_time_filter(self, time_range: str) -> Optional[Dict[str, Any]]:
        """Build time range filter for Elasticsearch query."""
        time_filters = {
            "last_hour": "now-1h",
            "last_day": "now-1d",
            "last_week": "now-1w",
            "last_month": "now-1M"
        }
        
        if time_range.lower() in time_filters:
            return {
                "range": {
                    "@timestamp": {
                        "gte": time_filters[time_range.lower()]
                    }
                }
            }
        
        return None
    
    def count(self, index: str, query: Dict[str, Any]) -> int:
        """Count documents matching query."""
        if not self.connected:
            raise ConnectionError("Not connected to Elasticsearch")
        
        try:
            response = self.client.count(index=index, body=query)
            return response.get('count', 0)
        except Exception as e:
            logger.error(f"Count failed: {e}")
            return 0
    
    def get_indices(self) -> List[str]:
        """Get list of available indices."""
        if not self.connected:
            return []
        
        try:
            indices = self.client.indices.get_alias()
            return list(indices.keys())
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            return []
    
    def health(self) -> Dict[str, Any]:
        """Get cluster health information."""
        if not self.connected:
            return {"status": "disconnected"}
        
        try:
            health = self.client.cluster.health()
            return {
                "status": health.get('status', 'unknown'),
                "cluster_name": health.get('cluster_name', ''),
                "number_of_nodes": health.get('number_of_nodes', 0),
                "active_primary_shards": health.get('active_primary_shards', 0)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}