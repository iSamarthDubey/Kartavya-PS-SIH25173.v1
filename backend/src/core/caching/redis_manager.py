"""
Redis Caching Manager - High-performance caching for SIEM queries and sessions
"""

import asyncio
import json
import logging
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import os

# Use aioredis for async Redis operations
try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

logger = logging.getLogger(__name__)


class RedisManager:
    """
    High-performance Redis caching manager for SIEM queries and session data
    """
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.connected = False
        self.enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # Configuration
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.password = os.getenv("REDIS_PASSWORD", "")
        self.db = int(os.getenv("REDIS_DB", "0"))
        
        # Cache settings
        self.default_ttl = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
        self.query_cache_ttl = int(os.getenv("QUERY_CACHE_TTL", "1800"))  # 30 minutes
        self.session_ttl = int(os.getenv("SESSION_TTL_SECONDS", "86400"))  # 24 hours
        
        # Prefixes for different data types
        self.prefixes = {
            "query": "kartavya:query:",
            "session": "kartavya:session:",
            "context": "kartavya:context:",
            "user": "kartavya:user:",
            "metrics": "kartavya:metrics:"
        }

    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - caching disabled")
            self.enabled = False
            return False
            
        if not self.enabled:
            logger.info("Redis caching disabled in configuration")
            return False

        try:
            # Create Redis connection
            redis_url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}" if self.password else f"redis://{self.host}:{self.port}/{self.db}"
            
            self.redis = aioredis.from_url(
                redis_url,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Test connection
            await self.redis.ping()
            self.connected = True
            
            logger.info(f"✅ Redis connected successfully at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e} - Running without cache")
            self.enabled = False
            self.connected = False
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
        """Get value from cache"""
        if not self.enabled or not self.connected:
            return None
            
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        if not self.enabled or not self.connected:
            return False
            
        try:
            value_json = json.dumps(value, default=str, ensure_ascii=False)
            await self.redis.set(key, value_json, ex=ttl or self.default_ttl)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

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
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.connected:
            return {"enabled": False, "connected": False}
            
        try:
            info = await self.redis.info()
            
            stats = {
                "enabled": True,
                "connected": True,
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": 0
            }
            
            # Calculate hit rate
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"] 
            if hits + misses > 0:
                stats["hit_rate"] = round((hits / (hits + misses)) * 100, 2)
                
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "connected": False, "error": str(e)}

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
