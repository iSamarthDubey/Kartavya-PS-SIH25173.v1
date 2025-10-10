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
        """Connect to MongoDB and setup collections with indexes"""
        try:
            logger.info(f"🔌 Connecting to MongoDB: {self.mongo_url}")
            
            # Create async MongoDB client
            self.client = AsyncIOMotorClient(
                self.mongo_url,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful")
            
            # Get database
            self.db = self.client[self.database_name]
            
            # Setup collections and indexes
            await self._setup_collections()
            
            self.connected = True
            logger.info(f"✅ MongoDB connector ready with database: {self.database_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
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
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
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
        """Execute SIEM query against MongoDB"""
        try:
            if not self.connected:
                logger.error("❌ Not connected to MongoDB")
                return []
            
            # Parse the query to determine which collection to use
            collection_type = self._determine_collection_type(query)
            collection = self.collections.get(collection_type, self.collections["events"])
            
            # Convert SIEM query to MongoDB query
            mongo_query = self._convert_to_mongo_query(query)
            
            logger.info(f"🔍 Executing MongoDB query on {collection_type}: {mongo_query}")
            
            # Execute query with limit and sort
            cursor = collection.find(mongo_query).limit(size).sort("@timestamp", -1)
            results = await cursor.to_list(length=size)
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])
            
            logger.info(f"✅ Query executed successfully: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
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
