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
import time
from concurrent.futures import TimeoutError as FuturesTimeoutError

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
class CircuitBreakerState:
    """Circuit breaker state for a data source"""
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    next_attempt_time: Optional[float] = None
    success_count_in_half_open: int = 0
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # successful calls to close circuit

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
    circuit_breaker: CircuitBreakerState = field(default_factory=CircuitBreakerState)


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
        
        # Enhanced query tracking and caching
        self.active_queries: Dict[str, Set[str]] = {}  # source_id -> query_ids
        self.query_history: List[Dict[str, Any]] = []
        self.query_cache: Dict[str, Tuple[List[Dict], float]] = {}  # query_hash -> (results, timestamp)
        self.cache_ttl = 300  # 5 minutes
        
        # Load balancing and performance tracking
        self.source_response_times: Dict[str, List[float]] = {}
        self.source_load_scores: Dict[str, float] = {}
        
        # Circuit breaker management
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        
        logger.info("🔗 MultiSourceManager initialized with enhanced features")
    
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
                
                # Initialize circuit breaker and performance tracking
                self.circuit_breakers[source_id] = CircuitBreakerState()
                self.source_response_times[source_id] = []
                self.source_load_scores[source_id] = 1.0
                
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
            
            # Initialize circuit breaker and performance tracking  
            self.circuit_breakers[source_id] = CircuitBreakerState()
            self.source_response_times[source_id] = []
            self.source_load_scores[source_id] = 1.0
            
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
                # Update circuit breaker on health check failure
                self._record_failure(source_id)
    
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
        
        # Check query cache first
        query_cache_key = self._generate_cache_key(query, filters, limit)
        cached_result = self._get_cached_result(query_cache_key)
        if cached_result:
            logger.info(f"⚡ Cache HIT for query [{query_id}]")
            return cached_result
        
        # Get available sources (healthy + circuit breaker check)
        available_sources = self._get_available_sources()
        
        # Apply load balancing to select optimal sources
        selected_sources = self._select_sources_with_load_balancing(available_sources, limit)
        
        if not selected_sources:
            logger.warning("⚠️ No available sources for query execution")
            return AggregatedResult(
                data=[],
                source_contributions={},
                total_records=0,
                execution_time=0.0,
                successful_sources=[],
                failed_sources=list(self.sources.keys()),
                metadata={"error": "No available sources (health/circuit breaker)"}
            )
        
        # Execute queries in parallel with enhanced error handling
        tasks = []
        for source_id in selected_sources:
            task = asyncio.create_task(
                self._query_single_source_with_circuit_breaker(
                    source_id, query, filters, limit, timeout
                )
            )
            tasks.append(task)
        
        # Wait for all queries to complete with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout + 5.0  # Add buffer to main timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Multi-source query [{query_id}] timed out")
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            results = [Exception("Query timeout") for _ in selected_sources]
        
        # Process results with circuit breaker updates
        successful_results = []
        failed_sources = []
        
        for i, result in enumerate(results):
            source_id = selected_sources[i]
            
            if isinstance(result, Exception):
                logger.error(f"❌ Query failed for {source_id}: {result}")
                failed_sources.append(source_id)
                self._record_failure(source_id)
            elif result and result.success:
                successful_results.append(result)
                self._record_success(source_id, result.execution_time)
            else:
                failed_sources.append(source_id)
                self._record_failure(source_id)
        
        # Aggregate results
        aggregated = await self._aggregate_results(
            successful_results, correlation_fields
        )
        
        # Update statistics
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Cache successful results
        if successful_results:
            self._cache_result(query_cache_key, aggregated)
        
        # Store query in history
        self.query_history.append({
            "query_id": query_id,
            "query": query,
            "execution_time": execution_time,
            "sources_queried": len(selected_sources),
            "sources_successful": len(successful_results),
            "total_records": aggregated.total_records,
            "timestamp": start_time.isoformat(),
            "cache_hit": False
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
    
    def _generate_cache_key(self, query: str, filters: Optional[Dict[str, Any]], limit: int) -> str:
        """Generate cache key for query result caching"""
        cache_data = {
            "query": query,
            "filters": filters or {},
            "limit": limit
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()[:12]
    
    def _get_cached_result(self, cache_key: str) -> Optional[AggregatedResult]:
        """Get cached query result if still valid"""
        if cache_key not in self.query_cache:
            return None
            
        result, timestamp = self.query_cache[cache_key]
        if time.time() - timestamp > self.cache_ttl:
            # Cache expired
            del self.query_cache[cache_key]
            return None
            
        # Convert cached data back to AggregatedResult
        return result
    
    def _cache_result(self, cache_key: str, result: AggregatedResult):
        """Cache query result"""
        self.query_cache[cache_key] = (result, time.time())
        
        # Limit cache size
        if len(self.query_cache) > 100:
            # Remove oldest entries
            oldest_keys = sorted(self.query_cache.keys(), 
                               key=lambda k: self.query_cache[k][1])[:20]
            for key in oldest_keys:
                del self.query_cache[key]
    
    def _get_available_sources(self) -> List[str]:
        """Get sources that are healthy and pass circuit breaker check"""
        available = []
        current_time = time.time()
        
        for source_id in self.sources.keys():
            if not self.source_configs[source_id].enabled:
                continue
                
            if not self.source_health[source_id]:
                continue
                
            # Check circuit breaker
            cb = self.circuit_breakers[source_id]
            
            if cb.state == "OPEN":
                if cb.next_attempt_time and current_time >= cb.next_attempt_time:
                    # Transition to HALF_OPEN
                    cb.state = "HALF_OPEN"
                    cb.success_count_in_half_open = 0
                    logger.info(f"🔄 Circuit breaker HALF_OPEN for {source_id}")
                    available.append(source_id)
                # else: circuit still open, skip source
            else:
                # CLOSED or HALF_OPEN
                available.append(source_id)
                
        return available
    
    def _select_sources_with_load_balancing(self, available_sources: List[str], limit: int) -> List[str]:
        """Select sources using load balancing strategy"""
        if not available_sources:
            return []
            
        if self.load_balance_strategy == LoadBalanceStrategy.PRIORITY_BASED:
            # Sort by priority and load score
            return sorted(available_sources, 
                         key=lambda s: (self.source_configs[s].priority.value, 
                                       self.source_load_scores[s]))
                                       
        elif self.load_balance_strategy == LoadBalanceStrategy.RESPONSE_TIME:
            # Sort by average response time
            return sorted(available_sources, 
                         key=lambda s: self._get_avg_response_time(s))
                         
        elif self.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            # Simple round robin (could be enhanced with state tracking)
            return available_sources
            
        else:
            # Default to all available sources
            return available_sources
    
    def _get_avg_response_time(self, source_id: str) -> float:
        """Get average response time for a source"""
        times = self.source_response_times[source_id]
        if not times:
            return 0.0
        return sum(times[-10:]) / len(times[-10:])  # Last 10 queries
    
    def _record_success(self, source_id: str, execution_time: float):
        """Record successful query execution"""
        cb = self.circuit_breakers[source_id]
        
        # Update response times
        self.source_response_times[source_id].append(execution_time)
        if len(self.source_response_times[source_id]) > 50:
            self.source_response_times[source_id] = self.source_response_times[source_id][-50:]
        
        # Update load score based on performance
        avg_time = self._get_avg_response_time(source_id)
        self.source_load_scores[source_id] = max(0.1, 1.0 / (avg_time + 0.1))
        
        if cb.state == "HALF_OPEN":
            cb.success_count_in_half_open += 1
            if cb.success_count_in_half_open >= cb.success_threshold:
                # Close circuit
                cb.state = "CLOSED"
                cb.failure_count = 0
                cb.next_attempt_time = None
                logger.info(f"✅ Circuit breaker CLOSED for {source_id}")
        elif cb.state == "CLOSED":
            # Reset failure count on success
            cb.failure_count = 0
    
    def _record_failure(self, source_id: str):
        """Record failed query execution"""
        cb = self.circuit_breakers[source_id]
        cb.failure_count += 1
        cb.last_failure_time = time.time()
        
        # Decrease load score on failure
        self.source_load_scores[source_id] *= 0.8
        
        if cb.state == "CLOSED" and cb.failure_count >= cb.failure_threshold:
            # Open circuit
            cb.state = "OPEN"
            cb.next_attempt_time = time.time() + cb.recovery_timeout
            logger.warning(f"⚠️ Circuit breaker OPEN for {source_id} (failures: {cb.failure_count})")
        elif cb.state == "HALF_OPEN":
            # Return to OPEN on any failure in HALF_OPEN
            cb.state = "OPEN"
            cb.next_attempt_time = time.time() + cb.recovery_timeout
            logger.warning(f"⚠️ Circuit breaker OPEN again for {source_id}")
    
    async def _query_single_source_with_circuit_breaker(
        self,
        source_id: str,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int,
        timeout: float
    ) -> QueryResult:
        """Query single source with circuit breaker protection"""
        cb = self.circuit_breakers[source_id]
        
        if cb.state == "OPEN":
            # Circuit is open, return failure immediately
            return QueryResult(
                source_id=source_id,
                connector_type=self.source_configs[source_id].connector_type,
                data=[],
                execution_time=0.0,
                success=False,
                error="Circuit breaker is OPEN"
            )
        
        # Proceed with normal query execution
        return await self._query_single_source(
            source_id, query, filters, limit, timeout
        )
    
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
        """Get comprehensive status of all configured sources"""
        available_sources = self._get_available_sources()
        
        return {
            "total_sources": len(self.sources),
            "healthy_sources": sum(self.source_health.values()),
            "available_sources": len(available_sources),
            "cache_stats": {
                "cache_size": len(self.query_cache),
                "cache_ttl": self.cache_ttl,
                "recent_queries": len(self.query_history)
            },
            "sources": {
                source_id: {
                    "type": config.connector_type,
                    "priority": config.priority.name,
                    "healthy": self.source_health[source_id],
                    "enabled": config.enabled,
                    "weight": config.weight,
                    "load_score": self.source_load_scores.get(source_id, 1.0),
                    "avg_response_time": self._get_avg_response_time(source_id),
                    "circuit_breaker": {
                        "state": self.circuit_breakers[source_id].state,
                        "failure_count": self.circuit_breakers[source_id].failure_count,
                        "last_failure": self.circuit_breakers[source_id].last_failure_time
                    },
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
