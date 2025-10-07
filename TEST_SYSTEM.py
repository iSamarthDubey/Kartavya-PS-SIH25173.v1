#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kartavya SIEM Assistant - System Test
Verifies that backend and frontend are properly integrated
"""

import subprocess
import time
import requests
import json
import sys
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.api_url = f"{self.backend_url}/api/v1"
        self.passed = 0
        self.failed = 0
        
    def print_header(self):
        print("\n" + "="*70)
        print("🧪 KARTAVYA SIEM ASSISTANT - SYSTEM TEST")
        print("="*70 + "\n")
        
    def test_backend_health(self):
        """Test if backend is running and healthy"""
        print("1️⃣ Testing Backend Health...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("   ✅ Backend is healthy")
                    print(f"   Version: {data.get('version')}")
                    self.passed += 1
                    return True
        except requests.exceptions.ConnectionError:
            print("   ❌ Backend is not running!")
            print("   Please start the backend first:")
            print("   cd backend && python -m uvicorn app.main:app --port 8001")
            self.failed += 1
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.failed += 1
            return False
            
    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("\n2️⃣ Testing API Endpoints...")
        
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/api/v1/suggestions", "Query suggestions"),
            ("GET", "/api/v1/stats", "Statistics"),
            ("GET", "/api/v1/intents", "Intent list"),
        ]
        
        for method, endpoint, description in endpoints:
            try:
                url = f"{self.backend_url}{endpoint}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {description}: OK")
                    self.passed += 1
                else:
                    print(f"   ❌ {description}: Failed (Status: {response.status_code})")
                    self.failed += 1
            except Exception as e:
                print(f"   ❌ {description}: Error - {e}")
                self.failed += 1
                
    def test_query_endpoint(self):
        """Test the main query endpoint"""
        print("\n3️⃣ Testing Query Processing...")
        
        test_queries = [
            "Show me failed login attempts in the last 24 hours",
            "Detect malware infections",
            "Generate security report"
        ]
        
        for query in test_queries:
            try:
                response = requests.post(
                    f"{self.api_url}/query",
                    json={"query": query, "session_id": "test"},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"   ✅ Query processed: '{query[:40]}...'")
                        print(f"      Intent: {data.get('intent')}")
                        print(f"      Events found: {len(data.get('results', {}).get('events', []))}")
                        self.passed += 1
                    else:
                        print(f"   ❌ Query failed: {query[:40]}")
                        self.failed += 1
                else:
                    print(f"   ❌ Query error (Status: {response.status_code})")
                    self.failed += 1
            except Exception as e:
                print(f"   ❌ Query error: {e}")
                self.failed += 1
                
    def test_frontend_files(self):
        """Check if frontend files exist"""
        print("\n4️⃣ Checking Frontend Files...")
        
        required_files = [
            "frontend/package.json",
            "frontend/src/App.tsx",
            "frontend/src/services/api.ts",
            "frontend/src/pages/Dashboard.tsx",
            "frontend/src/pages/ChatInterface.tsx"
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            if path.exists():
                print(f"   ✅ {file_path} exists")
                self.passed += 1
            else:
                print(f"   ❌ {file_path} missing")
                self.failed += 1
                
    def test_demo_data(self):
        """Test demo data generation"""
        print("\n5️⃣ Testing Demo Data Generation...")
        
        try:
            response = requests.post(
                f"{self.api_url}/query",
                json={"query": "show all events"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("results", {}).get("events", [])
                stats = data.get("results", {}).get("stats", {})
                charts = data.get("charts", [])
                
                print(f"   ✅ Generated {len(events)} demo events")
                print(f"   ✅ Statistics calculated: {len(stats)} metrics")
                print(f"   ✅ Charts created: {len(charts)} visualizations")
                
                if events:
                    print("\n   Sample Event:")
                    event = events[0]
                    print(f"      ID: {event.get('id')}")
                    print(f"      Type: {event.get('event_type')}")
                    print(f"      Severity: {event.get('severity')}")
                    print(f"      Source IP: {event.get('source_ip')}")
                    
                self.passed += 1
            else:
                print("   ❌ Demo data generation failed")
                self.failed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.failed += 1
            
    def print_results(self):
        """Print test results"""
        print("\n" + "="*70)
        print("📊 TEST RESULTS")
        print("="*70)
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"   📈 Success Rate: {success_rate:.1f}%")
            
            if success_rate == 100:
                print("\n🎉 ALL TESTS PASSED! Your system is ready!")
            elif success_rate >= 80:
                print("\n✨ System is mostly working. Check failed tests.")
            else:
                print("\n⚠️ System needs attention. Review the errors above.")
        
        print("\n" + "="*70)
        
    def run_tests(self):
        """Run all tests"""
        self.print_header()
        
        # Check if backend is running
        backend_ok = self.test_backend_health()
        
        if backend_ok:
            # Run API tests
            self.test_api_endpoints()
            self.test_query_endpoint()
            self.test_demo_data()
        else:
            print("\n⚠️ Skipping API tests since backend is not running")
            
        # Check frontend files
        self.test_frontend_files()
        
        # Print results
        self.print_results()
        
        # Instructions
        print("\n📝 NEXT STEPS:")
        if not backend_ok:
            print("\n1. Start the backend:")
            print("   cd backend")
            print("   pip install fastapi uvicorn")
            print("   python -m uvicorn app.main:app --port 8001")
            
        print("\n2. Start the frontend:")
        print("   cd frontend")
        print("   npm install")
        print("   npm run dev")
        
        print("\n3. Open in browser:")
        print("   Frontend: http://localhost:5173")
        print("   API Docs: http://localhost:8001/docs")
        
        print("\nOr use the one-click launcher:")
        print("   python START_DEMO.py")

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_tests()
