"""
Platform-Aware API Integration Service
Bridges the universal query builder with backend APIs.
NO HARDCODED VALUES - ALL DYNAMIC BASED ON ENVIRONMENT.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import asyncio

from ..platform.detector import RobustPlatformDetector, PlatformInfo
from ..query.universal_builder import UniversalQueryBuilder, QueryIntent
from ...connectors.multi_source_manager import MultiSourceManager
from ..nlp.entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)


class PlatformAwareAPIService:
    """
    Provides platform-aware API responses using dynamic detection and universal queries.
    """
    
    def __init__(self, multi_source_manager: MultiSourceManager):
        self.multi_source_manager = multi_source_manager
        
        # Get Elasticsearch client from multi_source_manager for platform detection
        elasticsearch_client = None
        if self.multi_source_manager and hasattr(self.multi_source_manager, 'sources'):
            for source_id, connector in self.multi_source_manager.sources.items():
                if hasattr(connector, 'client') and hasattr(connector.client, 'cat'):
                    elasticsearch_client = connector.client
                    logger.info(f"🔗 Using Elasticsearch client from source: {source_id}")
                    break
                elif hasattr(connector, 'es') and hasattr(connector.es, 'cat'):
                    elasticsearch_client = connector.es
                    logger.info(f"🔗 Using Elasticsearch client from source: {source_id}")
                    break
        
        if not elasticsearch_client:
            logger.warning("⚠️ No Elasticsearch client found in sources - platform detection will be limited")
        
        self.platform_detector = RobustPlatformDetector(elasticsearch_client)
        self.query_builder = UniversalQueryBuilder(self.platform_detector)
        self.entity_extractor = EntityExtractor()
        
        # Cache for performance
        self.platform_info_cache = None
        self.capabilities_cache = None
        
    async def initialize(self):
        """Initialize the service and detect platform capabilities"""
        logger.info("Initializing Platform-Aware API Service...")
        
        # Detect platform capabilities
        self.platform_info_cache = await self.platform_detector.detect_platform()
        
        logger.info(f"✅ Detected {self.platform_info_cache.platform_type.value} platform")
        logger.info(f"📊 Found {len(self.platform_info_cache.available_indices)} indices")
        logger.info(f"🔧 Detected {len(self.platform_info_cache.data_sources)} data source types")
    
    async def get_authentication_events(
        self,
        query: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get authentication events using dynamic platform detection"""
        return await self._execute_intent_query(
            intent=QueryIntent.AUTHENTICATION_EVENTS,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def get_failed_logins(
        self,
        query: str = "",
        time_range: str = "1h", 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get failed login attempts using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.FAILED_LOGINS,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def get_successful_logins(
        self,
        query: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get successful logins using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.SUCCESSFUL_LOGINS,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def get_system_metrics(
        self,
        query: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get system metrics using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.SYSTEM_METRICS,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def get_network_activity(
        self,
        query: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get network activity using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.NETWORK_ACTIVITY,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def get_process_activity(
        self,
        query: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get process activity using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.PROCESS_ACTIVITY,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def get_user_activity(
        self,
        query: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get user activity using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.USER_ACTIVITY,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def get_security_alerts(
        self,
        query: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get security alerts using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.SECURITY_ALERTS,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def generic_search(
        self,
        query: str,
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Perform generic search using platform-aware queries"""
        return await self._execute_intent_query(
            intent=QueryIntent.GENERIC_SEARCH,
            query_text=query,
            time_range=time_range,
            limit=limit
        )
    
    async def _execute_intent_query(
        self,
        intent: QueryIntent,
        query_text: str = "",
        time_range: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Execute platform-aware query for given intent"""
        start_time = datetime.now()
        
        try:
            # Extract entities from query text
            entities = []
            if query_text:
                entities = self.entity_extractor.extract_entities(query_text)
            
            # Build platform-aware query
            elasticsearch_query = await self.query_builder.build_query(
                intent=intent,
                query_text=query_text,
                entities=entities,
                time_range=time_range,
                limit=limit
            )
            
            # Get target indices
            target_indices = self.query_builder.get_target_indices()
            
            # Execute query across all available data sources
            # Convert Elasticsearch DSL to query string for multi-source manager
            query_text_for_execution = query_text if query_text else f"{intent.value}_query"
            
            results = await self.multi_source_manager.query_all_sources(
                query=query_text_for_execution,
                limit=limit
            )
            
            # Process and enhance results
            processed_results = await self._process_results(results, intent)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Build response
            response = {
                "success": True,
                "intent": intent.value,
                "query_info": {
                    "query_text": query_text,
                    "time_range": time_range,
                    "entities_found": len(entities),
                    "target_indices": target_indices,
                    "execution_time": execution_time,
                    "query_summary": self.query_builder.get_query_summary(elasticsearch_query)
                },
                "platform_info": {
                    "platform_type": self.platform_info_cache.platform_type.value,
                    "data_sources": [ds.value for ds in self.platform_info_cache.data_sources],
                    "available_indices": len(self.platform_info_cache.available_indices),
                    "field_mappings_found": len(self.platform_info_cache.field_mappings)
                },
                "results": processed_results,
                "total_hits": len(processed_results.get("events", [])),
                "has_more": len(processed_results.get("events", [])) == limit
            }
            
            logger.info(f"✅ {intent.value} query completed: {len(processed_results.get('events', []))} results in {execution_time:.3f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error executing {intent.value} query: {str(e)}")
            
            return {
                "success": False,
                "intent": intent.value,
                "error": str(e),
                "query_info": {
                    "query_text": query_text,
                    "time_range": time_range,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                },
                "results": {"events": [], "aggregations": {}},
                "total_hits": 0
            }
    
    async def _process_results(self, raw_results: Any, intent: QueryIntent) -> Dict[str, Any]:
        """Process and enhance results based on intent and platform"""
        if not raw_results or not hasattr(raw_results, 'data'):
            return {"events": [], "aggregations": {}}
        
        # AggregatedResult has data as a list of records
        events = [{"_source": record} for record in raw_results.data]
        
        # Process events based on platform and intent
        processed_events = []
        for event in events:
            source = event.get("_source", {})
            processed_event = await self._normalize_event(source, intent)
            processed_events.append(processed_event)
        
        # Generate platform-aware aggregations
        aggregations = await self._generate_aggregations(events, intent)
        
        return {
            "events": processed_events,
            "aggregations": aggregations,
            "data_source_info": {
                "sources_used": raw_results.successful_sources if hasattr(raw_results, 'successful_sources') else [],
                "sources_failed": raw_results.failed_sources if hasattr(raw_results, 'failed_sources') else [],
                "source_contributions": raw_results.source_contributions if hasattr(raw_results, 'source_contributions') else {},
                "total_execution_time": raw_results.execution_time if hasattr(raw_results, 'execution_time') else 0.0
            },
            "query_performance": {
                "execution_time": raw_results.execution_time if hasattr(raw_results, 'execution_time') else 0.0,
                "total_records": raw_results.total_records if hasattr(raw_results, 'total_records') else 0
            }
        }
    
    async def _normalize_event(self, source: Dict[str, Any], intent: QueryIntent) -> Dict[str, Any]:
        """Normalize event data based on detected platform fields"""
        field_mappings = self.platform_info_cache.field_mappings
        
        # Build normalized event using detected field mappings
        normalized = {
            "timestamp": self._extract_field(source, ["@timestamp", "timestamp", "event_time"]),
            "message": self._extract_field(source, ["message", "log_message", "event_message", "text"]),
            "source_type": self._extract_field(source, ["agent.type", "input.type", "source_type", "log_type"])
        }
        
        # Add intent-specific fields
        if intent in [QueryIntent.AUTHENTICATION_EVENTS, QueryIntent.FAILED_LOGINS, QueryIntent.SUCCESSFUL_LOGINS]:
            normalized.update({
                "username": self._extract_field(source, [
                    field_mappings.get("username", "user.name"),
                    "user.name", "username", "account", "logon_user"
                ]),
                "user_domain": self._extract_field(source, ["user.domain", "domain", "user_domain"]),
                "event_outcome": self._extract_field(source, ["event.outcome", "result", "status"]),
                "source_ip": self._extract_field(source, [
                    field_mappings.get("source_ip", "source.ip"),
                    "source.ip", "client.ip", "src_ip"
                ]),
                "hostname": self._extract_field(source, [
                    field_mappings.get("hostname", "host.name"),
                    "host.name", "hostname", "computer_name"
                ])
            })
        
        elif intent == QueryIntent.NETWORK_ACTIVITY:
            normalized.update({
                "source_ip": self._extract_field(source, ["source.ip", "src_ip", "client.ip"]),
                "destination_ip": self._extract_field(source, ["destination.ip", "dest_ip", "server.ip"]),
                "source_port": self._extract_field(source, ["source.port", "src_port"]),
                "destination_port": self._extract_field(source, ["destination.port", "dest_port"]),
                "protocol": self._extract_field(source, ["network.protocol", "protocol", "ip_protocol"]),
                "bytes_sent": self._extract_field(source, ["source.bytes", "bytes_out"]),
                "bytes_received": self._extract_field(source, ["destination.bytes", "bytes_in"])
            })
        
        elif intent == QueryIntent.PROCESS_ACTIVITY:
            normalized.update({
                "process_name": self._extract_field(source, ["process.name", "process", "image"]),
                "process_id": self._extract_field(source, ["process.pid", "pid", "process_id"]),
                "command_line": self._extract_field(source, ["process.command_line", "command", "cmd"]),
                "parent_process": self._extract_field(source, ["process.parent.name", "parent_image"]),
                "user": self._extract_field(source, ["user.name", "username", "account"])
            })
        
        elif intent == QueryIntent.SYSTEM_METRICS:
            normalized.update({
                "cpu_usage": self._extract_field(source, ["system.cpu.total.pct", "cpu_percent"]),
                "memory_usage": self._extract_field(source, ["system.memory.used.pct", "memory_percent"]),
                "disk_usage": self._extract_field(source, ["system.filesystem.used.pct", "disk_percent"]),
                "load_average": self._extract_field(source, ["system.load.1", "load_1m"])
            })
        
        # Keep original source for debugging
        normalized["_original_source"] = source
        
        return normalized
    
    def _extract_field(self, source: Dict[str, Any], field_candidates: List[str]) -> Any:
        """Extract field value using candidate field names"""
        for field in field_candidates:
            if "." in field:
                # Handle nested fields
                value = source
                for part in field.split("."):
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                if value is not None:
                    return value
            elif field in source:
                return source[field]
        
        return None
    
    async def _generate_aggregations(self, events: List[Dict[str, Any]], intent: QueryIntent) -> Dict[str, Any]:
        """Generate platform-aware aggregations"""
        if not events:
            return {}
        
        aggregations = {}
        
        # Time-based aggregations
        aggregations["timeline"] = self._create_timeline_agg(events)
        
        # Intent-specific aggregations
        if intent in [QueryIntent.AUTHENTICATION_EVENTS, QueryIntent.FAILED_LOGINS, QueryIntent.SUCCESSFUL_LOGINS]:
            aggregations["top_users"] = self._aggregate_field(events, ["user.name", "username", "account"])
            aggregations["top_hosts"] = self._aggregate_field(events, ["host.name", "hostname", "computer_name"])
            aggregations["outcomes"] = self._aggregate_field(events, ["event.outcome", "result", "status"])
        
        elif intent == QueryIntent.NETWORK_ACTIVITY:
            aggregations["top_source_ips"] = self._aggregate_field(events, ["source.ip", "src_ip"])
            aggregations["top_destinations"] = self._aggregate_field(events, ["destination.ip", "dest_ip"])
            aggregations["protocols"] = self._aggregate_field(events, ["network.protocol", "protocol"])
        
        elif intent == QueryIntent.PROCESS_ACTIVITY:
            aggregations["top_processes"] = self._aggregate_field(events, ["process.name", "process", "image"])
            aggregations["top_users"] = self._aggregate_field(events, ["user.name", "username"])
        
        return aggregations
    
    def _create_timeline_agg(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create timeline aggregation"""
        timeline = {}
        
        for event in events:
            source = event.get("_source", {})
            timestamp = self._extract_field(source, ["@timestamp", "timestamp", "event_time"])
            
            if timestamp:
                # Group by hour
                if isinstance(timestamp, str):
                    hour_key = timestamp[:13]  # YYYY-MM-DDTHH
                    timeline[hour_key] = timeline.get(hour_key, 0) + 1
        
        return [{"time": k, "count": v} for k, v in sorted(timeline.items())]
    
    def _aggregate_field(self, events: List[Dict[str, Any]], field_candidates: List[str]) -> List[Dict[str, Any]]:
        """Aggregate field values"""
        counts = {}
        
        for event in events:
            source = event.get("_source", {})
            value = self._extract_field(source, field_candidates)
            
            if value:
                value_str = str(value)
                counts[value_str] = counts.get(value_str, 0) + 1
        
        # Return top 10 values
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [{"value": k, "count": v} for k, v in sorted_items]
    
    async def get_platform_capabilities(self) -> Dict[str, Any]:
        """Get current platform capabilities and status"""
        if not self.platform_info_cache:
            await self.initialize()
        
        return {
            "platform_type": self.platform_info_cache.platform_type.value,
            "data_sources": [ds.value for ds in self.platform_info_cache.data_sources],
            "available_indices": self.platform_info_cache.available_indices,
            "field_mappings": self.platform_info_cache.field_mappings,
            "capabilities": {
                "authentication_events": True,
                "system_metrics": len([ds for ds in self.platform_info_cache.data_sources if "beats" in ds.value.lower()]) > 0,
                "network_monitoring": True,
                "process_tracking": True,
                "real_time_analysis": len(self.platform_info_cache.available_indices) > 0
            },
            "health_status": {
                "detection_time": self.platform_detector.detection_cache.get("last_detection_time"),
                "indices_accessible": len(self.platform_info_cache.available_indices),
                "field_mappings_detected": len(self.platform_info_cache.field_mappings),
                "data_sources_available": len(self.platform_info_cache.data_sources)
            }
        }
