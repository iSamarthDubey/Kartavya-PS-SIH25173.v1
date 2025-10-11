#!/usr/bin/env python3
"""
Debug login flow step by step
"""

import requests
import json
import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database.clients import MongoDBClient
from src.security.auth_manager import AuthManager
from src.api.routes.auth import get_user_by_identifier

async def test_auth_components():
    print("🔍 Testing Authentication Components\n")
    
    # 1. Test MongoDB status
    print("1️⃣ MongoDB Status:")
    mongodb_client = MongoDBClient()
    print(f"   Enabled: {mongodb_client.enabled}")
    
    # 2. Test Auth Manager
    print("\n2️⃣ Auth Manager:")
    auth_manager = AuthManager(user_store_path="data/users.json")
    print(f"   Users loaded: {len(auth_manager._users)}")
    
    # 3. Test get_user_by_identifier function
    print("\n3️⃣ User Lookup Function:")
    test_identifiers = ["admin@kartavya.demo", "security_admin", "analyst@kartavya.demo", "security_analyst"]
    
    for identifier in test_identifiers:
        user_profile = await get_user_by_identifier(identifier)
        if user_profile:
            print(f"   {identifier} -> ✅ Found: {user_profile['username']} ({user_profile['role']})")
        else:
            print(f"   {identifier} -> ❌ Not found")
    
    # 4. Test password authentication
    print("\n4️⃣ Password Authentication:")
    for identifier in ["security_admin", "security_analyst"]:
        user_profile = await get_user_by_identifier(identifier)
        if user_profile:
            username = user_profile['username']
            is_valid = auth_manager.authenticate(username, "Admin!2025")
            print(f"   {username} with 'Admin!2025': {'✅ Valid' if is_valid else '❌ Invalid'}")

def test_api_endpoint():
    print("\n5️⃣ API Endpoint Test:")
    test_data = {
        'identifier': 'admin@kartavya.demo',
        'password': 'Admin!2025'
    }
    
    try:
        response = requests.post('http://localhost:8000/api/auth/login', json=test_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

async def main():
    await test_auth_components()
    test_api_endpoint()

if __name__ == "__main__":
    asyncio.run(main())
