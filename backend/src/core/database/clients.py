"""
🗄️ Database Clients - Multi-service support
Handles Supabase (PostgreSQL + Auth), MongoDB Atlas, Redis Cloud
"""

import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from ..config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase client for PostgreSQL, Auth, and Real-time features"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client = None
        self.enabled = False
        
        if settings.supabase_url and settings.supabase_anon_key:
            try:
                from supabase import create_client
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_anon_key
                )
                self.enabled = True
                logger.info("✅ Supabase client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase: {e}")
        else:
            logger.info("🚫 Supabase disabled (missing config)")
    
    async def create_user_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Create user session in Supabase"""
        if not self.enabled:
            logger.debug(f"Mock: Created session for user {user_id}")
            return True  # Mock success when database not available
        
        try:
            result = self.client.table("user_sessions").insert({
                "user_id": user_id,
                "session_data": json.dumps(session_data),
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user sessions from Supabase"""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table("user_sessions").select("*").eq("user_id", user_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    async def log_audit_event(self, event_data: Dict[str, Any]) -> bool:
        """Log audit event to Supabase"""
        if not self.enabled:
            return True
        
        try:
            result = self.client.table("audit_logs").insert({
                **event_data,
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return False


class MongoDBClient:
    """MongoDB Atlas client for SIEM logs and analytics"""
    
    def __init__(self):
        """Initialize MongoDB client"""
        self.client = None
        self.database = None
        self.enabled = False
        
        if settings.mongodb_uri:
            try:
                from pymongo import MongoClient
                import certifi
                self.client = MongoClient(settings.mongodb_uri, tls=True, tlsCAFile=certifi.where())
                self.database = self.client[settings.mongodb_database]
                # Test connection
                self.client.server_info()
                self.enabled = True
                logger.info("✅ MongoDB client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize MongoDB: {e}")
        else:
            logger.info("🚫 MongoDB disabled (missing config)")
    
    async def store_siem_logs(self, logs: List[Dict[str, Any]], collection: str = "siem_logs") -> bool:
        """Store SIEM logs in MongoDB"""
        if not self.enabled:
            return True
        
        try:
            collection_obj = self.database[collection]
            
            # Add metadata to each log
            for log in logs:
                log["_inserted_at"] = datetime.utcnow()
                log["_source"] = "kartavya_assistant"
            
            result = collection_obj.insert_many(logs)
            logger.info(f"Stored {len(result.inserted_ids)} SIEM logs")
            return True
        except Exception as e:
            logger.error(f"Failed to store SIEM logs: {e}")
            return False
    
    async def query_siem_logs(self, query: Dict[str, Any], limit: int = 1000) -> List[Dict[str, Any]]:
        """Query SIEM logs from MongoDB"""
        if not self.enabled:
            return []
        
        try:
            collection_obj = self.database["siem_logs"]
            cursor = collection_obj.find(query).limit(limit).sort("timestamp", -1)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to query SIEM logs: {e}")
            return []
    
    async def get_log_stats(self) -> Dict[str, Any]:
        """Get SIEM log statistics"""
        if not self.enabled:
            return {"total": 0, "collections": []}
        
        try:
            stats = {}
            collections = self.database.list_collection_names()
            
            for collection_name in collections:
                if "log" in collection_name.lower():
                    count = self.database[collection_name].count_documents({})
                    stats[collection_name] = count
            
            return {
                "total": sum(stats.values()),
                "collections": stats,
                "database": settings.mongodb_database
            }
        except Exception as e:
            logger.error(f"Failed to get log stats: {e}")
            return {"total": 0, "collections": [], "error": str(e)}
    
    async def create_indexes(self):
        """Create performance indexes"""
        if not self.enabled:
            return
        
        try:
            collection = self.database["siem_logs"]
            
            # Create indexes for common queries
            indexes = [
                ("timestamp", -1),
                ("event_type", 1),
                ("severity", 1),
                ("source_ip", 1),
                ("user", 1),
                [("timestamp", -1), ("severity", 1)]  # Compound index
            ]
            
            for index in indexes:
                if isinstance(index, list):
                    collection.create_index(index)
                else:
                    collection.create_index([index])
            
            logger.info("✅ MongoDB indexes created")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")


class RedisClient:
    """Redis Cloud client for caching and context management"""
    
    def __init__(self):
        """Initialize Redis client"""
        self.client = None
        self.enabled = False
        
        if settings.redis_url:
            try:
                import redis
                # Parse Redis URL and create client
                if settings.redis_password:
                    self.client = redis.from_url(
                        settings.redis_url,
                        password=settings.redis_password,
                        decode_responses=True
                    )
                else:
                    self.client = redis.from_url(settings.redis_url, decode_responses=True)
                
                # Test connection
                self.client.ping()
                self.enabled = True
                logger.info("✅ Redis client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Redis: {e}")
        else:
            logger.info("🚫 Redis disabled (missing config)")
    
    async def set_context(self, session_id: str, context: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set conversation context in Redis"""
        if not self.enabled:
            return True
        
        try:
            key = f"context:{session_id}"
            value = json.dumps(context)
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set context: {e}")
            return False
    
    async def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation context from Redis"""
        if not self.enabled:
            return {}
        
        try:
            key = f"context:{session_id}"
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return {}
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return {}
    
    async def cache_query_result(self, query_hash: str, result: Dict[str, Any], ttl: int = 300) -> bool:
        """Cache query result in Redis"""
        if not self.enabled:
            return True
        
        try:
            key = f"query_cache:{query_hash}"
            value = json.dumps(result, default=str)  # Handle datetime objects
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to cache query result: {e}")
            return False
    
    async def get_cached_result(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached query result from Redis"""
        if not self.enabled:
            return None
        
        try:
            key = f"query_cache:{query_hash}"
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to get cached result: {e}")
            return None
    
    async def increment_rate_limit(self, identifier: str, window: int = 60) -> int:
        """Increment rate limit counter"""
        if not self.enabled:
            return 1
        
        try:
            key = f"rate_limit:{identifier}"
            current = self.client.incr(key)
            if current == 1:
                self.client.expire(key, window)
            return current
        except Exception as e:
            logger.error(f"Failed to increment rate limit: {e}")
            return 1
    
    async def set_user_cache(self, username: str, user_data: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache user session data"""
        if not self.enabled:
            return True
        
        try:
            key = f"user:{username}"
            value = json.dumps(user_data, default=str)
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to cache user data: {e}")
            return False
    
    async def set_with_expiry(self, key: str, data: Dict[str, Any], ttl: int) -> bool:
        """Set data with expiry"""
        if not self.enabled:
            return True
        
        try:
            value = json.dumps(data, default=str)
            result = self.client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set data with expiry: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.enabled:
            return True
        
        try:
            result = self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete key: {e}")
            return False


class DatabaseManager:
    """Manages all database clients"""
    
    def __init__(self):
        """Initialize all database clients"""
        self.supabase = SupabaseClient()
        self.mongodb = MongoDBClient()
        self.redis = RedisClient()
        
        self._log_status()
    
    def _log_status(self):
        """Log database status"""
        status = []
        if self.supabase.enabled:
            status.append("Supabase")
        if self.mongodb.enabled:
            status.append("MongoDB")
        if self.redis.enabled:
            status.append("Redis")
        
        if status:
            logger.info(f"🗄️ Database clients enabled: {', '.join(status)}")
        else:
            logger.info("🗄️ No external databases configured - using local fallbacks")
    
    async def initialize(self):
        """Initialize database schemas and indexes"""
        if self.mongodb.enabled:
            await self.mongodb.create_indexes()
        
        logger.info("✅ Database initialization complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get database status"""
        return {
            "supabase": {
                "enabled": self.supabase.enabled,
                "url": settings.supabase_url if self.supabase.enabled else None
            },
            "mongodb": {
                "enabled": self.mongodb.enabled,
                "database": settings.mongodb_database if self.mongodb.enabled else None
            },
            "redis": {
                "enabled": self.redis.enabled,
                "url": settings.redis_url if self.redis.enabled else None
            },
            "environment": settings.environment,
            "demo_mode": settings.is_demo
        }


# Global database manager
db_manager = DatabaseManager()
