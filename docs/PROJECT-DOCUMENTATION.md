# 📚 SIEM NLP Assistant - Complete Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Frontend Documentation](#frontend-documentation)
4. [Backend Documentation](#backend-documentation)
5. [NLP Pipeline](#nlp-pipeline)
6. [SIEM Integration](#siem-integration)
7. [Security Features](#security-features)
8. [API Documentation](#api-documentation)
9. [Deployment Guide](#deployment-guide)
10. [Testing Strategy](#testing-strategy)

---

## 1. Project Overview

### 🎯 Purpose

The SIEM NLP Assistant is an innovative solution developed for the Smart India Hackathon (SIH) 2025, addressing Problem Statement SIH25173 by ISRO. It provides a conversational interface for Security Information and Event Management (SIEM) systems, specifically targeting ELK-based platforms like Elastic SIEM and Wazuh.

### 🔑 Key Features

- **Natural Language Processing**: Convert plain English queries to SIEM-specific query languages
- **Multi-turn Conversations**: Maintain context across multiple queries
- **Automated Reporting**: Generate comprehensive security reports
- **Platform Agnostic**: Works with multiple SIEM platforms
- **Real-time Analysis**: Process and analyze security events in real-time

### 🏗️ Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **NLP**: spaCy, Transformers, Custom Intent Classification
- **Database**: Elasticsearch (primary), Mock data (testing)
- **Deployment**: Docker, Docker Compose
- **Testing**: Pytest, Jest, React Testing Library

---

## 2. System Architecture

### 🔄 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (React + TypeScript + Vite)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                             │
│                    (FastAPI + Middleware Stack)                 │
│  • Authentication  • Rate Limiting  • Logging  • CORS          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Processing Pipeline                     │
├──────────────────┬──────────────────┬──────────────────────────┤
│   NLP Engine     │  Query Builder   │   Context Manager        │
│ • Intent Class.  │ • DSL Generation │ • Session Management     │
│ • Entity Extract.│ • Optimization   │ • History Tracking       │
└──────────────────┴──────────────────┴──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SIEM Connectors                           │
├────────────┬────────────┬────────────┬─────────────────────────┤
│  Elastic   │   Wazuh    │    Mock    │    Future SIEMs        │
└────────────┴────────────┴────────────┴─────────────────────────┘
```

### 📊 Data Flow Diagram

```
1. User Input → Frontend UI
2. Frontend → API Request (with auth token)
3. API Gateway → Validate & Rate Limit
4. Request → NLP Pipeline
5. NLP → Extract Intent & Entities
6. Query Builder → Generate SIEM Query
7. SIEM Connector → Execute Query
8. Results → Response Formatter
9. Formatted Response → Frontend
10. Frontend → Display to User
```

---

## 3. Frontend Documentation

### 🎨 React Application Structure

#### **Core Components**

##### `App.tsx` - Main Application Component

```typescript
// Entry point managing routing and global state
- Router configuration
- Global theme provider
- Authentication wrapper
- Error boundary
```

##### `ChatWindow.tsx` - Chat Interface

```typescript
// Primary user interaction component
Features:
- Real-time message display
- Input validation
- Auto-scroll functionality
- Message threading
- Query suggestions
```

##### `MessageBubble.tsx` - Message Display

```typescript
// Individual message rendering
Features:
- User/AI message differentiation
- Timestamp display
- Copy functionality
- Syntax highlighting for queries
```

##### `QueryInput.tsx` - User Input Component

```typescript
// Smart input field with enhancements
Features:
- Auto-complete suggestions
- Query templates
- Voice input support (planned)
- Multi-line support
```

#### **Pages**

##### `Chat.tsx` - Main Chat Page

- WebSocket connection management
- Message history
- Real-time updates
- Export functionality

##### `Dashboard.tsx` - Analytics Dashboard

- Security metrics visualization
- Real-time threat indicators
- System health monitoring
- Alert statistics

##### `Reports.tsx` - Report Generation

- Template selection
- Custom report builder
- Export formats (PDF, JSON, CSV)
- Scheduling capabilities

##### `Settings.tsx` - Configuration

- User preferences
- SIEM connection settings
- Notification preferences
- Theme customization

#### **State Management (Zustand)**

```typescript
// useChatStore.ts - Global chat state
interface ChatState {
  messages: Message[]
  sessions: Session[]
  currentSession: string | null
  addMessage: (message: Message) => void
  clearSession: () => void
  loadHistory: (sessionId: string) => void
}
```

#### **API Integration**

```typescript
// services/api.ts - Backend communication
class APIClient {
  - Authentication handling
  - Request/response interceptors
  - Error handling
  - Retry logic
  - WebSocket management
}
```

### 🎨 UI/UX Design Principles

1. **Responsive Design**: Mobile-first approach with breakpoints
2. **Dark Theme**: Optimized for security operations centers
3. **Accessibility**: WCAG 2.1 AA compliance
4. **Performance**: Code splitting, lazy loading, optimized bundles

---

## 4. Backend Documentation

### 🔧 FastAPI Application Architecture

#### **Main Application (`src/api/main.py`)**

```python
# Core FastAPI application with lifespan management
Features:
- Async context manager for startup/shutdown
- Global exception handling
- Middleware pipeline configuration
- Route registration
- Health monitoring
```

#### **Route Modules**

##### `/api/assistant` - Conversational Interface

```python
Endpoints:
POST /chat - Process natural language query
GET /history - Retrieve conversation history
POST /feedback - Submit query feedback
DELETE /session - Clear conversation context
```

##### `/api/query` - Direct Query Interface

```python
Endpoints:
POST /execute - Execute SIEM query
POST /translate - Convert NL to SIEM query
GET /suggestions - Get query suggestions
POST /optimize - Optimize existing query
```

##### `/api/reports` - Report Generation

```python
Endpoints:
POST /generate - Create new report
GET /templates - List report templates
GET /export/{format} - Export report
POST /schedule - Schedule recurring reports
```

##### `/api/auth` - Authentication

```python
Endpoints:
POST /login - User authentication
POST /refresh - Refresh JWT token
POST /logout - Invalidate session
GET /profile - User information
```

##### `/api/admin` - Administration

```python
Endpoints:
GET /users - List all users
POST /users - Create new user
PUT /users/{id} - Update user
DELETE /users/{id} - Remove user
GET /audit - Audit log access
```

#### **Middleware Stack**

1. **Authentication Middleware**
   - JWT token validation
   - Role-based access control
   - Session management

2. **Rate Limiting Middleware**
   - Per-user limits
   - Endpoint-specific limits
   - Sliding window algorithm

3. **Logging Middleware**
   - Request/response logging
   - Performance metrics
   - Error tracking

4. **CORS Middleware**
   - Configurable origins
   - Credential support
   - Preflight handling

---

## 5. NLP Pipeline

### 🧠 Natural Language Processing Components

#### **Intent Classification (`intent_classifier.py`)**

```python
class IntentClassifier:
    """
    Identifies user intent from natural language input
    
    Supported Intents:
    - SEARCH_LOGS: General log search
    - INVESTIGATE_THREAT: Threat investigation
    - GENERATE_REPORT: Report generation
    - ANALYZE_ANOMALY: Anomaly detection
    - CORRELATION_ANALYSIS: Event correlation
    - USER_ACTIVITY: User behavior analysis
    - NETWORK_ANALYSIS: Network traffic analysis
    """
    
    Methods:
    - classify(text: str) -> Intent
    - get_confidence() -> float
    - get_alternatives() -> List[Intent]
```

#### **Entity Extraction (`entity_extractor.py`)**

```python
class EntityExtractor:
    """
    Extracts relevant entities from queries
    
    Entity Types:
    - TIME_RANGE: Temporal references
    - IP_ADDRESS: IP addresses (v4/v6)
    - USERNAME: User identifiers
    - HOSTNAME: System names
    - PORT: Network ports
    - SEVERITY: Alert severity levels
    - EVENT_TYPE: Security event types
    - FILE_PATH: File system paths
    - HASH: File hashes
    """
    
    Methods:
    - extract(text: str) -> List[Entity]
    - normalize_time(text: str) -> datetime
    - validate_entity(entity: Entity) -> bool
```

#### **Schema Mapper (`schema_mapper.py`)**

```python
class SchemaMapper:
    """
    Maps extracted entities to SIEM field names
    
    Features:
    - Dynamic field discovery
    - Platform-specific mappings
    - Fuzzy matching for fields
    - Custom field aliases
    """
    
    Methods:
    - map_to_siem(entities: List[Entity]) -> Dict
    - discover_fields(connector: SIEMConnector) -> Dict
    - add_custom_mapping(alias: str, field: str) -> None
```

#### **Query Optimizer (`query_optimizer.py`)**

```python
class QueryOptimizer:
    """
    Optimizes generated queries for performance
    
    Optimizations:
    - Index usage optimization
    - Time range partitioning
    - Field projection
    - Aggregation pushdown
    - Query caching
    """
    
    Methods:
    - optimize(query: Dict) -> Dict
    - estimate_cost(query: Dict) -> float
    - suggest_improvements(query: Dict) -> List[str]
```

### 🔄 Pipeline Orchestration

```python
class ConversationalPipeline:
    """
    Orchestrates the complete NLP pipeline
    
    Flow:
    1. Input preprocessing
    2. Intent classification
    3. Entity extraction
    4. Context enrichment
    5. Query generation
    6. Query optimization
    7. Execution
    8. Response formatting
    """
    
    async def process(
        self,
        text: str,
        context: Optional[Context] = None
    ) -> Response:
        # Pipeline implementation
```

---

## 6. SIEM Integration

### 🔌 Connector Architecture

#### **Base Connector Interface (`base.py`)**

```python
class BaseSIEMConnector(ABC):
    """
    Abstract base class for SIEM connectors
    
    Required Methods:
    - connect() -> bool
    - disconnect() -> None
    - execute_query(query: Dict) -> Dict
    - get_field_mappings() -> Dict
    - validate_connection() -> bool
    """
```

#### **Elasticsearch Connector (`elastic.py`)**

```python
class ElasticConnector(BaseSIEMConnector):
    """
    Elasticsearch/ELK Stack integration
    
    Features:
    - Multi-index support
    - Aggregation queries
    - Scroll API for large results
    - Index pattern discovery
    - Field mapping auto-detection
    """
    
    Configuration:
    - ELASTICSEARCH_HOST
    - ELASTICSEARCH_PORT
    - ELASTICSEARCH_USERNAME
    - ELASTICSEARCH_PASSWORD
    - ELASTICSEARCH_INDEX
```

#### **Wazuh Connector (`wazuh.py`)**

```python
class WazuhConnector(BaseSIEMConnector):
    """
    Wazuh SIEM integration
    
    Features:
    - Wazuh API v4 support
    - Alert retrieval
    - Agent management queries
    - Rule correlation
    - Vulnerability detection queries
    """
    
    Configuration:
    - WAZUH_API_URL
    - WAZUH_API_USERNAME
    - WAZUH_API_PASSWORD
```

#### **Mock Connector (`mock.py`)**

```python
class MockConnector(BaseSIEMConnector):
    """
    Mock connector for testing and demos
    
    Features:
    - Realistic synthetic data
    - Configurable event generation
    - Query simulation
    - Performance testing support
    """
    
    Data Types:
    - Failed login attempts
    - Malware detections
    - Network anomalies
    - VPN connections
    - File integrity changes
```

#### **Connector Factory (`factory.py`)**

```python
def create_connector(platform: str) -> BaseSIEMConnector:
    """
    Factory pattern for connector creation
    
    Supported Platforms:
    - elasticsearch
    - wazuh
    - mock
    - splunk (future)
    - qradar (future)
    """
```

---

## 7. Security Features

### 🔐 Authentication & Authorization

#### **JWT-based Authentication**

- Access tokens (15 minutes)
- Refresh tokens (7 days)
- Token rotation
- Blacklist management

#### **Role-Based Access Control (RBAC)**

```python
Roles:
- ADMIN: Full system access
- ANALYST: Query and report access
- VIEWER: Read-only access
- AUDITOR: Audit log access
```

#### **Session Management**

- Concurrent session limits
- Session timeout
- Device fingerprinting
- Activity tracking

### 🛡️ Input Validation & Sanitization

#### **Query Sanitization**

- SQL injection prevention
- NoSQL injection prevention
- Command injection prevention
- XSS protection

#### **Rate Limiting**

```python
Limits:
- Global: 1000 requests/hour
- Per-user: 100 requests/minute
- Query endpoint: 60 requests/minute
- Report generation: 10 requests/hour
```

### 📝 Audit Logging

#### **Logged Events**

- Authentication attempts
- Query executions
- Report generations
- Configuration changes
- Data exports
- Permission changes

#### **Log Format**

```json
{
  "timestamp": "2024-10-07T20:30:00Z",
  "user_id": "user123",
  "action": "QUERY_EXECUTE",
  "resource": "/api/query/execute",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "result": "SUCCESS",
  "details": {...}
}
```

---

## 8. API Documentation

### 📡 RESTful API Endpoints

#### **Authentication Endpoints**

##### `POST /api/auth/login`

```json
Request:
{
  "username": "analyst@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

##### `POST /api/auth/refresh`

```json
Request:
{
  "refresh_token": "eyJhbGc..."
}

Response:
{
  "access_token": "eyJhbGc...",
  "expires_in": 900
}
```

#### **Query Endpoints**

##### `POST /api/assistant/chat`

```json
Request:
{
  "query": "Show me failed login attempts from last 24 hours",
  "session_id": "session123",
  "context": {}
}

Response:
{
  "response": "Found 47 failed login attempts...",
  "query_executed": {
    "dsl": {...},
    "index": "security-logs"
  },
  "entities": {
    "time_range": "24 hours",
    "event_type": "authentication_failure"
  },
  "intent": "SEARCH_LOGS",
  "confidence": 0.95,
  "results": [...]
}
```

##### `POST /api/query/execute`

```json
Request:
{
  "platform": "elasticsearch",
  "query": {
    "query": {
      "bool": {
        "must": [...]
      }
    }
  },
  "index": "security-*",
  "size": 100
}

Response:
{
  "hits": [...],
  "total": 245,
  "took": 125,
  "aggregations": {...}
}
```

#### **Report Endpoints**

##### `POST /api/reports/generate`

```json
Request:
{
  "template": "security_summary",
  "time_range": "last_7_days",
  "format": "pdf",
  "parameters": {
    "include_charts": true,
    "detail_level": "high"
  }
}

Response:
{
  "report_id": "report_123",
  "status": "generating",
  "estimated_time": 30,
  "download_url": "/api/reports/download/report_123"
}
```

### 🔄 WebSocket API

#### **Real-time Chat Connection**

```javascript
ws://localhost:8000/ws/chat/{session_id}

Messages:
{
  "type": "query",
  "content": "Show current threats",
  "timestamp": "2024-10-07T20:30:00Z"
}

Events:
- message: New message received
- typing: User typing indicator
- error: Error occurred
- connected: Connection established
- disconnected: Connection lost
```

---

## 9. Deployment Guide

### 🐳 Docker Deployment

#### **Docker Compose Configuration**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SIEM_PLATFORM=mock
      - DATABASE_URL=postgresql://...
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=siem_assistant
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secure_password

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  elasticsearch:
    image: elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
```

#### **Environment Variables**

```bash
# Backend
SIEM_PLATFORM=elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### ☁️ Cloud Deployment

#### **AWS Deployment**

1. **ECS/Fargate** for containerized services
2. **RDS** for PostgreSQL database
3. **ElastiCache** for Redis
4. **ALB** for load balancing
5. **CloudWatch** for monitoring

#### **Azure Deployment**

1. **AKS** for Kubernetes orchestration
2. **Azure Database** for PostgreSQL
3. **Azure Cache** for Redis
4. **Application Gateway** for routing
5. **Azure Monitor** for observability

### 🔧 Production Configuration

#### **Performance Optimization**

- Enable query caching
- Configure connection pooling
- Set appropriate worker counts
- Enable CDN for static assets
- Implement database indexing

#### **Security Hardening**

- Enable HTTPS/TLS
- Configure firewall rules
- Implement secrets management
- Enable audit logging
- Regular security updates

#### **Monitoring & Alerting**

- Application metrics (Prometheus)
- Log aggregation (ELK/Splunk)
- Error tracking (Sentry)
- Uptime monitoring
- Performance monitoring (APM)

---

## 10. Testing Strategy

### 🧪 Testing Levels

#### **Unit Testing**

```python
# Example: Testing Intent Classifier
def test_intent_classification():
    classifier = IntentClassifier()
    result = classifier.classify("Show failed logins")
    assert result.intent == "SEARCH_LOGS"
    assert result.confidence > 0.8
```

#### **Integration Testing**

```python
# Example: Testing API Endpoint
async def test_chat_endpoint():
    response = await client.post(
        "/api/assistant/chat",
        json={"query": "test query"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
```

#### **End-to-End Testing**

```python
# Example: Complete User Flow
def test_user_investigation_flow():
    # 1. Login
    # 2. Submit query
    # 3. Review results
    # 4. Generate report
    # 5. Export data
```

### 📊 Testing Coverage

| Component | Coverage | Status |
|-----------|----------|--------|
| NLP Pipeline | 85% | ✅ |
| API Endpoints | 78% | ✅ |
| SIEM Connectors | 92% | ✅ |
| Frontend Components | 70% | 🔄 |
| Security Features | 88% | ✅ |

### 🔄 Continuous Integration

```yaml
# GitHub Actions Workflow
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: |
          pytest tests/
          npm test
      - name: Coverage Report
        run: |
          coverage report
```

---

## 📚 Additional Resources

### 🔗 Links

- [API Reference](./api-reference.md)
- [Architecture Diagrams](./architecture-diagrams.md)
- [Security Best Practices](./security-guide.md)
- [Troubleshooting Guide](./troubleshooting.md)

### 📖 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Elasticsearch Guide](https://elastic.co/guide/)
- [Wazuh Documentation](https://documentation.wazuh.com/)

### 👥 Team & Support

- **Project Lead**: Samarth Dubey
- **GitHub**: [iSamarthDubey](https://github.com/iSamarthDubey)
- **Team**: Kartavya (SIH 2025)
- **Support**: Open an issue on GitHub

---

*This documentation is maintained by Team Kartavya for the SIEM NLP Assistant project (PS: SIH25173) for Smart India Hackathon 2025.*

*Last Updated: October 2025*
