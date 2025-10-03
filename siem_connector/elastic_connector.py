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