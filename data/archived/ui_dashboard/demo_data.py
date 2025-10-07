"""
Demo data generator for Kartavya SIEM Assistant.
Provides sample data when real SIEM connections are not available.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DemoDataGenerator:
    """Generate sample security events for demonstration."""
    
    def __init__(self):
        """Initialize demo data generator."""
        self.sample_events = [
            "Failed authentication attempt",
            "Successful user login", 
            "Suspicious network traffic detected",
            "Malware signature detected",
            "Firewall rule violation",
            "Privilege escalation attempt",
            "Unusual file access pattern",
            "Port scan activity detected",
            "DNS query to suspicious domain",
            "Brute force attack detected"
        ]
        
        self.severity_levels = ["low", "medium", "high", "critical"]
        self.source_ips = [
            "192.168.1.100", "10.0.0.50", "172.16.1.200", 
            "203.0.113.10", "198.51.100.25", "192.0.2.100"
        ]
        self.users = ["admin", "user1", "service_account", "guest", "developer"]
        self.hosts = ["workstation-01", "server-db", "web-server", "mail-server"]
    
    def generate_events(self, count: int = 10, intent: str = "search_logs") -> List[Dict[str, Any]]:
        """Generate sample security events."""
        events = []
        
        for i in range(count):
            # Generate timestamp within last 24 hours
            timestamp = datetime.now() - timedelta(
                minutes=random.randint(0, 1440)
            )
            
            event = {
                "@timestamp": timestamp.isoformat(),
                "event_id": f"DEMO-{i+1:04d}",
                "message": random.choice(self.sample_events),
                "severity": random.choice(self.severity_levels),
                "source_ip": random.choice(self.source_ips),
                "user": random.choice(self.users),
                "host": random.choice(self.hosts),
                "event_type": self._get_event_type(intent),
                "status": random.choice(["success", "failure", "warning"]),
                "source": "demo_data"
            }
            
            # Add intent-specific fields
            if intent == "count_events":
                event["count"] = random.randint(1, 100)
            elif intent == "analyze_threat":
                event["threat_score"] = random.randint(1, 10)
                event["threat_category"] = random.choice([
                    "malware", "network_intrusion", "data_breach", "insider_threat"
                ])
            
            events.append(event)
        
        return events
    
    def _get_event_type(self, intent: str) -> str:
        """Get appropriate event type based on intent."""
        event_types = {
            "search_logs": ["authentication", "network", "system", "security"],
            "count_events": ["alert", "warning", "error"],
            "analyze_threat": ["malware", "intrusion", "suspicious_activity"],
            "get_stats": ["performance", "usage", "security"],
            "alert_info": ["alert", "critical_event", "security_incident"]
        }
        
        types = event_types.get(intent, ["general"])
        return random.choice(types)
    
    def get_demo_stats(self) -> Dict[str, Any]:
        """Generate demo statistics."""
        return {
            "total_events": random.randint(1000, 5000),
            "high_severity_alerts": random.randint(10, 50),
            "active_threats": random.randint(1, 10),
            "blocked_ips": random.randint(50, 200),
            "failed_logins": random.randint(20, 100),
            "malware_detections": random.randint(0, 5)
        }
    
    def get_demo_chart_data(self) -> Dict[str, Any]:
        """Generate data for demo charts."""
        # Generate trend data for last 30 days
        dates = []
        values = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
            values.append(random.randint(20, 100))
        
        return {
            "trend_data": {
                "dates": dates,
                "values": values
            },
            "severity_distribution": {
                "Low": random.randint(100, 200),
                "Medium": random.randint(50, 100), 
                "High": random.randint(20, 50),
                "Critical": random.randint(5, 20)
            },
            "top_threats": [
                {"name": "Malware Detection", "count": random.randint(10, 30)},
                {"name": "Failed Authentication", "count": random.randint(15, 40)},
                {"name": "Network Intrusion", "count": random.randint(5, 20)},
                {"name": "Suspicious Activity", "count": random.randint(8, 25)}
            ]
        }