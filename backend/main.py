"""
🚀 Kartavya SIEM Assistant - Main FastAPI Application
Dual-mode deployment: Demo (cloud) + Production (on-premise)
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime

# Import configuration and core modules
from src.core.config import settings, get_deployment_info
from src.core.database.clients import db_manager
from src.core.ai.hybrid_ai import hybrid_ai

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app with dynamic configuration
app = FastAPI(
    title="Kartavya SIEM Assistant", 
    description=f"Conversational SIEM Assistant - {settings.environment.upper()} Mode",
    version="1.0.0",
    docs_url="/docs" if settings.is_demo else None,  # Disable docs in production
    redoc_url="/redoc" if settings.is_demo else None
)

# Add security middleware
if not settings.is_demo:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1"]
    )

# Add CORS middleware with dynamic origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Import existing modules with fallback
try:
    from src.api.main import router as api_router
    from src.connectors.factory import SiemConnectorFactory
    from src.core.pipeline import SiemAssistantPipeline
    
    # Include existing API routes if available
    if api_router:
        app.include_router(api_router, prefix="/api/v1")
        logger.info("✅ Existing API routes included")
    
except ImportError as e:
    logger.warning(f"Some modules not available: {e}")
    api_router = None


# === PYDANTIC MODELS ===

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    siem_platform: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    intent: str
    entities: Dict[str, Any]
    siem_query: Dict[str, Any]
    results: Dict[str, Any]
    explanation: str
    timestamp: str
    session_id: str

class HealthResponse(BaseModel):
    status: str
    environment: str
    ai_enabled: bool
    databases: Dict[str, Any]
    version: str
    timestamp: str


# === STARTUP/SHUTDOWN EVENTS ===

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting Kartavya SIEM Assistant...")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"🤖 AI enabled: {settings.ai_enabled}")
    
    # Initialize databases
    await db_manager.initialize()
    
    # Log configuration status
    db_status = db_manager.get_status()
    ai_status = hybrid_ai.get_status()
    
    logger.info("✅ Kartavya SIEM Assistant started successfully!")


@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Kartavya SIEM Assistant...")


# === API ENDPOINTS ===

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with deployment info"""
    return {
        "message": "Kartavya SIEM Assistant API",
        "status": "online",
        "deployment": get_deployment_info(),
        "endpoints": {
            "health": "/health",
            "query": "/query", 
            "status": "/status",
            "docs": "/docs" if settings.is_demo else "disabled"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        ai_enabled=hybrid_ai.is_enabled,
        databases=db_manager.get_status(),
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/status", response_model=Dict[str, Any])
async def system_status():
    """Detailed system status"""
    return {
        "deployment": get_deployment_info(),
        "ai": hybrid_ai.get_status(),
        "databases": db_manager.get_status(),
        "configuration": {
            "cors_origins": settings.cors_origins_list,
            "rate_limit": settings.rate_limit_requests,
            "siem_platform": settings.default_siem_platform,
        }
    }


@app.post("/query", response_model=QueryResponse) 
async def process_query(request: QueryRequest):
    """Process natural language SIEM query"""
    try:
        session_id = request.session_id or f"session_{datetime.utcnow().timestamp()}"
        
        # Import NLP modules
        try:
            from src.core.nlp.intent_classifier import IntentClassifier
            from src.core.nlp.entity_extractor import EntityExtractor
            from rag_pipeline.pipeline import RAGPipeline
            
            # Initialize components
            intent_classifier = IntentClassifier()
            entity_extractor = EntityExtractor()
            rag_pipeline = RAGPipeline()
            
            # Process query
            logger.info(f"Processing query: {request.query}")
            
            # 1. Classify intent
            intent, confidence = intent_classifier.classify_intent(request.query)
            logger.info(f"Intent: {intent.value}, Confidence: {confidence:.2f}")
            
            # 2. Extract entities
            entities = entity_extractor.extract_entities(request.query)
            logger.info(f"Entities: {entities}")
            
            # 3. Get context from Redis
            context = await db_manager.redis.get_context(session_id)
            
            # 4. Generate SIEM query using RAG
            parsed_query = {
                'intent': intent.value,
                'entities': entities,
                'temporal': entities.get('temporal'),
                'filters': {}
            }
            
            platform = request.siem_platform or settings.default_siem_platform
            base_query = rag_pipeline.generate_query(parsed_query, platform)
            
            # 5. Enhance with AI if enabled
            enhanced_query = hybrid_ai.enhance_query(
                base_query, request.query, entities, context
            )
            
            # 6. Execute query (mock for now)
            results = {
                "total": 42,
                "events": [
                    {
                        "timestamp": "2025-01-08T10:30:00Z",
                        "event_type": "authentication_failure",
                        "source_ip": "192.168.1.100",
                        "severity": "high"
                    }
                ],
                "execution_time": 0.15
            }
            
            # 7. Generate explanation
            explanation = hybrid_ai.generate_explanation(request.query, results)
            
            # 8. Update context
            new_context = {
                **context,
                "last_query": request.query,
                "last_intent": intent.value,
                "last_entities": entities,
                "query_count": context.get("query_count", 0) + 1
            }
            await db_manager.redis.set_context(session_id, new_context)
            
            # 9. Log audit event
            await db_manager.supabase.log_audit_event({
                "event_type": "query_processed",
                "session_id": session_id,
                "query": request.query,
                "intent": intent.value,
                "platform": platform,
                "results_count": results["total"]
            })
            
            return QueryResponse(
                query=request.query,
                intent=intent.value,
                entities=entities,
                siem_query=enhanced_query,
                results=results,
                explanation=explanation,
                timestamp=datetime.utcnow().isoformat(),
                session_id=session_id
            )
            
        except ImportError as e:
            logger.error(f"NLP modules not available: {e}")
            raise HTTPException(
                status_code=500, 
                detail="NLP pipeline not initialized"
            )
    
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/datasets/stats")
async def dataset_stats():
    """Get dataset statistics"""
    if db_manager.mongodb.enabled:
        stats = await db_manager.mongodb.get_log_stats()
        return stats
    else:
        return {"message": "MongoDB not available in production mode"}


# === ERROR HANDLERS ===

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Path {request.url.path} not found",
            "available_endpoints": ["/", "/health", "/status", "/query"]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error", 
            "message": "An unexpected error occurred"
        }
    )


# === MAIN ===

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Kartavya SIEM Assistant...")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        workers=1 if settings.environment == "development" else settings.api_workers,
        access_log=True,
        log_level=settings.log_level.lower()
    )
