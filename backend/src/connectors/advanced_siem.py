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
    MOCK = "mock"


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
        self.platform = SiemPlatform(config.get('platform', 'mock'))
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
            elif self.platform == SiemPlatform.MOCK:
                logger.info("✅ Mock SIEM initialized")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize SIEM connector: {e}")
            return False
    
    async def _init_elasticsearch(self) -> None:
        """Initialize Elasticsearch connection"""
        es_config = self.config.get('elasticsearch', {})
        
        if self.is_demo:
            # Demo mode - use mock Elasticsearch or public instance
            logger.info("🎭 Demo mode - using mock Elasticsearch responses")
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
            logger.info("🎭 Demo mode - using mock Wazuh responses")
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
            if self.is_demo or self.platform == SiemPlatform.MOCK:
                result = await self._execute_mock_query(query)
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
    
    async def _execute_mock_query(self, query: SiemQuery) -> SiemResult:
        """Execute mock query for demo purposes"""
        await asyncio.sleep(0.1)  # Simulate network latency
        
        # Generate mock data based on query filters
        mock_events = self._generate_mock_events(query)
        
        return SiemResult(
            total_hits=len(mock_events),
            events=mock_events,
            aggregations=self._generate_mock_aggregations(query) if query.aggregations else None
        )
    
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
    
    def _generate_mock_events(self, query: SiemQuery) -> List[Dict[str, Any]]:
        """Generate realistic mock events for demo"""
        import random
        
        # Base event templates
        event_templates = [
            {
                "@timestamp": None,  # Will be set dynamically
                "event.type": "authentication_failure",
                "event.category": "authentication",
                "source.ip": "192.168.1.{ip}",
                "user.name": "admin",
                "host.name": "WS-SEC-{host}",
                "message": "Failed login attempt for user {user}",
                "event.severity": "high"
            },
            {
                "@timestamp": None,
                "event.type": "malware_detection", 
                "event.category": "malware",
                "source.ip": "10.0.0.{ip}",
                "file.name": "suspicious_{file}.exe",
                "host.name": "SRV-DB-{host}",
                "message": "Malware signature match: {malware_type}",
                "event.severity": "critical"
            },
            {
                "@timestamp": None,
                "event.type": "network_connection",
                "event.category": "network", 
                "source.ip": "203.45.12.{ip}",
                "destination.ip": "192.168.1.{dest_ip}",
                "source.port": random.randint(1024, 65535),
                "destination.port": 443,
                "network.protocol": "https",
                "message": "Suspicious outbound connection",
                "event.severity": "medium"
            }
        ]
        
        events = []
        num_events = min(query.size, random.randint(10, 100))
        
        for i in range(num_events):
            template = random.choice(event_templates).copy()
            
            # Generate timestamp within query range
            if query.time_range and query.time_range.get('gte'):
                start_time = datetime.fromisoformat(query.time_range['gte'].replace('Z', '+00:00'))
            else:
                start_time = datetime.now() - timedelta(hours=24)
            
            if query.time_range and query.time_range.get('lte'):
                end_time = datetime.fromisoformat(query.time_range['lte'].replace('Z', '+00:00'))
            else:
                end_time = datetime.now()
            
            # Random timestamp between start and end
            time_diff = end_time - start_time
            random_seconds = random.randint(0, int(time_diff.total_seconds()))
            event_time = start_time + timedelta(seconds=random_seconds)
            
            template["@timestamp"] = event_time.isoformat() + 'Z'
            
            # Fill template variables
            replacements = {
                'ip': random.randint(1, 254),
                'dest_ip': random.randint(1, 254),
                'host': random.randint(1, 50),
                'user': random.choice(['admin', 'service', 'backup', 'guest']),
                'file': random.choice(['update', 'install', 'backup', 'temp']),
                'malware_type': random.choice(['Trojan.Generic', 'Backdoor.Agent', 'Virus.Win32'])
            }
            
            # Apply replacements
            for key, value in template.items():
                if isinstance(value, str) and '{' in value:
                    for placeholder, replacement in replacements.items():
                        value = value.replace(f'{{{placeholder}}}', str(replacement))
                    template[key] = value
            
            events.append(template)
        
        return events
    
    def _generate_mock_aggregations(self, query: SiemQuery) -> Dict[str, Any]:
        """Generate mock aggregations for demo"""
        import random
        
        if not query.aggregations:
            return {}
        
        mock_aggs = {}
        
        for agg_name, agg_config in query.aggregations.items():
            if 'terms' in agg_config:
                # Terms aggregation
                field = agg_config['terms']['field']
                mock_aggs[agg_name] = {
                    "buckets": [
                        {"key": f"value_{i}", "doc_count": random.randint(1, 100)}
                        for i in range(1, 6)
                    ]
                }
            elif 'date_histogram' in agg_config:
                # Date histogram
                mock_aggs[agg_name] = {
                    "buckets": [
                        {
                            "key_as_string": f"2025-01-08T{i:02d}:00:00.000Z",
                            "key": 1641600000000 + (i * 3600000),
                            "doc_count": random.randint(0, 50)
                        }
                        for i in range(24)
                    ]
                }
            elif 'cardinality' in agg_config:
                # Cardinality aggregation
                mock_aggs[agg_name] = {
                    "value": random.randint(10, 1000)
                }
        
        return mock_aggs
    
    async def get_indices(self) -> List[str]:
        """Get list of available indices"""
        if self.is_demo:
            return list(self.index_mappings.keys())
        
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
        if self.is_demo:
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
        if self.is_demo:
            events = self._generate_mock_events(query)
            for event in events:
                yield event
                await asyncio.sleep(0.01)  # Simulate streaming delay
        
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
            'platform': 'mock'
        }
        
        connector = create_siem_connector('mock', config)
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
