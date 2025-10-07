# Kartavya SIEM Assistant 🛡️

**NLP-powered Conversational SIEM Assistant for ISRO**

## 🎯 Overview

Kartavya is an advanced Natural Language Processing (NLP) powered assistant that provides a conversational interface for SIEM (Security Information and Event Management) systems, specifically designed for Elastic SIEM and Wazuh platforms.

## ✨ Features

- **Natural Language Queries**: Convert plain English to Elasticsearch DSL/KQL
- **Multi-turn Conversations**: Maintain context across multiple queries
- **Automated Report Generation**: Generate security reports with charts and narratives
- **Real-time Threat Investigation**: Investigate security incidents conversationally
- **Schema-aware Query Generation**: Intelligent mapping to SIEM schema
- **Security-first Design**: Built for government/enterprise environments

## 🏗️ Architecture

```
kartavya-siem/
├── backend/          # FastAPI backend (Port 8001)
├── frontend/         # React frontend (Port 3000)  
├── deployment/       # Docker & Kubernetes configs
├── docs/            # Documentation
├── scripts/         # Utility scripts
└── tests/           # Test suites
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Elasticsearch 8.x or Wazuh 4.x

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/isro/kartavya-siem
   cd kartavya-siem
   ```

2. **Set up environment**
   ```bash
   cp deployment/.env.example deployment/.env
   # Edit deployment/.env with your configurations
   ```

3. **Start with Docker Compose**
   ```bash
   cd deployment
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

## 📖 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Development Guide](docs/DEVELOPMENT.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/backend/unit/
pytest tests/backend/integration/
pytest tests/e2e/
```

## 🔒 Security

This application is designed for government/enterprise environments with:
- Role-based access control (RBAC)
- API authentication & authorization
- Audit logging
- Data encryption
- Query validation & sanitization

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📞 Support

For issues and questions, please use the GitHub issue tracker.

---
**Built for ISRO | SIH 2025 | Problem Statement #25173**
