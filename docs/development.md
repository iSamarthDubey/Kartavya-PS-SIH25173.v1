# 🔨 Development Guide

Comprehensive guide for developers contributing to the SIEM NLP Assistant.

## Development Environment Setup

### Prerequisites

- **Python 3.10+** with pip
- **Git** for version control
- **Docker Desktop** for integration testing
- **VS Code** (recommended) with Python extension

### Initial Setup

```bash
# Clone and setup
git clone https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1.git
cd Kartavya-PS-SIH25173.v1

# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

```text
# requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.1
isort==5.12.0
pre-commit==3.6.0
bandit==1.7.5
safety==2.3.5
```

## Project Structure

### Code Organization

```text
Kartavya-PS-SIH25173.v1/
├── backend/                    # Main application
│   ├── app.py                  # FastAPI application entry point
│   ├── services/               # Business logic services
│   │   ├── nlp_parser.py       # Natural language processing
│   │   ├── query_generator.py  # Elasticsearch query generation
│   │   ├── siem_connector.py   # SIEM system integration
│   │   └── report_formatter.py # Response formatting
│   └── models/                 # Data models and schemas
├── context_manager/            # Context persistence layer
│   ├── context.py              # Core context management
│   └── memory_store.py         # High-level SIEM operations
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test data and mocks
├── docs/                       # Documentation
└── scripts/                    # Utility scripts
```

### Key Components

#### 1. Backend Services (`backend/services/`)

**NLP Parser** (`nlp_parser.py`):
- Intent recognition and classification
- Entity extraction from natural language
- Query preprocessing and normalization

**Query Generator** (`query_generator.py`):
- Natural language to Elasticsearch DSL conversion
- Query optimization and validation
- Time range and filter handling

**SIEM Connector** (`siem_connector.py`):
- Elasticsearch API integration
- Connection management and error handling
- Result processing and formatting

#### 2. Context Manager (`context_manager/`)

**Core Context** (`context.py`):
- SQLite-based persistent storage
- Thread-safe operations with RLock
- TTL management and cleanup
- In-memory caching with LRU

**Memory Store** (`memory_store.py`):
- High-level SIEM context operations
- Investigation workflow management
- Threat intelligence context

## Coding Standards

### Python Style Guide

We follow **PEP 8** with these specific configurations:

```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    migrations
```

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  migrations
  | venv
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

### Code Formatting

**Before committing, always run:**

```bash
# Format code
black .
isort .

# Check style
flake8 .

# Type checking
mypy backend/ context_manager/

# Security check
bandit -r backend/ context_manager/
```

### Documentation Standards

**Docstring Format** (Google Style):

```python
def process_query(query: str, user_id: str, namespace: str = "default") -> dict:
    """Process a natural language query and return SIEM results.
    
    Args:
        query: Natural language query string
        user_id: Unique identifier for the user session
        namespace: Context namespace for isolation
        
    Returns:
        Dictionary containing:
            - response: Formatted response text
            - elasticsearch_query: Generated ES query
            - results: Raw search results
            - metadata: Additional context information
            
    Raises:
        QueryGenerationError: If query cannot be parsed
        ElasticsearchError: If ES query fails
        
    Example:
        >>> result = process_query("show failed logins", "user123")
        >>> print(result["response"])
        "Found 15 failed login attempts..."
    """
```

## Testing

### Test Structure

```text
tests/
├── unit/                       # Fast, isolated tests
│   ├── test_nlp_parser.py
│   ├── test_query_generator.py
│   ├── test_context_manager.py
│   └── test_siem_connector.py
├── integration/                # Component interaction tests
│   ├── test_api_endpoints.py
│   ├── test_elasticsearch.py
│   └── test_end_to_end.py
├── fixtures/                   # Test data
│   ├── sample_queries.json
│   ├── mock_responses.json
│   └── test_database.db
└── conftest.py                 # Pytest configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=context_manager --cov-report=html

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest -k "test_context_manager"      # Specific test pattern

# Run tests in parallel
pytest -n auto                        # Requires pytest-xdist
```

### Writing Tests

**Unit Test Example:**

```python
# tests/unit/test_query_generator.py
import pytest
from backend.services.query_generator import QueryGenerator

class TestQueryGenerator:
    @pytest.fixture
    def query_generator(self):
        return QueryGenerator()
    
    def test_simple_security_query(self, query_generator):
        """Test basic security query generation."""
        query = "show failed login attempts"
        result = query_generator.generate(query)
        
        assert "bool" in result["query"]
        assert "failed" in str(result).lower()
        assert "login" in str(result).lower()
    
    def test_time_range_parsing(self, query_generator):
        """Test time range extraction."""
        query = "show events from last 24 hours"
        result = query_generator.generate(query)
        
        assert "range" in str(result)
        assert "@timestamp" in str(result)
        assert "gte" in str(result)
    
    @pytest.mark.parametrize("query,expected_type", [
        ("failed logins", "security"),
        ("cpu usage", "monitoring"),
        ("disk space", "system"),
    ])
    def test_query_classification(self, query_generator, query, expected_type):
        """Test query type classification."""
        result = query_generator.classify_query(query)
        assert result["type"] == expected_type
```

**Integration Test Example:**

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from backend.app import app

class TestAPIEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
    
    def test_query_endpoint(self, client):
        """Test query processing endpoint."""
        payload = {
            "query": "show system health",
            "user_id": "test_user"
        }
        
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "response" in data["data"]
```

### Test Data Management

**Fixtures for consistent test data:**

```python
# tests/conftest.py
import pytest
import tempfile
from context_manager.context import ContextManager

@pytest.fixture
def temp_database():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db') as f:
        yield f.name

@pytest.fixture
def context_manager(temp_database):
    """Create context manager with temporary database."""
    return ContextManager(db_path=temp_database)

@pytest.fixture
def sample_queries():
    """Sample queries for testing."""
    return [
        "show failed login attempts",
        "check system performance last hour",
        "find suspicious network activity",
        "list admin privilege changes today"
    ]
```

## API Development

### FastAPI Patterns

**Endpoint Structure:**

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="SIEM NLP Assistant", version="1.0.0")

class QueryRequest(BaseModel):
    query: str
    user_id: str
    namespace: Optional[str] = "default"
    
class QueryResponse(BaseModel):
    status: str
    data: dict
    context_id: Optional[str] = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query and return SIEM results."""
    try:
        # Process the query
        result = await query_processor.process(
            request.query, 
            request.user_id, 
            request.namespace
        )
        
        return QueryResponse(
            status="success",
            data=result,
            context_id=result.get("context_id")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Error Handling

**Structured Error Responses:**

```python
from enum import Enum

class ErrorCode(Enum):
    INVALID_QUERY = "INVALID_QUERY"
    ELASTICSEARCH_ERROR = "ELASTICSEARCH_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    CONTEXT_EXPIRED = "CONTEXT_EXPIRED"

class APIError(Exception):
    def __init__(self, code: ErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

@app.exception_handler(APIError)
async def api_error_handler(request, exc: APIError):
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Input Validation

**Pydantic Models for Validation:**

```python
from pydantic import BaseModel, validator, Field
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    user_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]+$')
    namespace: Optional[str] = Field(default="default", regex=r'^[a-zA-Z0-9_-]+$')
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if len(v) < 3:
            raise ValueError('User ID must be at least 3 characters')
        return v
```

## Database Development

### Context Manager Extensions

**Adding New Context Types:**

```python
# context_manager/context.py
class ContextManager:
    def set_investigation_context(self, user_id: str, investigation_data: dict):
        """Set context for security investigation."""
        context = {
            "type": "investigation",
            "investigation_id": investigation_data["id"],
            "entities": investigation_data["entities"],
            "timeline": investigation_data["timeline"],
            "status": "active"
        }
        
        return self.set_context(
            namespace="investigations",
            key=f"inv_{investigation_data['id']}",
            value=context,
            ttl=86400  # 24 hours
        )
    
    def get_active_investigations(self, user_id: str) -> List[dict]:
        """Get all active investigations for user."""
        pattern = f"investigations:inv_*"
        results = self.search(pattern, namespace="investigations")
        
        return [
            result["value"] for result in results 
            if result["value"].get("status") == "active"
        ]
```

### Database Migrations

**Migration Script Template:**

```python
# scripts/migrate_database.py
import sqlite3
from pathlib import Path

def migrate_v1_to_v2(db_path: str):
    """Migrate database from v1 to v2 schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current version
        cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
        current_version = cursor.fetchone()
        
        if current_version and current_version[0] == '2':
            print("Database already at version 2")
            return
        
        # Add new columns
        cursor.execute("""
            ALTER TABLE contexts 
            ADD COLUMN investigation_id TEXT
        """)
        
        # Update schema version
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value) 
            VALUES ('schema_version', '2')
        """)
        
        conn.commit()
        print("Migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_v1_to_v2("siem_contexts.db")
```

## Performance Optimization

### Profiling

**Performance Monitoring:**

```python
import time
import functools
from typing import Callable

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
    
    return wrapper

# Usage
@performance_monitor
def process_complex_query(query: str) -> dict:
    # Complex processing here
    pass
```

### Caching Strategies

**LRU Cache Implementation:**

```python
from functools import lru_cache
from typing import Dict, Any

class QueryCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
    
    @lru_cache(maxsize=1000)
    def get_cached_query(self, query_hash: str) -> Optional[dict]:
        """Get cached query result."""
        return self._cache.get(query_hash)
    
    def cache_query_result(self, query_hash: str, result: dict, ttl: int = 300):
        """Cache query result with TTL."""
        expiry = time.time() + ttl
        self._cache[query_hash] = {
            "result": result,
            "expiry": expiry
        }
        
        # Cleanup expired entries
        self._cleanup_expired()
    
    def _cleanup_expired(self):
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items()
            if value.get("expiry", 0) < current_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
```

## Contributing Workflow

### Git Workflow

**Branch Naming Convention:**
```text
feature/add-new-query-type
bugfix/context-manager-deadlock
hotfix/critical-security-patch
docs/update-api-reference
```

**Commit Message Format:**
```text
type(scope): description

feat(nlp): add support for time range queries
fix(context): resolve database locking issue
docs(api): update endpoint documentation
test(integration): add elasticsearch connection tests
```

### Pull Request Process

1. **Create Feature Branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Develop and Test:**
```bash
# Make changes
# Run tests
pytest

# Check code quality
black .
flake8 .
mypy backend/ context_manager/
```

3. **Commit Changes:**
```bash
git add .
git commit -m "feat(component): description of changes"
```

4. **Create Pull Request:**
- Use the PR template
- Include screenshots for UI changes
- Reference related issues
- Add reviewer assignments

### Code Review Guidelines

**For Reviewers:**
- Check code quality and style
- Verify test coverage
- Test functionality locally
- Review security implications
- Ensure documentation updates

**For Authors:**
- Address all review comments
- Update tests for changes
- Keep PRs focused and small
- Provide clear descriptions

## Release Management

### Versioning

We use **Semantic Versioning** (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Process

1. **Version Bump:**
```bash
# Update version in relevant files
# backend/app.py
# setup.py
# docker-compose.yml

git commit -m "chore: bump version to 1.2.0"
git tag v1.2.0
```

2. **Build and Test:**
```bash
# Run full test suite
pytest

# Build Docker images
docker-compose build

# Test deployment
docker-compose up -d
```

3. **Release Notes:**
```markdown
# Release v1.2.0

## New Features
- Added support for custom query types
- Improved context manager performance

## Bug Fixes
- Fixed database locking issue
- Resolved memory leak in query processing

## Breaking Changes
- Updated API response format for /query endpoint
```

## IDE Configuration

### VS Code Settings

```json
// .vscode/settings.json
{
    "python.pythonPath": "./venv/bin/python",
    "python.analysis.extraPaths": [
        "./backend",
        "./context_manager"
    ],
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

### VS Code Extensions

Recommended extensions:
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Python Docstring Generator**
- **GitLens**
- **Docker**
- **REST Client**

### Debug Configuration

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Backend",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/backend/app.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "LOG_LEVEL": "DEBUG"
            }
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

## Security Considerations

### Code Security

**Input Validation:**
```python
import re
from typing import List

def validate_query_input(query: str) -> bool:
    """Validate user query for security."""
    # Check for SQL injection patterns
    sql_patterns = [
        r'\b(DROP|DELETE|INSERT|UPDATE|ALTER)\b',
        r'--',
        r'/\*.*\*/',
        r'\bUNION\b'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False
    
    return True

def sanitize_user_input(data: str) -> str:
    """Sanitize user input."""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        data = data.replace(char, '')
    
    return data.strip()
```

**Security Headers:**
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Dependency Management

**Security Scanning:**
```bash
# Check for known vulnerabilities
safety check

# Audit dependencies
pip-audit

# Update dependencies
pip-review --auto
```

## Documentation

### API Documentation

**Automatic OpenAPI Generation:**
```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="SIEM NLP Assistant API",
        version="1.0.0",
        description="Natural language interface for SIEM data analysis",
        routes=app.routes,
    )
    
    # Add custom schema information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Access documentation at:**
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Code Documentation

**Generate documentation:**
```bash
# Install documentation tools
pip install sphinx sphinx-autodoc-typehints

# Generate documentation
sphinx-quickstart docs
sphinx-apidoc -o docs/source backend/ context_manager/
cd docs && make html
```

---

Ready to contribute? Check out our [open issues](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/issues) and [project roadmap](./roadmap.md)!