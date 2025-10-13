"""
Mock Elasticsearch Connector
Simulates a real Elasticsearch API for demo purposes with dynamic mock data
"""

import json
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict

from ..utils import MockDataScheduler, MockDataType
from ..generators import (WindowsEventGenerator, SystemMetricsGenerator, AuthenticationEventGenerator,
                                         AuditbeatEventGenerator, PacketbeatEventGenerator, FilebeatEventGenerator)


class MockElasticsearchConnector:
    """
    Mock Elasticsearch connector that behaves exactly like real Elasticsearch
    but serves dynamic mock data instead of real data
    """
    
    def __init__(self, host: str = "localhost", port: int = 9200):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        
        # Initialize data generators - ALL SECURITY BEATS!
        self.generators = [
            WindowsEventGenerator(),
            SystemMetricsGenerator(),
            AuthenticationEventGenerator(),
            AuditbeatEventGenerator(),
            PacketbeatEventGenerator(),
            FilebeatEventGenerator()
        ]
        
        # Initialize scheduler for continuous data generation
        self.scheduler = MockDataScheduler(self.generators, interval_seconds=3)
        
        # Mock indices with realistic names - ALL SECURITY BEATS!
        self.indices = {
            "winlogbeat-2025.10.12": {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": self._get_winlogbeat_mapping(),
                "aliases": {}
            },
            "metricbeat-2025.10.12": {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": self._get_metricbeat_mapping(),
                "aliases": {}
            },
            "auditbeat-2025.10.12": {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": self._get_auditbeat_mapping(),
                "aliases": {}
            },
            "packetbeat-2025.10.12": {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": self._get_packetbeat_mapping(),
                "aliases": {}
            },
            "filebeat-2025.10.12": {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": self._get_filebeat_mapping(),
                "aliases": {}
            },
            "security-logs-demo": {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": self._get_security_mapping(),
                "aliases": {}
            }
        }
        
        # Start background data generation
        self.scheduler.start()
        
        # Mock health status
        self.cluster_health = "green"
        
    async def connect(self) -> bool:
        """Simulate connection to Elasticsearch"""
        # Add small delay to simulate network
        await asyncio.sleep(random.uniform(0.01, 0.05))
        return True
    
    async def disconnect(self):
        """Simulate disconnection"""
        self.scheduler.stop()
        await asyncio.sleep(0.01)
    
    # Mock Elasticsearch API methods
    
    def info(self) -> Dict[str, Any]:
        """Mock cluster info"""
        return {
            "name": "mock-elasticsearch",
            "cluster_name": "mock-cluster",
            "cluster_uuid": "mock-uuid-12345",
            "version": {
                "number": "8.11.0",
                "build_flavor": "default",
                "build_type": "docker",
                "build_hash": "d9ec3fa628c7b0ba3d25692e277ba26814820b20",
                "build_date": "2023-11-04T10:04:57.184859352Z",
                "build_snapshot": False,
                "lucene_version": "9.8.0",
                "minimum_wire_compatibility_version": "7.17.0",
                "minimum_index_compatibility_version": "7.0.0"
            },
            "tagline": "You Know, for Mock Search"
        }
    
    class Cat:
        """Mock cat API"""
        def __init__(self, parent):
            self.parent = parent
        
        def indices(self, format: str = "json", h: str = None) -> List[Dict[str, Any]]:
            """Mock indices list"""
            if format == "json":
                return [\n                    {\n                        \"index\": name,\n                        \"health\": \"yellow\",\n                        \"status\": \"open\",\n                        \"pri\": \"1\",\n                        \"rep\": \"1\",\n                        \"docs.count\": str(random.randint(100, 10000)),\n                        \"docs.deleted\": \"0\",\n                        \"store.size\": f\"{random.randint(1, 100)}mb\",\n                        \"pri.store.size\": f\"{random.randint(1, 100)}mb\"\n                    }\n                    for name in self.parent.indices.keys()\n                ]\n            else:\n                # Plain text format\n                result = \"health status index                   uuid                   pri rep docs.count docs.deleted store.size pri.store.size\\n\"\n                for name in self.parent.indices.keys():\n                    result += f\"yellow open   {name:<25} mock-uuid-{name[:8]:<17} 1   1   {random.randint(100, 10000):<10} 0            {random.randint(1, 100)}mb        {random.randint(1, 100)}mb\\n\"\n                return result\n    \n    @property\n    def cat(self):\n        return self.Cat(self)\n    \n    class Indices:\n        \"\"\"Mock indices API\"\"\"\n        def __init__(self, parent):\n            self.parent = parent\n        \n        def get_mapping(self, index: str) -> Dict[str, Any]:\n            \"\"\"Mock index mapping\"\"\"\n            if index in self.parent.indices:\n                return {index: self.parent.indices[index]}\n            else:\n                raise Exception(f\"index_not_found_exception: no such index [{index}]\")\n        \n        def get_data_stream(self, name: str = \"*\") -> Dict[str, Any]:\n            \"\"\"Mock data streams\"\"\"\n            return {\n                \"data_streams\": [\n                    {\n                        \"name\": \"metricbeat-9.1.4\",\n                        \"timestamp_field\": \"@timestamp\",\n                        \"indices\": [\n                            {\n                                \"index_name\": \"metricbeat-9.1.4-2025.10.12-000001\",\n                                \"index_uuid\": \"mock-uuid-metricbeat\"\n                            }\n                        ],\n                        \"generation\": 1,\n                        \"status\": \"GREEN\",\n                        \"template\": \"metricbeat-9.1.4\"\n                    },\n                    {\n                        \"name\": \"winlogbeat-9.1.4\",\n                        \"timestamp_field\": \"@timestamp\",\n                        \"indices\": [\n                            {\n                                \"index_name\": \"winlogbeat-9.1.4-2025.10.12-000001\",\n                                \"index_uuid\": \"mock-uuid-winlogbeat\"\n                            }\n                        ],\n                        \"generation\": 1,\n                        \"status\": \"GREEN\",\n                        \"template\": \"winlogbeat-9.1.4\"\n                    }\n                ]\n            }\n        \n        def stats(self, index: str, metric: str = \"_all\") -> Dict[str, Any]:\n            \"\"\"Mock index statistics\"\"\"\n            return {\n                \"_all\": {\n                    \"primaries\": {\n                        \"docs\": {\n                            \"count\": random.randint(100, 10000),\n                            \"deleted\": 0\n                        }\n                    },\n                    \"total\": {\n                        \"docs\": {\n                            \"count\": random.randint(100, 10000),\n                            \"deleted\": 0\n                        }\n                    }\n                }\n            }\n    \n    @property\n    def indices(self):\n        return self.Indices(self)\n    \n    def search(self, index: str, body: Dict[str, Any], timeout: str = \"30s\") -> Dict[str, Any]:\n        \"\"\"Mock search functionality with realistic responses\"\"\"\n        \n        # Parse the query\n        size = body.get(\"size\", 10)\n        query = body.get(\"query\", {})\n        sort = body.get(\"sort\", [])\n        \n        # Get appropriate mock data based on index\n        mock_events = self._get_mock_data_for_index(index, size)\n        \n        # Convert mock events to Elasticsearch format\n        hits = []\n        for event in mock_events:\n            hit = {\n                \"_index\": index,\n                \"_type\": \"_doc\",\n                \"_id\": event.id,\n                \"_score\": random.uniform(0.5, 2.0),\n                \"_source\": event.data\n            }\n            hits.append(hit)\n        \n        # Sort hits if requested\n        if sort and \"@timestamp\" in str(sort):\n            reverse = \"desc\" in str(sort).lower()\n            hits.sort(key=lambda x: x[\"_source\"].get(\"@timestamp\", \"\"), reverse=reverse)\n        \n        # Build response\n        response = {\n            \"took\": random.randint(5, 50),\n            \"timed_out\": False,\n            \"_shards\": {\n                \"total\": 1,\n                \"successful\": 1,\n                \"skipped\": 0,\n                \"failed\": 0\n            },\n            \"hits\": {\n                \"total\": {\n                    \"value\": random.randint(size, size * 10),\n                    \"relation\": \"eq\"\n                },\n                \"max_score\": max([hit[\"_score\"] for hit in hits]) if hits else 0,\n                \"hits\": hits\n            }\n        }\n        \n        return response\n    \n    def _get_mock_data_for_index(self, index: str, limit: int) -> List[Any]:\n        \"\"\"Get appropriate mock data based on index name\"\"\"\n        \n        # Determine data type from index name\n        if \"winlog\" in index.lower() or \"security\" in index.lower():\n            data_types = [MockDataType.WINDOWS_EVENT, MockDataType.AUTHENTICATION]\n        elif \"metric\" in index.lower():\n            data_types = [MockDataType.SYSTEM_METRIC]\n        else:\n            data_types = [MockDataType.WINDOWS_EVENT, MockDataType.SYSTEM_METRIC, MockDataType.AUTHENTICATION]\n        \n        # Get latest data from scheduler\n        all_events = []\n        for data_type in data_types:\n            events = self.scheduler.get_latest_data(data_type, limit)\n            all_events.extend(events)\n        \n        # If no data available, generate some on the fly\n        if not all_events:\n            generator = random.choice(self.generators)\n            all_events = generator.generate_batch(limit)\n        \n        # Return requested number of events\n        return all_events[:limit]\n    \n    def _get_winlogbeat_mapping(self) -> Dict[str, Any]:\n        \"\"\"Mock Winlogbeat field mapping\"\"\"\n        return {\n            \"properties\": {\n                \"@timestamp\": {\"type\": \"date\"},\n                \"winlog\": {\n                    \"properties\": {\n                        \"event_id\": {\"type\": \"long\"},\n                        \"channel\": {\"type\": \"keyword\"},\n                        \"computer_name\": {\"type\": \"keyword\"},\n                        \"event_data\": {\"type\": \"object\"}\n                    }\n                },\n                \"event\": {\n                    \"properties\": {\n                        \"category\": {\"type\": \"keyword\"},\n                        \"code\": {\"type\": \"long\"},\n                        \"action\": {\"type\": \"keyword\"},\n                        \"outcome\": {\"type\": \"keyword\"}\n                    }\n                },\n                \"host\": {\n                    \"properties\": {\n                        \"hostname\": {\"type\": \"keyword\"},\n                        \"ip\": {\"type\": \"ip\"},\n                        \"os\": {\n                            \"properties\": {\n                                \"name\": {\"type\": \"keyword\"},\n                                \"family\": {\"type\": \"keyword\"},\n                                \"version\": {\"type\": \"keyword\"}\n                            }\n                        }\n                    }\n                },\n                \"user\": {\n                    \"properties\": {\n                        \"name\": {\"type\": \"keyword\"},\n                        \"domain\": {\"type\": \"keyword\"}\n                    }\n                },\n                \"source\": {\n                    \"properties\": {\n                        \"ip\": {\"type\": \"ip\"},\n                        \"port\": {\"type\": \"long\"}\n                    }\n                }\n            }\n        }\n    \n    def _get_metricbeat_mapping(self) -> Dict[str, Any]:\n        \"\"\"Mock Metricbeat field mapping\"\"\"\n        return {\n            \"properties\": {\n                \"@timestamp\": {\"type\": \"date\"},\n                \"system\": {\n                    \"properties\": {\n                        \"cpu\": {\n                            \"properties\": {\n                                \"total\": {\"properties\": {\"pct\": {\"type\": \"float\"}}},\n                                \"user\": {\"properties\": {\"pct\": {\"type\": \"float\"}}},\n                                \"system\": {\"properties\": {\"pct\": {\"type\": \"float\"}}}\n                            }\n                        },\n                        \"memory\": {\n                            \"properties\": {\n                                \"total\": {\"type\": \"long\"},\n                                \"used\": {\n                                    \"properties\": {\n                                        \"bytes\": {\"type\": \"long\"},\n                                        \"pct\": {\"type\": \"float\"}\n                                    }\n                                }\n                            }\n                        },\n                        \"filesystem\": {\n                            \"properties\": {\n                                \"total\": {\"type\": \"long\"},\n                                \"used\": {\n                                    \"properties\": {\n                                        \"bytes\": {\"type\": \"long\"},\n                                        \"pct\": {\"type\": \"float\"}\n                                    }\n                                }\n                            }\n                        }\n                    }\n                },\n                \"host\": {\n                    \"properties\": {\n                        \"hostname\": {\"type\": \"keyword\"},\n                        \"ip\": {\"type\": \"ip\"},\n                        \"os\": {\n                            \"properties\": {\n                                \"name\": {\"type\": \"keyword\"},\n                                \"family\": {\"type\": \"keyword\"}\n                            }\n                        }\n                    }\n                },\n                \"agent\": {\n                    \"properties\": {\n                        \"type\": {\"type\": \"keyword\"},\n                        \"version\": {\"type\": \"keyword\"}\n                    }\n                }\n            }\n        }\n    \n    def _get_security_mapping(self) -> Dict[str, Any]:\n        \"\"\"Mock security logs mapping\"\"\"\n        return {\n            \"properties\": {\n                \"@timestamp\": {\"type\": \"date\"},\n                \"event\": {\n                    \"properties\": {\n                        \"category\": {\"type\": \"keyword\"},\n                        \"type\": {\"type\": \"keyword\"},\n                        \"outcome\": {\"type\": \"keyword\"},\n                        \"action\": {\"type\": \"text\"}\n                    }\n                },\n                \"user\": {\n                    \"properties\": {\n                        \"name\": {\"type\": \"keyword\"},\n                        \"domain\": {\"type\": \"keyword\"}\n                    }\n                },\n                \"source\": {\n                    \"properties\": {\n                        \"ip\": {\"type\": \"ip\"},\n                        \"port\": {\"type\": \"long\"},\n                        \"geo\": {\n                            \"properties\": {\n                                \"country_iso_code\": {\"type\": \"keyword\"},\n                                \"city_name\": {\"type\": \"keyword\"},\n                                \"location\": {\"type\": \"geo_point\"}\n                            }\n                        }\n                    }\n                },\n                \"authentication\": {\n                    \"properties\": {\n                        \"method\": {\"type\": \"keyword\"},\n                        \"protocol\": {\"type\": \"keyword\"},\n                        \"success\": {\"type\": \"boolean\"}\n                    }\n                }\n            }\n        }