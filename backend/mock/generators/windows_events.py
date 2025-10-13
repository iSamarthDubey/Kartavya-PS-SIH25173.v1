"""
Dynamic Windows Event Log Generator
Generates realistic Windows security events matching real event log structure
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class WindowsEventGenerator(BaseMockGenerator):
    """
    Generates realistic Windows Event Log entries that match actual Windows Event Log schema
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Common Windows Event IDs and their descriptions
        self.event_types = {
            # Logon/Logoff Events
            4624: {"description": "An account was successfully logged on", "category": "Logon", "severity": SeverityLevel.LOW},
            4625: {"description": "An account failed to log on", "category": "Logon", "severity": SeverityLevel.MEDIUM},
            4634: {"description": "An account was logged off", "category": "Logon", "severity": SeverityLevel.LOW},
            4647: {"description": "User initiated logoff", "category": "Logon", "severity": SeverityLevel.LOW},
            4648: {"description": "A logon was attempted using explicit credentials", "category": "Logon", "severity": SeverityLevel.MEDIUM},
            
            # Account Management
            4720: {"description": "A user account was created", "category": "Account Management", "severity": SeverityLevel.MEDIUM},
            4722: {"description": "A user account was enabled", "category": "Account Management", "severity": SeverityLevel.MEDIUM},
            4725: {"description": "A user account was disabled", "category": "Account Management", "severity": SeverityLevel.MEDIUM},
            4726: {"description": "A user account was deleted", "category": "Account Management", "severity": SeverityLevel.HIGH},
            4738: {"description": "A user account was changed", "category": "Account Management", "severity": SeverityLevel.MEDIUM},
            
            # Privilege Use
            4672: {"description": "Special privileges assigned to new logon", "category": "Privilege Use", "severity": SeverityLevel.MEDIUM},
            4673: {"description": "A privileged service was called", "category": "Privilege Use", "severity": SeverityLevel.HIGH},
            
            # System Events
            4608: {"description": "Windows is starting up", "category": "System", "severity": SeverityLevel.LOW},
            4609: {"description": "Windows is shutting down", "category": "System", "severity": SeverityLevel.LOW},
            4616: {"description": "The system time was changed", "category": "System", "severity": SeverityLevel.MEDIUM},
            
            # Object Access
            4656: {"description": "A handle to an object was requested", "category": "Object Access", "severity": SeverityLevel.LOW},
            4658: {"description": "The handle to an object was closed", "category": "Object Access", "severity": SeverityLevel.LOW},
            4660: {"description": "An object was deleted", "category": "Object Access", "severity": SeverityLevel.MEDIUM},
            4663: {"description": "An attempt was made to access an object", "category": "Object Access", "severity": SeverityLevel.MEDIUM},
            
            # Process Tracking
            4688: {"description": "A new process has been created", "category": "Process Tracking", "severity": SeverityLevel.LOW},
            4689: {"description": "A process has exited", "category": "Process Tracking", "severity": SeverityLevel.LOW},
            
            # Security Policy Changes
            4719: {"description": "System audit policy was changed", "category": "Policy Change", "severity": SeverityLevel.HIGH},
            4739: {"description": "Domain Policy was changed", "category": "Policy Change", "severity": SeverityLevel.HIGH},
            
            # Suspicious Activities
            4771: {"description": "Kerberos pre-authentication failed", "category": "Account Logon", "severity": SeverityLevel.HIGH},
            4776: {"description": "The domain controller attempted to validate credentials", "category": "Account Logon", "severity": SeverityLevel.MEDIUM},
            5140: {"description": "A network share object was accessed", "category": "File Share", "severity": SeverityLevel.MEDIUM},
            5156: {"description": "Windows Firewall allowed a connection", "category": "Filtering Platform Connection", "severity": SeverityLevel.LOW},
        }
        
        # Logon types for event 4624/4625
        self.logon_types = {
            2: "Interactive",
            3: "Network", 
            4: "Batch",
            5: "Service",
            7: "Unlock", 
            8: "NetworkCleartext",
            9: "NewCredentials",
            10: "RemoteInteractive",
            11: "CachedInteractive"
        }
    
    def generate_event(self) -> MockEvent:
        """Generate a single Windows Event Log entry"""
        
        # Select random event type
        event_id = random.choice(list(self.event_types.keys()))
        event_info = self.event_types[event_id]
        
        # Generate basic event structure
        event_data = {
            "@timestamp": self._get_realistic_timestamp().isoformat(),
            "winlog": {
                "channel": "Security",
                "event_id": event_id,
                "provider_name": "Microsoft-Windows-Security-Auditing",
                "record_id": random.randint(100000, 999999),
                "computer_name": self._get_random_hostname(),
                "version": random.randint(1, 3),
                "level": self._get_log_level(event_info["severity"]),
                "task": event_info["category"],
                "opcode": "Info"
            },
            "event": {
                "action": event_info["description"],
                "category": [event_info["category"].lower().replace(" ", "_")],
                "code": event_id,
                "created": self._get_realistic_timestamp().isoformat(),
                "kind": "event",
                "module": "security",
                "outcome": "success" if random.random() > 0.2 else "failure",
                "provider": "Microsoft-Windows-Security-Auditing",
                "type": ["start", "info"]
            },
            "host": {
                "hostname": self._get_random_hostname(),
                "ip": self._get_random_ip(private=True),
                "name": self._get_random_hostname(),
                "os": {
                    "name": "Windows",
                    "family": "windows",
                    "version": random.choice(["10.0", "11.0", "2019", "2022"]),
                    "platform": "windows"
                }
            },
            "agent": {
                "type": "winlogbeat",
                "version": "9.1.4"
            }
        }
        
        # Add severity and status fields for dashboard calculations
        event_data["severity"] = event_info["severity"].value  # Add severity to data
        event_data["status"] = random.choice(["active", "resolved", "investigating"])  # Add status
        
        # Add security classification
        if event_info["severity"] in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            event_data["threat_level"] = "high"
            event_data["alert_type"] = "security_incident"
        else:
            event_data["threat_level"] = "normal"
            event_data["alert_type"] = "informational"
        
        # Add event-specific fields
        self._add_event_specific_fields(event_id, event_data)
        
        # Ensure all events have user field for consistency (if not already added by specific handler)
        if "user" not in event_data:
            event_data["user"] = {
                "name": self._get_random_username(),
                "domain": random.choice(["WORKGROUP", "DOMAIN", "CORP"])
            }
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=datetime.fromisoformat(event_data["@timestamp"].replace("Z", "+00:00")).replace(tzinfo=None),
            event_type=MockDataType.WINDOWS_EVENT,
            severity=event_info["severity"],
            source="winlogbeat",
            data=event_data
        )
    
    def _add_event_specific_fields(self, event_id: int, event_data: Dict[str, Any]):
        """Add specific fields based on event type"""
        
        if event_id in [4624, 4625, 4634, 4647]:  # Logon/Logoff events
            logon_type = random.choice(list(self.logon_types.keys()))
            event_data["winlog"]["event_data"] = {
                "SubjectUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserName": self._get_random_username(),
                "SubjectDomainName": random.choice(["WORKGROUP", "DOMAIN", "CORP"]),
                "SubjectLogonId": f"0x{random.randint(100000, 999999):x}",
                "TargetUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "TargetUserName": self._get_random_username(), 
                "TargetDomainName": random.choice(["WORKGROUP", "DOMAIN", "CORP"]),
                "LogonType": logon_type,
                "LogonProcessName": random.choice(["User32", "Advapi", "NtLmSsp", "Kerberos"]),
                "AuthenticationPackageName": random.choice(["NTLM", "Kerberos", "Negotiate"]),
                "WorkstationName": self._get_random_hostname(),
                "ProcessId": f"0x{random.randint(1000, 9999):x}",
                "ProcessName": "C:\\\\Windows\\\\System32\\\\winlogon.exe",
                "IpAddress": self._get_random_ip(private=random.choice([True, False])),
                "IpPort": random.randint(1024, 65535)
            }
            
            # Add user information
            event_data["user"] = {
                "name": event_data["winlog"]["event_data"]["TargetUserName"],
                "domain": event_data["winlog"]["event_data"]["TargetDomainName"]
            }
            
            # Add source IP
            event_data["source"] = {
                "ip": event_data["winlog"]["event_data"]["IpAddress"],
                "port": event_data["winlog"]["event_data"]["IpPort"]
            }
        
        elif event_id == 4688:  # Process creation
            process_info = self._get_random_process()
            event_data["winlog"]["event_data"] = {
                "SubjectUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserName": self._get_random_username(),
                "SubjectDomainName": random.choice(["WORKGROUP", "DOMAIN", "CORP"]),
                "NewProcessId": f"0x{process_info['pid']:x}",
                "NewProcessName": process_info["path"],
                "ParentProcessName": random.choice([
                    "C:\\\\Windows\\\\System32\\\\services.exe",
                    "C:\\\\Windows\\\\explorer.exe", 
                    "C:\\\\Windows\\\\System32\\\\svchost.exe"
                ]),
                "CommandLine": self._generate_command_line(process_info["name"]),
                "CreatorProcessId": f"0x{random.randint(1000, 9999):x}"
            }
            
            # Add user information for consistency
            event_data["user"] = {
                "name": event_data["winlog"]["event_data"]["SubjectUserName"],
                "domain": event_data["winlog"]["event_data"]["SubjectDomainName"]
            }
            
            # Add process information
            event_data["process"] = {
                "name": process_info["name"],
                "pid": process_info["pid"],
                "executable": process_info["path"],
                "command_line": event_data["winlog"]["event_data"]["CommandLine"]
            }
        
        elif event_id in [4720, 4722, 4725, 4726, 4738]:  # Account management
            event_data["winlog"]["event_data"] = {
                "SubjectUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserName": self._get_random_username(),
                "SubjectDomainName": random.choice(["WORKGROUP", "DOMAIN", "CORP"]),
                "TargetUserName": self._get_random_username(),
                "TargetDomainName": random.choice(["WORKGROUP", "DOMAIN", "CORP"]),
                "TargetSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}"
            }
            
            # Add user information
            event_data["user"] = {
                "name": event_data["winlog"]["event_data"]["TargetUserName"],
                "domain": event_data["winlog"]["event_data"]["TargetDomainName"]
            }
        
        elif event_id == 5156:  # Windows Firewall
            event_data["winlog"]["event_data"] = {
                "ProcessID": random.randint(1000, 9999),
                "Application": random.choice([
                    "C:\\\\Windows\\\\System32\\\\svchost.exe",
                    "C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe",
                    "C:\\\\Windows\\\\explorer.exe"
                ]),
                "Direction": random.choice(["Inbound", "Outbound"]),
                "SourceAddress": self._get_random_ip(private=random.choice([True, False])),
                "SourcePort": random.randint(1024, 65535),
                "DestAddress": self._get_random_ip(private=random.choice([True, False])),
                "DestPort": random.randint(80, 65535),
                "Protocol": random.choice([6, 17]),  # TCP or UDP
                "FilterRTID": random.randint(100000, 999999)
            }
            
            # Add user information for network activity
            event_data["user"] = {
                "name": self._get_random_username(),
                "domain": random.choice(["WORKGROUP", "DOMAIN", "CORP"])
            }
            
            # Add network information
            event_data["source"] = {
                "ip": event_data["winlog"]["event_data"]["SourceAddress"],
                "port": event_data["winlog"]["event_data"]["SourcePort"]
            }
            event_data["destination"] = {
                "ip": event_data["winlog"]["event_data"]["DestAddress"],
                "port": event_data["winlog"]["event_data"]["DestPort"]
            }
            event_data["network"] = {
                "protocol": "tcp" if event_data["winlog"]["event_data"]["Protocol"] == 6 else "udp",
                "direction": event_data["winlog"]["event_data"]["Direction"].lower()
            }
    
    def _generate_command_line(self, process_name: str) -> str:
        """Generate realistic command line for a process"""
        if process_name == "powershell.exe":
            commands = [
                "powershell.exe -ExecutionPolicy Bypass -File C:\\\\Scripts\\\\maintenance.ps1",
                "powershell.exe Get-Process | Where-Object {$_.CPU -gt 100}",
                "powershell.exe -Command Get-EventLog -LogName Security -Newest 50"
            ]
        elif process_name == "cmd.exe":
            commands = [
                "cmd.exe /c dir C:\\\\Windows\\\\System32",
                "cmd.exe /c ipconfig /all",
                "cmd.exe /c netstat -an"
            ]
        elif process_name == "chrome.exe":
            commands = [
                "\"C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe\" --no-sandbox",
                "\"C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe\" https://example.com"
            ]
        else:
            commands = [f"{process_name}"]
        
        return random.choice(commands)
    
    def _get_log_level(self, severity: SeverityLevel) -> str:
        """Convert severity to Windows log level"""
        level_map = {
            SeverityLevel.LOW: "Information",
            SeverityLevel.MEDIUM: "Warning", 
            SeverityLevel.HIGH: "Error",
            SeverityLevel.CRITICAL: "Critical"
        }
        return level_map[severity]
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of Windows events"""
        return [self.generate_event() for _ in range(count)]
