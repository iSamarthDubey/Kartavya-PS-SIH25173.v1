"""
Vercel-compatible entry point for Kartavya SIEM backend
This adapts your FastAPI app to work as Vercel serverless functions
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import your FastAPI app
try:
    from backend.src.api.main import app
except ImportError:
    # Fallback import structure
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))
    from api.main import app

# Set environment for Vercel
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("API_HOST", "0.0.0.0")
os.environ.setdefault("API_PORT", "3000")

# Configure app for Vercel
app.title = "Kartavya SIEM API"
app.description = "AI-Powered Security Information and Event Management API"
app.version = "1.0.0"

# Add a root endpoint for Vercel
@app.get("/")
async def vercel_root():
    """Vercel-specific root endpoint"""
    return {
        "service": "Kartavya SIEM API",
        "version": "1.0.0",
        "platform": "Vercel",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health", 
            "chat": "/api/assistant/chat",
            "events": "/api/events",
            "reports": "/api/reports",
            "dashboard": "/api/dashboard"
        }
    }

# Health check optimized for serverless
@app.get("/health")
async def serverless_health():
    """Lightweight health check for serverless"""
    return {
        "status": "healthy",
        "platform": "vercel",
        "serverless": True,
        "timestamp": "2024-01-15T12:00:00Z"
    }

# Export the app for Vercel
handler = app
