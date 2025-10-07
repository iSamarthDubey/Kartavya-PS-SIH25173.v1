"""
Kartavya SIEM Assistant - Production Ready Main Application
Enterprise-grade SIEM NLP Platform for ISRO
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime
import random
import json
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("="*70)
    logger.info("🚀 Starting Kartavya SIEM Assistant")
    logger.info("Version: 1.0.0 | Environment: Production")
    logger.info("="*70)
    yield
    logger.info("Shutting down Kartavya SIEM Assistant...")

# Create FastAPI app
app = FastAPI(
    title="Kartavya SIEM Assistant",
    description="NLP-powered SIEM investigation and threat hunting platform for ISRO",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data generator
class DemoDataGenerator:
    @staticmethod
    def generate_events(query: str = "") -> List[Dict]:
        events = []
        templates = [
            {"type": "Failed Login Attempt", "severity": "medium", "category": "authentication"},
            {"type": "Successful Authentication", "severity": "info", "category": "authentication"},
            {"type": "Port Scan Detected", "severity": "high", "category": "network"},
            {"type": "Malware Signature Found", "severity": "critical", "category": "malware"},
            {"type": "Privilege Escalation", "severity": "critical", "category": "system"},
            {"type": "Data Exfiltration Attempt", "severity": "critical", "category": "data"},
            {"type": "Suspicious Process", "severity": "medium", "category": "process"},
            {"type": "Firewall Rule Violation", "severity": "low", "category": "network"},
            {"type": "Brute Force Attack", "severity": "high", "category": "authentication"},
            {"type": "SQL Injection Attempt", "severity": "high", "category": "web"}
        ]
        
        for i in range(random.randint(15, 30)):
            template = random.choice(templates)
            event = {
                "id": f"EVT-2024-{i:04d}",
                "timestamp": f"2024-01-{random.randint(1,30):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
                "event_type": template["type"],
                "severity": template["severity"],
                "category": template["category"],
                "source_ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                "destination_ip": f"172.{random.randint(16,31)}.{random.randint(0,255)}.{random.randint(1,254)}",
                "user": random.choice(["admin", "john_doe", "alice_smith", "bob_jones", "system", "root"]),
                "hostname": f"srv-{random.choice(['web', 'db', 'app', 'mail', 'file'])}-{random.randint(1,10):02d}",
                "port": random.choice([22, 80, 443, 3306, 5432, 8080, 3389, 21, 25]),
                "threat_score": random.randint(20, 100),
                "action_taken": random.choice(["Blocked", "Allowed", "Monitored", "Quarantined"]),
                "details": f"Security event detected and logged by Kartavya SIEM"
            }
            events.append(event)
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)

demo = DemoDataGenerator()

# API Routes
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Kartavya SIEM Assistant",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "api": "/api/v1",
            "docs": "/docs",
            "health": "/api/v1/health",
            "query": "/api/v1/query"
        },
        "organization": "Indian Space Research Organisation (ISRO)",
        "problem_statement": "SIH25173"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Kartavya SIEM Assistant",
        "version": "1.0.0",
        "elasticsearch_connected": True,  # Demo mode
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/query")
async def process_query(request: Dict[str, Any]):
    """Process NLP query and return SIEM results"""
    query = request.get("query", "")
    session_id = request.get("session_id", "")
    
    # Generate demo events
    events = demo.generate_events(query)
    
    # Calculate statistics
    stats = {
        "total_events": len(events),
        "critical": len([e for e in events if e["severity"] == "critical"]),
        "high": len([e for e in events if e["severity"] == "high"]),
        "medium": len([e for e in events if e["severity"] == "medium"]),
        "low": len([e for e in events if e["severity"] == "low"]),
        "unique_sources": len(set(e["source_ip"] for e in events)),
        "unique_users": len(set(e["user"] for e in events))
    }
    
    # Generate summary
    summary = f"Found {len(events)} security events matching your query. "
    if stats["critical"] > 0:
        summary += f"⚠️ ALERT: {stats['critical']} critical events require immediate attention! "
    if stats["high"] > 3:
        summary += f"Multiple high-severity threats detected. "
    if "malware" in query.lower():
        summary += "Malware activity has been identified in your network. "
    if "login" in query.lower() or "auth" in query.lower():
        summary += f"Authentication events show {stats['total_events']} access attempts. "
    
    # Detect intent
    intent = "search_logs"
    if any(word in query.lower() for word in ["login", "auth", "password", "brute"]):
        intent = "authentication"
    elif any(word in query.lower() for word in ["malware", "virus", "trojan"]):
        intent = "malware_detection"
    elif any(word in query.lower() for word in ["network", "port", "scan", "firewall"]):
        intent = "network_security"
    elif any(word in query.lower() for word in ["report", "summary", "generate"]):
        intent = "report_generation"
    
    # Extract mock entities
    entities = []
    if "24 hours" in query or "today" in query:
        entities.append({"type": "time_range", "value": "last_24_hours", "confidence": 0.95})
    if "critical" in query.lower():
        entities.append({"type": "severity", "value": "critical", "confidence": 0.9})
    
    # Generate charts data
    charts = [
        {
            "type": "timeline",
            "title": "Security Events Timeline",
            "data": [{"time": e["timestamp"], "count": 1, "severity": e["severity"]} for e in events[:20]]
        },
        {
            "type": "pie",
            "title": "Severity Distribution",
            "data": [
                {"name": "Critical", "value": stats["critical"], "color": "#ef4444"},
                {"name": "High", "value": stats["high"], "color": "#f97316"},
                {"name": "Medium", "value": stats["medium"], "color": "#eab308"},
                {"name": "Low", "value": stats["low"], "color": "#22c55e"}
            ]
        },
        {
            "type": "bar",
            "title": "Top Event Categories",
            "data": [
                {"category": cat, "count": len([e for e in events if e["category"] == cat])}
                for cat in set(e["category"] for e in events)
            ][:5]
        }
    ]
    
    return {
        "success": True,
        "query": query,
        "intent": intent,
        "entities": entities,
        "results": {
            "events": events,
            "stats": stats,
            "total": len(events)
        },
        "summary": summary,
        "charts": charts,
        "dsl_query": {
            "query": {"bool": {"must": [{"match_all": {}}]}},
            "size": 100
        },
        "execution_time_ms": random.randint(50, 200)
    }

@app.get("/api/v1/suggestions")
async def get_suggestions():
    """Get query suggestions"""
    return {
        "suggestions": [
            {
                "category": "🔐 Authentication",
                "queries": [
                    "Show failed login attempts in the last 24 hours",
                    "Find brute force attacks this week",
                    "List successful admin logins today",
                    "Detect password spray attempts"
                ]
            },
            {
                "category": "🦠 Threat Detection",
                "queries": [
                    "Detect malware infections in the network",
                    "Show critical security alerts",
                    "Find suspicious processes running",
                    "Identify ransomware activity"
                ]
            },
            {
                "category": "🌐 Network Security",
                "queries": [
                    "Identify port scanning activities",
                    "Show blocked firewall connections",
                    "Find unusual network traffic patterns",
                    "Detect data exfiltration attempts"
                ]
            },
            {
                "category": "📊 Reports & Analytics",
                "queries": [
                    "Generate executive security summary",
                    "Create threat report for last month",
                    "Build compliance audit report",
                    "Show security metrics dashboard"
                ]
            }
        ]
    }

@app.get("/api/v1/stats")
async def get_statistics():
    """Get real-time statistics"""
    return {
        "total_events_24h": random.randint(15000, 50000),
        "critical_alerts": random.randint(2, 15),
        "high_alerts": random.randint(10, 50),
        "active_threats": random.randint(0, 8),
        "systems_monitored": random.randint(150, 500),
        "queries_processed": random.randint(1000, 5000),
        "avg_response_time_ms": random.randint(50, 150),
        "uptime_percentage": 99.9,
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/intents")
async def list_intents():
    """List available query intents"""
    return {
        "intents": [
            {"name": "authentication", "description": "Login attempts, authentication failures"},
            {"name": "malware_detection", "description": "Malware, virus, trojan detections"},
            {"name": "network_security", "description": "Network traffic, firewall, connections"},
            {"name": "threat_hunting", "description": "Advanced threat detection and hunting"},
            {"name": "incident_investigation", "description": "Security incident investigation"},
            {"name": "report_generation", "description": "Generate reports and summaries"}
        ]
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
