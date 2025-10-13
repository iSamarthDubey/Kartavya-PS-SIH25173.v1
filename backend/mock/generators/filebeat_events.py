"""
Filebeat Log Security Events Generator
Generates realistic log file monitoring and security analysis events matching Filebeat format
"""

import random
from datetime import datetime, timezone
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class FilebeatEventGenerator(BaseMockGenerator):
    """
    Generates realistic Filebeat events for log file monitoring and security analysis
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Log file types and their characteristics
        self.log_types = {
            "apache_access": {
                "description": "Apache access log monitoring",
                "category": "web",
                "severity": SeverityLevel.LOW,
                "log_path": "/var/log/apache2/access.log",
                "format": "combined"
            },
            "nginx_access": {
                "description": "Nginx access log monitoring",
                "category": "web", 
                "severity": SeverityLevel.LOW,
                "log_path": "/var/log/nginx/access.log",
                "format": "combined"
            },
            "system_auth": {
                "description": "System authentication logs",
                "category": "authentication",
                "severity": SeverityLevel.HIGH,
                "log_path": "/var/log/auth.log",
                "format": "syslog"
            },
            "sshd": {
                "description": "SSH daemon logs",
                "category": "network",
                "severity": SeverityLevel.HIGH, 
                "log_path": "/var/log/auth.log",
                "format": "syslog"
            },
            "firewall": {
                "description": "Firewall log monitoring",
                "category": "network",
                "severity": SeverityLevel.MEDIUM,
                "log_path": "/var/log/ufw.log",
                "format": "syslog"
            },
            "application": {
                "description": "Application error logs",
                "category": "application",
                "severity": SeverityLevel.MEDIUM,
                "log_path": "/var/log/application.log",
                "format": "json"
            },
            "security_audit": {
                "description": "Security audit logs",
                "category": "audit",
                "severity": SeverityLevel.HIGH,
                "log_path": "/var/log/audit/audit.log", 
                "format": "audit"
            },
            "database_slow": {
                "description": "Database slow query logs",
                "category": "database",
                "severity": SeverityLevel.MEDIUM,
                "log_path": "/var/log/mysql/mysql-slow.log",
                "format": "mysql_slow"
            }
        }
        
        # HTTP status codes and their meanings
        self.http_status_codes = {
            200: "OK", 301: "Moved Permanently", 302: "Found", 304: "Not Modified",
            400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
            500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable"
        }
        
        # Common web paths and user agents
        self.web_paths = [
            "/", "/index.html", "/api/v1/users", "/api/v1/data", "/login", "/dashboard",
            "/admin", "/wp-admin", "/api/auth", "/health", "/metrics", "/favicon.ico",
            "/robots.txt", "/.env", "/config.php", "/api/v2/search", "/upload"
        ]
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "python-requests/2.25.1", "curl/7.68.0", "PostmanRuntime/7.28.4",
            "Googlebot/2.1", "bingbot/2.0", "Slackbot-LinkExpanding 1.0"
        ]
        
        # SSH and authentication messages
        self.ssh_messages = [
            "Accepted publickey for {user} from {ip} port {port} ssh2: RSA SHA256:{key}",
            "Failed password for {user} from {ip} port {port} ssh2",
            "Failed password for invalid user {user} from {ip} port {port} ssh2", 
            "Connection closed by authenticating user {user} {ip} port {port} [preauth]",
            "Received disconnect from {ip} port {port}:11: Bye Bye [preauth]",
            "Invalid user {user} from {ip} port {port}",
            "User {user} from {ip} not allowed because not listed in AllowUsers"
        ]
        
        # Firewall actions and protocols  
        self.firewall_actions = ["ALLOW", "DENY", "DROP", "REJECT"]
        self.network_protocols = ["TCP", "UDP", "ICMP"]
        
        # Application log levels and messages
        self.app_log_levels = ["INFO", "WARN", "ERROR", "DEBUG", "FATAL"]
        self.app_messages = [
            "User authentication successful for user: {user}",
            "Failed login attempt from IP: {ip}",
            "Database connection established",
            "Cache miss for key: {key}",
            "API request processed successfully",
            "Payment processing completed for order: {order_id}",
            "File upload completed: {filename}",
            "Security alert: Multiple failed login attempts detected",
            "System backup completed successfully",
            "Configuration file updated by user: {user}"
        ]
    
    def generate_event(self) -> MockEvent:
        """Generate a single Filebeat log security event"""
        
        # Select random log type
        log_type = random.choice(list(self.log_types.keys()))
        log_info = self.log_types[log_type]
        
        # Generate basic log event structure
        event_data = {
            "@timestamp": self._get_realistic_timestamp().isoformat(),
            "event": {
                "module": "filebeat",
                "dataset": f"filebeat.{log_type}",
                "action": log_info["description"],
                "category": [log_info["category"]],
                "type": ["info", "access"] if "access" in log_type else ["start", "authentication"] if log_info["category"] == "authentication" else ["info"],
                "outcome": "success" if random.random() > 0.1 else "failure",
                "severity": log_info["severity"].value
            },
            "host": {
                "hostname": self._get_random_hostname(),
                "name": self._get_random_hostname(),
                "ip": [self._get_random_ip(private=True)],
                "os": {
                    "name": random.choice(["Linux", "Ubuntu", "CentOS", "RHEL"]),
                    "family": "linux",
                    "platform": "linux",
                    "version": random.choice(["20.04", "22.04", "8.5", "9.0"])
                }
            },
            "agent": {
                "type": "filebeat",
                "version": "8.11.0", 
                "hostname": self._get_random_hostname(),
                "ephemeral_id": self._generate_uuid(),
                "id": self._generate_uuid()
            },
            "log": {
                "file": {
                    "path": log_info["log_path"]
                },
                "offset": random.randint(1000, 999999)
            },
            "input": {
                "type": "log"
            },
            "ecs": {
                "version": "8.0.0"
            }
        }
        
        # Add log-specific fields
        self._add_log_specific_fields(log_type, event_data, log_info)
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=datetime.fromisoformat(event_data["@timestamp"].replace("Z", "+00:00")).replace(tzinfo=None),
            event_type=MockDataType.FILEBEAT_EVENT,
            severity=log_info["severity"],
            source="filebeat",
            data=event_data
        )
    
    def _add_log_specific_fields(self, log_type: str, event_data: Dict[str, Any], log_info: Dict[str, Any]):
        """Add specific fields based on log file type"""
        
        if log_type in ["apache_access", "nginx_access"]:
            # Web server access logs
            method = random.choice(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
            status_code = random.choice(list(self.http_status_codes.keys()))
            path = random.choice(self.web_paths)
            user_agent = random.choice(self.user_agents)
            
            event_data["http"] = {
                "request": {
                    "method": method,
                    "body": {
                        "bytes": random.randint(0, 5000) if method in ["POST", "PUT"] else 0
                    }
                },
                "response": {
                    "status_code": status_code,
                    "body": {
                        "bytes": random.randint(200, 50000)
                    }
                }
            }
            
            event_data["url"] = {
                "path": path,
                "domain": random.choice(["api.company.com", "www.example.org", "admin.internal.net"])
            }
            
            event_data["user_agent"] = {
                "original": user_agent,
                "name": self._extract_browser_name(user_agent),
                "version": self._extract_browser_version(user_agent)
            }
            
            event_data["source"] = {
                "ip": self._get_random_ip(private=random.choice([True, False])),
                "port": random.randint(1024, 65535)
            }
            
            # Add referrer occasionally
            if random.random() > 0.7:
                event_data["http"]["request"]["referrer"] = random.choice([
                    "https://google.com/", "https://github.com/", "https://stackoverflow.com/",
                    "-", "https://company.com/dashboard"
                ])
            
            # Generate raw log message
            event_data["message"] = self._generate_access_log_message(event_data, log_type)
            
            # Mark suspicious activity
            if status_code >= 400 or path in ["/admin", "/.env", "/config.php"]:
                event_data["event"]["risk_score"] = random.randint(50, 80)
                event_data["tags"] = ["suspicious", "security"]
        
        elif log_type in ["system_auth", "sshd"]:
            # Authentication and SSH logs
            user = random.choice(["admin", "root", "user", "developer", "service", "invalid_user"])
            ip = self._get_random_ip(private=random.choice([True, False]))
            port = random.randint(1024, 65535)
            ssh_key = self._generate_ssh_key_hash()
            
            # Select message template
            message_template = random.choice(self.ssh_messages)
            message = message_template.format(user=user, ip=ip, port=port, key=ssh_key)
            
            event_data["message"] = message
            event_data["system"] = {
                "auth": {
                    "ssh": {
                        "method": random.choice(["password", "publickey", "keyboard-interactive"]),
                        "signature": f"SSH-2.0-OpenSSH_{random.uniform(7.0, 8.5):.1f}"
                    }
                }
            }
            
            event_data["user"] = {
                "name": user
            }
            
            event_data["source"] = {
                "ip": ip,
                "port": port
            }
            
            # Add process info
            event_data["process"] = {
                "name": "sshd",
                "pid": random.randint(1000, 99999)
            }
            
            # Determine if this is suspicious
            if "Failed" in message or "Invalid" in message or user == "root":
                event_data["event"]["risk_score"] = random.randint(60, 90)
                event_data["tags"] = ["authentication", "failed", "security"]
                
                # Add geolocation for external IPs
                if not self._is_private_ip(ip):
                    event_data["source"]["geo"] = self._generate_geolocation()
        
        elif log_type == "firewall":
            # Firewall logs
            action = random.choice(self.firewall_actions)
            protocol = random.choice(self.network_protocols)
            src_ip = self._get_random_ip(private=random.choice([True, False]))
            dst_ip = self._get_random_ip(private=True)
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([22, 80, 443, 3306, 5432, 6379, 9200])
            
            event_data["message"] = f"[UFW {action}] {protocol} {src_ip}:{src_port} -> {dst_ip}:{dst_port}"
            
            event_data["network"] = {
                "transport": protocol.lower(),
                "protocol": protocol.lower(),
                "direction": random.choice(["inbound", "outbound"])
            }
            
            event_data["source"] = {
                "ip": src_ip,
                "port": src_port
            }
            
            event_data["destination"] = {
                "ip": dst_ip, 
                "port": dst_port
            }
            
            event_data["rule"] = {
                "name": f"UFW_{action}",
                "id": random.randint(1, 99)
            }
            
            # Mark blocked/denied traffic as suspicious
            if action in ["DENY", "DROP", "REJECT"]:
                event_data["event"]["risk_score"] = random.randint(40, 70)
                event_data["tags"] = ["firewall", "blocked", "security"]
        
        elif log_type == "application":
            # Application logs
            log_level = random.choice(self.app_log_levels)
            message_template = random.choice(self.app_messages)
            
            # Generate context variables
            context = {
                "user": self._get_random_username(),
                "ip": self._get_random_ip(),
                "key": f"cache_{random.randint(1000, 9999)}",
                "order_id": f"ORD_{random.randint(100000, 999999)}",
                "filename": f"upload_{random.randint(1000, 9999)}.{random.choice(['jpg', 'pdf', 'doc', 'xlsx'])}"
            }
            
            # Format message with available context
            try:
                message = message_template.format(**context)
            except KeyError:
                message = message_template
            
            event_data["message"] = f"[{log_level}] {message}"
            event_data["log"]["level"] = log_level
            
            # Add application context
            event_data["service"] = {
                "name": random.choice(["webapp", "api-server", "payment-service", "auth-service"]),
                "version": f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
            }
            
            # Add user info if relevant
            if "user" in message.lower():
                event_data["user"] = {
                    "name": context.get("user", "unknown")
                }
            
            # Mark ERROR and FATAL as higher risk
            if log_level in ["ERROR", "FATAL"]:
                event_data["event"]["risk_score"] = random.randint(50, 75)
                event_data["tags"] = ["application", "error"]
        
        elif log_type == "security_audit":
            # Security audit logs
            audit_events = [
                "SYSCALL: execve /bin/bash by user {user}",
                "USER_CMD: sudo command executed by {user}: {command}",
                "USER_LOGIN: Failed login attempt for user {user} from {ip}",
                "FILE_WRITE: Sensitive file modified: {file} by user {user}",
                "NETWORK_CONNECT: Outbound connection to {ip}:{port}",
                "PRIVILEGE_ESCALATION: User {user} gained elevated privileges"
            ]
            
            audit_event = random.choice(audit_events)
            context = {
                "user": random.choice(["admin", "root", "service", "developer"]),
                "ip": self._get_random_ip(),
                "command": random.choice(["systemctl restart nginx", "cat /etc/passwd", "chmod 777 /tmp"]),
                "file": random.choice(["/etc/passwd", "/etc/shadow", "/root/.ssh/authorized_keys"]),
                "port": random.choice([22, 80, 443, 3306])
            }
            
            try:
                message = audit_event.format(**context)
            except KeyError:
                message = audit_event
            
            event_data["message"] = message
            event_data["auditd"] = {
                "log": {
                    "record_type": random.choice(["SYSCALL", "USER_CMD", "USER_LOGIN", "PATH"]),
                    "sequence": random.randint(1000, 99999)
                }
            }
            
            # All audit events are high risk
            event_data["event"]["risk_score"] = random.randint(60, 90)
            event_data["tags"] = ["audit", "security", "compliance"]
    
    def _generate_access_log_message(self, event_data: Dict[str, Any], log_type: str) -> str:
        """Generate realistic access log message"""
        
        ip = event_data["source"]["ip"]
        method = event_data["http"]["request"]["method"]
        path = event_data["url"]["path"]
        status = event_data["http"]["response"]["status_code"]
        size = event_data["http"]["response"]["body"]["bytes"]
        user_agent = event_data["user_agent"]["original"]
        referrer = event_data.get("http", {}).get("request", {}).get("referrer", "-")
        
        timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
        
        if log_type == "apache_access":
            return f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status} {size} "{referrer}" "{user_agent}"'
        else:  # nginx_access
            return f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status} {size} "{referrer}" "{user_agent}"'
    
    def _extract_browser_name(self, user_agent: str) -> str:
        """Extract browser name from user agent"""
        if "Chrome" in user_agent:
            return "Chrome"
        elif "Firefox" in user_agent:
            return "Firefox"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            return "Safari"
        elif "curl" in user_agent:
            return "curl"
        elif "python" in user_agent.lower():
            return "python-requests"
        else:
            return "Other"
    
    def _extract_browser_version(self, user_agent: str) -> str:
        """Extract browser version from user agent"""
        import re
        if "Chrome" in user_agent:
            match = re.search(r"Chrome/(\d+\.\d+)", user_agent)
            return match.group(1) if match else "unknown"
        elif "Firefox" in user_agent:
            match = re.search(r"Firefox/(\d+\.\d+)", user_agent)
            return match.group(1) if match else "unknown"
        elif "Safari" in user_agent:
            match = re.search(r"Version/(\d+\.\d+)", user_agent)
            return match.group(1) if match else "unknown"
        else:
            return "unknown"
    
    def _generate_ssh_key_hash(self) -> str:
        """Generate a realistic SSH key hash"""
        import hashlib
        random_data = str(random.randint(100000, 999999))
        return hashlib.sha256(random_data.encode()).hexdigest()[:43]
    
    def _generate_geolocation(self) -> Dict[str, Any]:
        """Generate realistic geolocation data"""
        countries = [
            {"code": "US", "name": "United States"},
            {"code": "CN", "name": "China"},
            {"code": "RU", "name": "Russia"},
            {"code": "DE", "name": "Germany"},
            {"code": "BR", "name": "Brazil"}
        ]
        
        country = random.choice(countries)
        return {
            "country_iso_code": country["code"],
            "country_name": country["name"],
            "city_name": "Unknown",
            "location": {
                "lat": round(random.uniform(-90, 90), 4),
                "lon": round(random.uniform(-180, 180), 4)
            }
        }
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private"""
        parts = ip.split(".")
        if len(parts) != 4:
            return False
            
        first = int(parts[0])
        second = int(parts[1])
        
        return (first == 10 or 
                (first == 172 and 16 <= second <= 31) or
                (first == 192 and second == 168))
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of Filebeat log security events"""
        return [self.generate_event() for _ in range(count)]
