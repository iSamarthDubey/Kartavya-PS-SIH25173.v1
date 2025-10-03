"""
FastAPI Backend Service for SIEM NLP Assistant
Provides REST API endpoints for the SIEM query processing system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nlp_parser.parser import NLPParser
    from rag_pipeline.pipeline import RAGPipeline
    from siem_connector.elastic_connector import ElasticConnector
    from response_formatter.text_formatter import TextFormatter
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="SIEM NLP Assistant API",
    description="Natural Language Processing API for SIEM Query Generation",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    parser_type: str = "enhanced"  # enhanced or basic
    max_results: int = 100
    time_range: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    query: str
    intent: str
    confidence: float
    entities: Dict[str, List[str]]
    siem_query: str
    results: List[Dict[str, Any]]
    formatted_response: str
    execution_time: float

class HealthResponse(BaseModel):
    status: str
    version: str
    components: Dict[str, bool]

# Global components
nlp_parser = None
rag_pipeline = None
elastic_connector = None
text_formatter = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global nlp_parser, rag_pipeline, elastic_connector, text_formatter
    
    try:
        # Initialize NLP Parser with ML capabilities
        nlp_parser = NLPParser(use_ml=True)
        logging.info("✅ NLP Parser initialized")
        
        # Initialize RAG Pipeline
        rag_pipeline = RAGPipeline()
        logging.info("✅ RAG Pipeline initialized")
        
        # Initialize Elasticsearch connector
        elastic_connector = ElasticConnector()
        logging.info("✅ Elasticsearch connector initialized")
        
        # Initialize text formatter
        text_formatter = TextFormatter()
        logging.info("✅ Text formatter initialized")
        
    except Exception as e:
        logging.error(f"❌ Startup error: {e}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "SIEM NLP Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    components = {
        "nlp_parser": nlp_parser is not None,
        "rag_pipeline": rag_pipeline is not None,
        "elastic_connector": elastic_connector is not None,
        "text_formatter": text_formatter is not None
    }
    
    all_healthy = all(components.values())
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        version="1.0.0",
        components=components
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query and return SIEM results."""
    import time
    start_time = time.time()
    
    if not nlp_parser:
        raise HTTPException(status_code=503, detail="NLP Parser not available")
    
    try:
        # Parse natural language query
        use_ml = request.parser_type == "enhanced"
        parser = NLPParser(use_ml=use_ml)
        parsed_query = parser.parse_query(request.query)
        
        # Generate SIEM query using RAG
        if rag_pipeline:
            siem_query = rag_pipeline.generate_query(parsed_query)
        else:
            siem_query = "# RAG Pipeline not available"
        
        # Execute query (mock results if no real connection)
        results = []
        if elastic_connector:
            try:
                results = elastic_connector.search(siem_query, max_results=request.max_results)
            except Exception as e:
                logging.warning(f"Elasticsearch query failed: {e}")
                results = _generate_mock_results(parsed_query)
        else:
            results = _generate_mock_results(parsed_query)
        
        # Format response
        if text_formatter:
            formatted_response = text_formatter.format_results(results, parsed_query)
        else:
            formatted_response = f"Found {len(results)} results for query: {request.query}"
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            query=request.query,
            intent=parsed_query.get('intent', 'unknown'),
            confidence=parsed_query.get('confidence', 0.0),
            entities=parsed_query.get('entities', {}),
            siem_query=siem_query,
            results=results,
            formatted_response=formatted_response,
            execution_time=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/parser/info")
async def get_parser_info():
    """Get information about the NLP parser capabilities."""
    if not nlp_parser:
        raise HTTPException(status_code=503, detail="NLP Parser not available")
    
    return nlp_parser.get_parser_info()

@app.get("/suggestions")
async def get_query_suggestions(partial_query: str = ""):
    """Get query suggestions based on partial input."""
    if not nlp_parser:
        raise HTTPException(status_code=503, detail="NLP Parser not available")
    
    suggestions = nlp_parser.generate_query_suggestions(partial_query)
    return {"suggestions": suggestions}

def _generate_mock_results(parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate mock results for demonstration."""
    import random
    from datetime import datetime, timedelta
    
    mock_results = []
    intent = parsed_query.get('intent', 'search_logs')
    entities = parsed_query.get('entities', {})
    
    # Generate 5-10 mock results
    for i in range(random.randint(5, 10)):
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        
        if intent == 'search_logs':
            result = {
                "timestamp": timestamp.isoformat(),
                "level": random.choice(["INFO", "WARN", "ERROR", "CRITICAL"]),
                "source": f"server-{random.randint(1, 5)}",
                "message": f"Security event {i+1} detected",
                "ip_address": f"192.168.1.{random.randint(1, 254)}"
            }
        elif intent == 'count_events':
            result = {
                "count": random.randint(10, 100),
                "event_type": "failed_login",
                "time_range": "last_hour"
            }
        else:
            result = {
                "timestamp": timestamp.isoformat(),
                "event_type": intent,
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "description": f"Mock {intent} event"
            }
        
        mock_results.append(result)
    
    return mock_results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)