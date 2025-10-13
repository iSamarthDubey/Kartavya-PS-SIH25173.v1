"""
Multi-Source Data Manager
Handles multiple data sources simultaneously with intelligent aggregation,
load balancing, failover, and correlation capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

from .base import BaseSIEMConnector
from .factory import create_connector, get_available_platforms

logger = logging.getLogger(__name__)


class SourcePriority(Enum):
    """Data source priority levels"""
    PRIMARY = 1      # Highest priority - most reliable/fast
    SECONDARY = 2    # Medium priority - backup/supplementary  
    TERTIARY = 3     # Lower priority - fallback/archival
    DATASET = 4      # Lowest priority - offline/demo data


class LoadBalanceStrategy(Enum):
    """Load balancing strategies for multi-source queries"""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    RESPONSE_TIME = "response_time"
    RANDOM = "random"


@dataclass
class SourceConfig:
    """Configuration for a single data source"""
    connector_type: str
    priority: SourcePriority
    enabled: bool = True
    max_concurrent_queries: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    health_check_interval: int = 60  # seconds
    weight: float = 1.0  # Load balancing weight
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResult:
    """Result from a single data source query"""
    source_id: str
    connector_type: str
    data: List[Dict[str, Any]]
    execution_time: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedResult:
    """Aggregated results from multiple data sources"""
    data: List[Dict[str, Any]]
    source_contributions: Dict[str, int]  # source_id -> count
    total_records: int
    execution_time: float
    successful_sources: List[str]
    failed_sources: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiSourceManager:
    """
    Multi-Source Data Manager
    
    Handles multiple data sources simultaneously with:
    - Intelligent load balancing
    - Automatic failover
    - Data aggregation and correlation
    - Health monitoring
    - Query distribution
    """
    
    def __init__(self, environment: str = "demo"):
        self.environment = environment
        self.sources: Dict[str, BaseSIEMConnector] = {}
        self.source_configs: Dict[str, SourceConfig] = {}
        self.source_health: Dict[str, bool] = {}
        self.source_stats: Dict[str, Dict[str, Any]] = {}
        self.load_balance_strategy = LoadBalanceStrategy.PRIORITY_BASED
        
        # Query tracking
        self.active_queries: Dict[str, Set[str]] = {}  # source_id -> query_ids
        self.query_history: List[Dict[str, Any]] = []
        
        logger.info("🔗 MultiSourceManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the multi-source manager"""
        try:
            logger.info("🚀 Initializing MultiSourceManager...")
            
            # Auto-detect and configure all available sources
            await self._auto_discover_sources()
            
            # Initialize health monitoring
            await self._initialize_health_monitoring()
            
            logger.info(f"✅ MultiSourceManager ready with {len(self.sources)} active sources")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MultiSourceManager: {e}")
            return False
    
    async def _auto_discover_sources(self):
        """Automatically discover and configure available data sources"""
        logger.info("🔍 Auto-discovering available data sources...")
        
        # Get available platforms
        available_platforms = get_available_platforms(self.environment)
        
        # REAL data sources only (no datasets in production)
        real_sources = ["elasticsearch", "wazuh", "splunk"]
        
        # PRODUCTION: REAL SOURCES ONLY - NO EXCEPTIONS  
        if self.environment == "production":
            available_platforms = [p for p in available_platforms if p in real_sources]
            logger.info(f"🏢 PRODUCTION MODE: Only real sources considered: {available_platforms}")
            
            if not available_platforms:
                logger.error("❌ PRODUCTION: No real data sources detected!")
                logger.error("❌ PRODUCTION REQUIREMENT: At least one of Elasticsearch/Wazuh/Splunk must be available")
                raise RuntimeError("PRODUCTION: No real data sources available - deployment blocked")
        
        # Source priority mapping
        source_priorities = {
            "elasticsearch": SourcePriority.PRIMARY,
            "splunk": SourcePriority.PRIMARY, 
            "wazuh": SourcePriority.SECONDARY,
            "dataset": SourcePriority.DATASET
        }
        
        # Configure each available source
        for platform in available_platforms:
            source_id = f"{platform}_primary"
            
            try:
                # Create connector
                connector = create_connector(platform, self.environment)
                
                # Create source configuration
                config = SourceConfig(
                    connector_type=platform,
                    priority=source_priorities.get(platform, SourcePriority.TERTIARY),
                    weight=self._get_default_weight(platform),
                    tags={platform, "auto_discovered"},
                    metadata={"discovery_time": datetime.now().isoformat()}
                )
                
                # Add to sources
                self.sources[source_id] = connector
                self.source_configs[source_id] = config
                self.source_health[source_id] = True  # Assume healthy initially
                self.source_stats[source_id] = {
                    "queries_executed": 0,
                    "total_execution_time": 0.0,
                    "last_query_time": None,
                    "error_count": 0
                }
                
                logger.info(f"✅ Added source: {source_id} ({platform}) - Priority: {config.priority.name}")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to add source {platform}: {e}")
                continue
        
        # Ensure at least one source is available
        if not self.sources:
            if self.environment == "production":
                # PRODUCTION: ABSOLUTELY NO FALLBACKS
                logger.error("❌ PRODUCTION: CRITICAL FAILURE - No real data sources initialized!")
                logger.error("❌ PRODUCTION: System cannot operate without real security data sources")
                raise RuntimeError("PRODUCTION DEPLOYMENT BLOCKED: No real data sources available")
            else:
                # DEMO: Dataset fallback allowed
                logger.warning("⚠️ DEMO: No real sources discovered, adding dataset fallback")
                await self._add_fallback_dataset()
    
    def _get_default_weight(self, platform: str) -> float:
        """Get default weight for a platform"""
        weights = {
            "elasticsearch": 1.0,
            "splunk": 1.0,
            "wazuh": 0.8,
            "dataset": 0.3
        }
        return weights.get(platform, 0.5)
    
    async def _add_fallback_dataset(self):
        """Add dataset as fallback source"""
        source_id = "dataset_fallback"
        
        try:
            connector = create_connector("dataset", self.environment)
            config = SourceConfig(
                connector_type="dataset",
                priority=SourcePriority.DATASET,
                weight=0.3,
                tags={"dataset", "fallback"},
                metadata={"fallback": True}
            )
            
            self.sources[source_id] = connector
            self.source_configs[source_id] = config
            self.source_health[source_id] = True
            self.source_stats[source_id] = {
                "queries_executed": 0,
                "total_execution_time": 0.0,
                "last_query_time": None,
                "error_count": 0
            }
            
            logger.info("✅ Added fallback dataset source")
            
        except Exception as e:
            logger.error(f"❌ Failed to add fallback dataset: {e}")
    
    async def _initialize_health_monitoring(self):
        """Initialize health monitoring for all sources"""
        logger.info("💓 Initializing health monitoring...")
        
        # Start background health check task
        asyncio.create_task(self._health_check_loop())
        
        logger.info("✅ Health monitoring initialized")
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self):
        """Perform health checks on all sources"""
        for source_id, connector in self.sources.items():
            try:
                if hasattr(connector, 'is_available'):
                    is_healthy = connector.is_available()
                else:
                    # Basic connection test
                    is_healthy = True  # Assume healthy if no check available
                
                self.source_health[source_id] = is_healthy
                
                if not is_healthy:
                    logger.warning(f"⚠️ Source {source_id} health check failed")
                    
            except Exception as e:
                self.source_health[source_id] = False
                self.source_stats[source_id]["error_count"] += 1
                logger.error(f"❌ Health check failed for {source_id}: {e}")
    
    async def query_all_sources(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        timeout: float = 30.0,
        correlation_fields: Optional[List[str]] = None
    ) -> AggregatedResult:
        """
        Query all available sources and aggregate results
        
        Args:
            query: Search query
            filters: Additional filters
            limit: Maximum records per source
            timeout: Query timeout in seconds
            correlation_fields: Fields to use for result correlation
            
        Returns:
            Aggregated results from all sources
        """
        start_time = datetime.now()
        query_id = hashlib.md5(f"{query}{start_time}".encode()).hexdigest()[:8]
        
        logger.info(f"🔍 Multi-source query [{query_id}]: {query}")
        
        # Get healthy sources
        healthy_sources = [
            source_id for source_id, is_healthy 
            in self.source_health.items() 
            if is_healthy and self.source_configs[source_id].enabled
        ]
        
        if not healthy_sources:
            logger.warning("⚠️ No healthy sources available")
            return AggregatedResult(
                data=[],
                source_contributions={},
                total_records=0,
                execution_time=0.0,
                successful_sources=[],
                failed_sources=list(self.sources.keys()),
                metadata={"error": "No healthy sources available"}
            )
        
        # Execute queries in parallel
        tasks = []
        for source_id in healthy_sources:
            task = asyncio.create_task(
                self._query_single_source(
                    source_id, query, filters, limit, timeout
                )
            )
            tasks.append(task)
        
        # Wait for all queries to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_sources = []
        
        for i, result in enumerate(results):
            source_id = healthy_sources[i]
            
            if isinstance(result, Exception):
                logger.error(f"❌ Query failed for {source_id}: {result}")
                failed_sources.append(source_id)
            elif result and result.success:
                successful_results.append(result)
            else:
                failed_sources.append(source_id)
        
        # Aggregate results
        aggregated = await self._aggregate_results(
            successful_results, correlation_fields
        )
        
        # Update statistics
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Store query in history
        self.query_history.append({
            "query_id": query_id,
            "query": query,
            "execution_time": execution_time,
            "sources_queried": len(healthy_sources),
            "sources_successful": len(successful_results),
            "total_records": aggregated.total_records,
            "timestamp": start_time.isoformat()
        })
        
        # Limit history size
        if len(self.query_history) > 100:
            self.query_history = self.query_history[-100:]
        
        logger.info(
            f"✅ Multi-source query [{query_id}] completed: "
            f"{aggregated.total_records} records from {len(successful_results)} sources "
            f"in {execution_time:.2f}s"
        )
        
        return aggregated
    
    async def _query_single_source(
        self,
        source_id: str,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int,
        timeout: float
    ) -> QueryResult:
        """Query a single data source"""
        start_time = datetime.now()
        
        try:
            connector = self.sources[source_id]
            config = self.source_configs[source_id]
            
            # Track active query
            if source_id not in self.active_queries:
                self.active_queries[source_id] = set()
            
            query_id = f"{source_id}_{start_time.timestamp()}"
            self.active_queries[source_id].add(query_id)
            
            # Execute query (adapt based on connector type)
            if hasattr(connector, 'search'):
                data = await connector.search(query, limit=limit)
            elif hasattr(connector, 'query'):
                data = await connector.query(query, limit=limit)
            else:
                # Generic query method
                data = await connector.execute_query(query, limit=limit)
            
            # Clean up tracking
            self.active_queries[source_id].discard(query_id)
            
            # Update stats
            execution_time = (datetime.now() - start_time).total_seconds()
            self.source_stats[source_id]["queries_executed"] += 1
            self.source_stats[source_id]["total_execution_time"] += execution_time
            self.source_stats[source_id]["last_query_time"] = start_time.isoformat()
            
            return QueryResult(
                source_id=source_id,
                connector_type=config.connector_type,
                data=data if isinstance(data, list) else [],
                execution_time=execution_time,
                success=True,
                metadata={
                    "query": query,
                    "limit": limit,
                    "filters": filters
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.source_stats[source_id]["error_count"] += 1
            
            logger.error(f"❌ Query failed for {source_id}: {e}")
            
            return QueryResult(
                source_id=source_id,
                connector_type=self.source_configs[source_id].connector_type,
                data=[],
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
    
    async def _aggregate_results(
        self,
        results: List[QueryResult],
        correlation_fields: Optional[List[str]] = None
    ) -> AggregatedResult:
        """Aggregate results from multiple sources"""
        
        all_data = []
        source_contributions = {}
        successful_sources = []
        total_execution_time = 0.0
        
        # Collect all data
        for result in results:
            all_data.extend(result.data)
            source_contributions[result.source_id] = len(result.data)
            successful_sources.append(result.source_id)
            total_execution_time += result.execution_time
        
        # Remove duplicates if correlation fields provided
        if correlation_fields and all_data:
            all_data = self._deduplicate_records(all_data, correlation_fields)
        
        # Sort by timestamp if available
        try:
            all_data.sort(key=lambda x: x.get('@timestamp', x.get('timestamp', '')), reverse=True)
        except:
            pass  # Skip sorting if timestamp format issues
        
        return AggregatedResult(
            data=all_data,
            source_contributions=source_contributions,
            total_records=len(all_data),
            execution_time=max([r.execution_time for r in results]) if results else 0.0,
            successful_sources=successful_sources,
            failed_sources=[],
            metadata={
                "sources_queried": len(results),
                "correlation_fields": correlation_fields,
                "total_execution_time": total_execution_time
            }
        )
    
    def _deduplicate_records(
        self, 
        records: List[Dict[str, Any]], 
        correlation_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate records based on correlation fields"""
        seen = set()
        unique_records = []
        
        for record in records:
            # Create correlation key
            key_parts = []
            for field in correlation_fields:
                value = record.get(field, '')
                key_parts.append(str(value))
            
            correlation_key = '|'.join(key_parts)
            
            if correlation_key not in seen:
                seen.add(correlation_key)
                unique_records.append(record)
        
        logger.info(f"🔄 Deduplicated {len(records)} -> {len(unique_records)} records")
        return unique_records
    
    def get_source_status(self) -> Dict[str, Any]:
        """Get status of all configured sources"""
        return {
            "total_sources": len(self.sources),
            "healthy_sources": sum(self.source_health.values()),
            "sources": {
                source_id: {
                    "type": config.connector_type,
                    "priority": config.priority.name,
                    "healthy": self.source_health[source_id],
                    "enabled": config.enabled,
                    "weight": config.weight,
                    "stats": self.source_stats[source_id],
                    "tags": list(config.tags)
                }
                for source_id, config in self.source_configs.items()
            }
        }
    
    async def add_source(
        self, 
        source_id: str, 
        connector_type: str,
        config: Optional[SourceConfig] = None,
        **kwargs
    ) -> bool:
        """Manually add a data source"""
        try:
            if source_id in self.sources:
                logger.warning(f"⚠️ Source {source_id} already exists")
                return False
            
            # Create connector
            connector = create_connector(connector_type, self.environment, **kwargs)
            
            # Use provided config or create default
            if config is None:
                config = SourceConfig(
                    connector_type=connector_type,
                    priority=SourcePriority.SECONDARY,
                    tags={"manual"}
                )
            
            # Add source
            self.sources[source_id] = connector
            self.source_configs[source_id] = config
            self.source_health[source_id] = True
            self.source_stats[source_id] = {
                "queries_executed": 0,
                "total_execution_time": 0.0,
                "last_query_time": None,
                "error_count": 0
            }
            
            logger.info(f"✅ Added source: {source_id} ({connector_type})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add source {source_id}: {e}")
            return False
    
    async def remove_source(self, source_id: str) -> bool:
        """Remove a data source"""
        try:
            if source_id not in self.sources:
                logger.warning(f"⚠️ Source {source_id} not found")
                return False
            
            # Cleanup connector
            connector = self.sources[source_id]
            if hasattr(connector, 'disconnect'):
                await connector.disconnect()
            
            # Remove from all tracking
            del self.sources[source_id]
            del self.source_configs[source_id]
            del self.source_health[source_id]
            del self.source_stats[source_id]
            
            if source_id in self.active_queries:
                del self.active_queries[source_id]
            
            logger.info(f"✅ Removed source: {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove source {source_id}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup all sources and resources"""
        logger.info("🧹 Cleaning up MultiSourceManager...")
        
        for source_id, connector in self.sources.items():
            try:
                if hasattr(connector, 'disconnect'):
                    await connector.disconnect()
            except Exception as e:
                logger.error(f"❌ Error disconnecting {source_id}: {e}")
        
        self.sources.clear()
        self.source_configs.clear()
        self.source_health.clear()
        self.source_stats.clear()
        self.active_queries.clear()
        
        logger.info("✅ MultiSourceManager cleanup completed")
