"""
Mock SIEM Connector
Implements BaseSIEMConnector interface using the dynamic mock data system
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base import BaseSIEMConnector
from mock.connectors.elasticsearch_fixed import MockElasticsearchConnector

logger = logging.getLogger(__name__)


class MockSIEMConnector(BaseSIEMConnector):
    """
    Mock SIEM connector that uses the dynamic mock data system
    Implements the full BaseSIEMConnector interface for testing and demos
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mock_es = None
        self.name = kwargs.get("name", "mock_siem")
        self.platform = "mock"
        
        logger.info(f"🎭 Initializing Mock SIEM Connector: {self.name}")
        
    async def connect(self) -> bool:
        """Establish connection to mock data system"""
        try:
            logger.info("🔗 Connecting to mock data system...")
            
            # Initialize the mock Elasticsearch connector
            self.mock_es = MockElasticsearchConnector()
            
            # Test connection
            if await self.mock_es.connect():
                self.connected = True
                logger.info("✅ Mock SIEM connector connected successfully")
                return True
            else:
                logger.error("❌ Failed to connect to mock data system")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mock SIEM connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close connection to mock data system"""
        try:
            if self.mock_es:
                await self.mock_es.disconnect()
                logger.info("🔌 Mock SIEM connector disconnected")
            self.connected = False
        except Exception as e:
            logger.error(f"❌ Error disconnecting mock SIEM: {e}")
    
    async def execute_query(
        self,
        query: Dict[str, Any],
        size: int = 100,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a query against the mock data system
        
        Args:
            query: Query in Elasticsearch DSL format
            size: Maximum number of results
            index: Target index (will use appropriate mock index)
            
        Returns:
            Query results in Elasticsearch format
        """
        try:
            if not self.connected or not self.mock_es:
                raise Exception("Mock SIEM connector not connected")
            
            # Use default index if none specified
            target_index = index or "security-logs-demo"
            
            # Build the search body
            search_body = {
                "size": size,
                **query
            }
            
            # Execute search via mock Elasticsearch
            result = self.mock_es.search(target_index, search_body)
            
            logger.debug(f"🔍 Mock query executed: {len(result['hits']['hits'])} results from {target_index}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Mock query execution failed: {e}")
            return {
                "hits": {
                    "total": {"value": 0, "relation": "eq"},
                    "hits": []
                },
                "error": str(e)
            }
    
    async def get_field_mappings(
        self,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get field mappings from mock data system
        
        Args:
            index: Target index
            
        Returns:
            Field mappings dictionary
        """
        try:
            if not self.connected or not self.mock_es:
                raise Exception("Mock SIEM connector not connected")
            
            # Return realistic field mappings based on our mock data structure
            mappings = {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "event": {
                        "properties": {
                            "category": {"type": "keyword"},
                            "type": {"type": "keyword"},
                            "action": {"type": "text"},
                            "outcome": {"type": "keyword"}
                        }
                    },
                    "host": {
                        "properties": {
                            "hostname": {"type": "keyword"},
                            "ip": {"type": "ip"},
                            "os": {
                                "properties": {
                                    "name": {"type": "keyword"},
                                    "family": {"type": "keyword"},
                                    "version": {"type": "keyword"}
                                }
                            }
                        }
                    },
                    "user": {
                        "properties": {
                            "name": {"type": "keyword"},
                            "domain": {"type": "keyword"}
                        }
                    },
                    "source": {
                        "properties": {
                            "ip": {"type": "ip"},
                            "port": {"type": "long"}
                        }
                    },
                    "winlog": {
                        "properties": {
                            "event_id": {"type": "long"},
                            "channel": {"type": "keyword"},
                            "computer_name": {"type": "keyword"}
                        }
                    },
                    "system": {
                        "properties": {
                            "cpu": {
                                "properties": {
                                    "total": {"properties": {"pct": {"type": "float"}}}
                                }
                            },
                            "memory": {
                                "properties": {
                                    "used": {"properties": {"pct": {"type": "float"}}}
                                }
                            }
                        }
                    }
                }
            }
            
            return mappings
            
        except Exception as e:
            logger.error(f"❌ Failed to get mock field mappings: {e}")
            return {"properties": {}}
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        General query method for dashboard and other generic queries
        
        Args:
            query_params: Query parameters (size, type, filters, etc.)
            
        Returns:
            List of results
        """
        try:
            if not self.connected or not self.mock_es:
                await self.connect()
            
            # Extract parameters
            size = query_params.get('size', 100)
            query_type = query_params.get('type', 'general')
            filters = query_params.get('filters', {})
            
            # Build Elasticsearch query based on type
            if query_type == 'network':
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"event.category": "network"}}
                            ]
                        }
                    }
                }
            elif query_type == 'user_activity':
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"event.category": "authentication"}}
                            ]
                        }
                    }
                }
                if query_params.get('username'):
                    es_query["query"]["bool"]["must"].append({
                        "match": {"user.name": query_params['username']}
                    })
            else:
                # General query
                es_query = {
                    "query": {"match_all": {}}
                }
            
            # Apply filters
            if filters:
                filter_clauses = []
                for key, value in filters.items():
                    filter_clauses.append({"term": {key: value}})
                
                if filter_clauses:
                    if "query" not in es_query:
                        es_query["query"] = {"bool": {"filter": filter_clauses}}
                    elif "bool" not in es_query["query"]:
                        es_query["query"] = {"bool": {"must": [es_query["query"]], "filter": filter_clauses}}
                    else:
                        es_query["query"]["bool"]["filter"] = filter_clauses
            
            # Execute query
            result = await self.execute_query(es_query, size=size)
            
            # Extract hits and return as list
            if "hits" in result and "hits" in result["hits"]:
                return [hit["_source"] for hit in result["hits"]["hits"]]
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Mock query failed: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test if connection is working
        
        Returns:
            True if connection is successful
        """
        try:
            return self.connected and self.mock_es is not None
        except Exception as e:
            logger.error(f"❌ Mock connection test failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """
        Check if mock connector is available
        Always returns True since mock data is always available
        
        Returns:
            Always True for mock connector
        """
        return True
    
    async def get_indices(self) -> List[str]:
        """
        Get list of available mock indices
        
        Returns:
            List of mock index names
        """
        try:
            if not self.connected or not self.mock_es:
                return []
            
            # Get indices from mock Elasticsearch
            indices_info = self.mock_es.cat.indices(format="json")
            return [idx["index"] for idx in indices_info]
            
        except Exception as e:
            logger.error(f"❌ Failed to get mock indices: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get mock SIEM statistics
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "connected": self.connected,
            "platform": "mock",
            "name": self.name,
            "type": "Mock SIEM Connector",
            "version": "1.0.0",
            "data_source": "dynamic_mock",
            "last_updated": datetime.now().isoformat()
        }
        
        if self.connected and self.mock_es:
            try:
                # Get cluster info
                cluster_info = self.mock_es.info()
                stats.update({
                    "cluster_name": cluster_info.get("cluster_name", "mock-cluster"),
                    "version": cluster_info.get("version", {}).get("number", "8.11.0"),
                    "indices": await self.get_indices()
                })
            except Exception as e:
                logger.error(f"❌ Failed to get detailed mock stats: {e}")
        
        return stats
    
    async def search(
        self,
        query_string: str,
        size: int = 100,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simple text search in mock data
        
        Args:
            query_string: Search string
            size: Max results
            index: Target index
            
        Returns:
            Search results
        """
        # Build a query_string query for the mock system
        query = {
            "query": {
                "query_string": {
                    "query": query_string if query_string else "*",
                    "default_operator": "AND"
                }
            }
        }
        
        return await self.execute_query(query, size, index)
    
    async def detect_platform(self) -> Dict[str, Any]:
        """Mock platform detection"""
        return {
            "platform": "mock",
            "type": "Mock SIEM Platform",
            "version": "1.0.0",
            "capabilities": ["query", "aggregation", "real-time", "security"],
            "beats_supported": ["winlogbeat", "metricbeat", "auditbeat", "packetbeat", "filebeat"],
            "detected": True
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check"""
        return {
            "status": "healthy",
            "platform": "mock",
            "timestamp": datetime.now().isoformat(),
            "indices_available": len(await self.get_indices()),
            "mock_data_active": True
        }
    
    def __str__(self) -> str:
        return f"MockSIEMConnector(name={self.name}, connected={self.connected})"
    
    def __repr__(self) -> str:
        return self.__str__()
