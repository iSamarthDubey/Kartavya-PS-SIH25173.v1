#!/usr/bin/env python3
"""
Kartavya SIEM Assistant - Main Entry Point  
Start the backend server with: python main.py
"""

import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    import uvicorn
    from src.api.main import app
    
    # Get port from environment or use 8000 as default (FastAPI standard)
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"Starting Kartavya SIEM Assistant Backend...")
    print(f"API docs: http://localhost:{port}/api/docs")
    print(f"Chat endpoint: http://localhost:{port}/api/assistant/chat")
    print(f"Dashboard: http://localhost:{port}/api/dashboard")
    print(f"Health check: http://localhost:{port}/health")
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True
    )
