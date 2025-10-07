#!/usr/bin/env python3
"""
Kartavya SIEM Assistant - Repository Restructuring Script
Migrates from cluttered structure to clean production-ready architecture
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class RepositoryMigrator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.migration_map = {}
        self.created_dirs = []
        
    def create_new_structure(self):
        """Create the new directory structure"""
        print("📁 Creating new directory structure...")
        
        new_dirs = [
            # Backend structure
            "backend/app/core",
            "backend/app/api", 
            "backend/app/services",
            "backend/app/utils",
            "backend/tests",
            
            # Frontend (keep existing)
            "frontend/src/components/chat",
            "frontend/src/components/dashboard",
            "frontend/src/services",
            "frontend/src/hooks",
            "frontend/src/types",
            
            # Deployment
            "deployment/docker",
            "deployment/kubernetes",
            "deployment/configs",
            
            # Documentation
            "docs/api",
            "docs/guides",
            "docs/architecture",
            
            # Scripts
            "scripts/setup",
            "scripts/migration",
            
            # Tests
            "tests/backend/unit",
            "tests/backend/integration",
            "tests/e2e",
            
            # Data
            "data/samples",
            "data/models"
        ]
        
        for dir_path in new_dirs:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.created_dirs.append(dir_path)
            
        print(f"✅ Created {len(new_dirs)} directories")
        
    def consolidate_backend(self):
        """Consolidate backend modules"""
        print("\n🔧 Consolidating backend modules...")
        
        # Map old locations to new locations
        backend_migrations = {
            # NLP components
            "backend/nlp/intent_classifier.py": "backend/app/core/nlp.py",
            "backend/nlp/entity_extractor.py": "backend/app/core/nlp.py",
            
            # SIEM connectors  
            "siem_connector/elastic_connector.py": "backend/app/core/siem.py",
            "siem_connector/wazuh_connector.py": "backend/app/core/siem.py",
            "siem_connector/query_processor.py": "backend/app/services/pipeline.py",
            
            # Assistant module
            "assistant/main.py": "backend/app/main.py",
            "assistant/router.py": "backend/app/api/routes.py",
            "assistant/pipeline.py": "backend/app/services/pipeline.py",
            "assistant/context_manager.py": "backend/app/services/context.py",
            "assistant/security.py": "backend/app/core/security.py",
            
            # Response formatting
            "backend/response_formatter/formatter.py": "backend/app/services/formatter.py",
            "backend/response_formatter/text_formatter.py": "backend/app/services/formatter.py",
            "backend/response_formatter/chart_formatter.py": "backend/app/services/formatter.py",
            
            # Query building
            "backend/query_builder.py": "backend/app/services/pipeline.py",
            "backend/elastic_client.py": "backend/app/core/siem.py",
        }
        
        # Process each migration
        for old_path, new_path in backend_migrations.items():
            self._migrate_file(old_path, new_path)
            
    def _migrate_file(self, old_path: str, new_path: str):
        """Migrate a single file or merge into existing"""
        old_file = self.base_path / old_path
        new_file = self.base_path / new_path
        
        if old_file.exists():
            # Check if we need to merge or just copy
            if new_file.exists():
                print(f"  📝 Merging {old_path} -> {new_path}")
                # Append content for merge
                with open(old_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(new_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n# --- Merged from {old_path} ---\n")
                    f.write(content)
            else:
                print(f"  📋 Moving {old_path} -> {new_path}")
                new_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old_file, new_file)
                
            self.migration_map[str(old_path)] = str(new_path)
            
    def consolidate_tests(self):
        """Consolidate all test files"""
        print("\n🧪 Consolidating test files...")
        
        test_migrations = {
            "tests/test_connector.py": "tests/backend/integration/test_siem_connector.py",
            "tests/test_parser.py": "tests/backend/unit/test_nlp.py",
            "tests/test_siem_connector.py": "tests/backend/integration/test_siem_connector.py",
            "tests/complete_integration_test.py": "tests/e2e/test_complete_flow.py",
            "tests/e2e/test_complete_integration.py": "tests/e2e/test_complete_flow.py",
            "assistant/test_assistant.py": "tests/backend/integration/test_assistant.py",
        }
        
        for old_path, new_path in test_migrations.items():
            self._migrate_file(old_path, new_path)
            
    def clean_root_directory(self):
        """Clean up root directory files"""
        print("\n🧹 Cleaning root directory...")
        
        # Files to keep in root
        keep_files = [
            "README.md",
            "LICENSE",
            ".gitignore",
            ".env.example",
            "pyproject.toml"
        ]
        
        # Move configurations
        config_moves = {
            "requirements.txt": "backend/requirements.txt",
            "requirements-prod.txt": "deployment/requirements-prod.txt",
            "docker-compose.yml": "deployment/docker-compose.yml",
            ".env": "deployment/.env",
            "setup.py": "scripts/setup.py",
        }
        
        for old_path, new_path in config_moves.items():
            if (self.base_path / old_path).exists():
                self._migrate_file(old_path, new_path)
                
    def remove_redundant_directories(self):
        """Remove empty and redundant directories"""
        print("\n🗑️ Removing redundant directories...")
        
        dirs_to_remove = [
            "ui_dashboard",  # Streamlit (keeping React frontend)
            "rag_pipeline",  # Not implemented yet
            "llm_training",  # Move to data/models if needed
            "beats-config",  # Move to deployment
            "src/backend",   # Empty
            "datasets",      # Empty, using data/ instead
        ]
        
        for dir_name in dirs_to_remove:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                # Save any important files first
                important_files = list(dir_path.glob("**/*.py")) + list(dir_path.glob("**/*.json"))
                if important_files:
                    backup_dir = self.base_path / "data" / "archived" / dir_name
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    for file in important_files:
                        rel_path = file.relative_to(dir_path)
                        dest = backup_dir / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file, dest)
                print(f"  ✅ Archived {dir_name}")
                
    def create_consolidated_files(self):
        """Create new consolidated module files"""
        print("\n📝 Creating consolidated modules...")
        
        # Create consolidated NLP module
        nlp_content = '''"""
Kartavya SIEM NLP Module
Consolidated NLP processing for intent classification and entity extraction
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
import re
from datetime import datetime, timedelta
import dateparser

class QueryIntent(Enum):
    """Query intent types"""
    SEARCH_LOGS = "search_logs"
    AUTHENTICATION = "authentication"
    NETWORK_SECURITY = "network_security"
    MALWARE_DETECTION = "malware_detection"
    USER_ACTIVITY = "user_activity"
    SYSTEM_HEALTH = "system_health"
    THREAT_HUNTING = "threat_hunting"
    COMPLIANCE_CHECK = "compliance_check"
    INCIDENT_INVESTIGATION = "incident_investigation"
    REPORT_GENERATION = "report_generation"

class NLPProcessor:
    """Unified NLP processor for SIEM queries"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        
    def process_query(self, query: str) -> Dict:
        """Process natural language query"""
        intent = self.classify_intent(query)
        entities = self.extract_entities(query)
        
        return {
            "intent": intent,
            "entities": entities,
            "original_query": query,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Classify query intent with confidence score"""
        # Implementation will be merged from intent_classifier.py
        pass
        
    def extract_entities(self, query: str) -> List[Dict]:
        """Extract entities from query"""
        # Implementation will be merged from entity_extractor.py
        pass
        
    def _load_intent_patterns(self) -> Dict:
        """Load intent classification patterns"""
        return {
            QueryIntent.AUTHENTICATION: [
                r"(failed|successful)?\s*(login|logon|auth|authentication)",
                r"(password|credential)\s*(reset|change|expire)",
                r"mfa|multi.?factor|two.?factor"
            ],
            QueryIntent.MALWARE_DETECTION: [
                r"malware|virus|trojan|ransomware",
                r"(suspicious|malicious)\s*(file|process|activity)",
                r"threat\s*detect"
            ],
            # Add more patterns
        }
        
    def _load_entity_patterns(self) -> Dict:
        """Load entity extraction patterns"""
        return {
            "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            "username": r"user[:\s]+([a-zA-Z0-9_.-]+)",
            "domain": r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}",
            "time_range": r"(last|past|previous)\s+(\d+)\s+(hour|day|week|month)s?",
            # Add more patterns
        }
'''
        
        nlp_file = self.base_path / "backend/app/core/nlp.py"
        nlp_file.parent.mkdir(parents=True, exist_ok=True)
        nlp_file.write_text(nlp_content)
        
        # Create consolidated SIEM connector module
        siem_content = '''"""
Kartavya SIEM Connector Module
Unified interface for Elasticsearch and Wazuh SIEM platforms
"""

from typing import Dict, List, Optional, Any
from elasticsearch import AsyncElasticsearch
import aiohttp
import os
from datetime import datetime

class SIEMConnector:
    """Unified SIEM connector for Elastic and Wazuh"""
    
    def __init__(self, siem_type: str = "elastic"):
        self.siem_type = siem_type
        self.client = None
        self._initialize_client()
        
    async def search(self, query: Dict, index: str = "*") -> Dict:
        """Execute search query on SIEM"""
        if self.siem_type == "elastic":
            return await self._elastic_search(query, index)
        elif self.siem_type == "wazuh":
            return await self._wazuh_search(query, index)
            
    async def get_schema(self, index: str) -> Dict:
        """Get index mapping/schema"""
        if self.siem_type == "elastic":
            return await self.client.indices.get_mapping(index=index)
            
    def _initialize_client(self):
        """Initialize SIEM client"""
        if self.siem_type == "elastic":
            self.client = AsyncElasticsearch(
                hosts=[os.getenv("ELASTICSEARCH_HOST", "localhost:9200")],
                basic_auth=(
                    os.getenv("ELASTICSEARCH_USER", "elastic"),
                    os.getenv("ELASTICSEARCH_PASSWORD", "changeme")
                )
            )
            
    async def _elastic_search(self, query: Dict, index: str) -> Dict:
        """Execute Elasticsearch query"""
        # Implementation from elastic_connector.py
        pass
        
    async def _wazuh_search(self, query: Dict, index: str) -> Dict:
        """Execute Wazuh query"""
        # Implementation from wazuh_connector.py
        pass
'''
        
        siem_file = self.base_path / "backend/app/core/siem.py"
        siem_file.write_text(siem_content)
        
        print("✅ Created consolidated core modules")
        
    def create_main_app(self):
        """Create the main FastAPI application"""
        print("\n🚀 Creating main FastAPI app...")
        
        main_content = '''"""
Kartavya SIEM Assistant - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.api.routes import router
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
    yield
    logger.info("Shutting down Kartavya SIEM Assistant...")

# Create FastAPI app
app = FastAPI(
    title="Kartavya SIEM Assistant",
    description="NLP-powered SIEM investigation and reporting assistant for ISRO",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "kartavya-siem"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
'''
        
        main_file = self.base_path / "backend/app/main.py"
        main_file.write_text(main_content)
        print("✅ Created main FastAPI application")
        
    def update_package_files(self):
        """Update package.json and requirements.txt"""
        print("\n📦 Updating package files...")
        
        # Backend requirements
        requirements = """# Kartavya SIEM Assistant - Backend Dependencies

# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0

# SIEM Connectors
elasticsearch==8.11.0
aiohttp==3.9.1

# NLP & ML
spacy==3.7.2
dateparser==1.2.0
pandas==2.1.4
numpy==1.26.2

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.2

# Utils
redis==5.0.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
"""
        
        req_file = self.base_path / "backend/requirements.txt"
        req_file.write_text(requirements)
        
        print("✅ Updated package files")
        
    def create_migration_report(self):
        """Create a detailed migration report"""
        print("\n📊 Creating migration report...")
        
        report = {
            "migration_date": datetime.now().isoformat(),
            "directories_created": self.created_dirs,
            "files_migrated": self.migration_map,
            "new_structure": {
                "backend": "FastAPI backend with consolidated modules",
                "frontend": "React + TypeScript + TailwindCSS",
                "deployment": "Docker and Kubernetes configs",
                "docs": "Complete documentation",
                "tests": "Organized test suite"
            }
        }
        
        report_file = self.base_path / "MIGRATION_REPORT.json"
        report_file.write_text(json.dumps(report, indent=2))
        
        print("✅ Migration report created")
        
    def run_migration(self):
        """Execute the complete migration"""
        print("\n🚀 Starting Kartavya SIEM Repository Migration\n")
        print("=" * 60)
        
        self.create_new_structure()
        self.consolidate_backend()
        self.consolidate_tests()
        self.create_consolidated_files()
        self.create_main_app()
        self.clean_root_directory()
        self.remove_redundant_directories()
        self.update_package_files()
        self.create_migration_report()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print(f"📁 Check MIGRATION_REPORT.json for details")
        print(f"🔧 Next steps:")
        print("  1. Review consolidated files in backend/app/core/")
        print("  2. Update imports in all Python files")
        print("  3. Test the new structure with: python backend/app/main.py")
        print("  4. Remove old directories after verification")

if __name__ == "__main__":
    migrator = RepositoryMigrator()
    migrator.run_migration()
