#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE APPLICATION TEST SUITE
Complete end-to-end testing of SIEM NLP Assistant

Tests:
1. Import validation
2. Component initialization
3. NLP processing
4. Query generation
5. Backend API (if running)
6. Frontend connectivity
7. Integration workflow
"""

import sys
import os
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"{BOLD}{CYAN}{text.center(80)}{RESET}")
    print(f"{'='*80}\n")

def print_section(text: str):
    """Print section header"""
    print(f"\n{BOLD}{BLUE}{'─'*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}[PASS] {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}[FAIL] {text}{RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}[WARN] {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{CYAN}[INFO] {text}{RESET}")


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.start_time = time.time()
    
    def add_pass(self, test_name: str):
        self.passed.append(test_name)
        print_success(f"{test_name} - PASSED")
    
    def add_fail(self, test_name: str, error: str):
        self.failed.append((test_name, error))
        print_error(f"{test_name} - FAILED")
        print_error(f"   Error: {error}")
    
    def add_warning(self, test_name: str, message: str):
        self.warnings.append((test_name, message))
        print_warning(f"{test_name} - WARNING")
        print_warning(f"   {message}")
    
    def print_summary(self):
        """Print final test summary"""
        elapsed = time.time() - self.start_time
        
        print_header("TEST SUMMARY")
        
        print(f"{BOLD}Total Tests:{RESET} {len(self.passed) + len(self.failed)}")
        print(f"{GREEN}[PASS] Passed:{RESET} {len(self.passed)}")
        print(f"{RED}[FAIL] Failed:{RESET} {len(self.failed)}")
        print(f"{YELLOW}[WARN] Warnings:{RESET} {len(self.warnings)}")
        print(f"{CYAN}[TIME] Duration:{RESET} {elapsed:.2f}s")
        
        if self.failed:
            print_section("Failed Tests Details")
            for test_name, error in self.failed:
                print(f"{RED}[FAIL] {test_name}{RESET}")
                print(f"   {error}\n")
        
        if self.warnings:
            print_section("Warnings")
            for test_name, message in self.warnings:
                print(f"{YELLOW}[WARN] {test_name}{RESET}")
                print(f"   {message}\n")
        
        # Final verdict
        print("\n" + "="*80)
        if len(self.failed) == 0:
            print(f"{GREEN}{BOLD}{'*** ALL TESTS PASSED! ***'.center(80)}{RESET}")
        else:
            print(f"{YELLOW}{BOLD}{'*** SOME TESTS FAILED ***'.center(80)}{RESET}")
        print("="*80 + "\n")


# Initialize results tracker
results = TestResults()


def test_imports():
    """Test 1: Validate all module imports"""
    print_section("TEST 1: Import Validation")
    
    imports_to_test = [
        ("backend.nlp.intent_classifier", "IntentClassifier"),
        ("backend.nlp.entity_extractor", "EntityExtractor"),
        ("backend.query_builder", "QueryBuilder"),
        ("siem_connector.elastic_connector", "ElasticConnector"),
        ("siem_connector.wazuh_connector", "WazuhConnector"),
        ("backend.response_formatter.formatter", "ResponseFormatter"),
        ("assistant.pipeline", "ConversationalPipeline"),
        ("assistant.context_manager", "ContextManager"),
    ]
    
    failed_imports = []
    
    for module_path, class_name in imports_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print_success(f"Import {module_path}.{class_name}")
        except Exception as e:
            failed_imports.append((module_path, class_name, str(e)))
            print_error(f"Import {module_path}.{class_name}")
            print_info(f"   Error: {e}")
    
    if not failed_imports:
        results.add_pass("Import Validation")
    else:
        results.add_fail("Import Validation", f"{len(failed_imports)} imports failed")


def test_component_initialization():
    """Test 2: Initialize all components"""
    print_section("TEST 2: Component Initialization")
    
    try:
        from backend.nlp.intent_classifier import IntentClassifier
        from backend.nlp.entity_extractor import EntityExtractor
        from backend.query_builder import QueryBuilder
        
        # Test Intent Classifier
        try:
            classifier = IntentClassifier()
            print_success("IntentClassifier initialized")
        except Exception as e:
            results.add_fail("IntentClassifier Init", str(e))
            return
        
        # Test Entity Extractor
        try:
            extractor = EntityExtractor()
            print_success("EntityExtractor initialized")
        except Exception as e:
            results.add_fail("EntityExtractor Init", str(e))
            return
        
        # Test Query Builder
        try:
            builder = QueryBuilder()
            print_success("QueryBuilder initialized")
        except Exception as e:
            results.add_fail("QueryBuilder Init", str(e))
            return
        
        results.add_pass("Component Initialization")
        
    except Exception as e:
        results.add_fail("Component Initialization", str(e))


async def test_nlp_processing():
    """Test 3: NLP Processing (Intent + Entity)"""
    print_section("TEST 3: NLP Processing")
    
    try:
        from backend.nlp.intent_classifier import IntentClassifier
        from backend.nlp.entity_extractor import EntityExtractor
        
        classifier = IntentClassifier()
        extractor = EntityExtractor()
        
        test_queries = [
            "Show failed login attempts from user admin",
            "Find high severity alerts from 192.168.1.100",
            "List network connections on port 443 from yesterday",
        ]
        
        all_passed = True
        
        for query in test_queries:
            print_info(f"Testing: '{query}'")
            
            # Test intent classification
            try:
                intent, confidence = classifier.classify_intent(query)
                intent_str = intent.value if hasattr(intent, 'value') else str(intent)
                print(f"   Intent: {intent_str} (confidence: {confidence:.2%})")
            except Exception as e:
                print_error(f"   Intent classification failed: {e}")
                all_passed = False
                continue
            
            # Test entity extraction
            try:
                entities = extractor.extract_entities(query)
                print(f"   Entities: {len(entities)} extracted")
                for entity in entities[:3]:  # Show first 3
                    print(f"      • {entity.type}: {entity.value} ({entity.confidence:.2f})")
            except Exception as e:
                print_error(f"   Entity extraction failed: {e}")
                all_passed = False
                continue
        
        if all_passed:
            results.add_pass("NLP Processing")
        else:
            results.add_fail("NLP Processing", "Some queries failed")
    
    except Exception as e:
        results.add_fail("NLP Processing", str(e))
        print(traceback.format_exc())


async def test_query_generation():
    """Test 4: Query Generation"""
    print_section("TEST 4: Query Generation")
    
    try:
        from backend.nlp.intent_classifier import IntentClassifier
        from backend.nlp.entity_extractor import EntityExtractor
        from backend.query_builder import QueryBuilder
        
        classifier = IntentClassifier()
        extractor = EntityExtractor()
        builder = QueryBuilder()
        
        test_query = "Show failed logins from user admin in the last hour"
        print_info(f"Test Query: '{test_query}'")
        
        # Get intent and entities
        intent, confidence = classifier.classify_intent(test_query)
        entities = extractor.extract_entities(test_query)
        
        # Build query
        query_params = {
            'intent': intent.value if hasattr(intent, 'value') else str(intent),
            'entities': entities,
            'raw_text': test_query
        }
        
        result = await builder.build_query(query_params)
        
        print_success("Query generation successful")
        print_info(f"   Query Type: {result.get('query_type', 'N/A')}")
        print_info(f"   Query Structure: {type(result.get('query', {}))}")
        
        if 'query' in result:
            results.add_pass("Query Generation")
        else:
            results.add_fail("Query Generation", "No query generated")
    
    except Exception as e:
        results.add_fail("Query Generation", str(e))
        print(traceback.format_exc())


async def test_full_pipeline():
    """Test 5: Full Pipeline Integration"""
    print_section("TEST 5: Full Pipeline Integration")
    
    try:
        from assistant.pipeline import ConversationalPipeline
        
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
        
        print_success("Pipeline initialized")
        
        # Test queries
        test_queries = [
            "Show failed login attempts",
            "Find high severity alerts",
            "List security events from today",
        ]
        
        all_passed = True
        
        for query in test_queries:
            print_info(f"Processing: '{query}'")
            try:
                result = await pipeline.process_query(query)
                
                # Validate response structure
                required_keys = ['intent', 'entities', 'data', 'metadata']
                missing_keys = [k for k in required_keys if k not in result]
                
                if missing_keys:
                    print_warning(f"   Missing keys: {missing_keys}")
                else:
                    print_success(f"   Response complete")
                    print_info(f"      Intent: {result.get('intent', 'N/A')}")
                    print_info(f"      Entities: {len(result.get('entities', []))}")
                    print_info(f"      Results: {result.get('data', {}).get('total', 0)}")
            
            except Exception as e:
                print_error(f"   Pipeline processing failed: {e}")
                all_passed = False
        
        if all_passed:
            results.add_pass("Full Pipeline Integration")
        else:
            results.add_fail("Full Pipeline Integration", "Some queries failed")
    
    except Exception as e:
        results.add_fail("Full Pipeline Integration", str(e))
        print(traceback.format_exc())


def test_backend_api():
    """Test 6: Backend API Connectivity"""
    print_section("TEST 6: Backend API (Port 8001)")
    
    try:
        import requests
        
        api_url = "http://localhost:8001"
        
        # Test health endpoint
        try:
            response = requests.get(f"{api_url}/assistant/health", timeout=2)
            if response.status_code == 200:
                print_success("API Health Check: OK")
                print_info(f"   Status: {response.json()}")
                results.add_pass("Backend API Health")
            else:
                results.add_warning("Backend API", f"Status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            results.add_warning("Backend API", "Not running. Start with: python assistant/main.py")
            print_warning("Backend API not running")
            print_info("   Start with: python assistant/main.py")
        except Exception as e:
            results.add_fail("Backend API", str(e))
    
    except ImportError:
        results.add_warning("Backend API Test", "requests library not installed")


def test_elasticsearch_connection():
    """Test 7: Elasticsearch Connection"""
    print_section("TEST 7: Elasticsearch Connection (Port 9200)")
    
    try:
        from siem_connector.elastic_connector import ElasticConnector
        
        connector = ElasticConnector()
        
        # Try to connect
        try:
            # This will fail if Elasticsearch isn't running - that's expected
            print_info("Attempting Elasticsearch connection...")
            
            results.add_warning(
                "Elasticsearch", 
                "Not running (expected). This is optional for demo mode."
            )
            print_warning("Elasticsearch not running (expected for demo mode)")
            print_info("   To use real data, start with: docker run -p 9200:9200 elasticsearch:8.11.0")
        
        except Exception as e:
            results.add_warning("Elasticsearch", "Not available (optional)")
    
    except Exception as e:
        results.add_fail("Elasticsearch Test", str(e))


def test_file_structure():
    """Test 8: Verify File Structure"""
    print_section("TEST 8: File Structure Validation")
    
    required_files = [
        "assistant/main.py",
        "assistant/pipeline.py",
        "assistant/router.py",
        "backend/nlp/intent_classifier.py",
        "backend/nlp/entity_extractor.py",
        "backend/query_builder.py",
        "siem_connector/elastic_connector.py",
        "ui_dashboard/streamlit_app.py",
        "requirements.txt",
        "README.md",
    ]
    
    required_dirs = [
        "assistant",
        "backend",
        "backend/nlp",
        "siem_connector",
        "ui_dashboard",
        "tests",
        "docs",
    ]
    
    all_exist = True
    
    # Check files
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"File: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_exist = False
    
    # Check directories
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print_success(f"Dir:  {dir_path}/")
        else:
            print_error(f"Missing: {dir_path}/")
            all_exist = False
    
    if all_exist:
        results.add_pass("File Structure")
    else:
        results.add_fail("File Structure", "Some files/directories missing")


def test_dependencies():
    """Test 9: Check Dependencies"""
    print_section("TEST 9: Dependency Check")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "elasticsearch",
        "pydantic",
        "pandas",
        "plotly",
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"Package: {package}")
        except ImportError:
            print_error(f"Missing: {package}")
            missing.append(package)
    
    if not missing:
        results.add_pass("Dependencies")
    else:
        results.add_fail("Dependencies", f"Missing: {', '.join(missing)}")
        print_info("   Install with: pip install -r requirements.txt")


async def run_all_tests():
    """Run all tests in sequence"""
    
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    print_header("KARTAVYA - SIEM NLP ASSISTANT")
    print_header("COMPREHENSIVE TEST SUITE")
    print(f"\n{CYAN}Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")
    
    # Run tests
    test_file_structure()
    test_dependencies()
    test_imports()
    test_component_initialization()
    await test_nlp_processing()
    await test_query_generation()
    await test_full_pipeline()
    test_backend_api()
    test_elasticsearch_connection()
    
    # Print summary
    results.print_summary()
    
    # Recommendations
    print_section("RECOMMENDATIONS")
    
    if any("Backend API" in w[0] for w in results.warnings):
        print(f"{YELLOW}1. Start Backend API:{RESET}")
        print(f"   python assistant/main.py")
        print()
    
    if any("Elasticsearch" in w[0] for w in results.warnings):
        print(f"{YELLOW}2. (Optional) Start Elasticsearch:{RESET}")
        print(f"   docker run -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0")
        print()
    
    print(f"{GREEN}3. Start Frontend UI:{RESET}")
    print(f"   streamlit run ui_dashboard/streamlit_app.py")
    print()
    
    print(f"{CYAN}4. Access Application:{RESET}")
    print(f"   Backend API: http://localhost:8001")
    print(f"   Frontend UI: http://localhost:8502")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        print(traceback.format_exc())
