#!/usr/bin/env python3
"""
Quick System Verification Test
"""

import requests
import json

def test_quick():
    """Quick test of the system."""
    
    print("🔍 QUICK SYSTEM VERIFICATION")
    print("=" * 40)
    
    # Test backend
    try:
        print("1. 🚀 Testing Backend...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend healthy: {data.get('status')}")
            components = data.get('components', {})
            working = sum(1 for s in components.values() if s)
            print(f"   📊 Components: {working}/{len(components)} working")
        else:
            print(f"   ❌ Backend unhealthy: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend error: {e}")
    
    # Test query
    try:
        print("\n2. 🧠 Testing Query...")
        payload = {"query": "show security alerts", "max_results": 3}
        response = requests.post("http://localhost:8000/query", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Query successful: {data.get('intent')}")
            print(f"   📊 Results: {len(data.get('results', []))}")
        else:
            print(f"   ❌ Query failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Query error: {e}")
    
    # Test frontend
    try:
        print("\n3. 🎨 Testing Frontend...")
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend accessible")
        else:
            print(f"   ⚠️ Frontend status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Frontend check: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 VERIFICATION COMPLETE!")
    print("📊 Backend: http://localhost:8000/docs")
    print("🎨 Frontend: http://localhost:8501")
    print("=" * 40)

if __name__ == "__main__":
    test_quick()