#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kartavya SIEM Assistant - Quick Start Demo Script
Launches the complete platform for demonstration
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

class DemoLauncher:
    def __init__(self):
        self.base = Path(".")
        self.backend_process = None
        self.frontend_process = None
        
    def print_banner(self):
        """Print startup banner"""
        print("\n" + "="*80)
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     KARTAVYA SIEM ASSISTANT                              ║
║                  Enterprise Security Platform for ISRO                   ║
║                        Problem Statement: SIH25173                       ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)
        print("="*80 + "\n")
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python packages
        try:
            import fastapi
            import uvicorn
            print("  ✅ FastAPI installed")
        except ImportError:
            print("  ⚠️ Installing FastAPI...")
            subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "pydantic-settings", "python-dotenv"], check=True)
            
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Node.js installed ({result.stdout.strip()})")
        except:
            print("  ❌ Node.js not found. Please install from https://nodejs.org")
            return False
            
        return True
        
    def start_backend(self):
        """Start the backend server"""
        print("\n🚀 Starting Backend Server...")
        
        # Create minimal backend if main.py doesn't exist
        backend_main = self.base / "backend" / "app" / "main.py"
        if not backend_main.exists():
            self.create_minimal_backend()
            
        # Start backend
        os.chdir("backend")
        self.backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        os.chdir("..")
        
        time.sleep(3)  # Give backend time to start
        print("  ✅ Backend running at http://localhost:8001")
        print("  📖 API Docs at http://localhost:8001/docs")
        
    def start_frontend(self):
        """Start the frontend server"""
        print("\n🎨 Starting Frontend...")
        
        frontend_path = self.base / "frontend"
        
        # Check if node_modules exists
        if not (frontend_path / "node_modules").exists():
            print("  📦 Installing frontend dependencies...")
            os.chdir("frontend")
            subprocess.run(["npm", "install"], check=True)
            os.chdir("..")
            
        # Start frontend
        os.chdir("frontend")
        self.frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        os.chdir("..")
        
        time.sleep(5)  # Give frontend time to start
        print("  ✅ Frontend running at http://localhost:5173")
        
    def create_minimal_backend(self):
        """Create a minimal working backend"""
        print("  📝 Creating minimal backend...")
        
        # Ensure directories exist
        (self.base / "backend" / "app" / "core").mkdir(parents=True, exist_ok=True)
        (self.base / "backend" / "app" / "api" / "v1").mkdir(parents=True, exist_ok=True)
        (self.base / "backend" / "app" / "models").mkdir(parents=True, exist_ok=True)
        
        # Create minimal main.py
        main_code = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

app = FastAPI(title="Kartavya SIEM Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Kartavya SIEM Assistant",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "service": "kartavya-siem"}

@app.post("/api/v1/query")
async def query(request: dict):
    # Mock response for demo
    events = []
    for i in range(10):
        events.append({
            "id": f"EVT-{i:04d}",
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": random.choice(["Failed Login", "Port Scan", "Malware Detected"]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "source_ip": f"10.0.0.{random.randint(1,254)}"
        })
    
    return {
        "success": True,
        "query": request.get("query", ""),
        "intent": "search_logs",
        "entities": [],
        "results": {"events": events, "total": len(events)},
        "summary": f"Found {len(events)} security events",
        "charts": []
    }

@app.get("/api/v1/suggestions")
async def suggestions():
    return {
        "suggestions": [
            {"category": "Authentication", "queries": ["Show failed logins"]},
            {"category": "Threats", "queries": ["Detect malware"]}
        ]
    }

@app.get("/api/v1/stats")
async def stats():
    return {
        "total_events_24h": random.randint(1000, 5000),
        "critical_alerts": random.randint(0, 10),
        "active_threats": random.randint(0, 5),
        "systems_monitored": random.randint(50, 200)
    }
'''
        
        main_path = self.base / "backend" / "app" / "main.py"
        main_path.write_text(main_code, encoding='utf-8')
        
        # Create __init__ files
        for dir_path in ["backend/app", "backend/app/core", "backend/app/api"]:
            init_path = Path(dir_path) / "__init__.py"
            if not init_path.exists():
                init_path.touch()
                
    def launch_browser(self):
        """Open the application in browser"""
        print("\n🌐 Launching browser...")
        time.sleep(2)
        
        # Open API docs first
        webbrowser.open("http://localhost:8001/docs")
        
        # Then open frontend
        time.sleep(1)
        webbrowser.open("http://localhost:5173")
        
        print("  ✅ Opened in browser")
        
    def run(self):
        """Run the complete demo"""
        self.print_banner()
        
        if not self.check_dependencies():
            print("\n❌ Please install required dependencies and try again.")
            return
            
        try:
            self.start_backend()
            self.start_frontend()
            self.launch_browser()
            
            print("\n" + "="*80)
            print("✨ KARTAVYA SIEM ASSISTANT IS RUNNING!")
            print("="*80)
            print("\n📍 Access Points:")
            print("  • Frontend: http://localhost:5173")
            print("  • Backend API: http://localhost:8001")
            print("  • API Documentation: http://localhost:8001/docs")
            print("\n⌨️ Press Ctrl+C to stop all services\n")
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down services...")
            if self.backend_process:
                self.backend_process.terminate()
            if self.frontend_process:
                self.frontend_process.terminate()
            print("✅ All services stopped")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please check the logs and try again.")

if __name__ == "__main__":
    launcher = DemoLauncher()
    launcher.run()
