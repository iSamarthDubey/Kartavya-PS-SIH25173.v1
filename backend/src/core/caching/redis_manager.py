"""
Redis Caching Manager - High-performance caching for SIEM queries and sessions
"""

import asyncio
import json
import logging
import hashlib
import time
import random
from typing import Any, Optional, Dict, List, Set
from datetime import datetime, timedelta
import os
from dataclasses import dataclass, field
from enum import Enum

# Use aioredis for async Redis operations
try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RedisConnectionState(Enum):
    """Redis connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class RedisStats:
    """Redis connection and performance statistics"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    connection_attempts: int = 0
    connection_failures: int = 0
    last_connection_time: Optional[float] = None
    avg_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total_operations == 0:
            return 100.0
        return (self.successful_operations / self.total_operations) * 100
    
    @property
    def cache_hit_rate(self) -> float:
        total_cache_ops = self.cache_hits + self.cache_misses
        if total_cache_ops == 0:
            return 0.0
        return (self.cache_hits / total_cache_ops) * 100


@dataclass
class RedisClusterNode:
    """Redis cluster node configuration"""
    host: str
    port: int
    password: Optional[str] = None
    weight: float = 1.0
    max_connections: int = 20
    is_primary: bool = True


class RedisManager:
    """
    High-performance Redis caching manager for SIEM queries and session data
    """
    
    def __init__(self):
        self.redis = None
        self.connection_state = RedisConnectionState.DISCONNECTED
        self.enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # Enhanced Configuration
        self.primary_config = RedisClusterNode(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD") if os.getenv("REDIS_PASSWORD") else None,
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
        )
        
        # Fallback Redis nodes (for distributed setup)
        self.fallback_nodes: List[RedisClusterNode] = []
        self._parse_fallback_nodes()
        
        # Connection settings
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.max_retries = int(os.getenv("REDIS_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("REDIS_RETRY_DELAY", "1.0"))
        self.health_check_interval = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30"))
        
        # Cache settings with smart TTL
        self.default_ttl = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
        self.query_cache_ttl = int(os.getenv("QUERY_CACHE_TTL", "1800"))  # 30 minutes
        self.session_ttl = int(os.getenv("SESSION_TTL_SECONDS", "86400"))  # 24 hours
        self.adaptive_ttl_enabled = os.getenv("ADAPTIVE_TTL_ENABLED", "true").lower() == "true"
        
        # Performance and monitoring
        self.stats = RedisStats()
        self.local_cache: Dict[str, tuple[Any, float]] = {}  # key -> (value, expiry_time)
        self.max_local_cache_size = int(os.getenv("MAX_LOCAL_CACHE_SIZE", "1000"))
        
        # Connection pool monitoring
        self.connection_pools: Dict[str, Any] = {}
        self.active_connections: Set[str] = set()
        
        # Prefixes for different data types
        self.prefixes = {
            "query": "kartavya:query:",
            "session": "kartavya:session:",
            "context": "kartavya:context:",
            "user": "kartavya:user:",
            "metrics": "kartavya:metrics:",
            "lock": "kartavya:lock:",
            "counter": "kartavya:counter:"
        }
        
        # Distributed caching preparation
        self.cluster_id = os.getenv("REDIS_CLUSTER_ID", "node1")
        self.enable_clustering = os.getenv("REDIS_CLUSTERING_ENABLED", "false").lower() == "true"
        
        logger.info(f"🚀 Enhanced Redis Manager initialized - Clustering: {self.enable_clustering}")
    
    def _parse_fallback_nodes(self):
        """Parse fallback Redis nodes from environment variables"""
        fallback_hosts = os.getenv("REDIS_FALLBACK_HOSTS", "")
        if fallback_hosts:
            try:
                for host_config in fallback_hosts.split(","):
                    if ":" in host_config:
                        host, port = host_config.strip().split(":")
                        self.fallback_nodes.append(RedisClusterNode(
                            host=host,
                            port=int(port),
                            password=self.primary_config.password,
                            is_primary=False
                        ))
                logger.info(f"🔄 Configured {len(self.fallback_nodes)} fallback Redis nodes")
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse fallback nodes: {e}")
    
    async def _start_health_monitoring(self):
        """Start background health monitoring task"""
        asyncio.create_task(self._health_monitor_loop())
        logger.info("💓 Redis health monitoring started")
    
    async def _health_monitor_loop(self):
        """Background health monitoring loop"""
        while self.enabled:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        if not self.redis or self.connection_state == RedisConnectionState.FAILED:
            return
            
        try:
            start_time = time.time()
            await self.redis.ping()
            response_time = time.time() - start_time
            
            # Update response time statistics
            self.stats.response_times.append(response_time)
            if len(self.stats.response_times) > 100:
                self.stats.response_times = self.stats.response_times[-100:]
            
            self.stats.avg_response_time = sum(self.stats.response_times) / len(self.stats.response_times)
            
            # Log slow health checks
            if response_time > 1.0:
                logger.warning(f"🐌 Slow Redis health check: {response_time:.3f}s")
            
            if self.connection_state != RedisConnectionState.CONNECTED:
                self.connection_state = RedisConnectionState.CONNECTED
                logger.info("✅ Redis connection restored")
                
        except Exception as e:
            logger.error(f"❌ Redis health check failed: {e}")
            if self.connection_state == RedisConnectionState.CONNECTED:
                self.connection_state = RedisConnectionState.RECONNECTING
                await self._attempt_reconnection()
    
    async def _attempt_reconnection(self):
        """Attempt to reconnect to Redis with fallback nodes"""
        self.connection_state = RedisConnectionState.RECONNECTING
        
        # Try primary node first
        nodes_to_try = [self.primary_config] + self.fallback_nodes
        
        for node in nodes_to_try:
            try:
                logger.info(f"🔄 Attempting Redis reconnection to {node.host}:{node.port}")
                
                if self.redis:
                    await self.redis.close()
                
                self.redis = await self._create_redis_connection(node)
                await self.redis.ping()
                
                self.connection_state = RedisConnectionState.CONNECTED
                self.stats.connection_attempts += 1
                self.stats.last_connection_time = time.time()
                
                logger.info(f"✅ Reconnected to Redis at {node.host}:{node.port}")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to reconnect to {node.host}:{node.port}: {e}")
                continue
        
        # All nodes failed
        self.connection_state = RedisConnectionState.FAILED
        self.stats.connection_failures += 1
        logger.error("❌ Failed to reconnect to any Redis node")
        return False
    
    async def _create_redis_connection(self, node: RedisClusterNode):
        """Create optimized Redis connection with connection pooling"""
        if not aioredis:
            raise ImportError("aioredis is not installed")
            
        redis_url = f"redis://:{node.password}@{node.host}:{node.port}/{self.db}" if node.password else f"redis://{node.host}:{node.port}/{self.db}"
        
        return aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=self.health_check_interval,
            max_connections=node.max_connections,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=30
        )

    async def initialize(self) -> bool:
        """Initialize enhanced Redis connection with monitoring and failover"""
        if not REDIS_AVAILABLE:
            logger.warning("📛 Redis not available - using local cache fallback")
            self.enabled = False
            return False
            
        if not self.enabled:
            logger.info("📛 Redis caching disabled in configuration - using local cache")
            return False

        self.connection_state = RedisConnectionState.CONNECTING
        self.stats.connection_attempts += 1
        
        try:
            # Try to connect to primary node first
            logger.info(f"🔌 Connecting to primary Redis at {self.primary_config.host}:{self.primary_config.port}")
            
            self.redis = await self._create_redis_connection(self.primary_config)
            
            # Test connection
            start_time = time.time()
            await self.redis.ping()
            connection_time = time.time() - start_time
            
            self.connection_state = RedisConnectionState.CONNECTED
            self.stats.last_connection_time = time.time()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            logger.info(f"✅ Enhanced Redis connected successfully in {connection_time:.3f}s")
            logger.info(f"📊 Connection pool: {self.primary_config.max_connections} max connections")
            logger.info(f"🔄 Fallback nodes: {len(self.fallback_nodes)} configured")
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Primary Redis connection failed: {e}")
            
            # Try fallback nodes if available
            if self.fallback_nodes and await self._attempt_reconnection():
                await self._start_health_monitoring()
                return True
            
            # All connections failed
            logger.warning("📛 Redis connection failed - using local cache fallback")
            self.connection_state = RedisConnectionState.FAILED
            self.stats.connection_failures += 1
            return False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            try:
                await self.redis.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")

    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        return f"{self.prefixes.get(prefix, 'kartavya:')}{identifier}"

    def _hash_query(self, query: str, params: Dict[str, Any] = None) -> str:
        """Generate deterministic hash for query caching"""
        query_data = {
            "query": query.lower().strip(),
            "params": params or {}
        }
        query_json = json.dumps(query_data, sort_keys=True)
        return hashlib.sha256(query_json.encode()).hexdigest()[:16]

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with smart failover"""
        start_time = time.time()
        self.stats.total_operations += 1
        
        # Try Redis first if connected
        if self.connection_state == RedisConnectionState.CONNECTED and self.redis:
            try:
                value = await self.redis.get(key)
                response_time = time.time() - start_time
                
                if value is not None:
                    self.stats.successful_operations += 1
                    self.stats.cache_hits += 1
                    
                    # Update response time stats
                    self.stats.response_times.append(response_time)
                    if len(self.stats.response_times) > 100:
                        self.stats.response_times = self.stats.response_times[-100:]
                    
                    parsed_value = json.loads(value)
                    
                    # Update local cache as backup
                    self._update_local_cache(key, parsed_value, self.default_ttl)
                    
                    return parsed_value
                else:
                    self.stats.cache_misses += 1
                    
            except Exception as e:
                logger.warning(f"⚠️ Redis GET error for key {key}: {e}")
                self.stats.failed_operations += 1
                
                # Connection might be lost, check local cache
                if self.connection_state == RedisConnectionState.CONNECTED:
                    self.connection_state = RedisConnectionState.RECONNECTING
                    asyncio.create_task(self._attempt_reconnection())
        
        # Fallback to local cache
        local_value = self._get_from_local_cache(key)
        if local_value is not None:
            logger.debug(f"💾 Local cache HIT for key: {key}")
            self.stats.cache_hits += 1
            self.stats.successful_operations += 1
            return local_value
        
        self.stats.cache_misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with smart failover and adaptive TTL"""
        start_time = time.time()
        self.stats.total_operations += 1
        
        # Calculate adaptive TTL if enabled
        if self.adaptive_ttl_enabled and ttl is None:
            ttl = self._calculate_adaptive_ttl(key, value)
        else:
            ttl = ttl or self.default_ttl
        
        success = False
        
        # Try Redis first if connected
        if self.connection_state == RedisConnectionState.CONNECTED and self.redis:
            try:
                value_json = json.dumps(value, default=str, ensure_ascii=False)
                await self.redis.set(key, value_json, ex=ttl)
                
                response_time = time.time() - start_time
                self.stats.successful_operations += 1
                
                # Update response time stats
                self.stats.response_times.append(response_time)
                if len(self.stats.response_times) > 100:
                    self.stats.response_times = self.stats.response_times[-100:]
                
                success = True
                
            except Exception as e:
                logger.warning(f"⚠️ Redis SET error for key {key}: {e}")
                self.stats.failed_operations += 1
                
                # Connection might be lost
                if self.connection_state == RedisConnectionState.CONNECTED:
                    self.connection_state = RedisConnectionState.RECONNECTING
                    asyncio.create_task(self._attempt_reconnection())
        
        # Always update local cache as backup
        self._update_local_cache(key, value, ttl)
        
        if not success:
            logger.debug(f"💾 Stored in local cache: {key}")
        
        return True  # Always return True since we have local fallback
    
    def _update_local_cache(self, key: str, value: Any, ttl: int):
        """Update local cache with TTL"""
        expiry_time = time.time() + ttl
        self.local_cache[key] = (value, expiry_time)
        
        # Limit local cache size with LRU eviction
        if len(self.local_cache) > self.max_local_cache_size:
            # Remove expired entries first
            current_time = time.time()
            expired_keys = [
                k for k, (_, exp) in self.local_cache.items() 
                if exp < current_time
            ]
            for k in expired_keys:
                del self.local_cache[k]
            
            # If still over limit, remove oldest entries
            if len(self.local_cache) > self.max_local_cache_size:
                # Sort by expiry time and remove oldest
                sorted_items = sorted(
                    self.local_cache.items(), 
                    key=lambda x: x[1][1]
                )
                items_to_remove = len(self.local_cache) - self.max_local_cache_size + 100
                for key_to_remove, _ in sorted_items[:items_to_remove]:
                    del self.local_cache[key_to_remove]
    
    def _get_from_local_cache(self, key: str) -> Optional[Any]:
        """Get value from local cache if not expired"""
        if key not in self.local_cache:
            return None
            
        value, expiry_time = self.local_cache[key]
        
        if time.time() > expiry_time:
            # Expired, remove from cache
            del self.local_cache[key]
            return None
            
        return value
    
    def _calculate_adaptive_ttl(self, key: str, value: Any) -> int:
        """Calculate adaptive TTL based on key type and value size"""
        # Base TTL
        base_ttl = self.default_ttl
        
        # Adjust based on key prefix
        for prefix_name, prefix in self.prefixes.items():
            if key.startswith(prefix):
                if prefix_name == "query":
                    # Query results - shorter TTL for freshness
                    base_ttl = self.query_cache_ttl
                elif prefix_name == "session":
                    # Session data - longer TTL
                    base_ttl = self.session_ttl
                elif prefix_name == "metrics":
                    # Metrics - very short TTL
                    base_ttl = 300  # 5 minutes
                break
        
        # Adjust based on value size (larger values get shorter TTL)
        try:
            value_size = len(json.dumps(value, default=str))
            if value_size > 10000:  # > 10KB
                base_ttl = int(base_ttl * 0.5)  # Halve TTL for large values
            elif value_size > 100000:  # > 100KB
                base_ttl = int(base_ttl * 0.25)  # Quarter TTL for very large values
        except:
            pass  # Use base TTL if serialization fails
        
        return max(300, base_ttl)  # Minimum 5 minutes

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.connected:
            return False
            
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    # Query Caching Methods
    async def cache_query_result(
        self, 
        query: str, 
        result: Dict[str, Any], 
        params: Dict[str, Any] = None,
        ttl: int = None
    ) -> bool:
        """Cache query result for performance"""
        query_hash = self._hash_query(query, params)
        cache_key = self._generate_key("query", query_hash)
        
        cache_data = {
            "query": query,
            "params": params or {},
            "result": result,
            "cached_at": datetime.now().isoformat(),
            "hit_count": 1
        }
        
        return await self.set(cache_key, cache_data, ttl or self.query_cache_ttl)

    async def get_cached_query_result(
        self, 
        query: str, 
        params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        query_hash = self._hash_query(query, params)
        cache_key = self._generate_key("query", query_hash)
        
        cached_data = await self.get(cache_key)
        if cached_data:
            # Update hit count
            cached_data["hit_count"] = cached_data.get("hit_count", 0) + 1
            cached_data["last_hit"] = datetime.now().isoformat()
            await self.set(cache_key, cached_data, self.query_cache_ttl)
            
            logger.info(f"Cache HIT for query hash {query_hash}")
            return cached_data["result"]
            
        logger.info(f"Cache MISS for query hash {query_hash}")
        return None

    # Session and Context Caching
    async def cache_session_context(
        self, 
        session_id: str, 
        context: Dict[str, Any]
    ) -> bool:
        """Cache user session context"""
        cache_key = self._generate_key("session", session_id)
        
        session_data = {
            "session_id": session_id,
            "context": context,
            "updated_at": datetime.now().isoformat()
        }
        
        return await self.set(cache_key, session_data, self.session_ttl)

    async def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached session context"""
        cache_key = self._generate_key("session", session_id)
        cached_data = await self.get(cache_key)
        
        if cached_data:
            return cached_data.get("context", {})
        return None

    async def invalidate_session(self, session_id: str) -> bool:
        """Remove session from cache"""
        cache_key = self._generate_key("session", session_id)
        return await self.delete(cache_key)

    # Conversation Context Caching
    async def cache_conversation_context(
        self,
        conversation_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Cache conversation context for multi-turn conversations"""
        cache_key = self._generate_key("context", conversation_id)
        
        context_data = {
            "conversation_id": conversation_id,
            "context": context,
            "message_count": context.get("message_count", 0),
            "updated_at": datetime.now().isoformat()
        }
        
        return await self.set(cache_key, context_data, self.session_ttl)

    async def get_conversation_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get cached conversation context"""
        cache_key = self._generate_key("context", conversation_id)
        cached_data = await self.get(cache_key)
        
        if cached_data:
            return cached_data.get("context", {})
        return {}

    # Metrics and Analytics Caching
    async def cache_metrics(self, metric_type: str, data: Dict[str, Any], ttl: int = 300):
        """Cache system metrics (5 minute default TTL for metrics)"""
        cache_key = self._generate_key("metrics", metric_type)
        
        metrics_data = {
            "type": metric_type,
            "data": data,
            "generated_at": datetime.now().isoformat()
        }
        
        return await self.set(cache_key, metrics_data, ttl)

    async def get_cached_metrics(self, metric_type: str) -> Optional[Dict[str, Any]]:
        """Get cached metrics"""
        cache_key = self._generate_key("metrics", metric_type)
        cached_data = await self.get(cache_key)
        
        if cached_data:
            return cached_data.get("data", {})
        return None

    # Cache Management
    async def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics with local cache info"""
        base_stats = {
            "enabled": self.enabled,
            "connection_state": self.connection_state.value,
            "clustering_enabled": self.enable_clustering,
            "cluster_id": self.cluster_id,
            "adaptive_ttl_enabled": self.adaptive_ttl_enabled,
            "fallback_nodes_count": len(self.fallback_nodes),
            "local_cache_size": len(self.local_cache),
            "max_local_cache_size": self.max_local_cache_size
        }
        
        # Add our internal statistics
        stats_dict = {
            "total_operations": self.stats.total_operations,
            "successful_operations": self.stats.successful_operations,
            "failed_operations": self.stats.failed_operations,
            "success_rate": self.stats.success_rate,
            "cache_hits": self.stats.cache_hits,
            "cache_misses": self.stats.cache_misses,
            "cache_hit_rate": self.stats.cache_hit_rate,
            "connection_attempts": self.stats.connection_attempts,
            "connection_failures": self.stats.connection_failures,
            "avg_response_time": self.stats.avg_response_time,
            "last_connection_time": self.stats.last_connection_time
        }
        
        base_stats.update(stats_dict)
        
        # Try to get Redis server info if connected
        if self.connection_state == RedisConnectionState.CONNECTED and self.redis:
            try:
                info = await self.redis.info()
                
                redis_stats = {
                    "redis_connected": True,
                    "redis_version": info.get("redis_version"),
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "uptime_in_seconds": info.get("uptime_in_seconds", 0)
                }
                
                # Calculate Redis hit rate
                redis_hits = redis_stats["keyspace_hits"]
                redis_misses = redis_stats["keyspace_misses"]
                if redis_hits + redis_misses > 0:
                    redis_stats["redis_hit_rate"] = round((redis_hits / (redis_hits + redis_misses)) * 100, 2)
                else:
                    redis_stats["redis_hit_rate"] = 0.0
                
                base_stats.update(redis_stats)
                
            except Exception as e:
                base_stats.update({
                    "redis_connected": False,
                    "redis_error": str(e)
                })
        else:
            base_stats["redis_connected"] = False
        
        return base_stats
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics for monitoring"""
        recent_times = self.stats.response_times[-50:] if self.stats.response_times else []
        
        if recent_times:
            p50 = sorted(recent_times)[len(recent_times) // 2]
            p95_index = int(len(recent_times) * 0.95)
            p95 = sorted(recent_times)[p95_index] if p95_index < len(recent_times) else recent_times[-1]
            p99_index = int(len(recent_times) * 0.99)
            p99 = sorted(recent_times)[p99_index] if p99_index < len(recent_times) else recent_times[-1]
        else:
            p50 = p95 = p99 = 0.0
        
        return {
            "response_time_p50": p50,
            "response_time_p95": p95,
            "response_time_p99": p99,
            "avg_response_time": self.stats.avg_response_time,
            "total_operations": self.stats.total_operations,
            "operations_per_second": self._calculate_ops_per_second(),
            "error_rate": (self.stats.failed_operations / max(1, self.stats.total_operations)) * 100,
            "uptime_seconds": time.time() - (self.stats.last_connection_time or time.time())
        }
    
    def _calculate_ops_per_second(self) -> float:
        """Calculate operations per second based on recent activity"""
        if not self.stats.response_times:
            return 0.0
        
        # Estimate based on recent operations (last 100)
        recent_ops = min(100, len(self.stats.response_times))
        if recent_ops < 2:
            return 0.0
        
        # Rough estimate: recent operations / average time window
        avg_time = sum(self.stats.response_times[-recent_ops:]) / recent_ops
        return 1.0 / max(0.001, avg_time)  # Avoid division by zero
    
    async def get_distributed_cache_info(self) -> Dict[str, Any]:
        """Get distributed caching information and node status"""
        return {
            "clustering_enabled": self.enable_clustering,
            "cluster_id": self.cluster_id,
            "primary_node": {
                "host": self.primary_config.host,
                "port": self.primary_config.port,
                "max_connections": self.primary_config.max_connections,
                "is_connected": self.connection_state == RedisConnectionState.CONNECTED
            },
            "fallback_nodes": [
                {
                    "host": node.host,
                    "port": node.port,
                    "weight": node.weight,
                    "max_connections": node.max_connections
                }
                for node in self.fallback_nodes
            ],
            "local_cache": {
                "enabled": True,
                "size": len(self.local_cache),
                "max_size": self.max_local_cache_size,
                "usage_percentage": (len(self.local_cache) / self.max_local_cache_size) * 100
            },
            "connection_state": self.connection_state.value,
            "health_check_interval": self.health_check_interval
        }

    async def clear_cache(self, pattern: str = None) -> bool:
        """Clear cache - use with caution"""
        if not self.enabled or not self.connected:
            return False
            
        try:
            if pattern:
                # Clear specific pattern
                keys = await self.redis.keys(f"kartavya:{pattern}:*")
                if keys:
                    await self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys matching pattern: {pattern}")
            else:
                # Clear all Kartavya keys
                keys = await self.redis.keys("kartavya:*")
                if keys:
                    await self.redis.delete(*keys)
                logger.info(f"Cleared all {len(keys)} Kartavya cache keys")
                
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis_manager() -> RedisManager:
    """Dependency function to get Redis manager"""
    return redis_manager
