# 🧹 CODEBASE CLEANUP & RESTRUCTURING PLAN

**Date**: October 4, 2025  
**Status**: 🚧 IN PROGRESS  
**Objective**: Clean up, organize, and finalize routing for production

---

## 📋 Current Issues Found

### 1. **Duplicate/Redundant Files**
- ❌ `app.py` (root) - Old file, not in use
- ❌ `nlp_parser/` - Duplicate of `backend/nlp/`
- ❌ `response_formatter/` (root) - Duplicate of `backend/response_formatter/`
- ❌ `context_manager/` - Redundant with assistant module
- ❌ `test_entity_fix.py` - One-time test, can be removed
- ❌ `siem_contexts.db` (root) - Old database file
- ❌ `verification_test.db` - Old test file

### 2. **Import Path Inconsistencies**
```python
# INCONSISTENT: Mix of relative and absolute imports
backend/query_builder.py: from nlp.intent_classifier import ...
assistant/pipeline.py: from backend.nlp.intent_classifier import ...
```

### 3. **Missing __init__.py Files**
- ❌ `backend/nlp/__init__.py` - Missing
- ❌ `backend/response_formatter/__init__.py` - Incomplete
- ❌ `siem_connector/__init__.py` - Missing

### 4. **Scattered Test Files**
- `test_complete_integration.py` (root)
- `test_entity_fix.py` (root)
- `tests/` folder (separate location)

### 5. **Documentation Clutter**
- Multiple status reports (need consolidation)
- Outdated TODO/roadmap files

---

## 🎯 Cleanup Actions

### Phase 1: Remove Redundant Files ✅
```bash
# Delete old/duplicate files
rm app.py
rm -rf nlp_parser/
rm -rf response_formatter/  # Keep backend/response_formatter/
rm -rf context_manager/     # Using assistant's context
rm test_entity_fix.py
rm siem_contexts.db
rm verification_test.db
```

### Phase 2: Standardize Import Paths ✅
**New Standard**: All imports from project root
```python
# ✅ CORRECT (from root)
from backend.nlp.intent_classifier import IntentClassifier
from backend.nlp.entity_extractor import EntityExtractor
from backend.query_builder import QueryBuilder
from siem_connector.elastic_connector import ElasticsearchConnector
from assistant.pipeline import ConversationalPipeline
```

### Phase 3: Add Missing __init__.py Files ✅
Create proper module initialization:
- `backend/__init__.py`
- `backend/nlp/__init__.py`
- `backend/response_formatter/__init__.py`
- `siem_connector/__init__.py`
- `rag_pipeline/__init__.py`

### Phase 4: Reorganize Tests ✅
Move all tests to `tests/` folder:
```
tests/
├── unit/
│   ├── test_intent_classifier.py
│   ├── test_entity_extractor.py
│   └── test_query_builder.py
├── integration/
│   ├── test_pipeline.py
│   └── test_api.py
└── e2e/
    └── test_complete_integration.py
```

### Phase 5: Consolidate Documentation ✅
```
docs/
├── ARCHITECTURE.md          # System design
├── API_REFERENCE.md         # API endpoints
├── DEVELOPMENT.md           # Dev setup
└── DEPLOYMENT.md            # Production deployment
```

### Phase 6: Update Configuration Files ✅
- Fix `requirements.txt` (remove duplicates)
- Update `.gitignore`
- Create proper `setup.py` or `pyproject.toml`

---

## 📁 Final Directory Structure

```
Kartavya-PS-SIH25173.v1/
│
├── 📦 assistant/              # Conversational AI module
│   ├── __init__.py
│   ├── main.py               # FastAPI server (port 8001)
│   ├── router.py             # API routes
│   ├── pipeline.py           # Main orchestrator
│   └── models.py             # Pydantic models
│
├── 🧠 backend/                # Core processing modules
│   ├── __init__.py
│   ├── nlp/                  # NLP components
│   │   ├── __init__.py
│   │   ├── intent_classifier.py
│   │   └── entity_extractor.py
│   ├── response_formatter/   # Output formatting
│   │   ├── __init__.py
│   │   ├── formatter.py
│   │   ├── text_formatter.py
│   │   └── chart_formatter.py
│   ├── query_builder.py      # Query generation
│   └── elastic_client.py     # Elasticsearch helper
│
├── 🔌 siem_connector/         # SIEM integrations
│   ├── __init__.py
│   ├── elastic_connector.py
│   ├── wazuh_connector.py
│   └── utils.py
│
├── 🧪 rag_pipeline/           # RAG/LLM pipeline
│   ├── __init__.py
│   ├── pipeline.py
│   ├── retriever.py
│   ├── vector_store.py
│   └── prompt_builder.py
│
├── 🎨 ui_dashboard/           # Streamlit UI
│   ├── streamlit_app.py      # Main UI (port 8502)
│   ├── demo_data.py          # Mock data generator
│   └── static/
│
├── 🧪 tests/                  # All test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── 📜 scripts/                # Utility scripts
│   ├── ingest_logs.py
│   ├── setup_beats.ps1
│   └── update_dependencies.ps1
│
├── 📊 datasets/               # Sample data
│   ├── raw/
│   ├── processed/
│   └── synthetic/
│
├── 📚 docs/                   # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   └── DEPLOYMENT.md
│
├── 🐳 docker/                 # Docker configs
│   ├── docker-compose.yml
│   └── logstash/
│
├── ⚙️  beats-config/          # Beats configuration
│   ├── metricbeat.yml
│   └── winlogbeat.yml
│
├── 📝 Configuration Files
│   ├── requirements.txt      # Python dependencies
│   ├── .gitignore
│   ├── .env                  # Environment variables
│   └── README.md
│
└── 🗑️  TO DELETE
    ├── app.py (old)
    ├── nlp_parser/ (duplicate)
    ├── response_formatter/ (duplicate)
    ├── context_manager/ (redundant)
    └── *.db files (old databases)
```

---

## 🔄 Import Routing Map

### Core Module Paths
```python
# Assistant Module
from assistant.pipeline import ConversationalPipeline
from assistant.router import assistant_router
from assistant.main import app

# Backend NLP
from backend.nlp.intent_classifier import IntentClassifier, QueryIntent
from backend.nlp.entity_extractor import EntityExtractor, Entity

# Backend Query Builder
from backend.query_builder import QueryBuilder

# SIEM Connectors
from siem_connector.elastic_connector import ElasticsearchConnector
from siem_connector.wazuh_connector import WazuhConnector

# Response Formatting
from backend.response_formatter.formatter import ResponseFormatter
from backend.response_formatter.text_formatter import TextFormatter
from backend.response_formatter.chart_formatter import ChartFormatter

# RAG Pipeline
from rag_pipeline.pipeline import RAGPipeline
from rag_pipeline.retriever import DocumentRetriever
from rag_pipeline.vector_store import VectorStore
```

---

## ✅ Validation Checklist

### Pre-Cleanup
- [x] Backup current state (Git commit)
- [x] Document current import paths
- [x] Identify redundant files
- [x] List all dependencies

### During Cleanup
- [ ] Remove redundant files
- [ ] Add missing __init__.py files
- [ ] Fix all import statements
- [ ] Reorganize tests
- [ ] Update documentation
- [ ] Fix requirements.txt

### Post-Cleanup
- [ ] Run all tests (pytest)
- [ ] Verify backend starts (port 8001)
- [ ] Verify frontend starts (port 8502)
- [ ] Test end-to-end flow
- [ ] Check import resolution
- [ ] Validate API endpoints
- [ ] Git commit clean state

---

## 🚀 Execution Order

1. **Git Commit Current State** ✅
   ```bash
   git add -A
   git commit -m "Pre-cleanup checkpoint"
   ```

2. **Create Backup Branch** ✅
   ```bash
   git checkout -b backup/pre-cleanup
   git checkout main
   ```

3. **Execute Cleanup** 🚧
   - Delete redundant files
   - Add __init__.py files
   - Fix imports
   - Reorganize structure

4. **Test & Validate** ⏳
   - Run pytest
   - Start backend
   - Start frontend
   - Test integration

5. **Final Commit** ⏳
   ```bash
   git add -A
   git commit -m "feat: Clean up and restructure codebase"
   git push origin main
   ```

---

## 📊 Expected Results

### Before Cleanup
- 📁 50+ files in root
- ⚠️  Import path inconsistencies
- ❌ Duplicate modules
- 🗑️  Old test files scattered
- 📚 Documentation clutter

### After Cleanup
- ✅ Clean organized structure
- ✅ Consistent import paths
- ✅ No duplicates
- ✅ Tests in proper location
- ✅ Consolidated documentation
- ✅ Production-ready routing

---

**Status**: Ready to execute  
**Time Estimate**: 30 minutes  
**Risk Level**: Low (backed up on Git)

---

*Generated: October 4, 2025*  
*Team: Kartavya - SIH 2025*
