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
import time

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our new NLP components
try:
    from nlp.intent_classifier import IntentClassifier, QueryIntent
    from nlp.entity_extractor import EntityExtractor
    from query_builder import QueryBuilder
    from elastic_client import ElasticClient
    from response_formatter.formatter import ResponseFormatter
    logger.info("✅ All imports successful")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    # Fallback imports for running from different directories
    import sys
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_dir)
    try:
        from nlp.intent_classifier import IntentClassifier, QueryIntent
        from nlp.entity_extractor import EntityExtractor
        from query_builder import QueryBuilder
        from elastic_client import ElasticClient
        from response_formatter.formatter import ResponseFormatter
        logger.info("✅ Fallback imports successful")
    except ImportError as e2:
        logger.error(f"❌ Fallback import error: {e2}")
        raise

# Legacy imports with fallback
try:
    from rag_pipeline.pipeline import RAGPipeline
except ImportError:
    RAGPipeline = None
    logging.warning("RAG Pipeline not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
intent_classifier = None
entity_extractor = None
query_builder = None
elastic_client = None
response_formatter = None
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global intent_classifier, entity_extractor, query_builder, elastic_client, response_formatter, rag_pipeline
    
    logger.info("🚀 Starting backend components initialization...")
    
    # Initialize NLP components
    try:
        intent_classifier = IntentClassifier()
        logger.info("✅ Intent Classifier initialized")
    except Exception as e:
        logger.error(f"❌ Intent Classifier failed: {e}")
        intent_classifier = None
        
    try:
        entity_extractor = EntityExtractor()
        logger.info("✅ Entity Extractor initialized")
    except Exception as e:
        logger.error(f"❌ Entity Extractor failed: {e}")
        entity_extractor = None
        
    try:
        query_builder = QueryBuilder()
        logger.info("✅ Query Builder initialized")
    except Exception as e:
        logger.error(f"❌ Query Builder failed: {e}")
        query_builder = None
        
    # Initialize Elasticsearch client
    try:
        elastic_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        elastic_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
        elastic_client = ElasticClient(host=elastic_host, port=elastic_port)
        logger.info("✅ Elasticsearch client initialized")
    except Exception as e:
        logger.error(f"❌ Elasticsearch client failed: {e}")
        elastic_client = None
        
    # Initialize response formatter
    try:
        response_formatter = ResponseFormatter()
        logger.info("✅ Response formatter initialized")
    except Exception as e:
        logger.error(f"❌ Response formatter failed: {e}")
        response_formatter = None
        
    # Initialize RAG Pipeline if available
    try:
        if RAGPipeline:
            rag_pipeline = RAGPipeline()
            logger.info("✅ RAG Pipeline initialized")
        else:
            logger.info("ℹ️ RAG Pipeline not available")
    except Exception as e:
        logger.error(f"❌ RAG Pipeline failed: {e}")
        rag_pipeline = None
    
    # Report final status
    working_components = sum([
        intent_classifier is not None,
        entity_extractor is not None, 
        query_builder is not None,
        response_formatter is not None
    ])
    
    logger.info(f"🎯 Initialization complete: {working_components}/4 core components working")
    
    if working_components < 4:
        logger.warning("⚠️ Some components failed to initialize - NLP Parser may have limited functionality")

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
        "nlp_parser": (intent_classifier is not None and 
                      entity_extractor is not None and 
                      query_builder is not None),
        "rag_pipeline": rag_pipeline is not None,
        "elastic_connector": elastic_client is not None,
        "text_formatter": response_formatter is not None
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
    start_time = time.time()
    
    # Check if core NLP components are available
    if not intent_classifier or not entity_extractor or not query_builder:
        logger.error("❌ NLP Parser components not available")
        raise HTTPException(status_code=503, detail="NLP Parser not available")
    
    if not response_formatter:
        logger.error("❌ Response formatter not available")
        raise HTTPException(status_code=503, detail="Response formatter not available")
    
    try:
        # Step 1: Classify intent
        intent, intent_confidence = intent_classifier.classify_intent(request.query)
        logger.info(f"Intent classified: {intent.value} (confidence: {intent_confidence:.2f})")
        
        # Step 2: Extract entities
        entities = entity_extractor.extract_entities(request.query)
        entity_summary = entity_extractor.get_entity_summary(entities)
        logger.info(f"Entities extracted: {entity_summary}")
        
        # Step 3: Build Elasticsearch query
        es_query = query_builder.build_query(request.query)
        logger.info("Elasticsearch query built")
        
        # Step 4: Execute query
        results = []
        aggregations = None
        
        if elastic_client and elastic_client.connected:
            try:
                # Use the search method from our ElasticClient
                index_pattern = "logs-*"  # Default index pattern
                search_response = elastic_client.client.search(
                    index=index_pattern,
                    body=es_query,
                    size=request.max_results
                )
                
                # Extract hits
                hits = search_response.get('hits', {}).get('hits', [])
                results = [hit.get('_source', {}) for hit in hits]
                
                # Extract aggregations if present
                aggregations = search_response.get('aggregations', None)
                
                logger.info(f"Query executed successfully: {len(results)} results")
                
            except Exception as e:
                logger.warning(f"Elasticsearch query failed: {e}")
                results = _generate_mock_results(intent, entity_summary)
        else:
            logger.warning("Elasticsearch not connected, using mock results")
            results = _generate_mock_results(intent, entity_summary)
        
        # Step 5: Format response
        formatted_response = None
        if response_formatter:
            formatted_response = response_formatter.format_response(
                query=request.query,
                intent=intent.value,
                results=results,
                aggregations=aggregations
            )
            formatted_text = formatted_response.summary
        else:
            formatted_text = f"Found {len(results)} results for query: {request.query}"
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            query=request.query,
            intent=intent.value,
            confidence=intent_confidence,
            entities=entity_summary,
            siem_query=str(es_query),  # Convert query dict to string
            results=results,
            formatted_response=formatted_text,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/parser/info")
async def get_parser_info():
    """Get information about the NLP parser capabilities."""
    if not intent_classifier or not entity_extractor:
        raise HTTPException(status_code=503, detail="NLP components not available")
    
    return {
        "intent_classifier": {
            "available_intents": [intent.value for intent in QueryIntent],
            "description": "Classifies user intent from natural language queries"
        },
        "entity_extractor": {
            "supported_entities": ["ip_address", "username", "domain", "port", "event_id", "time_range"],
            "description": "Extracts entities like IPs, usernames, and time ranges from queries"
        },
        "query_builder": {
            "output_formats": ["elasticsearch_dsl", "kql"],
            "description": "Converts natural language to SIEM queries"
        }
    }

@app.get("/suggestions")
async def get_query_suggestions(partial_query: str = ""):
    """Get query suggestions based on partial input."""
    suggestions = [
        "Show failed login attempts from last hour",
        "Find security alerts with high severity",
        "Get network traffic on port 443",
        "List successful logins for admin users",
        "Show malware detections from yesterday",
        "Find system errors from specific server",
        "Display user activity for suspicious accounts",
        "Get firewall blocked connections"
    ]
    
    # Filter suggestions based on partial query
    if partial_query:
        filtered_suggestions = [s for s in suggestions if partial_query.lower() in s.lower()]
        return {"suggestions": filtered_suggestions[:5]}
    
    return {"suggestions": suggestions[:8]}

def _generate_mock_results(intent: QueryIntent, entity_summary: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Generate mock results for demonstration."""
    import random
    from datetime import datetime, timedelta
    
    mock_results = []
    
    # Generate 5-15 mock results based on intent
    count = random.randint(5, 15)
    
    for i in range(count):
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        
        if intent in [QueryIntent.SHOW_FAILED_LOGINS, QueryIntent.SHOW_SUCCESSFUL_LOGINS]:
            username = "admin" if "username" in entity_summary else f"user{random.randint(1, 100)}"
            source_ip = "192.168.1.100" if "ip_address" in entity_summary else f"192.168.1.{random.randint(1, 254)}"
            
            result = {
                "@timestamp": timestamp.isoformat() + "Z",
                "user.name": username,
                "source.ip": source_ip,
                "host.name": f"server-{random.randint(1, 5)}",
                "winlog.event_id": "4625" if intent == QueryIntent.SHOW_FAILED_LOGINS else "4624",
                "event.outcome": "failure" if intent == QueryIntent.SHOW_FAILED_LOGINS else "success",
                "message": f"Authentication {'failed' if intent == QueryIntent.SHOW_FAILED_LOGINS else 'successful'} for user {username}"
            }
            
        elif intent == QueryIntent.SECURITY_ALERTS:
            result = {
                "@timestamp": timestamp.isoformat() + "Z",
                "event.type": "alert",
                "event.severity": random.randint(5, 10),
                "host.name": f"server-{random.randint(1, 5)}",
                "source.ip": f"10.0.0.{random.randint(1, 254)}",
                "message": f"Security alert: {random.choice(['Malware detected', 'Suspicious activity', 'Unauthorized access', 'Policy violation'])}",
                "tags": ["security", "alert"]
            }
            
        elif intent == QueryIntent.NETWORK_TRAFFIC:
            result = {
                "@timestamp": timestamp.isoformat() + "Z",
                "source.ip": f"192.168.1.{random.randint(1, 254)}",
                "destination.ip": f"10.0.0.{random.randint(1, 254)}",
                "source.port": random.randint(1024, 65535),
                "destination.port": random.choice([80, 443, 22, 3389, 21]),
                "network.protocol": random.choice(["tcp", "udp", "icmp"]),
                "network.bytes": random.randint(1024, 1048576),
                "message": "Network connection established"
            }
            
        elif intent == QueryIntent.SYSTEM_ERRORS:
            result = {
                "@timestamp": timestamp.isoformat() + "Z",
                "log.level": random.choice(["ERROR", "CRITICAL", "FATAL"]),
                "host.name": f"server-{random.randint(1, 5)}",
                "process.name": random.choice(["service.exe", "application.exe", "system.exe"]),
                "event.code": random.choice(["1000", "1001", "7034"]),
                "message": f"System error: {random.choice(['Service crashed', 'Application hang', 'Memory violation', 'Disk error'])}"
            }
            
        else:  # General search
            result = {
                "@timestamp": timestamp.isoformat() + "Z",
                "host.name": f"server-{random.randint(1, 5)}",
                "log.level": random.choice(["INFO", "WARN", "ERROR"]),
                "message": f"Log event {i+1}: {random.choice(['System event', 'User action', 'Network activity', 'Security event'])}",
                "source.ip": f"192.168.1.{random.randint(1, 254)}"
            }
        
        mock_results.append(result)
    
    return mock_results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)