#!/usr/bin/env python3
"""
Debug MongoDB client status
"""

from src.core.database.clients import MongoDBClient

# Initialize MongoDB client to see its status
mongodb_client = MongoDBClient()

print(f"MongoDB enabled: {mongodb_client.enabled}")
print(f"MongoDB client: {mongodb_client.client}")
print(f"MongoDB database: {mongodb_client.database}")

if mongodb_client.enabled:
    print("❌ MongoDB is enabled - this will prevent local auth fallback")
else:
    print("✅ MongoDB is disabled - will use local auth fallback")
