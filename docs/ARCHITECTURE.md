# Kartavya SIEM Assistant - Architecture

## System Architecture

### Overview
Kartavya follows a microservices architecture with clear separation between frontend, backend, and data layers.

### Components

#### 1. Backend (FastAPI)
- **Core Module**: NLP processing, SIEM connectors, security
- **API Module**: RESTful API endpoints
- **Services Module**: Business logic, query pipeline, context management
- **Models Module**: Pydantic schemas for validation

#### 2. Frontend (React + TypeScript)
- **Components**: Reusable UI components
- **Services**: API integration layer
- **Hooks**: Custom React hooks
- **State Management**: Context API / Redux

#### 3. Data Layer
- **Elasticsearch**: Primary SIEM data store
- **Redis**: Session cache and context storage
- **PostgreSQL**: User management and audit logs (optional)

### Data Flow

1. User enters natural language query in frontend
2. Frontend sends query to backend API
3. Backend processes query through NLP pipeline
4. NLP extracts intent and entities
5. Query builder converts to Elasticsearch DSL
6. SIEM connector executes query
7. Response formatter processes results
8. Frontend displays results with visualizations

### Security Architecture

- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS for all communications
- **Audit**: All queries and actions logged
- **Validation**: Input sanitization and query validation

### Scalability

- Horizontal scaling via Kubernetes
- Load balancing with nginx
- Caching with Redis
- Async processing for heavy queries
- Rate limiting and throttling
