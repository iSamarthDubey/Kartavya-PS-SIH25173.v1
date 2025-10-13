#!/usr/bin/env python3
"""
🔍 Threat Intelligence Integration System
=========================================
Comprehensive threat intelligence platform integrating:
- Multiple threat intelligence feeds (OSINT, Commercial, Private)
- IOC (Indicators of Compromise) enrichment
- Threat actor attribution and profiling
- Campaign tracking and correlation
- MITRE ATT&CK framework mapping
- Threat hunting IOC generation
- Risk scoring based on threat intelligence
- Automated IOC reputation scoring
"""

import json
import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from pathlib import Path
import sys
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp.security_entities import SecurityNLPRecognizer
from analytics.attack_chains import SimpleAttackChainGenerator


class IOCType(Enum):
    """Types of Indicators of Compromise"""
    IP_ADDRESS = "ip"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    MUTEX = "mutex"
    REGISTRY_KEY = "registry"
    FILE_PATH = "file_path"
    USER_AGENT = "user_agent"
    X509_CERTIFICATE = "certificate"


class ThreatSource(Enum):
    """Sources of threat intelligence"""
    OSINT = "osint"
    COMMERCIAL = "commercial"
    PRIVATE = "private"
    GOVERNMENT = "government"
    COMMUNITY = "community"


class ConfidenceLevel(Enum):
    """Confidence levels for threat intelligence"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class ThreatType(Enum):
    """Types of threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    C2 = "command_control"
    EXPLOIT = "exploit"
    BOTNET = "botnet"
    APT = "apt"
    RANSOMWARE = "ransomware"
    TROJAN = "trojan"
    BACKDOOR = "backdoor"


@dataclass
class IOCIndicator:
    """Individual Indicator of Compromise"""
    ioc_id: str
    ioc_type: IOCType
    value: str
    threat_types: List[ThreatType]
    confidence: ConfidenceLevel
    first_seen: datetime
    last_seen: datetime
    source: ThreatSource
    source_name: str
    description: str
    tags: List[str] = field(default_factory=list)
    malware_families: List[str] = field(default_factory=list)
    threat_actors: List[str] = field(default_factory=list)
    campaigns: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)
    reputation_score: float = 0.0
    false_positive_rate: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatActor:
    """Threat actor profile with attribution data"""
    actor_id: str
    name: str
    aliases: List[str]
    country: Optional[str]
    motivation: List[str]
    targets: List[str]
    active_since: datetime
    last_activity: datetime
    sophistication: str
    tools: List[str]
    techniques: List[str]
    campaigns: List[str] = field(default_factory=list)
    iocs: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class ThreatCampaign:
    """Threat campaign with associated IOCs and TTPs"""
    campaign_id: str
    name: str
    description: str
    threat_actors: List[str]
    targets: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    active: bool
    iocs: List[str]
    mitre_techniques: List[str]
    malware_families: List[str]
    objectives: List[str] = field(default_factory=list)


class ThreatIntelligenceFeed:
    """Simulated threat intelligence feed"""
    
    def __init__(self, feed_name: str, source_type: ThreatSource):
        self.feed_name = feed_name
        self.source_type = source_type
        self.last_updated = datetime.now()
        
        # Generate realistic IOCs for demonstration
        self.sample_iocs = self._generate_sample_iocs()
        self.sample_actors = self._generate_sample_actors()
        self.sample_campaigns = self._generate_sample_campaigns()
    
    def _generate_sample_iocs(self) -> List[IOCIndicator]:
        """Generate realistic sample IOCs"""
        iocs = []
        
        # Malicious IPs
        malicious_ips = [
            "185.220.101.182", "194.147.85.16", "91.240.118.172",
            "45.142.214.222", "172.67.181.72", "104.21.84.78"
        ]
        
        for ip in malicious_ips:
            ioc = IOCIndicator(
                ioc_id=f"ip_{hashlib.md5(ip.encode()).hexdigest()[:8]}",
                ioc_type=IOCType.IP_ADDRESS,
                value=ip,
                threat_types=[ThreatType.C2, ThreatType.MALWARE],
                confidence=ConfidenceLevel.HIGH,
                first_seen=datetime.now() - timedelta(days=random.randint(1, 30)),
                last_seen=datetime.now() - timedelta(hours=random.randint(1, 24)),
                source=self.source_type,
                source_name=self.feed_name,
                description=f"Command and control server associated with {random.choice(['APT29', 'Lazarus', 'FIN7'])}",
                tags=["c2", "malware", "apt"],
                threat_actors=[random.choice(["APT29", "Lazarus Group", "FIN7"])],
                campaigns=[f"Operation {random.choice(['ShadowStorm', 'CyberPhoenix', 'DarkVortex'])}"],
                mitre_techniques=[random.choice(["T1071.001", "T1090", "T1041"])],
                reputation_score=random.uniform(0.7, 0.95),
                false_positive_rate=random.uniform(0.01, 0.05)
            )
            iocs.append(ioc)
        
        # Malicious domains
        malicious_domains = [
            "malicious-c2.evil.com", "phishing.suspicious.org",
            "update-service.company-cdn.net", "fake-bank.secure-login.net"
        ]
        
        for domain in malicious_domains:
            ioc = IOCIndicator(
                ioc_id=f"domain_{hashlib.md5(domain.encode()).hexdigest()[:8]}",
                ioc_type=IOCType.DOMAIN,
                value=domain,
                threat_types=[ThreatType.PHISHING, ThreatType.C2],
                confidence=ConfidenceLevel.MEDIUM,
                first_seen=datetime.now() - timedelta(days=random.randint(1, 15)),
                last_seen=datetime.now() - timedelta(hours=random.randint(1, 12)),
                source=self.source_type,
                source_name=self.feed_name,
                description=f"Phishing domain impersonating legitimate services",
                tags=["phishing", "typosquatting", "credential_harvesting"],
                malware_families=[random.choice(["Emotet", "TrickBot", "QakBot"])],
                mitre_techniques=["T1566.002", "T1071.001"],
                reputation_score=random.uniform(0.6, 0.85),
                false_positive_rate=random.uniform(0.02, 0.08)
            )
            iocs.append(ioc)
        
        # File hashes
        malicious_hashes = [
            "a1b2c3d4e5f6789012345678901234567890abcdef",
            "9f8e7d6c5b4a321098765432109876543210fedc",
            "1a2b3c4d5e6f789012345678901234567890abcd"
        ]
        
        for file_hash in malicious_hashes:
            ioc = IOCIndicator(
                ioc_id=f"hash_{hashlib.md5(file_hash.encode()).hexdigest()[:8]}",
                ioc_type=IOCType.FILE_HASH,
                value=file_hash,
                threat_types=[ThreatType.MALWARE, ThreatType.RANSOMWARE],
                confidence=ConfidenceLevel.VERY_HIGH,
                first_seen=datetime.now() - timedelta(days=random.randint(5, 60)),
                last_seen=datetime.now() - timedelta(days=random.randint(1, 7)),
                source=self.source_type,
                source_name=self.feed_name,
                description=f"Malware sample - {random.choice(['Ransomware', 'Banking Trojan', 'Remote Access Tool'])}",
                tags=["malware", "executable", "windows"],
                malware_families=[random.choice(["Ryuk", "Conti", "Emotet", "TrickBot"])],
                threat_actors=[random.choice(["APT29", "FIN7", "Lazarus Group"])],
                mitre_techniques=["T1055", "T1027", "T1486"],
                reputation_score=random.uniform(0.85, 0.99),
                false_positive_rate=random.uniform(0.001, 0.01)
            )
            iocs.append(ioc)
        
        return iocs
    
    def _generate_sample_actors(self) -> List[ThreatActor]:
        """Generate sample threat actors"""
        actors = [
            ThreatActor(
                actor_id="apt29",
                name="APT29",
                aliases=["Cozy Bear", "The Dukes", "NOBELIUM"],
                country="Russia",
                motivation=["espionage", "intelligence_gathering"],
                targets=["government", "healthcare", "technology"],
                active_since=datetime(2008, 1, 1),
                last_activity=datetime.now() - timedelta(days=random.randint(1, 30)),
                sophistication="high",
                tools=["Cobalt Strike", "PowerShell", "WMI"],
                techniques=["T1566.001", "T1055", "T1078", "T1071.001"],
                description="Russian state-sponsored APT group known for sophisticated spear-phishing campaigns"
            ),
            ThreatActor(
                actor_id="lazarus",
                name="Lazarus Group",
                aliases=["HIDDEN COBRA", "Guardians of Peace"],
                country="North Korea",
                motivation=["financial", "espionage", "sabotage"],
                targets=["financial", "cryptocurrency", "entertainment"],
                active_since=datetime(2009, 1, 1),
                last_activity=datetime.now() - timedelta(days=random.randint(1, 15)),
                sophistication="high",
                tools=["Custom Malware", "PowerShell", "Living off the Land"],
                techniques=["T1566.002", "T1059.003", "T1486", "T1041"],
                description="North Korean state-sponsored group responsible for major financial heists and destructive attacks"
            ),
            ThreatActor(
                actor_id="fin7",
                name="FIN7",
                aliases=["Carbanak", "Navigator Group"],
                country=None,
                motivation=["financial"],
                targets=["retail", "restaurant", "financial"],
                active_since=datetime(2013, 1, 1),
                last_activity=datetime.now() - timedelta(days=random.randint(5, 45)),
                sophistication="medium",
                tools=["Carbanak", "PowerShell", "Mimikatz"],
                techniques=["T1566.001", "T1059.001", "T1003.001", "T1005"],
                description="Financially motivated cybercriminal group targeting point-of-sale systems"
            )
        ]
        return actors
    
    def _generate_sample_campaigns(self) -> List[ThreatCampaign]:
        """Generate sample threat campaigns"""
        campaigns = [
            ThreatCampaign(
                campaign_id="op_shadowstorm",
                name="Operation ShadowStorm",
                description="Sophisticated spear-phishing campaign targeting government entities",
                threat_actors=["APT29"],
                targets=["government", "defense", "healthcare"],
                start_date=datetime.now() - timedelta(days=90),
                end_date=None,
                active=True,
                iocs=["ip_12345678", "domain_abcd1234"],
                mitre_techniques=["T1566.001", "T1055", "T1078"],
                malware_families=["Cobalt Strike"],
                objectives=["intelligence_gathering", "credential_harvesting"]
            ),
            ThreatCampaign(
                campaign_id="cyber_phoenix",
                name="CyberPhoenix",
                description="Financial fraud campaign using banking trojans",
                threat_actors=["Lazarus Group"],
                targets=["financial", "cryptocurrency"],
                start_date=datetime.now() - timedelta(days=120),
                end_date=datetime.now() - timedelta(days=30),
                active=False,
                iocs=["hash_98765432", "domain_efgh5678"],
                mitre_techniques=["T1566.002", "T1486", "T1041"],
                malware_families=["TrickBot", "Ryuk"],
                objectives=["financial_theft", "ransomware"]
            )
        ]
        return campaigns
    
    def get_iocs_by_type(self, ioc_type: IOCType) -> List[IOCIndicator]:
        """Get IOCs filtered by type"""
        return [ioc for ioc in self.sample_iocs if ioc.ioc_type == ioc_type]
    
    def get_iocs_by_actor(self, actor_name: str) -> List[IOCIndicator]:
        """Get IOCs associated with a specific threat actor"""
        return [ioc for ioc in self.sample_iocs if actor_name in ioc.threat_actors]
    
    def search_iocs(self, value: str) -> List[IOCIndicator]:
        """Search for IOCs by value"""
        return [ioc for ioc in self.sample_iocs if value.lower() in ioc.value.lower()]


class ThreatIntelligenceManager:
    """Main threat intelligence management system"""
    
    def __init__(self):
        self.feeds: Dict[str, ThreatIntelligenceFeed] = {}
        self.ioc_cache: Dict[str, IOCIndicator] = {}
        self.actors: Dict[str, ThreatActor] = {}
        self.campaigns: Dict[str, ThreatCampaign] = {}
        self.nlp_recognizer = SecurityNLPRecognizer()
        self.attack_generator = SimpleAttackChainGenerator()
        
        # Initialize default feeds
        self._initialize_feeds()
        self._build_caches()
    
    def _initialize_feeds(self):
        """Initialize threat intelligence feeds"""
        feeds_config = [
            ("VirusTotal", ThreatSource.COMMERCIAL),
            ("AlienVault OTX", ThreatSource.COMMUNITY),
            ("ThreatFox", ThreatSource.OSINT),
            ("MalwareBazaar", ThreatSource.OSINT),
            ("Internal TI", ThreatSource.PRIVATE),
            ("CISA", ThreatSource.GOVERNMENT)
        ]
        
        for feed_name, source_type in feeds_config:
            self.feeds[feed_name] = ThreatIntelligenceFeed(feed_name, source_type)
    
    def _build_caches(self):
        """Build internal caches from all feeds"""
        # Build IOC cache
        for feed in self.feeds.values():
            for ioc in feed.sample_iocs:
                self.ioc_cache[ioc.value] = ioc
        
        # Build actor cache
        for feed in self.feeds.values():
            for actor in feed.sample_actors:
                self.actors[actor.actor_id] = actor
        
        # Build campaign cache
        for feed in self.feeds.values():
            for campaign in feed.sample_campaigns:
                self.campaigns[campaign.campaign_id] = campaign
    
    def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich security event with threat intelligence"""
        enriched_event = event.copy()
        
        # Extract entities for IOC matching
        event_text = json.dumps(event)
        analysis = self.nlp_recognizer.analyze_text(event_text)
        
        threat_intelligence = {
            "matched_iocs": [],
            "associated_actors": [],
            "related_campaigns": [],
            "risk_enhancement": 0,
            "enrichment_timestamp": datetime.now().isoformat()
        }
        
        # Check entities against IOC database
        for entity in analysis.get("entities", []):
            entity_value = entity.get("value", "")
            
            # Search for matching IOCs
            if entity_value in self.ioc_cache:
                ioc = self.ioc_cache[entity_value]
                
                ioc_info = {
                    "ioc_id": ioc.ioc_id,
                    "type": ioc.ioc_type.value,
                    "value": ioc.value,
                    "threat_types": [t.value for t in ioc.threat_types],
                    "confidence": ioc.confidence.value,
                    "reputation_score": ioc.reputation_score,
                    "source": ioc.source_name,
                    "description": ioc.description,
                    "threat_actors": ioc.threat_actors,
                    "campaigns": ioc.campaigns,
                    "mitre_techniques": ioc.mitre_techniques
                }
                
                threat_intelligence["matched_iocs"].append(ioc_info)
                
                # Add associated threat actors
                for actor_name in ioc.threat_actors:
                    if actor_name not in [a["name"] for a in threat_intelligence["associated_actors"]]:
                        actor = next((a for a in self.actors.values() if a.name == actor_name), None)
                        if actor:
                            threat_intelligence["associated_actors"].append({
                                "name": actor.name,
                                "aliases": actor.aliases,
                                "country": actor.country,
                                "sophistication": actor.sophistication,
                                "motivation": actor.motivation
                            })
                
                # Add related campaigns
                for campaign_name in ioc.campaigns:
                    if campaign_name not in [c["name"] for c in threat_intelligence["related_campaigns"]]:
                        campaign = next((c for c in self.campaigns.values() if c.name == campaign_name), None)
                        if campaign:
                            threat_intelligence["related_campaigns"].append({
                                "name": campaign.name,
                                "description": campaign.description,
                                "active": campaign.active,
                                "objectives": campaign.objectives
                            })
                
                # Enhance risk score based on IOC reputation
                threat_intelligence["risk_enhancement"] += ioc.reputation_score * 20
        
        # Calculate overall threat intelligence score
        ti_score = min(100, threat_intelligence["risk_enhancement"])
        threat_intelligence["overall_score"] = ti_score
        
        enriched_event["threat_intelligence"] = threat_intelligence
        
        return enriched_event
    
    def generate_hunt_iocs(self, actor_name: str = None, campaign_name: str = None, 
                          threat_type: ThreatType = None) -> Dict[str, Any]:
        """Generate IOCs for threat hunting based on criteria"""
        hunt_iocs = {
            "generated_at": datetime.now().isoformat(),
            "criteria": {},
            "iocs": [],
            "hunting_queries": [],
            "mitre_techniques": set(),
            "recommended_searches": []
        }
        
        # Set criteria
        if actor_name:
            hunt_iocs["criteria"]["actor"] = actor_name
        if campaign_name:
            hunt_iocs["criteria"]["campaign"] = campaign_name
        if threat_type:
            hunt_iocs["criteria"]["threat_type"] = threat_type.value
        
        # Filter IOCs based on criteria
        filtered_iocs = list(self.ioc_cache.values())
        
        if actor_name:
            filtered_iocs = [ioc for ioc in filtered_iocs if actor_name in ioc.threat_actors]
        
        if campaign_name:
            filtered_iocs = [ioc for ioc in filtered_iocs if campaign_name in ioc.campaigns]
        
        if threat_type:
            filtered_iocs = [ioc for ioc in filtered_iocs if threat_type in ioc.threat_types]
        
        # Build hunt IOCs
        for ioc in filtered_iocs[:20]:  # Limit to 20 for practical hunting
            hunt_ioc = {
                "type": ioc.ioc_type.value,
                "value": ioc.value,
                "confidence": ioc.confidence.value,
                "last_seen": ioc.last_seen.isoformat(),
                "description": ioc.description,
                "hunt_priority": "high" if ioc.reputation_score > 0.8 else "medium"
            }
            hunt_iocs["iocs"].append(hunt_ioc)
            hunt_iocs["mitre_techniques"].update(ioc.mitre_techniques)
        
        # Convert set to list for JSON serialization
        hunt_iocs["mitre_techniques"] = list(hunt_iocs["mitre_techniques"])
        
        # Generate hunting queries
        if hunt_iocs["iocs"]:
            ip_iocs = [ioc["value"] for ioc in hunt_iocs["iocs"] if ioc["type"] == "ip"]
            domain_iocs = [ioc["value"] for ioc in hunt_iocs["iocs"] if ioc["type"] == "domain"]
            hash_iocs = [ioc["value"] for ioc in hunt_iocs["iocs"] if ioc["type"] == "file_hash"]
            
            if ip_iocs:
                hunt_iocs["hunting_queries"].append(f"source.ip:({' OR '.join(ip_iocs[:5])})")
                hunt_iocs["hunting_queries"].append(f"destination.ip:({' OR '.join(ip_iocs[:5])})")
            
            if domain_iocs:
                hunt_iocs["hunting_queries"].append(f"dns.question.name:({' OR '.join(domain_iocs[:5])})")
            
            if hash_iocs:
                hunt_iocs["hunting_queries"].append(f"file.hash.sha256:({' OR '.join(hash_iocs[:3])})")
        
        # Generate recommended searches
        hunt_iocs["recommended_searches"] = [
            "Search for network connections to identified malicious IPs",
            "Look for DNS queries to suspicious domains",
            "Hunt for file executions with known malicious hashes",
            "Check for processes associated with identified malware families",
            "Investigate user accounts with connections to threat actor infrastructure"
        ]
        
        return hunt_iocs
    
    def get_actor_profile(self, actor_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed threat actor profile"""
        actor = next((a for a in self.actors.values() if a.name == actor_name), None)
        if not actor:
            return None
        
        # Get associated IOCs
        associated_iocs = [ioc for ioc in self.ioc_cache.values() if actor_name in ioc.threat_actors]
        
        # Get associated campaigns
        associated_campaigns = [c for c in self.campaigns.values() if actor_name in c.threat_actors]
        
        profile = {
            "basic_info": {
                "name": actor.name,
                "aliases": actor.aliases,
                "country": actor.country,
                "active_since": actor.active_since.isoformat(),
                "last_activity": actor.last_activity.isoformat(),
                "sophistication": actor.sophistication
            },
            "targeting": {
                "motivation": actor.motivation,
                "targets": actor.targets
            },
            "capabilities": {
                "tools": actor.tools,
                "techniques": actor.techniques
            },
            "indicators": {
                "total_iocs": len(associated_iocs),
                "ioc_breakdown": {
                    ioc_type.value: len([ioc for ioc in associated_iocs if ioc.ioc_type == ioc_type])
                    for ioc_type in IOCType
                }
            },
            "campaigns": [
                {
                    "name": campaign.name,
                    "active": campaign.active,
                    "description": campaign.description,
                    "objectives": campaign.objectives
                }
                for campaign in associated_campaigns
            ],
            "recent_activity": [
                {
                    "ioc_value": ioc.value,
                    "ioc_type": ioc.ioc_type.value,
                    "last_seen": ioc.last_seen.isoformat(),
                    "description": ioc.description
                }
                for ioc in sorted(associated_iocs, key=lambda x: x.last_seen, reverse=True)[:5]
            ]
        }
        
        return profile
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        total_iocs = len(self.ioc_cache)
        total_actors = len(self.actors)
        total_campaigns = len(self.campaigns)
        active_campaigns = len([c for c in self.campaigns.values() if c.active])
        
        # IOC breakdown by type
        ioc_breakdown = {}
        for ioc_type in IOCType:
            count = len([ioc for ioc in self.ioc_cache.values() if ioc.ioc_type == ioc_type])
            if count > 0:
                ioc_breakdown[ioc_type.value] = count
        
        # Source breakdown
        source_breakdown = {}
        for ioc in self.ioc_cache.values():
            source = ioc.source_name
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        # Threat type breakdown
        threat_breakdown = {}
        for ioc in self.ioc_cache.values():
            for threat_type in ioc.threat_types:
                threat_breakdown[threat_type.value] = threat_breakdown.get(threat_type.value, 0) + 1
        
        return {
            "overview": {
                "total_iocs": total_iocs,
                "total_threat_actors": total_actors,
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "feeds_connected": len(self.feeds)
            },
            "ioc_breakdown": ioc_breakdown,
            "source_breakdown": source_breakdown,
            "threat_breakdown": threat_breakdown,
            "top_threat_actors": list(self.actors.keys())[:5],
            "recent_updates": [
                f"Updated {feed_name} feed" for feed_name in list(self.feeds.keys())[:3]
            ]
        }


def test_threat_intelligence():
    """Test the threat intelligence integration system"""
    print("🔍 THREAT INTELLIGENCE INTEGRATION SYSTEM")
    print("=" * 60)
    
    # Initialize threat intelligence manager
    ti_manager = ThreatIntelligenceManager()
    
    print("📊 THREAT INTELLIGENCE STATISTICS")
    print("-" * 40)
    stats = ti_manager.get_statistics()
    
    print(f"• Total IOCs: {stats['overview']['total_iocs']}")
    print(f"• Threat Actors: {stats['overview']['total_threat_actors']}")
    print(f"• Active Campaigns: {stats['overview']['active_campaigns']}")
    print(f"• Connected Feeds: {stats['overview']['feeds_connected']}")
    
    print("\n📈 IOC Breakdown by Type:")
    for ioc_type, count in stats["ioc_breakdown"].items():
        print(f"  - {ioc_type}: {count}")
    
    print("\n🏢 IOC Sources:")
    for source, count in stats["source_breakdown"].items():
        print(f"  - {source}: {count}")
    
    # Test event enrichment
    print(f"\n🔍 TESTING EVENT ENRICHMENT")
    print("-" * 40)
    
    # Create sample security event
    sample_event = {
        "event_id": "test_001",
        "timestamp": datetime.now().isoformat(),
        "event_type": "network_connection",
        "source_ip": "185.220.101.182",  # This should match our malicious IPs
        "destination_ip": "10.0.1.100",
        "user": "john.doe",
        "host": "WORKSTATION-01",
        "description": "Suspicious outbound connection detected"
    }
    
    print(f"Original Event: {sample_event['description']}")
    print(f"Source IP: {sample_event['source_ip']}")
    
    # Enrich with threat intelligence
    enriched_event = ti_manager.enrich_event(sample_event)
    ti_data = enriched_event.get("threat_intelligence", {})
    
    print(f"\n🎯 Threat Intelligence Enrichment:")
    print(f"• Overall TI Score: {ti_data.get('overall_score', 0):.1f}/100")
    print(f"• Matched IOCs: {len(ti_data.get('matched_iocs', []))}")
    print(f"• Associated Actors: {len(ti_data.get('associated_actors', []))}")
    print(f"• Related Campaigns: {len(ti_data.get('related_campaigns', []))}")
    
    if ti_data.get("matched_iocs"):
        print("\n🚨 IOC Matches:")
        for ioc in ti_data["matched_iocs"]:
            print(f"  - {ioc['type']}: {ioc['value']} (confidence: {ioc['confidence']}/4)")
            print(f"    Description: {ioc['description']}")
            if ioc['threat_actors']:
                print(f"    Threat Actors: {', '.join(ioc['threat_actors'])}")
    
    if ti_data.get("associated_actors"):
        print("\n🎭 Associated Threat Actors:")
        for actor in ti_data["associated_actors"]:
            print(f"  - {actor['name']} ({actor.get('country', 'Unknown')})")
            print(f"    Sophistication: {actor['sophistication']}")
            print(f"    Motivation: {', '.join(actor['motivation'])}")
    
    # Test threat hunting IOC generation
    print(f"\n🎯 TESTING THREAT HUNTING IOC GENERATION")
    print("-" * 40)
    
    # Generate hunt IOCs for APT29
    hunt_iocs = ti_manager.generate_hunt_iocs(actor_name="APT29")
    
    print(f"Hunt IOCs for APT29:")
    print(f"• Total IOCs: {len(hunt_iocs['iocs'])}")
    print(f"• MITRE Techniques: {len(hunt_iocs['mitre_techniques'])}")
    print(f"• Hunting Queries: {len(hunt_iocs['hunting_queries'])}")
    
    if hunt_iocs["iocs"]:
        print("\n🔍 Sample Hunt IOCs:")
        for i, ioc in enumerate(hunt_iocs["iocs"][:3], 1):
            print(f"  {i}. {ioc['type']}: {ioc['value']} (priority: {ioc['hunt_priority']})")
    
    if hunt_iocs["hunting_queries"]:
        print("\n📝 Sample Hunting Queries:")
        for i, query in enumerate(hunt_iocs["hunting_queries"][:3], 1):
            print(f"  {i}. {query}")
    
    # Test threat actor profiling
    print(f"\n👤 TESTING THREAT ACTOR PROFILING")
    print("-" * 40)
    
    actor_profile = ti_manager.get_actor_profile("APT29")
    if actor_profile:
        basic_info = actor_profile["basic_info"]
        print(f"Actor: {basic_info['name']}")
        print(f"Aliases: {', '.join(basic_info['aliases'])}")
        print(f"Country: {basic_info['country']}")
        print(f"Sophistication: {basic_info['sophistication']}")
        print(f"Active Since: {basic_info['active_since'][:10]}")
        
        print(f"\n🎯 Targeting:")
        targeting = actor_profile["targeting"]
        print(f"• Motivation: {', '.join(targeting['motivation'])}")
        print(f"• Targets: {', '.join(targeting['targets'])}")
        
        print(f"\n🛠️ Capabilities:")
        capabilities = actor_profile["capabilities"]
        print(f"• Tools: {', '.join(capabilities['tools'])}")
        print(f"• Techniques: {', '.join(capabilities['techniques'][:5])}...")
        
        print(f"\n📊 Intelligence Summary:")
        indicators = actor_profile["indicators"]
        print(f"• Total IOCs: {indicators['total_iocs']}")
        print(f"• Active Campaigns: {len([c for c in actor_profile['campaigns'] if c['active']])}")
    
    # Save comprehensive report
    report_data = {
        "test_execution": {
            "timestamp": datetime.now().isoformat(),
            "test_type": "threat_intelligence_integration"
        },
        "statistics": stats,
        "sample_enrichment": {
            "original_event": sample_event,
            "enriched_event": enriched_event
        },
        "hunt_iocs_sample": hunt_iocs,
        "actor_profile_sample": actor_profile
    }
    
    with open("threat_intelligence_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 Test report saved to: threat_intelligence_test_report.json")
    print("🟢 Threat intelligence integration testing complete!")
    
    return ti_manager


if __name__ == "__main__":
    test_threat_intelligence()
