#!/usr/bin/env python3
"""
Quick Backend Integration Test
Focused on core API functionality with faster execution.
"""

import asyncio
import requests
import time
import json
from datetime import datetime
from typing import Dict, Any, List

def test_server_running(base_url: str = "http://localhost:8001") -> bool:
    """Test if server is running"""
    try:
        response = requests.get(f"{base_url}/ping", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_endpoint_test(base_url: str, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
    """Run a single endpoint test"""
    start_time = time.time()
    
    try:
        url = f"{base_url}{endpoint}"
        response = requests.request(method, url, timeout=30, **kwargs)
        execution_time = time.time() - start_time
        
        try:
            response_data = response.json()
        except:
            response_data = {"raw_response": response.text[:200]}
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300,
            "execution_time": execution_time,
            "response_data": response_data,
            "error": None if 200 <= response.status_code < 300 else f"HTTP {response.status_code}"
        }
    
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": 0,
            "success": False,
            "execution_time": execution_time,
            "response_data": None,
            "error": str(e)
        }

def test_basic_endpoints(base_url: str) -> List[Dict[str, Any]]:
    """Test basic endpoints"""
    print("🧪 Testing Basic Endpoints...")
    
    endpoints = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/ping", "GET"),
        ("/api/docs", "GET"),
    ]
    
    results = []
    for endpoint, method in endpoints:
        result = run_endpoint_test(base_url, endpoint, method)
        results.append(result)
        
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {method} {endpoint} - {result['status_code']} ({result['execution_time']:.3f}s)")
        
        if result["error"]:
            print(f"    Error: {result['error']}")
    
    return results

def test_platform_events(base_url: str) -> List[Dict[str, Any]]:
    """Test platform-aware event endpoints"""
    print("\n🎯 Testing Platform Events...")
    
    results = []
    
    # Test capabilities
    result = run_endpoint_test(base_url, "/api/events/capabilities", "GET")
    results.append(result)
    status = "✅" if result["success"] else "❌"
    print(f"  {status} GET /api/events/capabilities - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    # Test core event endpoints
    event_endpoints = [
        "authentication", 
        "failed-logins",
        "successful-logins",
        "search"
    ]
    
    for endpoint in event_endpoints:
        # Test GET with basic params
        result = run_endpoint_test(
            base_url, 
            f"/api/events/{endpoint}",
            "GET",
            params={"query": "test", "limit": 5}
        )
        results.append(result)
        
        status = "✅" if result["success"] else "❌"
        print(f"  {status} GET /api/events/{endpoint} - {result['status_code']} ({result['execution_time']:.3f}s)")
        
        # Test POST
        result = run_endpoint_test(
            base_url,
            f"/api/events/{endpoint}",
            "POST", 
            json={"query": "test query", "time_range": "1h", "limit": 5}
        )
        results.append(result)
        
        status = "✅" if result["success"] else "❌"
        print(f"  {status} POST /api/events/{endpoint} - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    return results

def test_auth_endpoints(base_url: str) -> List[Dict[str, Any]]:
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication...")
    
    results = []
    
    # Test login
    login_data = {"identifier": "admin@kartavya.demo", "password": "admin123"}
    result = run_endpoint_test(base_url, "/api/auth/login", "POST", json=login_data)
    results.append(result)
    
    status = "✅" if result["success"] else "❌"
    print(f"  {status} POST /api/auth/login - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    # Extract token if successful
    token = None
    if result["success"] and result["response_data"]:
        token = result["response_data"].get("token")
        if token:
            print("    📝 Token acquired for subsequent tests")
    
    # Test profile with token
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        result = run_endpoint_test(base_url, "/api/auth/profile", "GET", headers=headers)
        results.append(result)
        
        status = "✅" if result["success"] else "❌"
        print(f"  {status} GET /api/auth/profile - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    return results

def test_query_endpoints(base_url: str) -> List[Dict[str, Any]]:
    """Test legacy query endpoints"""
    print("\n🔄 Testing Query Endpoints...")
    
    results = []
    
    # Test query suggestions
    result = run_endpoint_test(base_url, "/api/query/suggestions", "GET")
    results.append(result)
    
    status = "✅" if result["success"] else "❌"
    print(f"  {status} GET /api/query/suggestions - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    # Test query execution
    query_data = {"query": "show recent security events", "params": {"size": 5}}
    result = run_endpoint_test(base_url, "/api/query/execute", "POST", json=query_data)
    results.append(result)
    
    status = "✅" if result["success"] else "❌"
    print(f"  {status} POST /api/query/execute - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    # Test query translation
    result = run_endpoint_test(base_url, "/api/query/translate", "POST", json=query_data)
    results.append(result)
    
    status = "✅" if result["success"] else "❌"
    print(f"  {status} POST /api/query/translate - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    return results

def test_assistant_endpoints(base_url: str) -> List[Dict[str, Any]]:
    """Test AI assistant endpoints"""
    print("\n🤖 Testing Assistant...")
    
    results = []
    
    # Test chat
    chat_data = {"message": "Show me recent security alerts"}
    result = run_endpoint_test(base_url, "/api/assistant/chat", "POST", json=chat_data)
    results.append(result)
    
    status = "✅" if result["success"] else "❌"
    print(f"  {status} POST /api/assistant/chat - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    # Test context
    result = run_endpoint_test(base_url, "/api/assistant/context", "GET")
    results.append(result)
    
    status = "✅" if result["success"] else "❌"  
    print(f"  {status} GET /api/assistant/context - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    return results

def test_dashboard_endpoints(base_url: str) -> List[Dict[str, Any]]:
    """Test dashboard endpoints"""
    print("\n📊 Testing Dashboard...")
    
    results = []
    
    endpoints = [
        "/api/dashboard/overview",
        "/api/dashboard/metrics", 
        "/api/dashboard/alerts",
        "/api/dashboard/system-status"
    ]
    
    for endpoint in endpoints:
        result = run_endpoint_test(base_url, endpoint, "GET")
        results.append(result)
        
        status = "✅" if result["success"] else "❌"
        print(f"  {status} GET {endpoint} - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    return results

def test_error_handling(base_url: str) -> List[Dict[str, Any]]:
    """Test error scenarios"""
    print("\n💥 Testing Error Handling...")
    
    results = []
    
    # Test invalid endpoints
    invalid_endpoints = [
        "/api/nonexistent",
        "/api/events/invalid-type", 
        "/api/invalid/endpoint"
    ]
    
    for endpoint in invalid_endpoints:
        result = run_endpoint_test(base_url, endpoint, "GET")
        results.append(result)
        
        # For error tests, 404 is the expected "success" 
        expected_success = result["status_code"] == 404
        status = "✅" if expected_success else "❌"
        print(f"  {status} GET {endpoint} - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    # Test invalid login
    result = run_endpoint_test(base_url, "/api/auth/login", "POST", json={"invalid": "data"})
    results.append(result)
    
    # Expect 4xx error for invalid data
    expected_success = 400 <= result["status_code"] < 500
    status = "✅" if expected_success else "❌"
    print(f"  {status} POST /api/auth/login (invalid) - {result['status_code']} ({result['execution_time']:.3f}s)")
    
    return results

def generate_quick_report(all_results: List[Dict[str, Any]]) -> bool:
    """Generate quick test report"""
    print("\n" + "="*70)
    print("🧪 KARTAVYA BACKEND QUICK INTEGRATION TEST REPORT")
    print("="*70)
    
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r["success"])
    failed_tests = total_tests - successful_tests
    
    avg_response_time = sum(r["execution_time"] for r in all_results) / total_tests if total_tests > 0 else 0
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {successful_tests} ✅")
    print(f"   Failed: {failed_tests} ❌")  
    print(f"   Success Rate: {(successful_tests/total_tests*100):.1f}%")
    print(f"   Avg Response Time: {avg_response_time:.3f}s")
    
    # Show failures
    if failed_tests > 0:
        print(f"\n❌ FAILED TESTS:")
        for result in all_results:
            if not result["success"]:
                print(f"   • {result['method']} {result['endpoint']} - {result['error']}")
    
    # Critical endpoints check
    print(f"\n🎯 CRITICAL ENDPOINTS:")
    critical_endpoints = [
        "/health",
        "/api/events/capabilities",
        "/api/events/authentication", 
        "/api/auth/login"
    ]
    
    for endpoint in critical_endpoints:
        endpoint_results = [r for r in all_results if endpoint in r["endpoint"]]
        if endpoint_results:
            success_count = sum(1 for r in endpoint_results if r["success"])
            total_count = len(endpoint_results)
            success_rate = success_count / total_count * 100
            
            status = "✅" if success_rate >= 80 else "❌"
            print(f"   {status} {endpoint}: {success_rate:.1f}% ({success_count}/{total_count})")
        else:
            print(f"   ❓ {endpoint}: Not tested")
    
    # Performance check
    print(f"\n⚡ PERFORMANCE:")
    fast_responses = sum(1 for r in all_results if r["execution_time"] < 1.0)
    slow_responses = sum(1 for r in all_results if r["execution_time"] >= 3.0)
    
    print(f"   Fast responses (<1s): {fast_responses}/{total_tests} ({fast_responses/total_tests*100:.1f}%)")
    if slow_responses > 0:
        print(f"   Slow responses (≥3s): {slow_responses}/{total_tests} ({slow_responses/total_tests*100:.1f}%)")
    
    # Save results
    report = {
        "test_time": datetime.now().isoformat(),
        "total_tests": total_tests,
        "successful": successful_tests, 
        "failed": failed_tests,
        "success_rate": f"{(successful_tests/total_tests*100):.1f}%",
        "avg_response_time": f"{avg_response_time:.3f}s",
        "results": all_results
    }
    
    try:
        with open("quick_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: quick_test_report.json")
    except Exception as e:
        print(f"\n⚠️ Could not save report: {e}")
    
    print("="*70)
    
    return successful_tests == total_tests or (successful_tests/total_tests) >= 0.8

def main():
    """Run quick backend tests"""
    print("🚀 Kartavya Backend Quick Integration Tests")
    print("="*50)
    
    base_url = "http://localhost:8001"
    
    # Check if server is running
    if not test_server_running(base_url):
        print(f"❌ Server not running at {base_url}")
        print("Please start the server first:")
        print("python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8001")
        return 1
    
    print(f"✅ Server is running at {base_url}")
    
    # Run all tests
    all_results = []
    
    test_functions = [
        test_basic_endpoints,
        test_platform_events,
        test_auth_endpoints,
        test_query_endpoints,
        test_assistant_endpoints,
        test_dashboard_endpoints,
        test_error_handling
    ]
    
    for test_func in test_functions:
        try:
            results = test_func(base_url)
            all_results.extend(results)
        except Exception as e:
            print(f"❌ Test function {test_func.__name__} failed: {e}")
    
    # Generate report
    success = generate_quick_report(all_results)
    
    if success:
        print("\n🎉 QUICK TESTS PASSED! Backend core functionality is working!")
    else:
        print("\n⚠️ Some tests failed. Check the report for details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
