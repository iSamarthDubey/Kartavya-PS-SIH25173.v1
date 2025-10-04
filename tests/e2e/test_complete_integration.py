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
