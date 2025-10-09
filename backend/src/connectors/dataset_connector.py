"""
Simple Dataset SIEM Connector
Two simple steps:
1. Use local JSONL file if it exists
2. Download from HuggingFace and save locally if not present
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from datasets import load_dataset
from pathlib import Path
from .base import BaseSIEMConnector

logger = logging.getLogger(__name__)

class DatasetConnector(BaseSIEMConnector):
    """Simple dataset connector - local file first, then HuggingFace download"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset_cache = {}
        self.connected = False
        
        # Setup data directory
        current_dir = Path(__file__).parent
        self.data_dir = current_dir.parent.parent.parent / "backend" / "data" / "datasets"
        
        # Dataset configuration
        self.datasets = {
            "advanced_siem": {
                "local_path": self.data_dir / "Advanced_SIEM_Dataset" / "advanced_siem_dataset.jsonl",
                "hf_name": "darkknight25/Advanced_SIEM_Dataset",
                "description": "Advanced SIEM Dataset with comprehensive security logs"
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize the dataset connector"""
        return await self.connect()
    
    async def connect(self) -> bool:
        """Load datasets: local file first, then HuggingFace download"""
        try:
            logger.info("🔄 Loading SIEM datasets...")
            
            for dataset_key, dataset_info in self.datasets.items():
                local_path = dataset_info["local_path"]
                hf_name = dataset_info["hf_name"]
                
                # 📁 STEP 1: Check if local JSONL file exists
                if local_path.exists():
                    logger.info(f"📁 Found local file: {local_path.name}")
                    dataset = await self._load_local_jsonl(local_path)
                    if dataset:
                        self.dataset_cache[dataset_key] = dataset
                        logger.info(f"✅ Loaded {len(dataset)} records from local file")
                        continue
                
                # 📥 STEP 2: Download from HuggingFace and save
                logger.info(f"📥 Local file not found, downloading from HuggingFace...")
                dataset = await self._download_and_save_hf(hf_name, local_path)
                if dataset:
                    self.dataset_cache[dataset_key] = dataset
                    logger.info(f"✅ Downloaded and saved {len(dataset)} records")
            
            # Check if we loaded anything
            if not self.dataset_cache:
                logger.error("❌ No datasets loaded!")
                return False
            
            self.connected = True
            logger.info(f"✅ Dataset connector ready with {len(self.dataset_cache)} datasets")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load datasets: {e}")
            return False
    
    async def _load_local_jsonl(self, file_path: Path) -> Optional[List[Dict]]:
        """Load JSONL file from local disk"""
        try:
            logger.info(f"📖 Reading JSONL file: {file_path}")
            
            dataset = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    if line.strip():
                        try:
                            record = json.loads(line)
                            # Convert to ECS format
                            ecs_record = self._convert_to_ecs(record)
                            if ecs_record:
                                dataset.append(ecs_record)
                                
                            # Log progress every 10k records
                            if len(dataset) % 10000 == 0:
                                logger.info(f"📈 Processed {len(dataset)} records...")
                                
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ Invalid JSON on line {line_num + 1}")
                            continue
                    
                    # Limit to 50k records for performance
                    if len(dataset) >= 50000:
                        logger.info("📊 Limiting to 50,000 records for optimal performance")
                        break
            
            logger.info(f"📁 Loaded {len(dataset)} records from local JSONL file")
            return dataset
            
        except Exception as e:
            logger.error(f"❌ Failed to load local JSONL {file_path}: {e}")
            return None
    
    async def _download_and_save_hf(self, hf_name: str, save_path: Path) -> Optional[List[Dict]]:
        """Download from HuggingFace and save to local JSONL file"""
        try:
            logger.info(f"📥 Downloading dataset: {hf_name}")
            
            # Download from HuggingFace
            hf_dataset = load_dataset(hf_name, split='train')
            logger.info(f"✅ Downloaded {len(hf_dataset)} records from HuggingFace")
            
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert and save to JSONL
            logger.info(f"💾 Saving to local file: {save_path}")
            
            dataset = []
            with open(save_path, 'w', encoding='utf-8') as f:
                for i, record in enumerate(hf_dataset):
                    # Convert to ECS format
                    ecs_record = self._convert_to_ecs(record)
                    if ecs_record:
                        # Save to JSONL file
                        f.write(json.dumps(ecs_record) + '\n')
                        dataset.append(ecs_record)
                        
                        # Log progress
                        if len(dataset) % 10000 == 0:
                            logger.info(f"📈 Processed {len(dataset)} records...")
                    
                    # Limit to 50k records
                    if len(dataset) >= 50000:
                        logger.info("📊 Limiting to 50,000 records for optimal performance")
                        break
            
            logger.info(f"✅ Saved {len(dataset)} records to {save_path}")
            logger.info(f"📁 Next time startup will be MUCH faster using local file!")
            
            return dataset
            
        except Exception as e:
            logger.error(f"❌ Failed to download and save {hf_name}: {e}")
            return None
    
    def _convert_to_ecs(self, record: Dict) -> Optional[Dict]:
        """Convert dataset record to ECS (Elastic Common Schema) format"""
        try:
            ecs_record = {
                "@timestamp": datetime.now().isoformat(),
                "event": {},
                "source": {},
                "destination": {},
                "network": {},
                "user": {},
                "host": {},
                "metadata": {"dataset": "advanced_siem"}
            }
            
            # Map fields from the record
            for key, value in record.items():
                if value is None or value == '':
                    continue
                    
                key_lower = str(key).lower()
                
                # Map common SIEM fields
                if 'timestamp' in key_lower or 'time' in key_lower:
                    try:
                        ecs_record["@timestamp"] = str(value)
                    except:
                        pass
                elif 'severity' in key_lower or 'level' in key_lower:
                    ecs_record["event"]["severity"] = str(value).lower()
                elif 'action' in key_lower or 'activity' in key_lower:
                    ecs_record["event"]["action"] = str(value).lower()
                elif 'src_ip' in key_lower or 'source_ip' in key_lower:
                    ecs_record["source"]["ip"] = str(value)
                elif 'dst_ip' in key_lower or 'dest_ip' in key_lower:
                    ecs_record["destination"]["ip"] = str(value)
                elif 'protocol' in key_lower:
                    ecs_record["network"]["protocol"] = str(value).lower()
                elif 'user' in key_lower:
                    ecs_record["user"]["name"] = str(value)
                elif 'message' in key_lower or 'description' in key_lower:
                    ecs_record["message"] = str(value)
                else:
                    # Store unmapped fields in metadata
                    ecs_record["metadata"][key] = value
            
            return ecs_record
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to convert record: {e}")
            return None
    
    async def execute_query(self, query: Dict[str, Any], size: int = 100) -> List[Dict]:
        """Execute query against loaded dataset"""
        try:
            if not self.connected or not self.dataset_cache:
                logger.error("❌ Dataset not loaded!")
                return []
            
            # Get the dataset (assuming we only have one)
            dataset_key = list(self.dataset_cache.keys())[0]
            dataset = self.dataset_cache[dataset_key]
            
            # Simple filtering based on query
            query_text = query.get("query", "").lower()
            
            if query_text == "*" or not query_text:
                # Return random sample
                import random
                results = random.sample(dataset, min(size, len(dataset)))
            else:
                # Filter by text search
                results = []
                for record in dataset:
                    record_text = json.dumps(record).lower()
                    if query_text in record_text:
                        results.append(record)
                        if len(results) >= size:
                            break
                
                # If no matches, return random sample
                if not results:
                    results = random.sample(dataset, min(size, len(dataset)))
            
            logger.info(f"🔍 Query executed: {len(results)} results returned")
            return results
            
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return []
    
    async def disconnect(self) -> bool:
        """Disconnect from dataset (simple cleanup)"""
        self.connected = False
        self.dataset_cache.clear()
        logger.info("📤 Dataset connector disconnected")
        return True
    
    async def test_connection(self) -> bool:
        """Test if dataset is loaded and ready"""
        return self.connected and len(self.dataset_cache) > 0
    
    async def get_field_mappings(self) -> Dict[str, str]:
        """Get field mappings for this connector"""
        return {
            "timestamp": "@timestamp",
            "source_ip": "source.ip", 
            "destination_ip": "destination.ip",
            "severity": "event.severity",
            "action": "event.action",
            "protocol": "network.protocol",
            "user": "user.name",
            "message": "message"
        }
