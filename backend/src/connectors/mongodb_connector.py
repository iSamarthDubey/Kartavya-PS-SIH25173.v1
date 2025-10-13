"""
MongoDB SIEM Connector  
Production-ready connector for storing and querying SIEM data in MongoDB
Designed for high-performance queries on large datasets
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import json
import os
import time
from contextlib import asynccontextmanager
from .base import BaseSIEMConnector

logger = logging.getLogger(__name__)

class MongoDBConnector(BaseSIEMConnector):
    """MongoDB connector for production SIEM data storage and querying"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None
        self.db = None
        self.collections = {}
        self.connected = False
        
        # MongoDB configuration
        self.mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("MONGODB_DATABASE", "kartavya_siem")
        
        # Enhanced connection pool settings
        self.pool_config = {
            "maxPoolSize": int(os.getenv("MONGODB_MAX_POOL_SIZE", "100")),  # Increased from 50
            "minPoolSize": int(os.getenv("MONGODB_MIN_POOL_SIZE", "20")),   # Increased from 10
            "maxIdleTimeMS": int(os.getenv("MONGODB_MAX_IDLE_TIME", "45000")),  # 45 seconds
            "waitQueueTimeoutMS": int(os.getenv("MONGODB_WAIT_TIMEOUT", "10000")),  # 10 seconds
            "serverSelectionTimeoutMS": int(os.getenv("MONGODB_SERVER_TIMEOUT", "5000")),
            "connectTimeoutMS": int(os.getenv("MONGODB_CONNECT_TIMEOUT", "10000")),
            "socketTimeoutMS": int(os.getenv("MONGODB_SOCKET_TIMEOUT", "30000")),
            "heartbeatFrequencyMS": 10000,  # 10 seconds
            "retryWrites": True,
            "retryReads": True,
            "readConcern": {"level": "majority"},
            "writeConcern": {"w": "majority", "wtimeout": 5000}
        }
        
        # Connection monitoring
        self.connection_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "last_connection_check": None,
            "connection_failures": 0,
            "consecutive_failures": 0
        }
        
        # Retry configuration
        self.max_retries = int(os.getenv("MONGODB_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("MONGODB_RETRY_DELAY", "1.0"))
        
        # Collection names for different types of SIEM data
        self.collection_names = {
            "events": "siem_events",
            "alerts": "security_alerts", 
            "threats": "threat_indicators",
            "users": "user_activities",
            "network": "network_traffic",
            "metadata": "system_metadata"
        }
        
    async def initialize(self) -> bool:
        """Initialize MongoDB connection and setup collections"""
        return await self.connect()
    
    async def connect(self) -> bool:
        """Connect to MongoDB with enhanced connection pooling and monitoring"""
        max_attempts = self.max_retries + 1
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"🔌 Connecting to MongoDB (attempt {attempt + 1}/{max_attempts}): {self.mongo_url}")
                
                # Create async MongoDB client with optimized pool settings
                self.client = AsyncIOMotorClient(
                    self.mongo_url,
                    **self.pool_config
                )
                
                # Test connection with timeout
                start_time = time.time()
                await asyncio.wait_for(
                    self.client.admin.command('ping'), 
                    timeout=5.0
                )
                connection_time = time.time() - start_time
                
                logger.info(f"✅ MongoDB connection successful in {connection_time:.3f}s")
                
                # Get database
                self.db = self.client[self.database_name]
                
                # Setup collections and indexes
                await self._setup_collections()
                
                # Start connection monitoring
                asyncio.create_task(self._monitor_connection_health())
                
                # Reset failure counters on successful connection
                self.connection_stats["connection_failures"] = 0
                self.connection_stats["consecutive_failures"] = 0
                self.connection_stats["last_connection_check"] = datetime.now()
                
                self.connected = True
                logger.info(f"✅ MongoDB connector ready with database: {self.database_name}")
                logger.info(f"📊 Pool config: Max={self.pool_config['maxPoolSize']}, Min={self.pool_config['minPoolSize']}")
                return True
                
            except Exception as e:
                self.connection_stats["connection_failures"] += 1
                self.connection_stats["consecutive_failures"] += 1
                
                if attempt < max_attempts - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"⚠️ MongoDB connection attempt {attempt + 1} failed: {e}")
                    logger.info(f"🔄 Retrying in {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to connect to MongoDB after {max_attempts} attempts: {e}")
                    return False
        
        return False
    
    async def _setup_collections(self):
        """Create collections and indexes for optimal query performance"""
        logger.info("🔧 Setting up MongoDB collections and indexes...")
        
        for collection_key, collection_name in self.collection_names.items():
            collection = self.db[collection_name]
            self.collections[collection_key] = collection
            
            # Create indexes based on collection type
            if collection_key == "events":
                # SIEM events - optimize for time-based and field queries
                await collection.create_index([("@timestamp", -1)])
                await collection.create_index([("event.severity", 1)])
                await collection.create_index([("source.ip", 1)])
                await collection.create_index([("destination.ip", 1)])
                await collection.create_index([("event.category", 1)])
                await collection.create_index([
                    ("@timestamp", -1), 
                    ("event.severity", 1)
                ])
                
            elif collection_key == "alerts":
                # Security alerts - optimize for status and severity queries
                await collection.create_index([("created_at", -1)])
                await collection.create_index([("severity", 1)])
                await collection.create_index([("status", 1)])
                await collection.create_index([("alert_type", 1)])
                
            elif collection_key == "users":
                # User activities - optimize for user and time queries
                await collection.create_index([("user.name", 1)])
                await collection.create_index([("@timestamp", -1)])
                await collection.create_index([("user.ip", 1)])
                await collection.create_index([("event.action", 1)])
                
            elif collection_key == "network":
                # Network traffic - optimize for IP and protocol queries
                await collection.create_index([("source.ip", 1)])
                await collection.create_index([("destination.ip", 1)])
                await collection.create_index([("network.protocol", 1)])
                await collection.create_index([("@timestamp", -1)])
                
        logger.info("✅ Collections and indexes created successfully")
    
    async def _monitor_connection_health(self):
        """Background task to monitor MongoDB connection health"""
        while self.connected:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if not self.connected:
                    break
                
                # Perform health check
                start_time = time.time()
                await asyncio.wait_for(
                    self.client.admin.command('ping'),
                    timeout=5.0
                )
                response_time = time.time() - start_time
                
                # Update health stats
                self.connection_stats["last_connection_check"] = datetime.now()
                self.connection_stats["consecutive_failures"] = 0
                
                # Log slow health checks
                if response_time > 2.0:
                    logger.warning(f"⚠️ MongoDB health check slow: {response_time:.3f}s")
                    
            except Exception as e:
                self.connection_stats["consecutive_failures"] += 1
                logger.error(f"❌ MongoDB health check failed: {e}")
                
                # If too many consecutive failures, attempt reconnection
                if self.connection_stats["consecutive_failures"] >= 3:
                    logger.warning("🔄 Attempting MongoDB reconnection due to health check failures")
                    await self._attempt_reconnection()
    
    async def _attempt_reconnection(self):
        """Attempt to reconnect to MongoDB"""
        try:
            self.connected = False
            if self.client:
                self.client.close()
            
            # Wait before reconnection attempt
            await asyncio.sleep(5.0)
            
            # Attempt reconnection
            if await self.connect():
                logger.info("✅ MongoDB reconnection successful")
            else:
                logger.error("❌ MongoDB reconnection failed")
                
        except Exception as e:
            logger.error(f"❌ Error during MongoDB reconnection: {e}")
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.connected = False  # Stop health monitoring
            self.client.close()
            logger.info("🔌 MongoDB connection closed")
    
    async def migrate_dataset_to_mongodb(self, dataset: List[Dict], collection_type: str = "events") -> bool:
        """Migrate processed dataset to MongoDB for production use"""
        try:
            if not self.connected:
                logger.error("❌ Not connected to MongoDB")
                return False
            
            if not dataset or len(dataset) == 0:
                logger.warning("⚠️ No data to migrate")
                return False
            
            collection = self.collections.get(collection_type)
            if not collection:
                logger.error(f"❌ Unknown collection type: {collection_type}")
                return False
            
            logger.info(f"🔄 Migrating {len(dataset)} records to MongoDB collection: {collection_type}")
            
            # Add migration metadata
            for record in dataset:
                record["_migration_timestamp"] = datetime.now()
                record["_source"] = "dataset_migration"
            
            # Batch insert for better performance
            batch_size = 1000
            total_inserted = 0
            
            for i in range(0, len(dataset), batch_size):
                batch = dataset[i:i + batch_size]
                try:
                    result = await collection.insert_many(batch, ordered=False)
                    total_inserted += len(result.inserted_ids)
                    
                    if i % (batch_size * 10) == 0:  # Log every 10 batches
                        logger.info(f"📈 Migrated {total_inserted}/{len(dataset)} records...")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Batch insert failed for batch {i//batch_size}: {e}")
                    continue
            
            # Create summary document
            summary = {
                "migration_date": datetime.now(),
                "collection_type": collection_type,
                "total_records": len(dataset),
                "successfully_inserted": total_inserted,
                "migration_source": "huggingface_dataset",
                "status": "completed"
            }
            
            await self.collections["metadata"].insert_one(summary)
            
            logger.info(f"✅ Migration completed: {total_inserted}/{len(dataset)} records migrated to {collection_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    async def execute_query(self, query: Dict[str, Any], size: int = 100) -> List[Dict]:
        """Execute SIEM query against MongoDB with retry logic and monitoring"""
        max_attempts = self.max_retries + 1
        
        for attempt in range(max_attempts):
            start_time = time.time()
            
            try:
                if not self.connected:
                    if attempt == 0:  # Only try reconnection on first attempt
                        logger.warning("⚠️ Not connected to MongoDB, attempting reconnection...")
                        if await self.connect():
                            logger.info("✅ Reconnected to MongoDB successfully")
                        else:
                            logger.error("❌ Failed to reconnect to MongoDB")
                            return []
                    else:
                        logger.error("❌ Not connected to MongoDB")
                        return []
                
                # Parse the query to determine which collection to use
                collection_type = self._determine_collection_type(query)
                collection = self.collections.get(collection_type, self.collections["events"])
                
                # Convert SIEM query to MongoDB query
                mongo_query = self._convert_to_mongo_query(query)
                
                if attempt == 0:  # Log only on first attempt
                    logger.info(f"🔍 Executing MongoDB query on {collection_type}: {mongo_query}")
                
                # Execute query with timeout and performance monitoring
                query_start = time.time()
                cursor = collection.find(mongo_query).limit(size).sort("@timestamp", -1)
                
                # Execute with timeout
                results = await asyncio.wait_for(
                    cursor.to_list(length=size),
                    timeout=30.0  # 30 second query timeout
                )
                
                query_time = time.time() - query_start
                
                # Convert ObjectId to string for JSON serialization
                for result in results:
                    if "_id" in result:
                        result["_id"] = str(result["_id"])
                
                # Update performance statistics
                self.connection_stats["total_queries"] += 1
                self.connection_stats["successful_queries"] += 1
                
                # Update average response time
                total_successful = self.connection_stats["successful_queries"]
                current_avg = self.connection_stats["avg_response_time"]
                self.connection_stats["avg_response_time"] = (
                    (current_avg * (total_successful - 1) + query_time) / total_successful
                )
                
                # Log slow queries
                if query_time > 5.0:
                    logger.warning(f"🐌 Slow MongoDB query detected: {query_time:.3f}s for {len(results)} results")
                
                if attempt == 0 or len(results) > 0:  # Log success on first attempt or when results found
                    logger.info(f"✅ Query executed successfully: {len(results)} results in {query_time:.3f}s")
                
                return results
                
            except asyncio.TimeoutError:
                self.connection_stats["failed_queries"] += 1
                if attempt < max_attempts - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⏱️ Query timeout on attempt {attempt + 1}, retrying in {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("❌ Query execution timed out after all retry attempts")
                    return []
                    
            except Exception as e:
                self.connection_stats["total_queries"] += 1
                self.connection_stats["failed_queries"] += 1
                
                if attempt < max_attempts - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Query execution attempt {attempt + 1} failed: {e}")
                    logger.info(f"🔄 Retrying in {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
                    
                    # Check if it's a connection error and attempt reconnection
                    if "connection" in str(e).lower() or "timeout" in str(e).lower():
                        logger.info("🔄 Attempting to reconnect due to connection error")
                        await self._attempt_reconnection()
                else:
                    logger.error(f"❌ Query execution failed after {max_attempts} attempts: {e}")
                    return []
        
        return []
    
    def _determine_collection_type(self, query: Dict[str, Any]) -> str:
        """Determine which MongoDB collection to query based on query content"""
        query_str = str(query).lower()
        
        if any(term in query_str for term in ["alert", "incident", "threat"]):
            return "alerts"
        elif any(term in query_str for term in ["user", "login", "authentication"]):
            return "users"  
        elif any(term in query_str for term in ["network", "traffic", "connection"]):
            return "network"
        else:
            return "events"  # Default to events collection
    
    def _convert_to_mongo_query(self, siem_query: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SIEM query to MongoDB query format"""
        mongo_query = {}
        
        # Handle text search
        if "query" in siem_query and siem_query["query"]:
            query_text = siem_query["query"]
            if query_text != "*":
                # Create text search across multiple fields
                mongo_query["$or"] = [
                    {"event.action": {"$regex": query_text, "$options": "i"}},
                    {"event.category": {"$regex": query_text, "$options": "i"}},
                    {"source.ip": {"$regex": query_text, "$options": "i"}},
                    {"destination.ip": {"$regex": query_text, "$options": "i"}},
                    {"user.name": {"$regex": query_text, "$options": "i"}},
                    {"message": {"$regex": query_text, "$options": "i"}}
                ]
        
        # Handle time range
        if "time_range" in siem_query:
            time_range = siem_query["time_range"]
            if time_range:
                # Convert time range to MongoDB date query
                now = datetime.now()
                if time_range.endswith("h"):
                    hours = int(time_range[:-1])
                    start_time = now - timedelta(hours=hours)
                elif time_range.endswith("d"):
                    days = int(time_range[:-1])  
                    start_time = now - timedelta(days=days)
                else:
                    start_time = now - timedelta(hours=24)  # Default to 24h
                
                mongo_query["@timestamp"] = {"$gte": start_time}
        
        # Handle severity filter
        if "severity" in siem_query:
            mongo_query["event.severity"] = siem_query["severity"]
        
        return mongo_query
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        try:
            stats = {}
            
            for collection_key, collection in self.collections.items():
                count = await collection.count_documents({})
                stats[collection_key] = {
                    "count": count,
                    "collection_name": self.collection_names[collection_key]
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {}
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection and performance statistics"""
        try:
            stats = self.connection_stats.copy()
            
            # Add connection pool info if available
            if self.client:
                try:
                    # Get server status for additional metrics
                    server_status = await self.client.admin.command("serverStatus")
                    
                    stats.update({
                        "pool_config": self.pool_config,
                        "database_name": self.database_name,
                        "connected": self.connected,
                        "server_info": {
                            "version": server_status.get("version"),
                            "uptime": server_status.get("uptime"),
                            "connections_current": server_status.get("connections", {}).get("current", 0),
                            "connections_available": server_status.get("connections", {}).get("available", 0)
                        },
                        "collection_counts": await self.get_collection_stats()
                    })
                    
                    # Calculate success rate
                    total_queries = stats["total_queries"]
                    if total_queries > 0:
                        stats["success_rate"] = (stats["successful_queries"] / total_queries) * 100
                    else:
                        stats["success_rate"] = 100.0
                        
                except Exception as e:
                    logger.warning(f"Could not get extended server stats: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old data to manage storage"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            total_deleted = 0
            for collection_key, collection in self.collections.items():
                if collection_key == "metadata":
                    continue  # Don't delete metadata
                
                result = await collection.delete_many({
                    "@timestamp": {"$lt": cutoff_date}
                })
                
                total_deleted += result.deleted_count
                logger.info(f"🗑️ Deleted {result.deleted_count} old records from {collection_key}")
            
            logger.info(f"✅ Cleanup completed: {total_deleted} total records deleted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return False
