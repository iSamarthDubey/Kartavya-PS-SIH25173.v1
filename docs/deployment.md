# 🚀 Deployment Guide

Production deployment strategies for the SIEM NLP Assistant.

## Deployment Options

### 1. Docker Compose (Recommended)

Complete containerized deployment with all services.

**Production docker-compose.yml:**

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: siem-elasticsearch
    environment:
      - node.name=es-node01
      - cluster.name=siem-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - siem-network
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: siem-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - SERVER_NAME=kibana
      - SERVER_HOST=0.0.0.0
    ports:
      - "5601:5601"
    networks:
      - siem-network
    depends_on:
      - elasticsearch
    restart: unless-stopped

  siem-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: siem-api
    environment:
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - DATABASE_URL=sqlite:///data/siem_contexts.db
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    volumes:
      - api_data:/app/data
      - ./logs:/app/logs
    networks:
      - siem-network
    depends_on:
      - elasticsearch
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: siem-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - siem-network
    depends_on:
      - siem-api
      - kibana
    restart: unless-stopped

volumes:
  elasticsearch_data:
    driver: local
  api_data:
    driver: local

networks:
  siem-network:
    driver: bridge
```

**Production Dockerfile:**

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY context_manager/ ./context_manager/
COPY models/ ./models/

# Create necessary directories
RUN mkdir -p data logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes Deployment

**Namespace and ConfigMap:**

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: siem-assistant

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: siem-config
  namespace: siem-assistant
data:
  ELASTICSEARCH_URL: "http://elasticsearch:9200"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
```

**Elasticsearch Deployment:**

```yaml
# k8s/elasticsearch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
  namespace: siem-assistant
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
        ports:
        - containerPort: 9200
        env:
        - name: discovery.type
          value: single-node
        - name: ES_JAVA_OPTS
          value: "-Xms2g -Xmx2g"
        - name: xpack.security.enabled
          value: "false"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: es-data
          mountPath: /usr/share/elasticsearch/data
      volumes:
      - name: es-data
        persistentVolumeClaim:
          claimName: elasticsearch-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  namespace: siem-assistant
spec:
  selector:
    app: elasticsearch
  ports:
  - port: 9200
    targetPort: 9200
  type: ClusterIP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: elasticsearch-pvc
  namespace: siem-assistant
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

**API Deployment:**

```yaml
# k8s/api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: siem-api
  namespace: siem-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: siem-api
  template:
    metadata:
      labels:
        app: siem-api
    spec:
      containers:
      - name: siem-api
        image: your-registry/siem-assistant:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: siem-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: api-data
          mountPath: /app/data
      volumes:
      - name: api-data
        persistentVolumeClaim:
          claimName: api-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: siem-api
  namespace: siem-assistant
spec:
  selector:
    app: siem-api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: api-pvc
  namespace: siem-assistant
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**Ingress Configuration:**

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: siem-ingress
  namespace: siem-assistant
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - siem.yourdomain.com
    secretName: siem-tls
  rules:
  - host: siem.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: siem-api
            port:
              number: 8000
      - path: /kibana
        pathType: Prefix
        backend:
          service:
            name: kibana
            port:
              number: 5601
```

### 3. Cloud Deployments

#### AWS ECS Deployment

**Task Definition:**

```json
{
  "family": "siem-assistant",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "siem-api",
      "image": "your-registry/siem-assistant:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ELASTICSEARCH_URL",
          "value": "https://your-es-domain.us-east-1.es.amazonaws.com"
        },
        {
          "name": "DATABASE_URL",
          "value": "sqlite:///app/data/siem_contexts.db"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "api-data",
          "containerPath": "/app/data"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/siem-assistant",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ],
  "volumes": [
    {
      "name": "api-data",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-12345678",
        "transitEncryption": "ENABLED"
      }
    }
  ]
}
```

#### Azure Container Instances

**ARM Template:**

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "containerGroupName": {
      "type": "string",
      "defaultValue": "siem-assistant"
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]"
    }
  },
  "resources": [
    {
      "type": "Microsoft.ContainerInstance/containerGroups",
      "apiVersion": "2021-09-01",
      "name": "[parameters('containerGroupName')]",
      "location": "[parameters('location')]",
      "properties": {
        "containers": [
          {
            "name": "siem-api",
            "properties": {
              "image": "your-registry/siem-assistant:latest",
              "ports": [
                {
                  "port": 8000
                }
              ],
              "environmentVariables": [
                {
                  "name": "ELASTICSEARCH_URL",
                  "value": "https://your-es-cluster.eastus.azure.elastic-cloud.com"
                }
              ],
              "resources": {
                "requests": {
                  "cpu": 1,
                  "memoryInGb": 2
                }
              }
            }
          }
        ],
        "osType": "Linux",
        "ipAddress": {
          "type": "Public",
          "ports": [
            {
              "protocol": "TCP",
              "port": 8000
            }
          ]
        }
      }
    }
  ]
}
```

## Production Configuration

### Environment Variables

**Production .env file:**

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_WORKERS=4

# Database Configuration
DATABASE_URL=sqlite:///data/siem_contexts.db
DATABASE_CACHE_SIZE=1000
DATABASE_POOL_SIZE=20

# Elasticsearch Configuration
ELASTICSEARCH_URL=https://your-es-cluster.com:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your-secure-password
ELASTICSEARCH_INDEX=logs-*
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3

# Context Manager Configuration
CONTEXT_TTL=3600
CONTEXT_CLEANUP_INTERVAL=300
CONTEXT_MAX_SIZE=10000

# Security Configuration
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=24

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/siem_assistant.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# Performance Configuration
MAX_CONCURRENT_QUERIES=100
QUERY_TIMEOUT=300
CACHE_TTL=300

# Monitoring Configuration
METRICS_ENABLED=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
```

### Security Configuration

**SSL/TLS Setup:**

```nginx
# nginx.conf
server {
    listen 80;
    server_name siem.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name siem.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location /api/ {
        proxy_pass http://siem-api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
    }
    
    location /kibana/ {
        proxy_pass http://kibana:5601/;
        proxy_redirect off;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Rate limiting configuration
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
}
```

**Authentication Integration:**

```python
# backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

# Usage in endpoints
@app.post("/query")
async def process_query(
    request: QueryRequest,
    current_user: str = Depends(verify_token)
):
    # Process query with authenticated user
    pass
```

## Monitoring and Logging

### Application Monitoring

**Prometheus Metrics:**

```python
# backend/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Metrics definitions
query_counter = Counter('siem_queries_total', 'Total number of queries processed')
query_duration = Histogram('siem_query_duration_seconds', 'Time spent processing queries')
active_sessions = Gauge('siem_active_sessions', 'Number of active user sessions')
elasticsearch_errors = Counter('siem_elasticsearch_errors_total', 'Elasticsearch connection errors')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Process request
            await self.app(scope, receive, send)
            
            # Record metrics
            duration = time.time() - start_time
            query_duration.observe(duration)
            
            if scope["path"] == "/query":
                query_counter.inc()

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**Grafana Dashboard Configuration:**

```json
{
  "dashboard": {
    "title": "SIEM Assistant Monitoring",
    "panels": [
      {
        "title": "Query Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(siem_queries_total[5m])",
            "legendFormat": "Queries/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(siem_query_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "type": "singlestat",
        "targets": [
          {
            "expr": "siem_active_sessions",
            "legendFormat": "Sessions"
          }
        ]
      }
    ]
  }
}
```

### Centralized Logging

**ELK Stack Integration:**

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: siem-filebeat
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ./logs:/var/log/siem:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - siem-network
    depends_on:
      - elasticsearch

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: siem-logstash
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    networks:
      - siem-network
    depends_on:
      - elasticsearch
```

**Filebeat Configuration:**

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/siem/*.log
  fields:
    service: siem-assistant
    environment: production

- type: container
  paths:
    - /var/lib/docker/containers/*/*.log
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "siem-logs-%{+yyyy.MM.dd}"

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
```

## Backup and Recovery

### Database Backup

**Automated Backup Script:**

```bash
#!/bin/bash
# backup.sh

# Configuration
DB_PATH="/app/data/siem_contexts.db"
BACKUP_DIR="/backup/database"
RETENTION_DAYS=30
S3_BUCKET="your-backup-bucket"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/siem_contexts_$TIMESTAMP.db"

# SQLite backup
sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

# Compress backup
gzip "$BACKUP_FILE"

# Upload to S3 (optional)
if [ ! -z "$S3_BUCKET" ]; then
    aws s3 cp "$BACKUP_FILE.gz" "s3://$S3_BUCKET/database/"
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "*.db.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

**Scheduled Backup (crontab):**

```bash
# Add to crontab
0 2 * * * /opt/siem-assistant/backup.sh >> /var/log/siem-backup.log 2>&1
```

### Disaster Recovery

**Recovery Procedure:**

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE="$1"
DB_PATH="/app/data/siem_contexts.db"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop services
docker-compose stop siem-api

# Backup current database
cp "$DB_PATH" "$DB_PATH.before_restore"

# Restore from backup
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "$DB_PATH"
else
    cp "$BACKUP_FILE" "$DB_PATH"
fi

# Verify database integrity
sqlite3 "$DB_PATH" "PRAGMA integrity_check;"

# Start services
docker-compose start siem-api

echo "Database restored from $BACKUP_FILE"
```

## Performance Optimization

### Production Tuning

**Elasticsearch Production Settings:**

```yaml
# elasticsearch.yml
cluster.name: siem-production
node.name: es-node-01

# Memory settings
bootstrap.memory_lock: true
indices.memory.index_buffer_size: 30%
indices.memory.min_index_buffer_size: 96mb

# Thread pool settings
thread_pool.write.queue_size: 1000
thread_pool.search.queue_size: 1000

# Discovery settings
discovery.type: single-node
discovery.zen.minimum_master_nodes: 1

# Performance settings
indices.queries.cache.size: 20%
indices.fielddata.cache.size: 40%
```

**Application Performance Settings:**

```python
# backend/config.py
import os

class ProductionConfig:
    # API settings
    WORKERS = int(os.getenv("API_WORKERS", "4"))
    WORKER_CLASS = "uvicorn.workers.UvicornWorker"
    MAX_REQUESTS = 1000
    MAX_REQUESTS_JITTER = 100
    
    # Database settings
    DB_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DB_CACHE_SIZE = int(os.getenv("DATABASE_CACHE_SIZE", "1000"))
    
    # Context manager settings
    CONTEXT_CACHE_SIZE = int(os.getenv("CONTEXT_CACHE_SIZE", "10000"))
    CONTEXT_CLEANUP_INTERVAL = int(os.getenv("CONTEXT_CLEANUP_INTERVAL", "300"))
    
    # Query settings
    MAX_CONCURRENT_QUERIES = int(os.getenv("MAX_CONCURRENT_QUERIES", "100"))
    QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", "300"))
```

## Health Checks

### Comprehensive Health Monitoring

```python
# backend/health.py
from fastapi import APIRouter
import asyncio
import time
from elasticsearch import Elasticsearch

router = APIRouter()

class HealthChecker:
    def __init__(self):
        self.es = Elasticsearch([os.getenv("ELASTICSEARCH_URL")])
        self.last_check = {}
        self.check_interval = 30  # seconds
    
    async def check_elasticsearch(self) -> dict:
        """Check Elasticsearch connectivity and cluster health."""
        try:
            start_time = time.time()
            health = self.es.cluster.health()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if health["status"] in ["green", "yellow"] else "unhealthy",
                "cluster_status": health["status"],
                "nodes": health["number_of_nodes"],
                "response_time": f"{response_time:.3f}s"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_database(self) -> dict:
        """Check database connectivity and integrity."""
        try:
            from context_manager.context import ContextManager
            cm = ContextManager()
            
            # Test write/read operation
            test_key = f"health_check_{int(time.time())}"
            cm.set_context("health", test_key, {"test": True}, ttl=60)
            result = cm.get_context("health", test_key)
            
            return {
                "status": "healthy" if result else "unhealthy",
                "write_test": "passed" if result else "failed"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_memory_usage(self) -> dict:
        """Check memory usage."""
        import psutil
        
        memory = psutil.virtual_memory()
        return {
            "status": "healthy" if memory.percent < 90 else "warning",
            "usage_percent": memory.percent,
            "available_mb": memory.available // 1024 // 1024
        }

health_checker = HealthChecker()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    checks = await asyncio.gather(
        health_checker.check_elasticsearch(),
        health_checker.check_database(),
        health_checker.check_memory_usage(),
        return_exceptions=True
    )
    
    es_health, db_health, memory_health = checks
    
    overall_status = "healthy"
    if any(check.get("status") == "unhealthy" for check in [es_health, db_health, memory_health]):
        overall_status = "unhealthy"
    elif any(check.get("status") == "warning" for check in [es_health, db_health, memory_health]):
        overall_status = "warning"
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "components": {
            "elasticsearch": es_health,
            "database": db_health,
            "memory": memory_health
        }
    }

@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint."""
    es_check = await health_checker.check_elasticsearch()
    db_check = await health_checker.check_database()
    
    if es_check["status"] == "healthy" and db_check["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive", "timestamp": time.time()}
```

## Scaling Strategies

### Horizontal Scaling

**Load Balancer Configuration:**

```nginx
# nginx-lb.conf
upstream siem_api {
    least_conn;
    server siem-api-1:8000 max_fails=3 fail_timeout=30s;
    server siem-api-2:8000 max_fails=3 fail_timeout=30s;
    server siem-api-3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://siem_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}
```

### Auto-scaling with Kubernetes

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: siem-api-hpa
  namespace: siem-assistant
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: siem-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
```

---

This deployment guide provides comprehensive instructions for production deployment. Choose the method that best fits your infrastructure and requirements.