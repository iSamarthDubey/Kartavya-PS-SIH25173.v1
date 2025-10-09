"""
Unified SIEM NLP Assistant API
Main FastAPI application combining all backend services
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import routers
from .routes import assistant, query, reports, auth, admin, dashboard
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
app_state = {
    "pipeline": None,
    "siem_connector": None,
    "context_manager": None,
    "schema_mapper": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚀 Starting SIEM NLP Assistant API...")
    
    try:
        # Import core modules
        from src.core.pipeline import ConversationalPipeline
        from src.connectors.factory import create_connector
        from src.core.context.manager import ContextManager
        from src.core.nlp.schema_mapper import SchemaMapper
        
        # Initialize components
        logger.info("Initializing core components...")
        
        # Initialize pipeline
        app_state["pipeline"] = ConversationalPipeline()
        await app_state["pipeline"].initialize()
        logger.info("✅ Pipeline initialized")
        
        # Initialize SIEM connector
        siem_platform = os.getenv("DEFAULT_SIEM_PLATFORM", "dataset")
        app_state["siem_connector"] = create_connector(siem_platform)
        # Actually connect to the datasets
        if hasattr(app_state["siem_connector"], 'initialize'):
            await app_state["siem_connector"].initialize()
        else:
            await app_state["siem_connector"].connect()
        logger.info(f"✅ {siem_platform} connector initialized")
        
        # Initialize context manager
        app_state["context_manager"] = ContextManager()
        logger.info("✅ Context manager initialized")
        
        # Initialize schema mapper
        app_state["schema_mapper"] = SchemaMapper()
        await app_state["schema_mapper"].initialize(app_state["siem_connector"])
        logger.info("✅ Schema mapper initialized")
        
        logger.info("✅ All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        # Continue running with limited functionality
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")
    if app_state["pipeline"]:
        await app_state["pipeline"].cleanup()
    if app_state["siem_connector"]:
        await app_state["siem_connector"].disconnect()

# Create FastAPI app
app = FastAPI(
    title="SIEM NLP Assistant API",
    description="Conversational interface for SIEM investigation and automated threat reporting",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8501",
        "https://kartavya-siem.vercel.app",
        "https://kartavya-siem-backend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "SIEM NLP Assistant",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/api/docs",
            "health": "/health",
            "chat": "/api/assistant/chat"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "pipeline": app_state["pipeline"] is not None,
            "siem_connector": app_state["siem_connector"] is not None,
            "context_manager": app_state["context_manager"] is not None,
            "schema_mapper": app_state["schema_mapper"] is not None
        }
    }
    
    # Calculate overall health
    services_ok = sum(health_status["services"].values())
    total_services = len(health_status["services"])
    
    if services_ok == total_services:
        health_status["health_score"] = "excellent"
    elif services_ok >= total_services * 0.75:
        health_status["health_score"] = "good"
    elif services_ok >= total_services * 0.5:
        health_status["health_score"] = "degraded"
    else:
        health_status["health_score"] = "critical"
    
    return health_status

# Ping endpoint for simple liveness check
@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"status": "pong", "timestamp": datetime.now().isoformat()}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "true" else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Error reporting endpoint for frontend ErrorBoundary
from fastapi import Body
@app.post("/api/errors")
async def report_error(error: dict = Body(...)):
    """Receive error reports from frontend"""
    logger.error(f"Frontend error reported: {error}")
    return {"status": "received", "timestamp": datetime.now().isoformat()}

# Make app state accessible to routes
@app.get("/api/state")
async def get_app_state():
    """Get current app state (for debugging)"""
    if os.getenv("DEBUG") != "true":
        raise HTTPException(status_code=403, detail="Debug mode not enabled")
    
    return {
        "pipeline": app_state["pipeline"] is not None,
        "siem_connector": app_state["siem_connector"] is not None,
        "context_manager": app_state["context_manager"] is not None,
        "schema_mapper": app_state["schema_mapper"] is not None
    }

def get_pipeline():
    """Dependency to get pipeline instance"""
    if not app_state["pipeline"]:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    return app_state["pipeline"]

def get_siem_connector():
    """Dependency to get SIEM connector"""
    if not app_state["siem_connector"]:
        raise HTTPException(status_code=503, detail="SIEM connector not initialized")
    return app_state["siem_connector"]

def get_context_manager():
    """Dependency to get context manager"""
    if not app_state["context_manager"]:
        raise HTTPException(status_code=503, detail="Context manager not initialized")
    return app_state["context_manager"]

def get_schema_mapper():
    """Dependency to get schema mapper"""
    if not app_state["schema_mapper"]:
        raise HTTPException(status_code=503, detail="Schema mapper not initialized")
    return app_state["schema_mapper"]

# Export dependencies for use in routes
__all__ = [
    'app',
    'get_pipeline',
    'get_siem_connector',
    'get_context_manager',
    'get_schema_mapper'
]
