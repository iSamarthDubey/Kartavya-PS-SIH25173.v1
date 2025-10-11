"""
SIEM Integration Layer
Unified interface for all SIEM connectors, processors, and data handling
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Union, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

# Import our SIEM components
try:
    from ..connectors.enterprise_siem import (
        create_siem_connector, SIEMConfig, NormalizedEvent, 
        DataNormalizer, StreamingProcessor
    )
    from ..processors.batch_processor import (
        BatchExecutionEngine, BatchConfig, BatchJob, SIEMBatchProcessor,
        create_batch_job, BatchScheduler
    )
    from ..optimization.query_builder import AdvancedQueryBuilder
    from ..ai.response_generator import AIResponseGenerator
    from ..optimization.schema_mapper import SchemaMapper
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some SIEM components not available: {e}")
    COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SIEMIntegrationConfig:
    """Configuration for SIEM integration"""
    # Supported SIEM platforms
    supported_platforms: List[str] = None
    
    # Default connection settings
    connection_timeout: int = 30
    max_retries: int = 3
    batch_processing: bool = True
    real_time_streaming: bool = True
    
    # Processing options
    enable_normalization: bool = True
    enable_ai_analysis: bool = True
    enable_caching: bool = True
    enable_schema_mapping: bool = True
    
    # Storage paths
    data_storage_path: str = "/tmp/siem_data"
    cache_storage_path: str = "/tmp/siem_cache"
    
    # AI and optimization
    ai_model_name: str = "gemini-pro"
    query_optimization: bool = True
    
    # Batch processing settings
    batch_config: Optional[BatchConfig] = None
    
    def __post_init__(self):
        if self.supported_platforms is None:
            self.supported_platforms = ["elasticsearch", "splunk", "qradar", "azure_sentinel"]
        
        if self.batch_config is None:
            self.batch_config = BatchConfig()


class SIEMConnectionManager:
    """Manages connections to multiple SIEM platforms"""
    
    def __init__(self, config: SIEMIntegrationConfig):
        self.config = config
        self.connections = {}
        self.connection_status = {}
        
    async def add_connection(self, platform_id: str, platform_type: str, siem_config: SIEMConfig) -> bool:
        """Add a SIEM connection"""
        try:
            if not COMPONENTS_AVAILABLE:
                logger.error("SIEM components not available")
                return False
            
            # Create connector
            connector = create_siem_connector(platform_type, siem_config)
            
            # Test connection
            success = await connector.connect()
            if success:
                self.connections[platform_id] = connector
                self.connection_status[platform_id] = {
                    "status": "connected",
                    "platform_type": platform_type,
                    "connected_at": datetime.now().isoformat(),
                    "last_used": None
                }
                logger.info(f"Successfully connected to {platform_type} as {platform_id}")
                return True
            else:
                logger.error(f"Failed to connect to {platform_type} as {platform_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding connection {platform_id}: {e}")
            self.connection_status[platform_id] = {
                "status": "failed",
                "platform_type": platform_type,
                "error": str(e),
                "last_attempt": datetime.now().isoformat()
            }
            return False
    
    async def remove_connection(self, platform_id: str) -> bool:
        """Remove a SIEM connection"""
        try:
            if platform_id in self.connections:
                connector = self.connections[platform_id]
                await connector.disconnect()
                del self.connections[platform_id]
                del self.connection_status[platform_id]
                logger.info(f"Removed connection {platform_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing connection {platform_id}: {e}")
            return False
    
    async def get_connection(self, platform_id: str):
        """Get a SIEM connection"""
        connector = self.connections.get(platform_id)
        if connector:
            # Update last used timestamp
            self.connection_status[platform_id]["last_used"] = datetime.now().isoformat()
        return connector
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all connections"""
        results = {}
        for platform_id, connector in self.connections.items():
            try:
                success, error = await connector.test_connection()
                results[platform_id] = success
                if not success:
                    logger.warning(f"Connection test failed for {platform_id}: {error}")
            except Exception as e:
                results[platform_id] = False
                logger.error(f"Error testing connection {platform_id}: {e}")
        return results
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all connections"""
        return self.connection_status.copy()
    
    async def cleanup_connections(self):
        """Cleanup all connections"""
        for platform_id in list(self.connections.keys()):
            await self.remove_connection(platform_id)


class UnifiedSIEMInterface:
    """Unified interface for SIEM operations"""
    
    def __init__(self, config: SIEMIntegrationConfig):
        self.config = config
        self.connection_manager = SIEMConnectionManager(config)
        
        # Initialize components if available
        if COMPONENTS_AVAILABLE:
            self.data_normalizer = DataNormalizer()
            self.query_builder = AdvancedQueryBuilder()
            self.ai_generator = AIResponseGenerator() if config.enable_ai_analysis else None
            self.schema_mapper = SchemaMapper() if config.enable_schema_mapping else None
            
            # Initialize batch processing
            if config.batch_processing:
                self.batch_processor = SIEMBatchProcessor(self.data_normalizer)
                self.batch_engine = BatchExecutionEngine(config.batch_config, self.batch_processor)
                self.batch_scheduler = BatchScheduler(self.batch_engine)
            else:
                self.batch_processor = None
                self.batch_engine = None
                self.batch_scheduler = None
            
            # Initialize streaming
            if config.real_time_streaming:
                self.streaming_processor = StreamingProcessor(self.data_normalizer)
            else:
                self.streaming_processor = None
        else:
            self.data_normalizer = None
            self.query_builder = None
            self.ai_generator = None
            self.schema_mapper = None
            self.batch_processor = None
            self.batch_engine = None
            self.batch_scheduler = None
            self.streaming_processor = None
        
        # Create storage directories
        Path(config.data_storage_path).mkdir(parents=True, exist_ok=True)
        Path(config.cache_storage_path).mkdir(parents=True, exist_ok=True)
        
    async def initialize(self):
        """Initialize the SIEM interface"""
        if self.batch_engine:
            await self.batch_engine.initialize()
        logger.info("SIEM interface initialized")
    
    async def add_siem_platform(self, platform_id: str, platform_type: str, connection_config: Dict[str, Any]) -> bool:
        """Add a SIEM platform connection"""
        try:
            # Create SIEM config
            siem_config = SIEMConfig(**connection_config)
            
            # Add connection
            return await self.connection_manager.add_connection(platform_id, platform_type, siem_config)
            
        except Exception as e:
            logger.error(f"Error adding SIEM platform {platform_id}: {e}")
            return False
    
    async def remove_siem_platform(self, platform_id: str) -> bool:
        """Remove a SIEM platform connection"""
        return await self.connection_manager.remove_connection(platform_id)
    
    async def execute_query(self, platform_id: str, query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute query on specified SIEM platform"""
        try:
            connector = await self.connection_manager.get_connection(platform_id)
            if not connector:
                raise Exception(f"No connection found for platform {platform_id}")
            
            # Optimize query if enabled
            if self.query_builder and self.config.query_optimization:
                try:
                    optimized_query = await self.query_builder.build_optimized_query(
                        query, platform_id
                    )
                    query = optimized_query
                except Exception as e:
                    logger.warning(f"Query optimization failed, using original: {e}")
            
            # Execute query
            results = await connector.execute_query(query, **kwargs)
            
            # Normalize results if enabled
            if self.config.enable_normalization and self.data_normalizer:
                normalized_results = await self._normalize_results(results, platform_id)
                results["normalized_data"] = normalized_results
            
            # Add metadata
            results["_metadata"] = {
                **results.get("_metadata", {}),
                "platform_id": platform_id,
                "query_time": datetime.now().isoformat(),
                "normalized": self.config.enable_normalization
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing query on {platform_id}: {e}")
            raise
    
    async def execute_multi_platform_query(self, query: Dict[str, Any], platform_ids: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute query across multiple SIEM platforms"""
        if platform_ids is None:
            platform_ids = list(self.connection_manager.connections.keys())
        
        results = {}
        errors = {}
        
        # Execute queries concurrently
        tasks = []
        for platform_id in platform_ids:
            task = self._execute_query_safe(platform_id, query, **kwargs)
            tasks.append((platform_id, task))
        
        # Wait for all queries to complete
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (platform_id, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                errors[platform_id] = str(result)
                logger.error(f"Query failed on {platform_id}: {result}")
            else:
                results[platform_id] = result
        
        # Aggregate results
        aggregated = await self._aggregate_results(results)
        aggregated["_metadata"] = {
            "platforms_queried": platform_ids,
            "successful_platforms": list(results.keys()),
            "failed_platforms": list(errors.keys()),
            "errors": errors,
            "query_time": datetime.now().isoformat()
        }
        
        return aggregated
    
    async def submit_batch_job(self, platform_id: str, query: Dict[str, Any], **kwargs) -> str:
        """Submit a batch processing job"""
        if not self.batch_engine:
            raise Exception("Batch processing not enabled")
        
        try:
            # Create batch job
            job = create_batch_job(
                source_platform=platform_id,
                query=query,
                **kwargs
            )
            
            # Submit job
            success = await self.batch_engine.submit_job(job)
            if success:
                logger.info(f"Submitted batch job {job.job_id} for platform {platform_id}")
                return job.job_id
            else:
                raise Exception("Failed to submit batch job")
                
        except Exception as e:
            logger.error(f"Error submitting batch job: {e}")
            raise
    
    async def get_batch_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a batch job"""
        if not self.batch_engine:
            return None
        
        status = await self.batch_engine.get_job_status(job_id)
        return asdict(status) if status else None
    
    async def start_streaming(self, platform_id: str, query: Dict[str, Any], callback: callable):
        """Start real-time streaming from a SIEM platform"""
        if not self.streaming_processor:
            raise Exception("Streaming not enabled")
        
        connector = await self.connection_manager.get_connection(platform_id)
        if not connector:
            raise Exception(f"No connection found for platform {platform_id}")
        
        # Subscribe to streaming events
        self.streaming_processor.subscribe(callback)
        
        # Start streaming
        asyncio.create_task(self.streaming_processor.process_stream(connector, query))
        logger.info(f"Started streaming from {platform_id}")
    
    async def analyze_with_ai(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], analysis_type: str = "summary") -> Dict[str, Any]:
        """Analyze data using AI"""
        if not self.ai_generator:
            raise Exception("AI analysis not enabled")
        
        try:
            if analysis_type == "summary":
                return await self.ai_generator.generate_summary(data)
            elif analysis_type == "recommendations":
                return await self.ai_generator.generate_recommendations(data)
            elif analysis_type == "threat_analysis":
                return await self.ai_generator.analyze_threat_patterns(data)
            else:
                raise Exception(f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise
    
    async def get_platform_schema(self, platform_id: str) -> Dict[str, Any]:
        """Get schema information for a SIEM platform"""
        try:
            connector = await self.connection_manager.get_connection(platform_id)
            if not connector:
                raise Exception(f"No connection found for platform {platform_id}")
            
            schema = await connector.get_schema()
            
            # Enhance with schema mapping if available
            if self.schema_mapper:
                try:
                    enhanced_schema = await self.schema_mapper.get_enhanced_mapping(platform_id)
                    schema["enhanced_mappings"] = enhanced_schema
                except Exception as e:
                    logger.warning(f"Schema mapping enhancement failed: {e}")
            
            return schema
            
        except Exception as e:
            logger.error(f"Error getting schema for {platform_id}: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status = {
            "connections": await self.connection_manager.get_connection_status(),
            "components": {
                "data_normalizer": self.data_normalizer is not None,
                "query_builder": self.query_builder is not None,
                "ai_generator": self.ai_generator is not None,
                "schema_mapper": self.schema_mapper is not None,
                "batch_processor": self.batch_processor is not None,
                "streaming_processor": self.streaming_processor is not None
            },
            "batch_processing": {}
        }
        
        # Add batch processing status
        if self.batch_engine:
            try:
                batch_stats = await self.batch_engine.get_engine_stats()
                status["batch_processing"] = batch_stats
            except Exception as e:
                status["batch_processing"]["error"] = str(e)
        
        return status
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop batch processing
            if self.batch_engine:
                await self.batch_engine.stop()
            
            if self.batch_scheduler:
                await self.batch_scheduler.stop_scheduler()
            
            # Cleanup connections
            await self.connection_manager.cleanup_connections()
            
            logger.info("SIEM interface cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _execute_query_safe(self, platform_id: str, query: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Safely execute query with error handling"""
        try:
            return await self.execute_query(platform_id, query, **kwargs)
        except Exception as e:
            logger.error(f"Query failed on {platform_id}: {e}")
            raise
    
    async def _normalize_results(self, results: Dict[str, Any], platform_id: str) -> List[Dict[str, Any]]:
        """Normalize query results"""
        normalized_results = []
        
        try:
            hits = results.get("hits", {}).get("hits", [])
            
            for hit in hits:
                source_data = hit.get("_source", {})
                if source_data:
                    normalized_event = self.data_normalizer.normalize_event(source_data, platform_id)
                    normalized_results.append(asdict(normalized_event))
            
            return normalized_results
            
        except Exception as e:
            logger.error(f"Error normalizing results: {e}")
            return []
    
    async def _aggregate_results(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple platforms"""
        aggregated = {
            "hits": {
                "total": {"value": 0},
                "hits": []
            },
            "took": 0,
            "platforms": {}
        }
        
        try:
            for platform_id, platform_results in results.items():
                hits = platform_results.get("hits", {})
                total = hits.get("total", {}).get("value", 0)
                platform_hits = hits.get("hits", [])
                
                # Add platform identifier to each hit
                for hit in platform_hits:
                    hit["_platform"] = platform_id
                
                aggregated["hits"]["hits"].extend(platform_hits)
                aggregated["hits"]["total"]["value"] += total
                aggregated["took"] += platform_results.get("took", 0)
                aggregated["platforms"][platform_id] = {
                    "hits": total,
                    "took": platform_results.get("took", 0)
                }
            
            # Sort hits by timestamp if available
            try:
                aggregated["hits"]["hits"].sort(
                    key=lambda x: x.get("_source", {}).get("@timestamp", ""),
                    reverse=True
                )
            except:
                pass
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Error aggregating results: {e}")
            return aggregated


# High-level convenience functions
async def create_siem_interface(config: SIEMIntegrationConfig = None) -> UnifiedSIEMInterface:
    """Create and initialize a SIEM interface"""
    if config is None:
        config = SIEMIntegrationConfig()
    
    interface = UnifiedSIEMInterface(config)
    await interface.initialize()
    return interface


async def quick_siem_query(platforms: Dict[str, Dict[str, Any]], query: Dict[str, Any]) -> Dict[str, Any]:
    """Quick utility for executing a query across multiple SIEM platforms"""
    config = SIEMIntegrationConfig()
    interface = await create_siem_interface(config)
    
    try:
        # Add platform connections
        for platform_id, platform_config in platforms.items():
            platform_type = platform_config.pop("type", "elasticsearch")
            success = await interface.add_siem_platform(platform_id, platform_type, platform_config)
            if not success:
                logger.warning(f"Failed to connect to {platform_id}")
        
        # Execute query
        results = await interface.execute_multi_platform_query(query)
        
        return results
        
    finally:
        await interface.cleanup()


# Export main classes and functions
__all__ = [
    'SIEMIntegrationConfig',
    'SIEMConnectionManager',
    'UnifiedSIEMInterface',
    'create_siem_interface',
    'quick_siem_query'
]
