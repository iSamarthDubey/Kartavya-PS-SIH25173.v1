# 📦 Dependencies & Installation Guide

This document explains the different requirements files and installation options for the SIEM NLP Assistant project.

## 📋 Requirements Files Overview

| File | Purpose | Use Case |
|------|---------|----------|
| `requirements.txt` | **Main dependencies** | Development & full feature set |
| `backend/requirements.txt` | **Backend service only** | FastAPI backend deployment |
| `requirements-prod.txt` | **Production optimized** | Production deployments |
| `requirements-docker.txt` | **Container optimized** | Docker deployments |
| `requirements-dev.txt` | **Development tools** | Development workflow |

## 🚀 Quick Installation

### **Option 1: Automated Installation (Recommended)**

```bash
# Development environment (full features)
python install_dependencies.py --env development --verify

# Production environment (optimized)
python install_dependencies.py --env production --verify

# Backend service only
python install_dependencies.py --env backend --verify
```

### **Option 2: Manual Installation**

```bash
# Development (recommended for local development)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Production deployment
pip install -r requirements-prod.txt

# Backend service only
pip install -r backend/requirements.txt

# Docker container
pip install -r requirements-docker.txt
```

## 🔧 Environment-Specific Setup

### **Development Environment**

Full feature set with development tools:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### **Production Environment**

Optimized for production with minimal dependencies:

```bash
pip install -r requirements-prod.txt
python -m spacy download en_core_web_sm
```

### **Docker Container**

Pinned versions for consistent container builds:

```bash
pip install -r requirements-docker.txt
```

### **Backend Service Only**

Minimal FastAPI backend dependencies:

```bash
pip install -r backend/requirements.txt
```

## 📊 Package Categories

### **Core Framework**

- **Streamlit** (1.50.0+): Interactive web dashboard
- **FastAPI** (0.118.0+): REST API framework
- **Uvicorn** (0.37.0+): ASGI server

### **Machine Learning & AI**

- **PyTorch** (2.8.0+): Deep learning framework
- **Transformers** (4.56.0+): Hugging Face transformer models
- **Sentence-Transformers** (5.1.0+): Semantic embeddings
- **Scikit-learn** (1.7.0+): Traditional ML algorithms

### **Natural Language Processing**

- **spaCy** (3.8.0+): Industrial NLP library
- **NLTK** (3.9.0+): Natural Language Toolkit
- **TextStat** (0.7.10+): Text statistics

### **Search & Data**

- **Elasticsearch** (9.1.0+): Search engine client
- **FAISS** (1.12.0+): Vector similarity search
- **Pandas** (2.3.0+): Data manipulation
- **NumPy** (2.3.0+): Numerical computing

### **Security & Authentication**

- **Cryptography** (43.0.0+): Cryptographic operations
- **BCrypt** (4.3.0+): Password hashing
- **Python-JOSE** (3.3.0+): JWT token handling

### **Development Tools**

- **Pytest** (8.4.0+): Testing framework
- **Black** (25.9.0+): Code formatter
- **Flake8** (7.3.0+): Linting
- **MyPy** (1.12.0+): Type checking

## ⚡ Performance Optimization

### **Production Optimizations**

- Pinned major versions for stability
- Minimal dependency set
- CPU-optimized ML libraries
- Structured logging for monitoring

### **Docker Optimizations**

- Exact version pinning
- CPU-only PyTorch variant
- Reduced image size
- Process management tools

### **Memory Management**

- FAISS CPU variant (lower memory)
- Caching utilities included
- Async operations support

## 🔍 Verification & Testing

### **Verify Installation**

```bash
python install_dependencies.py --verify
```

### **Test Core Functionality**

```bash
# Test imports
python -c "from nlp_parser.parser import NLPParser; print('✅ NLP Parser OK')"
python -c "from siem_connector.elastic_connector import ElasticConnector; print('✅ SIEM Connector OK')"
python -c "import streamlit, fastapi, torch; print('✅ Core frameworks OK')"

# Run tests
pytest tests/

# Check code quality
black --check .
flake8 .
```

## 🐳 Docker Deployment

### **Build with Optimized Requirements**

```dockerfile
# Dockerfile uses requirements-docker.txt for optimal container size
FROM python:3.11-slim
COPY requirements-docker.txt requirements.txt
RUN pip install -r requirements.txt
```

### **Docker Compose**

```bash
# Uses optimized requirements automatically
docker-compose up --build
```

## 📈 Version Management

### **Version Pinning Strategy**

- **Development**: Minimum versions (>=) for latest features
- **Production**: Major version pinning for stability
- **Docker**: Exact versions for reproducible builds

### **Upgrade Guidelines**

```bash
# Check for outdated packages
pip list --outdated

# Upgrade specific packages
pip install --upgrade package_name

# Regenerate requirements
pip freeze > requirements-updated.txt
```

## ❓ Troubleshooting

### **Common Issues**

**PyTorch Installation**

```bash
# For CPU-only (recommended for most deployments)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**spaCy Model Missing**

```bash
python -m spacy download en_core_web_sm
```

**NLTK Data Missing**

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

**Elasticsearch Connection**

```bash
# Verify Elasticsearch is running
curl -X GET "localhost:9200/"
```

### **Dependency Conflicts**

```bash
# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # or fresh_env\Scripts\activate on Windows
pip install -r requirements.txt
```

## 🎯 Environment Variables

Create a `.env` file with:

```env
# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=siem-logs

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
```

---

For issues or questions, please check the main README.md or create an issue in the repository.
