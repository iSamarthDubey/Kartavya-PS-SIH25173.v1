# 🚀 Quick Start Guide

Get your SIEM NLP Assistant up and running in under 10 minutes!

## Prerequisites

- **Python 3.10+**
- **Docker Desktop** (for Elasticsearch & Kibana)
- **8GB RAM** (16GB recommended)
- **Windows/Linux/macOS**

## Step 1: Clone & Setup

```bash
# Clone the repository
git clone https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1.git
cd Kartavya-PS-SIH25173.v1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Start SIEM Infrastructure

```bash
# Start Elasticsearch & Kibana
docker-compose up -d

# Wait for services to be ready (2-3 minutes)
# Check Elasticsearch: http://localhost:9200
# Check Kibana: http://localhost:5601
```

## Step 3: Initialize Context Database

```bash
# Run the context manager setup
python -c "from context_manager.context import ContextManager; cm = ContextManager(); print('✅ Database initialized')"
```

## Step 4: Start the Assistant

```bash
# Start the backend service
python backend/app.py
```

## Step 5: Test Your First Query

Open another terminal and test:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "show system health", "user_id": "test_user"}'
```

## 🎉 Success

Your SIEM NLP Assistant is now running! You can:

- Query in natural language: `"Show failed login attempts"`
- Ask follow-up questions: `"What about in the last hour?"`
- Get threat analysis: `"Any suspicious patterns?"`

## Next Steps

- Read the [Architecture Overview](./architecture.md)
- Explore [API Reference](./api-reference.md)
- Check [Troubleshooting](./troubleshooting.md) if you encounter issues

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 9200 in use | Stop other Elasticsearch instances |
| Database locked | Restart the backend service |
| Memory issues | Increase Docker memory to 8GB+ |

---

Need help? Check our [FAQ](./faq.md) or [create an issue](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/issues).
