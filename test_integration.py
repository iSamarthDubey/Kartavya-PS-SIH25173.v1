#!/usr/bin/env python3
"""Test complete integration of Kartavya SIEM Assistant"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_backend():
    """Test backend endpoints"""
    base_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        async with session.get(f"{base_url}/health") as resp:
            if resp.status == 200:
                print("✅ Health check passed")
            else:
                print("❌ Health check failed")
                
        # Test query endpoint
        test_query = {
            "query": "Show me failed login attempts in the last 24 hours",
            "session_id": "test-session"
        }
        
        async with session.post(
            f"{base_url}/api/v1/query",
            json=test_query,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Query endpoint working")
                print(f"  Intent: {result.get('intent')}")
                print(f"  Entities: {len(result.get('entities', []))} found")
            else:
                print("❌ Query endpoint failed")

if __name__ == "__main__":
    print("Testing Kartavya SIEM Assistant Integration...")
    asyncio.run(test_backend())
