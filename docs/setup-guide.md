# 🔧 Setup & Installation Guide

Comprehensive setup instructions for the SIEM NLP Assistant.

## System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 11+
- **Python**: 3.10 or higher
- **RAM**: 8GB
- **Storage**: 10GB free space
- **Docker**: Latest version

### Recommended Requirements

- **RAM**: 16GB or higher
- **CPU**: 4+ cores
- **Storage**: 50GB+ SSD
- **Network**: Stable internet connection

## Installation Methods

### Method 1: Docker Compose (Recommended)

Complete setup with all components in containers.

```bash
# Clone repository
git clone https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1.git
cd Kartavya-PS-SIH25173.v1

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Method 2: Local Development Setup

For development and customization.

```bash
# Clone repository
git clone https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1.git
cd Kartavya-PS-SIH25173.v1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start Elasticsearch and Kibana
docker-compose up elasticsearch kibana -d

# Initialize database
python -c "from context_manager.context import ContextManager; ContextManager()"

# Start the backend
python backend/app.py
```

### Method 3: Production Deployment

For production environments with monitoring and scaling.

See [Deployment Guide](./deployment.md) for detailed production setup.

## Component Setup

### 1. Elasticsearch Configuration

Create `elasticsearch.yml` configuration:

```yaml
cluster.name: siem-cluster
node.name: siem-node-1
path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
```

### 2. Kibana Configuration

Create `kibana.yml` configuration:

```yaml
server.name: siem-kibana
server.host: 0.0.0.0
server.port: 5601
elasticsearch.hosts: ["http://elasticsearch:9200"]
```

### 3. Backend Configuration

Create `.env` file:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./siem_contexts.db
DATABASE_CACHE_SIZE=100

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=logs-*
ELASTICSEARCH_TIMEOUT=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Context Manager Configuration
CONTEXT_TTL=3600
CONTEXT_CLEANUP_INTERVAL=300
CONTEXT_MAX_SIZE=1000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=siem_assistant.log
```

## Environment Setup

### Python Dependencies

Core dependencies in `requirements.txt`:

```text
fastapi==0.104.1
uvicorn==0.24.0
elasticsearch==8.11.0
sqlite3
threading
pydantic==2.5.0
python-multipart==0.0.6
aiofiles==23.2.1
python-dotenv==1.0.0
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Development dependencies include:

```text
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.6.0
```

### Docker Environment

Ensure Docker Desktop is running and has sufficient resources:

```bash
# Check Docker status
docker --version
docker-compose --version

# Verify Docker is running
docker info

# Set Docker memory (recommended: 8GB+)
# Docker Desktop > Settings > Resources > Memory
```

## Data Setup

### Sample Data Ingestion

Load sample security logs for testing:

```bash
# Navigate to data directory
cd data

# Load sample logs
python ../scripts/load_sample_data.py

# Verify data in Elasticsearch
curl http://localhost:9200/_cat/indices?v
```

### Custom Data Sources

To add your own data sources:

1. **Log Files**: Place files in `data/logs/` directory
2. **CSV Data**: Use `scripts/csv_to_elasticsearch.py`
3. **Real-time Beats**: Configure beat agents

#### Configuring Filebeat

Create `filebeat.yml`:

```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/*.log
    - /var/log/syslog

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "filebeat-%{+yyyy.MM.dd}"

processors:
- add_host_metadata:
    when.not.contains.tags: forwarded
```

#### Configuring Winlogbeat (Windows)

Create `winlogbeat.yml`:

```yaml
winlogbeat.event_logs:
  - name: Security
    ignore_older: 72h
  - name: System
  - name: Application

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "winlogbeat-%{+yyyy.MM.dd}"
```

## Service Configuration

### systemd Service (Linux)

Create `/etc/systemd/system/siem-assistant.service`:

```ini
[Unit]
Description=SIEM NLP Assistant
After=network.target

[Service]
Type=simple
User=siem
WorkingDirectory=/opt/siem-assistant
Environment=PATH=/opt/siem-assistant/venv/bin
ExecStart=/opt/siem-assistant/venv/bin/python backend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl enable siem-assistant
sudo systemctl start siem-assistant
sudo systemctl status siem-assistant
```

### Windows Service

Install as Windows service using `nssm`:

```cmd
# Download and install NSSM
# https://nssm.cc/download

# Install service
nssm install SIEMAssistant

# Configure service
nssm set SIEMAssistant Application "C:\siem-assistant\venv\Scripts\python.exe"
nssm set SIEMAssistant AppParameters "backend\app.py"
nssm set SIEMAssistant AppDirectory "C:\siem-assistant"

# Start service
nssm start SIEMAssistant
```

## Database Setup

### SQLite Configuration

The context manager uses SQLite with optimized settings:

```python
# Database configuration in context_manager/context.py
DATABASE_CONFIG = {
    'journal_mode': 'WAL',
    'synchronous': 'NORMAL',
    'cache_size': -64000,  # 64MB cache
    'temp_store': 'MEMORY',
    'mmap_size': 268435456,  # 256MB mmap
}
```

### Database Migration

For schema updates:

```bash
# Backup current database
cp siem_contexts.db siem_contexts.db.backup

# Run migration
python scripts/migrate_database.py

# Verify migration
python scripts/verify_database.py
```

## Networking Configuration

### Port Configuration

Default ports used:

- **Backend API**: 8000
- **Elasticsearch**: 9200
- **Kibana**: 5601

### Firewall Rules

Configure firewall for production:

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp
sudo ufw allow 9200/tcp
sudo ufw allow 5601/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=9200/tcp
sudo firewall-cmd --permanent --add-port=5601/tcp
sudo firewall-cmd --reload
```

### Reverse Proxy (nginx)

Configure nginx for production:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /kibana/ {
        proxy_pass http://localhost:5601/;
        proxy_redirect off;
    }
}
```

## Verification Steps

### 1. Service Health Check

```bash
# Check all services
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "components": {
    "api": "up",
    "database": "up",
    "elasticsearch": "up"
  }
}
```

### 2. Test Query

```bash
# Test natural language query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "system health check",
    "user_id": "test_user"
  }'
```

### 3. Database Verification

```bash
# Check database
python -c "
from context_manager.context import ContextManager
cm = ContextManager()
print('Database tables:', cm.list_keys('test'))
"
```

### 4. Elasticsearch Verification

```bash
# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check indices
curl http://localhost:9200/_cat/indices?v
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 9200 in use | `sudo lsof -i :9200` and kill process |
| Permission denied | Check file permissions and user ownership |
| Database locked | Restart backend service |
| Memory issues | Increase Docker memory allocation |

### Logs Location

- **Backend logs**: `logs/siem_assistant.log`
- **Elasticsearch logs**: `docker logs elasticsearch_container`
- **Kibana logs**: `docker logs kibana_container`

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set environment variable
export API_DEBUG=true

# Or in .env file
echo "API_DEBUG=true" >> .env

# Restart service
python backend/app.py
```

## Performance Tuning

### Elasticsearch Optimization

```yaml
# elasticsearch.yml optimizations
indices.memory.index_buffer_size: 20%
thread_pool.write.queue_size: 1000
cluster.routing.allocation.disk.threshold.enabled: false
```

### Backend Optimization

```python
# Backend configuration
CONTEXT_CACHE_SIZE = 1000
ELASTICSEARCH_TIMEOUT = 30
MAX_CONCURRENT_QUERIES = 100
```

### Database Optimization

```sql
-- SQLite optimizations
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;
PRAGMA temp_store = MEMORY;
```

---

Next: [API Reference](./api-reference.md) | [Development Guide](./development.md)
