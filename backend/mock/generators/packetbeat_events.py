"""
Packetbeat Network Security Events Generator  
Generates realistic network packet analysis and security monitoring events matching Packetbeat format
"""

import random
from datetime import datetime, timezone
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class PacketbeatEventGenerator(BaseMockGenerator):
    """
    Generates realistic Packetbeat events for network traffic analysis and security monitoring
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Network protocols and their details
        self.network_protocols = {
            "http": {
                "description": "HTTP traffic analysis",
                "category": "network", 
                "port": [80, 8080, 8000, 3000],
                "severity": SeverityLevel.LOW,
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "status_codes": [200, 201, 301, 302, 400, 401, 403, 404, 500, 502, 503]
            },
            "https": {
                "description": "HTTPS/TLS traffic analysis", 
                "category": "network",
                "port": [443, 8443, 9443],
                "severity": SeverityLevel.LOW,
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "status_codes": [200, 201, 301, 302, 400, 401, 403, 404, 500, 502, 503]
            },
            "dns": {
                "description": "DNS query monitoring",
                "category": "network",
                "port": [53],
                "severity": SeverityLevel.MEDIUM,
                "query_types": ["A", "AAAA", "CNAME", "MX", "NS", "PTR", "TXT", "SOA"],
                "response_codes": ["NOERROR", "NXDOMAIN", "SERVFAIL", "REFUSED"]
            },
            "mysql": {
                "description": "MySQL database monitoring",
                "category": "database",
                "port": [3306],
                "severity": SeverityLevel.MEDIUM,
                "commands": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "SHOW", "USE"]
            },
            "postgresql": {
                "description": "PostgreSQL database monitoring", 
                "category": "database",
                "port": [5432],
                "severity": SeverityLevel.MEDIUM,
                "commands": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "GRANT", "REVOKE"]
            },
            "redis": {
                "description": "Redis cache monitoring",
                "category": "database",
                "port": [6379],
                "severity": SeverityLevel.LOW,
                "commands": ["GET", "SET", "DEL", "EXISTS", "HGET", "HSET", "LPUSH", "RPOP"]
            },
            "elasticsearch": {
                "description": "Elasticsearch API monitoring",
                "category": "database", 
                "port": [9200, 9300],
                "severity": SeverityLevel.MEDIUM,
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "endpoints": ["/_search", "/_bulk", "/_mapping", "/_cluster/health", "/_cat/indices"]
            },
            "ssh": {
                "description": "SSH connection monitoring",
                "category": "network",
                "port": [22],
                "severity": SeverityLevel.HIGH,
                "auth_methods": ["password", "publickey", "keyboard-interactive", "gssapi-with-mic"]
            },
            "ftp": {
                "description": "FTP file transfer monitoring",
                "category": "file",
                "port": [21, 990],
                "severity": SeverityLevel.MEDIUM,
                "commands": ["USER", "PASS", "STOR", "RETR", "LIST", "DELE", "MKD", "RMD"]
            },
            "smtp": {
                "description": "SMTP email monitoring",
                "category": "email",
                "port": [25, 587, 465],
                "severity": SeverityLevel.MEDIUM,
                "commands": ["HELO", "EHLO", "MAIL FROM", "RCPT TO", "DATA", "QUIT", "AUTH"]
            }
        }
        
        # Common domains and URLs
        self.domains = [
            "api.company.com", "www.example.org", "auth.service.io", "db.internal.net",
            "cdn.assets.com", "mail.enterprise.co", "ftp.backup.site", "ssh.admin.local",
            "elastic.logging.io", "redis.cache.net", "mysql.db.internal", "postgres.data.co"
        ]
        
        # User agents for HTTP traffic
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15", 
            "curl/7.68.0", "PostmanRuntime/7.29.2", "Python-urllib/3.9",
            "Go-http-client/1.1", "Apache-HttpClient/4.5.13", "okhttp/4.9.3"
        ]
        
        # SQL queries for database monitoring
        self.sql_queries = [
            "SELECT * FROM users WHERE active = 1",
            "INSERT INTO logs (timestamp, message, level) VALUES (?, ?, ?)",
            "UPDATE user_sessions SET last_activity = NOW() WHERE user_id = ?",
            "DELETE FROM temp_files WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 DAY)",
            "CREATE INDEX idx_user_email ON users(email)",
            "SHOW TABLES LIKE 'audit_%'",
            "GRANT SELECT ON database.* TO 'readonly'@'%'",
            "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
        ]
    
    def generate_event(self) -> MockEvent:
        """Generate a single Packetbeat network security event"""
        
        # Select random protocol
        protocol = random.choice(list(self.network_protocols.keys()))
        protocol_info = self.network_protocols[protocol]
        
        # Generate basic network event structure
        event_data = {
            "@timestamp": self._get_realistic_timestamp().isoformat(),
            "event": {
                "module": "packetbeat",
                "dataset": f"packetbeat.{protocol}",
                "action": protocol_info["description"],
                "category": [protocol_info["category"]],
                "type": ["connection", "protocol"] if protocol in ["ssh", "ftp"] else ["info", "network"],
                "outcome": "success" if random.random() > 0.05 else "failure",
                "duration": random.randint(1000000, 500000000),  # nanoseconds
                "severity": protocol_info["severity"].value
            },
            "host": {
                "hostname": self._get_random_hostname(),
                "name": self._get_random_hostname(),
                "ip": [self._get_random_ip(private=True)],
                "os": {
                    "name": random.choice(["Linux", "Windows", "macOS"]),
                    "family": random.choice(["linux", "windows", "darwin"]),
                    "platform": random.choice(["linux", "windows", "darwin"])
                }
            },
            "agent": {
                "type": "packetbeat", 
                "version": "8.11.0",
                "hostname": self._get_random_hostname(),
                "ephemeral_id": self._generate_uuid(),
                "id": self._generate_uuid()
            },
            "network": {
                "protocol": protocol if protocol in ["tcp", "udp"] else "tcp",
                "transport": "tcp" if protocol not in ["dns"] else "udp",
                "type": "ipv4",
                "direction": random.choice(["inbound", "outbound", "internal"]),
                "community_id": self._generate_community_id()
            },
            "source": {
                "ip": self._get_random_ip(private=random.choice([True, False])),
                "port": random.randint(1024, 65535),
                "bytes": random.randint(100, 50000),
                "packets": random.randint(1, 100)
            },
            "destination": {
                "ip": self._get_random_ip(private=True),
                "port": random.choice(protocol_info["port"]),
                "bytes": random.randint(500, 100000),
                "packets": random.randint(5, 200)
            },
            "ecs": {
                "version": "8.0.0"
            }
        }
        
        # Add protocol-specific fields
        self._add_protocol_specific_fields(protocol, event_data, protocol_info)
        
        # Add geolocation for external IPs
        if not self._is_private_ip(event_data["source"]["ip"]):
            event_data["source"]["geo"] = self._generate_geolocation()
        
        # Add threat intelligence for suspicious activity
        if (event_data["event"]["outcome"] == "failure" or 
            protocol in ["ssh", "ftp"] or
            event_data["network"]["direction"] == "inbound"):
            self._add_threat_intelligence(event_data, protocol)
        
        # Add status and classification fields for dashboard metrics
        event_data["severity"] = protocol_info["severity"].value  # Root level for dashboard
        event_data["status"] = random.choice(["active", "resolved", "investigating"])
        
        # Add additional classification fields based on severity
        if protocol_info["severity"].value >= 3:  # HIGH or CRITICAL
            event_data["alert_type"] = "network_alert"
            event_data["threat_level"] = "network_security"
        elif protocol_info["severity"].value >= 2:  # MEDIUM
            event_data["alert_type"] = "network_warning"
            event_data["threat_level"] = "network_security"
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=datetime.fromisoformat(event_data["@timestamp"].replace("Z", "+00:00")).replace(tzinfo=None),
            event_type=MockDataType.PACKETBEAT_EVENT,
            severity=protocol_info["severity"], 
            source="packetbeat",
            data=event_data
        )
    
    def _add_protocol_specific_fields(self, protocol: str, event_data: Dict[str, Any], protocol_info: Dict[str, Any]):
        """Add protocol-specific fields based on network protocol"""
        
        if protocol in ["http", "https"]:
            # HTTP/HTTPS specific fields
            method = random.choice(protocol_info["methods"])
            status_code = random.choice(protocol_info["status_codes"])
            domain = random.choice(self.domains)
            path = random.choice(["/", "/api/v1/users", "/dashboard", "/login", "/api/data", "/health", "/metrics"])
            
            event_data["http"] = {
                "request": {
                    "method": method,
                    "body": {
                        "bytes": random.randint(0, 10000)
                    },
                    "bytes": random.randint(200, 5000),
                    "headers": {
                        "user-agent": [random.choice(self.user_agents)],
                        "host": [domain],
                        "accept": ["application/json, text/plain, */*"],
                        "content-type": ["application/json"] if method in ["POST", "PUT", "PATCH"] else []
                    }
                },
                "response": {
                    "status_code": status_code,
                    "body": {
                        "bytes": random.randint(500, 20000)
                    },
                    "bytes": random.randint(1000, 25000),
                    "headers": {
                        "content-type": ["application/json"],
                        "server": [random.choice(["nginx/1.20.2", "Apache/2.4.41", "Microsoft-IIS/10.0"])],
                        "x-powered-by": [random.choice(["Express", "PHP/8.0", "ASP.NET"])]
                    }
                }
            }
            
            event_data["url"] = {
                "domain": domain,
                "path": path,
                "scheme": protocol,
                "full": f"{protocol}://{domain}{path}"
            }
            
            # Add suspicious indicators
            if status_code >= 400 or path in ["/admin", "/wp-admin", "/.env", "/config"]:
                event_data["event"]["risk_score"] = random.randint(60, 90)
        
        elif protocol == "dns":
            # DNS specific fields
            query_type = random.choice(protocol_info["query_types"])
            response_code = random.choice(protocol_info["response_codes"])
            domain = random.choice(self.domains + ["malware.suspicious.com", "phishing.bad.net"])
            
            event_data["dns"] = {
                "question": {
                    "name": domain,
                    "type": query_type,
                    "class": "IN"
                },
                "answers": [] if response_code != "NOERROR" else [
                    {
                        "name": domain,
                        "type": query_type,
                        "class": "IN",
                        "data": self._get_random_ip() if query_type == "A" else f"mail.{domain}",
                        "ttl": random.randint(300, 86400)
                    }
                ],
                "response_code": response_code,
                "flags": {
                    "authoritative": random.choice([True, False]),
                    "recursion_desired": True,
                    "recursion_available": True,
                    "truncated_response": False
                }
            }
            
            # Suspicious DNS queries
            if "malware" in domain or "phishing" in domain or response_code == "NXDOMAIN":
                event_data["event"]["risk_score"] = random.randint(70, 95)
                event_data["threat"] = {
                    "indicator": {
                        "type": "domain",
                        "value": domain,
                        "description": "Suspicious domain query"
                    }
                }
        
        elif protocol in ["mysql", "postgresql"]:
            # Database specific fields
            command = random.choice(protocol_info["commands"])
            query = random.choice(self.sql_queries)
            
            event_data[protocol] = {
                "query": query,
                "command": command,
                "rows_affected": random.randint(0, 1000) if command in ["INSERT", "UPDATE", "DELETE"] else 0,
                "rows_examined": random.randint(1, 10000) if command == "SELECT" else 0,
                "response_time": random.randint(1, 5000),  # milliseconds
                "status": "OK" if event_data["event"]["outcome"] == "success" else "ERROR"
            }
            
            # Add database connection info
            event_data["user"] = {
                "name": random.choice(["app_user", "admin", "readonly", "backup", "developer"]),
                "database": random.choice(["webapp", "analytics", "logs", "users", "inventory"])
            }
            
            # Suspicious database activity
            if command in ["DROP", "DELETE", "GRANT", "CREATE"] or "admin" in query.lower():
                event_data["event"]["risk_score"] = random.randint(50, 80)
        
        elif protocol == "ssh":
            # SSH specific fields
            auth_method = random.choice(protocol_info["auth_methods"])
            username = random.choice(["admin", "root", "user", "developer", "service", "backup"])
            
            event_data["ssh"] = {
                "method": auth_method,
                "signature": f"SSH-2.0-OpenSSH_{random.uniform(7.4, 8.9):.1f}",
                "connection": {
                    "session": self._generate_uuid()[:8],
                    "state": "established" if event_data["event"]["outcome"] == "success" else "failed"
                }
            }
            
            event_data["user"] = {
                "name": username
            }
            
            # SSH is always high risk for monitoring
            event_data["event"]["risk_score"] = random.randint(40, 70)
            if event_data["event"]["outcome"] == "failure":
                event_data["event"]["risk_score"] = random.randint(70, 90)
        
        elif protocol == "redis":
            # Redis specific fields
            command = random.choice(protocol_info["commands"])
            
            event_data["redis"] = {
                "command": command,
                "key": f"cache:{random.choice(['user', 'session', 'data', 'config'])}:{random.randint(1000, 9999)}",
                "database": random.randint(0, 15),
                "response_time": random.randint(1, 100),  # milliseconds
                "status": "OK" if event_data["event"]["outcome"] == "success" else "ERROR"
            }
    
    def _add_threat_intelligence(self, event_data: Dict[str, Any], protocol: str):
        """Add threat intelligence information for suspicious events"""
        
        # Generate threat indicators
        threat_types = ["malware", "phishing", "brute_force", "port_scan", "data_exfiltration", "backdoor"]
        
        event_data["threat"] = {
            "indicator": {
                "type": random.choice(["ip", "domain", "hash", "url"]),
                "confidence": random.choice(["low", "medium", "high"]),
                "description": f"Suspicious {protocol} activity detected"
            },
            "technique": {
                "id": f"T{random.randint(1000, 1599)}",
                "name": random.choice(threat_types).replace("_", " ").title()
            },
            "tactic": {
                "id": f"TA{random.randint(1, 15):04d}",
                "name": random.choice(["Initial Access", "Execution", "Defense Evasion", "Discovery", "Command and Control"])
            }
        }
        
        # Risk scoring
        if "risk_score" not in event_data["event"]:
            event_data["event"]["risk_score"] = random.randint(50, 90)
        
        event_data["risk"] = {
            "score": event_data["event"]["risk_score"],
            "score_norm": round(event_data["event"]["risk_score"] / 10.0, 1)
        }
    
    def _generate_community_id(self) -> str:
        """Generate a network community ID hash"""
        import hashlib
        data = f"{random.randint(1, 999999)}{random.randint(1, 999999)}"
        return f"1:{hashlib.sha1(data.encode()).hexdigest()[:16]}"
    
    def _generate_geolocation(self) -> Dict[str, Any]:
        """Generate realistic geolocation data"""
        countries = [
            {"code": "US", "name": "United States", "continent": "North America"},
            {"code": "CN", "name": "China", "continent": "Asia"},
            {"code": "RU", "name": "Russia", "continent": "Asia"}, 
            {"code": "DE", "name": "Germany", "continent": "Europe"},
            {"code": "BR", "name": "Brazil", "continent": "South America"},
            {"code": "IN", "name": "India", "continent": "Asia"}
        ]
        
        country = random.choice(countries)
        return {
            "country_iso_code": country["code"],
            "country_name": country["name"],
            "continent_name": country["continent"],
            "city_name": random.choice(["Unknown", "Moscow", "Beijing", "Berlin", "São Paulo", "Mumbai"]),
            "location": {
                "lat": round(random.uniform(-90, 90), 4),
                "lon": round(random.uniform(-180, 180), 4)
            }
        }
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP address is private"""
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        
        first_octet = int(parts[0])
        second_octet = int(parts[1])
        
        # Private IP ranges
        if first_octet == 10:
            return True
        elif first_octet == 172 and 16 <= second_octet <= 31:
            return True
        elif first_octet == 192 and second_octet == 168:
            return True
        
        return False
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of Packetbeat network security events"""
        return [self.generate_event() for _ in range(count)]
