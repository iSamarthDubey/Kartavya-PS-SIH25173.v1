#!/usr/bin/env python3
"""
🧠 Enhanced Security NLP Entity Recognition
===========================================
Advanced entity extraction for security-specific terms including:
- MITRE ATT&CK techniques and tactics
- CVE identifiers and vulnerability scores
- Threat actor names and campaigns
- IOCs (IPs, domains, hashes, file paths)
- Security tools and products
- Attack indicators and patterns
"""

import re
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import asyncio


class EntityType(Enum):
    """Types of security entities we can extract"""
    MITRE_TECHNIQUE = "mitre_technique"
    MITRE_TACTIC = "mitre_tactic"
    CVE_ID = "cve_id"
    THREAT_ACTOR = "threat_actor"
    MALWARE_FAMILY = "malware_family"
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    FILE_HASH = "file_hash"
    FILE_PATH = "file_path"
    EMAIL_ADDRESS = "email_address"
    URL = "url"
    SECURITY_TOOL = "security_tool"
    ATTACK_PATTERN = "attack_pattern"
    VULNERABILITY_SCORE = "vulnerability_score"
    PORT_NUMBER = "port_number"
    PROCESS_NAME = "process_name"
    USERNAME = "username"
    HOSTNAME = "hostname"


@dataclass
class SecurityEntity:
    """Represents an extracted security entity"""
    entity_type: EntityType
    value: str
    confidence: float
    position: Tuple[int, int]  # Start and end position in text
    context: str
    metadata: Dict[str, Any] = None


class SecurityNLPRecognizer:
    """Advanced NLP recognizer for security-specific entities"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.knowledge_base = self._initialize_knowledge_base()
        self.confidence_thresholds = {
            EntityType.MITRE_TECHNIQUE: 0.95,
            EntityType.CVE_ID: 0.98,
            EntityType.THREAT_ACTOR: 0.85,
            EntityType.IP_ADDRESS: 0.95,
            EntityType.DOMAIN: 0.90,
            EntityType.FILE_HASH: 0.95,
            EntityType.MALWARE_FAMILY: 0.80,
            EntityType.SECURITY_TOOL: 0.85,
        }
    
    def _initialize_patterns(self) -> Dict[EntityType, List[str]]:
        """Initialize regex patterns for entity recognition"""
        return {
            EntityType.MITRE_TECHNIQUE: [
                r'\b[Tt](\d{4})(?:\.(\d{3}))?\b',  # T1055.001 format
                r'\bATT&CK\s+[Tt](\d{4})\b',
                r'\bMITRE\s+[Tt](\d{4})\b'
            ],
            EntityType.CVE_ID: [
                r'\bCVE-\d{4}-\d{4,}\b',
                r'\bcve-\d{4}-\d{4,}\b'
            ],
            EntityType.IP_ADDRESS: [
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'  # IPv6
            ],
            EntityType.DOMAIN: [
                r'\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}\b'
            ],
            EntityType.FILE_HASH: [
                r'\b[a-fA-F0-9]{32}\b',  # MD5
                r'\b[a-fA-F0-9]{40}\b',  # SHA1
                r'\b[a-fA-F0-9]{64}\b'   # SHA256
            ],
            EntityType.EMAIL_ADDRESS: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            EntityType.URL: [
                r'\bhttps?://[^\s<>"{}|\\^`\[\]]+\b'
            ],
            EntityType.FILE_PATH: [
                r'\b[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*\b',  # Windows paths
                r'\b/(?:[^/\s]+/)*[^/\s]*\b'  # Unix paths
            ],
            EntityType.PORT_NUMBER: [
                r'\bport\s+(\d{1,5})\b',
                r':(\d{1,5})\b'
            ],
            EntityType.PROCESS_NAME: [
                r'\b\w+\.exe\b',
                r'\b\w+\.dll\b',
                r'\b\w+\.bin\b'
            ]
        }
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize security knowledge base"""
        return {
            "mitre_techniques": {
                "T1055": {"name": "Process Injection", "tactic": "Defense Evasion"},
                "T1059": {"name": "Command and Scripting Interpreter", "tactic": "Execution"},
                "T1003": {"name": "OS Credential Dumping", "tactic": "Credential Access"},
                "T1021": {"name": "Remote Services", "tactic": "Lateral Movement"},
                "T1566": {"name": "Phishing", "tactic": "Initial Access"},
                "T1070": {"name": "Indicator Removal on Host", "tactic": "Defense Evasion"},
                "T1486": {"name": "Data Encrypted for Impact", "tactic": "Impact"},
                "T1078": {"name": "Valid Accounts", "tactic": "Defense Evasion"},
                "T1071": {"name": "Application Layer Protocol", "tactic": "Command and Control"},
                "T1053": {"name": "Scheduled Task/Job", "tactic": "Execution"},
                "T1027": {"name": "Obfuscated Files or Information", "tactic": "Defense Evasion"},
                "T1105": {"name": "Ingress Tool Transfer", "tactic": "Command and Control"},
                "T1083": {"name": "File and Directory Discovery", "tactic": "Discovery"},
                "T1036": {"name": "Masquerading", "tactic": "Defense Evasion"},
                "T1204": {"name": "User Execution", "tactic": "Execution"},
                "T1052": {"name": "Exfiltration Over Physical Medium", "tactic": "Exfiltration"},
                "T1005": {"name": "Data from Local System", "tactic": "Collection"}
            },
            "threat_actors": {
                "APT29": {"aliases": ["Cozy Bear", "The Dukes"], "country": "Russia"},
                "APT28": {"aliases": ["Fancy Bear", "Sofacy"], "country": "Russia"},
                "Lazarus Group": {"aliases": ["HIDDEN COBRA"], "country": "North Korea"},
                "APT1": {"aliases": ["Comment Crew"], "country": "China"},
                "FIN7": {"aliases": ["Carbanak"], "focus": "Financial"},
                "Equation Group": {"aliases": ["NSA TAO"], "country": "USA"},
                "Sandworm": {"aliases": ["VoodooBear"], "country": "Russia"},
                "APT40": {"aliases": ["Leviathan"], "country": "China"},
                "Turla": {"aliases": ["Snake", "Uroburos"], "country": "Russia"},
                "Carbanak": {"aliases": ["FIN7"], "focus": "Financial"}
            },
            "malware_families": {
                "Emotet": {"type": "Banking Trojan", "first_seen": "2014"},
                "TrickBot": {"type": "Banking Trojan", "first_seen": "2016"},
                "Ryuk": {"type": "Ransomware", "first_seen": "2018"},
                "Conti": {"type": "Ransomware", "first_seen": "2020"},
                "Maze": {"type": "Ransomware", "first_seen": "2019"},
                "REvil": {"type": "Ransomware", "first_seen": "2019"},
                "DarkSide": {"type": "Ransomware", "first_seen": "2020"},
                "Cobalt Strike": {"type": "Penetration Testing Tool", "first_seen": "2012"},
                "Mimikatz": {"type": "Credential Dumper", "first_seen": "2011"},
                "BloodHound": {"type": "AD Reconnaissance", "first_seen": "2016"},
                "Zeus": {"type": "Banking Trojan", "first_seen": "2006"},
                "Dridex": {"type": "Banking Trojan", "first_seen": "2014"}
            },
            "security_tools": [
                "Windows Defender", "CrowdStrike Falcon", "SentinelOne", "Carbon Black",
                "Symantec Endpoint Protection", "McAfee", "Trend Micro", "ESET",
                "Splunk", "QRadar", "ArcSight", "LogRhythm", "Phantom", "Demisto",
                "Wireshark", "Nmap", "Metasploit", "Burp Suite", "OWASP ZAP",
                "Nessus", "OpenVAS", "Qualys", "Rapid7", "Tenable"
            ],
            "attack_patterns": [
                "Living off the land", "Fileless attack", "Supply chain attack",
                "Watering hole attack", "Spear phishing", "SQL injection",
                "Cross-site scripting", "Buffer overflow", "Privilege escalation",
                "Lateral movement", "Data exfiltration", "Command and control",
                "Persistence mechanism", "Defense evasion", "Credential dumping"
            ]
        }
    
    def extract_entities(self, text: str) -> List[SecurityEntity]:
        """Extract all security entities from text"""
        entities = []
        text_lower = text.lower()
        
        # Extract pattern-based entities
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = SecurityEntity(
                        entity_type=entity_type,
                        value=match.group(0),
                        confidence=0.9,  # Base confidence for regex matches
                        position=(match.start(), match.end()),
                        context=self._get_context(text, match.start(), match.end()),
                        metadata={"pattern": pattern}
                    )
                    entities.append(entity)
        
        # Extract knowledge base entities
        entities.extend(self._extract_threat_actors(text))
        entities.extend(self._extract_malware_families(text))
        entities.extend(self._extract_security_tools(text))
        entities.extend(self._extract_attack_patterns(text))
        
        # Enhance entities with metadata
        entities = self._enhance_entities(entities)
        
        # Filter by confidence thresholds
        entities = self._filter_by_confidence(entities)
        
        # Remove duplicates and overlaps
        entities = self._remove_duplicates(entities)
        
        return sorted(entities, key=lambda x: x.position[0])
    
    def _extract_threat_actors(self, text: str) -> List[SecurityEntity]:
        """Extract threat actor names from text"""
        entities = []
        text_lower = text.lower()
        
        for actor, info in self.knowledge_base["threat_actors"].items():
            # Check main name
            if actor.lower() in text_lower:
                start_pos = text_lower.find(actor.lower())
                entity = SecurityEntity(
                    entity_type=EntityType.THREAT_ACTOR,
                    value=actor,
                    confidence=0.85,
                    position=(start_pos, start_pos + len(actor)),
                    context=self._get_context(text, start_pos, start_pos + len(actor)),
                    metadata=info
                )
                entities.append(entity)
            
            # Check aliases
            for alias in info.get("aliases", []):
                if alias.lower() in text_lower:
                    start_pos = text_lower.find(alias.lower())
                    entity = SecurityEntity(
                        entity_type=EntityType.THREAT_ACTOR,
                        value=alias,
                        confidence=0.80,  # Slightly lower confidence for aliases
                        position=(start_pos, start_pos + len(alias)),
                        context=self._get_context(text, start_pos, start_pos + len(alias)),
                        metadata={**info, "primary_name": actor}
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_malware_families(self, text: str) -> List[SecurityEntity]:
        """Extract malware family names from text"""
        entities = []
        text_lower = text.lower()
        
        for malware, info in self.knowledge_base["malware_families"].items():
            if malware.lower() in text_lower:
                start_pos = text_lower.find(malware.lower())
                entity = SecurityEntity(
                    entity_type=EntityType.MALWARE_FAMILY,
                    value=malware,
                    confidence=0.80,
                    position=(start_pos, start_pos + len(malware)),
                    context=self._get_context(text, start_pos, start_pos + len(malware)),
                    metadata=info
                )
                entities.append(entity)
        
        return entities
    
    def _extract_security_tools(self, text: str) -> List[SecurityEntity]:
        """Extract security tool names from text"""
        entities = []
        text_lower = text.lower()
        
        for tool in self.knowledge_base["security_tools"]:
            if tool.lower() in text_lower:
                start_pos = text_lower.find(tool.lower())
                entity = SecurityEntity(
                    entity_type=EntityType.SECURITY_TOOL,
                    value=tool,
                    confidence=0.85,
                    position=(start_pos, start_pos + len(tool)),
                    context=self._get_context(text, start_pos, start_pos + len(tool)),
                    metadata={"category": self._categorize_security_tool(tool)}
                )
                entities.append(entity)
        
        return entities
    
    def _extract_attack_patterns(self, text: str) -> List[SecurityEntity]:
        """Extract attack pattern descriptions from text"""
        entities = []
        text_lower = text.lower()
        
        for pattern in self.knowledge_base["attack_patterns"]:
            if pattern.lower() in text_lower:
                start_pos = text_lower.find(pattern.lower())
                entity = SecurityEntity(
                    entity_type=EntityType.ATTACK_PATTERN,
                    value=pattern,
                    confidence=0.75,
                    position=(start_pos, start_pos + len(pattern)),
                    context=self._get_context(text, start_pos, start_pos + len(pattern)),
                    metadata={"category": "attack_technique"}
                )
                entities.append(entity)
        
        return entities
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for an entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _enhance_entities(self, entities: List[SecurityEntity]) -> List[SecurityEntity]:
        """Enhance entities with additional metadata"""
        enhanced = []
        
        for entity in entities:
            # Enhance MITRE techniques
            if entity.entity_type == EntityType.MITRE_TECHNIQUE:
                technique_id = entity.value.upper()
                if technique_id.startswith('T') and technique_id[1:].replace('.', '').isdigit():
                    base_technique = technique_id.split('.')[0]
                    if base_technique in self.knowledge_base["mitre_techniques"]:
                        entity.metadata = self.knowledge_base["mitre_techniques"][base_technique]
                        entity.confidence = 0.95
            
            # Enhance CVE IDs
            elif entity.entity_type == EntityType.CVE_ID:
                entity.confidence = 0.98
                entity.metadata = {"type": "vulnerability", "format": "CVE-YYYY-NNNN"}
            
            # Enhance IP addresses with geolocation hints
            elif entity.entity_type == EntityType.IP_ADDRESS:
                entity.metadata = {
                    "type": "ipv4" if "." in entity.value else "ipv6",
                    "private": self._is_private_ip(entity.value)
                }
            
            enhanced.append(entity)
        
        return enhanced
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is in private range"""
        private_ranges = [
            "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
            "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.",
            "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "192.168."
        ]
        return any(ip.startswith(range_prefix) for range_prefix in private_ranges)
    
    def _categorize_security_tool(self, tool: str) -> str:
        """Categorize security tool by type"""
        categories = {
            "endpoint": ["Windows Defender", "CrowdStrike Falcon", "SentinelOne", "Carbon Black"],
            "siem": ["Splunk", "QRadar", "ArcSight", "LogRhythm"],
            "soar": ["Phantom", "Demisto"],
            "network": ["Wireshark", "Nmap"],
            "vulnerability": ["Nessus", "OpenVAS", "Qualys"]
        }
        
        for category, tools in categories.items():
            if tool in tools:
                return category
        return "security_tool"
    
    def _filter_by_confidence(self, entities: List[SecurityEntity]) -> List[SecurityEntity]:
        """Filter entities by confidence threshold"""
        filtered = []
        for entity in entities:
            threshold = self.confidence_thresholds.get(entity.entity_type, 0.7)
            if entity.confidence >= threshold:
                filtered.append(entity)
        return filtered
    
    def _remove_duplicates(self, entities: List[SecurityEntity]) -> List[SecurityEntity]:
        """Remove duplicate and overlapping entities"""
        # Sort by position
        entities.sort(key=lambda x: (x.position[0], x.position[1]))
        
        cleaned = []
        for entity in entities:
            # Check for overlaps with existing entities
            overlaps = False
            for existing in cleaned:
                if (entity.position[0] < existing.position[1] and 
                    entity.position[1] > existing.position[0]):
                    # There's an overlap - keep the higher confidence one
                    if entity.confidence > existing.confidence:
                        cleaned.remove(existing)
                    else:
                        overlaps = True
                        break
            
            if not overlaps:
                cleaned.append(entity)
        
        return cleaned
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive analysis of security text"""
        start_time = time.time()
        
        entities = self.extract_entities(text)
        
        analysis = {
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": (time.time() - start_time) * 1000,
            "total_entities": len(entities),
            "entities": [
                {
                    "type": entity.entity_type.value,
                    "value": entity.value,
                    "confidence": entity.confidence,
                    "position": entity.position,
                    "context": entity.context,
                    "metadata": entity.metadata or {}
                }
                for entity in entities
            ],
            "entity_summary": self._create_entity_summary(entities),
            "threat_indicators": self._identify_threat_indicators(entities),
            "mitre_mapping": self._create_mitre_mapping(entities)
        }
        
        return analysis
    
    def _create_entity_summary(self, entities: List[SecurityEntity]) -> Dict[str, int]:
        """Create summary of entity types found"""
        summary = {}
        for entity in entities:
            entity_type = entity.entity_type.value
            summary[entity_type] = summary.get(entity_type, 0) + 1
        return summary
    
    def _identify_threat_indicators(self, entities: List[SecurityEntity]) -> Dict[str, Any]:
        """Identify threat indicators from entities"""
        indicators = {
            "iocs": [],
            "threat_actors": [],
            "malware": [],
            "attack_techniques": [],
            "severity_score": 0
        }
        
        for entity in entities:
            if entity.entity_type in [EntityType.IP_ADDRESS, EntityType.DOMAIN, EntityType.FILE_HASH, EntityType.URL]:
                indicators["iocs"].append({
                    "type": entity.entity_type.value,
                    "value": entity.value,
                    "confidence": entity.confidence
                })
            
            elif entity.entity_type == EntityType.THREAT_ACTOR:
                indicators["threat_actors"].append({
                    "name": entity.value,
                    "metadata": entity.metadata
                })
                indicators["severity_score"] += 30  # Threat actors are high severity
            
            elif entity.entity_type == EntityType.MALWARE_FAMILY:
                indicators["malware"].append({
                    "family": entity.value,
                    "metadata": entity.metadata
                })
                indicators["severity_score"] += 25
            
            elif entity.entity_type == EntityType.MITRE_TECHNIQUE:
                indicators["attack_techniques"].append({
                    "technique": entity.value,
                    "metadata": entity.metadata
                })
                indicators["severity_score"] += 20
        
        return indicators
    
    def _create_mitre_mapping(self, entities: List[SecurityEntity]) -> Dict[str, Any]:
        """Create MITRE ATT&CK mapping from entities"""
        mitre_data = {
            "techniques": [],
            "tactics": set(),
            "matrix_coverage": {}
        }
        
        for entity in entities:
            if entity.entity_type == EntityType.MITRE_TECHNIQUE and entity.metadata:
                technique_data = {
                    "id": entity.value,
                    "name": entity.metadata.get("name"),
                    "tactic": entity.metadata.get("tactic"),
                    "confidence": entity.confidence
                }
                mitre_data["techniques"].append(technique_data)
                
                if entity.metadata.get("tactic"):
                    mitre_data["tactics"].add(entity.metadata.get("tactic"))
        
        mitre_data["tactics"] = list(mitre_data["tactics"])
        return mitre_data


def test_enhanced_nlp():
    """Test the enhanced NLP entity recognition"""
    print("🧠 ENHANCED SECURITY NLP ENTITY RECOGNITION")
    print("=" * 60)
    
    recognizer = SecurityNLPRecognizer()
    
    # Test cases with various security content
    test_cases = [
        "APT29 used T1055 process injection to deploy Cobalt Strike beacon connecting to malicious-c2.evil.com",
        "CVE-2021-44228 Log4j vulnerability exploited by Lazarus Group using 192.168.1.100 as staging server",
        "Emotet malware sample hash a1b2c3d4e5f6789012345678901234567890abcdef detected by Windows Defender",
        "Lateral movement using T1021.002 SMB/Windows Admin Shares to compromise IT-SERVER-01 from attacker@evil.com",
        "Ryuk ransomware executed powershell.exe with encoded command, files encrypted with .locked extension",
        "Hunt for MITRE ATT&CK technique T1003.001 LSASS memory credential dumping on domain controllers",
        "Suspicious network traffic to C2 domain update-service.company-cdn.net on port 443 using HTTPS",
        "FIN7 threat actor deployed Carbanak malware targeting financial institutions via spear phishing"
    ]
    
    total_entities = 0
    total_processing_time = 0
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}:")
        print(f"Text: {test_text}")
        print("-" * 50)
        
        analysis = recognizer.analyze_text(test_text)
        
        print(f"⏱️  Processing Time: {analysis['processing_time_ms']:.2f}ms")
        print(f"📊 Total Entities: {analysis['total_entities']}")
        
        # Show entity summary
        if analysis['entity_summary']:
            print("🔖 Entity Types Found:")
            for entity_type, count in analysis['entity_summary'].items():
                print(f"   • {entity_type.replace('_', ' ').title()}: {count}")
        
        # Show key entities
        print("🎯 Key Entities:")
        for entity in analysis['entities'][:5]:  # Show first 5
            entity_type = entity['type'].replace('_', ' ').title()
            confidence = entity['confidence'] * 100
            print(f"   • {entity_type}: '{entity['value']}' ({confidence:.1f}% confidence)")
        
        if analysis['entities'] and len(analysis['entities']) > 5:
            print(f"   ... and {len(analysis['entities']) - 5} more entities")
        
        # Show threat indicators
        if analysis['threat_indicators']['severity_score'] > 0:
            severity = analysis['threat_indicators']['severity_score']
            print(f"⚠️  Threat Severity Score: {severity}")
            
            if analysis['threat_indicators']['threat_actors']:
                actors = [ta['name'] for ta in analysis['threat_indicators']['threat_actors']]
                print(f"🎭 Threat Actors: {', '.join(actors)}")
            
            if analysis['threat_indicators']['attack_techniques']:
                techniques = [at['technique'] for at in analysis['threat_indicators']['attack_techniques']]
                print(f"🔧 MITRE Techniques: {', '.join(techniques)}")
        
        total_entities += analysis['total_entities']
        total_processing_time += analysis['processing_time_ms']
    
    print(f"\n🎯 OVERALL RESULTS")
    print("=" * 60)
    print(f"Total Test Cases: {len(test_cases)}")
    print(f"Total Entities Extracted: {total_entities}")
    print(f"Average Entities per Text: {total_entities / len(test_cases):.1f}")
    print(f"Average Processing Time: {total_processing_time / len(test_cases):.2f}ms")
    print(f"Total Processing Time: {total_processing_time:.2f}ms")
    
    # Save results
    results = {
        "test_run": {
            "timestamp": datetime.now().isoformat(),
            "total_test_cases": len(test_cases),
            "total_entities_extracted": total_entities,
            "total_processing_time_ms": total_processing_time
        },
        "test_cases": []
    }
    
    for test_text in test_cases:
        analysis = recognizer.analyze_text(test_text)
        results["test_cases"].append(analysis)
    
    with open("enhanced_nlp_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: enhanced_nlp_test_results.json")
    print("🟢 Enhanced NLP entity recognition testing complete!")


if __name__ == "__main__":
    test_enhanced_nlp()
