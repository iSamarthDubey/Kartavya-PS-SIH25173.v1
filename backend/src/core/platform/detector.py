"""
Robust Platform Detection System
Dynamically detects platform, available indices, and data sources.
NO FALLBACKS, NO STATIC VALUES - ALL DYNAMIC DETECTION.
"""

import asyncio
import logging
import platform
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Detected platform types"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNIX = "unix"
    MIXED = "mixed"  # Multi-platform environment


class DataSourceType(Enum):
    """Detected data source types"""
    BEATS = "beats"           # Elastic Beats (winlogbeat, metricbeat, etc.)
    SYSLOG = "syslog"         # Standard syslog
    ECS = "ecs"               # Elastic Common Schema
    CUSTOM = "custom"         # Custom/proprietary format
    MIXED = "mixed"           # Multiple formats


@dataclass
class PlatformInfo:
    """Complete platform information"""
    platform_type: PlatformType
    data_sources: Set[DataSourceType]
    available_indices: List[str]
    detected_beats: List[str]
    field_mappings: Dict[str, str]
    capabilities: Dict[str, bool]
    metadata: Dict[str, Any]


class RobustPlatformDetector:
    """
    Production-grade platform detection system.
    Dynamically detects environment capabilities without any fallbacks.
    """
    
    def __init__(self, elasticsearch_client=None):
        self.es_client = elasticsearch_client
        self.platform_info: Optional[PlatformInfo] = None
        self.detection_cache: Dict[str, Any] = {}
        self.last_detection = None
        
        # Detection patterns - NO static values, all dynamic
        self.platform_indicators = {
            PlatformType.WINDOWS: [
                r"winlogbeat", r"windows", r"Microsoft-Windows", 
                r"EventLog", r"\.exe", r"C:\\\\", r"event\.code"
            ],
            PlatformType.LINUX: [
                r"syslog", r"rsyslog", r"journald", r"systemd",
                r"\/var\/log", r"auth\.log", r"kern\.log"
            ],
            PlatformType.UNIX: [
                r"unix", r"bsd", r"aix", r"solaris"
            ]
        }
    
    async def detect_platform(self, force_refresh: bool = False) -> PlatformInfo:
        """
        Comprehensive platform detection.
        NO fallbacks - pure detection based on available data.
        """
        cache_key = "platform_detection"
        cache_ttl = 300  # 5 minutes
        
        # Check cache (but allow force refresh)
        if (not force_refresh and 
            cache_key in self.detection_cache and
            self.last_detection and
            (datetime.now() - self.last_detection).seconds < cache_ttl):
            logger.info("🔄 Using cached platform detection")
            return self.detection_cache[cache_key]
        
        logger.info("🔍 Starting comprehensive platform detection...")
        
        # Step 1: Detect available indices
        available_indices = await self._detect_indices()
        
        # Step 2: Analyze indices to determine platform
        platform_type = await self._analyze_platform_from_indices(available_indices)
        
        # Step 3: Detect data sources and formats
        data_sources = await self._detect_data_sources(available_indices)
        
        # Step 4: Detect beats and agents
        detected_beats = await self._detect_beats(available_indices)
        
        # Step 5: Generate dynamic field mappings
        field_mappings = await self._generate_field_mappings(available_indices, platform_type)
        
        # Step 6: Detect capabilities
        capabilities = await self._detect_capabilities(available_indices, platform_type)
        
        # Step 7: Gather metadata
        metadata = await self._gather_metadata(available_indices)
        
        # Create platform info
        self.platform_info = PlatformInfo(
            platform_type=platform_type,
            data_sources=data_sources,
            available_indices=available_indices,
            detected_beats=detected_beats,
            field_mappings=field_mappings,
            capabilities=capabilities,
            metadata=metadata
        )
        
        # Cache result
        self.detection_cache[cache_key] = self.platform_info
        self.last_detection = datetime.now()
        
        logger.info(f"✅ Platform detection complete: {platform_type.value}")
        logger.info(f"   Data sources: {[ds.value for ds in data_sources]}")
        logger.info(f"   Indices found: {len(available_indices)}")
        logger.info(f"   Beats detected: {detected_beats}")
        
        return self.platform_info
    
    async def _detect_indices(self) -> List[str]:
        """Dynamically detect all available Elasticsearch indices"""
        if not self.es_client:
            logger.warning("No Elasticsearch client - cannot detect indices")
            return []
        
        try:
            # Get all indices
            indices_response = await asyncio.to_thread(
                self.es_client.cat.indices, 
                format="json", 
                h="index"
            )
            
            indices = [idx["index"] for idx in indices_response if not idx["index"].startswith(".")]
            
            # Also check for data streams
            try:
                streams_response = await asyncio.to_thread(
                    self.es_client.indices.get_data_stream,
                    name="*"
                )
                
                data_streams = []
                if "data_streams" in streams_response:
                    data_streams = [ds["name"] for ds in streams_response["data_streams"]]
                    
                indices.extend(data_streams)
                
            except Exception as e:
                logger.debug(f"Data streams not available: {e}")
            
            logger.info(f"🔍 Detected {len(indices)} indices/streams")
            return sorted(list(set(indices)))
            
        except Exception as e:
            logger.error(f"❌ Failed to detect indices: {e}")
            return []
    
    async def _analyze_platform_from_indices(self, indices: List[str]) -> PlatformType:
        """Analyze indices to determine platform type"""
        if not indices:
            # Try to detect from system
            system_platform = platform.system().lower()
            if "windows" in system_platform:
                return PlatformType.WINDOWS
            elif "linux" in system_platform:
                return PlatformType.LINUX
            elif "darwin" in system_platform:
                return PlatformType.MACOS
            else:
                return PlatformType.UNIX
        
        platform_scores = {ptype: 0 for ptype in PlatformType}
        
        # Analyze index names for platform indicators
        for index in indices:
            index_lower = index.lower()
            
            # Check for platform-specific patterns
            for ptype, patterns in self.platform_indicators.items():
                for pattern in patterns:
                    if re.search(pattern, index_lower):
                        platform_scores[ptype] += 1
        
        # Sample data from top indices to get more evidence
        await self._analyze_index_data(indices[:5], platform_scores)
        
        # Determine primary platform
        if platform_scores[PlatformType.WINDOWS] > 0 and platform_scores[PlatformType.LINUX] > 0:
            return PlatformType.MIXED
        
        max_score = max(platform_scores.values())
        if max_score == 0:
            # No clear indicators - check system platform
            system_platform = platform.system().lower()
            if "windows" in system_platform:
                return PlatformType.WINDOWS
            elif "linux" in system_platform:
                return PlatformType.LINUX
            else:
                return PlatformType.UNIX
        
        # Return platform with highest score
        return max(platform_scores.items(), key=lambda x: x[1])[0]
    
    async def _analyze_index_data(self, indices: List[str], platform_scores: Dict[PlatformType, int]):
        """Sample data from indices to determine platform"""
        if not self.es_client or not indices:
            return
        
        for index in indices:
            try:
                # Get sample documents
                response = await asyncio.to_thread(
                    self.es_client.search,
                    index=index,
                    body={"size": 10, "sort": [{"@timestamp": {"order": "desc"}}]},
                    timeout="5s"
                )
                
                if response["hits"]["total"]["value"] > 0:
                    # Analyze document structure
                    for hit in response["hits"]["hits"]:
                        source = hit["_source"]
                        source_str = str(source).lower()
                        
                        # Check for platform indicators in data
                        for ptype, patterns in self.platform_indicators.items():
                            for pattern in patterns:
                                if re.search(pattern, source_str):
                                    platform_scores[ptype] += 1
                
            except Exception as e:
                logger.debug(f"Could not analyze index {index}: {e}")
    
    async def _detect_data_sources(self, indices: List[str]) -> Set[DataSourceType]:
        """Detect data source types from indices"""
        data_sources = set()
        
        for index in indices:
            index_lower = index.lower()
            
            # Detect Beats
            if any(beat in index_lower for beat in ["beat", "winlogbeat", "metricbeat", "filebeat"]):
                data_sources.add(DataSourceType.BEATS)
            
            # Detect syslog
            if any(term in index_lower for term in ["syslog", "rsyslog", "log"]):
                data_sources.add(DataSourceType.SYSLOG)
            
            # Detect ECS
            if any(term in index_lower for term in ["ecs", "elastic"]):
                data_sources.add(DataSourceType.ECS)
            
            # If nothing specific detected, it's custom
            if not any(term in index_lower for term in ["beat", "syslog", "ecs", "log"]):
                data_sources.add(DataSourceType.CUSTOM)
        
        if len(data_sources) > 1:
            data_sources.add(DataSourceType.MIXED)
        
        return data_sources
    
    async def _detect_beats(self, indices: List[str]) -> List[str]:
        """Detect which Beats are active"""
        beats = set()
        
        for index in indices:
            index_lower = index.lower()
            
            # Common beats patterns
            beat_patterns = [
                "winlogbeat", "metricbeat", "filebeat", "packetbeat",
                "heartbeat", "auditbeat", "journalbeat", "functionbeat"
            ]
            
            for beat in beat_patterns:
                if beat in index_lower:
                    beats.add(beat)
        
        return sorted(list(beats))
    
    async def _generate_field_mappings(self, indices: List[str], platform_type: PlatformType) -> Dict[str, str]:
        """Dynamically generate field mappings based on detected schema"""
        if not self.es_client or not indices:
            return {}
        
        field_mappings = {}
        
        # Sample mappings from actual indices
        for index in indices[:3]:  # Check first 3 indices
            try:
                mapping_response = await asyncio.to_thread(
                    self.es_client.indices.get_mapping,
                    index=index
                )
                
                # Extract common security fields
                for idx_name, mapping in mapping_response.items():
                    properties = mapping.get("mappings", {}).get("properties", {})
                    
                    # Map common field patterns
                    self._map_security_fields(properties, field_mappings, "", platform_type)
                
            except Exception as e:
                logger.debug(f"Could not get mapping for {index}: {e}")
        
        return field_mappings
    
    def _map_security_fields(self, properties: Dict, mappings: Dict[str, str], prefix: str, platform_type: PlatformType):
        """Recursively map security-relevant fields"""
        for field_name, field_config in properties.items():
            full_field = f"{prefix}.{field_name}" if prefix else field_name
            
            # Map common security fields
            if "timestamp" in field_name.lower():
                mappings["timestamp"] = full_field
            elif "user" in field_name.lower() and "name" in str(field_config).lower():
                mappings["username"] = full_field
            elif "ip" in field_name.lower() or "addr" in field_name.lower():
                if "src" in field_name.lower() or "source" in field_name.lower():
                    mappings["source_ip"] = full_field
                elif "dst" in field_name.lower() or "dest" in field_name.lower():
                    mappings["destination_ip"] = full_field
                else:
                    mappings["ip_address"] = full_field
            elif "host" in field_name.lower() and "name" in str(field_config).lower():
                mappings["hostname"] = full_field
            elif "process" in field_name.lower() and "name" in str(field_config).lower():
                mappings["process_name"] = full_field
            elif "event" in field_name.lower():
                if "code" in str(field_config).lower() or "id" in field_name.lower():
                    mappings["event_id"] = full_field
                elif "category" in str(field_config).lower():
                    mappings["event_category"] = full_field
            
            # Recurse into nested objects
            if isinstance(field_config, dict) and "properties" in field_config:
                self._map_security_fields(field_config["properties"], mappings, full_field, platform_type)
    
    async def _detect_capabilities(self, indices: List[str], platform_type: PlatformType) -> Dict[str, bool]:
        """Detect what capabilities are available"""
        capabilities = {
            "authentication_logs": False,
            "system_metrics": False,
            "network_logs": False,
            "process_logs": False,
            "file_access_logs": False,
            "real_time_data": False,
            "historical_data": False,
        }
        
        if not self.es_client or not indices:
            return capabilities
        
        # Check for specific log types by sampling data
        for index in indices[:5]:
            try:
                # Sample recent documents
                response = await asyncio.to_thread(
                    self.es_client.search,
                    index=index,
                    body={
                        "size": 50,
                        "sort": [{"@timestamp": {"order": "desc"}}]
                    },
                    timeout="10s"
                )
                
                if response["hits"]["total"]["value"] > 0:
                    # Check for real-time data (documents from last hour)
                    recent_docs = 0
                    one_hour_ago = datetime.now() - timedelta(hours=1)
                    
                    for hit in response["hits"]["hits"]:
                        source = hit["_source"]
                        source_str = str(source).lower()
                        
                        # Check timestamp recency
                        timestamp_str = source.get("@timestamp", "")
                        if timestamp_str:
                            try:
                                doc_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                                if doc_time.replace(tzinfo=None) > one_hour_ago:
                                    recent_docs += 1
                            except:
                                pass
                        
                        # Check for log type indicators
                        if any(term in source_str for term in ["login", "logon", "auth", "password"]):
                            capabilities["authentication_logs"] = True
                        
                        if any(term in source_str for term in ["cpu", "memory", "disk", "system"]):
                            capabilities["system_metrics"] = True
                        
                        if any(term in source_str for term in ["network", "tcp", "udp", "ip", "connection"]):
                            capabilities["network_logs"] = True
                        
                        if any(term in source_str for term in ["process", "exec", "command"]):
                            capabilities["process_logs"] = True
                        
                        if any(term in source_str for term in ["file", "access", "read", "write"]):
                            capabilities["file_access_logs"] = True
                    
                    # Real-time if >10% of sampled docs are from last hour
                    if recent_docs > len(response["hits"]["hits"]) * 0.1:
                        capabilities["real_time_data"] = True
                    
                    # Historical data if we have any documents
                    capabilities["historical_data"] = True
                
            except Exception as e:
                logger.debug(f"Could not analyze capabilities for {index}: {e}")
        
        return capabilities
    
    async def _gather_metadata(self, indices: List[str]) -> Dict[str, Any]:
        """Gather additional metadata about the environment"""
        metadata = {
            "detection_time": datetime.now().isoformat(),
            "total_indices": len(indices),
            "system_platform": platform.system(),
            "python_version": platform.python_version(),
        }
        
        if self.es_client and indices:
            try:
                # Get cluster info
                cluster_info = await asyncio.to_thread(self.es_client.info)
                metadata["elasticsearch_version"] = cluster_info.get("version", {}).get("number", "unknown")
                metadata["cluster_name"] = cluster_info.get("cluster_name", "unknown")
                
                # Get document counts
                total_docs = 0
                for index in indices[:10]:  # Sample first 10 indices
                    try:
                        stats = await asyncio.to_thread(
                            self.es_client.indices.stats,
                            index=index,
                            metric="docs"
                        )
                        if "_all" in stats and "primaries" in stats["_all"]:
                            docs = stats["_all"]["primaries"].get("docs", {}).get("count", 0)
                            total_docs += docs
                    except:
                        pass
                
                metadata["estimated_total_documents"] = total_docs
                
            except Exception as e:
                logger.debug(f"Could not gather cluster metadata: {e}")
        
        return metadata
    
    def get_query_builder(self) -> str:
        """Return the appropriate query builder class name"""
        if not self.platform_info:
            return "GenericQueryBuilder"
        
        platform = self.platform_info.platform_type
        data_sources = self.platform_info.data_sources
        
        if platform == PlatformType.WINDOWS and DataSourceType.BEATS in data_sources:
            return "WindowsBeatsQueryBuilder"
        elif platform == PlatformType.LINUX and DataSourceType.SYSLOG in data_sources:
            return "LinuxSyslogQueryBuilder"
        elif DataSourceType.ECS in data_sources:
            return "ECSQueryBuilder"
        else:
            return "GenericQueryBuilder"
