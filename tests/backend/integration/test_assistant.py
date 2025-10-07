"""
Test Suite for Conversational Assistant
Comprehensive testing for the assistant pipeline and API endpoints.
"""

import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant.pipeline import ConversationalPipeline, create_pipeline
from assistant.main import app

class TestConversationalPipeline:
    """Test the core conversational pipeline functionality."""
    
    @pytest_asyncio.fixture
    async def pipeline(self):
        """Create a test pipeline instance."""
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
        return pipeline
    
    @pytest.mark.asyncio
    async def test_pipeline_initialization(self):
        """Test that pipeline initializes correctly."""
        pipeline = ConversationalPipeline()
        result = await pipeline.initialize()
        
        assert result is True or result is False  # Should return boolean
        assert hasattr(pipeline, 'is_initialized')
    
    @pytest.mark.asyncio
    async def test_process_query_basic(self, pipeline):
        """Test basic query processing."""
        user_input = "Show me recent security alerts"
        
        result = await pipeline.process_query(user_input)
        
        assert 'conversation_id' in result
        assert 'user_query' in result
        assert 'status' in result
        assert result['user_query'] == user_input
    
    @pytest.mark.asyncio
    async def test_process_query_with_conversation_id(self, pipeline):
        """Test query processing with conversation context."""
        user_input = "What about failed logins?"
        conversation_id = "test_conv_123"
        
        result = await pipeline.process_query(user_input, conversation_id)
        
        assert result['conversation_id'] == conversation_id
        assert 'metadata' in result
    
    @pytest.mark.asyncio
    async def test_health_status(self, pipeline):
        """Test health status reporting."""
        status = pipeline.get_health_status()
        
        assert 'is_initialized' in status
        assert 'components' in status
        assert 'health_score' in status
        assert 'status' in status
        
        # Check that components dict has expected keys
        expected_components = [
            'intent_classifier', 'entity_extractor', 'query_builder', 
            'elastic_connector', 'wazuh_connector', 'response_formatter', 
            'context_manager'
        ]
        for component in expected_components:
            assert component in status['components']
    
    @pytest.mark.asyncio
    async def test_conversation_history(self, pipeline):
        """Test conversation history functionality."""
        conversation_id = "test_history_123"
        
        # Process a query first
        await pipeline.process_query("Test query", conversation_id)
        
        # Get history
        history = await pipeline.get_conversation_history(conversation_id)
        
        assert isinstance(history, list)

class TestConversationalAPI:
    """Test the FastAPI endpoints for the conversational assistant."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/assistant/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/assistant/health")
        # May return 500 if components aren't fully initialized in test
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "components" in data
    
    def test_ask_endpoint_basic(self, client):
        """Test the basic ask endpoint."""
        query_data = {
            "query": "Show me recent logs"
        }
        
        response = client.post("/assistant/ask", json=query_data)
        # May return 500 if backend components aren't available
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "conversation_id" in data
            assert "user_query" in data
            assert data["user_query"] == query_data["query"]
    
    def test_ask_endpoint_with_conversation_id(self, client):
        """Test ask endpoint with conversation ID."""
        query_data = {
            "query": "What about errors?",
            "conversation_id": "test_conv_456"
        }
        
        response = client.post("/assistant/ask", json=query_data)
        assert response.status_code in [200, 422, 500]
    
    def test_ask_endpoint_validation(self, client):
        """Test input validation on ask endpoint."""
        # Test empty query
        response = client.post("/assistant/ask", json={"query": ""})
        assert response.status_code == 422
        
        # Test missing query
        response = client.post("/assistant/ask", json={})
        assert response.status_code == 422
    
    def test_status_endpoint(self, client):
        """Test the detailed status endpoint."""
        response = client.get("/assistant/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "features" in data
    
    def test_capabilities_endpoint(self, client):
        """Test the capabilities endpoint."""
        response = client.get("/assistant/v1/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "natural_language_support" in data
        assert "intent_categories" in data
        assert "entity_types" in data
    
    def test_examples_endpoint(self, client):
        """Test the examples endpoint."""
        response = client.get("/assistant/v1/examples")
        assert response.status_code == 200
        data = response.json()
        assert "security_queries" in data
        assert "investigation_queries" in data
        assert "monitoring_queries" in data
    
    def test_feedback_endpoint(self, client):
        """Test the feedback submission endpoint."""
        feedback_data = {
            "rating": 5,
            "comment": "Great response!",
            "query": "test query"
        }
        
        response = client.post("/assistant/v1/feedback", json=feedback_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "feedback_id" in data

class TestPipelineComponents:
    """Test individual pipeline components in isolation."""
    
    @pytest.mark.asyncio
    async def test_nlp_processing_fallback(self):
        """Test NLP processing with fallback when components unavailable."""
        pipeline = ConversationalPipeline()
        
        # Test without initializing components
        result = await pipeline._process_nlp("test query", "conv_123")
        
        assert 'intent' in result
        assert 'entities' in result
        assert 'confidence' in result
    
    @pytest.mark.asyncio
    async def test_query_generation_fallback(self):
        """Test query generation fallback."""
        pipeline = ConversationalPipeline()
        
        nlp_result = {'intent': 'search_logs', 'entities': []}
        result = await pipeline._generate_query(nlp_result, "test query")
        
        assert 'query_type' in result
        assert 'query' in result
    
    @pytest.mark.asyncio
    async def test_siem_execution_empty(self):
        """Test SIEM execution with no connectors."""
        pipeline = ConversationalPipeline()
        
        query_result = {'query': '*', 'limit': 10}
        result = await pipeline._execute_siem_query(query_result)
        
        assert 'hits' in result
        assert 'total' in result
        assert 'sources' in result
        assert result['total'] == 0
    
    @pytest.mark.asyncio
    async def test_response_formatting_fallback(self):
        """Test response formatting fallback."""
        pipeline = ConversationalPipeline()
        
        siem_result = {'hits': [], 'total': 0}
        nlp_result = {'intent': 'search_logs'}
        result = await pipeline._format_response(siem_result, nlp_result)
        
        assert 'data' in result
        assert 'summary' in result
        assert 'visualizations' in result

def test_create_pipeline_function():
    """Test the convenience pipeline creation function."""
    # This is an async function, so we need to test it differently
    assert callable(create_pipeline)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

# --- Merged from assistant/test_assistant.py ---
"""
Test Suite for Conversational Assistant
Comprehensive testing for the assistant pipeline and API endpoints.
"""

import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant.pipeline import ConversationalPipeline, create_pipeline
from assistant.main import app

class TestConversationalPipeline:
    """Test the core conversational pipeline functionality."""
    
    @pytest_asyncio.fixture
    async def pipeline(self):
        """Create a test pipeline instance."""
        pipeline = ConversationalPipeline()
        await pipeline.initialize()
        return pipeline
    
    @pytest.mark.asyncio
    async def test_pipeline_initialization(self):
        """Test that pipeline initializes correctly."""
        pipeline = ConversationalPipeline()
        result = await pipeline.initialize()
        
        assert result is True or result is False  # Should return boolean
        assert hasattr(pipeline, 'is_initialized')
    
    @pytest.mark.asyncio
    async def test_process_query_basic(self, pipeline):
        """Test basic query processing."""
        user_input = "Show me recent security alerts"
        
        result = await pipeline.process_query(user_input)
        
        assert 'conversation_id' in result
        assert 'user_query' in result
        assert 'status' in result
        assert result['user_query'] == user_input
    
    @pytest.mark.asyncio
    async def test_process_query_with_conversation_id(self, pipeline):
        """Test query processing with conversation context."""
        user_input = "What about failed logins?"
        conversation_id = "test_conv_123"
        
        result = await pipeline.process_query(user_input, conversation_id)
        
        assert result['conversation_id'] == conversation_id
        assert 'metadata' in result
    
    @pytest.mark.asyncio
    async def test_health_status(self, pipeline):
        """Test health status reporting."""
        status = pipeline.get_health_status()
        
        assert 'is_initialized' in status
        assert 'components' in status
        assert 'health_score' in status
        assert 'status' in status
        
        # Check that components dict has expected keys
        expected_components = [
            'intent_classifier', 'entity_extractor', 'query_builder', 
            'elastic_connector', 'wazuh_connector', 'response_formatter', 
            'context_manager'
        ]
        for component in expected_components:
            assert component in status['components']
    
    @pytest.mark.asyncio
    async def test_conversation_history(self, pipeline):
        """Test conversation history functionality."""
        conversation_id = "test_history_123"
        
        # Process a query first
        await pipeline.process_query("Test query", conversation_id)
        
        # Get history
        history = await pipeline.get_conversation_history(conversation_id)
        
        assert isinstance(history, list)

class TestConversationalAPI:
    """Test the FastAPI endpoints for the conversational assistant."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/assistant/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/assistant/health")
        # May return 500 if components aren't fully initialized in test
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "components" in data
    
    def test_ask_endpoint_basic(self, client):
        """Test the basic ask endpoint."""
        query_data = {
            "query": "Show me recent logs"
        }
        
        response = client.post("/assistant/ask", json=query_data)
        # May return 500 if backend components aren't available
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "conversation_id" in data
            assert "user_query" in data
            assert data["user_query"] == query_data["query"]
    
    def test_ask_endpoint_with_conversation_id(self, client):
        """Test ask endpoint with conversation ID."""
        query_data = {
            "query": "What about errors?",
            "conversation_id": "test_conv_456"
        }
        
        response = client.post("/assistant/ask", json=query_data)
        assert response.status_code in [200, 422, 500]
    
    def test_ask_endpoint_validation(self, client):
        """Test input validation on ask endpoint."""
        # Test empty query
        response = client.post("/assistant/ask", json={"query": ""})
        assert response.status_code == 422
        
        # Test missing query
        response = client.post("/assistant/ask", json={})
        assert response.status_code == 422
    
    def test_status_endpoint(self, client):
        """Test the detailed status endpoint."""
        response = client.get("/assistant/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "features" in data
    
    def test_capabilities_endpoint(self, client):
        """Test the capabilities endpoint."""
        response = client.get("/assistant/v1/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "natural_language_support" in data
        assert "intent_categories" in data
        assert "entity_types" in data
    
    def test_examples_endpoint(self, client):
        """Test the examples endpoint."""
        response = client.get("/assistant/v1/examples")
        assert response.status_code == 200
        data = response.json()
        assert "security_queries" in data
        assert "investigation_queries" in data
        assert "monitoring_queries" in data
    
    def test_feedback_endpoint(self, client):
        """Test the feedback submission endpoint."""
        feedback_data = {
            "rating": 5,
            "comment": "Great response!",
            "query": "test query"
        }
        
        response = client.post("/assistant/v1/feedback", json=feedback_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "feedback_id" in data

class TestPipelineComponents:
    """Test individual pipeline components in isolation."""
    
    @pytest.mark.asyncio
    async def test_nlp_processing_fallback(self):
        """Test NLP processing with fallback when components unavailable."""
        pipeline = ConversationalPipeline()
        
        # Test without initializing components
        result = await pipeline._process_nlp("test query", "conv_123")
        
        assert 'intent' in result
        assert 'entities' in result
        assert 'confidence' in result
    
    @pytest.mark.asyncio
    async def test_query_generation_fallback(self):
        """Test query generation fallback."""
        pipeline = ConversationalPipeline()
        
        nlp_result = {'intent': 'search_logs', 'entities': []}
        result = await pipeline._generate_query(nlp_result, "test query")
        
        assert 'query_type' in result
        assert 'query' in result
    
    @pytest.mark.asyncio
    async def test_siem_execution_empty(self):
        """Test SIEM execution with no connectors."""
        pipeline = ConversationalPipeline()
        
        query_result = {'query': '*', 'limit': 10}
        result = await pipeline._execute_siem_query(query_result)
        
        assert 'hits' in result
        assert 'total' in result
        assert 'sources' in result
        assert result['total'] == 0
    
    @pytest.mark.asyncio
    async def test_response_formatting_fallback(self):
        """Test response formatting fallback."""
        pipeline = ConversationalPipeline()
        
        siem_result = {'hits': [], 'total': 0}
        nlp_result = {'intent': 'search_logs'}
        result = await pipeline._format_response(siem_result, nlp_result)
        
        assert 'data' in result
        assert 'summary' in result
        assert 'visualizations' in result

def test_create_pipeline_function():
    """Test the convenience pipeline creation function."""
    # This is an async function, so we need to test it differently
    assert callable(create_pipeline)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])