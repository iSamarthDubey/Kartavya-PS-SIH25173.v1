#!/usr/bin/env python3
"""
Repository Restructuring Script for Kartavya SIEM Assistant
This script will help reorganize the repository to a clean, professional structure.
"""

import os
import shutil
from pathlib import Path
import json
import yaml

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def create_directory_structure():
    """Create the new clean directory structure"""
    print_header("Creating New Directory Structure")
    
    directories = [
        # Core source directories
        "src/api",
        "src/api/routes",
        "src/api/middleware",
        "src/core/nlp",
        "src/core/query",
        "src/core/context",
        "src/core/reporting",
        "src/connectors",
        "src/security",
        "src/utils",
        
        # Web frontend
        "web/src/components",
        "web/src/pages",
        "web/src/services",
        "web/src/store",
        "web/src/hooks",
        "web/src/types",
        
        # Configuration
        "config",
        
        # Data directories
        "data/models",
        "data/datasets",
        "data/schemas",
        
        # Documentation
        "docs",
        
        # Keep existing test structure
        "tests/unit",
        "tests/integration",
        "tests/e2e",
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")
    
    # Create __init__.py files for Python packages
    python_dirs = [d for d in directories if d.startswith("src/")]
    for dir_path in python_dirs:
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    print("\n✅ Directory structure created successfully!")

def move_and_consolidate_files():
    """Move and consolidate files to new structure"""
    print_header("Consolidating Files")
    
    migrations = {
        # Backend consolidation
        "backend/nlp/intent_classifier.py": "src/core/nlp/intent_classifier.py",
        "backend/nlp/entity_extractor.py": "src/core/nlp/entity_extractor.py",
        "backend/query_builder.py": "src/core/query/builder.py",
        "backend/response_formatter/formatter.py": "src/core/reporting/formatter.py",
        "backend/response_formatter/chart_formatter.py": "src/core/reporting/visualizer.py",
        
        # Assistant module consolidation
        "assistant/context_manager.py": "src/core/context/manager.py",
        "assistant/pipeline.py": "src/core/pipeline.py",
        "assistant/router.py": "src/api/routes/assistant.py",
        
        # SIEM Connectors
        "siem_connector/elastic_connector.py": "src/connectors/elastic.py",
        "siem_connector/wazuh_connector.py": "src/connectors/wazuh.py",
        "siem_connector/utils.py": "src/connectors/utils.py",
        
        # Security modules - already in good location
        "src/security/auth_manager.py": "src/security/auth.py",
        "src/security/rbac.py": "src/security/rbac.py",
        "src/security/audit_logger.py": "src/security/audit.py",
        "src/security/rate_limiter.py": "src/security/rate_limiter.py",
        "src/security/sanitizer.py": "src/security/sanitizer.py",
        
        # Configuration files
        "config/index_mappings.yaml": "config/schema_mappings.yaml",
        "config/security_users.json": "config/security_policies.yaml",
        
        # Frontend files (choosing React over Streamlit)
        "frontend/src/App.tsx": "web/src/App.tsx",
        "frontend/src/components/": "web/src/components/",
        "frontend/src/pages/": "web/src/pages/",
        "frontend/src/services/": "web/src/services/",
        "frontend/src/store/": "web/src/store/",
        "frontend/package.json": "web/package.json",
        "frontend/vite.config.ts": "web/vite.config.ts",
        "frontend/tsconfig.json": "web/tsconfig.json",
        "frontend/tailwind.config.js": "web/tailwind.config.js",
        "frontend/postcss.config.js": "web/postcss.config.js",
    }
    
    for src, dst in migrations.items():
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            if src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                print(f"📁 Moved directory: {src} → {dst}")
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                print(f"📄 Moved file: {src} → {dst}")
    
    print("\n✅ Files consolidated successfully!")

def create_unified_api():
    """Create the unified API main.py file"""
    print_header("Creating Unified API")
    
    api_content = '''"""
Unified SIEM NLP Assistant API
Combines all backend services into a single FastAPI application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Import routes
from .routes import assistant, query, reports, admin
from ..core import pipeline
from ..connectors import elastic, wazuh
from ..security import auth, rbac, rate_limiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
app_pipeline = None
siem_connector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global app_pipeline, siem_connector
    
    logger.info("🚀 Starting SIEM NLP Assistant...")
    
    # Initialize pipeline
    app_pipeline = pipeline.ConversationalPipeline()
    await app_pipeline.initialize()
    
    # Initialize SIEM connector
    siem_platform = os.getenv("SIEM_PLATFORM", "elasticsearch")
    if siem_platform == "elasticsearch":
        siem_connector = elastic.ElasticConnector()
    else:
        siem_connector = wazuh.WazuhConnector()
    
    logger.info("✅ All services initialized successfully!")
    
    yield
    
    logger.info("Shutting down services...")

# Create FastAPI app
app = FastAPI(
    title="SIEM NLP Assistant API",
    description="Conversational interface for SIEM investigation and reporting",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.add_middleware(rate_limiter.RateLimitMiddleware)

# Include routers
app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SIEM NLP Assistant",
        "version": "2.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "pipeline": app_pipeline is not None,
            "siem_connector": siem_connector is not None
        }
    }
'''
    
    api_file = Path("src/api/main.py")
    api_file.write_text(api_content)
    print(f"✅ Created unified API: {api_file}")

def create_missing_modules():
    """Create missing but required modules"""
    print_header("Creating Missing Modules")
    
    # Schema Mapper
    schema_mapper = '''"""
Schema Mapper - Maps natural language terms to SIEM field names
"""

from typing import Dict, List, Optional
import yaml
from pathlib import Path

class SchemaMapper:
    """Maps natural language entities to SIEM schema fields"""
    
    def __init__(self, mapping_file: str = "config/schema_mappings.yaml"):
        self.mappings = self._load_mappings(mapping_file)
        self.field_cache = {}
    
    def _load_mappings(self, file_path: str) -> Dict:
        """Load schema mappings from YAML file"""
        path = Path(file_path)
        if path.exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        return self._default_mappings()
    
    def _default_mappings(self) -> Dict:
        """Default field mappings for common SIEM schemas"""
        return {
            "user": ["user.name", "source.user.name", "winlog.event_data.TargetUserName"],
            "ip": ["source.ip", "destination.ip", "client.ip", "server.ip"],
            "host": ["host.name", "hostname", "computer_name"],
            "failed_login": ["event.action:login_failed", "winlog.event_id:4625"],
            "malware": ["event.category:malware", "threat.name:*"],
            "vpn": ["network.protocol:vpn", "service.name:vpn"],
        }
    
    def map_entity_to_field(self, entity: str, entity_type: str) -> List[str]:
        """Map a natural language entity to SIEM field names"""
        key = f"{entity_type}:{entity}" if entity_type else entity
        
        if key in self.field_cache:
            return self.field_cache[key]
        
        # Check direct mappings
        fields = self.mappings.get(entity.lower(), [])
        
        if not fields and entity_type:
            fields = self.mappings.get(entity_type.lower(), [])
        
        self.field_cache[key] = fields
        return fields
    
    async def discover_schema(self, connector) -> Dict:
        """Discover schema from live SIEM"""
        try:
            mappings = await connector.get_field_mappings()
            # Process and cache discovered mappings
            return mappings
        except Exception as e:
            print(f"Schema discovery failed: {e}")
            return {}
'''
    
    Path("src/core/nlp/schema_mapper.py").write_text(schema_mapper)
    print("✅ Created SchemaMapper module")
    
    # Query Validator
    query_validator = '''"""
Query Validator - Validates and sanitizes SIEM queries for safety
"""

from typing import Dict, Tuple, List
import re

class QueryValidator:
    """Validates queries for safety and performance"""
    
    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r'\\*:\\*',  # Wildcard everything
        r'DELETE|DROP|TRUNCATE',  # Destructive operations
        r'size"?\\s*:\\s*[0-9]{5,}',  # Extremely large result sets
    ]
    
    # Performance thresholds
    MAX_SIZE = 10000
    MAX_AGGREGATION_BUCKETS = 1000
    MAX_TIME_RANGE_DAYS = 365
    
    def validate(self, query: Dict) -> Tuple[bool, str]:
        """
        Validate a query for safety and performance
        Returns (is_valid, error_message)
        """
        # Check for dangerous patterns
        query_str = str(query)
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query_str, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check size limits
        size = query.get("size", 0)
        if size > self.MAX_SIZE:
            return False, f"Result size {size} exceeds maximum {self.MAX_SIZE}"
        
        # Check aggregation limits
        if "aggs" in query or "aggregations" in query:
            if not self._validate_aggregations(query.get("aggs", query.get("aggregations", {}))):
                return False, "Aggregation too complex or exceeds bucket limit"
        
        return True, ""
    
    def _validate_aggregations(self, aggs: Dict, depth: int = 0) -> bool:
        """Validate aggregation complexity"""
        if depth > 3:  # Max nesting depth
            return False
        
        for key, value in aggs.items():
            if isinstance(value, dict):
                # Check bucket size
                if "size" in value and value["size"] > self.MAX_AGGREGATION_BUCKETS:
                    return False
                
                # Recursive check for nested aggregations
                if "aggs" in value or "aggregations" in value:
                    nested = value.get("aggs", value.get("aggregations", {}))
                    if not self._validate_aggregations(nested, depth + 1):
                        return False
        
        return True
    
    def add_safety_limits(self, query: Dict) -> Dict:
        """Add safety limits to a query"""
        # Add size limit if not specified
        if "size" not in query:
            query["size"] = 100
        
        # Add timeout
        if "timeout" not in query:
            query["timeout"] = "30s"
        
        # Add terminate_after for safety
        if "terminate_after" not in query:
            query["terminate_after"] = 100000
        
        return query
'''
    
    Path("src/core/query/validator.py").write_text(query_validator)
    print("✅ Created QueryValidator module")
    
    # Ambiguity Resolver
    ambiguity_resolver = '''"""
Ambiguity Resolver - Handles unclear queries and requests clarification
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re

class AmbiguityResolver:
    """Resolves ambiguous queries by requesting clarification"""
    
    def __init__(self):
        self.ambiguous_terms = {
            "recent": ["last hour", "last 24 hours", "last week", "last month"],
            "unusual": ["anomalous count", "new source IP", "outside business hours", "high severity"],
            "suspicious": ["failed authentication", "malware detected", "privilege escalation", "data exfiltration"],
            "last week": ["past 7 days", "previous calendar week", "ISO week"],
        }
    
    def detect_ambiguity(self, query: str, entities: Dict) -> Tuple[bool, List[str]]:
        """
        Detect if query contains ambiguous terms
        Returns (has_ambiguity, list_of_ambiguous_terms)
        """
        ambiguous = []
        query_lower = query.lower()
        
        # Check for ambiguous temporal references
        temporal_patterns = [
            r'\\b(recent|recently|lately)\\b',
            r'\\b(last week|previous week)\\b',
            r'\\b(unusual|abnormal|strange)\\b',
            r'\\b(suspicious|suspect)\\b',
        ]
        
        for pattern in temporal_patterns:
            if re.search(pattern, query_lower):
                match = re.search(pattern, query_lower).group()
                if match in self.ambiguous_terms:
                    ambiguous.append(match)
        
        # Check for missing required context
        if "show" in query_lower or "get" in query_lower:
            if not entities.get("time_range") and "all" not in query_lower:
                ambiguous.append("time_range_not_specified")
        
        return len(ambiguous) > 0, ambiguous
    
    def get_clarification_options(self, ambiguous_term: str) -> List[str]:
        """Get clarification options for an ambiguous term"""
        return self.ambiguous_terms.get(ambiguous_term, [])
    
    def resolve_temporal_ambiguity(self, term: str, choice: str) -> Dict:
        """Resolve temporal ambiguity to concrete time range"""
        now = datetime.now()
        
        resolutions = {
            "last hour": {"gte": "now-1h", "lte": "now"},
            "last 24 hours": {"gte": "now-24h", "lte": "now"},
            "last week": {"gte": "now-7d", "lte": "now"},
            "last month": {"gte": "now-30d", "lte": "now"},
            "past 7 days": {"gte": "now-7d", "lte": "now"},
            "previous calendar week": self._get_previous_calendar_week(),
        }
        
        return resolutions.get(choice, {"gte": "now-24h", "lte": "now"})
    
    def _get_previous_calendar_week(self) -> Dict:
        """Get the previous calendar week range"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=6)
        return {
            "gte": start_of_week.isoformat(),
            "lte": end_of_week.isoformat()
        }
    
    def generate_clarification_response(self, ambiguous_terms: List[str]) -> Dict:
        """Generate a clarification request response"""
        clarifications = {}
        
        for term in ambiguous_terms:
            options = self.get_clarification_options(term)
            if options:
                clarifications[term] = {
                    "question": f"What do you mean by '{term}'?",
                    "options": options
                }
        
        return {
            "needs_clarification": True,
            "message": "Your query contains some ambiguous terms. Please clarify:",
            "clarifications": clarifications
        }
'''
    
    Path("src/core/nlp/ambiguity_resolver.py").write_text(ambiguity_resolver)
    print("✅ Created AmbiguityResolver module")

def create_config_files():
    """Create configuration files"""
    print_header("Creating Configuration Files")
    
    # Settings YAML
    settings = {
        "app": {
            "name": "SIEM NLP Assistant",
            "version": "2.0.0",
            "debug": False
        },
        "siem": {
            "platform": "elasticsearch",
            "host": "localhost",
            "port": 9200,
            "index": "security-logs",
            "timeout": 30,
            "max_results": 1000
        },
        "nlp": {
            "model": "en_core_web_sm",
            "confidence_threshold": 0.7,
            "max_entities": 10
        },
        "security": {
            "jwt_secret": "change-this-in-production",
            "jwt_algorithm": "HS256",
            "jwt_expiry_minutes": 60,
            "rate_limit": 100,
            "rate_window": 60
        },
        "features": {
            "multi_turn_context": True,
            "query_validation": True,
            "ambiguity_resolution": True,
            "report_generation": True,
            "export_enabled": True
        }
    }
    
    with open("config/settings.yaml", "w") as f:
        yaml.dump(settings, f, default_flow_style=False)
    print("✅ Created settings.yaml")
    
    # Query Templates
    templates = {
        "failed_logins": {
            "description": "Query for failed login attempts",
            "query": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"event.action": "login_failed"}},
                            {"range": {"@timestamp": {"gte": "now-24h"}}}
                        ]
                    }
                }
            }
        },
        "malware_detection": {
            "description": "Query for malware detections",
            "query": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"event.category": "malware"}}
                        ]
                    }
                }
            }
        },
        "vpn_activity": {
            "description": "Query for VPN activity",
            "query": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"service.name": "vpn"}}
                        ]
                    }
                }
            }
        }
    }
    
    with open("config/query_templates.yaml", "w") as f:
        yaml.dump(templates, f, default_flow_style=False)
    print("✅ Created query_templates.yaml")

def create_documentation():
    """Create documentation files"""
    print_header("Creating Documentation")
    
    # Architecture documentation
    arch_doc = '''# Architecture Documentation

## System Architecture

The SIEM NLP Assistant follows a clean, layered architecture:

### 1. API Layer (`src/api/`)
- **Purpose**: HTTP interface for all services
- **Technology**: FastAPI
- **Components**:
  - Unified main application
  - Route handlers for different features
  - Middleware for auth, CORS, rate limiting

### 2. Core Business Logic (`src/core/`)
- **NLP Module**: Natural language processing
  - Intent classification
  - Entity extraction
  - Schema mapping
  - Ambiguity resolution
  
- **Query Module**: Query generation and validation
  - DSL/KQL builder
  - Query validator
  - Cost estimator
  - Query optimizer
  
- **Context Module**: Conversation management
  - Session management
  - Context preservation
  - Query history
  
- **Reporting Module**: Report generation
  - Text formatting
  - Chart generation
  - PDF/ZIP export

### 3. Connectors (`src/connectors/`)
- **Purpose**: SIEM platform integrations
- **Supported Platforms**:
  - Elasticsearch/Elastic SIEM
  - Wazuh
  - Mock connector for testing

### 4. Security Layer (`src/security/`)
- Authentication & authorization
- Role-based access control
- Audit logging
- Input sanitization
- Rate limiting

## Data Flow

1. User sends natural language query via API
2. NLP module processes query:
   - Extract intent and entities
   - Map to SIEM schema
   - Resolve ambiguities
3. Query builder generates DSL/KQL
4. Validator ensures query safety
5. Connector executes query on SIEM
6. Results are formatted and returned
7. Context is preserved for follow-ups

## Deployment Architecture

- **Backend**: FastAPI server (Python)
- **Frontend**: React SPA
- **Database**: PostgreSQL (audit logs, history)
- **Cache**: Redis (session, query cache)
- **SIEM**: Elasticsearch or Wazuh
'''
    
    Path("docs/ARCHITECTURE.md").write_text(arch_doc)
    print("✅ Created ARCHITECTURE.md")
    
    # API documentation
    api_doc = '''# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints require JWT authentication except `/health` and `/auth/login`.

### Login
```
POST /auth/login
{
  "username": "admin",
  "password": "password"
}
```

## Endpoints

### Assistant Chat
```
POST /api/assistant/chat
{
  "query": "Show me failed login attempts in the last hour",
  "conversation_id": "conv_123",
  "context": {}
}
```

### Query Execution
```
POST /api/query/execute
{
  "query": "event.action:login_failed",
  "index": "security-logs",
  "size": 100
}
```

### Report Generation
```
POST /api/reports/generate
{
  "type": "security_summary",
  "time_range": "last_24_hours",
  "format": "pdf"
}
```

### Health Check
```
GET /health
```

## Response Format
All responses follow this structure:
```json
{
  "success": true,
  "data": {},
  "error": null,
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "execution_time": 0.123
  }
}
```
'''
    
    Path("docs/API.md").write_text(api_doc)
    print("✅ Created API.md")

def cleanup_old_structure():
    """Remove old/redundant directories"""
    print_header("Cleaning Up Old Structure")
    
    dirs_to_remove = [
        "ui_dashboard",  # Remove Streamlit dashboard
        "backend",  # Old backend directory
        "assistant",  # Old assistant module
        "siem_connector",  # Old connector directory
        "rag_pipeline",  # Move to core
    ]
    
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            # Create backup first
            backup_name = f"{dir_name}_backup"
            if Path(backup_name).exists():
                shutil.rmtree(backup_name)
            shutil.copytree(dir_path, backup_name)
            print(f"📦 Backed up: {dir_name} → {backup_name}")

def create_startup_script():
    """Create a new startup script"""
    print_header("Creating Startup Script")
    
    startup_content = '''#!/usr/bin/env python3
"""
SIEM NLP Assistant - Application Launcher
Simplified startup script for the restructured application
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    required = ["fastapi", "uvicorn", "spacy", "elasticsearch", "react"]
    missing = []
    
    for req in required[:4]:  # Check Python packages
        try:
            __import__(req)
        except ImportError:
            missing.append(req)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "src.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def start_frontend():
    """Start the React frontend"""
    print("🚀 Starting frontend...")
    os.chdir("web")
    return subprocess.Popen(["npm", "run", "dev"])

def main():
    """Main startup function"""
    print("=" * 60)
    print("  SIEM NLP Assistant - Starting Services")
    print("=" * 60)
    
    if not check_requirements():
        sys.exit(1)
    
    # Start services
    backend = start_backend()
    time.sleep(3)  # Wait for backend to start
    
    frontend = start_frontend()
    
    print("\\n✅ All services started!")
    print("📍 Backend API: http://localhost:8000")
    print("📍 Frontend: http://localhost:5173")
    print("📚 API Docs: http://localhost:8000/api/docs")
    print("\\nPress Ctrl+C to stop all services...")
    
    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\\n⏹️ Shutting down services...")
        backend.terminate()
        frontend.terminate()
        print("✅ Services stopped.")

if __name__ == "__main__":
    main()
'''
    
    Path("start.py").write_text(startup_content)
    print("✅ Created start.py")

def main():
    """Main execution function"""
    print("\n" + "🔧 REPOSITORY RESTRUCTURING TOOL 🔧".center(60, "="))
    print("\nThis script will reorganize your repository to a clean, professional structure.")
    print("Your old files will be backed up before any changes.\n")
    
    response = input("Do you want to proceed? (yes/no): ").lower()
    
    if response != 'yes':
        print("Restructuring cancelled.")
        return
    
    # Execute restructuring steps
    create_directory_structure()
    move_and_consolidate_files()
    create_unified_api()
    create_missing_modules()
    create_config_files()
    create_documentation()
    create_startup_script()
    cleanup_old_structure()
    
    print("\n" + "="*60)
    print("✅ REPOSITORY RESTRUCTURING COMPLETE!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Review the new structure in 'src/' directory")
    print("2. Update dependencies: pip install -r requirements.txt")
    print("3. Install frontend deps: cd web && npm install")
    print("4. Run the application: python start.py")
    print("\nOld directories have been backed up with '_backup' suffix.")
    print("Once verified, you can delete the backup directories.")

if __name__ == "__main__":
    main()
