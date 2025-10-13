"""
Network Security Logs Generator
Generates realistic network security events including firewalls, intrusion detection, VPN logs, etc.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..utils import BaseMockGenerator, MockEvent, MockDataType, SeverityLevel


class NetworkLogsGenerator(BaseMockGenerator):
    """
    Generates realistic network security logs from firewalls, IDS/IPS, VPN, routers, etc.
    """
    
    def __init__(self, seed: int = None):
        super().__init__(seed)
        
        # Network security event types
        self.network_events = {
            "firewall_block": {
                "description": "Firewall blocked connection",
                "severity": SeverityLevel.MEDIUM,
                "action": ["BLOCK", "DENY", "DROP"]
            },
            "firewall_allow": {
                "description": "Firewall allowed connection", 
                "severity": SeverityLevel.LOW,
                "action": ["ALLOW", "PERMIT", "ACCEPT"]
            },
            "intrusion_detection": {
                "description": "Intrusion detection alert",
                "severity": SeverityLevel.HIGH,
                "action": ["ALERT", "DETECT", "SIGNATURE_MATCH"]
            },
            "vpn_connect": {
                "description": "VPN connection established",
                "severity": SeverityLevel.LOW,
                "action": ["CONNECT", "LOGIN", "ESTABLISHED"]
            },
            "vpn_disconnect": {
                "description": "VPN connection terminated",
                "severity": SeverityLevel.LOW,
                "action": ["DISCONNECT", "LOGOUT", "TERMINATED"]
            },
            "ddos_attack": {
                "description": "DDoS attack detected",
                "severity": SeverityLevel.CRITICAL,
                "action": ["ATTACK", "FLOOD", "OVERWHELM"]
            },
            "port_scan": {
                "description": "Port scan detected",
                "severity": SeverityLevel.HIGH,
                "action": ["SCAN", "PROBE", "RECONNAISSANCE"]
            },
            "malware_communication": {
                "description": "Malware C&C communication",
                "severity": SeverityLevel.CRITICAL,
                "action": ["C2_CALLBACK", "BEACON", "EXFILTRATION"]
            },
            "bandwidth_anomaly": {
                "description": "Abnormal bandwidth usage",
                "severity": SeverityLevel.MEDIUM,
                "action": ["ANOMALY", "THRESHOLD_EXCEEDED", "UNUSUAL_TRAFFIC"]
            },
            "dns_tunneling": {
                "description": "DNS tunneling detected",
                "severity": SeverityLevel.HIGH,
                "action": ["TUNNEL", "COVERT_CHANNEL", "DATA_EXFILTRATION"]
            }
        }
        
        # Common network devices
        self.network_devices = [
            "Cisco-ASA-5520", "Palo-Alto-PA-3220", "Fortinet-FortiGate-100D",
            "pfSense-Firewall", "SonicWall-TZ570", "Checkpoint-1490",
            "Juniper-SRX300", "WatchGuard-T35", "Barracuda-F180",
            "Sophos-XG-310", "Router-Core-01", "Switch-Access-24"
        ]
        
        # Attack signatures and patterns
        self.attack_signatures = [
            "ET TROJAN Win32/Emotet", "ET MALWARE Zeus Banking Trojan",
            "GPL SCAN Nmap TCP", "ET SCAN Suspicious inbound to mySQL port 3306",
            "ET TROJAN Trickbot Checkin", "ET MALWARE Cobalt Strike Beacon",
            "GPL WEB_ATTACKS /etc/passwd", "ET EXPLOIT MS17-010 EternalBlue",
            "ET POLICY Dropbox DNS Lookup", "GPL ICMP_INFO PING *NIX"
        ]
        
        # VPN user pools
        self.vpn_users = [
            "john.doe", "alice.smith", "bob.wilson", "carol.brown", "dave.jones",
            "eve.garcia", "frank.miller", "grace.davis", "henry.rodriguez", "iris.martinez"
        ]
        
        # Common ports and services
        self.common_ports = {
            22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP", 
            110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS", 995: "POP3S",
            1433: "MSSQL", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 
            6379: "Redis", 8080: "HTTP-Alt", 9200: "Elasticsearch"
        }
    
    def generate_event(self) -> MockEvent:
        """Generate a single network security log event"""
        
        # Select event type
        event_type = random.choice(list(self.network_events.keys()))
        event_info = self.network_events[event_type]
        
        # Generate timestamp
        timestamp = self._get_realistic_timestamp()
        
        # Base event structure
        event_data = {
            "@timestamp": timestamp.isoformat(),
            "event": {
                "category": ["network", "security"],
                "type": ["connection", "denied"] if "block" in event_type or "attack" in event_type else ["connection", "allowed"],
                "action": random.choice(event_info["action"]),
                "outcome": "success" if event_type in ["firewall_allow", "vpn_connect"] else "failure",
                "severity": event_info["severity"].value
            },
            "host": {
                "name": random.choice(self.network_devices),
                "ip": self._get_random_ip(private=True),
                "type": "firewall" if "firewall" in event_type else "ids" if "intrusion" in event_type else "vpn" if "vpn" in event_type else "network"
            },
            "observer": {
                "name": random.choice(self.network_devices),
                "product": "Security Gateway",
                "type": "firewall",
                "version": f"{random.randint(6, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
            },
            "network": {
                "protocol": random.choice(["tcp", "udp", "icmp"]),
                "direction": random.choice(["inbound", "outbound", "internal"]),
                "bytes": random.randint(64, 65536),
                "packets": random.randint(1, 1000)
            },
            "source": {
                "ip": self._get_random_ip(private=random.choice([True, False])),
                "port": random.randint(1024, 65535),
                "bytes": random.randint(32, 8192),
                "packets": random.randint(1, 500)
            },
            "destination": {
                "ip": self._get_random_ip(private=True),
                "port": random.choice(list(self.common_ports.keys())),
                "bytes": random.randint(32, 8192),
                "packets": random.randint(1, 500)
            },
            "rule": {
                "name": f"SecurityRule_{random.randint(100, 999)}",
                "id": str(random.randint(1, 999)),
                "uuid": self._generate_uuid()
            }
        }
        
        # Add service information
        dest_port = event_data["destination"]["port"]
        if dest_port in self.common_ports:
            event_data["destination"]["service"] = self.common_ports[dest_port]
            event_data["network"]["application"] = self.common_ports[dest_port].lower()
        
        # Add event-specific fields
        self._add_event_specific_fields(event_type, event_data, event_info)
        
        # Add threat intelligence for malicious events
        if event_type in ["intrusion_detection", "ddos_attack", "malware_communication", "dns_tunneling", "port_scan"]:
            self._add_threat_intelligence(event_data, event_type)
        
        # Add severity and status fields for dashboard
        event_data["severity"] = event_info["severity"].value
        event_data["status"] = random.choice(["active", "resolved", "investigating"])
        
        # Classification based on severity
        if event_info["severity"].value >= 4:  # CRITICAL
            event_data["alert_type"] = "critical_security_incident"
            event_data["threat_level"] = "critical_network_threat"
        elif event_info["severity"].value >= 3:  # HIGH
            event_data["alert_type"] = "high_security_alert"
            event_data["threat_level"] = "high_network_threat"
        elif event_info["severity"].value >= 2:  # MEDIUM
            event_data["alert_type"] = "network_security_warning"
            event_data["threat_level"] = "medium_network_threat"
        else:  # LOW
            event_data["alert_type"] = "network_informational"
            event_data["threat_level"] = "low_network_activity"
        
        return MockEvent(
            id=self._generate_id(),
            timestamp=timestamp,
            event_type=MockDataType.NETWORK_LOG,
            severity=event_info["severity"],
            source="network_security",
            data=event_data
        )
    
    def _add_event_specific_fields(self, event_type: str, event_data: Dict[str, Any], event_info: Dict[str, Any]):
        """Add specific fields based on network event type"""
        
        if event_type in ["firewall_block", "firewall_allow"]:
            # Firewall specific fields
            event_data["firewall"] = {
                "rule_name": f"Rule_{random.randint(1, 999)}",
                "policy": random.choice(["CORPORATE", "DMZ", "GUEST", "INTERNAL"]),
                "zone_source": random.choice(["INTERNAL", "DMZ", "EXTERNAL", "GUEST"]),
                "zone_destination": random.choice(["INTERNAL", "DMZ", "EXTERNAL", "GUEST"]),
                "action": random.choice(event_info["action"])
            }
            
        elif event_type == "intrusion_detection":
            # IDS/IPS specific fields
            signature = random.choice(self.attack_signatures)
            event_data["ids"] = {
                "signature": signature,
                "signature_id": random.randint(1000000, 9999999),
                "classification": random.choice(["Trojan", "Exploit", "Scan", "Policy", "Malware"]),
                "priority": random.randint(1, 4),
                "confidence": random.randint(70, 100)
            }
            event_data["threat"] = {
                "technique": signature.split()[0] if " " in signature else signature,
                "category": random.choice(["malware", "exploit", "reconnaissance", "policy_violation"])
            }
            
        elif event_type in ["vpn_connect", "vpn_disconnect"]:
            # VPN specific fields
            user = random.choice(self.vpn_users)
            event_data["vpn"] = {
                "user": user,
                "client_version": f"OpenVPN {random.randint(2, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                "tunnel_type": random.choice(["OpenVPN", "IPSec", "L2TP", "PPTP", "WireGuard"]),
                "assigned_ip": self._get_random_ip(private=True),
                "session_duration": random.randint(60, 28800) if event_type == "vpn_disconnect" else 0,
                "bytes_sent": random.randint(1024, 1048576) if event_type == "vpn_disconnect" else 0,
                "bytes_received": random.randint(1024, 1048576) if event_type == "vpn_disconnect" else 0
            }
            event_data["user"] = {"name": user}
            
        elif event_type == "ddos_attack":
            # DDoS specific fields
            event_data["attack"] = {
                "type": random.choice(["SYN Flood", "UDP Flood", "HTTP Flood", "DNS Amplification", "ICMP Flood"]),
                "volume_pps": random.randint(10000, 1000000),  # packets per second
                "volume_bps": random.randint(1000000, 10000000000),  # bits per second
                "duration": random.randint(30, 3600),  # seconds
                "source_count": random.randint(100, 10000),  # number of source IPs
                "target": event_data["destination"]["ip"]
            }
            
        elif event_type == "port_scan":
            # Port scan specific fields
            event_data["scan"] = {
                "type": random.choice(["TCP SYN", "TCP Connect", "UDP", "XMAS", "NULL", "FIN"]),
                "ports_scanned": random.randint(10, 65535),
                "ports_open": random.randint(0, 20),
                "duration": random.randint(1, 3600),
                "technique": random.choice(["Sequential", "Random", "Stealth", "Decoy"])
            }
            
        elif event_type == "malware_communication":
            # Malware C&C specific fields
            event_data["malware"] = {
                "family": random.choice(["Emotet", "TrickBot", "Cobalt Strike", "Metasploit", "Empire"]),
                "c2_domain": random.choice(["malicious-c2.com", "bad-actor.net", "evil-command.org"]),
                "communication_type": random.choice(["Beacon", "Download", "Upload", "Command", "Heartbeat"]),
                "payload_size": random.randint(100, 10000),
                "encryption": random.choice(["TLS", "RC4", "AES", "None"])
            }
            
        elif event_type == "dns_tunneling":
            # DNS tunneling specific fields
            event_data["dns_tunnel"] = {
                "domain": random.choice(["tunnel.suspicious.com", "covert.badactor.net", "exfil.malware.org"]),
                "query_type": random.choice(["TXT", "A", "AAAA", "CNAME"]),
                "data_size": random.randint(50, 1000),
                "queries_count": random.randint(10, 1000),
                "encoding": random.choice(["Base64", "Hexadecimal", "Custom"])
            }
    
    def _add_threat_intelligence(self, event_data: Dict[str, Any], event_type: str):
        """Add threat intelligence information"""
        
        event_data["threat_intel"] = {
            "ioc_type": random.choice(["ip", "domain", "hash", "url"]),
            "confidence": random.choice(["high", "medium", "low"]),
            "source": random.choice(["VirusTotal", "AlienVault", "ThreatFox", "URLVoid", "Internal"]),
            "first_seen": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "last_seen": datetime.now().isoformat(),
            "reputation": random.choice(["malicious", "suspicious", "unknown"])
        }
        
        # Risk scoring
        event_data["risk"] = {
            "score": random.randint(60, 100),
            "factors": random.sample([
                "known_malware_ip", "suspicious_geolocation", "port_scan_source",
                "c2_communication", "dns_tunneling", "tor_exit_node"
            ], random.randint(1, 3))
        }
    
    def generate_batch(self, count: int = 10) -> List[MockEvent]:
        """Generate a batch of network security log events"""
        return [self.generate_event() for _ in range(count)]
