"""
Data Caching and Optimization Layer
Provides Redis caching, query optimization, result pagination, and performance monitoring
"""

import os
import json
import hashlib
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import gzip
from contextlib import asynccontextmanager

# Redis imports (with fallback)
try:
    import redis.asyncio as redis
    import redis.exceptions
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies"""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"
    REFRESH_AHEAD = "refresh_ahead"


@dataclass
class CacheConfig:
    """Cache configuration"""
    redis_url: str = "redis://localhost:6379/0"
    default_ttl: int = 3600  # 1 hour
    max_memory: str = "512mb"
    max_connections: int = 100
    connection_timeout: int = 5
    enable_compression: bool = True
    compression_threshold: int = 1024  # bytes
    key_prefix: str = "synrgy:"
    strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    memory_usage: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100


class CacheManager:
    """Advanced cache manager with Redis backend and optimization"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize cache manager"""
        self.config = config or CacheConfig()
        self.redis_client = None
        self.local_cache = {}  # Fallback local cache
        self.metrics = CacheMetrics()
        self.connected = False
        
        # Performance monitoring
        self.performance_stats = {
            "query_times": [],
            "cache_operations": [],
            "memory_usage_history": []
        }
        
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using local cache fallback")
            return False
        
        try:
            # Create Redis connection pool
            self.redis_client = redis.from_url(
                self.config.redis_url,
                max_connections=self.config.max_connections,
                socket_connect_timeout=self.config.connection_timeout,
                decode_responses=False  # We handle encoding/decoding
            )
            
            # Test connection
            await self.redis_client.ping()
            self.connected = True
            logger.info("Redis connection established successfully")
            
            # Configure Redis
            await self._configure_redis()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            return False
    
    async def get(
        self, 
        key: str, 
        default: Any = None,
        deserializer: Optional[Callable] = None
    ) -> Any:
        """Get value from cache"""
        start_time = time.time()
        full_key = self._build_key(key)
        
        try:
            self.metrics.total_requests += 1
            
            if self.connected and self.redis_client:
                # Try Redis first
                cached_data = await self.redis_client.get(full_key)
                if cached_data is not None:
                    self.metrics.hits += 1
                    value = self._deserialize(cached_data, deserializer)
                    self._update_performance_stats("get", time.time() - start_time, True)
                    return value
            
            # Fallback to local cache
            if full_key in self.local_cache:
                entry = self.local_cache[full_key]
                if entry["expires_at"] > time.time():
                    self.metrics.hits += 1
                    self._update_performance_stats("get", time.time() - start_time, True)
                    return entry["data"]
                else:
                    # Expired entry
                    del self.local_cache[full_key]
            
            # Cache miss
            self.metrics.misses += 1
            self._update_performance_stats("get", time.time() - start_time, False)
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.metrics.errors += 1
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serializer: Optional[Callable] = None
    ) -> bool:
        """Set value in cache"""
        start_time = time.time()
        full_key = self._build_key(key)
        ttl = ttl or self.config.default_ttl
        
        try:
            serialized_data = self._serialize(value, serializer)
            
            if self.connected and self.redis_client:
                # Store in Redis
                await self.redis_client.setex(full_key, ttl, serialized_data)
                
            # Also store in local cache as backup
            self.local_cache[full_key] = {
                "data": value,
                "expires_at": time.time() + ttl
            }
            
            self.metrics.sets += 1
            self._update_performance_stats("set", time.time() - start_time, True)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.metrics.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        start_time = time.time()
        full_key = self._build_key(key)
        
        try:
            deleted = False
            
            if self.connected and self.redis_client:
                result = await self.redis_client.delete(full_key)
                deleted = result > 0
            
            # Remove from local cache
            if full_key in self.local_cache:
                del self.local_cache[full_key]
                deleted = True
            
            if deleted:
                self.metrics.deletes += 1
            
            self._update_performance_stats("delete", time.time() - start_time, deleted)
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.metrics.errors += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        full_key = self._build_key(key)
        
        try:
            if self.connected and self.redis_client:
                return bool(await self.redis_client.exists(full_key))
            
            # Check local cache
            if full_key in self.local_cache:
                entry = self.local_cache[full_key]
                if entry["expires_at"] > time.time():
                    return True
                else:
                    del self.local_cache[full_key]
            
            return False
            
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key"""
        full_key = self._build_key(key)
        
        try:
            if self.connected and self.redis_client:
                return bool(await self.redis_client.expire(full_key, ttl))
            
            # Update local cache expiration
            if full_key in self.local_cache:
                self.local_cache[full_key]["expires_at"] = time.time() + ttl
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value"""
        full_key = self._build_key(key)
        
        try:
            if self.connected and self.redis_client:
                return await self.redis_client.incrby(full_key, amount)
            
            # Local cache increment
            if full_key not in self.local_cache:
                self.local_cache[full_key] = {
                    "data": 0,
                    "expires_at": time.time() + self.config.default_ttl
                }
            
            current_value = self.local_cache[full_key]["data"]
            new_value = int(current_value) + amount
            self.local_cache[full_key]["data"] = new_value
            return new_value
            
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        results = {}
        
        if self.connected and self.redis_client:
            try:
                full_keys = [self._build_key(key) for key in keys]
                cached_values = await self.redis_client.mget(full_keys)
                
                for i, cached_data in enumerate(cached_values):
                    if cached_data is not None:
                        results[keys[i]] = self._deserialize(cached_data)
                        self.metrics.hits += 1
                    else:
                        self.metrics.misses += 1
                
                self.metrics.total_requests += len(keys)
                return results
                
            except Exception as e:
                logger.error(f"Cache get_many error: {e}")
        
        # Fallback to individual gets
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        
        return results
    
    async def set_many(
        self, 
        data: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values in cache"""
        ttl = ttl or self.config.default_ttl
        
        if self.connected and self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                
                for key, value in data.items():
                    full_key = self._build_key(key)
                    serialized_data = self._serialize(value)
                    pipe.setex(full_key, ttl, serialized_data)
                
                await pipe.execute()
                self.metrics.sets += len(data)
                return True
                
            except Exception as e:
                logger.error(f"Cache set_many error: {e}")
        
        # Fallback to individual sets
        success_count = 0
        for key, value in data.items():
            if await self.set(key, value, ttl):
                success_count += 1
        
        return success_count == len(data)
    
    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in namespace"""
        pattern = self._build_key(f"{namespace}*")
        deleted_count = 0
        
        try:
            if self.connected and self.redis_client:
                keys = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    keys.append(key)
                
                if keys:
                    deleted_count = await self.redis_client.delete(*keys)
            
            # Clear from local cache
            to_delete = [key for key in self.local_cache.keys() if key.startswith(pattern[:-1])]  # Remove * from pattern
            for key in to_delete:
                del self.local_cache[key]
                deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache clear_namespace error: {e}")
            return 0
    
    async def get_metrics(self) -> CacheMetrics:
        """Get cache performance metrics"""
        if self.connected and self.redis_client:
            try:
                # Update memory usage from Redis
                info = await self.redis_client.info("memory")
                self.metrics.memory_usage = info.get("used_memory", 0)
            except Exception as e:
                logger.error(f"Error getting Redis metrics: {e}")
        
        return self.metrics
    
    def _build_key(self, key: str) -> str:
        """Build full cache key with prefix"""
        return f"{self.config.key_prefix}{key}"
    
    def _serialize(self, data: Any, serializer: Optional[Callable] = None) -> bytes:
        """Serialize data for storage"""
        if serializer:
            serialized = serializer(data)
        else:
            # Default serialization
            if isinstance(data, (str, int, float)):
                serialized = str(data).encode()
            else:
                serialized = pickle.dumps(data)
        
        # Compress if enabled and data is large enough
        if (self.config.enable_compression and 
            len(serialized) > self.config.compression_threshold):
            serialized = gzip.compress(serialized)
        
        return serialized
    
    def _deserialize(self, data: bytes, deserializer: Optional[Callable] = None) -> Any:
        """Deserialize data from storage"""
        try:
            # Check if compressed
            if data[:2] == b'\x1f\x8b':  # gzip magic number
                data = gzip.decompress(data)
            
            if deserializer:
                return deserializer(data)
            
            # Try pickle first
            try:
                return pickle.loads(data)
            except:
                # Fallback to string
                return data.decode()
                
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    def _update_performance_stats(self, operation: str, duration: float, success: bool):
        """Update performance statistics"""
        self.performance_stats["cache_operations"].append({
            "operation": operation,
            "duration": duration,
            "success": success,
            "timestamp": time.time()
        })
        
        # Keep only recent stats (last 1000 operations)
        if len(self.performance_stats["cache_operations"]) > 1000:
            self.performance_stats["cache_operations"] = self.performance_stats["cache_operations"][-1000:]
    
    async def _configure_redis(self):
        """Configure Redis settings"""
        try:
            if self.connected and self.redis_client:
                # Set memory policy
                await self.redis_client.config_set("maxmemory", self.config.max_memory)
                await self.redis_client.config_set("maxmemory-policy", "allkeys-lru")
                
                # Set save settings (optional)
                await self.redis_client.config_set("save", "900 1 300 10 60 10000")
                
        except Exception as e:
            logger.warning(f"Could not configure Redis: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        self.local_cache.clear()


class QueryOptimizer:
    """Query optimization and result caching"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.query_stats = {}
        
    async def optimize_query(self, query: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Optimize query and return cache key"""
        # Generate cache key from query
        query_hash = self._generate_query_hash(query)
        
        # Track query patterns
        self._track_query_pattern(query)
        
        # Apply optimizations
        optimized_query = await self._apply_optimizations(query)
        
        return optimized_query, query_hash
    
    async def cache_query_result(
        self, 
        query_hash: str, 
        results: Any, 
        ttl: Optional[int] = None
    ):
        """Cache query results"""
        cache_key = f"query_result:{query_hash}"
        await self.cache_manager.set(cache_key, results, ttl)
    
    async def get_cached_result(self, query_hash: str) -> Optional[Any]:
        """Get cached query result"""
        cache_key = f"query_result:{query_hash}"
        return await self.cache_manager.get(cache_key)
    
    def _generate_query_hash(self, query: Dict[str, Any]) -> str:
        """Generate hash for query caching"""
        # Normalize query for consistent hashing
        normalized = self._normalize_query(query)
        query_str = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(query_str.encode()).hexdigest()[:16]
    
    def _normalize_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize query for consistent caching"""
        normalized = {}
        
        # Sort and standardize fields
        for key, value in query.items():
            if key == "sort":
                # Normalize sorting
                if isinstance(value, list):
                    normalized[key] = sorted(value)
                else:
                    normalized[key] = value
            elif key == "size":
                # Round size to nearest 10 for better cache hit rates
                normalized[key] = ((value // 10) + 1) * 10
            else:
                normalized[key] = value
        
        return normalized
    
    def _track_query_pattern(self, query: Dict[str, Any]):
        """Track query patterns for optimization"""
        query_type = query.get("_metadata", {}).get("query_type", "unknown")
        
        if query_type not in self.query_stats:
            self.query_stats[query_type] = {
                "count": 0,
                "avg_size": 0,
                "common_fields": {},
                "performance": []
            }
        
        self.query_stats[query_type]["count"] += 1
        
        # Track common fields
        for field in query.get("query", {}).get("bool", {}).get("must", []):
            field_name = list(field.keys())[0] if field else "unknown"
            self.query_stats[query_type]["common_fields"][field_name] = \
                self.query_stats[query_type]["common_fields"].get(field_name, 0) + 1
    
    async def _apply_optimizations(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Apply query optimizations"""
        optimized = query.copy()
        
        # Optimize Elasticsearch queries
        if "query" in optimized and "bool" in optimized["query"]:
            bool_query = optimized["query"]["bool"]
            
            # Move range queries to filter context for better caching
            if "must" in bool_query:
                must_queries = bool_query["must"]
                filter_queries = bool_query.get("filter", [])
                
                new_must = []
                for q in must_queries:
                    if "range" in q or "term" in q:
                        filter_queries.append(q)
                    else:
                        new_must.append(q)
                
                bool_query["must"] = new_must
                bool_query["filter"] = filter_queries
        
        # Add query optimization hints
        if "_metadata" not in optimized:
            optimized["_metadata"] = {}
        
        optimized["_metadata"]["optimized"] = True
        optimized["_metadata"]["optimization_time"] = datetime.now().isoformat()
        
        return optimized


class ResultPaginator:
    """Advanced result pagination with caching"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.page_size = 100
        self.max_pages = 100
        
    async def paginate_results(
        self, 
        results: List[Dict[str, Any]], 
        page: int = 1, 
        page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Paginate results with metadata"""
        page_size = page_size or self.page_size
        total_results = len(results)
        total_pages = (total_results + page_size - 1) // page_size
        
        # Validate page number
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages if total_pages > 0 else 1
        
        # Calculate pagination
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_results)
        page_results = results[start_index:end_index]
        
        return {
            "data": page_results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_results": total_results,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "next_page": page + 1 if page < total_pages else None,
                "previous_page": page - 1 if page > 1 else None
            }
        }
    
    async def cache_paginated_results(
        self, 
        query_hash: str, 
        results: List[Dict[str, Any]], 
        ttl: Optional[int] = None
    ):
        """Cache paginated results by pages"""
        total_pages = (len(results) + self.page_size - 1) // self.page_size
        
        # Cache each page separately
        for page in range(1, min(total_pages + 1, self.max_pages + 1)):
            start_index = (page - 1) * self.page_size
            end_index = min(start_index + self.page_size, len(results))
            page_results = results[start_index:end_index]
            
            cache_key = f"page:{query_hash}:{page}"
            await self.cache_manager.set(cache_key, page_results, ttl)
        
        # Cache metadata
        metadata = {
            "total_results": len(results),
            "total_pages": total_pages,
            "page_size": self.page_size
        }
        
        metadata_key = f"page_meta:{query_hash}"
        await self.cache_manager.set(metadata_key, metadata, ttl)
    
    async def get_cached_page(
        self, 
        query_hash: str, 
        page: int
    ) -> Optional[Dict[str, Any]]:
        """Get cached page results"""
        # Get metadata first
        metadata_key = f"page_meta:{query_hash}"
        metadata = await self.cache_manager.get(metadata_key)
        
        if not metadata:
            return None
        
        # Validate page
        if page < 1 or page > metadata["total_pages"]:
            return None
        
        # Get page data
        cache_key = f"page:{query_hash}:{page}"
        page_results = await self.cache_manager.get(cache_key)
        
        if page_results is None:
            return None
        
        return {
            "data": page_results,
            "pagination": {
                "page": page,
                "page_size": metadata["page_size"],
                "total_results": metadata["total_results"],
                "total_pages": metadata["total_pages"],
                "has_next": page < metadata["total_pages"],
                "has_previous": page > 1,
                "next_page": page + 1 if page < metadata["total_pages"] else None,
                "previous_page": page - 1 if page > 1 else None
            }
        }


class PerformanceMonitor:
    """Performance monitoring and optimization recommendations"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.performance_data = {
            "query_times": [],
            "cache_performance": [],
            "memory_usage": [],
            "slow_queries": []
        }
        
    async def record_query_performance(
        self, 
        query_hash: str, 
        execution_time: float,
        result_count: int,
        cache_hit: bool
    ):
        """Record query performance metrics"""
        performance_record = {
            "query_hash": query_hash,
            "execution_time": execution_time,
            "result_count": result_count,
            "cache_hit": cache_hit,
            "timestamp": datetime.now().isoformat()
        }
        
        self.performance_data["query_times"].append(performance_record)
        
        # Track slow queries
        if execution_time > 5.0:  # 5 seconds threshold
            self.performance_data["slow_queries"].append(performance_record)
        
        # Keep only recent data
        if len(self.performance_data["query_times"]) > 1000:
            self.performance_data["query_times"] = self.performance_data["query_times"][-1000:]
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        metrics = await self.cache_manager.get_metrics()
        
        # Calculate averages
        recent_queries = self.performance_data["query_times"][-100:]  # Last 100 queries
        avg_query_time = sum(q["execution_time"] for q in recent_queries) / len(recent_queries) if recent_queries else 0
        
        return {
            "cache_metrics": asdict(metrics),
            "query_performance": {
                "average_query_time": avg_query_time,
                "total_queries": len(self.performance_data["query_times"]),
                "slow_queries": len(self.performance_data["slow_queries"]),
                "cache_hit_rate": metrics.hit_rate
            },
            "recommendations": await self._generate_recommendations()
        }
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        metrics = await self.cache_manager.get_metrics()
        
        # Cache hit rate recommendations
        if metrics.hit_rate < 50:
            recommendations.append("Cache hit rate is low. Consider increasing cache TTL or reviewing cache key strategies.")
        
        # Query performance recommendations
        if len(self.performance_data["slow_queries"]) > 10:
            recommendations.append("Multiple slow queries detected. Consider query optimization or adding more specific indexes.")
        
        # Memory usage recommendations
        if metrics.memory_usage > 400 * 1024 * 1024:  # 400MB
            recommendations.append("High cache memory usage detected. Consider implementing cache eviction policies.")
        
        return recommendations


# Factory function to create optimized cache stack
async def create_cache_stack(config: Optional[CacheConfig] = None) -> Tuple[CacheManager, QueryOptimizer, ResultPaginator, PerformanceMonitor]:
    """Create complete caching and optimization stack"""
    cache_config = config or CacheConfig()
    
    # Initialize cache manager
    cache_manager = CacheManager(cache_config)
    await cache_manager.initialize()
    
    # Create optimization components
    query_optimizer = QueryOptimizer(cache_manager)
    result_paginator = ResultPaginator(cache_manager)
    performance_monitor = PerformanceMonitor(cache_manager)
    
    logger.info("Cache and optimization stack initialized successfully")
    
    return cache_manager, query_optimizer, result_paginator, performance_monitor
