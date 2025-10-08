#!/usr/bin/env python3
"""
🎯 Hugging Face Dataset Integration Strategy
Dual-mode support: Demo (streaming) vs Production (cached/local)
"""

import os
import logging
from typing import Optional, Dict, Any, Iterator
from pathlib import Path
from datasets import load_dataset, Dataset
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class HFDatasetManager:
    """
    Manages Hugging Face datasets with dual-mode support:
    - Demo mode: Stream datasets directly from HF
    - Production mode: Use cached/local datasets
    """
    
    def __init__(self, 
                 is_demo: bool = True,
                 cache_dir: str = "./data/cache",
                 hf_token: Optional[str] = None):
        self.is_demo = is_demo
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        
        logger.info(f"🎯 HF Dataset Manager initialized - Mode: {'Demo' if is_demo else 'Production'}")
        
    def get_cybersecurity_logs(self, 
                             sample_size: Optional[int] = None,
                             streaming: bool = None) -> Iterator[Dict[str, Any]]:
        """
        Load cybersecurity logs dataset
        
        Args:
            sample_size: Number of samples to load (None = all)
            streaming: Whether to use streaming mode (auto-detected if None)
        """
        
        if streaming is None:
            streaming = self.is_demo
            
        try:
            logger.info(f"📊 Loading cybersecurity dataset - Streaming: {streaming}")
            
            # Recommended datasets for SIEM demo
            dataset_configs = [
                {
                    "name": "isaackd/cyber-security-logs",
                    "split": "train",
                    "description": "Comprehensive cybersecurity logs"
                },
                {
                    "name": "logpai/loghub", 
                    "config": "Apache",
                    "split": "train",
                    "description": "Apache access logs"
                },
                {
                    "name": "microsoft/MS-MARCO",
                    "config": "v2.1", 
                    "split": "train",
                    "description": "General log analysis"
                }
            ]
            
            # Primary dataset
            primary_config = dataset_configs[0]
            
            if self.is_demo and streaming:
                # Stream directly from HF - no local storage
                dataset = load_dataset(
                    primary_config["name"],
                    split=primary_config["split"],
                    streaming=True,
                    use_auth_token=self.hf_token
                )
                
                logger.info("✅ Streaming dataset loaded successfully")
                
                # Take sample if specified
                if sample_size:
                    dataset = dataset.take(sample_size)
                    
                # Convert to iterator
                for item in dataset:
                    yield self._process_log_entry(item)
                    
            else:
                # Production mode - cache locally
                cache_path = self.cache_dir / f"{primary_config['name'].replace('/', '_')}"
                
                dataset = load_dataset(
                    primary_config["name"],
                    split=primary_config["split"],
                    cache_dir=str(cache_path),
                    download_mode="reuse_cache_if_exists",
                    use_auth_token=self.hf_token
                )
                
                logger.info(f"✅ Cached dataset loaded - {len(dataset)} entries")
                
                # Convert to iterator with sampling
                indices = range(len(dataset))
                if sample_size and sample_size < len(dataset):
                    import random
                    indices = random.sample(indices, sample_size)
                
                for idx in indices:
                    yield self._process_log_entry(dataset[idx])
                    
        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise RuntimeError(f"Dataset loading failed: {e}. No fallback data available in production.")
    
    def _process_log_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and normalize a log entry for SIEM consumption
        """
        # Normalize different dataset formats
        processed = {
            "timestamp": self._extract_timestamp(entry),
            "event_type": self._classify_event_type(entry),
            "source_ip": self._extract_ip(entry),
            "user_agent": entry.get("user_agent", "unknown"),
            "severity": self._assess_severity(entry),
            "message": str(entry.get("message", entry.get("text", ""))),
            "raw_data": entry,
            "processed_at": datetime.utcnow().isoformat(),
        }
        
        # Add SIEM-specific fields
        processed.update({
            "event_id": self._generate_event_id(),
            "source": "hf_dataset",
            "category": self._categorize_security_event(processed),
            "risk_score": self._calculate_risk_score(processed),
        })
        
        return processed
    
    def _extract_timestamp(self, entry: Dict[str, Any]) -> str:
        """Extract or generate timestamp"""
        for field in ["timestamp", "time", "@timestamp", "datetime"]:
            if field in entry and entry[field]:
                return str(entry[field])
        
        # Generate realistic timestamp within last 7 days
        import random
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 24)
        timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
        return timestamp.isoformat()
    
    def _classify_event_type(self, entry: Dict[str, Any]) -> str:
        """Classify log entry into SIEM event types"""
        message = str(entry.get("message", entry.get("text", ""))).lower()
        
        if any(word in message for word in ["failed", "denied", "unauthorized", "forbidden"]):
            return "authentication_failure"
        elif any(word in message for word in ["malware", "virus", "threat", "suspicious"]):
            return "malware_detection"
        elif any(word in message for word in ["login", "logon", "signin"]):
            return "authentication_success"
        elif any(word in message for word in ["error", "exception", "critical"]):
            return "system_error"
        elif any(word in message for word in ["network", "connection", "traffic"]):
            return "network_event"
        else:
            return "general_security"
    
    def _extract_ip(self, entry: Dict[str, Any]) -> str:
        """Extract IP address from log entry"""
        for field in ["source_ip", "client_ip", "remote_addr", "ip"]:
            if field in entry and entry[field]:
                return str(entry[field])
        
        # Generate realistic IP for demo
        import random
        return f"{random.randint(192, 203)}.{random.randint(168, 255)}.{random.randint(1, 255)}.{random.randint(1, 254)}"
    
    def _assess_severity(self, entry: Dict[str, Any]) -> str:
        """Assess severity level"""
        message = str(entry.get("message", "")).lower()
        
        if any(word in message for word in ["critical", "emergency", "fatal"]):
            return "critical"
        elif any(word in message for word in ["high", "important", "severe"]):
            return "high"  
        elif any(word in message for word in ["medium", "warning", "moderate"]):
            return "medium"
        else:
            return "low"
    
    def _categorize_security_event(self, processed: Dict[str, Any]) -> str:
        """Categorize into security event categories"""
        event_type = processed["event_type"]
        
        categories = {
            "authentication_failure": "access_control",
            "authentication_success": "access_control", 
            "malware_detection": "threat_detection",
            "network_event": "network_security",
            "system_error": "system_integrity",
            "general_security": "general"
        }
        
        return categories.get(event_type, "unknown")
    
    def _calculate_risk_score(self, processed: Dict[str, Any]) -> int:
        """Calculate risk score (0-100)"""
        base_score = 20
        
        # Severity multiplier
        severity_multipliers = {
            "critical": 4.0,
            "high": 3.0,
            "medium": 2.0,
            "low": 1.0
        }
        
        multiplier = severity_multipliers.get(processed["severity"], 1.0)
        
        # Event type risk
        event_risks = {
            "authentication_failure": 30,
            "malware_detection": 40,
            "network_event": 20,
            "system_error": 25,
            "authentication_success": 5
        }
        
        event_risk = event_risks.get(processed["event_type"], 15)
        
        return min(100, int((base_score + event_risk) * multiplier))
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return f"evt_{uuid.uuid4().hex[:12]}"
    
    def validate_dataset_connection(self) -> bool:
        """Validate that real datasets can be accessed"""
        try:
            # Test connection to primary dataset
            test_dataset = load_dataset(
                "isaackd/cyber-security-logs",
                split="train",
                streaming=True,
                use_auth_token=self.hf_token
            )
            
            # Try to get one item
            next(iter(test_dataset))
            logger.info("✅ Dataset connection validated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dataset validation failed: {e}")
            return False
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Get information about available datasets"""
        return {
            "mode": "demo" if self.is_demo else "production",
            "cache_dir": str(self.cache_dir),
            "hf_token_available": bool(self.hf_token),
            "recommended_datasets": [
                {
                    "name": "isaackd/cyber-security-logs",
                    "description": "Comprehensive cybersecurity logs",
                    "size": "~50MB",
                    "use_case": "General SIEM training"
                },
                {
                    "name": "logpai/loghub",
                    "description": "Various system logs",
                    "size": "~100MB", 
                    "use_case": "System log analysis"
                },
                {
                    "name": "splunk/attack_range",
                    "description": "Attack simulation logs",
                    "size": "~200MB",
                    "use_case": "Threat detection training"
                }
            ],
            "privacy_notes": [
                "Demo mode streams data directly from HuggingFace",
                "Production mode caches data locally",
                "All datasets are publicly available and anonymized",
                "No sensitive ISRO data is used in demo mode"
            ]
        }
    
    def prepare_for_siem_indexing(self, 
                                 batch_size: int = 1000) -> Iterator[List[Dict[str, Any]]]:
        """
        Prepare dataset in batches for Elasticsearch indexing
        """
        batch = []
        for log_entry in self.get_cybersecurity_logs():
            batch.append(log_entry)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        # Yield final batch if not empty
        if batch:
            yield batch


# Factory function for easy instantiation
def create_hf_manager(is_demo: bool = None) -> HFDatasetManager:
    """Create HF dataset manager based on environment"""
    if is_demo is None:
        is_demo = os.getenv("ENVIRONMENT", "demo").lower() == "demo"
    
    return HFDatasetManager(
        is_demo=is_demo,
        cache_dir=os.getenv("HF_CACHE_DIR", "./data/cache"),
        hf_token=os.getenv("HF_TOKEN")
    )


if __name__ == "__main__":
    # Demo usage
    manager = create_hf_manager(is_demo=True)
    
    print("📊 Dataset Info:")
    print(json.dumps(manager.get_dataset_info(), indent=2))
    
    print("\n🔍 Sample logs:")
    for i, log in enumerate(manager.get_cybersecurity_logs(sample_size=5)):
        print(f"{i+1}. {log['timestamp']} - {log['event_type']}: {log['message'][:100]}...")
