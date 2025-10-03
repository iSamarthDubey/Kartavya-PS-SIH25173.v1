# 🛠️ Troubleshooting Guide

Common issues and their solutions for the SIEM NLP Assistant.

## Quick Diagnostics

### Health Check Commands

Run these commands to quickly identify issues:

```bash
# Check all services
curl http://localhost:8000/health

# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check Docker containers
docker-compose ps

# Check Python dependencies
python -c "import fastapi, elasticsearch; print('Dependencies OK')"
```

### Common Error Patterns

| Error Pattern | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `Connection refused` | Service not running | Start the service |
| `Port already in use` | Port conflict | Change port or kill process |
| `Database is locked` | Concurrent access issue | Restart backend |
| `Import Error` | Missing dependencies | `pip install -r requirements.txt` |

## Installation Issues

### Docker Problems

#### Docker Desktop Not Starting

**Symptoms:**

- Docker commands fail
- "Docker Desktop starting..." indefinitely

**Solutions:**

Windows:

```powershell
# Restart Docker Desktop
Stop-Process -Name "Docker Desktop" -Force
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Reset Docker Desktop (last resort)
# Docker Desktop > Troubleshoot > Reset to factory defaults
```

Linux:

```bash
# Restart Docker service
sudo systemctl restart docker

# Check Docker status
sudo systemctl status docker

# Fix permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### Container Build Failures

**Symptoms:**

- `docker-compose up` fails
- Build context errors

**Solutions:**

```bash
# Clean Docker cache
docker system prune -a

# Rebuild containers
docker-compose build --no-cache

# Check disk space
df -h
docker system df
```

### Python Environment Issues

#### Import Errors

**Symptoms:**

```text
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**

```bash
# Verify virtual environment
which python
python --version

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Check for conflicts
pip check
```

#### Python Version Compatibility

**Symptoms:**

- Syntax errors in modern Python code
- Feature not available errors

**Solutions:**

```bash
# Check Python version
python --version

# Install Python 3.10+
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.10 python3.10-venv

# Windows: Download from python.org
# macOS: brew install python@3.10
```

## Service Issues

### Backend API Problems

#### API Server Won't Start

**Symptoms:**

```text
uvicorn.error: Error loading ASGI app
```

**Diagnostic Steps:**

```bash
# Check configuration
python -c "from backend.app import app; print('App loads OK')"

# Check port availability
netstat -tlnp | grep 8000

# Start with debug mode
python backend/app.py --debug
```

**Common Solutions:**

1. **Port Conflict:**

```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

2. **Configuration Error:**

```bash
# Check .env file
cat .env

# Verify environment variables
python -c "import os; print(os.environ.get('API_PORT', 'Not set'))"
```

3. **Missing Dependencies:**

```bash
# Install missing packages
pip install fastapi uvicorn python-multipart
```

#### API Returns 500 Errors

**Symptoms:**

- All requests return Internal Server Error
- No specific error message

**Diagnostic Steps:**

```bash
# Check backend logs
tail -f logs/siem_assistant.log

# Enable debug logging
export LOG_LEVEL=DEBUG
python backend/app.py
```

**Common Causes:**

1. **Database Connection:**

```python
# Test database connection
from context_manager.context import ContextManager
cm = ContextManager()
print("Database OK")
```

2. **Elasticsearch Connection:**

```bash
# Test Elasticsearch
curl http://localhost:9200/_cluster/health
```

### Database Issues

#### SQLite Database Locked

**Symptoms:**

```text
sqlite3.OperationalError: database is locked
```

**Solutions:**

1. **Immediate Fix:**

```bash
# Stop backend service
pkill -f "python backend/app.py"

# Remove WAL files
rm siem_contexts.db-wal siem_contexts.db-shm

# Restart service
python backend/app.py
```

2. **Prevention:**

```python
# Ensure proper connection handling
# Check context_manager/context.py for:
# - Connection timeouts
# - Proper connection closing
# - WAL mode configuration
```

#### Database Corruption

**Symptoms:**

- Random database errors
- Inconsistent query results

**Recovery Steps:**

```bash
# Backup current database
cp siem_contexts.db siem_contexts.db.backup

# Check database integrity
sqlite3 siem_contexts.db "PRAGMA integrity_check;"

# Repair if needed
sqlite3 siem_contexts.db ".recover" | sqlite3 recovered.db
mv recovered.db siem_contexts.db
```

### Elasticsearch Issues

#### Elasticsearch Won't Start

**Symptoms:**

- Container exits immediately
- Connection refused errors

**Diagnostic Steps:**

```bash
# Check container logs
docker logs elasticsearch_container

# Check memory allocation
docker stats elasticsearch_container

# Check disk space
df -h
```

**Common Solutions:**

1. **Memory Issues:**

```yaml
# In docker-compose.yml
services:
  elasticsearch:
    environment:
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    mem_limit: 2g
```

2. **Permission Issues:**

```bash
# Fix data directory permissions
sudo chown -R 1000:1000 elasticsearch_data/
```

3. **Port Conflicts:**

```bash
# Check what's using port 9200
sudo lsof -i :9200

# Change port in docker-compose.yml
ports:
  - "9201:9200"
```

#### Elasticsearch Yellow/Red Status

**Symptoms:**

```json
{
  "status": "yellow",
  "number_of_nodes": 1,
  "unassigned_shards": 5
}
```

**Solutions:**

1. **Single Node Setup:**

```bash
# Set discovery type
curl -X PUT "localhost:9200/_cluster/settings" \
  -H 'Content-Type: application/json' \
  -d '{"persistent": {"discovery.type": "single-node"}}'
```

2. **Reduce Replica Count:**

```bash
# Set replicas to 0 for single node
curl -X PUT "localhost:9200/_template/default" \
  -H 'Content-Type: application/json' \
  -d '{"index_patterns": ["*"], "settings": {"number_of_replicas": 0}}'
```

## Performance Issues

### Slow Query Response

**Symptoms:**

- API responses take > 5 seconds
- Timeout errors

**Diagnostic Steps:**

```bash
# Check Elasticsearch performance
curl "localhost:9200/_cat/nodes?v&h=name,cpu,ram.percent,load_1m"

# Check slow queries
curl "localhost:9200/_cat/pending_tasks?v"

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s "localhost:8000/health"
```

**Solutions:**

1. **Elasticsearch Optimization:**

```yaml
# elasticsearch.yml
indices.memory.index_buffer_size: 20%
thread_pool.search.queue_size: 1000
```

2. **Query Optimization:**

```python
# Limit result size
query = {
    "size": 100,  # Instead of default 10000
    "sort": [{"@timestamp": "desc"}]
}
```

3. **Caching:**

```python
# Enable request caching in context manager
CACHE_SIZE = 1000
CACHE_TTL = 300  # 5 minutes
```

### High Memory Usage

**Symptoms:**

- System becomes unresponsive
- Out of memory errors

**Solutions:**

1. **Elasticsearch Memory:**

```yaml
# docker-compose.yml
services:
  elasticsearch:
    environment:
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"  # Limit heap size
```

2. **Context Manager:**

```python
# Reduce cache size
CONTEXT_CACHE_SIZE = 100  # Instead of 1000
CONTEXT_CLEANUP_INTERVAL = 60  # More frequent cleanup
```

3. **System Level:**

```bash
# Monitor memory usage
free -h
docker stats

# Clean system caches
sudo sync && sudo sysctl vm.drop_caches=3
```

## Network Issues

### Connection Refused Errors

**Symptoms:**

```text
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**Diagnostic Steps:**

```bash
# Test network connectivity
ping localhost
telnet localhost 8000
telnet localhost 9200

# Check firewall
sudo ufw status
sudo iptables -L
```

**Solutions:**

1. **Docker Networking:**

```bash
# Check Docker networks
docker network ls
docker network inspect bridge

# Recreate network
docker-compose down
docker network prune
docker-compose up
```

2. **Host Networking:**

```yaml
# Use host networking for development
services:
  api:
    network_mode: "host"
```

### Proxy/Firewall Issues

**Symptoms:**

- Works locally but not remotely
- Intermittent connection issues

**Solutions:**

1. **nginx Configuration:**

```nginx
server {
    listen 80;
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

2. **Firewall Rules:**

```bash
# Allow required ports
sudo ufw allow 8000/tcp
sudo ufw allow 9200/tcp
sudo ufw allow 5601/tcp
```

## Data Issues

### No Search Results

**Symptoms:**

- Queries return empty results
- "No data found" messages

**Diagnostic Steps:**

```bash
# Check if data exists
curl "localhost:9200/_cat/indices?v"
curl "localhost:9200/logs-*/_count"

# Test simple query
curl -X GET "localhost:9200/logs-*/_search?size=1"
```

**Solutions:**

1. **Index Mapping Issues:**

```bash
# Check index mapping
curl "localhost:9200/logs-*/_mapping"

# Look for field naming mismatches
# Common: @timestamp vs timestamp
```

2. **Time Range Issues:**

```bash
# Check document timestamps
curl -X GET "localhost:9200/logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match_all": {}}, "sort": [{"@timestamp": "desc"}], "size": 1}'
```

3. **Data Ingestion:**

```python
# Test data ingestion
from elasticsearch import Elasticsearch
es = Elasticsearch(['localhost:9200'])
doc = {"message": "test", "@timestamp": "2025-10-03T12:00:00Z"}
es.index(index="test-logs", body=doc)
```

### Incorrect Query Generation

**Symptoms:**

- NLP generates wrong Elasticsearch queries
- Results don't match the question

**Diagnostic Steps:**

```bash
# Enable query logging
export LOG_LEVEL=DEBUG

# Check generated queries
curl -X POST "localhost:8000/query" \
  -H 'Content-Type: application/json' \
  -d '{"query": "test query", "user_id": "debug"}' | jq '.data.elasticsearch_query'
```

**Solutions:**

1. **Improve Query Templates:**

```json
// In models/prompts/query_template.json
{
  "security_events": {
    "patterns": ["failed login", "authentication failure"],
    "query_template": {
      "query": {
        "bool": {
          "must": [
            {"match": {"event.action": "logon"}},
            {"match": {"event.outcome": "failure"}}
          ]
        }
      }
    }
  }
}
```

2. **Add Query Validation:**

```python
# In query_generator.py
def validate_query(query):
    """Validate generated Elasticsearch query"""
    try:
        es.indices.validate_query(index="logs-*", body=query)
        return True
    except Exception as e:
        logger.error(f"Invalid query: {e}")
        return False
```

## Development Issues

### Code Changes Not Reflected

**Symptoms:**

- Modified code doesn't seem to be running
- Old behavior persists

**Solutions:**

1. **Python Import Cache:**

```bash
# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Restart Python process
pkill -f "python backend/app.py"
python backend/app.py
```

2. **Docker Cache:**

```bash
# Rebuild containers
docker-compose build --no-cache
docker-compose up
```

### IDE/Editor Issues

**Symptoms:**

- Import errors in IDE
- Autocomplete not working

**Solutions:**

1. **VS Code Configuration:**

```json
// .vscode/settings.json
{
    "python.pythonPath": "./venv/bin/python",
    "python.analysis.extraPaths": ["./backend", "./context_manager"]
}
```

2. **PyCharm Configuration:**

- Mark `backend/` and `context_manager/` as source roots
- Set project interpreter to virtual environment

## Monitoring and Logs

### Log Analysis

**Key Log Files:**

```bash
# Application logs
tail -f logs/siem_assistant.log

# Docker logs
docker-compose logs -f elasticsearch
docker-compose logs -f api

# System logs
journalctl -f -u siem-assistant  # systemd service
```

**Log Patterns to Watch:**

```text
ERROR: Database connection failed
WARNING: Elasticsearch timeout
INFO: Query processing time: 5.23s
DEBUG: Generated query: {...}
```

### Performance Monitoring

**Metrics to Track:**

```bash
# System resources
htop
iostat 1
df -h

# Docker stats
docker stats

# Elasticsearch metrics
curl "localhost:9200/_cat/nodes?v&h=name,cpu,ram.percent"
curl "localhost:9200/_cat/thread_pool/search?v"
```

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Search existing GitHub issues**
3. **Run diagnostic commands**
4. **Collect relevant logs**

### Information to Provide

When reporting issues, include:

```bash
# System information
uname -a
python --version
docker --version

# Service status
curl http://localhost:8000/health
curl http://localhost:9200/_cluster/health

# Error logs (last 50 lines)
tail -50 logs/siem_assistant.log

# Configuration
cat .env (remove sensitive data)
```

### Creating Issue Reports

Use this template:

```markdown
## Problem Description
Brief description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: 
- Python version:
- Docker version:
- Browser (if relevant):

## Logs
```

Paste relevant log output here

```

## Configuration
Paste relevant configuration (remove secrets)
```

---

Still need help? [Create an issue](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/issues) with detailed information!
