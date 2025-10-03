#!/usr/bin/env python3
"""
Test script for SIEM NLP components
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_components():
    """Test all NLP components."""
    print("🧪 Testing SIEM NLP Components")
    print("=" * 50)
    
    # Test Intent Classifier
    try:
        from nlp.intent_classifier import IntentClassifier, QueryIntent
        classifier = IntentClassifier()
        
        test_query = "Show failed login attempts from last hour"
        intent, confidence = classifier.classify_intent(test_query)
        
        print(f"✅ Intent Classifier: {intent.value} (confidence: {confidence:.2f})")
    except Exception as e:
        print(f"❌ Intent Classifier failed: {e}")
    
    # Test Entity Extractor
    try:
        from nlp.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        
        test_query = "Show failed logins from user admin on 192.168.1.100"
        entities = extractor.extract_entities(test_query)
        
        print(f"✅ Entity Extractor: Found {len(entities)} entities")
        for entity in entities:
            print(f"   - {entity.type}: {entity.value}")
    except Exception as e:
        print(f"❌ Entity Extractor failed: {e}")
    
    # Test Query Builder
    try:
        from query_builder import QueryBuilder
        builder = QueryBuilder()
        
        test_query = "Show failed login attempts"
        es_query = builder.build_query(test_query)
        
        print(f"✅ Query Builder: Generated query with {len(str(es_query))} characters")
    except Exception as e:
        print(f"❌ Query Builder failed: {e}")
    
    # Test Elasticsearch Client
    try:
        from elastic_client import ElasticClient
        client = ElasticClient()
        
        print(f"✅ Elasticsearch Client: Connected = {client.connected}")
    except Exception as e:
        print(f"❌ Elasticsearch Client failed: {e}")
    
    # Test Response Formatter
    try:
        from response_formatter.formatter import ResponseFormatter
        formatter = ResponseFormatter()
        
        sample_results = [
            {"@timestamp": "2024-01-15T10:30:00Z", "user.name": "admin", "message": "Test event"}
        ]
        
        response = formatter.format_response(
            query="test query",
            intent="test_intent", 
            results=sample_results
        )
        
        print(f"✅ Response Formatter: Generated response with {len(response.summary)} chars")
    except Exception as e:
        print(f"❌ Response Formatter failed: {e}")
    
    print("\n🎉 Component testing complete!")

def start_server():
    """Start the FastAPI server."""
    try:
        import uvicorn
        from main import app
        
        print("🚀 Starting SIEM NLP Backend Server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("💡 Health Check: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    # First test components
    test_components()
    
    # Ask user if they want to start the server
    response = input("\n🔥 Start the backend server? (Y/N): ").strip().lower()
    if response in ['y', 'yes']:
        start_server()
    else:
        print("👋 Testing complete. Run this script again and choose 'Y' to start the server.")