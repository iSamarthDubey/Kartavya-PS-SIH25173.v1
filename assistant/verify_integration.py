"""
Quick Integration Verification
Tests the complete assistant setup without requiring running servers.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from assistant.pipeline import ConversationalPipeline
        print("  ✅ ConversationalPipeline imported")
    except Exception as e:
        print(f"  ❌ ConversationalPipeline import failed: {e}")
        return False
    
    try:
        from assistant.main import app
        print("  ✅ FastAPI app imported")
    except Exception as e:
        print(f"  ❌ FastAPI app import failed: {e}")
        return False
    
    try:
        from assistant.router import assistant_router
        print("  ✅ Router imported")
    except Exception as e:
        print(f"  ❌ Router import failed: {e}")
        return False
    
    return True

def test_component_imports():
    """Test that backend components can be imported."""
    print("\nTesting backend component imports...")
    
    try:
        from backend.nlp.intent_classifier import IntentClassifier
        print("  ✅ IntentClassifier imported")
    except Exception as e:
        print(f"  ❌ IntentClassifier import failed: {e}")
        return False
    
    try:
        from backend.nlp.entity_extractor import EntityExtractor
        print("  ✅ EntityExtractor imported")
    except Exception as e:
        print(f"  ❌ EntityExtractor import failed: {e}")
        return False
    
    try:
        from backend.query_builder import QueryBuilder
        print("  ✅ QueryBuilder imported")
    except Exception as e:
        print(f"  ❌ QueryBuilder import failed: {e}")
        return False
    
    try:
        from siem_connector.elastic_connector import ElasticConnector
        print("  ✅ ElasticConnector imported")
    except Exception as e:
        print(f"  ❌ ElasticConnector import failed: {e}")
        return False
    
    try:
        from backend.response_formatter.formatter import ResponseFormatter
        print("  ✅ ResponseFormatter imported")
    except Exception as e:
        print(f"  ❌ ResponseFormatter import failed: {e}")
        return False
    
    return True

def test_pipeline_creation():
    """Test that pipeline can be created."""
    print("\nTesting pipeline creation...")
    
    try:
        from assistant.pipeline import ConversationalPipeline
        pipeline = ConversationalPipeline()
        print("  ✅ Pipeline created successfully")
        
        # Test health status
        status = pipeline.get_health_status()
        print(f"  ✅ Health status: {status['health_score']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Pipeline creation failed: {e}")
        return False

def test_nlp_components():
    """Test NLP components directly."""
    print("\nTesting NLP components...")
    
    try:
        from backend.nlp.intent_classifier import IntentClassifier
        from backend.nlp.entity_extractor import EntityExtractor
        
        # Test intent classification
        classifier = IntentClassifier()
        intent, confidence = classifier.classify_intent("Show me failed login attempts")
        print(f"  ✅ Intent classification: {intent} (confidence: {confidence:.2f})")
        
        # Test entity extraction
        extractor = EntityExtractor()
        entities = extractor.extract_entities("Show logs from user admin and IP 192.168.1.100")
        print(f"  ✅ Entity extraction: Found {len(entities)} entities")
        
        return True
    except Exception as e:
        print(f"  ❌ NLP component test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("CONVERSATIONAL ASSISTANT INTEGRATION VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Component Imports", test_component_imports()))
    results.append(("Pipeline Creation", test_pipeline_creation()))
    results.append(("NLP Components", test_nlp_components()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Assistant is ready to use.")
        print("\nNext steps:")
        print("1. Start the assistant: python assistant/main.py")
        print("2. Test the API: curl http://localhost:8001/assistant/health")
        print("3. Start the frontend: streamlit run ui_dashboard/streamlit_app.py")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
