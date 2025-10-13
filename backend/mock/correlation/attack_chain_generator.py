#!/usr/bin/env python3
"""
Intelligent Attack Chain Generator
Creates realistic, correlated security incidents that span multiple data sources
Simulates sophisticated attack scenarios for comprehensive testing and demos
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import mock generators
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from mock.generators.windows_events import WindowsEventGenerator
from mock.generators.security_alerts import SecurityAlertsGenerator
from mock.generators.authentication import AuthenticationEventGenerator
from mock.generators.network_logs import NetworkLogsGenerator
from mock.generators.process_logs import ProcessLogsGenerator
from mock.utils.base import MockEvent, MockDataType, SeverityLevel


class AttackPhase(Enum):
    """MITRE ATT&CK kill chain phases"""
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"


@dataclass
class AttackActor:
    """Attack actor profile"""
    name: str
    sophistication: str  # "low", "medium", "high", "advanced"
    preferred_techniques: List[str]
    target_types: List[str]
    geographic_origin: str
    motivation: str


@dataclass
class AttackScenario:
    """Complete attack scenario definition"""
    scenario_id: str
    name: str
    description: str
    actor: AttackActor
    phases: List[AttackPhase]
    duration_hours: int
    target_environment: str
    success_indicators: List[str]


@dataclass
class CorrelatedEvent:
    """Event with correlation metadata"""
    event: MockEvent
    scenario_id: str
    phase: AttackPhase
    sequence_number: int
    correlation_id: str
    related_events: List[str]
    indicators: Dict[str, Any]


class AttackChainGenerator:
    """Generates realistic, correlated attack chains"""
    
    def __init__(self):
        """Initialize the attack chain generator"""
        self.generators = {
            'windows': WindowsEventGenerator(),
            'security_alerts': SecurityAlertsGenerator(),
            'auth': AuthenticationEventGenerator(),
            'network': NetworkLogsGenerator(),
            'process': ProcessLogsGenerator()
        }
        
        # Define threat actors
        self.threat_actors = self._initialize_threat_actors()
        
        # Define attack scenarios
        self.attack_scenarios = self._initialize_attack_scenarios()
        
        # Common IoCs for correlation
        self.iocs = {
            'malicious_ips': [
                '203.0.113.10', '198.51.100.15', '192.0.2.20',
                '45.32.15.120', '104.248.50.75', '159.89.105.30'
            ],
            'c2_domains': [
                'malicious-c2.com', 'evil-command.net', 'bad-actor.org',
                'suspicious-domain.info', 'threat-server.biz'
            ],
            'malware_hashes': [
                'a1b2c3d4e5f6789012345678901234567890abcd',
                'deadbeef1234567890abcdef1234567890abcdef',
                'cafebabe9876543210fedcba9876543210fedcba'
            ],
            'attack_tools': [
                'mimikatz.exe', 'psexec.exe', 'cobalt-strike.exe',
                'metasploit.exe', 'empire.exe', 'bloodhound.exe'
            ]
        }
    
    def _initialize_threat_actors(self) -> List[AttackActor]:
        """Initialize threat actor profiles"""
        return [
            AttackActor(
                name="APT Shadow Dragon",
                sophistication="advanced",
                preferred_techniques=["T1055", "T1003", "T1021", "T1083"],
                target_types=["enterprise", "government", "critical_infrastructure"],
                geographic_origin="Unknown",
                motivation="espionage"
            ),
            AttackActor(
                name="Ransomware Gang Alpha",
                sophistication="high",
                preferred_techniques=["T1486", "T1490", "T1082", "T1018"],
                target_types=["healthcare", "education", "manufacturing"],
                geographic_origin="Eastern Europe",
                motivation="financial"
            ),
            AttackActor(
                name="Insider Threat Beta",
                sophistication="medium",
                preferred_techniques=["T1078", "T1005", "T1039", "T1114"],
                target_types=["any"],
                geographic_origin="Internal",
                motivation="financial"
            ),
            AttackActor(
                name="Script Kiddie Gamma",
                sophistication="low",
                preferred_techniques=["T1110", "T1059", "T1203", "T1566"],
                target_types=["small_business", "individual"],
                geographic_origin="Global",
                motivation="fame"
            ),
            AttackActor(
                name="Nation State Delta",
                sophistication="advanced",
                preferred_techniques=["T1195", "T1071", "T1027", "T1140"],
                target_types=["government", "defense", "technology"],
                geographic_origin="Classified",
                motivation="intelligence"
            )
        ]
    
    def _initialize_attack_scenarios(self) -> List[AttackScenario]:
        """Initialize attack scenario templates"""
        return [
            AttackScenario(
                scenario_id="apt_campaign_001",
                name="Advanced Persistent Threat Campaign",
                description="Sophisticated multi-stage attack targeting sensitive data",
                actor=self.threat_actors[0],  # APT Shadow Dragon
                phases=[
                    AttackPhase.RECONNAISSANCE,
                    AttackPhase.INITIAL_ACCESS,
                    AttackPhase.EXECUTION,
                    AttackPhase.PERSISTENCE,
                    AttackPhase.PRIVILEGE_ESCALATION,
                    AttackPhase.CREDENTIAL_ACCESS,
                    AttackPhase.DISCOVERY,
                    AttackPhase.LATERAL_MOVEMENT,
                    AttackPhase.COLLECTION,
                    AttackPhase.EXFILTRATION
                ],
                duration_hours=72,
                target_environment="enterprise",
                success_indicators=["data_exfiltration", "persistent_access", "credential_theft"]
            ),
            AttackScenario(
                scenario_id="ransomware_001",
                name="Ransomware Deployment Attack",
                description="Fast-moving ransomware attack with data encryption",
                actor=self.threat_actors[1],  # Ransomware Gang Alpha
                phases=[
                    AttackPhase.INITIAL_ACCESS,
                    AttackPhase.EXECUTION,
                    AttackPhase.DEFENSE_EVASION,
                    AttackPhase.DISCOVERY,
                    AttackPhase.LATERAL_MOVEMENT,
                    AttackPhase.IMPACT
                ],
                duration_hours=24,
                target_environment="enterprise",
                success_indicators=["file_encryption", "ransom_note", "system_disruption"]
            ),
            AttackScenario(
                scenario_id="insider_threat_001",
                name="Malicious Insider Data Theft",
                description="Authorized user abusing access to steal sensitive data",
                actor=self.threat_actors[2],  # Insider Threat Beta
                phases=[
                    AttackPhase.COLLECTION,
                    AttackPhase.EXFILTRATION
                ],
                duration_hours=48,
                target_environment="any",
                success_indicators=["unusual_data_access", "large_downloads", "off_hours_activity"]
            ),
            AttackScenario(
                scenario_id="bruteforce_001",
                name="Brute Force Authentication Attack",
                description="Automated credential stuffing and brute force attempts",
                actor=self.threat_actors[3],  # Script Kiddie Gamma
                phases=[
                    AttackPhase.RECONNAISSANCE,
                    AttackPhase.INITIAL_ACCESS,
                    AttackPhase.LATERAL_MOVEMENT
                ],
                duration_hours=12,
                target_environment="any",
                success_indicators=["successful_login", "account_lockouts", "suspicious_locations"]
            ),
            AttackScenario(
                scenario_id="supply_chain_001",
                name="Supply Chain Compromise",
                description="Nation-state attack via compromised software supply chain",
                actor=self.threat_actors[4],  # Nation State Delta
                phases=[
                    AttackPhase.INITIAL_ACCESS,
                    AttackPhase.EXECUTION,
                    AttackPhase.PERSISTENCE,
                    AttackPhase.DEFENSE_EVASION,
                    AttackPhase.COMMAND_CONTROL,
                    AttackPhase.COLLECTION
                ],
                duration_hours=168,  # 1 week
                target_environment="government",
                success_indicators=["supply_chain_infection", "backdoor_installation", "stealth_communication"]
            )
        ]
    
    def generate_attack_chain(
        self, 
        scenario: Optional[AttackScenario] = None,
        start_time: Optional[datetime] = None
    ) -> List[CorrelatedEvent]:
        """Generate a complete, correlated attack chain"""
        
        if scenario is None:
            scenario = random.choice(self.attack_scenarios)
        
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=random.randint(1, 24))
        
        print(f"🎯 Generating attack chain: {scenario.name}")
        print(f"   Actor: {scenario.actor.name}")
        print(f"   Duration: {scenario.duration_hours} hours")
        print(f"   Phases: {len(scenario.phases)}")
        
        correlation_id = str(uuid.uuid4())
        correlated_events = []
        
        # Generate victim profile
        victim_profile = self._generate_victim_profile()
        
        # Generate events for each phase
        current_time = start_time
        phase_duration = scenario.duration_hours / len(scenario.phases)
        
        for phase_index, phase in enumerate(scenario.phases):
            phase_events = self._generate_phase_events(
                scenario=scenario,
                phase=phase,
                phase_index=phase_index,
                victim_profile=victim_profile,
                correlation_id=correlation_id,
                start_time=current_time,
                duration_hours=phase_duration
            )
            
            correlated_events.extend(phase_events)
            current_time += timedelta(hours=phase_duration)
            
            print(f"   ✅ Phase {phase.value}: {len(phase_events)} events")
        
        print(f"🎯 Generated {len(correlated_events)} correlated events")
        return correlated_events
    
    def _generate_victim_profile(self) -> Dict[str, Any]:
        """Generate a consistent victim profile for the attack"""
        return {
            'primary_user': f"{random.choice(['john', 'alice', 'bob', 'carol', 'dave'])}.{random.choice(['smith', 'johnson', 'brown', 'davis', 'wilson'])}",
            'primary_host': f"WORKSTATION-{random.randint(10, 99)}",
            'primary_ip': f"192.168.1.{random.randint(100, 250)}",
            'domain': random.choice(['CORP', 'DOMAIN', 'ENTERPRISE']),
            'department': random.choice(['IT', 'Finance', 'HR', 'Operations', 'Executive']),
            'privilege_level': random.choice(['user', 'admin', 'power_user'])
        }
    
    def _generate_phase_events(
        self,
        scenario: AttackScenario,
        phase: AttackPhase,
        phase_index: int,
        victim_profile: Dict[str, Any],
        correlation_id: str,
        start_time: datetime,
        duration_hours: float
    ) -> List[CorrelatedEvent]:
        """Generate events for a specific attack phase"""
        
        events = []
        event_count = random.randint(2, 8)  # 2-8 events per phase
        
        for i in range(event_count):
            # Calculate event timestamp within phase duration
            phase_progress = i / event_count
            event_time = start_time + timedelta(hours=duration_hours * phase_progress)
            
            # Generate event based on phase
            base_event = self._generate_phase_specific_event(
                phase=phase,
                victim_profile=victim_profile,
                event_time=event_time,
                scenario=scenario
            )
            
            if base_event:
                # Add correlation metadata
                correlated_event = CorrelatedEvent(
                    event=base_event,
                    scenario_id=scenario.scenario_id,
                    phase=phase,
                    sequence_number=phase_index * 100 + i,
                    correlation_id=correlation_id,
                    related_events=[],  # Will be populated later
                    indicators=self._extract_indicators(base_event, phase)
                )
                
                events.append(correlated_event)
        
        # Add cross-references between events in the same phase
        for i, event in enumerate(events):
            event.related_events = [e.event.id for e in events if e != event]
        
        return events
    
    def _generate_phase_specific_event(
        self,
        phase: AttackPhase,
        victim_profile: Dict[str, Any],
        event_time: datetime,
        scenario: AttackScenario
    ) -> Optional[MockEvent]:
        """Generate a specific event for an attack phase"""
        
        if phase == AttackPhase.RECONNAISSANCE:
            return self._generate_reconnaissance_event(victim_profile, event_time)
        elif phase == AttackPhase.INITIAL_ACCESS:
            return self._generate_initial_access_event(victim_profile, event_time, scenario)
        elif phase == AttackPhase.EXECUTION:
            return self._generate_execution_event(victim_profile, event_time)
        elif phase == AttackPhase.PERSISTENCE:
            return self._generate_persistence_event(victim_profile, event_time)
        elif phase == AttackPhase.PRIVILEGE_ESCALATION:
            return self._generate_privilege_escalation_event(victim_profile, event_time)
        elif phase == AttackPhase.CREDENTIAL_ACCESS:
            return self._generate_credential_access_event(victim_profile, event_time)
        elif phase == AttackPhase.DISCOVERY:
            return self._generate_discovery_event(victim_profile, event_time)
        elif phase == AttackPhase.LATERAL_MOVEMENT:
            return self._generate_lateral_movement_event(victim_profile, event_time)
        elif phase == AttackPhase.COLLECTION:
            return self._generate_collection_event(victim_profile, event_time)
        elif phase == AttackPhase.EXFILTRATION:
            return self._generate_exfiltration_event(victim_profile, event_time)
        elif phase == AttackPhase.IMPACT:
            return self._generate_impact_event(victim_profile, event_time)
        else:
            return self._generate_generic_attack_event(victim_profile, event_time, phase)
    
    def _generate_reconnaissance_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate reconnaissance phase event"""
        # Network scanning or port scanning event
        event = self.generators['network'].generate_event()
        event_data = event.data
        
        # Customize for reconnaissance
        event_data['@timestamp'] = event_time.isoformat()
        event_data['event']['action'] = 'network_scan'
        event_data['event']['category'] = ['network', 'intrusion_detection']
        event_data['source']['ip'] = random.choice(self.iocs['malicious_ips'])
        event_data['destination']['ip'] = victim_profile['primary_ip']
        event_data['network']['protocol'] = 'tcp'
        
        # Add threat intel
        event_data['threat_intel'] = {
            'ioc_type': 'malicious_ip',
            'confidence': 'high',
            'first_seen': (event_time - timedelta(days=random.randint(1, 30))).isoformat()
        }
        
        event_data['severity'] = SeverityLevel.MEDIUM.value
        event_data['alert_type'] = 'reconnaissance_activity'
        event_data['threat_level'] = 'medium_threat'
        
        return event
    
    def _generate_initial_access_event(self, victim_profile: Dict, event_time: datetime, scenario: AttackScenario) -> MockEvent:
        """Generate initial access phase event"""
        if scenario.actor.sophistication == "low":
            # Brute force login
            event = self.generators['auth'].generate_event()
            event_data = event.data
            
            # Customize for brute force
            event_data['@timestamp'] = event_time.isoformat()
            event_data['event']['outcome'] = 'success'  # Successful after many attempts
            event_data['user']['name'] = victim_profile['primary_user']
            event_data['source']['ip'] = random.choice(self.iocs['malicious_ips'])
            event_data['authentication']['method'] = 'RemoteInteractive'
            event_data['authentication']['failure_count'] = random.randint(50, 200)
            
        else:
            # Spear phishing or malware delivery
            event = self.generators['security_alerts'].generate_event()
            event_data = event.data
            
            # Customize for sophisticated initial access
            event_data['@timestamp'] = event_time.isoformat()
            event_data['alert']['title'] = 'Suspicious email attachment execution'
            event_data['user']['name'] = victim_profile['primary_user']
            event_data['host']['name'] = victim_profile['primary_host']
            event_data['malware'] = {
                'family': 'APT-toolkit',
                'hash': random.choice(self.iocs['malware_hashes']),
                'file_path': f"C:\\Users\\{victim_profile['primary_user']}\\Downloads\\invoice.pdf.exe"
            }
        
        event_data['severity'] = SeverityLevel.HIGH.value
        event_data['alert_type'] = 'initial_access_attempt'
        event_data['threat_level'] = 'high_threat'
        
        return event
    
    def _generate_execution_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate execution phase event"""
        event = self.generators['process'].generate_event()
        event_data = event.data
        
        # Customize for malicious execution
        event_data['@timestamp'] = event_time.isoformat()
        event_data['process']['name'] = random.choice(self.iocs['attack_tools'])
        event_data['process']['command_line'] = f"{event_data['process']['name']} -stealth -bypass"
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['host']['name'] = victim_profile['primary_host']
        
        # Add MITRE technique
        event_data['mitre_attack'] = {
            'technique_id': 'T1059',
            'technique_name': 'Command and Scripting Interpreter',
            'tactic': 'execution'
        }
        
        event_data['severity'] = SeverityLevel.HIGH.value
        event_data['alert_type'] = 'malicious_execution'
        event_data['threat_level'] = 'high_threat'
        
        return event
    
    def _generate_persistence_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate persistence phase event"""
        event = self.generators['windows'].generate_event()
        event_data = event.data
        
        # Customize for persistence mechanism
        event_data['@timestamp'] = event_time.isoformat()
        event_data['winlog']['event_id'] = 4720  # User account created
        event_data['event']['action'] = 'Backdoor user account created'
        event_data['user']['name'] = f"svc_{random.choice(['update', 'backup', 'admin', 'temp'])}"
        event_data['host']['name'] = victim_profile['primary_host']
        
        # Registry modification for persistence
        event_data['registry'] = {
            'key': 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
            'value': 'WindowsUpdate',
            'data': f"C:\\Windows\\Temp\\{random.choice(self.iocs['attack_tools'])}"
        }
        
        event_data['severity'] = SeverityLevel.HIGH.value
        event_data['alert_type'] = 'persistence_mechanism'
        event_data['threat_level'] = 'high_threat'
        
        return event
    
    def _generate_privilege_escalation_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate privilege escalation phase event"""
        event = self.generators['security_alerts'].generate_event()
        event_data = event.data
        
        # Customize for privilege escalation
        event_data['@timestamp'] = event_time.isoformat()
        event_data['alert']['title'] = 'Privilege escalation attempt detected'
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['host']['name'] = victim_profile['primary_host']
        
        event_data['privilege_escalation'] = {
            'method': 'token_impersonation',
            'target_privilege': 'SYSTEM',
            'source_privilege': 'user',
            'technique': 'T1134'
        }
        
        event_data['severity'] = SeverityLevel.CRITICAL.value
        event_data['alert_type'] = 'privilege_escalation'
        event_data['threat_level'] = 'critical_threat'
        
        return event
    
    def _generate_credential_access_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate credential access phase event"""
        event = self.generators['process'].generate_event()
        event_data = event.data
        
        # Customize for credential dumping
        event_data['@timestamp'] = event_time.isoformat()
        event_data['process']['name'] = 'mimikatz.exe'
        event_data['process']['command_line'] = 'mimikatz.exe "sekurlsa::logonpasswords" "exit"'
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['host']['name'] = victim_profile['primary_host']
        
        event_data['credential_access'] = {
            'target': 'lsass_memory',
            'technique': 'T1003.001',
            'credentials_extracted': random.randint(5, 15)
        }
        
        event_data['severity'] = SeverityLevel.CRITICAL.value
        event_data['alert_type'] = 'credential_theft'
        event_data['threat_level'] = 'critical_threat'
        
        return event
    
    def _generate_discovery_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate discovery phase event"""
        event = self.generators['process'].generate_event()
        event_data = event.data
        
        # Customize for network discovery
        event_data['@timestamp'] = event_time.isoformat()
        event_data['process']['name'] = 'net.exe'
        event_data['process']['command_line'] = 'net view /domain'
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['host']['name'] = victim_profile['primary_host']
        
        event_data['discovery'] = {
            'technique': 'T1018',
            'target': 'network_shares',
            'systems_discovered': random.randint(10, 50)
        }
        
        event_data['severity'] = SeverityLevel.MEDIUM.value
        event_data['alert_type'] = 'reconnaissance_activity'
        event_data['threat_level'] = 'medium_threat'
        
        return event
    
    def _generate_lateral_movement_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate lateral movement phase event"""
        event = self.generators['auth'].generate_event()
        event_data = event.data
        
        # Customize for lateral movement
        event_data['@timestamp'] = event_time.isoformat()
        event_data['event']['outcome'] = 'success'
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['source']['ip'] = victim_profile['primary_ip']
        
        # Ensure destination field exists
        if 'destination' not in event_data:
            event_data['destination'] = {}
        event_data['destination']['ip'] = f"192.168.1.{random.randint(50, 99)}"
        event_data['authentication']['method'] = 'Network'
        
        event_data['lateral_movement'] = {
            'technique': 'T1021.001',
            'protocol': 'SMB',
            'target_host': f"SERVER-{random.randint(10, 99)}"
        }
        
        event_data['severity'] = SeverityLevel.HIGH.value
        event_data['alert_type'] = 'lateral_movement'
        event_data['threat_level'] = 'high_threat'
        
        return event
    
    def _generate_collection_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate collection phase event"""
        event = self.generators['process'].generate_event()
        event_data = event.data
        
        # Customize for data collection
        event_data['@timestamp'] = event_time.isoformat()
        event_data['process']['name'] = 'powershell.exe'
        event_data['process']['command_line'] = 'powershell.exe Get-ChildItem -Recurse -Include "*.docx","*.xlsx","*.pdf"'
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['host']['name'] = victim_profile['primary_host']
        
        event_data['collection'] = {
            'technique': 'T1005',
            'files_collected': random.randint(100, 1000),
            'data_size_mb': random.randint(50, 500)
        }
        
        event_data['severity'] = SeverityLevel.HIGH.value
        event_data['alert_type'] = 'data_collection'
        event_data['threat_level'] = 'high_threat'
        
        return event
    
    def _generate_exfiltration_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate exfiltration phase event"""
        event = self.generators['network'].generate_event()
        event_data = event.data
        
        # Customize for data exfiltration
        event_data['@timestamp'] = event_time.isoformat()
        event_data['event']['action'] = 'large_data_transfer'
        event_data['source']['ip'] = victim_profile['primary_ip']
        event_data['destination']['ip'] = random.choice(self.iocs['malicious_ips'])
        event_data['network']['bytes'] = random.randint(100_000_000, 1_000_000_000)  # 100MB - 1GB
        
        event_data['exfiltration'] = {
            'technique': 'T1041',
            'protocol': 'HTTPS',
            'destination': random.choice(self.iocs['c2_domains']),
            'encrypted': True
        }
        
        event_data['severity'] = SeverityLevel.CRITICAL.value
        event_data['alert_type'] = 'data_exfiltration'
        event_data['threat_level'] = 'critical_threat'
        
        return event
    
    def _generate_impact_event(self, victim_profile: Dict, event_time: datetime) -> MockEvent:
        """Generate impact phase event"""
        event = self.generators['security_alerts'].generate_event()
        event_data = event.data
        
        # Customize for ransomware impact
        event_data['@timestamp'] = event_time.isoformat()
        event_data['alert']['title'] = 'Ransomware encryption detected'
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['host']['name'] = victim_profile['primary_host']
        
        event_data['impact'] = {
            'technique': 'T1486',
            'files_encrypted': random.randint(1000, 10000),
            'ransom_note': 'README_DECRYPT.txt',
            'encryption_algorithm': 'AES-256'
        }
        
        event_data['severity'] = SeverityLevel.CRITICAL.value
        event_data['alert_type'] = 'ransomware_attack'
        event_data['threat_level'] = 'critical_threat'
        
        return event
    
    def _generate_generic_attack_event(self, victim_profile: Dict, event_time: datetime, phase: AttackPhase) -> MockEvent:
        """Generate generic attack event for any phase"""
        event = self.generators['security_alerts'].generate_event()
        event_data = event.data
        
        event_data['@timestamp'] = event_time.isoformat()
        event_data['alert']['title'] = f'{phase.value.replace("_", " ").title()} activity detected'
        event_data['user']['name'] = victim_profile['primary_user']
        event_data['host']['name'] = victim_profile['primary_host']
        
        return event
    
    def _extract_indicators(self, event: MockEvent, phase: AttackPhase) -> Dict[str, Any]:
        """Extract key indicators from an event"""
        indicators = {
            'phase': phase.value,
            'timestamp': event.data.get('@timestamp'),
            'severity': event.data.get('severity'),
            'alert_type': event.data.get('alert_type')
        }
        
        # Extract phase-specific indicators
        if 'user' in event.data:
            indicators['user'] = event.data['user'].get('name')
        
        if 'host' in event.data:
            indicators['host'] = event.data['host'].get('name')
        
        if 'source' in event.data:
            indicators['source_ip'] = event.data['source'].get('ip')
        
        if 'process' in event.data:
            indicators['process'] = event.data['process'].get('name')
        
        return indicators
    
    def generate_multiple_scenarios(self, count: int = 3) -> List[List[CorrelatedEvent]]:
        """Generate multiple concurrent attack scenarios"""
        print(f"🚀 Generating {count} concurrent attack scenarios...")
        
        scenarios = []
        base_time = datetime.now() - timedelta(hours=48)
        
        for i in range(count):
            # Stagger start times
            start_time = base_time + timedelta(hours=random.randint(0, 24))
            
            # Select different scenario for each
            scenario_template = self.attack_scenarios[i % len(self.attack_scenarios)]
            attack_chain = self.generate_attack_chain(scenario_template, start_time)
            
            scenarios.append(attack_chain)
        
        total_events = sum(len(chain) for chain in scenarios)
        print(f"✅ Generated {total_events} total correlated events across {count} scenarios")
        
        return scenarios
    
    def export_attack_timeline(self, correlated_events: List[CorrelatedEvent]) -> Dict[str, Any]:
        """Export attack timeline for visualization"""
        timeline = {
            'scenario_id': correlated_events[0].scenario_id if correlated_events else 'unknown',
            'total_events': len(correlated_events),
            'start_time': min(event.event.timestamp for event in correlated_events).isoformat(),
            'end_time': max(event.event.timestamp for event in correlated_events).isoformat(),
            'phases': [],
            'key_indicators': set(),
            'timeline_events': []
        }
        
        # Group by phase
        phases = {}
        for event in correlated_events:
            phase = event.phase.value
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(event)
        
        timeline['phases'] = [
            {
                'name': phase,
                'event_count': len(events),
                'start_time': min(e.event.timestamp for e in events).isoformat(),
                'end_time': max(e.event.timestamp for e in events).isoformat(),
                'severity': max(e.event.severity for e in events).value
            }
            for phase, events in phases.items()
        ]
        
        # Extract key indicators
        for event in correlated_events:
            for key, value in event.indicators.items():
                if value and key in ['user', 'host', 'source_ip', 'process']:
                    timeline['key_indicators'].add(f"{key}:{value}")
        
        timeline['key_indicators'] = list(timeline['key_indicators'])
        
        # Create timeline events
        for event in sorted(correlated_events, key=lambda e: e.event.timestamp):
            timeline['timeline_events'].append({
                'timestamp': event.event.timestamp.isoformat(),
                'phase': event.phase.value,
                'sequence': event.sequence_number,
                'event_type': event.event.event_type.value,
                'severity': event.event.severity.value,
                'description': event.event.data.get('event', {}).get('action', 'Unknown action'),
                'indicators': event.indicators
            })
        
        return timeline


def main():
    """Main function for testing attack chain generation"""
    print("🎯 ATTACK CHAIN GENERATOR TEST")
    print("=" * 50)
    
    generator = AttackChainGenerator()
    
    # Generate single attack scenario
    print("\n📊 Generating single APT attack scenario...")
    apt_scenario = generator.attack_scenarios[0]  # APT campaign
    attack_chain = generator.generate_attack_chain(apt_scenario)
    
    print(f"\n✅ Attack chain summary:")
    print(f"   Scenario: {apt_scenario.name}")
    print(f"   Events: {len(attack_chain)}")
    print(f"   Phases: {len(set(event.phase for event in attack_chain))}")
    print(f"   Duration: {apt_scenario.duration_hours} hours")
    
    # Generate timeline export
    timeline = generator.export_attack_timeline(attack_chain)
    
    print(f"\n📅 Timeline export:")
    print(f"   Total events: {timeline['total_events']}")
    print(f"   Time span: {timeline['start_time']} to {timeline['end_time']}")
    print(f"   Key indicators: {len(timeline['key_indicators'])}")
    
    # Generate multiple concurrent scenarios
    print("\n🔄 Generating multiple concurrent scenarios...")
    multiple_scenarios = generator.generate_multiple_scenarios(3)
    
    total_events = sum(len(chain) for chain in multiple_scenarios)
    print(f"✅ Generated {len(multiple_scenarios)} scenarios with {total_events} total events")
    
    return attack_chain, timeline


if __name__ == "__main__":
    main()
