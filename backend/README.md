# Backend Service for SIEM NLP Assistant

This backend provides a REST API for the SIEM NLP Assistant, built with FastAPI.

## 🚀 Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the API Server

```bash
python main.py
```

The API will be available at: <http://localhost:8000>

## 📚 API Documentation

### Endpoints

- **GET /**: API information
- **GET /health**: Health check and component status
- **POST /query**: Process natural language queries
- **GET /parser/info**: NLP parser capabilities
- **GET /suggestions**: Get query suggestions

### Interactive Documentation

Visit <http://localhost:8000/docs> for Swagger UI documentation.

## 🔧 Configuration

Environment variables:

- `ELASTICSEARCH_HOST`: Elasticsearch host (default: localhost)
- `ELASTICSEARCH_PORT`: Elasticsearch port (default: 9200)
- `ELASTICSEARCH_USER`: Username for authentication
- `ELASTICSEARCH_PASS`: Password for authentication

## 🏗️ Architecture

```0
Backend Service
├── main.py              # FastAPI application and routes
├── elastic_client.py    # Elasticsearch wrapper
└── requirements.txt     # Python dependencies
```

## 🧪 Example Usage

### Query Processing

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "show me failed login attempts from the last hour",
       "parser_type": "enhanced",
       "max_results": 50
     }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🔗 Integration

This backend integrates with:

- **NLP Parser**: Enhanced ML-based query understanding
- **RAG Pipeline**: Query generation and context retrieval
- **SIEM Connectors**: Elasticsearch and Wazuh integration
- **Response Formatters**: Human-readable result formatting

## 🐳 Docker Deployment

Build and run with Docker:

```bash
docker build -t siem-nlp-backend .
docker run -p 8000:8000 siem-nlp-backend
```
