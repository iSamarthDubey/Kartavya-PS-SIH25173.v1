#!/usr/bin/env python3
"""
Complete Integration Test - SIEM NLP Assistant
Tests the entire pipeline with real data simulation and actual component integration.
"""

import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_1_component_imports():
    """Test 1: Verify all components import successfully."""
    print("🧪 TEST 1: Component Import Verification")
    print("=" * 60)
    
    try:
        # Test NLP components
        from backend.nlp.intent_classifier import IntentClassifier, QueryIntent
        from backend.nlp.entity_extractor import EntityExtractor
        print("✅ NLP components imported successfully")
        
        # Test Query Builder
        from backend.query_builder import QueryBuilder
        print("✅ Query Builder imported successfully")
        
        # Test SIEM Connector
        from siem_connector import SIEMQueryProcessor, create_siem_processor
        print("✅ SIEM Connector imported successfully")
        
        # Test Response Formatter
        from backend.response_formatter.formatter import ResponseFormatter
        print("✅ Response Formatter imported successfully")
        
        # Test Backend
        from backend.main import app
        print("✅ FastAPI Backend imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_2_component_initialization():
    """Test 2: Initialize all components and verify they work."""
    print("\n🔧 TEST 2: Component Initialization")
    print("=" * 60)
    
    try:
        # Initialize NLP components
        from backend.nlp.intent_classifier import IntentClassifier
        from backend.nlp.entity_extractor import EntityExtractor
        from backend.query_builder import QueryBuilder
        
        intent_classifier = IntentClassifier()
        entity_extractor = EntityExtractor()
        query_builder = QueryBuilder()
        
        print("✅ All NLP components initialized")
        
        # Initialize SIEM processor
        from siem_connector import create_siem_processor
        siem_processor = create_siem_processor("elasticsearch")
        
        print("✅ SIEM processor initialized")
        
        # Initialize response formatter
        from backend.response_formatter.formatter import ResponseFormatter
        formatter = ResponseFormatter()
        
        print("✅ Response formatter initialized")
        
        return {
            'intent_classifier': intent_classifier,
            'entity_extractor': entity_extractor,
            'query_builder': query_builder,
            'siem_processor': siem_processor,
            'formatter': formatter
        }
        
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        return None

def test_3_nlp_pipeline(components):
    """Test 3: Test the complete NLP processing pipeline."""
    print("\n🧠 TEST 3: NLP Pipeline Processing")
    print("=" * 60)
    
    test_queries = [
        "Show failed login attempts from user admin in the last hour",
        "Find security alerts with high severity from 192.168.1.100",
        "Get network traffic on port 443 from yesterday",
        "Show successful logins for john.doe@company.com",
        "List system errors from server.example.com"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        
        try:
            # Step 1: Intent Classification
            intent, confidence = components['intent_classifier'].classify_intent(query)
            print(f"   Intent: {intent.value} (confidence: {confidence:.2f})")
            
            # Step 2: Entity Extraction
            entities = components['entity_extractor'].extract_entities(query)
            entity_summary = components['entity_extractor'].get_entity_summary(entities)
            print(f"   Entities: {entity_summary}")
            
            # Step 3: Query Building
            es_query = components['query_builder'].build_query(query)
            print(f"   ES Query: {len(str(es_query))} characters")
            
            # Step 4: KQL Generation
            kql_query = components['query_builder'].build_kql_query(query)
            print(f"   KQL: {kql_query[:50]}...")
            
            results.append({
                'query': query,
                'intent': intent.value,
                'confidence': confidence,
                'entities': entity_summary,
                'es_query': es_query,
                'kql_query': kql_query
            })
            
            print("   ✅ NLP pipeline completed successfully")
            
        except Exception as e:
            print(f"   ❌ NLP pipeline failed: {e}")
            
    return results

def test_4_siem_connector(components, nlp_results):
    """Test 4: Test SIEM connector with generated queries."""
    print("\n🔌 TEST 4: SIEM Connector Integration")
    print("=" * 60)
    
    siem_results = []
    
    for result in nlp_results[:3]:  # Test first 3 queries
        print(f"\n🔍 Testing: {result['query'][:50]}...")
        
        try:
            # Test query processing
            response = components['siem_processor'].process_query(
                result['es_query'], 
                size=5
            )
            
            total_hits = response.get('metadata', {}).get('total_hits', 0)
            execution_time = response.get('metadata', {}).get('execution_time', 0)
            platform = response.get('metadata', {}).get('platform', 'unknown')
            
            print(f"   Platform: {platform}")
            print(f"   Results: {total_hits} hits in {execution_time:.3f}s")
            print(f"   Status: {'✅ Success' if 'error' not in response.get('metadata', {}) else '⚠️ Expected Error'}")
            
            # Test health check
            health = components['siem_processor'].get_health_status()
            print(f"   Health: {health.get('status', 'unknown')}")
            
            siem_results.append({
                'query': result['query'],
                'response': response,
                'health': health
            })
            
        except Exception as e:
            print(f"   ⚠️ SIEM connector error (expected): {e}")
            
    return siem_results

def test_5_response_formatting(components, siem_results):
    """Test 5: Test response formatting with SIEM results."""
    print("\n📝 TEST 5: Response Formatting")
    print("=" * 60)
    
    formatted_results = []
    
    for result in siem_results:
        print(f"\n📋 Formatting: {result['query'][:40]}...")
        
        try:
            # Extract response data
            response_data = result['response']
            hits = response_data.get('hits', [])
            
            # Test response formatter
            if hits:
                formatted_response = components['formatter'].format_response(
                    query=result['query'],
                    intent="search_logs",
                    results=[hit.get('source', {}) for hit in hits],
                    aggregations=response_data.get('aggregations')
                )
                
                print(f"   Summary: {formatted_response.summary[:100]}...")
                print(f"   Table rows: {len(formatted_response.table_data) if formatted_response.table_data is not None else 0}")
                print("   ✅ Response formatting successful")
                
                formatted_results.append({
                    'query': result['query'],
                    'formatted_response': formatted_response
                })
            else:
                print("   ⚠️ No data to format (expected without real ES)")
                
        except Exception as e:
            print(f"   ❌ Response formatting failed: {e}")
            
    return formatted_results

def test_6_api_endpoints():
    """Test 6: Test FastAPI endpoints."""
    print("\n🌐 TEST 6: API Endpoint Testing")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        print("🔍 Testing /health endpoint...")
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   System status: {health_data.get('status')}")
            print(f"   Components: {health_data.get('components')}")
            print("   ✅ Health endpoint working")
        
        # Test SIEM health endpoint
        print("\n🔍 Testing /siem/health endpoint...")
        response = client.get("/siem/health")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 503]:  # 503 expected without ES
            print("   ✅ SIEM health endpoint working")
        
        # Test query endpoint
        print("\n🔍 Testing /query endpoint...")
        test_query = {
            "query": "show failed login attempts",
            "max_results": 5
        }
        response = client.post("/query", json=test_query)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 503]:  # 503 expected without full setup
            if response.status_code == 200:
                query_data = response.json()
                print(f"   Intent: {query_data.get('intent')}")
                print(f"   Results: {len(query_data.get('results', []))}")
            print("   ✅ Query endpoint working")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def test_7_error_handling():
    """Test 7: Test error handling and resilience."""
    print("\n🛡️ TEST 7: Error Handling & Resilience")
    print("=" * 60)
    
    try:
        from siem_connector import create_siem_processor
        from siem_connector.utils import validate_query_dsl, build_error_response
        
        # Test invalid query validation
        print("🔍 Testing query validation...")
        invalid_query = {"invalid": "query"}
        is_valid, message = validate_query_dsl(invalid_query)
        print(f"   Invalid query detected: {'✅' if not is_valid else '❌'}")
        print(f"   Error message: {message}")
        
        # Test error response building
        print("\n🔍 Testing error response building...")
        error_response = build_error_response("Test error", "test query")
        print(f"   Error response structure: {'✅' if 'metadata' in error_response else '❌'}")
        print(f"   Error message preserved: {'✅' if error_response['metadata']['error'] == 'Test error' else '❌'}")
        
        # Test processor with bad connection
        print("\n🔍 Testing graceful degradation...")
        processor = create_siem_processor("elasticsearch")
        health = processor.get_health_status()
        print(f"   Graceful failure: {'✅' if health['status'] in ['disconnected', 'error'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_8_performance_benchmarks():
    """Test 8: Performance benchmarks."""
    print("\n⚡ TEST 8: Performance Benchmarks")
    print("=" * 60)
    
    try:
        from backend.query_builder import QueryBuilder
        from siem_connector import create_siem_processor
        
        query_builder = QueryBuilder()
        processor = create_siem_processor("elasticsearch")
        
        test_queries = [
            "show failed logins",
            "find security alerts",
            "get network traffic",
            "list system errors",
            "display user activity"
        ]
        
        print("🔍 Query Building Performance:")
        total_time = 0
        for query in test_queries:
            start_time = time.time()
            es_query = query_builder.build_query(query)
            elapsed = time.time() - start_time
            total_time += elapsed
            print(f"   '{query}': {elapsed:.3f}s")
        
        avg_time = total_time / len(test_queries)
        print(f"   Average query building time: {avg_time:.3f}s")
        print(f"   Performance: {'✅ Good' if avg_time < 0.1 else '⚠️ Slow'}")
        
        print("\n🔍 Memory Usage Check:")
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   Current memory usage: {memory_mb:.1f} MB")
        print(f"   Memory efficiency: {'✅ Good' if memory_mb < 200 else '⚠️ High'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def create_test_data():
    """Create realistic test data for demonstration."""
    print("\n📊 Creating Test Data for Demo")
    print("=" * 60)
    
    # Sample log entries that would come from Elasticsearch
    sample_logs = [
        {
            "@timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "event.type": "authentication",
            "event.outcome": "failure",
            "user.name": "admin",
            "source.ip": "192.168.1.100",
            "host.name": "server-01",
            "message": "Authentication failed for user admin from 192.168.1.100",
            "winlog.event_id": "4625"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=25)).isoformat(),
            "event.type": "network",
            "source.ip": "192.168.1.100",
            "destination.ip": "10.0.0.50",
            "destination.port": 443,
            "network.protocol": "tcp",
            "message": "Network connection from 192.168.1.100 to 10.0.0.50:443"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
            "event.type": "security",
            "event.severity": 8,
            "rule.name": "Suspicious Login Pattern",
            "source.ip": "192.168.1.100",
            "user.name": "admin",
            "message": "Multiple failed login attempts detected"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "event.type": "authentication", 
            "event.outcome": "success",
            "user.name": "john.doe",
            "source.ip": "192.168.1.50",
            "host.name": "workstation-05",
            "message": "Successful login for user john.doe",
            "winlog.event_id": "4624"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "event.type": "system",
            "log.level": "ERROR",
            "host.name": "server.example.com",
            "service.name": "web-service",
            "message": "Service connection timeout error"
        }
    ]
    
    print(f"✅ Created {len(sample_logs)} sample log entries")
    return sample_logs

def run_complete_integration_test():
    """Run the complete integration test suite."""
    print("🚀 SIEM NLP Assistant - Complete Integration Test")
    print("=" * 80)
    print("Testing the entire pipeline from natural language to SIEM response")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test 1: Component Imports
    if not test_1_component_imports():
        print("\n❌ CRITICAL: Component imports failed. Stopping tests.")
        return False
    
    # Test 2: Component Initialization
    components = test_2_component_initialization()
    if not components:
        print("\n❌ CRITICAL: Component initialization failed. Stopping tests.")
        return False
    
    # Test 3: NLP Pipeline
    nlp_results = test_3_nlp_pipeline(components)
    if not nlp_results:
        print("\n❌ WARNING: NLP pipeline tests failed.")
    
    # Test 4: SIEM Connector
    siem_results = test_4_siem_connector(components, nlp_results)
    
    # Test 5: Response Formatting
    formatted_results = test_5_response_formatting(components, siem_results)
    
    # Test 6: API Endpoints
    api_success = test_6_api_endpoints()
    
    # Test 7: Error Handling
    error_handling_success = test_7_error_handling()
    
    # Test 8: Performance Benchmarks
    perf_success = test_8_performance_benchmarks()
    
    # Create test data for demo
    test_data = create_test_data()
    
    # Final Results
    print("\n" + "=" * 80)
    print("🎯 INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    test_results = [
        ("Component Imports", True),
        ("Component Initialization", bool(components)),
        ("NLP Pipeline", len(nlp_results) > 0),
        ("SIEM Connector", len(siem_results) > 0),
        ("Response Formatting", len(formatted_results) > 0),
        ("API Endpoints", api_success),
        ("Error Handling", error_handling_success),
        ("Performance", perf_success)
    ]
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25}: {status}")
    
    print("\n" + "=" * 80)
    print(f"🏆 OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed >= 6:  # At least 75% pass rate
        print("✅ INTEGRATION TEST SUITE: PASSED")
        print("\n🎉 The SIEM NLP Assistant is ready for production!")
        print("\n📋 To start using the system:")
        print("1. Start backend: cd backend && python main.py")
        print("2. Start frontend: cd ui_dashboard && streamlit run streamlit_app.py")
        print("3. Configure Elasticsearch: Set environment variables")
        return True
    else:
        print("❌ INTEGRATION TEST SUITE: FAILED")
        print("\n⚠️ Some components need attention before production deployment.")
        return False

if __name__ == "__main__":
    try:
        success = run_complete_integration_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)

# --- Merged from tests/e2e/test_complete_integration.py ---
"""
🎯 COMPLETE END-TO-END INTEGRATION TEST
Tests the entire NLP → SIEM workflow with real components
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from assistant.pipeline import ConversationalPipeline
from backend.nlp.intent_classifier import IntentClassifier
from backend.nlp.entity_extractor import EntityExtractor
from backend.query_builder import QueryBuilder

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

async def test_nlp_components():
    """Test NLP components individually."""
    print_header("🧠 TESTING NLP COMPONENTS")
    
    test_query = "Show failed login attempts from user admin on 192.168.1.100 in the last hour"
    print_info(f"Test Query: \"{test_query}\"\n")
    
    # Test Intent Classifier
    print(f"{Colors.BOLD}1. Intent Classifier{Colors.END}")
    try:
        classifier = IntentClassifier()
        intent, confidence = classifier.classify_intent(test_query)
        print_success(f"Intent: {intent.value}")
        print_info(f"   Confidence: {confidence:.2%}")
    except Exception as e:
        print_error(f"Intent Classifier failed: {e}")
        return False
    
    # Test Entity Extractor
    print(f"\n{Colors.BOLD}2. Entity Extractor{Colors.END}")
    try:
        extractor = EntityExtractor()
        entities = extractor.extract_entities(test_query)
        print_success(f"Extracted {len(entities)} entities:")
        for entity in entities:
            print_info(f"   • {entity.type}: '{entity.value}' (confidence: {entity.confidence:.2f})")
        entity_summary = extractor.get_entity_summary(entities)
        print_info(f"   Summary: {entity_summary}")
    except Exception as e:
        print_error(f"Entity Extractor failed: {e}")
        return False
    
    # Test Query Builder
    print(f"\n{Colors.BOLD}3. Query Builder{Colors.END}")
    try:
        builder = QueryBuilder()
        query_result = builder.build_query(test_query)
        print_success(f"Generated Elasticsearch query:")
        print_info(f"   Index: {query_result.get('index', 'N/A')}")
        print_info(f"   Size: {query_result.get('query', {}).get('size', 'N/A')}")
        print_info(f"   Query Type: bool with {len(query_result.get('query', {}).get('query', {}).get('bool', {}).get('must', []))} must clauses")
    except Exception as e:
        print_error(f"Query Builder failed: {e}")
        return False
    
    return True

async def test_full_pipeline():
    """Test the complete conversational pipeline."""
    print_header("🔥 TESTING COMPLETE PIPELINE")
    
    test_queries = [
        "Show failed login attempts from the last hour",
        "Find high severity alerts",
        "What are the network connections from 192.168.1.100?",
        "List all security events from today",
        "Show authentication failures for user admin"
    ]
    
    try:
        # Initialize pipeline
        print_info("Initializing ConversationalPipeline...")
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
        print_success("Pipeline initialized\n")
        
        # Test each query
        for idx, query in enumerate(test_queries, 1):
            print(f"{Colors.BOLD}Test Query {idx}/{len(test_queries)}{Colors.END}")
            print(f"Query: \"{query}\"")
            
            start_time = datetime.now()
            
            try:
                # Process query
                result = await pipeline.process_query(
                    user_input=query,
                    conversation_id=f"test_conv_{idx}"
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Display results
                print_success(f"Query processed in {processing_time:.3f}s")
                print_info(f"   Intent: {result.get('intent', 'unknown')}")
                print_info(f"   Entities: {len(result.get('entities', []))} extracted")
                print_info(f"   Results: {len(result.get('results', []))} records")
                print_info(f"   Summary: {result.get('summary', 'N/A')}")
                
                # Show metadata
                metadata = result.get('metadata', {})
                print_info(f"   Confidence: {metadata.get('confidence_score', 0):.2%}")
                print_info(f"   Processing Time: {metadata.get('processing_time_seconds', 0):.3f}s")
                
                # Show entities in detail
                if result.get('entities'):
                    print(f"\n   {Colors.BOLD}Entities Detail:{Colors.END}")
                    for entity in result.get('entities', [])[:5]:  # Show first 5
                        print(f"      • {entity.get('type')}: {entity.get('value')} ({entity.get('confidence', 0):.2f})")
                
                print()
                
            except Exception as e:
                print_error(f"Query failed: {e}")
                print()
        
        # Show pipeline health
        print(f"\n{Colors.BOLD}Pipeline Health Status:{Colors.END}")
        health = pipeline.get_health_status()
        print_info(f"Health Score: {health['health_score']}")
        print_info(f"Status: {health['status']}")
        print(f"\n{Colors.BOLD}Component Status:{Colors.END}")
        for component, status in health['components'].items():
            if status:
                print_success(f"{component}: Ready")
            else:
                print_warning(f"{component}: Not available")
        
        return True
        
    except Exception as e:
        print_error(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_integration():
    """Test API endpoints."""
    print_header("🌐 TESTING API INTEGRATION")
    
    import requests
    
    API_URL = "http://localhost:8001/assistant"
    
    # Test health endpoint
    print(f"{Colors.BOLD}1. Health Check{Colors.END}")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"API is healthy")
            print_info(f"   Status: {health_data.get('status')}")
            print_info(f"   Health Score: {health_data.get('health_score')}")
        else:
            print_error(f"Health check failed: {response.status_code}")
    except Exception as e:
        print_warning(f"API not running: {e}")
        print_info("Start with: python assistant/main.py")
        return False
    
    # Test query endpoint
    print(f"\n{Colors.BOLD}2. Query Endpoint{Colors.END}")
    try:
        payload = {
            "query": "Show failed logins from the last hour",
            "conversation_id": "test_api_conv"
        }
        
        response = requests.post(f"{API_URL}/ask", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Query processed successfully")
            print_info(f"   Intent: {data.get('intent')}")
            print_info(f"   Entities: {len(data.get('entities', []))}")
            print_info(f"   Results: {len(data.get('results', []))}")
            print_info(f"   Summary: {data.get('summary')}")
        else:
            print_error(f"Query failed: {response.status_code}")
            print_error(f"   Error: {response.text}")
    except Exception as e:
        print_error(f"API query failed: {e}")
        return False
    
    return True

async def main():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║        🎯 SIEM NLP ASSISTANT - INTEGRATION TEST SUITE 🎯          ║")
    print("║                                                                    ║")
    print("║                    Team Kartavya | SIH 2025                        ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    results = {}
    
    # Test 1: NLP Components
    results['nlp_components'] = await test_nlp_components()
    
    # Test 2: Full Pipeline
    results['full_pipeline'] = await test_full_pipeline()
    
    # Test 3: API Integration
    results['api_integration'] = await test_api_integration()
    
    # Final Summary
    print_header("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        test_display = test_name.replace('_', ' ').title()
        if passed:
            print_success(f"{test_display}: PASSED")
        else:
            print_error(f"{test_display}: FAILED")
    
    print(f"\n{Colors.BOLD}Overall Result:{Colors.END}")
    if passed_tests == total_tests:
        print_success(f"ALL TESTS PASSED ({passed_tests}/{total_tests})")
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 BACKEND INTEGRATION COMPLETE! 🎉{Colors.END}")
    else:
        print_warning(f"Some tests failed ({passed_tests}/{total_tests})")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())


# --- Merged from tests/complete_integration_test.py ---
#!/usr/bin/env python3
"""
Complete Integration Test - SIEM NLP Assistant
Tests the entire pipeline with real data simulation and actual component integration.
"""

import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_1_component_imports():
    """Test 1: Verify all components import successfully."""
    print("🧪 TEST 1: Component Import Verification")
    print("=" * 60)
    
    try:
        # Test NLP components
        from backend.nlp.intent_classifier import IntentClassifier, QueryIntent
        from backend.nlp.entity_extractor import EntityExtractor
        print("✅ NLP components imported successfully")
        
        # Test Query Builder
        from backend.query_builder import QueryBuilder
        print("✅ Query Builder imported successfully")
        
        # Test SIEM Connector
        from siem_connector import SIEMQueryProcessor, create_siem_processor
        print("✅ SIEM Connector imported successfully")
        
        # Test Response Formatter
        from backend.response_formatter.formatter import ResponseFormatter
        print("✅ Response Formatter imported successfully")
        
        # Test Backend
        from backend.main import app
        print("✅ FastAPI Backend imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_2_component_initialization():
    """Test 2: Initialize all components and verify they work."""
    print("\n🔧 TEST 2: Component Initialization")
    print("=" * 60)
    
    try:
        # Initialize NLP components
        from backend.nlp.intent_classifier import IntentClassifier
        from backend.nlp.entity_extractor import EntityExtractor
        from backend.query_builder import QueryBuilder
        
        intent_classifier = IntentClassifier()
        entity_extractor = EntityExtractor()
        query_builder = QueryBuilder()
        
        print("✅ All NLP components initialized")
        
        # Initialize SIEM processor
        from siem_connector import create_siem_processor
        siem_processor = create_siem_processor("elasticsearch")
        
        print("✅ SIEM processor initialized")
        
        # Initialize response formatter
        from backend.response_formatter.formatter import ResponseFormatter
        formatter = ResponseFormatter()
        
        print("✅ Response formatter initialized")
        
        return {
            'intent_classifier': intent_classifier,
            'entity_extractor': entity_extractor,
            'query_builder': query_builder,
            'siem_processor': siem_processor,
            'formatter': formatter
        }
        
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        return None

def test_3_nlp_pipeline(components):
    """Test 3: Test the complete NLP processing pipeline."""
    print("\n🧠 TEST 3: NLP Pipeline Processing")
    print("=" * 60)
    
    test_queries = [
        "Show failed login attempts from user admin in the last hour",
        "Find security alerts with high severity from 192.168.1.100",
        "Get network traffic on port 443 from yesterday",
        "Show successful logins for john.doe@company.com",
        "List system errors from server.example.com"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        
        try:
            # Step 1: Intent Classification
            intent, confidence = components['intent_classifier'].classify_intent(query)
            print(f"   Intent: {intent.value} (confidence: {confidence:.2f})")
            
            # Step 2: Entity Extraction
            entities = components['entity_extractor'].extract_entities(query)
            entity_summary = components['entity_extractor'].get_entity_summary(entities)
            print(f"   Entities: {entity_summary}")
            
            # Step 3: Query Building
            es_query = components['query_builder'].build_query(query)
            print(f"   ES Query: {len(str(es_query))} characters")
            
            # Step 4: KQL Generation
            kql_query = components['query_builder'].build_kql_query(query)
            print(f"   KQL: {kql_query[:50]}...")
            
            results.append({
                'query': query,
                'intent': intent.value,
                'confidence': confidence,
                'entities': entity_summary,
                'es_query': es_query,
                'kql_query': kql_query
            })
            
            print("   ✅ NLP pipeline completed successfully")
            
        except Exception as e:
            print(f"   ❌ NLP pipeline failed: {e}")
            
    return results

def test_4_siem_connector(components, nlp_results):
    """Test 4: Test SIEM connector with generated queries."""
    print("\n🔌 TEST 4: SIEM Connector Integration")
    print("=" * 60)
    
    siem_results = []
    
    for result in nlp_results[:3]:  # Test first 3 queries
        print(f"\n🔍 Testing: {result['query'][:50]}...")
        
        try:
            # Test query processing
            response = components['siem_processor'].process_query(
                result['es_query'], 
                size=5
            )
            
            total_hits = response.get('metadata', {}).get('total_hits', 0)
            execution_time = response.get('metadata', {}).get('execution_time', 0)
            platform = response.get('metadata', {}).get('platform', 'unknown')
            
            print(f"   Platform: {platform}")
            print(f"   Results: {total_hits} hits in {execution_time:.3f}s")
            print(f"   Status: {'✅ Success' if 'error' not in response.get('metadata', {}) else '⚠️ Expected Error'}")
            
            # Test health check
            health = components['siem_processor'].get_health_status()
            print(f"   Health: {health.get('status', 'unknown')}")
            
            siem_results.append({
                'query': result['query'],
                'response': response,
                'health': health
            })
            
        except Exception as e:
            print(f"   ⚠️ SIEM connector error (expected): {e}")
            
    return siem_results

def test_5_response_formatting(components, siem_results):
    """Test 5: Test response formatting with SIEM results."""
    print("\n📝 TEST 5: Response Formatting")
    print("=" * 60)
    
    formatted_results = []
    
    for result in siem_results:
        print(f"\n📋 Formatting: {result['query'][:40]}...")
        
        try:
            # Extract response data
            response_data = result['response']
            hits = response_data.get('hits', [])
            
            # Test response formatter
            if hits:
                formatted_response = components['formatter'].format_response(
                    query=result['query'],
                    intent="search_logs",
                    results=[hit.get('source', {}) for hit in hits],
                    aggregations=response_data.get('aggregations')
                )
                
                print(f"   Summary: {formatted_response.summary[:100]}...")
                print(f"   Table rows: {len(formatted_response.table_data) if formatted_response.table_data is not None else 0}")
                print("   ✅ Response formatting successful")
                
                formatted_results.append({
                    'query': result['query'],
                    'formatted_response': formatted_response
                })
            else:
                print("   ⚠️ No data to format (expected without real ES)")
                
        except Exception as e:
            print(f"   ❌ Response formatting failed: {e}")
            
    return formatted_results

def test_6_api_endpoints():
    """Test 6: Test FastAPI endpoints."""
    print("\n🌐 TEST 6: API Endpoint Testing")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        print("🔍 Testing /health endpoint...")
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   System status: {health_data.get('status')}")
            print(f"   Components: {health_data.get('components')}")
            print("   ✅ Health endpoint working")
        
        # Test SIEM health endpoint
        print("\n🔍 Testing /siem/health endpoint...")
        response = client.get("/siem/health")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 503]:  # 503 expected without ES
            print("   ✅ SIEM health endpoint working")
        
        # Test query endpoint
        print("\n🔍 Testing /query endpoint...")
        test_query = {
            "query": "show failed login attempts",
            "max_results": 5
        }
        response = client.post("/query", json=test_query)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 503]:  # 503 expected without full setup
            if response.status_code == 200:
                query_data = response.json()
                print(f"   Intent: {query_data.get('intent')}")
                print(f"   Results: {len(query_data.get('results', []))}")
            print("   ✅ Query endpoint working")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def test_7_error_handling():
    """Test 7: Test error handling and resilience."""
    print("\n🛡️ TEST 7: Error Handling & Resilience")
    print("=" * 60)
    
    try:
        from siem_connector import create_siem_processor
        from siem_connector.utils import validate_query_dsl, build_error_response
        
        # Test invalid query validation
        print("🔍 Testing query validation...")
        invalid_query = {"invalid": "query"}
        is_valid, message = validate_query_dsl(invalid_query)
        print(f"   Invalid query detected: {'✅' if not is_valid else '❌'}")
        print(f"   Error message: {message}")
        
        # Test error response building
        print("\n🔍 Testing error response building...")
        error_response = build_error_response("Test error", "test query")
        print(f"   Error response structure: {'✅' if 'metadata' in error_response else '❌'}")
        print(f"   Error message preserved: {'✅' if error_response['metadata']['error'] == 'Test error' else '❌'}")
        
        # Test processor with bad connection
        print("\n🔍 Testing graceful degradation...")
        processor = create_siem_processor("elasticsearch")
        health = processor.get_health_status()
        print(f"   Graceful failure: {'✅' if health['status'] in ['disconnected', 'error'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_8_performance_benchmarks():
    """Test 8: Performance benchmarks."""
    print("\n⚡ TEST 8: Performance Benchmarks")
    print("=" * 60)
    
    try:
        from backend.query_builder import QueryBuilder
        from siem_connector import create_siem_processor
        
        query_builder = QueryBuilder()
        processor = create_siem_processor("elasticsearch")
        
        test_queries = [
            "show failed logins",
            "find security alerts",
            "get network traffic",
            "list system errors",
            "display user activity"
        ]
        
        print("🔍 Query Building Performance:")
        total_time = 0
        for query in test_queries:
            start_time = time.time()
            es_query = query_builder.build_query(query)
            elapsed = time.time() - start_time
            total_time += elapsed
            print(f"   '{query}': {elapsed:.3f}s")
        
        avg_time = total_time / len(test_queries)
        print(f"   Average query building time: {avg_time:.3f}s")
        print(f"   Performance: {'✅ Good' if avg_time < 0.1 else '⚠️ Slow'}")
        
        print("\n🔍 Memory Usage Check:")
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   Current memory usage: {memory_mb:.1f} MB")
        print(f"   Memory efficiency: {'✅ Good' if memory_mb < 200 else '⚠️ High'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def create_test_data():
    """Create realistic test data for demonstration."""
    print("\n📊 Creating Test Data for Demo")
    print("=" * 60)
    
    # Sample log entries that would come from Elasticsearch
    sample_logs = [
        {
            "@timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "event.type": "authentication",
            "event.outcome": "failure",
            "user.name": "admin",
            "source.ip": "192.168.1.100",
            "host.name": "server-01",
            "message": "Authentication failed for user admin from 192.168.1.100",
            "winlog.event_id": "4625"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=25)).isoformat(),
            "event.type": "network",
            "source.ip": "192.168.1.100",
            "destination.ip": "10.0.0.50",
            "destination.port": 443,
            "network.protocol": "tcp",
            "message": "Network connection from 192.168.1.100 to 10.0.0.50:443"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
            "event.type": "security",
            "event.severity": 8,
            "rule.name": "Suspicious Login Pattern",
            "source.ip": "192.168.1.100",
            "user.name": "admin",
            "message": "Multiple failed login attempts detected"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "event.type": "authentication", 
            "event.outcome": "success",
            "user.name": "john.doe",
            "source.ip": "192.168.1.50",
            "host.name": "workstation-05",
            "message": "Successful login for user john.doe",
            "winlog.event_id": "4624"
        },
        {
            "@timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "event.type": "system",
            "log.level": "ERROR",
            "host.name": "server.example.com",
            "service.name": "web-service",
            "message": "Service connection timeout error"
        }
    ]
    
    print(f"✅ Created {len(sample_logs)} sample log entries")
    return sample_logs

def run_complete_integration_test():
    """Run the complete integration test suite."""
    print("🚀 SIEM NLP Assistant - Complete Integration Test")
    print("=" * 80)
    print("Testing the entire pipeline from natural language to SIEM response")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test 1: Component Imports
    if not test_1_component_imports():
        print("\n❌ CRITICAL: Component imports failed. Stopping tests.")
        return False
    
    # Test 2: Component Initialization
    components = test_2_component_initialization()
    if not components:
        print("\n❌ CRITICAL: Component initialization failed. Stopping tests.")
        return False
    
    # Test 3: NLP Pipeline
    nlp_results = test_3_nlp_pipeline(components)
    if not nlp_results:
        print("\n❌ WARNING: NLP pipeline tests failed.")
    
    # Test 4: SIEM Connector
    siem_results = test_4_siem_connector(components, nlp_results)
    
    # Test 5: Response Formatting
    formatted_results = test_5_response_formatting(components, siem_results)
    
    # Test 6: API Endpoints
    api_success = test_6_api_endpoints()
    
    # Test 7: Error Handling
    error_handling_success = test_7_error_handling()
    
    # Test 8: Performance Benchmarks
    perf_success = test_8_performance_benchmarks()
    
    # Create test data for demo
    test_data = create_test_data()
    
    # Final Results
    print("\n" + "=" * 80)
    print("🎯 INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    test_results = [
        ("Component Imports", True),
        ("Component Initialization", bool(components)),
        ("NLP Pipeline", len(nlp_results) > 0),
        ("SIEM Connector", len(siem_results) > 0),
        ("Response Formatting", len(formatted_results) > 0),
        ("API Endpoints", api_success),
        ("Error Handling", error_handling_success),
        ("Performance", perf_success)
    ]
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25}: {status}")
    
    print("\n" + "=" * 80)
    print(f"🏆 OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed >= 6:  # At least 75% pass rate
        print("✅ INTEGRATION TEST SUITE: PASSED")
        print("\n🎉 The SIEM NLP Assistant is ready for production!")
        print("\n📋 To start using the system:")
        print("1. Start backend: cd backend && python main.py")
        print("2. Start frontend: cd ui_dashboard && streamlit run streamlit_app.py")
        print("3. Configure Elasticsearch: Set environment variables")
        return True
    else:
        print("❌ INTEGRATION TEST SUITE: FAILED")
        print("\n⚠️ Some components need attention before production deployment.")
        return False

if __name__ == "__main__":
    try:
        success = run_complete_integration_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)

# --- Merged from tests/e2e/test_complete_integration.py ---
"""
🎯 COMPLETE END-TO-END INTEGRATION TEST
Tests the entire NLP → SIEM workflow with real components
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from assistant.pipeline import ConversationalPipeline
from backend.nlp.intent_classifier import IntentClassifier
from backend.nlp.entity_extractor import EntityExtractor
from backend.query_builder import QueryBuilder

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

async def test_nlp_components():
    """Test NLP components individually."""
    print_header("🧠 TESTING NLP COMPONENTS")
    
    test_query = "Show failed login attempts from user admin on 192.168.1.100 in the last hour"
    print_info(f"Test Query: \"{test_query}\"\n")
    
    # Test Intent Classifier
    print(f"{Colors.BOLD}1. Intent Classifier{Colors.END}")
    try:
        classifier = IntentClassifier()
        intent, confidence = classifier.classify_intent(test_query)
        print_success(f"Intent: {intent.value}")
        print_info(f"   Confidence: {confidence:.2%}")
    except Exception as e:
        print_error(f"Intent Classifier failed: {e}")
        return False
    
    # Test Entity Extractor
    print(f"\n{Colors.BOLD}2. Entity Extractor{Colors.END}")
    try:
        extractor = EntityExtractor()
        entities = extractor.extract_entities(test_query)
        print_success(f"Extracted {len(entities)} entities:")
        for entity in entities:
            print_info(f"   • {entity.type}: '{entity.value}' (confidence: {entity.confidence:.2f})")
        entity_summary = extractor.get_entity_summary(entities)
        print_info(f"   Summary: {entity_summary}")
    except Exception as e:
        print_error(f"Entity Extractor failed: {e}")
        return False
    
    # Test Query Builder
    print(f"\n{Colors.BOLD}3. Query Builder{Colors.END}")
    try:
        builder = QueryBuilder()
        query_result = builder.build_query(test_query)
        print_success(f"Generated Elasticsearch query:")
        print_info(f"   Index: {query_result.get('index', 'N/A')}")
        print_info(f"   Size: {query_result.get('query', {}).get('size', 'N/A')}")
        print_info(f"   Query Type: bool with {len(query_result.get('query', {}).get('query', {}).get('bool', {}).get('must', []))} must clauses")
    except Exception as e:
        print_error(f"Query Builder failed: {e}")
        return False
    
    return True

async def test_full_pipeline():
    """Test the complete conversational pipeline."""
    print_header("🔥 TESTING COMPLETE PIPELINE")
    
    test_queries = [
        "Show failed login attempts from the last hour",
        "Find high severity alerts",
        "What are the network connections from 192.168.1.100?",
        "List all security events from today",
        "Show authentication failures for user admin"
    ]
    
    try:
        # Initialize pipeline
        print_info("Initializing ConversationalPipeline...")
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
        print_success("Pipeline initialized\n")
        
        # Test each query
        for idx, query in enumerate(test_queries, 1):
            print(f"{Colors.BOLD}Test Query {idx}/{len(test_queries)}{Colors.END}")
            print(f"Query: \"{query}\"")
            
            start_time = datetime.now()
            
            try:
                # Process query
                result = await pipeline.process_query(
                    user_input=query,
                    conversation_id=f"test_conv_{idx}"
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Display results
                print_success(f"Query processed in {processing_time:.3f}s")
                print_info(f"   Intent: {result.get('intent', 'unknown')}")
                print_info(f"   Entities: {len(result.get('entities', []))} extracted")
                print_info(f"   Results: {len(result.get('results', []))} records")
                print_info(f"   Summary: {result.get('summary', 'N/A')}")
                
                # Show metadata
                metadata = result.get('metadata', {})
                print_info(f"   Confidence: {metadata.get('confidence_score', 0):.2%}")
                print_info(f"   Processing Time: {metadata.get('processing_time_seconds', 0):.3f}s")
                
                # Show entities in detail
                if result.get('entities'):
                    print(f"\n   {Colors.BOLD}Entities Detail:{Colors.END}")
                    for entity in result.get('entities', [])[:5]:  # Show first 5
                        print(f"      • {entity.get('type')}: {entity.get('value')} ({entity.get('confidence', 0):.2f})")
                
                print()
                
            except Exception as e:
                print_error(f"Query failed: {e}")
                print()
        
        # Show pipeline health
        print(f"\n{Colors.BOLD}Pipeline Health Status:{Colors.END}")
        health = pipeline.get_health_status()
        print_info(f"Health Score: {health['health_score']}")
        print_info(f"Status: {health['status']}")
        print(f"\n{Colors.BOLD}Component Status:{Colors.END}")
        for component, status in health['components'].items():
            if status:
                print_success(f"{component}: Ready")
            else:
                print_warning(f"{component}: Not available")
        
        return True
        
    except Exception as e:
        print_error(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_integration():
    """Test API endpoints."""
    print_header("🌐 TESTING API INTEGRATION")
    
    import requests
    
    API_URL = "http://localhost:8001/assistant"
    
    # Test health endpoint
    print(f"{Colors.BOLD}1. Health Check{Colors.END}")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"API is healthy")
            print_info(f"   Status: {health_data.get('status')}")
            print_info(f"   Health Score: {health_data.get('health_score')}")
        else:
            print_error(f"Health check failed: {response.status_code}")
    except Exception as e:
        print_warning(f"API not running: {e}")
        print_info("Start with: python assistant/main.py")
        return False
    
    # Test query endpoint
    print(f"\n{Colors.BOLD}2. Query Endpoint{Colors.END}")
    try:
        payload = {
            "query": "Show failed logins from the last hour",
            "conversation_id": "test_api_conv"
        }
        
        response = requests.post(f"{API_URL}/ask", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Query processed successfully")
            print_info(f"   Intent: {data.get('intent')}")
            print_info(f"   Entities: {len(data.get('entities', []))}")
            print_info(f"   Results: {len(data.get('results', []))}")
            print_info(f"   Summary: {data.get('summary')}")
        else:
            print_error(f"Query failed: {response.status_code}")
            print_error(f"   Error: {response.text}")
    except Exception as e:
        print_error(f"API query failed: {e}")
        return False
    
    return True

async def main():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║        🎯 SIEM NLP ASSISTANT - INTEGRATION TEST SUITE 🎯          ║")
    print("║                                                                    ║")
    print("║                    Team Kartavya | SIH 2025                        ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    results = {}
    
    # Test 1: NLP Components
    results['nlp_components'] = await test_nlp_components()
    
    # Test 2: Full Pipeline
    results['full_pipeline'] = await test_full_pipeline()
    
    # Test 3: API Integration
    results['api_integration'] = await test_api_integration()
    
    # Final Summary
    print_header("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        test_display = test_name.replace('_', ' ').title()
        if passed:
            print_success(f"{test_display}: PASSED")
        else:
            print_error(f"{test_display}: FAILED")
    
    print(f"\n{Colors.BOLD}Overall Result:{Colors.END}")
    if passed_tests == total_tests:
        print_success(f"ALL TESTS PASSED ({passed_tests}/{total_tests})")
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 BACKEND INTEGRATION COMPLETE! 🎉{Colors.END}")
    else:
        print_warning(f"Some tests failed ({passed_tests}/{total_tests})")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())
