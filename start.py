#!/usr/bin/env python3
"""
SIEM NLP Assistant - Application Launcher
Main startup script for the restructured application
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import signal
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AppLauncher:
    def __init__(self):
        self.processes = []
        self.backend_port = int(os.getenv("BACKEND_PORT", 8000))
        self.frontend_port = int(os.getenv("FRONTEND_PORT", 5173))
        
    def check_requirements(self) -> bool:
        """Check if all requirements are installed"""
        required_python = ["fastapi", "uvicorn", "spacy", "elasticsearch", "pydantic"]
        missing = []
        
        logger.info("Checking Python dependencies...")
        for req in required_python:
            try:
                __import__(req)
                logger.info(f"✓ {req} installed")
            except ImportError:
                missing.append(req)
                logger.error(f"✗ {req} missing")
        
        if missing:
            logger.error(f"Missing packages: {', '.join(missing)}")
            logger.info("Run: pip install -r requirements.txt")
            return False
        
        # Check if spaCy model is installed
        try:
            import spacy
            spacy.load("en_core_web_sm")
            logger.info("✓ spaCy model 'en_core_web_sm' installed")
        except:
            logger.warning("✗ spaCy model not installed")
            logger.info("Run: python -m spacy download en_core_web_sm")
        
        return True
    
    def check_services(self) -> dict:
        """Check which services are available"""
        services = {
            "elasticsearch": False,
            "redis": False,
            "postgresql": False
        }
        
        # Check Elasticsearch
        try:
            import requests
            response = requests.get("http://localhost:9200", timeout=2)
            if response.status_code == 200:
                services["elasticsearch"] = True
                logger.info("✓ Elasticsearch is running")
        except:
            logger.warning("✗ Elasticsearch not available (will use mock data)")
        
        return services
    
    def start_backend(self):
        """Start the FastAPI backend"""
        logger.info(f"Starting backend server on port {self.backend_port}...")
        
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--host", "0.0.0.0",
            "--port", str(self.backend_port),
            "--reload"
        ]
        
        process = subprocess.Popen(cmd)
        self.processes.append(process)
        logger.info(f"✓ Backend started (PID: {process.pid})")
        return process
    
    def start_frontend(self):
        """Start the React frontend"""
        web_dir = Path("web")
        
        if not web_dir.exists():
            logger.warning("Frontend directory not found. Skipping frontend.")
            return None
        
        # Check if package.json exists
        if not (web_dir / "package.json").exists():
            logger.warning("Frontend not configured. Skipping.")
            return None
        
        logger.info(f"Starting frontend on port {self.frontend_port}...")
        
        # Check if node_modules exists
        if not (web_dir / "node_modules").exists():
            logger.info("Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=web_dir, check=True)
        
        cmd = ["npm", "run", "dev"]
        process = subprocess.Popen(cmd, cwd=web_dir)
        self.processes.append(process)
        logger.info(f"✓ Frontend started (PID: {process.pid})")
        return process
    
    def wait_for_backend(self, timeout=30):
        """Wait for backend to be ready"""
        import requests
        
        logger.info("Waiting for backend to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{self.backend_port}/health")
                if response.status_code == 200:
                    logger.info("✓ Backend is ready!")
                    return True
            except:
                pass
            time.sleep(1)
        
        logger.error("Backend failed to start within timeout")
        return False
    
    def cleanup(self):
        """Clean up all processes"""
        logger.info("Shutting down services...")
        for process in self.processes:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        logger.info("✓ All services stopped")
    
    def run(self):
        """Main run method"""
        print("=" * 60)
        print("  SIEM NLP Assistant - Starting Services")
        print("=" * 60)
        
        # Check requirements
        if not self.check_requirements():
            logger.error("Missing requirements. Please install them first.")
            sys.exit(1)
        
        # Check available services
        services = self.check_services()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: self.cleanup())
        signal.signal(signal.SIGTERM, lambda s, f: self.cleanup())
        
        try:
            # Start backend
            backend = self.start_backend()
            
            # Wait for backend to be ready
            if self.wait_for_backend():
                # Start frontend
                frontend = self.start_frontend()
            
            print("\n" + "=" * 60)
            print("✅ All services started successfully!")
            print("=" * 60)
            print(f"📍 Backend API: http://localhost:{self.backend_port}")
            print(f"📚 API Docs: http://localhost:{self.backend_port}/api/docs")
            if frontend:
                print(f"📍 Frontend: http://localhost:{self.frontend_port}")
            print("\nPress Ctrl+C to stop all services...")
            print("=" * 60)
            
            # Wait for processes
            for process in self.processes:
                if process:
                    process.wait()
                    
        except KeyboardInterrupt:
            logger.info("\nReceived interrupt signal...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    launcher = AppLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
