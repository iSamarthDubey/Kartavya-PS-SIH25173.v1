"""
Auditbeat Security Events Generator
Generates realistic Linux/Unix system audit and security events matching Auditbeat format
"""

import random
from datetime import datetime, timezone
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class AuditbeatEventGenerator(BaseMockGenerator):
    """
    Generates realistic Auditbeat events for Linux/Unix system security auditing
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Linux audit event types and their details
        self.audit_events = {
            # System calls and security events
            "syscall": {
                "description": "System call auditing",
                "category": "process",
                "severity": SeverityLevel.LOW,
                "subcategories": ["execve", "connect", "accept", "bind", "listen", "open", "write", "unlink"]
            },
            "user_login": {
                "description": "User login event",
                "category": "authentication", 
                "severity": SeverityLevel.MEDIUM,
                "subcategories": ["login", "logout", "failed_login", "session_start", "session_end"]
            },
            "user_mgmt": {
                "description": "User management event",
                "category": "iam",
                "severity": SeverityLevel.HIGH,
                "subcategories": ["user_add", "user_del", "user_mod", "group_add", "group_del", "password_change"]
            },
            "file_integrity": {
                "description": "File integrity monitoring",
                "category": "file",
                "severity": SeverityLevel.MEDIUM,
                "subcategories": ["file_created", "file_deleted", "file_modified", "file_moved", "permission_changed"]
            },
            "network_connection": {
                "description": "Network connection monitoring", 
                "category": "network",
                "severity": SeverityLevel.MEDIUM,
                "subcategories": ["connection_accept", "connection_refused", "port_scan", "suspicious_connection"]
            },
            "privilege_escalation": {
                "description": "Privilege escalation attempt",
                "category": "privilege_use",
                "severity": SeverityLevel.HIGH,
                "subcategories": ["sudo_command", "su_attempt", "setuid_execution", "capability_change"]
            },
            "kernel_module": {
                "description": "Kernel module activity",
                "category": "driver",
                "severity": SeverityLevel.HIGH,
                "subcategories": ["module_load", "module_unload", "suspicious_module"]
            }
        }
        
        # Common Linux processes and executables
        self.linux_processes = [
            "/bin/bash", "/bin/sh", "/usr/bin/python3", "/usr/bin/node", "/usr/bin/java",
            "/usr/bin/ssh", "/usr/bin/sudo", "/usr/bin/su", "/bin/systemctl", "/usr/bin/systemd",
            "/usr/sbin/nginx", "/usr/bin/apache2", "/usr/bin/mysql", "/usr/bin/docker",
            "/usr/bin/kubectl", "/opt/app/server", "/usr/local/bin/custom-app"
        ]
        
        # Linux system users
        self.system_users = [
            "root", "www-data", "mysql", "nginx", "docker", "systemd-network", "systemd-resolve",
            "admin", "developer", "operator", "service", "backup", "monitor"
        ]
        
        # File paths commonly monitored
        self.monitored_paths = [
            "/etc/passwd", "/etc/shadow", "/etc/sudoers", "/etc/ssh/sshd_config",
            "/var/log/auth.log", "/var/log/secure", "/etc/crontab", "/etc/hosts",
            "/bin/", "/usr/bin/", "/usr/sbin/", "/etc/systemd/", "/opt/", "/home/",
            "/var/www/", "/etc/nginx/", "/etc/apache2/", "/etc/mysql/"
        ]
    
    def generate_event(self) -> MockEvent:
        """Generate a single Auditbeat security event"""
        
        # Select random event type
        event_type = random.choice(list(self.audit_events.keys()))
        event_info = self.audit_events[event_type]
        
        # Generate basic audit event structure
        event_data = {
            "@timestamp": self._get_realistic_timestamp().isoformat(),
            "event": {
                "module": "auditd",
                "dataset": f"auditd.log",
                "action": event_info["description"],
                "category": [event_info["category"]],
                "type": ["info", "access"] if event_type in ["syscall", "file_integrity"] else ["start", "authentication"],
                "outcome": "success" if random.random() > 0.1 else "failure",
                "severity": event_info["severity"].value,
                "risk_score": self._calculate_risk_score(event_info["severity"])
            },
            "host": {
                "hostname": self._get_random_hostname(),
                "name": self._get_random_hostname(),
                "ip": [self._get_random_ip(private=True)],
                "mac": [self._generate_mac_address()],
                "os": {
                    "name": "Linux",
                    "family": "linux", 
                    "kernel": f"{random.randint(4, 6)}.{random.randint(1, 20)}.{random.randint(0, 15)}",
                    "platform": "linux",
                    "version": random.choice(["Ubuntu 20.04", "Ubuntu 22.04", "CentOS 7", "RHEL 8", "Debian 11"]),
                    "full": f"Linux {random.choice(['Ubuntu', 'CentOS', 'RHEL', 'Debian'])} {random.randint(7, 22)}.{random.randint(1, 10)}"
                },
                "architecture": random.choice(["x86_64", "aarch64"])
            },
            "agent": {
                "type": "auditbeat",
                "version": "8.11.0",
                "hostname": self._get_random_hostname(),
                "ephemeral_id": self._generate_uuid(),
                "id": self._generate_uuid()
            },
            "ecs": {
                "version": "8.0.0"
            }
        }
        
        # Add event-specific fields
        self._add_event_specific_fields(event_type, event_data, event_info)
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=datetime.fromisoformat(event_data["@timestamp"].replace("Z", "+00:00")).replace(tzinfo=None),
            event_type=MockDataType.AUDITBEAT_EVENT,
            severity=event_info["severity"],
            source="auditbeat",
            data=event_data
        )
    
    def _add_event_specific_fields(self, event_type: str, event_data: Dict[str, Any], event_info: Dict[str, Any]):
        """Add specific fields based on audit event type"""
        
        if event_type == "syscall":
            # System call auditing
            subcategory = random.choice(event_info["subcategories"])
            process_name = random.choice(self.linux_processes)
            
            event_data["process"] = {
                "name": process_name.split("/")[-1],
                "executable": process_name,
                "pid": random.randint(1000, 99999),
                "ppid": random.randint(1, 999),
                "args": [process_name] + self._generate_process_args(process_name),
                "working_directory": random.choice(["/home/user", "/var/www", "/opt", "/tmp"])
            }
            
            event_data["auditd"] = {
                "log": {
                    "record_type": "SYSCALL",
                    "syscall": subcategory,
                    "success": "yes" if event_data["event"]["outcome"] == "success" else "no",
                    "exit": 0 if event_data["event"]["outcome"] == "success" else random.randint(1, 255),
                    "pid": event_data["process"]["pid"],
                    "ppid": event_data["process"]["ppid"]
                }
            }
            
            if subcategory in ["connect", "accept", "bind"]:
                event_data["source"] = {
                    "ip": self._get_random_ip(private=random.choice([True, False])),
                    "port": random.randint(1024, 65535)
                }
                event_data["destination"] = {
                    "ip": self._get_random_ip(private=True),
                    "port": random.choice([22, 80, 443, 3306, 5432, 6379, 9200])
                }
        
        elif event_type == "user_login":
            # User authentication events
            subcategory = random.choice(event_info["subcategories"])
            username = random.choice(self.system_users + [self._get_random_username()])
            
            event_data["user"] = {
                "name": username,
                "id": str(random.randint(1000, 65535)),
                "group": {"name": random.choice(["users", "admin", "sudo", "wheel", "docker"])}
            }
            
            event_data["source"] = {
                "ip": self._get_random_ip(private=random.choice([True, False])),
                "port": random.randint(1024, 65535)
            }
            
            event_data["auditd"] = {
                "log": {
                    "record_type": "USER_LOGIN" if "login" in subcategory else "USER_LOGOUT",
                    "terminal": random.choice(["pts/0", "pts/1", "tty1", "console", ":0"]),
                    "ses": random.randint(1, 999),
                    "success": "yes" if event_data["event"]["outcome"] == "success" else "no"
                }
            }
            
            # Add failed login details
            if subcategory == "failed_login":
                event_data["event"]["reason"] = random.choice([
                    "Invalid credentials",
                    "Account locked",
                    "Too many attempts", 
                    "Account disabled",
                    "Password expired"
                ])
        
        elif event_type == "file_integrity":
            # File integrity monitoring
            subcategory = random.choice(event_info["subcategories"])
            file_path = random.choice(self.monitored_paths) + random.choice(["config.conf", "index.html", "app.log", "data.db", "script.sh"])
            
            event_data["file"] = {
                "path": file_path,
                "name": file_path.split("/")[-1],
                "directory": "/".join(file_path.split("/")[:-1]),
                "type": "file",
                "mode": oct(random.randint(0o644, 0o755)),
                "size": random.randint(100, 1000000),
                "mtime": self._get_realistic_timestamp().isoformat(),
                "owner": random.choice(self.system_users),
                "group": random.choice(["root", "www-data", "users", "admin"])
            }
            
            event_data["auditd"] = {
                "log": {
                    "record_type": "PATH",
                    "item": 0,
                    "name": file_path,
                    "nametype": "NORMAL",
                    "mode": event_data["file"]["mode"],
                    "ouid": random.randint(0, 65535),
                    "ogid": random.randint(0, 65535)
                }
            }
            
            if subcategory == "permission_changed":
                event_data["file"]["attributes"] = ["mode_changed"]
                event_data["auditd"]["log"]["record_type"] = "CHMOD"
        
        elif event_type == "privilege_escalation":
            # Privilege escalation events
            subcategory = random.choice(event_info["subcategories"])
            username = random.choice([self._get_random_username(), "admin", "developer"])
            
            event_data["user"] = {
                "name": username,
                "id": str(random.randint(1000, 65535)),
                "effective": {
                    "name": "root" if subcategory in ["sudo_command", "su_attempt"] else username,
                    "id": "0" if subcategory in ["sudo_command", "su_attempt"] else str(random.randint(1000, 65535))
                }
            }
            
            if subcategory == "sudo_command":
                command = random.choice([
                    "systemctl restart nginx",
                    "apt update && apt upgrade",
                    "docker ps -a",
                    "tail -f /var/log/auth.log", 
                    "chmod 755 /opt/app/deploy.sh",
                    "netstat -tulpn"
                ])
                
                event_data["process"] = {
                    "name": "sudo",
                    "executable": "/usr/bin/sudo",
                    "args": ["sudo"] + command.split(),
                    "command_line": f"sudo {command}"
                }
                
                event_data["auditd"] = {
                    "log": {
                        "record_type": "USER_CMD",
                        "cmd": command,
                        "terminal": random.choice(["pts/0", "pts/1", "console"])
                    }
                }
        
        # Add threat intelligence for suspicious events
        if event_data["event"]["outcome"] == "failure" or event_type in ["privilege_escalation", "kernel_module"]:
            event_data["threat"] = {
                "indicator": {
                    "type": random.choice(["file", "ip", "process", "user"]),
                    "description": f"Suspicious {event_type} activity detected"
                },
                "technique": {
                    "id": f"T{random.randint(1000, 1999)}",
                    "name": f"Suspicious {event_type.replace('_', ' ').title()}"
                }
            }
            
            event_data["risk"] = {
                "score": random.randint(50, 95),
                "score_norm": round(random.uniform(5.0, 9.5), 2)
            }
    
    def _generate_process_args(self, process_name: str) -> List[str]:
        """Generate realistic process arguments"""
        if "python" in process_name:
            return [random.choice(["-u", "-m"]), random.choice(["app.py", "server.py", "main.py"])]
        elif "java" in process_name:
            return ["-jar", "app.jar", f"-Xmx{random.randint(512, 2048)}m"]
        elif "docker" in process_name:
            return [random.choice(["ps", "run", "logs", "exec"]), "-it"]
        elif "ssh" in process_name:
            return [f"{self._get_random_username()}@{self._get_random_ip()}"]
        else:
            return [random.choice(["-v", "--help", "-c", "--config"])]
    
    def _generate_mac_address(self) -> str:
        """Generate a realistic MAC address"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def _calculate_risk_score(self, severity: SeverityLevel) -> int:
        """Calculate risk score based on severity"""
        risk_map = {
            SeverityLevel.LOW: random.randint(10, 30),
            SeverityLevel.MEDIUM: random.randint(40, 60),
            SeverityLevel.HIGH: random.randint(70, 85),
            SeverityLevel.CRITICAL: random.randint(90, 99)
        }
        return risk_map[severity]
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of Auditbeat security events"""
        return [self.generate_event() for _ in range(count)]
