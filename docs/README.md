# 📚 SIEM NLP Assistant - Documentation

**Welcome to the comprehensive documentation for the Kartavya SIEM NLP Assistant!**

This intelligent SIEM analysis tool transforms natural language queries into actionable cybersecurity insights using advanced machine learning and natural language processing.

## 📖 Documentation Structure

**Choose the guide that best fits your needs:**

| Section | Description | Best For |
|---------|-------------|----------|
| **[Quick Start Guide](./quick-start.md)** | Get up and running in 10 minutes | **New Users - Start Here!** |
| **[Architecture Overview](./architecture.md)** | System design and component relationships | **Technical Understanding** |
| **[API Reference](./api-reference.md)** | Complete backend API documentation | **Developers & Integrators** |
| **[Setup & Installation](./setup-guide.md)** | Detailed installation instructions | **System Administrators** |
| **[Development Guide](./development.md)** | For contributors and developers | **Contributors & Maintainers** |
| **[Deployment Guide](./deployment.md)** | Production deployment strategies | **DevOps & Production Teams** |
| **[Troubleshooting](./troubleshooting.md)** | Common issues and solutions | **Support & Maintenance** |
| **[FAQ](./faq.md)** | Frequently asked questions | **Quick Reference** |

## 🎯 What This Project Does

Transform complex SIEM operations into simple conversations:

```text
👤 User: "Show me failed login attempts from last 24 hours"
🤖 Assistant: "Found 47 failed login attempts. Here's the breakdown by user and time..."

👤 User: "Any suspicious activity patterns?"
🤖 Assistant: "Yes, I detected 3 anomalies: unusual login times, geographic inconsistencies..."
```

## 🚀 Key Features

- **Natural Language Processing**: Query your SIEM data in plain English
- **Context-Aware Conversations**: Multi-turn dialogues with memory
- **Advanced Analytics**: Threat detection and anomaly identification  
- **Real-time Monitoring**: Live log analysis and alerting
- **Integration Ready**: Works with Elasticsearch, Kibana, Wazuh
- **Extensible Architecture**: Plugin-based design for custom modules

## 📋 Prerequisites

- Python 3.10+
- Docker & Docker Compose
- 8GB RAM minimum (16GB recommended)
- Windows/Linux/macOS supported

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1.git
cd Kartavya-PS-SIH25173.v1

# Start the SIEM stack
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Run the assistant
python backend/app.py
```

Visit `http://localhost:8000` to start querying!

## 🏗️ Project Structure

```text
Kartavya-PS-SIH25173.v1/
├── backend/           # Core NLP + API service
├── context_manager/   # SQLite-based context storage
├── docs/             # This documentation
├── models/           # Prompt templates & configurations
├── docker/           # Elasticsearch + Kibana setup
└── tests/            # Unit & integration tests
```

## 🤝 Contributing

We welcome contributions! Please read our [Development Guide](./development.md) for:

- Code style guidelines
- Testing requirements
- Pull request process
- Feature request templates

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/discussions)
- **Email**: [Team Kartavya](mailto:team@kartavya.dev)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

### Built with ❤️ by Team Kartavya for SIH 2025