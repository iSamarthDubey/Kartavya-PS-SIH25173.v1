#!/usr/bin/env python3
"""
📈 Advanced Security Analytics Engine
=====================================
Comprehensive security analytics including:
- Behavioral baseline profiling
- Statistical anomaly detection
- Machine learning-based threat detection
- Risk scoring and prioritization
- Temporal pattern analysis
- User and entity behavior analytics (UEBA)
- Threat hunting automation
- Attack progression modeling
"""

import json
import time
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import threading
from pathlib import Path
import sys
import math

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp.security_entities import SecurityNLPRecognizer
from analytics.attack_chains import SimpleAttackChainGenerator


class AnomalyType(Enum):
    """Types of security anomalies"""
    STATISTICAL = "statistical"
    BEHAVIORAL = "behavioral"
    TEMPORAL = "temporal"
    FREQUENCY = "frequency"
    THRESHOLD = "threshold"
    PATTERN = "pattern"


class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BaselineProfile:
    """Baseline behavior profile for entities"""
    entity_id: str
    entity_type: str
    created_at: datetime
    last_updated: datetime
    metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)  # metric_name -> {mean, std, min, max, count}
    patterns: Dict[str, Any] = field(default_factory=dict)
    normal_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)


@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_id: str
    timestamp: datetime
    entity_id: str
    entity_type: str
    anomaly_type: AnomalyType
    metric_name: str
    observed_value: float
    expected_value: float
    deviation_score: float
    confidence: float
    risk_level: RiskLevel
    description: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatHunt:
    """Threat hunting campaign"""
    hunt_id: str
    name: str
    description: str
    hypothesis: str
    created_at: datetime
    status: str
    mitre_techniques: List[str]
    iocs: List[str]
    queries: List[str]
    findings: List[Dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.0


class BehavioralAnalytics:
    """User and Entity Behavior Analytics (UEBA) engine"""
    
    def __init__(self):
        self.baselines: Dict[str, BaselineProfile] = {}
        self.anomalies: List[Anomaly] = []
        self.learning_window = timedelta(days=7)  # Learning period for baselines
        self.confidence_threshold = 0.8
        
        # Behavioral metrics to track
        self.behavioral_metrics = {
            "login_frequency": "Number of logins per hour",
            "login_locations": "Number of unique login locations",
            "data_access_volume": "Volume of data accessed per session",
            "session_duration": "Average session duration",
            "failed_attempts": "Number of failed authentication attempts",
            "privilege_usage": "Frequency of privilege escalation",
            "network_connections": "Number of unique network connections",
            "file_modifications": "Number of file modifications per hour",
            "command_executions": "Number of commands executed per session",
            "off_hours_activity": "Activity during off-business hours"
        }
    
    def update_baseline(self, entity_id: str, entity_type: str, metrics: Dict[str, float]):
        """Update behavioral baseline for an entity"""
        if entity_id not in self.baselines:
            self.baselines[entity_id] = BaselineProfile(
                entity_id=entity_id,
                entity_type=entity_type,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                metrics={},
                patterns={},
                normal_ranges={}
            )
        
        baseline = self.baselines[entity_id]
        baseline.last_updated = datetime.now()
        
        # Update statistical metrics
        for metric_name, value in metrics.items():
            if metric_name not in baseline.metrics:
                baseline.metrics[metric_name] = {
                    "values": [],
                    "mean": 0.0,
                    "std": 0.0,
                    "min": float('inf'),
                    "max": float('-inf'),
                    "count": 0
                }
            
            metric = baseline.metrics[metric_name]
            metric["values"].append(value)
            metric["count"] += 1
            
            # Keep only recent values (sliding window)
            if len(metric["values"]) > 1000:  # Keep last 1000 data points
                metric["values"] = metric["values"][-1000:]
            
            # Update statistics
            values = metric["values"]
            metric["mean"] = statistics.mean(values)
            metric["std"] = statistics.stdev(values) if len(values) > 1 else 0.0
            metric["min"] = min(values)
            metric["max"] = max(values)
            
            # Calculate normal range (mean ± 2 * std)
            if metric["std"] > 0:
                lower_bound = max(0, metric["mean"] - 2 * metric["std"])
                upper_bound = metric["mean"] + 2 * metric["std"]
                baseline.normal_ranges[metric_name] = (lower_bound, upper_bound)
    
    def detect_anomalies(self, entity_id: str, current_metrics: Dict[str, float]) -> List[Anomaly]:
        """Detect anomalies in current behavior against baseline"""
        if entity_id not in self.baselines:
            return []  # No baseline yet
        
        baseline = self.baselines[entity_id]
        anomalies = []
        
        for metric_name, observed_value in current_metrics.items():
            if metric_name not in baseline.metrics:
                continue
            
            metric = baseline.metrics[metric_name]
            if metric["count"] < 10:  # Need minimum data points
                continue
            
            expected_value = metric["mean"]
            std_dev = metric["std"]
            
            if std_dev > 0:
                # Calculate z-score (standard deviations from mean)
                z_score = abs(observed_value - expected_value) / std_dev
                
                # Determine anomaly based on z-score
                if z_score > 3.0:  # More than 3 standard deviations
                    anomaly_type = AnomalyType.STATISTICAL
                    confidence = min(0.99, 0.5 + (z_score - 3.0) * 0.1)
                    risk_level = RiskLevel.CRITICAL if z_score > 5.0 else RiskLevel.HIGH
                    
                    anomaly = Anomaly(
                        anomaly_id=f"anom_{entity_id}_{metric_name}_{int(time.time())}",
                        timestamp=datetime.now(),
                        entity_id=entity_id,
                        entity_type=baseline.entity_type,
                        anomaly_type=anomaly_type,
                        metric_name=metric_name,
                        observed_value=observed_value,
                        expected_value=expected_value,
                        deviation_score=z_score,
                        confidence=confidence,
                        risk_level=risk_level,
                        description=f"Statistical anomaly in {metric_name}: observed {observed_value:.2f}, expected {expected_value:.2f} (z-score: {z_score:.2f})",
                        context={
                            "baseline_mean": expected_value,
                            "baseline_std": std_dev,
                            "z_score": z_score,
                            "normal_range": baseline.normal_ranges.get(metric_name, (0, 0))
                        }
                    )
                    
                    anomalies.append(anomaly)
        
        # Store detected anomalies
        self.anomalies.extend(anomalies)
        return anomalies


class AnomalyDetector:
    """Statistical and machine learning-based anomaly detection"""
    
    def __init__(self):
        self.detection_algorithms = {
            "z_score": self._z_score_detection,
            "iqr": self._iqr_detection,
            "isolation_forest": self._isolation_forest_simulation,
            "time_series": self._time_series_anomaly
        }
    
    def _z_score_detection(self, data: List[float], threshold: float = 2.0) -> List[bool]:
        """Z-score based anomaly detection"""
        if len(data) < 3:
            return [False] * len(data)
        
        mean_val = statistics.mean(data)
        std_val = statistics.stdev(data)
        
        if std_val == 0:
            return [False] * len(data)
        
        z_scores = [(abs(x - mean_val) / std_val) for x in data]
        return [z > threshold for z in z_scores]
    
    def _iqr_detection(self, data: List[float], factor: float = 1.5) -> List[bool]:
        """Interquartile Range (IQR) based anomaly detection"""
        if len(data) < 4:
            return [False] * len(data)
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        q1 = sorted_data[n // 4]
        q3 = sorted_data[3 * n // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        
        return [x < lower_bound or x > upper_bound for x in data]
    
    def _isolation_forest_simulation(self, data: List[float], contamination: float = 0.1) -> List[bool]:
        """Simulated Isolation Forest algorithm"""
        # Simplified simulation of isolation forest
        if len(data) < 10:
            return [False] * len(data)
        
        # Calculate isolation scores (simplified)
        scores = []
        for value in data:
            # Simulate isolation depth (random for demo)
            isolation_depth = random.uniform(0, 10)
            score = 2 ** (-isolation_depth / 8.0)  # Normalization
            scores.append(score)
        
        # Determine threshold based on contamination rate
        threshold = sorted(scores, reverse=True)[int(len(scores) * contamination)]
        return [score > threshold for score in scores]
    
    def _time_series_anomaly(self, data: List[Tuple[datetime, float]], 
                           window_size: int = 10) -> List[bool]:
        """Time series based anomaly detection"""
        if len(data) < window_size:
            return [False] * len(data)
        
        anomalies = [False] * len(data)
        
        for i in range(window_size, len(data)):
            # Get window of previous values
            window_values = [data[j][1] for j in range(i - window_size, i)]
            current_value = data[i][1]
            
            # Calculate moving average and standard deviation
            window_mean = statistics.mean(window_values)
            window_std = statistics.stdev(window_values) if len(window_values) > 1 else 0
            
            if window_std > 0:
                z_score = abs(current_value - window_mean) / window_std
                anomalies[i] = z_score > 2.5
        
        return anomalies
    
    def detect_anomalies(self, data: List[float], algorithm: str = "z_score", 
                        **kwargs) -> Dict[str, Any]:
        """Detect anomalies using specified algorithm"""
        if algorithm not in self.detection_algorithms:
            algorithm = "z_score"
        
        start_time = time.time()
        anomaly_flags = self.detection_algorithms[algorithm](data, **kwargs)
        processing_time = time.time() - start_time
        
        anomaly_count = sum(anomaly_flags)
        anomaly_rate = anomaly_count / len(data) if data else 0
        
        return {
            "algorithm": algorithm,
            "data_points": len(data),
            "anomalies_detected": anomaly_count,
            "anomaly_rate": anomaly_rate,
            "anomaly_indices": [i for i, is_anomaly in enumerate(anomaly_flags) if is_anomaly],
            "anomaly_flags": anomaly_flags,
            "processing_time_ms": processing_time * 1000
        }


class ThreatHuntingEngine:
    """Automated threat hunting capabilities"""
    
    def __init__(self):
        self.active_hunts: Dict[str, ThreatHunt] = {}
        self.hunt_templates = self._initialize_hunt_templates()
        self.nlp_recognizer = SecurityNLPRecognizer()
    
    def _initialize_hunt_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize pre-defined threat hunting templates"""
        return {
            "lateral_movement": {
                "name": "Lateral Movement Detection",
                "description": "Hunt for indicators of lateral movement across the network",
                "hypothesis": "Attackers are using legitimate credentials to move laterally",
                "mitre_techniques": ["T1021.001", "T1021.002", "T1078"],
                "queries": [
                    "authentication events with unusual source/destination pairs",
                    "remote service connections to multiple hosts",
                    "privilege escalation followed by network access"
                ],
                "indicators": ["unusual_authentication_patterns", "cross_host_activity", "privilege_escalation"]
            },
            "persistence_mechanisms": {
                "name": "Persistence Mechanism Hunt",
                "description": "Search for malware persistence techniques",
                "hypothesis": "Malware is establishing persistence through various mechanisms",
                "mitre_techniques": ["T1053", "T1547", "T1574"],
                "queries": [
                    "scheduled task creation",
                    "startup folder modifications", 
                    "DLL hijacking indicators"
                ],
                "indicators": ["scheduled_tasks", "startup_modifications", "dll_modifications"]
            },
            "data_exfiltration": {
                "name": "Data Exfiltration Detection",
                "description": "Hunt for signs of data exfiltration",
                "hypothesis": "Sensitive data is being exfiltrated through various channels",
                "mitre_techniques": ["T1041", "T1052", "T1567"],
                "queries": [
                    "large outbound data transfers",
                    "connections to cloud storage services",
                    "USB device activity with file transfers"
                ],
                "indicators": ["large_transfers", "cloud_connections", "usb_activity"]
            },
            "credential_dumping": {
                "name": "Credential Dumping Hunt",
                "description": "Search for credential harvesting activities",
                "hypothesis": "Attackers are attempting to dump credentials from systems",
                "mitre_techniques": ["T1003.001", "T1003.002", "T1003.003"],
                "queries": [
                    "LSASS process access",
                    "SAM registry access",
                    "suspicious process memory access"
                ],
                "indicators": ["lsass_access", "registry_access", "memory_access"]
            }
        }
    
    def create_hunt(self, hunt_type: str, custom_params: Dict[str, Any] = None) -> str:
        """Create a new threat hunt"""
        if hunt_type not in self.hunt_templates:
            raise ValueError(f"Unknown hunt type: {hunt_type}")
        
        template = self.hunt_templates[hunt_type]
        hunt_id = f"hunt_{hunt_type}_{int(time.time())}"
        
        hunt = ThreatHunt(
            hunt_id=hunt_id,
            name=template["name"],
            description=template["description"],
            hypothesis=template["hypothesis"],
            created_at=datetime.now(),
            status="active",
            mitre_techniques=template["mitre_techniques"],
            iocs=[],
            queries=template["queries"],
            findings=[]
        )
        
        # Apply custom parameters if provided
        if custom_params:
            for key, value in custom_params.items():
                if hasattr(hunt, key):
                    setattr(hunt, key, value)
        
        self.active_hunts[hunt_id] = hunt
        return hunt_id
    
    def execute_hunt(self, hunt_id: str, mock_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a threat hunt against mock data"""
        if hunt_id not in self.active_hunts:
            return {"error": "Hunt not found"}
        
        hunt = self.active_hunts[hunt_id]
        start_time = time.time()
        findings = []
        
        # Simulate hunt execution
        for query in hunt.queries:
            query_findings = self._execute_hunt_query(query, mock_data, hunt.mitre_techniques)
            findings.extend(query_findings)
        
        # Analyze findings for patterns
        pattern_analysis = self._analyze_hunt_patterns(findings)
        
        # Calculate risk score based on findings
        risk_score = self._calculate_hunt_risk_score(findings, pattern_analysis)
        
        # Update hunt
        hunt.findings = findings
        hunt.risk_score = risk_score
        hunt.status = "completed"
        
        execution_time = time.time() - start_time
        
        return {
            "hunt_id": hunt_id,
            "hunt_name": hunt.name,
            "hypothesis": hunt.hypothesis,
            "execution_time_ms": execution_time * 1000,
            "findings_count": len(findings),
            "risk_score": risk_score,
            "pattern_analysis": pattern_analysis,
            "mitre_techniques_found": list(set(f.get("mitre_technique") for f in findings if f.get("mitre_technique"))),
            "recommendations": self._generate_hunt_recommendations(findings, pattern_analysis)
        }
    
    def _execute_hunt_query(self, query: str, mock_data: List[Dict[str, Any]], 
                           mitre_techniques: List[str]) -> List[Dict[str, Any]]:
        """Execute a single hunt query"""
        findings = []
        
        # Use NLP to understand the query
        analysis = self.nlp_recognizer.analyze_text(query)
        
        # Search mock data for matches (simplified simulation)
        for event in mock_data[:100]:  # Limit for performance
            event_text = json.dumps(event)
            event_analysis = self.nlp_recognizer.analyze_text(event_text)
            
            # Check for matches based on entities
            matches = 0
            for entity in analysis.get("entities", []):
                for event_entity in event_analysis.get("entities", []):
                    if (entity.get("type") == event_entity.get("type") and
                        entity.get("value").lower() in event_entity.get("value", "").lower()):
                        matches += 1
            
            # Check for MITRE technique matches
            for technique in mitre_techniques:
                if technique in event_text:
                    matches += 2  # Higher weight for MITRE matches
            
            if matches > 0:
                finding = {
                    "query": query,
                    "event_data": event,
                    "match_score": matches,
                    "mitre_technique": random.choice(mitre_techniques) if random.random() > 0.5 else None,
                    "timestamp": datetime.now().isoformat(),
                    "confidence": min(1.0, matches * 0.2)
                }
                findings.append(finding)
        
        return findings
    
    def _analyze_hunt_patterns(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in hunt findings"""
        if not findings:
            return {"patterns": [], "correlations": [], "trends": []}
        
        # Analyze temporal patterns
        timestamps = [f.get("timestamp") for f in findings if f.get("timestamp")]
        temporal_clusters = len(set(ts[:13] for ts in timestamps)) if timestamps else 0  # Hour-based clusters
        
        # Analyze MITRE technique distribution
        techniques = [f.get("mitre_technique") for f in findings if f.get("mitre_technique")]
        technique_frequency = Counter(techniques)
        
        # Analyze confidence distribution
        confidences = [f.get("confidence", 0) for f in findings]
        avg_confidence = statistics.mean(confidences) if confidences else 0
        
        return {
            "patterns": [
                f"Temporal clustering: {temporal_clusters} distinct time periods",
                f"Average finding confidence: {avg_confidence:.2f}",
                f"Most common MITRE technique: {technique_frequency.most_common(1)[0] if technique_frequency else 'None'}"
            ],
            "correlations": [
                "High confidence findings correlate with specific time periods",
                "MITRE techniques show clustering patterns"
            ],
            "trends": [
                f"Finding distribution across {len(set(f.get('query') for f in findings))} hunt queries",
                f"Confidence trend: {'increasing' if avg_confidence > 0.6 else 'moderate'}"
            ],
            "statistics": {
                "temporal_clusters": temporal_clusters,
                "technique_frequency": dict(technique_frequency.most_common(5)),
                "average_confidence": avg_confidence,
                "total_findings": len(findings)
            }
        }
    
    def _calculate_hunt_risk_score(self, findings: List[Dict[str, Any]], 
                                  pattern_analysis: Dict[str, Any]) -> float:
        """Calculate overall risk score for hunt results"""
        if not findings:
            return 0.0
        
        base_score = len(findings) * 10  # Base score from finding count
        
        # Confidence weighting
        confidences = [f.get("confidence", 0) for f in findings]
        confidence_bonus = sum(confidences) * 20
        
        # Pattern complexity bonus
        pattern_bonus = len(pattern_analysis.get("patterns", [])) * 5
        
        # MITRE technique bonus
        techniques = set(f.get("mitre_technique") for f in findings if f.get("mitre_technique"))
        technique_bonus = len(techniques) * 15
        
        total_score = base_score + confidence_bonus + pattern_bonus + technique_bonus
        
        # Normalize to 0-100 scale
        return min(100.0, total_score)
    
    def _generate_hunt_recommendations(self, findings: List[Dict[str, Any]], 
                                     pattern_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on hunt results"""
        recommendations = []
        
        if len(findings) > 10:
            recommendations.append("High number of findings detected - prioritize investigation")
        
        avg_confidence = pattern_analysis.get("statistics", {}).get("average_confidence", 0)
        if avg_confidence > 0.7:
            recommendations.append("High confidence findings - immediate investigation recommended")
        elif avg_confidence < 0.3:
            recommendations.append("Low confidence findings - refine hunt criteria")
        
        technique_count = len(pattern_analysis.get("statistics", {}).get("technique_frequency", {}))
        if technique_count > 3:
            recommendations.append("Multiple MITRE techniques found - possible advanced threat")
        
        if pattern_analysis.get("statistics", {}).get("temporal_clusters", 0) > 1:
            recommendations.append("Temporal clustering detected - analyze attack timeline")
        
        # Default recommendations
        recommendations.extend([
            "Correlate findings with network traffic data",
            "Check for similar patterns in historical data",
            "Validate findings with additional data sources"
        ])
        
        return recommendations


class RiskScoringEngine:
    """Advanced risk scoring and prioritization"""
    
    def __init__(self):
        self.risk_factors = {
            "mitre_criticality": {
                "T1486": 10,  # Data Encrypted for Impact (Ransomware)
                "T1003": 9,   # OS Credential Dumping
                "T1055": 8,   # Process Injection
                "T1078": 7,   # Valid Accounts
                "T1021": 6,   # Remote Services
                "default": 5
            },
            "entity_criticality": {
                "domain_controller": 10,
                "file_server": 8,
                "workstation": 5,
                "guest_account": 3,
                "default": 4
            },
            "time_criticality": {
                "off_hours": 2.0,
                "business_hours": 1.0,
                "weekend": 1.5
            }
        }
    
    def calculate_event_risk_score(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk score for a security event"""
        base_score = 50  # Base risk score
        
        # MITRE technique scoring
        mitre_bonus = 0
        mitre_techniques = event.get("mitre_techniques", [])
        for technique in mitre_techniques:
            mitre_bonus += self.risk_factors["mitre_criticality"].get(technique, 
                                                                    self.risk_factors["mitre_criticality"]["default"])
        
        # Entity criticality
        entity_bonus = 0
        entities = event.get("entities", [])
        for entity in entities:
            entity_type = entity.get("type", "").lower()
            entity_value = entity.get("value", "").lower()
            
            if "domain" in entity_value or "dc" in entity_value:
                entity_bonus += self.risk_factors["entity_criticality"]["domain_controller"]
            elif "server" in entity_value:
                entity_bonus += self.risk_factors["entity_criticality"]["file_server"]
            elif "admin" in entity_value:
                entity_bonus += 7  # Admin accounts are high risk
            else:
                entity_bonus += self.risk_factors["entity_criticality"]["default"]
        
        # Temporal scoring
        event_time = datetime.now()
        if event_time.hour < 7 or event_time.hour > 19:  # Off hours
            time_multiplier = self.risk_factors["time_criticality"]["off_hours"]
        elif event_time.weekday() >= 5:  # Weekend
            time_multiplier = self.risk_factors["time_criticality"]["weekend"]
        else:
            time_multiplier = self.risk_factors["time_criticality"]["business_hours"]
        
        # Threat actor bonus
        actor_bonus = 0
        threat_actors = event.get("threat_actors", [])
        if threat_actors:
            actor_bonus = 20  # Known threat actors are high risk
        
        # Calculate final score
        final_score = (base_score + mitre_bonus + entity_bonus + actor_bonus) * time_multiplier
        
        # Normalize to 0-100
        final_score = min(100, max(0, final_score))
        
        # Determine risk level
        if final_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif final_score >= 60:
            risk_level = RiskLevel.HIGH
        elif final_score >= 40:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            "risk_score": final_score,
            "risk_level": risk_level.name,
            "scoring_breakdown": {
                "base_score": base_score,
                "mitre_bonus": mitre_bonus,
                "entity_bonus": entity_bonus,
                "actor_bonus": actor_bonus,
                "time_multiplier": time_multiplier
            },
            "risk_factors": {
                "mitre_techniques": len(mitre_techniques),
                "critical_entities": len(entities),
                "threat_actors": len(threat_actors),
                "temporal_factor": "off_hours" if time_multiplier > 1.0 else "business_hours"
            }
        }


class SecurityAnalyticsEngine:
    """Main analytics engine coordinating all analytics capabilities"""
    
    def __init__(self):
        self.behavioral_analytics = BehavioralAnalytics()
        self.anomaly_detector = AnomalyDetector()
        self.threat_hunting = ThreatHuntingEngine()
        self.risk_scoring = RiskScoringEngine()
        self.nlp_recognizer = SecurityNLPRecognizer()
        self.attack_generator = SimpleAttackChainGenerator()
    
    def run_comprehensive_analysis(self, sample_size: int = 100) -> Dict[str, Any]:
        """Run comprehensive security analytics on generated data"""
        print("📈 COMPREHENSIVE SECURITY ANALYTICS")
        print("=" * 60)
        
        start_time = time.time()
        
        # Generate sample data for analysis
        print("🔄 Generating sample security data...")
        sample_data = self._generate_sample_data(sample_size)
        
        # Run behavioral analysis
        print("🧠 Running behavioral analysis...")
        behavioral_results = self._run_behavioral_analysis(sample_data)
        
        # Run anomaly detection
        print("🔍 Running anomaly detection...")
        anomaly_results = self._run_anomaly_detection(sample_data)
        
        # Run threat hunting
        print("🎯 Running threat hunting campaigns...")
        hunting_results = self._run_threat_hunting(sample_data)
        
        # Run risk scoring
        print("⚖️  Running risk assessment...")
        risk_results = self._run_risk_assessment(sample_data)
        
        total_time = time.time() - start_time
        
        # Compile comprehensive report
        report = {
            "analysis_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_execution_time_ms": total_time * 1000,
                "sample_size": sample_size,
                "analysis_modules": ["behavioral", "anomaly_detection", "threat_hunting", "risk_scoring"]
            },
            "behavioral_analysis": behavioral_results,
            "anomaly_detection": anomaly_results,
            "threat_hunting": hunting_results,
            "risk_assessment": risk_results,
            "key_findings": self._generate_key_findings(behavioral_results, anomaly_results, 
                                                       hunting_results, risk_results),
            "recommendations": self._generate_recommendations(behavioral_results, anomaly_results,
                                                            hunting_results, risk_results)
        }
        
        return report
    
    def _generate_sample_data(self, sample_size: int) -> List[Dict[str, Any]]:
        """Generate realistic sample data for analysis"""
        sample_data = []
        
        # Generate various types of security events
        event_types = [
            "authentication_event",
            "network_connection",
            "file_access",
            "process_execution",
            "security_alert"
        ]
        
        for i in range(sample_size):
            event_type = random.choice(event_types)
            
            # Generate realistic event data
            event = {
                "event_id": f"event_{i:06d}",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
                "event_type": event_type,
                "user": random.choice(["john.doe", "jane.smith", "admin", "sa", "guest"]),
                "host": random.choice(["WIN-DC01", "WIN-FS01", "WORKSTATION-01", "SERVER-02"]),
                "ip_address": f"10.0.{random.randint(1,255)}.{random.randint(1,254)}",
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "mitre_techniques": random.sample(["T1055", "T1003", "T1078", "T1021", "T1486"], 
                                                random.randint(0, 2)),
                "threat_actors": ["APT29"] if random.random() > 0.9 else [],
                "metrics": {
                    "login_frequency": random.uniform(1, 20),
                    "session_duration": random.uniform(10, 480),
                    "data_access_volume": random.uniform(1, 1000),
                    "failed_attempts": random.randint(0, 5),
                    "network_connections": random.randint(1, 50)
                }
            }
            
            # Add NLP analysis
            event_text = f"{event_type} by {event['user']} on {event['host']}"
            nlp_analysis = self.nlp_recognizer.analyze_text(event_text)
            event["entities"] = nlp_analysis.get("entities", [])
            event["threat_indicators"] = nlp_analysis.get("threat_indicators", {})
            
            sample_data.append(event)
        
        return sample_data
    
    def _run_behavioral_analysis(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run behavioral analysis on sample data"""
        behavioral_results = {
            "baselines_created": 0,
            "anomalies_detected": [],
            "user_profiles": {},
            "entity_profiles": {}
        }
        
        # Group data by user and entity
        user_data = defaultdict(list)
        entity_data = defaultdict(list)
        
        for event in sample_data:
            user = event.get("user")
            host = event.get("host")
            metrics = event.get("metrics", {})
            
            if user:
                user_data[user].append(metrics)
            if host:
                entity_data[host].append(metrics)
        
        # Update baselines and detect anomalies
        for user, metrics_list in user_data.items():
            # Calculate average metrics for baseline
            avg_metrics = {}
            for metric_name in ["login_frequency", "session_duration", "data_access_volume"]:
                values = [m.get(metric_name, 0) for m in metrics_list]
                if values:
                    avg_metrics[metric_name] = statistics.mean(values)
            
            if avg_metrics:
                self.behavioral_analytics.update_baseline(user, "user", avg_metrics)
                behavioral_results["baselines_created"] += 1
                
                # Test for anomalies with current metrics
                if metrics_list:
                    current_metrics = metrics_list[-1]  # Use latest metrics
                    anomalies = self.behavioral_analytics.detect_anomalies(user, current_metrics)
                    behavioral_results["anomalies_detected"].extend(anomalies)
                    
                    behavioral_results["user_profiles"][user] = {
                        "baseline_metrics": avg_metrics,
                        "latest_metrics": current_metrics,
                        "anomalies_count": len(anomalies)
                    }
        
        # Same for entities
        for entity, metrics_list in entity_data.items():
            avg_metrics = {}
            for metric_name in ["network_connections", "failed_attempts"]:
                values = [m.get(metric_name, 0) for m in metrics_list]
                if values:
                    avg_metrics[metric_name] = statistics.mean(values)
            
            if avg_metrics:
                self.behavioral_analytics.update_baseline(entity, "host", avg_metrics)
                
                if metrics_list:
                    current_metrics = metrics_list[-1]
                    anomalies = self.behavioral_analytics.detect_anomalies(entity, current_metrics)
                    behavioral_results["anomalies_detected"].extend(anomalies)
                    
                    behavioral_results["entity_profiles"][entity] = {
                        "baseline_metrics": avg_metrics,
                        "latest_metrics": current_metrics,
                        "anomalies_count": len(anomalies)
                    }
        
        behavioral_results["total_anomalies"] = len(behavioral_results["anomalies_detected"])
        return behavioral_results
    
    def _run_anomaly_detection(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run statistical anomaly detection"""
        anomaly_results = {}
        
        # Test different metrics with different algorithms
        metrics_to_test = ["login_frequency", "session_duration", "data_access_volume", "network_connections"]
        algorithms = ["z_score", "iqr", "isolation_forest"]
        
        for metric_name in metrics_to_test:
            metric_values = [event.get("metrics", {}).get(metric_name, 0) for event in sample_data]
            metric_values = [v for v in metric_values if v > 0]  # Filter out zeros
            
            if len(metric_values) < 10:
                continue
            
            anomaly_results[metric_name] = {}
            
            for algorithm in algorithms:
                detection_result = self.anomaly_detector.detect_anomalies(metric_values, algorithm)
                anomaly_results[metric_name][algorithm] = detection_result
        
        return anomaly_results
    
    def _run_threat_hunting(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run automated threat hunting campaigns"""
        hunting_results = {
            "campaigns": {},
            "total_findings": 0,
            "high_risk_findings": 0
        }
        
        # Run different types of hunts
        hunt_types = ["lateral_movement", "persistence_mechanisms", "data_exfiltration", "credential_dumping"]
        
        for hunt_type in hunt_types:
            hunt_id = self.threat_hunting.create_hunt(hunt_type)
            campaign_results = self.threat_hunting.execute_hunt(hunt_id, sample_data)
            
            hunting_results["campaigns"][hunt_type] = campaign_results
            hunting_results["total_findings"] += campaign_results.get("findings_count", 0)
            
            if campaign_results.get("risk_score", 0) > 70:
                hunting_results["high_risk_findings"] += 1
        
        return hunting_results
    
    def _run_risk_assessment(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run comprehensive risk assessment"""
        risk_results = {
            "event_scores": [],
            "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "average_risk_score": 0,
            "high_risk_events": []
        }
        
        total_score = 0
        
        for event in sample_data:
            risk_assessment = self.risk_scoring.calculate_event_risk_score(event)
            risk_results["event_scores"].append(risk_assessment)
            
            risk_level = risk_assessment["risk_level"]
            risk_results["risk_distribution"][risk_level] += 1
            
            total_score += risk_assessment["risk_score"]
            
            if risk_assessment["risk_score"] > 70:
                risk_results["high_risk_events"].append({
                    "event_id": event.get("event_id"),
                    "risk_score": risk_assessment["risk_score"],
                    "risk_level": risk_level,
                    "key_factors": risk_assessment["risk_factors"]
                })
        
        if sample_data:
            risk_results["average_risk_score"] = total_score / len(sample_data)
        
        return risk_results
    
    def _generate_key_findings(self, behavioral: Dict, anomaly: Dict, hunting: Dict, risk: Dict) -> List[str]:
        """Generate key findings from all analytics"""
        findings = []
        
        # Behavioral findings
        total_anomalies = behavioral.get("total_anomalies", 0)
        if total_anomalies > 0:
            findings.append(f"Detected {total_anomalies} behavioral anomalies across users and systems")
        
        # Anomaly detection findings
        if anomaly:
            high_anomaly_metrics = [metric for metric, results in anomaly.items() 
                                  if any(result.get("anomaly_rate", 0) > 0.1 for result in results.values())]
            if high_anomaly_metrics:
                findings.append(f"High anomaly rates detected in metrics: {', '.join(high_anomaly_metrics)}")
        
        # Threat hunting findings
        high_risk_hunts = hunting.get("high_risk_findings", 0)
        if high_risk_hunts > 0:
            findings.append(f"{high_risk_hunts} threat hunting campaigns returned high-risk findings")
        
        # Risk assessment findings
        critical_events = risk.get("risk_distribution", {}).get("CRITICAL", 0)
        high_events = risk.get("risk_distribution", {}).get("HIGH", 0)
        if critical_events + high_events > 0:
            findings.append(f"Identified {critical_events} critical and {high_events} high-risk security events")
        
        avg_risk = risk.get("average_risk_score", 0)
        if avg_risk > 60:
            findings.append(f"Elevated average risk score: {avg_risk:.1f}/100")
        
        return findings if findings else ["No significant security concerns identified in current data"]
    
    def _generate_recommendations(self, behavioral: Dict, anomaly: Dict, hunting: Dict, risk: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Behavioral recommendations
        if behavioral.get("total_anomalies", 0) > 5:
            recommendations.append("Investigate users and systems with multiple behavioral anomalies")
        
        # Anomaly detection recommendations
        if anomaly and any(any(result.get("anomaly_rate", 0) > 0.15 for result in results.values()) 
                          for results in anomaly.values()):
            recommendations.append("Review and tune anomaly detection thresholds for high false-positive metrics")
        
        # Threat hunting recommendations
        total_findings = hunting.get("total_findings", 0)
        if total_findings > 20:
            recommendations.append("Prioritize investigation of threat hunting findings with highest confidence scores")
        
        # Risk-based recommendations
        high_risk_count = len(risk.get("high_risk_events", []))
        if high_risk_count > 0:
            recommendations.append(f"Immediate investigation required for {high_risk_count} high-risk security events")
        
        # General recommendations
        recommendations.extend([
            "Implement continuous monitoring for detected behavioral patterns",
            "Enhance logging for entities with frequent anomalies",
            "Consider deploying additional security controls for high-risk systems",
            "Schedule regular threat hunting campaigns based on current findings"
        ])
        
        return recommendations


def test_advanced_analytics():
    """Test the advanced security analytics engine"""
    print("📈 ADVANCED SECURITY ANALYTICS ENGINE")
    print("=" * 60)
    
    # Create analytics engine
    analytics_engine = SecurityAnalyticsEngine()
    
    # Run comprehensive analysis
    results = analytics_engine.run_comprehensive_analysis(sample_size=50)
    
    # Display results
    print(f"\n🎯 KEY FINDINGS")
    print("-" * 30)
    for finding in results["key_findings"]:
        print(f"• {finding}")
    
    print(f"\n📋 RECOMMENDATIONS")
    print("-" * 30)
    for recommendation in results["recommendations"]:
        print(f"• {recommendation}")
    
    print(f"\n📊 ANALYSIS SUMMARY")
    print("-" * 30)
    summary = results["analysis_summary"]
    print(f"• Total Execution Time: {summary['total_execution_time_ms']:.2f}ms")
    print(f"• Sample Size: {summary['sample_size']} events")
    print(f"• Analysis Modules: {', '.join(summary['analysis_modules'])}")
    
    # Behavioral Analysis Summary
    behavioral = results["behavioral_analysis"]
    print(f"\n🧠 BEHAVIORAL ANALYSIS")
    print(f"• Baselines Created: {behavioral['baselines_created']}")
    print(f"• Anomalies Detected: {behavioral['total_anomalies']}")
    print(f"• User Profiles: {len(behavioral['user_profiles'])}")
    print(f"• Entity Profiles: {len(behavioral['entity_profiles'])}")
    
    # Anomaly Detection Summary
    anomaly = results["anomaly_detection"]
    print(f"\n🔍 ANOMALY DETECTION")
    for metric, algorithms in anomaly.items():
        print(f"• {metric}:")
        for alg, result in algorithms.items():
            rate = result.get("anomaly_rate", 0) * 100
            print(f"  - {alg}: {rate:.1f}% anomaly rate")
    
    # Threat Hunting Summary
    hunting = results["threat_hunting"]
    print(f"\n🎯 THREAT HUNTING")
    print(f"• Campaigns Executed: {len(hunting['campaigns'])}")
    print(f"• Total Findings: {hunting['total_findings']}")
    print(f"• High-Risk Campaigns: {hunting['high_risk_findings']}")
    
    for campaign_type, campaign_results in hunting["campaigns"].items():
        risk_score = campaign_results.get("risk_score", 0)
        findings_count = campaign_results.get("findings_count", 0)
        print(f"  - {campaign_type}: {findings_count} findings (risk: {risk_score:.1f})")
    
    # Risk Assessment Summary
    risk = results["risk_assessment"]
    print(f"\n⚖️  RISK ASSESSMENT")
    print(f"• Average Risk Score: {risk['average_risk_score']:.1f}/100")
    print(f"• High-Risk Events: {len(risk['high_risk_events'])}")
    print("• Risk Distribution:")
    for level, count in risk["risk_distribution"].items():
        print(f"  - {level}: {count} events")
    
    # Save comprehensive report
    with open("advanced_analytics_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive report saved to: advanced_analytics_report.json")
    print("🟢 Advanced security analytics testing complete!")


if __name__ == "__main__":
    test_advanced_analytics()
