"""
Dynamic Authentication Events Generator
Generates realistic authentication events (logins, logouts, failures)
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class AuthenticationEventGenerator(BaseMockGenerator):
    """
    Generates realistic authentication events for demo purposes
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Authentication event types with realistic distribution
        self.auth_event_types = {
            "successful_login": {
                "weight": 0.70,  # 70% successful logins
                "severity": SeverityLevel.LOW,
                "description": "User successfully authenticated"
            },
            "failed_login": {
                "weight": 0.20,  # 20% failed logins
                "severity": SeverityLevel.MEDIUM,
                "description": "Authentication failed"
            },
            "logout": {
                "weight": 0.08,  # 8% logouts
                "severity": SeverityLevel.LOW,
                "description": "User logged out"
            },
            "suspicious_login": {
                "weight": 0.02,  # 2% suspicious logins (unusual location, time, etc.)
                "severity": SeverityLevel.HIGH,
                "description": "Suspicious login attempt detected"
            }
        }
        
        # Login methods
        self.login_methods = [
            "Interactive", "Network", "Service", "RemoteInteractive",
            "CachedInteractive", "NetworkCleartext", "NewCredentials"
        ]
        
        # Common failure reasons
        self.failure_reasons = [
            "Invalid password", "Account locked", "Account disabled",
            "Password expired", "Unknown user", "Time restriction",
            "Logon type not granted", "Account expired"
        ]
        
        # Authentication protocols
        self.auth_protocols = ["NTLM", "Kerberos", "LDAP", "RADIUS", "OAuth2"]
        
        # User agent strings for web logins
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    def generate_event(self) -> MockEvent:
        """Generate a single authentication event"""
        
        # Select event type based on weights
        event_type = self._select_weighted_event_type()
        event_info = self.auth_event_types[event_type]
        
        timestamp = self._get_realistic_timestamp()
        
        # Generate base event structure
        event_data = {
            "@timestamp": timestamp.isoformat(),
            "event": {
                "category": ["authentication"],
                "type": [event_type.replace("_", "-")],
                "outcome": "success" if "successful" in event_type or event_type == "logout" else "failure",
                "action": event_info["description"],
                "kind": "event",
                "module": "authentication"
            },
            "user": {
                "name": self._get_random_username(),
                "domain": random.choice(["WORKGROUP", "DOMAIN", "CORP", "LOCAL"])
            },
            "source": {
                "ip": self._get_random_ip(private=random.choice([True, False])),
                "port": random.randint(1024, 65535)
            },
            "host": {
                "hostname": self._get_random_hostname(),
                "ip": [self._get_random_ip(private=True)],
                "os": {
                    "name": "Windows",
                    "family": "windows",
                    "version": random.choice(["10.0", "11.0", "2019", "2022"])
                }
            },
            "agent": {
                "type": random.choice(["winlogbeat", "auditbeat", "security-agent"]),
                "version": "9.1.4"
            }
        }
        
        # Add event-specific data
        if event_type == "successful_login":
            self._add_successful_login_data(event_data)
        elif event_type == "failed_login":
            self._add_failed_login_data(event_data)
        elif event_type == "logout":
            self._add_logout_data(event_data)
        elif event_type == "suspicious_login":
            self._add_suspicious_login_data(event_data)
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=timestamp,
            event_type=MockDataType.AUTHENTICATION,
            severity=event_info["severity"],
            source=event_data["agent"]["type"],
            data=event_data
        )
    
    def _select_weighted_event_type(self) -> str:
        """Select event type based on realistic weights"""
        rand = random.random()
        cumulative = 0
        
        for event_type, info in self.auth_event_types.items():
            cumulative += info["weight"]
            if rand <= cumulative:
                return event_type
        
        return "successful_login"  # fallback
    
    def _add_successful_login_data(self, event_data: Dict[str, Any]):
        """Add data specific to successful login events"""
        event_data["authentication"] = {
            "method": random.choice(self.login_methods),
            "protocol": random.choice(self.auth_protocols),
            "success": True,
            "session_id": self._generate_id()[:16],
            "logon_type": random.randint(2, 11),
            "duration": random.randint(1, 300)  # seconds to authenticate
        }
        
        # Add session information
        event_data["session"] = {
            "id": event_data["authentication"]["session_id"],
            "start_time": event_data["@timestamp"],
            "duration": random.randint(3600, 28800)  # 1-8 hours
        }
        
        # Add geolocation for remote logins
        if event_data["authentication"]["method"] in ["RemoteInteractive", "Network"]:
            event_data["source"]["geo"] = self._generate_geolocation()
        
        # Add Windows-specific logon data
        event_data["winlog"] = {
            "event_id": 4624,  # Successful logon
            "event_data": {
                "LogonType": event_data["authentication"]["logon_type"],
                "AuthenticationPackageName": event_data["authentication"]["protocol"],
                "LogonProcessName": random.choice(["User32", "Advapi", "NtLmSsp", "Kerberos"]),
                "WorkstationName": self._get_random_hostname(),
                "IpAddress": event_data["source"]["ip"]
            }
        }
    
    def _add_failed_login_data(self, event_data: Dict[str, Any]):
        """Add data specific to failed login events"""
        failure_reason = random.choice(self.failure_reasons)
        
        event_data["authentication"] = {
            "method": random.choice(self.login_methods),
            "protocol": random.choice(self.auth_protocols),
            "success": False,
            "failure_reason": failure_reason,
            "attempt_count": random.randint(1, 5),
            "duration": random.randint(1, 30)  # Usually faster for failures
        }
        
        # Add error details
        event_data["error"] = {
            "code": random.choice(["0xC000006D", "0xC000006E", "0xC0000064", "0xC000006F"]),
            "message": failure_reason
        }
        
        # Add threat intelligence for suspicious IPs
        if random.random() < 0.3:  # 30% chance of suspicious IP
            event_data["threat"] = {
                "indicator": {
                    "ip": event_data["source"]["ip"],
                    "type": "ip",
                    "confidence": random.choice(["low", "medium", "high"])
                },
                "enrichments": {
                    "matched_atomic": random.choice(["tor-exit-node", "malware-c2", "scanner"])
                }
            }
        
        # Windows-specific failed logon data
        event_data["winlog"] = {
            "event_id": 4625,  # Failed logon
            "event_data": {
                "LogonType": random.randint(2, 11),
                "FailureReason": failure_reason,
                "Status": event_data["error"]["code"],
                "SubStatus": event_data["error"]["code"],
                "IpAddress": event_data["source"]["ip"]
            }
        }
    
    def _add_logout_data(self, event_data: Dict[str, Any]):
        """Add data specific to logout events"""
        session_duration = random.randint(300, 28800)  # 5 minutes to 8 hours
        
        event_data["authentication"] = {
            "method": "Logoff",
            "success": True,
            "logoff_type": random.choice(["User", "System", "Forced"])
        }
        
        event_data["session"] = {
            "id": self._generate_id()[:16],
            "duration": session_duration,
            "end_time": event_data["@timestamp"]
        }
        
        # Windows logoff event
        event_data["winlog"] = {
            "event_id": random.choice([4634, 4647]),  # Logoff events
            "event_data": {
                "LogonType": random.randint(2, 11),
                "SessionDuration": session_duration
            }
        }
    
    def _add_suspicious_login_data(self, event_data: Dict[str, Any]):
        """Add data for suspicious login attempts"""
        # Make it look like successful login but add suspicious indicators
        self._add_successful_login_data(event_data)
        
        # Override with suspicious indicators
        event_data["event"]["type"] = ["authentication", "suspicious"]
        
        suspicious_indicators = []
        
        # Unusual time login
        if random.random() < 0.4:
            suspicious_indicators.append("unusual_time")
            # Make timestamp outside business hours
            hour = random.choice([2, 3, 4, 22, 23])
            event_data["@timestamp"] = event_data["@timestamp"][:11] + f"{hour:02d}" + event_data["@timestamp"][13:]
        
        # Unusual location
        if random.random() < 0.5:
            suspicious_indicators.append("unusual_location")
            event_data["source"]["geo"] = self._generate_suspicious_geolocation()
        
        # Multiple rapid attempts
        if random.random() < 0.3:
            suspicious_indicators.append("rapid_attempts")
            event_data["authentication"]["rapid_attempts"] = {
                "count": random.randint(5, 20),
                "timeframe": "5m"
            }
        
        # Add risk scoring
        event_data["risk"] = {
            "score": random.randint(70, 95),
            "level": "high",
            "factors": suspicious_indicators
        }
        
        # Add alert information
        event_data["alert"] = {
            "id": self._generate_id(),
            "title": "Suspicious Authentication Detected",
            "severity": "high",
            "rule": "authentication_anomaly_detection"
        }
    
    def _generate_geolocation(self) -> Dict[str, Any]:
        """Generate realistic geolocation data"""
        locations = [
            {"country": "US", "city": "New York", "region": "NY", "lat": 40.7128, "lon": -74.0060},
            {"country": "US", "city": "Los Angeles", "region": "CA", "lat": 34.0522, "lon": -118.2437},
            {"country": "GB", "city": "London", "region": "ENG", "lat": 51.5074, "lon": -0.1278},
            {"country": "DE", "city": "Berlin", "region": "BE", "lat": 52.5200, "lon": 13.4050},
            {"country": "IN", "city": "Mumbai", "region": "MH", "lat": 19.0760, "lon": 72.8777}
        ]
        
        location = random.choice(locations)
        return {
            "country_iso_code": location["country"],
            "city_name": location["city"],
            "region_name": location["region"],
            "location": {
                "lat": location["lat"] + random.uniform(-0.5, 0.5),
                "lon": location["lon"] + random.uniform(-0.5, 0.5)
            }
        }
    
    def _generate_suspicious_geolocation(self) -> Dict[str, Any]:
        """Generate geolocation from suspicious/unusual locations"""
        suspicious_locations = [
            {"country": "RU", "city": "Moscow", "region": "MOW", "lat": 55.7558, "lon": 37.6173},
            {"country": "CN", "city": "Beijing", "region": "BJ", "lat": 39.9042, "lon": 116.4074},
            {"country": "KP", "city": "Pyongyang", "region": "PY", "lat": 39.0392, "lon": 125.7625},
            {"country": "IR", "city": "Tehran", "region": "TH", "lat": 35.6892, "lon": 51.3890},
            {"country": "BY", "city": "Minsk", "region": "MI", "lat": 53.9045, "lon": 27.5615}
        ]
        
        location = random.choice(suspicious_locations)
        return {
            "country_iso_code": location["country"],
            "city_name": location["city"],
            "region_name": location["region"],
            "location": {
                "lat": location["lat"] + random.uniform(-0.5, 0.5),
                "lon": location["lon"] + random.uniform(-0.5, 0.5)
            },
            "threat_intel": {
                "is_tor": random.choice([True, False]),
                "is_vpn": random.choice([True, False]),
                "reputation": "suspicious"
            }
        }
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of authentication events"""
        return [self.generate_event() for _ in range(count)]
