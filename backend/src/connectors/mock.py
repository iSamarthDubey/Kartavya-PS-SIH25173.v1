"""
Mock SIEM Connector
Provides realistic mock data for testing and demos
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from .base import BaseSIEMConnector

logger = logging.getLogger(__name__)

class MockConnector(BaseSIEMConnector):
    """Mock SIEM connector for testing and demos"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connected = True
        self.mock_data = self._generate_mock_data()
        
    def _generate_mock_data(self) -> List[Dict[str, Any]]:
        """Generate realistic mock security events"""
        events = []
        now = datetime.now()
        
        # Failed login attempts
        for i in range(50):
            events.append({
                "@timestamp": (now - timedelta(hours=random.randint(0, 72))).isoformat(),
                "event": {
                    "action": "authentication_failure",
                    "category": "authentication",
                    "outcome": "failure",
                    "severity": random.choice(["low", "medium", "high"])
                },
                "source": {
                    "ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    "user": {"name": random.choice(["admin", "user1", "john.doe", "alice", "bob"])}
                },
                "destination": {
                    "ip": "10.0.0.1",
                    "port": 22
                },
                "host": {"name": f"server-{random.randint(1, 10)}"},
                "message": "Failed SSH login attempt"
            })
        
        # Malware detections
        for i in range(20):
            events.append({
                "@timestamp": (now - timedelta(hours=random.randint(0, 48))).isoformat(),
                "event": {
                    "action": "malware_detected",
                    "category": "malware",
                    "outcome": "detected",
                    "severity": "critical"
                },
                "threat": {
                    "indicator": {
                        "name": random.choice(["Trojan.Generic", "Ransomware.Lockbit", "Backdoor.IRC"]),
                        "type": "malware"
                    }
                },
                "host": {"name": f"workstation-{random.randint(1, 20)}"},
                "file": {
                    "path": f"C:\\Users\\user\\Downloads\\{random.choice(['file', 'document', 'app'])}.exe",
                    "hash": {"sha256": f"{''.join(random.choices('0123456789abcdef', k=64))}"}
                },
                "message": "Malware detected and quarantined"
            })
        
        # VPN connections
        for i in range(30):
            events.append({
                "@timestamp": (now - timedelta(hours=random.randint(0, 24))).isoformat(),
                "event": {
                    "action": "vpn_connection",
                    "category": "network",
                    "outcome": "success",
                    "severity": "info"
                },
                "service": {"name": "vpn"},
                "network": {"protocol": "vpn"},
                "source": {
                    "ip": f"{random.choice(['8.8.8.8', '1.1.1.1', '203.0.113.1'])}",
                    "user": {"name": random.choice(["remote_user1", "contractor", "admin"])}
                },
                "message": "VPN connection established"
            })
        
        # Network anomalies
        for i in range(15):
            events.append({
                "@timestamp": (now - timedelta(hours=random.randint(0, 12))).isoformat(),
                "event": {
                    "action": "network_anomaly",
                    "category": "network",
                    "severity": "high"
                },
                "network": {
                    "bytes": random.randint(1000000, 100000000),
                    "packets": random.randint(1000, 100000)
                },
                "source": {"ip": f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"},
                "destination": {"ip": f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(0, 255)}"},
                "message": "Unusual network traffic detected"
            })
        
        return events
    
    async def connect(self) -> bool:
        """Simulate connection"""
        await asyncio.sleep(0.1)  # Simulate connection delay
        self.connected = True
        logger.info("Mock SIEM connector connected")
        return True
    
    async def disconnect(self) -> None:
        """Simulate disconnection"""
        self.connected = False
        logger.info("Mock SIEM connector disconnected")
    
    async def execute_query(
        self,
        query: Dict[str, Any],
        size: int = 100,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute mock query and return filtered results"""
        await asyncio.sleep(0.2)  # Simulate query delay
        
        # Filter mock data based on query
        filtered_events = self._filter_events(query, self.mock_data)
        
        # Limit results
        filtered_events = filtered_events[:size]
        
        return {
            "hits": {
                "total": {"value": len(filtered_events)},
                "hits": [{"_source": event} for event in filtered_events]
            },
            "took": random.randint(10, 100),
            "timed_out": False
        }
    
    def _filter_events(self, query: Dict[str, Any], events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter events based on query criteria"""
        if not query or "query" not in query:
            return events
        
        query_dict = query.get("query", {})
        
        # Handle query_string
        if "query_string" in query_dict:
            query_str = query_dict["query_string"].get("query", "").lower()
            if "failed" in query_str and "login" in query_str:
                return [e for e in events if e.get("event", {}).get("action") == "authentication_failure"]
            elif "malware" in query_str:
                return [e for e in events if e.get("event", {}).get("category") == "malware"]
            elif "vpn" in query_str:
                return [e for e in events if e.get("service", {}).get("name") == "vpn"]
            elif "anomaly" in query_str or "unusual" in query_str:
                return [e for e in events if "anomaly" in e.get("event", {}).get("action", "")]
        
        # Handle bool query
        if "bool" in query_dict:
            bool_query = query_dict["bool"]
            must_clauses = bool_query.get("must", [])
            
            filtered = events
            for clause in must_clauses:
                if "match" in clause:
                    for field, value in clause["match"].items():
                        field_parts = field.split(".")
                        filtered = [e for e in filtered if self._match_field(e, field_parts, value)]
                elif "range" in clause:
                    # Handle time range queries
                    for field, range_def in clause["range"].items():
                        if field == "@timestamp" and "gte" in range_def:
                            # Filter by time
                            pass  # Simplified for demo
            
            return filtered
        
        return events
    
    def _match_field(self, event: Dict, field_parts: List[str], value: Any) -> bool:
        """Check if event field matches value"""
        current = event
        for part in field_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        return str(current).lower() == str(value).lower()
    
    async def get_field_mappings(self, index: Optional[str] = None) -> Dict[str, Any]:
        """Return mock field mappings"""
        return {
            "@timestamp": {"type": "date"},
            "event.action": {"type": "keyword"},
            "event.category": {"type": "keyword"},
            "event.outcome": {"type": "keyword"},
            "event.severity": {"type": "keyword"},
            "source.ip": {"type": "ip"},
            "source.user.name": {"type": "keyword"},
            "destination.ip": {"type": "ip"},
            "destination.port": {"type": "long"},
            "host.name": {"type": "keyword"},
            "threat.indicator.name": {"type": "keyword"},
            "threat.indicator.type": {"type": "keyword"},
            "service.name": {"type": "keyword"},
            "network.protocol": {"type": "keyword"},
            "message": {"type": "text"}
        }
    
    def test_connection(self) -> bool:
        """Test mock connection"""
        return True
    
    async def get_indices(self) -> List[str]:
        """Return mock indices"""
        return [
            "security-logs-2024.01",
            "security-logs-2024.02", 
            "firewall-logs",
            "vpn-logs",
            "endpoint-logs"
        ]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Return mock statistics"""
        return {
            "connected": True,
            "platform": "Mock SIEM",
            "total_events": len(self.mock_data),
            "indices": 5,
            "status": "healthy"
        }
