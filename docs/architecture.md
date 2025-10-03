# 🏗️ Architecture Overview

## System Design

The SIEM NLP Assistant follows a modular, microservices-inspired architecture designed for scalability and maintainability.

## High-Level Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   User Input    │────│  NLP Backend    │────│  SIEM Stack     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
                       ┌─────────────────┐
                       │                 │
                       │ Context Manager │
                       │                 │
                       └─────────────────┘
```

## Core Components

### 1. NLP Backend (`backend/`)

**Purpose**: Main application server handling natural language processing and API endpoints.

**Key Features**:

- FastAPI-based REST API
- Natural language parsing and intent recognition
- Query generation for SIEM systems
- Response formatting and presentation

**Files**:

- `app.py` - Main FastAPI application
- `services/nlp_parser.py` - Natural language processing
- `services/query_generator.py` - SIEM query generation
- `services/siem_connector.py` - SIEM system integration

### 2. Context Manager (`context_manager/`)

**Purpose**: Persistent conversation memory and context storage using SQLite.

**Key Features**:

- SQLite database with WAL mode for concurrent access
- TTL (Time-To-Live) support for automatic cleanup
- Thread-safe operations with RLock
- In-memory caching for performance
- Namespace-based context isolation

**Architecture**:

```text
┌─────────────────────────────────────────┐
│          Context Manager               │
├─────────────────────────────────────────┤
│  Memory Cache (LRU)                    │
├─────────────────────────────────────────┤
│  Thread-Safe Operations (RLock)        │
├─────────────────────────────────────────┤
│  SQLite Database (WAL Mode)            │
│  ├─ Contexts Table                     │
│  ├─ TTL Management                     │
│  └─ Metadata Storage                   │
└─────────────────────────────────────────┘
```

### 3. SIEM Stack (External)

**Purpose**: Data storage, indexing, and visualization.

**Components**:

- **Elasticsearch**: Log storage and search engine
- **Kibana**: Visualization and dashboard interface
- **Beats**: Data collection agents (optional)

## Data Flow

### 1. Query Processing Flow

```text
User Query
    │
    ▼
┌─────────────────┐
│  NLP Parser     │  ──► Parse intent, extract entities
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Context Manager │  ──► Retrieve conversation history
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Query Generator │  ──► Generate Elasticsearch query
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ SIEM Connector  │  ──► Execute query on Elasticsearch
└─────────────────┘
    │
    ▼
┌─────────────────┐
│Response Format  │  ──► Format and present results
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Context Manager │  ──► Store context for next query
└─────────────────┘
```

### 2. Context Management Flow

```text
┌─────────────────┐
│   New Query     │
└─────────────────┘
         │
         ▼
┌─────────────────┐    Cache Hit?     ┌─────────────────┐
│  Check Cache    │ ──────────────────│  Return Cached  │
└─────────────────┘                   └─────────────────┘
         │ Cache Miss
         ▼
┌─────────────────┐
│ Query Database  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Update Cache   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Return Context  │
└─────────────────┘
```

## Security Considerations

### 1. Data Protection

- SQLite database with appropriate file permissions
- No sensitive data stored in plain text
- Session isolation through namespacing

### 2. API Security

- Input validation and sanitization
- Rate limiting (planned)
- Authentication integration points

### 3. SIEM Integration

- Secure connection to Elasticsearch
- Query injection prevention
- Access control delegation to SIEM system

## Performance Characteristics

### Context Manager Performance

- **Memory Cache**: LRU cache for frequently accessed contexts
- **Database**: SQLite with WAL mode for concurrent reads
- **TTL Cleanup**: Automatic cleanup of expired contexts
- **Thread Safety**: RLock for safe concurrent operations

### Scalability Considerations

- **Horizontal Scaling**: Stateless backend design
- **Database Scaling**: SQLite suitable for single-instance deployments
- **Cache Efficiency**: In-memory LRU cache reduces database load

## Configuration

### Environment Variables

```bash
# Database Configuration
DB_PATH=./siem_contexts.db
DB_CACHE_SIZE=100

# SIEM Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=logs-*

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Database Schema

```sql
CREATE TABLE contexts (
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    PRIMARY KEY (namespace, key)
);

CREATE INDEX idx_expires_at ON contexts(expires_at);
```

## Deployment Patterns

### Development

- Local SQLite database
- Docker Compose for SIEM stack
- FastAPI development server

### Production

- Persistent volume for SQLite database
- Container orchestration (Docker/Kubernetes)
- Load balancer for multiple instances
- Monitoring and logging integration

## Integration Points

### External Systems

- **Elasticsearch/Kibana**: Primary SIEM data source
- **Wazuh**: Alternative SIEM integration
- **Splunk**: Future integration possibility

### Extensions

- **Plugin Architecture**: Modular service design
- **Custom Parsers**: Pluggable NLP components
- **Response Formatters**: Customizable output formats

---

Next: [API Reference](./api-reference.md) | [Setup Guide](./setup-guide.md)
