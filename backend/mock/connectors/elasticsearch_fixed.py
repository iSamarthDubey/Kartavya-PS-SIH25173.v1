"""
Mock Elasticsearch Connector - Fixed Version
Simulates a real Elasticsearch API for demo purposes with dynamic mock data
"""

import json
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from ..utils import MockDataScheduler, MockDataType
from ..generators import (
    WindowsEventGenerator, 
    SystemMetricsGenerator, 
    AuthenticationEventGenerator,
    AuditbeatEventGenerator,
    PacketbeatEventGenerator,
    FilebeatEventGenerator,
    NetworkLogsGenerator,
    SecurityAlertsGenerator,
    ProcessLogsGenerator
)


class MockElasticsearchConnector:
    """Mock Elasticsearch connector that behaves exactly like real Elasticsearch"""
    
    def __init__(self, host: str = "localhost", port: int = 9200):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        
        # Initialize data generators - comprehensive security coverage
        self.generators = [
            WindowsEventGenerator(),
            SystemMetricsGenerator(),
            AuthenticationEventGenerator(),
            AuditbeatEventGenerator(),
            PacketbeatEventGenerator(),
            FilebeatEventGenerator(),
            NetworkLogsGenerator(),
            SecurityAlertsGenerator(),
            ProcessLogsGenerator()
        ]
        
        # Initialize scheduler for continuous data generation
        self.scheduler = MockDataScheduler(self.generators, interval_seconds=3)
        
        # Mock indices with realistic names for comprehensive security data
        self.mock_indices = {
            "winlogbeat-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "metricbeat-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "auditbeat-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "packetbeat-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "filebeat-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "network-logs-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "security-alerts-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "process-logs-2025.10.13": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}},
            "security-logs-demo": {"settings": {"number_of_shards": 1, "number_of_replicas": 1}}
        }
        
        # Start background data generation
        self.scheduler.start()
        
    async def connect(self) -> bool:
        """Simulate connection to Elasticsearch"""
        await asyncio.sleep(random.uniform(0.01, 0.05))
        return True
    
    async def disconnect(self):
        """Simulate disconnection"""
        self.scheduler.stop()
        await asyncio.sleep(0.01)
    
    def info(self) -> Dict[str, Any]:
        """Mock cluster info"""
        return {
            "name": "mock-elasticsearch",
            "cluster_name": "mock-cluster",
            "cluster_uuid": "mock-uuid-12345",
            "version": {
                "number": "8.11.0",
                "build_flavor": "default",
                "build_type": "docker"
            },
            "tagline": "You Know, for Mock Search"
        }
    
    class Cat:
        """Mock cat API"""
        def __init__(self, parent):
            self.parent = parent
        
        def indices(self, format: str = "json", h: str = None):
            """Mock indices list"""
            if format == "json":
                return [
                    {
                        "index": name,
                        "health": "yellow",
                        "status": "open",
                        "pri": "1",
                        "rep": "1",
                        "docs.count": str(random.randint(100, 10000)),
                        "docs.deleted": "0",
                        "store.size": f"{random.randint(1, 100)}mb",
                        "pri.store.size": f"{random.randint(1, 100)}mb"
                    }
                    for name in self.parent.mock_indices.keys()
                ]
    
    @property
    def cat(self):
        return self.Cat(self)
    
    def search(self, index: str, body: Dict[str, Any], timeout: str = "30s") -> Dict[str, Any]:
        """Mock search functionality with realistic responses"""
        
        # Parse the query
        size = body.get("size", 10)
        
        # Get appropriate mock data based on index
        mock_events = self._get_mock_data_for_index(index, size)
        
        # Convert mock events to Elasticsearch format
        hits = []
        for event in mock_events:
            hit = {
                "_index": index,
                "_type": "_doc",
                "_id": event.id,
                "_score": random.uniform(0.5, 2.0),
                "_source": event.data
            }
            hits.append(hit)
        
        # Build response
        response = {
            "took": random.randint(5, 50),
            "timed_out": False,
            "_shards": {
                "total": 1,
                "successful": 1,
                "skipped": 0,
                "failed": 0
            },
            "hits": {
                "total": {
                    "value": random.randint(size, size * 10),
                    "relation": "eq"
                },
                "max_score": max([hit["_score"] for hit in hits]) if hits else 0,
                "hits": hits
            }
        }
        
        return response
    
    def _get_mock_data_for_index(self, index: str, limit: int) -> List[Any]:
        """Get appropriate mock data based on index name"""
        
        # Determine data type from index name
        if "winlog" in index.lower():
            data_types = [MockDataType.WINDOWS_EVENT, MockDataType.AUTHENTICATION]
        elif "metric" in index.lower():
            data_types = [MockDataType.SYSTEM_METRIC]
        elif "audit" in index.lower():
            data_types = [MockDataType.AUDITBEAT_EVENT]
        elif "packet" in index.lower():
            data_types = [MockDataType.PACKETBEAT_EVENT]
        elif "filebeat" in index.lower():
            data_types = [MockDataType.FILEBEAT_EVENT]
        elif "network-logs" in index.lower():
            data_types = [MockDataType.NETWORK_LOG]
        elif "security-alerts" in index.lower():
            data_types = [MockDataType.SECURITY_ALERT]
        elif "process-logs" in index.lower():
            data_types = [MockDataType.PROCESS_LOG]
        elif "security" in index.lower():
            # Mixed comprehensive security data for demo index
            data_types = [MockDataType.WINDOWS_EVENT, MockDataType.AUTHENTICATION, 
                         MockDataType.AUDITBEAT_EVENT, MockDataType.PACKETBEAT_EVENT, MockDataType.FILEBEAT_EVENT,
                         MockDataType.NETWORK_LOG, MockDataType.SECURITY_ALERT, MockDataType.PROCESS_LOG]
        else:
            # Default: all available event types for comprehensive coverage
            data_types = [MockDataType.WINDOWS_EVENT, MockDataType.SYSTEM_METRIC, MockDataType.AUTHENTICATION,
                         MockDataType.AUDITBEAT_EVENT, MockDataType.PACKETBEAT_EVENT, MockDataType.FILEBEAT_EVENT,
                         MockDataType.NETWORK_LOG, MockDataType.SECURITY_ALERT, MockDataType.PROCESS_LOG]
        
        # Get latest data from scheduler
        all_events = []
        for data_type in data_types:
            events = self.scheduler.get_latest_data(data_type, limit // len(data_types) + 1)
            all_events.extend(events)
        
        # If no data available, generate some on the fly
        if not all_events:
            generator = random.choice(self.generators)
            all_events = generator.generate_batch(limit)
        
        # Shuffle to mix event types and return requested number
        random.shuffle(all_events)
        return all_events[:limit]
