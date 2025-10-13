"""
Conversational Assistant API
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
from .routes import assistant, query, reports, auth, admin, dashboard, websocket
from .routes.windows_data import router as windows_router
from .routes.platform_events import router as platform_events_router
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
    "multi_source_manager": None,
    "context_manager": None,
    "schema_mapper": None,
    "platform_service": None
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
        
        # Import settings for centralized configuration
        from src.core.config import settings
        from src.connectors.multi_source_manager import MultiSourceManager
        
        # Choose initialization strategy based on environment and available sources
        if settings.is_production:
            logger.info("🏢 PRODUCTION MODE: Initializing Multi-Source Manager for real data sources...")
            
            # In production, always try multi-source for real data sources
            multi_source_manager = MultiSourceManager(environment=settings.environment)
            try:
                success = await multi_source_manager.initialize()
                
                if success and multi_source_manager.sources:
                    app_state["multi_source_manager"] = multi_source_manager
                    
                    # Set primary connector for backward compatibility
                    sources = multi_source_manager.sources
                    primary_sources = [
                        (sid, conn) for sid, conn in sources.items()
                        if multi_source_manager.source_configs[sid].priority.value <= 2
                        and multi_source_manager.source_health[sid]
                    ]
                    
                    if primary_sources:
                        app_state["siem_connector"] = primary_sources[0][1]
                        logger.info(f"✅ PRODUCTION: Multi-source ready with {len(sources)} real data sources")
                    else:
                        app_state["siem_connector"] = list(sources.values())[0]
                        logger.info("✅ PRODUCTION: Multi-source ready with available sources")
                else:
                    raise RuntimeError("No real data sources available in production")
                    
            except Exception as e:
                logger.error(f"❌ PRODUCTION DEPLOYMENT FAILED: {e}")
                logger.error("❌ PRODUCTION REQUIREMENT: At least one real data source must be available:")
                logger.error("   - Elasticsearch (http://localhost:9200)")
                logger.error("   - Wazuh SIEM (http://localhost:55000)")
                logger.error("   - Splunk Enterprise")
                logger.error("❌ NO FALLBACKS ALLOWED IN PRODUCTION MODE")
                logger.error("❌ Dataset/demo data is DISABLED for security reasons")
                raise RuntimeError(f"PRODUCTION DEPLOYMENT BLOCKED: {e}")
                
        else:
            logger.info("🎭 DEMO MODE: Checking for real sources, fallback to dataset if needed...")
            
            # In demo mode, try multi-source first, fallback to single dataset
            multi_source_manager = MultiSourceManager(environment=settings.environment)
            
            try:
                success = await multi_source_manager.initialize()
                
                if success and multi_source_manager.sources:
                    # Check if we have real sources or just dataset
                    real_sources = [
                        sid for sid, config in multi_source_manager.source_configs.items()
                        if config.connector_type != "dataset"
                    ]
                    
                    if real_sources:
                        logger.info(f"✅ DEMO: Found real sources, using multi-source mode")
                        app_state["multi_source_manager"] = multi_source_manager
                        
                        # Set primary connector
                        sources = multi_source_manager.sources
                        primary_sources = [
                            (sid, conn) for sid, conn in sources.items()
                            if multi_source_manager.source_configs[sid].priority.value <= 2
                            and multi_source_manager.source_health[sid]
                        ]
                        
                        if primary_sources:
                            app_state["siem_connector"] = primary_sources[0][1]
                        else:
                            app_state["siem_connector"] = list(sources.values())[0]
                    else:
                        logger.info("✅ DEMO: Only dataset available, using single-source mode")
                        # Use single dataset connector
                        app_state["multi_source_manager"] = None
                        app_state["siem_connector"] = list(multi_source_manager.sources.values())[0]
                        await multi_source_manager.cleanup()  # Don't need multi-source for just dataset
                        
            except Exception as e:
                logger.warning(f"⚠️ DEMO: Multi-source failed: {e}, using single dataset fallback")
                app_state["multi_source_manager"] = None
        
        # Single source mode or fallback
        if not app_state.get("multi_source_manager"):
            logger.info("🎯 Initializing single data source...")
            
            data_source = settings.get_effective_data_source()
            logger.info(f"Using data source: {data_source}")
            
            # Create connector using factory with proper configuration
            try:
                app_state["siem_connector"] = create_connector(
                    platform=data_source,
                    environment=settings.environment,
                )
                logger.info(f"✅ Successfully initialized single data source: {data_source}")
            except Exception as e:
                logger.error(f"❌ Data source initialization failed: {e}")
                # Always fall back to dataset connector for reliability
                logger.info("📊 Falling back to dataset connector")
                app_state["siem_connector"] = create_connector(
                    platform="dataset",
                    environment=settings.environment
                )
        
        # Initialize context manager
        app_state["context_manager"] = ContextManager()
        logger.info("✅ Context manager initialized")
        
        # Initialize schema mapper
        app_state["schema_mapper"] = SchemaMapper()
        await app_state["schema_mapper"].initialize(app_state["siem_connector"])
        logger.info("✅ Schema mapper initialized")
        
        # Initialize platform-aware API service
        logger.info("🔧 Initializing Platform-Aware API Service...")
        from src.core.services.platform_aware_api import PlatformAwareAPIService
        
        # Use multi-source manager if available, otherwise create a dummy one for single source
        if app_state["multi_source_manager"]:
            app_state["platform_service"] = PlatformAwareAPIService(app_state["multi_source_manager"])
        else:
            # Create a wrapper for single source connector
            from src.connectors.multi_source_manager import MultiSourceManager
            single_source_wrapper = MultiSourceManager(environment=settings.environment)
            # Add the single source to the wrapper
            single_source_wrapper.sources = {"primary": app_state["siem_connector"]}
            single_source_wrapper.source_health = {"primary": True}
            single_source_wrapper.source_configs = {"primary": type('Config', (), {'priority': type('Priority', (), {'value': 1})()})()}
            app_state["platform_service"] = PlatformAwareAPIService(single_source_wrapper)
        
        # Initialize platform service
        await app_state["platform_service"].initialize()
        logger.info("✅ Platform-Aware API Service initialized")
        
        # Set the platform service in the route module
        from .routes.platform_events import set_platform_service
        set_platform_service(app_state["platform_service"])
        
        logger.info("✅ All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        # Continue running with limited functionality
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")
    if app_state["pipeline"]:
        await app_state["pipeline"].cleanup()
    if app_state["multi_source_manager"]:
        await app_state["multi_source_manager"].cleanup()
    elif app_state["siem_connector"]:
        if hasattr(app_state["siem_connector"], 'disconnect'):
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
app.include_router(platform_events_router, prefix="/api", tags=["Platform Events"])
app.include_router(windows_router, prefix="/api", tags=["Windows Data"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(websocket.router, tags=["WebSocket"])

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
            "multi_source_manager": app_state["multi_source_manager"] is not None,
            "context_manager": app_state["context_manager"] is not None,
            "schema_mapper": app_state["schema_mapper"] is not None,
            "platform_service": app_state["platform_service"] is not None
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
    """Dependency to get SIEM connector - returns None if not available"""
    return app_state["siem_connector"]

def get_context_manager():
    """Dependency to get context manager"""
    if not app_state["context_manager"]:
        raise HTTPException(status_code=503, detail="Context manager not initialized")
    return app_state["context_manager"]

def get_schema_mapper():
    """Dependency to get schema mapper - returns None if not available"""
    return app_state["schema_mapper"]

# Create a router instance for the main.py to export
from fastapi import APIRouter
router = APIRouter()

# Include all the routes in the router
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(assistant.router, prefix="/assistant", tags=["Assistant"])
router.include_router(query.router, prefix="/query", tags=["Query"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Export dependencies for use in routes
__all__ = [
    'app',
    'router',
    'get_pipeline',
    'get_siem_connector',
    'get_context_manager',
    'get_schema_mapper'
]
