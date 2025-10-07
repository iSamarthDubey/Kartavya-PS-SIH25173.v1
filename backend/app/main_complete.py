"""
Kartavya SIEM Assistant - Main FastAPI Application
Production-ready version with all integrations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from app.api.v1.routes import router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Kartavya SIEM Assistant...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"Elasticsearch: {settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}")
    
    # Initialize connections
    from app.core.siem_complete import SIEMConnector
    connector = SIEMConnector()
    connected = await connector.check_connection()
    
    if connected:
        logger.info("✅ SIEM connection established")
    else:
        logger.warning("⚠️ SIEM connection failed - running in demo mode")
    
    yield
    
    logger.info("Shutting down Kartavya SIEM Assistant...")
    # Cleanup connections
    if hasattr(connector, 'close'):
        await connector.close()

# Create FastAPI app
app = FastAPI(
    title="Kartavya SIEM Assistant",
    description="NLP-powered SIEM investigation and reporting assistant for ISRO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.isro.gov.in"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["SIEM Assistant"])

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Kartavya SIEM Assistant",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "kartavya-siem",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True if settings.DEBUG else False,
        log_level="debug" if settings.DEBUG else "info"
    )
