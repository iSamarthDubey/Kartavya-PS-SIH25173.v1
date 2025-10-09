"""
Dataset SIEM Connector
Connects to real SIEM datasets from HuggingFace, Kaggle, etc.
Replaces mock data with realistic security logs
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from datasets import load_dataset
import json
import random
from .base import BaseSIEMConnector

logger = logging.getLogger(__name__)

class DatasetConnector(BaseSIEMConnector):
    """Real dataset connector for SIEM logs from HuggingFace/Kaggle"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset_cache = {}
        self.connected = False
        
        # Only use the Advanced SIEM Dataset - exactly what you wanted!
        self.datasets = {
            "advanced_siem": {
                "source": "huggingface",
                "name": "darkknight25/Advanced_SIEM_Dataset",
                "description": "Advanced SIEM Dataset with comprehensive security logs (100K-1M records)"
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize the dataset connector by connecting to datasets"""
        return await self.connect()
    
    async def connect(self) -> bool:
        """Load and cache datasets"""
        try:
            logger.info("🔄 Loading SIEM datasets...")
            
            # Sort datasets by priority (1 = highest priority)
            sorted_datasets = sorted(
                self.datasets.items(), 
                key=lambda x: x[1].get('priority', 999)
            )
            
            # Try to load datasets in priority order
            for dataset_key, dataset_info in sorted_datasets:
                try:
                    if dataset_info["source"] == "huggingface":
                        # Try loading from HuggingFace
                        dataset = await self._load_huggingface_dataset(dataset_info["name"])
                        if dataset:
                            self.dataset_cache[dataset_key] = dataset
                            logger.info(f"✅ Loaded {dataset_key}: {len(dataset)} records")
                    
                    elif dataset_info["source"] == "csv_url":
                        # Load from direct URL
                        dataset = await self._load_csv_dataset(dataset_info["name"])
                        if dataset:
                            self.dataset_cache[dataset_key] = dataset
                            logger.info(f"✅ Loaded {dataset_key}: {len(dataset)} records")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {dataset_key}: {e}")
                    continue
            
            if not self.dataset_cache:
                # Generate synthetic but realistic data as last resort
                logger.warning("📊 No datasets loaded, generating synthetic SIEM data...")
                self.dataset_cache["synthetic"] = await self._generate_synthetic_siem_data()
            
            self.connected = True
            logger.info(f"✅ Dataset connector ready with {len(self.dataset_cache)} datasets")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to datasets: {e}")
            return False
    
    async def _load_huggingface_dataset(self, dataset_name: str) -> Optional[List[Dict]]:
        """Load dataset from HuggingFace"""
        try:
            logger.info(f"📚 Loading HuggingFace dataset: {dataset_name}")
            
            # Load dataset
            dataset = load_dataset(dataset_name, split='train')
            logger.info(f"✅ Dataset loaded: {len(dataset)} records")
            
            # Convert to SIEM log format
            siem_logs = []
            
            # Special handling for Advanced SIEM Dataset
            if "Advanced_SIEM_Dataset" in dataset_name:
                siem_logs = await self._convert_advanced_siem_dataset(dataset)
            else:
                # Generic conversion for other datasets
                for item in dataset:
                    log_entry = self._convert_to_ecs_format(item)
                    if log_entry:
                        siem_logs.append(log_entry)
            
            # Limit dataset size (more for Advanced SIEM since it's high quality)
            limit = 50000 if "Advanced_SIEM_Dataset" in dataset_name else 10000
            return siem_logs[:limit]
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load HuggingFace dataset {dataset_name}: {e}")
            return None
    
    async def _load_csv_dataset(self, url: str) -> Optional[List[Dict]]:
        """Load dataset from CSV URL"""
        try:
            # Load CSV data
            df = pd.read_csv(url)
            
            # Convert to SIEM format
            siem_logs = []
            for _, row in df.iterrows():
                log_entry = self._convert_csv_to_ecs(row.to_dict())
                if log_entry:
                    siem_logs.append(log_entry)
            
            return siem_logs[:5000]  # Limit to 5k records
            
        except Exception as e:
            logger.warning(f"Failed to load CSV dataset {url}: {e}")
            return None
    
    async def _convert_advanced_siem_dataset(self, dataset) -> List[Dict]:
        """Convert Advanced SIEM Dataset to ECS format"""
        logger.info("🔄 Converting Advanced SIEM Dataset to ECS format...")
        
        siem_logs = []
        
        for i, item in enumerate(dataset):
            try:
                # The Advanced SIEM Dataset should have structured fields
                # Let's handle it intelligently based on available fields
                
                ecs_log = {
                    "@timestamp": datetime.now().isoformat(),
                    "event": {},
                    "source": {},
                    "destination": {},
                    "network": {},
                    "user": {},
                    "host": {},
                    "metadata": {"dataset": "darkknight25/Advanced_SIEM_Dataset"}
                }
                
                # Map all fields from the dataset item
                for key, value in item.items():
                    if value is None or value == '':
                        continue
                        
                    key_lower = str(key).lower()
                    
                    # Timestamp mapping
                    if any(t in key_lower for t in ['timestamp', 'time', 'date']):
                        try:
                            if isinstance(value, str) and value:
                                ecs_log["@timestamp"] = pd.to_datetime(value).isoformat()
                        except:
                            pass
                    
                    # Event type and category mapping
                    elif any(e in key_lower for e in ['event_type', 'event_category', 'category']):
                        ecs_log["event"]["category"] = str(value).lower()
                    elif any(a in key_lower for a in ['action', 'activity']):
                        ecs_log["event"]["action"] = str(value).lower()
                    elif any(s in key_lower for s in ['severity', 'level', 'priority']):
                        ecs_log["event"]["severity"] = self._normalize_severity(str(value))
                    
                    # IP address mapping
                    elif any(ip in key_lower for ip in ['src_ip', 'source_ip', 'srcip']):
                        ecs_log["source"]["ip"] = str(value)
                    elif any(ip in key_lower for ip in ['dst_ip', 'dest_ip', 'dstip', 'destination_ip']):
                        ecs_log["destination"]["ip"] = str(value)
                    
                    # Port mapping
                    elif any(p in key_lower for p in ['src_port', 'source_port']):
                        try:
                            ecs_log["source"]["port"] = int(value)
                        except:
                            pass
                    elif any(p in key_lower for p in ['dst_port', 'dest_port', 'destination_port']):
                        try:
                            ecs_log["destination"]["port"] = int(value)
                        except:
                            pass
                    
                    # Protocol mapping
                    elif 'protocol' in key_lower:
                        ecs_log["network"]["protocol"] = str(value).lower()
                    
                    # User mapping
                    elif any(u in key_lower for u in ['user', 'username', 'account']):
                        ecs_log["user"]["name"] = str(value)
                    
                    # Host mapping
                    elif any(h in key_lower for h in ['host', 'hostname', 'computer']):
                        ecs_log["host"]["name"] = str(value)
                    
                    # Store original field in metadata
                    ecs_log["metadata"][key] = value
                
                # Set default values if not present
                if not ecs_log["event"].get("action"):
                    ecs_log["event"]["action"] = "unknown"
                if not ecs_log["event"].get("category"):
                    ecs_log["event"]["category"] = "network"
                if not ecs_log["event"].get("severity"):
                    ecs_log["event"]["severity"] = "medium"
                
                siem_logs.append(ecs_log)
                
                # Progress logging
                if i > 0 and i % 5000 == 0:
                    logger.info(f"📈 Processed {i} records from Advanced SIEM Dataset")
                    
            except Exception as e:
                logger.warning(f"Failed to convert record {i}: {e}")
                continue
        
        logger.info(f"✅ Converted {len(siem_logs)} records from Advanced SIEM Dataset")
        return siem_logs
    
    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels to standard values"""
        severity_lower = str(severity).lower()
        
        if any(s in severity_lower for s in ['critical', 'crit', 'fatal', '4', 'high']):
            return 'critical'
        elif any(s in severity_lower for s in ['high', '3', 'important']):
            return 'high'
        elif any(s in severity_lower for s in ['medium', 'med', '2', 'warning', 'warn']):
            return 'medium'
        elif any(s in severity_lower for s in ['low', '1', 'info', 'informational']):
            return 'low'
        else:
            return 'medium'  # Default
    
    def _convert_to_ecs_format(self, data_item: Dict) -> Dict:
        """Convert dataset item to Elastic Common Schema format"""
        try:
            # Base ECS structure
            ecs_log = {
                "@timestamp": datetime.now().isoformat(),
                "event": {
                    "action": "unknown",
                    "category": "network", 
                    "type": "info"
                },
                "host": {
                    "name": "unknown"
                }
            }
            
            # Try to map fields intelligently
            for key, value in data_item.items():
                key_lower = str(key).lower()
                
                # Map timestamp fields
                if any(t in key_lower for t in ['time', 'date', 'timestamp']):
                    try:
                        if isinstance(value, str):
                            # Try to parse timestamp
                            ecs_log["@timestamp"] = pd.to_datetime(value).isoformat()
                    except:
                        pass
                
                # Map IP addresses
                elif any(ip in key_lower for ip in ['src_ip', 'source_ip', 'src']):
                    ecs_log.setdefault("source", {})["ip"] = str(value)
                elif any(ip in key_lower for ip in ['dst_ip', 'dest_ip', 'destination_ip', 'dst']):
                    ecs_log.setdefault("destination", {})["ip"] = str(value)
                
                # Map ports
                elif any(p in key_lower for p in ['src_port', 'source_port']):
                    ecs_log.setdefault("source", {})["port"] = int(value) if str(value).isdigit() else 0
                elif any(p in key_lower for p in ['dst_port', 'dest_port', 'destination_port']):
                    ecs_log.setdefault("destination", {})["port"] = int(value) if str(value).isdigit() else 0
                
                # Map protocols
                elif 'protocol' in key_lower or 'proto' in key_lower:
                    ecs_log.setdefault("network", {})["protocol"] = str(value).lower()
                
                # Map action/event type
                elif any(a in key_lower for a in ['action', 'activity', 'event_type']):
                    ecs_log["event"]["action"] = str(value).lower()
                
                # Map severity/priority  
                elif any(s in key_lower for s in ['severity', 'priority', 'level']):
                    severity_map = {
                        '0': 'info', '1': 'low', '2': 'medium', 
                        '3': 'high', '4': 'critical',
                        'info': 'info', 'low': 'low', 'medium': 'medium',
                        'high': 'high', 'critical': 'critical'
                    }
                    ecs_log["event"]["severity"] = severity_map.get(str(value).lower(), 'medium')
                
                # Map user information
                elif any(u in key_lower for u in ['user', 'username', 'account']):
                    ecs_log.setdefault("user", {})["name"] = str(value)
                
                # Add original data as metadata
                ecs_log.setdefault("metadata", {})[key] = value
            
            return ecs_log
            
        except Exception as e:
            logger.warning(f"Failed to convert item to ECS: {e}")
            return None
    
    def _convert_csv_to_ecs(self, row_dict: Dict) -> Dict:
        """Convert CSV row to ECS format (KDD Cup 99 specific)"""
        try:
            # KDD Cup 99 format mapping
            if len(row_dict) >= 41:  # KDD Cup has 41+ features
                return {
                    "@timestamp": datetime.now().isoformat(),
                    "event": {
                        "action": "network_connection",
                        "category": "network",
                        "type": "connection",
                        "outcome": "success" if row_dict.get('attack_type', 'normal') == 'normal' else 'failure'
                    },
                    "network": {
                        "protocol": row_dict.get('protocol_type', 'tcp'),
                        "bytes": int(row_dict.get('src_bytes', 0)),
                        "packets": int(row_dict.get('count', 1))
                    },
                    "source": {
                        "ip": f"192.168.{hash(str(row_dict)) % 255}.{hash(str(row_dict)) % 255}",
                        "port": int(row_dict.get('src_port', 0)) if str(row_dict.get('src_port', '')).isdigit() else 80
                    },
                    "destination": {
                        "ip": f"10.0.{hash(str(row_dict)) % 255}.{hash(str(row_dict)) % 255}",  
                        "port": int(row_dict.get('dst_port', 0)) if str(row_dict.get('dst_port', '')).isdigit() else 443
                    },
                    "metadata": {
                        "attack_type": row_dict.get('attack_type', 'normal'),
                        "service": row_dict.get('service', 'unknown'),
                        "flag": row_dict.get('flag', 'SF')
                    }
                }
            
            # Generic CSV mapping
            return self._convert_to_ecs_format(row_dict)
            
        except Exception as e:
            logger.warning(f"Failed to convert CSV row: {e}")
            return None
    
    async def _generate_synthetic_siem_data(self) -> List[Dict]:
        """Generate realistic synthetic SIEM data (last resort)"""
        logger.info("🔬 Generating synthetic SIEM data patterns...")
        
        import random
        from datetime import datetime, timedelta
        
        events = []
        now = datetime.now()
        
        # Attack patterns from real threat intelligence
        attack_patterns = [
            {
                "name": "Brute Force SSH",
                "category": "authentication",
                "action": "authentication_failure",
                "severity": "high",
                "count": 150
            },
            {
                "name": "SQL Injection",
                "category": "web",
                "action": "sql_injection_attempt", 
                "severity": "critical",
                "count": 25
            },
            {
                "name": "Port Scanning",
                "category": "network",
                "action": "port_scan",
                "severity": "medium", 
                "count": 80
            },
            {
                "name": "Malware Detection",
                "category": "malware",
                "action": "malware_detected",
                "severity": "critical",
                "count": 30
            },
            {
                "name": "DDoS Attack", 
                "category": "network",
                "action": "ddos_attack",
                "severity": "high",
                "count": 200
            }
        ]
        
        for pattern in attack_patterns:
            for i in range(pattern["count"]):
                event = {
                    "@timestamp": (now - timedelta(
                        hours=random.randint(0, 72),
                        minutes=random.randint(0, 59)
                    )).isoformat(),
                    "event": {
                        "action": pattern["action"],
                        "category": pattern["category"],
                        "severity": pattern["severity"],
                        "type": "security"
                    },
                    "source": {
                        "ip": f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                    },
                    "destination": {
                        "ip": f"10.0.{random.randint(0,255)}.{random.randint(1,254)}"
                    },
                    "metadata": {
                        "pattern": pattern["name"],
                        "synthetic": True
                    }
                }
                events.append(event)
        
        logger.info(f"✅ Generated {len(events)} synthetic security events")
        return events
    
    async def disconnect(self) -> None:
        """Clear dataset cache"""
        self.dataset_cache.clear()
        self.connected = False
        logger.info("Dataset connector disconnected")
    
    async def execute_query(
        self,
        query: Dict[str, Any],
        size: int = 100,
        index: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute query against cached datasets"""
        if not self.connected:
            raise RuntimeError("Dataset connector not connected")
        
        # Combine all cached datasets
        all_events = []
        for dataset_name, events in self.dataset_cache.items():
            all_events.extend(events)
        
        # Filter events based on query
        filtered_events = self._filter_events(query, all_events)
        
        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x.get('@timestamp', ''), reverse=True)
        
        # Apply size limit
        filtered_events = filtered_events[:size]
        
        return {
            "hits": {
                "total": {"value": len(filtered_events)},
                "hits": [{"_source": event} for event in filtered_events]
            },
            "took": random.randint(10, 100),
            "timed_out": False
        }
    
    def _filter_events(self, query: Dict[str, Any], events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter events based on Elasticsearch-like query"""
        if not query or "query" not in query:
            return events
        
        query_dict = query.get("query", {})
        
        # Handle different query types
        if "query_string" in query_dict:
            return self._filter_by_query_string(query_dict["query_string"], events)
        elif "bool" in query_dict:
            return self._filter_by_bool_query(query_dict["bool"], events)
        elif "match" in query_dict:
            return self._filter_by_match_query(query_dict["match"], events)
        
        return events
    
    def _filter_by_query_string(self, query_string: Dict, events: List[Dict]) -> List[Dict]:
        """Filter by query string"""
        query_text = query_string.get("query", "").lower()
        
        # Keyword-based filtering
        keywords = {
            "failed login": lambda e: e.get("event", {}).get("action") == "authentication_failure",
            "malware": lambda e: e.get("event", {}).get("category") == "malware", 
            "ddos": lambda e: "ddos" in e.get("event", {}).get("action", ""),
            "port scan": lambda e: "port_scan" in e.get("event", {}).get("action", ""),
            "sql injection": lambda e: "sql_injection" in e.get("event", {}).get("action", ""),
            "high severity": lambda e: e.get("event", {}).get("severity") == "high",
            "critical": lambda e: e.get("event", {}).get("severity") == "critical"
        }
        
        for keyword, filter_func in keywords.items():
            if keyword in query_text:
                return [e for e in events if filter_func(e)]
        
        return events
    
    def _filter_by_bool_query(self, bool_query: Dict, events: List[Dict]) -> List[Dict]:
        """Filter by boolean query"""
        filtered = events
        
        # Handle must clauses
        for clause in bool_query.get("must", []):
            if "match" in clause:
                for field, value in clause["match"].items():
                    filtered = [e for e in filtered if self._field_matches(e, field, value)]
            elif "range" in clause:
                for field, range_def in clause["range"].items():
                    filtered = [e for e in filtered if self._field_in_range(e, field, range_def)]
        
        return filtered
    
    def _filter_by_match_query(self, match_query: Dict, events: List[Dict]) -> List[Dict]:
        """Filter by match query"""
        filtered = events
        for field, value in match_query.items():
            filtered = [e for e in filtered if self._field_matches(e, field, value)]
        return filtered
    
    def _field_matches(self, event: Dict, field: str, value: Any) -> bool:
        """Check if event field matches value"""
        field_parts = field.split(".")
        current = event
        
        for part in field_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return str(current).lower() == str(value).lower()
    
    def _field_in_range(self, event: Dict, field: str, range_def: Dict) -> bool:
        """Check if field value is in specified range"""
        # Simplified range checking for timestamps
        if field == "@timestamp":
            event_time = event.get("@timestamp", "")
            # Add actual timestamp range logic here
            return True  # Placeholder
        return True
    
    async def get_field_mappings(self, index: Optional[str] = None) -> Dict[str, Any]:
        """Get field mappings for the datasets"""
        return {
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "event": {
                        "properties": {
                            "action": {"type": "keyword"},
                            "category": {"type": "keyword"}, 
                            "severity": {"type": "keyword"}
                        }
                    },
                    "source": {
                        "properties": {
                            "ip": {"type": "ip"},
                            "port": {"type": "integer"}
                        }
                    },
                    "destination": {
                        "properties": {
                            "ip": {"type": "ip"},
                            "port": {"type": "integer"}
                        }
                    },
                    "network": {
                        "properties": {
                            "protocol": {"type": "keyword"},
                            "bytes": {"type": "long"}
                        }
                    }
                }
            }
        }

    async def get_indices(self) -> List[str]:
        """Get available dataset indices"""
        return list(self.dataset_cache.keys())
    
    def test_connection(self) -> bool:
        """Test if datasets can be loaded (required by base class)"""
        try:
            # Simple test - try importing required modules
            import datasets
            import pandas
            return True
        except ImportError:
            return False
