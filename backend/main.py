#!/usr/bin/env python3
"""
Kartavya SIEM Assistant - Main Entry Point
Run: python main.py

Enhancements:
- Secure logging with credential redaction (no API keys/tokens/passwords in logs)
- Port preflight checks and auto-free using Windows tools (and optional psutil)
- Clear startup banners and robust error handling
"""

from __future__ import annotations

import os
import sys
import logging

from dotenv import load_dotenv

# Import the core helpers we created
from src.core.security_filter import setup_secure_logging
from src.core.port_manager import setup_port_for_service

log = logging.getLogger("main")

if __name__ == "__main__":
    # Load environment
    load_dotenv()

    # Secure logging before importing app (to catch early logs that may include secrets)
    setup_secure_logging(os.getenv("LOG_LEVEL", "INFO"))

    # Read host/port config
    host = os.getenv("API_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("API_PORT", "8000"))
    except ValueError:
        port = 8000
        log.warning("Invalid API_PORT; defaulting to 8000")

    auto_kill = os.getenv("AUTO_KILL_PORT", "true").lower() in ("1", "true", "yes", "y")

    # Ensure the port is available (auto-kill if required)
    ok, final_port, message = setup_port_for_service(port, "Kartavya Backend", auto_kill=auto_kill)
    if not ok:
        log.error(message)
        sys.exit(2)

    # Print startup banner (no secrets)
    print("🚀 Starting Kartavya SIEM Assistant Backend...")
    print(f"📖 API docs: http://localhost:{final_port}/api/docs")
    print(f"💬 Chat: http://localhost:{final_port}/api/assistant/chat")
    print(f"❤️ Health: http://localhost:{final_port}/health")
    log.info(f"✅ Port {final_port} ready for service")

    # Run server
    try:
        import uvicorn
        # Importing app after logging/filter is configured to ensure redaction applies
        from src.api.main import app

        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=final_port,
            reload=True,
            log_level=os.getenv("UVICORN_LOG_LEVEL", os.getenv("LOG_LEVEL", "info")).lower(),
        )
    except Exception as e:
        log.exception(f"Failed to start server: {e}")
        sys.exit(1)
