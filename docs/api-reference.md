# 📋 API Reference

Complete documentation for the SIEM NLP Assistant API endpoints.

## Base URL

```text
http://localhost:8000
```

## Authentication

Currently, the API uses session-based identification through `user_id` parameter. Authentication integration is planned for production deployment.

## Endpoints

### 1. Query Processing

#### POST `/query`

Process a natural language query and return SIEM insights.

**Request Body:**

```json
{
  "query": "string",
  "user_id": "string",
  "namespace": "string (optional)",
  "context": "object (optional)"
}
```

**Parameters:**

- `query` (required): Natural language query string
- `user_id` (required): Unique identifier for the user session
- `namespace` (optional): Context namespace for isolation (default: "default")
- `context` (optional): Additional context for the query

**Response:**

```json
{
  "status": "success",
  "data": {
    "response": "string",
    "query_type": "string",
    "elasticsearch_query": "object",
    "results": "array",
    "metadata": "object"
  },
  "context_id": "string"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show failed login attempts from last 24 hours",
    "user_id": "analyst_001"
  }'
```

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "response": "Found 47 failed login attempts in the last 24 hours. Here's the breakdown:",
    "query_type": "security_analysis",
    "elasticsearch_query": {
      "query": {
        "bool": {
          "must": [
            {"match": {"event.action": "logon"}},
            {"match": {"event.outcome": "failure"}}
          ],
          "filter": [
            {"range": {"@timestamp": {"gte": "now-24h"}}}
          ]
        }
      }
    },
    "results": [
      {
        "timestamp": "2025-10-03T10:30:00Z",
        "user": "jdoe",
        "source_ip": "192.168.1.100",
        "reason": "invalid_password"
      }
    ],
    "metadata": {
      "total_hits": 47,
      "query_time": "0.045s",
      "sources": ["winlogbeat-*"]
    }
  },
  "context_id": "ctx_12345"
}
```

### 2. Context Management

#### GET `/context/{user_id}`

Retrieve conversation context for a user.

**Parameters:**

- `user_id` (path): User identifier
- `namespace` (query, optional): Context namespace

**Response:**

```json
{
  "status": "success",
  "data": {
    "context": "object",
    "last_updated": "string",
    "expires_at": "string"
  }
}
```

#### POST `/context/{user_id}`

Set or update conversation context.

**Request Body:**

```json
{
  "context": "object",
  "ttl": "number (optional)",
  "namespace": "string (optional)"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Context updated successfully"
}
```

#### DELETE `/context/{user_id}`

Clear conversation context for a user.

**Response:**

```json
{
  "status": "success",
  "message": "Context cleared successfully"
}
```

### 3. Health & Status

#### GET `/health`

Check system health and connectivity.

**Response:**

```json
{
  "status": "healthy",
  "components": {
    "api": "up",
    "database": "up",
    "elasticsearch": "up",
    "cache": "up"
  },
  "timestamp": "2025-10-03T15:30:00Z"
}
```

#### GET `/metrics`

Get system performance metrics.

**Response:**

```json
{
  "status": "success",
  "data": {
    "queries_processed": 1250,
    "active_sessions": 15,
    "database_size": "2.4MB",
    "cache_hit_rate": 0.85,
    "avg_response_time": "0.12s"
  }
}
```

### 4. Search & Discovery

#### GET `/search`

Search through conversation history and context.

**Parameters:**

- `q` (query): Search query string
- `user_id` (query, optional): Filter by user
- `namespace` (query, optional): Filter by namespace
- `limit` (query, optional): Result limit (default: 10)

**Response:**

```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "key": "string",
        "value": "object",
        "namespace": "string",
        "created_at": "string",
        "relevance": 0.95
      }
    ],
    "total": 25,
    "page": 1
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  },
  "timestamp": "string"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_QUERY` | Malformed query parameter | 400 |
| `USER_NOT_FOUND` | User ID not found | 404 |
| `CONTEXT_EXPIRED` | Context has expired | 410 |
| `ELASTICSEARCH_ERROR` | SIEM connection failed | 503 |
| `DATABASE_ERROR` | Context storage failed | 503 |
| `RATE_LIMITED` | Too many requests | 429 |

### Example Error Response

```json
{
  "status": "error",
  "error": {
    "code": "ELASTICSEARCH_ERROR",
    "message": "Failed to connect to Elasticsearch",
    "details": {
      "elasticsearch_url": "http://localhost:9200",
      "error": "Connection refused"
    }
  },
  "timestamp": "2025-10-03T15:30:00Z"
}
```

## Rate Limiting

Current rate limits (planned for production):

- **Query endpoint**: 100 requests per minute per user
- **Context endpoints**: 200 requests per minute per user
- **Search endpoint**: 50 requests per minute per user

Rate limit headers:

```text
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1696348200
```

## Query Types

The system recognizes various query types automatically:

| Type | Description | Example |
|------|-------------|---------|
| `security_analysis` | Security events and threats | "Show failed logins" |
| `system_monitoring` | System health and performance | "CPU usage last hour" |
| `log_search` | General log searching | "Find errors in apache logs" |
| `threat_hunting` | Proactive threat detection | "Suspicious network activity" |
| `compliance` | Compliance and audit queries | "Show admin access changes" |

## Elasticsearch Query Generation

The system automatically generates optimized Elasticsearch queries based on natural language input.

### Query Structure

```json
{
  "query": {
    "bool": {
      "must": [],
      "filter": [],
      "should": [],
      "must_not": []
    }
  },
  "aggs": {},
  "sort": [],
  "_source": [],
  "size": 100
}
```

### Time Range Handling

Natural language time expressions are converted to Elasticsearch date filters:

- "last hour" → `{"gte": "now-1h"}`
- "yesterday" → `{"gte": "now-1d/d", "lt": "now/d"}`
- "this week" → `{"gte": "now/w"}`

## SDK Examples

### Python SDK Usage

```python
import requests

class SIEMAssistant:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def query(self, text, user_id, namespace="default"):
        response = requests.post(f"{self.base_url}/query", json={
            "query": text,
            "user_id": user_id,
            "namespace": namespace
        })
        return response.json()
    
    def get_context(self, user_id, namespace="default"):
        response = requests.get(f"{self.base_url}/context/{user_id}", 
                              params={"namespace": namespace})
        return response.json()

# Usage
assistant = SIEMAssistant()
result = assistant.query("Show network anomalies", "analyst_001")
print(result["data"]["response"])
```

### JavaScript SDK Usage

```javascript
class SIEMAssistant {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async query(text, userId, namespace = 'default') {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: text,
        user_id: userId,
        namespace: namespace
      })
    });
    return await response.json();
  }
  
  async getContext(userId, namespace = 'default') {
    const response = await fetch(`${this.baseUrl}/context/${userId}?namespace=${namespace}`);
    return await response.json();
  }
}

// Usage
const assistant = new SIEMAssistant();
const result = await assistant.query('Show failed authentications', 'analyst_001');
console.log(result.data.response);
```

---

Next: [Setup Guide](./setup-guide.md) | [Troubleshooting](./troubleshooting.md)
