#!/usr/bin/env python3
"""
Advanced SIEM Connector - Production-ready Elasticsearch & Wazuh Integration
Supports both demo (mock data) and production (live SIEM) modes
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_scan, async_bulk

logger = logging.getLogger(__name__)


class SiemPlatform(Enum):
    """Supported SIEM platforms"""
    ELASTICSEARCH = "elasticsearch"
    WAZUH = "wazuh"
    DATASET = "dataset"


class QueryType(Enum):
    """SIEM query types"""
    SEARCH = "search"
    AGGREGATION = "aggregation"
    COUNT = "count"
    SCROLL = "scroll"


@dataclass
class SiemQuery:
    """Structured SIEM query representation"""
    query_type: QueryType
    index_pattern: str
    time_range: Dict[str, Any]
    filters: List[Dict[str, Any]]
    aggregations: Optional[Dict[str, Any]] = None
    size: int = 1000
    sort: Optional[List[Dict[str, Any]]] = None
    fields: Optional[List[str]] = None
    raw_query: Optional[Dict[str, Any]] = None


@dataclass
class SiemResult:
    """SIEM query result container"""
    total_hits: int
    events: List[Dict[str, Any]]
    aggregations: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    query_hash: Optional[str] = None
    platform: Optional[str] = None
    index: Optional[str] = None


class AdvancedSiemConnector:
    """
    Advanced SIEM connector with support for multiple platforms
    Handles both demo and production modes seamlessly
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SIEM connector with configuration"""
        self.config = config
        self.platform = SiemPlatform(config.get('platform', 'dataset'))
        self.is_demo = config.get('is_demo', True)
        
        # Connection instances
        self.es_client: Optional[AsyncElasticsearch] = None
        self.wazuh_session: Optional[aiohttp.ClientSession] = None
        
        # Index mappings for different log types
        self.index_mappings = self._load_index_mappings()
        
        logger.info(f"🎯 SIEM Connector initialized - Platform: {self.platform.value}, Demo: {self.is_demo}")
    
    async def initialize(self) -> bool:
        """Initialize connections to SIEM platforms"""
        try:
            if self.platform == SiemPlatform.ELASTICSEARCH:
                await self._init_elasticsearch()
            elif self.platform == SiemPlatform.WAZUH:
                await self._init_wazuh()
            elif self.platform == SiemPlatform.DATASET:
                logger.info("✅ Dataset SIEM connector initialized")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize SIEM connector: {e}")
            return False
    
    async def _init_elasticsearch(self) -> None:
        """Initialize Elasticsearch connection"""
        es_config = self.config.get('elasticsearch', {})
        
        if self.is_demo:
            # Demo mode - use dataset connector instead of direct Elasticsearch
            logger.info("🎭 Demo mode - will use dataset connector for queries")
            return
        
        # Production mode - real Elasticsearch
        try:
            self.es_client = AsyncElasticsearch(
                [es_config.get('host', 'localhost:9200')],
                http_auth=(
                    es_config.get('username', 'elastic'),
                    es_config.get('password', '')
                ) if es_config.get('password') else None,
                verify_certs=es_config.get('verify_certs', True),
                ca_certs=es_config.get('ca_certs'),
                timeout=es_config.get('timeout', 30)
            )
            
            # Test connection
            info = await self.es_client.info()
            logger.info(f"✅ Elasticsearch connected - Version: {info['version']['number']}")
            
        except Exception as e:
            logger.error(f"❌ Elasticsearch connection failed: {e}")
            raise
    
    async def _init_wazuh(self) -> None:
        """Initialize Wazuh connection"""
        wazuh_config = self.config.get('wazuh', {})
        
        if self.is_demo:
            logger.info("🎭 Demo mode - will use dataset connector for queries")
            return
        
        # Production mode - real Wazuh API
        try:
            self.wazuh_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'Content-Type': 'application/json'}
            )
            
            # Authenticate with Wazuh API
            auth_url = f"{wazuh_config['url']}/security/user/authenticate"
            auth_data = {
                'user': wazuh_config.get('username', 'wazuh'),
                'password': wazuh_config.get('password', '')
            }
            
            async with self.wazuh_session.post(auth_url, json=auth_data) as resp:
                if resp.status == 200:
                    token = (await resp.json())['data']['token']
                    self.wazuh_session.headers.update({'Authorization': f'Bearer {token}'})
                    logger.info("✅ Wazuh API authenticated")
                else:
                    raise Exception(f"Wazuh authentication failed: {resp.status}")
                    
        except Exception as e:
            logger.error(f"❌ Wazuh connection failed: {e}")
            raise
    
    def _load_index_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load index mappings for different log types"""
        return {
            "security-logs": {
                "pattern": "security-logs-*",
                "fields": {
                    "@timestamp": "date",
                    "event.type": "keyword", 
                    "event.category": "keyword",
                    "source.ip": "ip",
                    "destination.ip": "ip",
                    "user.name": "keyword",
                    "host.name": "keyword",
                    "process.name": "keyword",
                    "message": "text"
                }
            },
            "network-logs": {
                "pattern": "network-logs-*", 
                "fields": {
                    "@timestamp": "date",
                    "source.ip": "ip",
                    "destination.ip": "ip",
                    "source.port": "integer",
                    "destination.port": "integer",
                    "network.protocol": "keyword",
                    "network.bytes": "long"
                }
            },
            "auth-logs": {
                "pattern": "auth-logs-*",
                "fields": {
                    "@timestamp": "date",
                    "user.name": "keyword",
                    "source.ip": "ip",
                    "event.outcome": "keyword",
                    "user_agent.original": "text"
                }
            }
        }
    
    async def execute_query(self, query: SiemQuery) -> SiemResult:
        """Execute SIEM query and return results"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if self.is_demo or self.platform == SiemPlatform.DATASET:
                # For demo mode or dataset platform, use dataset connector
                from .dataset_connector import DatasetConnector
                dataset_connector = DatasetConnector()
                await dataset_connector.connect()
                
                # Convert SIEM-Query to dataset query format
                dataset_query = self._convert_to_dataset_query(query)
                dataset_result = await dataset_connector.execute_query(dataset_query, size=query.size)
                
                # Convert back to SiemResult
                events = [hit['_source'] for hit in dataset_result['hits']['hits']]
                result = SiemResult(
                    total_hits=dataset_result['hits']['total']['value'],
                    events=events,
                    platform="dataset"
                )
            elif self.platform == SiemPlatform.ELASTICSEARCH:
                result = await self._execute_elasticsearch_query(query)
            elif self.platform == SiemPlatform.WAZUH:
                result = await self._execute_wazuh_query(query)
            else:
                raise ValueError(f"Unsupported platform: {self.platform}")
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            result.execution_time_ms = execution_time
            result.platform = self.platform.value
            
            logger.info(f"📊 Query executed - Platform: {self.platform.value}, "
                       f"Results: {result.total_hits}, Time: {execution_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise
    
    def _convert_to_dataset_query(self, siem_query: SiemQuery) -> Dict[str, Any]:
        """Convert SiemQuery to dataset connector query format"""
        query = {"query": {}}
        
        if siem_query.filters:
            bool_query = {"bool": {"must": [], "filter": []}}
            
            for filter_clause in siem_query.filters:
                if 'match' in filter_clause:
                    bool_query["bool"]["must"].append(filter_clause)
                elif 'term' in filter_clause or 'terms' in filter_clause:
                    bool_query["bool"]["filter"].append(filter_clause)
            
            if bool_query["bool"]["must"] or bool_query["bool"]["filter"]:
                query["query"] = bool_query
        
        # Add time range if specified
        if siem_query.time_range:
            if "query" not in query:
                query["query"] = {"bool": {"filter": []}}
            elif "bool" not in query["query"]:
                query["query"] = {"bool": {"filter": []}}
            
            query["query"]["bool"]["filter"].append({
                "range": {
                    "@timestamp": siem_query.time_range
                }
            })
        
        return query
    
    async def _execute_elasticsearch_query(self, query: SiemQuery) -> SiemResult:
        """Execute Elasticsearch query"""
        if not self.es_client:
            raise RuntimeError("Elasticsearch client not initialized")
        
        # Build Elasticsearch DSL query
        es_query = self._build_elasticsearch_dsl(query)
        
        try:
            response = await self.es_client.search(
                index=query.index_pattern,
                body=es_query,
                size=query.size
            )
            
            # Parse results
            events = [hit['_source'] for hit in response['hits']['hits']]
            
            return SiemResult(
                total_hits=response['hits']['total']['value'],
                events=events,
                aggregations=response.get('aggregations'),
                index=query.index_pattern
            )
            
        except Exception as e:
            logger.error(f"❌ Elasticsearch query failed: {e}")
            raise
    
    async def _execute_wazuh_query(self, query: SiemQuery) -> SiemResult:
        """Execute Wazuh API query"""
        if not self.wazuh_session:
            raise RuntimeError("Wazuh session not initialized")
        
        # Convert to Wazuh API parameters
        wazuh_params = self._build_wazuh_params(query)
        
        try:
            url = f"{self.config['wazuh']['url']}/events"
            
            async with self.wazuh_session.get(url, params=wazuh_params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    return SiemResult(
                        total_hits=data.get('data', {}).get('total_affected_items', 0),
                        events=data.get('data', {}).get('affected_items', [])
                    )
                else:
                    raise Exception(f"Wazuh API error: {resp.status}")
                    
        except Exception as e:
            logger.error(f"❌ Wazuh query failed: {e}")
            raise
    
    def _build_elasticsearch_dsl(self, query: SiemQuery) -> Dict[str, Any]:
        """Build Elasticsearch DSL query from SiemQuery"""
        if query.raw_query:
            return query.raw_query
        
        dsl = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            }
        }
        
        # Add time range filter
        if query.time_range:
            dsl["query"]["bool"]["filter"].append({
                "range": {
                    "@timestamp": query.time_range
                }
            })
        
        # Add filters
        for filter_clause in query.filters:
            if filter_clause.get('term'):
                dsl["query"]["bool"]["filter"].append(filter_clause)
            elif filter_clause.get('match'):
                dsl["query"]["bool"]["must"].append(filter_clause)
            elif filter_clause.get('wildcard'):
                dsl["query"]["bool"]["must"].append(filter_clause)
        
        # Add aggregations
        if query.aggregations:
            dsl["aggs"] = query.aggregations
        
        # Add sorting
        if query.sort:
            dsl["sort"] = query.sort
        
        # Add field selection
        if query.fields:
            dsl["_source"] = query.fields
        
        return dsl
    
    def _build_wazuh_params(self, query: SiemQuery) -> Dict[str, Any]:
        """Build Wazuh API parameters from SiemQuery"""
        params = {
            "limit": query.size,
            "offset": 0
        }
        
        # Add time range
        if query.time_range:
            if query.time_range.get('gte'):
                params['timestamp'] = f">={query.time_range['gte']}"
            if query.time_range.get('lte'):
                params['timestamp'] += f",<={query.time_range['lte']}"
        
        # Add search filters
        search_terms = []
        for filter_clause in query.filters:
            if 'match' in filter_clause:
                for field, value in filter_clause['match'].items():
                    search_terms.append(f"{field}:{value}")
        
        if search_terms:
            params['search'] = ' AND '.join(search_terms)
        
        return params
    
    
    async def get_indices(self) -> List[str]:
        """Get list of available indices"""
        if self.is_demo or self.platform == SiemPlatform.DATASET:
            # Return available dataset index patterns
            return ["security-logs", "network-logs", "auth-logs", "system-logs"]
        
        if self.platform == SiemPlatform.ELASTICSEARCH and self.es_client:
            try:
                response = await self.es_client.indices.get('*')
                return list(response.keys())
            except Exception as e:
                logger.error(f"❌ Failed to get indices: {e}")
                return []
        
        return []
    
    async def get_field_mappings(self, index: str) -> Dict[str, Any]:
        """Get field mappings for an index"""
        if self.is_demo or self.platform == SiemPlatform.DATASET:
            return self.index_mappings.get(index, {}).get('fields', {})
        
        if self.platform == SiemPlatform.ELASTICSEARCH and self.es_client:
            try:
                response = await self.es_client.indices.get_mapping(index=index)
                # Extract field mappings from response
                mappings = {}
                for idx, mapping in response.items():
                    if 'mappings' in mapping:
                        properties = mapping['mappings'].get('properties', {})
                        for field, field_mapping in properties.items():
                            mappings[field] = field_mapping.get('type', 'unknown')
                return mappings
            except Exception as e:
                logger.error(f"❌ Failed to get field mappings: {e}")
                return {}
        
        return {}
    
    async def stream_events(self, query: SiemQuery) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream events for large result sets"""
        if self.is_demo or self.platform == SiemPlatform.DATASET:
            # Use dataset connector for streaming
            from .dataset_connector import DatasetConnector
            dataset_connector = DatasetConnector()
            await dataset_connector.connect()
            
            dataset_query = self._convert_to_dataset_query(query)
            dataset_result = await dataset_connector.execute_query(dataset_query, size=query.size or 1000)
            
            for hit in dataset_result['hits']['hits']:
                yield hit['_source']
                await asyncio.sleep(0.01)  # Simulate realistic streaming delay
        
        elif self.platform == SiemPlatform.ELASTICSEARCH and self.es_client:
            es_query = self._build_elasticsearch_dsl(query)
            
            async for doc in async_scan(
                self.es_client,
                query=es_query,
                index=query.index_pattern,
                scroll='5m',
                size=1000
            ):
                yield doc['_source']
    
    async def close(self):
        """Close all connections"""
        try:
            if self.es_client:
                await self.es_client.close()
                logger.info("✅ Elasticsearch connection closed")
            
            if self.wazuh_session:
                await self.wazuh_session.close()
                logger.info("✅ Wazuh session closed")
                
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")


# Factory function for creating SIEM connectors
def create_siem_connector(platform: str, config: Dict[str, Any]) -> AdvancedSiemConnector:
    """Factory function to create SIEM connector instances"""
    connector_config = {
        'platform': platform,
        'is_demo': config.get('is_demo', True),
        **config
    }
    
    return AdvancedSiemConnector(connector_config)


# Utility functions for query building
def build_time_range(period: str) -> Dict[str, str]:
    """Build time range filter for common periods"""
    now = datetime.utcnow()
    
    ranges = {
        '1h': now - timedelta(hours=1),
        '24h': now - timedelta(hours=24), 
        '7d': now - timedelta(days=7),
        '30d': now - timedelta(days=30)
    }
    
    start_time = ranges.get(period, now - timedelta(hours=1))
    
    return {
        'gte': start_time.isoformat() + 'Z',
        'lte': now.isoformat() + 'Z'
    }


def build_security_query(
    query_type: str,
    time_range: str = '24h',
    severity: Optional[List[str]] = None,
    event_types: Optional[List[str]] = None,
    source_ips: Optional[List[str]] = None
) -> SiemQuery:
    """Build common security queries"""
    
    filters = []
    
    # Add severity filter
    if severity:
        filters.append({
            "terms": {"event.severity": severity}
        })
    
    # Add event type filter
    if event_types:
        filters.append({
            "terms": {"event.type": event_types}
        })
    
    # Add source IP filter
    if source_ips:
        filters.append({
            "terms": {"source.ip": source_ips}
        })
    
    return SiemQuery(
        query_type=QueryType.SEARCH,
        index_pattern="security-logs-*",
        time_range=build_time_range(time_range),
        filters=filters,
        sort=[{"@timestamp": {"order": "desc"}}]
    )


if __name__ == "__main__":
    # Demo usage
    async def demo():
        config = {
            'is_demo': True,
            'platform': 'dataset'
        }
        
        connector = create_siem_connector('dataset', config)
        await connector.initialize()
        
        # Test query
        query = build_security_query(
            'authentication_failures',
            time_range='24h',
            severity=['high', 'critical']
        )
        
        result = await connector.execute_query(query)
        print(f"📊 Found {result.total_hits} events in {result.execution_time_ms:.2f}ms")
        
        for event in result.events[:3]:
            print(f"  - {event['@timestamp']}: {event['message']}")
        
        await connector.close()
    
    import asyncio
    asyncio.run(demo())
