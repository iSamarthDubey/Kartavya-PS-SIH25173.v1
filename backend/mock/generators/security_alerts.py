"""
Security Alerts Generator
Generates realistic SOC-style security alerts, incidents, and threat intelligence events
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class SecurityAlertsGenerator(BaseMockGenerator):
    """
    Generates realistic security alerts, incidents, and threat intelligence events
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Security alert types
        self.alert_types = {
            "malware_detection": {
                "description": "Malware detected on endpoint",
                "severity": SeverityLevel.HIGH,
                "category": "malware",
                "mitre_tactics": ["execution", "persistence", "defense_evasion"]
            },
            "data_exfiltration": {
                "description": "Potential data exfiltration detected", 
                "severity": SeverityLevel.CRITICAL,
                "category": "exfiltration",
                "mitre_tactics": ["exfiltration", "command_and_control"]
            },
            "privilege_escalation": {
                "description": "Privilege escalation attempt",
                "severity": SeverityLevel.HIGH,
                "category": "privilege_escalation",
                "mitre_tactics": ["privilege_escalation", "defense_evasion"]
            },
            "lateral_movement": {
                "description": "Lateral movement detected",
                "severity": SeverityLevel.HIGH,
                "category": "lateral_movement",
                "mitre_tactics": ["lateral_movement", "discovery"]
            },
            "phishing_email": {
                "description": "Phishing email detected",
                "severity": SeverityLevel.MEDIUM,
                "category": "initial_access",
                "mitre_tactics": ["initial_access", "execution"]
            },
            "suspicious_powershell": {
                "description": "Suspicious PowerShell execution",
                "severity": SeverityLevel.MEDIUM,
                "category": "execution",
                "mitre_tactics": ["execution", "defense_evasion"]
            },
            "credential_dumping": {
                "description": "Credential dumping activity",
                "severity": SeverityLevel.CRITICAL,
                "category": "credential_access",
                "mitre_tactics": ["credential_access", "defense_evasion"]
            },
            "suspicious_network_traffic": {
                "description": "Anomalous network traffic pattern",
                "severity": SeverityLevel.MEDIUM,
                "category": "command_and_control",
                "mitre_tactics": ["command_and_control", "exfiltration"]
            },
            "file_integrity_violation": {
                "description": "Critical file modification detected",
                "severity": SeverityLevel.HIGH,
                "category": "impact",
                "mitre_tactics": ["impact", "defense_evasion"]
            },
            "insider_threat": {
                "description": "Insider threat activity detected",
                "severity": SeverityLevel.HIGH,
                "category": "collection",
                "mitre_tactics": ["collection", "exfiltration"]
            }
        }
        
        # Malware families
        self.malware_families = [
            "Emotet", "TrickBot", "Ryuk", "Conti", "Maze", "REvil", "DarkSide",
            "Cobalt Strike", "Metasploit", "Empire", "Mimikatz", "BloodHound",
            "Zeus", "Dridex", "IcedID", "QakBot", "BazarLoader", "Ursnif"
        ]
        
        # IOC types and examples
        self.iocs = {
            "ip": ["192.168.1.100", "10.0.0.50", "172.16.1.25", "203.0.113.5", "198.51.100.10"],
            "domain": ["malicious.example.com", "c2.badactor.net", "phishing.suspicious.org", "evil.domain.com"],
            "hash": ["a1b2c3d4e5f6...", "9f8e7d6c5b4a...", "1a2b3c4d5e6f...", "f6e5d4c3b2a1..."],
            "url": ["http://malicious.com/payload", "https://phishing.net/login", "http://c2.evil.org/beacon"],
            "email": ["attacker@evil.com", "phishing@suspicious.net", "malware@badactor.org"]
        }
        
        # Common attack techniques (MITRE ATT&CK)
        self.attack_techniques = {
            "T1055": "Process Injection",
            "T1053": "Scheduled Task/Job",
            "T1059": "Command and Scripting Interpreter",
            "T1105": "Ingress Tool Transfer",
            "T1027": "Obfuscated Files or Information",
            "T1003": "OS Credential Dumping",
            "T1021": "Remote Services",
            "T1083": "File and Directory Discovery",
            "T1036": "Masquerading",
            "T1070": "Indicator Removal on Host"
        }
        
        # Security tools and sources
        self.security_tools = [
            "Windows Defender", "CrowdStrike Falcon", "SentinelOne", "Carbon Black",
            "Symantec Endpoint Protection", "McAfee", "Trend Micro", "ESET",
            "Splunk", "QRadar", "ArcSight", "LogRhythm", "Phantom", "Demisto"
        ]
        
        # Analyst information
        self.analysts = [
            {"name": "Alice Johnson", "tier": "L1", "shift": "day"},
            {"name": "Bob Smith", "tier": "L2", "shift": "evening"},
            {"name": "Carol Wilson", "tier": "L3", "shift": "night"},
            {"name": "David Brown", "tier": "L1", "shift": "day"},
            {"name": "Eve Garcia", "tier": "L2", "shift": "evening"}
        ]
    
    def generate_event(self) -> MockEvent:
        """Generate a single security alert event"""
        
        # Select alert type
        alert_type = random.choice(list(self.alert_types.keys()))
        alert_info = self.alert_types[alert_type]
        
        # Generate timestamp
        timestamp = self._get_realistic_timestamp()
        
        # Base alert structure
        event_data = {
            "@timestamp": timestamp.isoformat(),
            "alert": {
                "id": self._generate_uuid(),
                "title": alert_info["description"],
                "description": self._generate_alert_description(alert_type, alert_info),
                "severity": alert_info["severity"].value,
                "status": random.choice(["open", "in_progress", "resolved", "closed", "false_positive"]),
                "category": alert_info["category"],
                "subcategory": random.choice(["suspicious_activity", "policy_violation", "malware", "intrusion_attempt"]),
                "confidence": random.randint(60, 100),
                "risk_score": self._calculate_risk_score(alert_info["severity"]),
                "created": timestamp.isoformat(),
                "updated": (timestamp + timedelta(minutes=random.randint(1, 60))).isoformat()
            },
            "event": {
                "category": ["security"],
                "type": ["alert", "incident"],
                "action": f"security_alert_{alert_type}",
                "outcome": random.choice(["success", "failure", "unknown"]),
                "severity": alert_info["severity"].value
            },
            "host": {
                "name": self._get_random_hostname(),
                "ip": [self._get_random_ip(private=True)],
                "os": {
                    "name": random.choice(["Windows", "Linux", "macOS"]),
                    "family": random.choice(["windows", "linux", "darwin"]),
                    "version": self._get_random_os_version()
                },
                "architecture": random.choice(["x86_64", "x86", "arm64"])
            },
            "user": {
                "name": self._get_random_username(),
                "domain": random.choice(["CORP", "DOMAIN", "LOCAL"]),
                "role": random.choice(["user", "admin", "service", "guest"])
            },
            "observer": {
                "name": random.choice(self.security_tools),
                "type": "security_tool",
                "version": f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 99)}"
            }
        }
        
        # Add MITRE ATT&CK information
        tactics = alert_info.get("mitre_tactics", [])
        if tactics:
            technique_id = random.choice(list(self.attack_techniques.keys()))
            event_data["threat"] = {
                "tactic": random.choice(tactics),
                "technique": {
                    "id": technique_id,
                    "name": self.attack_techniques[technique_id]
                },
                "framework": "MITRE ATT&CK"
            }
        
        # Add IOCs
        self._add_iocs(event_data, alert_type)
        
        # Add alert-specific fields
        self._add_alert_specific_fields(alert_type, event_data, alert_info)
        
        # Add SOC workflow information
        self._add_soc_workflow(event_data, alert_info["severity"])
        
        # Add dashboard fields
        event_data["severity"] = alert_info["severity"].value
        event_data["status"] = event_data["alert"]["status"]
        
        # Classification based on severity
        if alert_info["severity"].value >= 4:  # CRITICAL
            event_data["alert_type"] = "critical_security_incident"
            event_data["threat_level"] = "critical_threat"
        elif alert_info["severity"].value >= 3:  # HIGH
            event_data["alert_type"] = "high_priority_alert"
            event_data["threat_level"] = "high_threat"
        elif alert_info["severity"].value >= 2:  # MEDIUM
            event_data["alert_type"] = "medium_priority_alert"
            event_data["threat_level"] = "medium_threat"
        else:  # LOW
            event_data["alert_type"] = "informational_alert"
            event_data["threat_level"] = "low_threat"
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=timestamp,
            event_type=MockDataType.SECURITY_ALERT,
            severity=alert_info["severity"],
            source="security_operations_center",
            data=event_data
        )
    
    def _generate_alert_description(self, alert_type: str, alert_info: Dict[str, Any]) -> str:
        """Generate detailed alert description"""
        
        descriptions = {
            "malware_detection": f"Malware family {random.choice(self.malware_families)} detected on endpoint",
            "data_exfiltration": f"Large data transfer ({random.randint(100, 5000)}MB) to external IP detected",
            "privilege_escalation": f"User attempted to elevate privileges using {random.choice(['runas', 'sudo', 'UAC bypass'])}",
            "lateral_movement": f"Unusual network activity between internal hosts detected",
            "phishing_email": f"Email with suspicious attachment or link detected",
            "suspicious_powershell": f"PowerShell executed with suspicious parameters: {random.choice(['-enc', '-windowstyle hidden', '-noprofile'])}",
            "credential_dumping": f"Attempt to dump credentials from {random.choice(['LSASS', 'SAM', 'memory'])} detected",
            "suspicious_network_traffic": f"Unusual traffic pattern to {random.choice(['known C2 server', 'suspicious domain', 'Tor exit node'])}",
            "file_integrity_violation": f"Critical system file {random.choice(['/etc/passwd', 'C:\\\\Windows\\\\System32\\\\ntdll.dll'])} was modified",
            "insider_threat": f"User accessed {random.randint(50, 500)} sensitive files in short timeframe"
        }
        
        return descriptions.get(alert_type, alert_info["description"])
    
    def _add_iocs(self, event_data: Dict[str, Any], alert_type: str):
        """Add Indicators of Compromise"""
        
        ioc_count = random.randint(1, 3)
        iocs = []
        
        for _ in range(ioc_count):
            ioc_type = random.choice(list(self.iocs.keys()))
            ioc_value = random.choice(self.iocs[ioc_type])
            
            iocs.append({
                "type": ioc_type,
                "value": ioc_value,
                "confidence": random.randint(70, 100),
                "first_seen": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "source": random.choice(["VirusTotal", "AlienVault", "Internal", "ThreatFox"])
            })
        
        event_data["threat_intel"] = {
            "iocs": iocs,
            "reputation_score": random.randint(1, 100),
            "threat_score": random.randint(50, 100)
        }
    
    def _add_alert_specific_fields(self, alert_type: str, event_data: Dict[str, Any], alert_info: Dict[str, Any]):
        """Add specific fields based on alert type"""
        
        if alert_type == "malware_detection":
            malware_family = random.choice(self.malware_families)
            event_data["malware"] = {
                "family": malware_family,
                "variant": f"{malware_family}.{random.choice(['A', 'B', 'C'])}",
                "file_path": self._get_random_file_path(),
                "file_hash": f"sha256:{random.randint(10**15, 10**16-1):x}",
                "detection_method": random.choice(["signature", "behavior", "heuristic", "machine_learning"])
            }
            
        elif alert_type == "data_exfiltration":
            event_data["exfiltration"] = {
                "data_size": random.randint(100, 5000),  # MB
                "file_types": random.sample(["pdf", "docx", "xlsx", "csv", "txt", "zip"], random.randint(1, 3)),
                "destination_ip": self._get_random_ip(private=False),
                "protocol": random.choice(["HTTP", "HTTPS", "FTP", "DNS"]),
                "compression_ratio": round(random.uniform(0.3, 0.8), 2)
            }
            
        elif alert_type == "privilege_escalation":
            event_data["privilege_escalation"] = {
                "method": random.choice(["UAC bypass", "token impersonation", "service exploitation", "kernel exploit"]),
                "target_privileges": random.choice(["SYSTEM", "Administrator", "root", "Domain Admin"]),
                "process_name": random.choice(["powershell.exe", "cmd.exe", "rundll32.exe", "schtasks.exe"]),
                "success": random.choice([True, False])
            }
            
        elif alert_type == "phishing_email":
            event_data["email"] = {
                "sender": random.choice(self.iocs["email"]),
                "subject": random.choice([
                    "Urgent: Account Verification Required",
                    "Invoice Attached",
                    "Security Alert: Suspicious Login",
                    "Document Shared With You"
                ]),
                "attachment_hash": f"md5:{random.randint(10**15, 10**16-1):x}",
                "recipient_count": random.randint(1, 100),
                "click_through_rate": round(random.uniform(0.01, 0.15), 3)
            }
        
        elif alert_type == "suspicious_powershell":
            event_data["powershell"] = {
                "command_line": random.choice([
                    "powershell.exe -enc aGVsbG8gd29ybGQ=",
                    "powershell.exe -windowstyle hidden -noprofile -command",
                    "powershell.exe Invoke-WebRequest -Uri http://malicious.com"
                ]),
                "execution_policy": random.choice(["Bypass", "Unrestricted", "RemoteSigned"]),
                "script_length": random.randint(100, 5000),
                "obfuscation_detected": random.choice([True, False])
            }
    
    def _add_soc_workflow(self, event_data: Dict[str, Any], severity: SeverityLevel):
        """Add SOC workflow and analyst information"""
        
        analyst = random.choice(self.analysts)
        
        event_data["soc"] = {
            "assigned_analyst": analyst["name"],
            "analyst_tier": analyst["tier"],
            "shift": analyst["shift"],
            "escalation_level": random.randint(0, 3),
            "investigation_status": random.choice(["new", "assigned", "investigating", "resolved", "escalated"]),
            "playbook_id": f"PB-{random.randint(1000, 9999)}",
            "sla_deadline": (datetime.now() + timedelta(hours=self._get_sla_hours(severity))).isoformat(),
            "tags": random.sample(["malware", "phishing", "insider", "apt", "ransomware", "credential_theft"], random.randint(1, 3))
        }
    
    def _get_sla_hours(self, severity: SeverityLevel) -> int:
        """Get SLA hours based on severity"""
        sla_map = {
            SeverityLevel.CRITICAL: 1,
            SeverityLevel.HIGH: 4,
            SeverityLevel.MEDIUM: 24,
            SeverityLevel.LOW: 72
        }
        return sla_map.get(severity, 24)
    
    def _calculate_risk_score(self, severity: SeverityLevel) -> int:
        """Calculate risk score based on severity"""
        base_scores = {
            SeverityLevel.CRITICAL: 90,
            SeverityLevel.HIGH: 70,
            SeverityLevel.MEDIUM: 50,
            SeverityLevel.LOW: 30
        }
        base = base_scores.get(severity, 50)
        return base + random.randint(-10, 10)
    
    def _get_random_os_version(self) -> str:
        """Generate random OS version"""
        versions = [
            "Windows 10 21H2", "Windows 11 22H2", "Windows Server 2019", "Windows Server 2022",
            "Ubuntu 20.04.3 LTS", "Ubuntu 22.04 LTS", "CentOS 7.9", "RHEL 8.5",
            "macOS 12.6 (Monterey)", "macOS 13.0 (Ventura)"
        ]
        return random.choice(versions)
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of security alert events"""
        return [self.generate_event() for _ in range(count)]
