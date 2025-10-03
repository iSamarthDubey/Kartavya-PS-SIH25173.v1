# Docker Setup Notes

## 🐳 **Quick Start**

### Start the Stack

```bash
cd docker
docker-compose up -d
```

### Stop the Stack

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f
```

## 📊 **Services Overview**

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| Elasticsearch | 9200 | Search Engine | <http://localhost:9200> |
| Kibana | 5601 | Visualization | <http://localhost:5601> |
| SIEM Backend | 8000 | API Service | <http://localhost:8000> |
| Logstash | 5044 | Data Pipeline | <http://localhost:9600> |

## 🔧 **Configuration**

### Memory Requirements

- **Minimum**: 4GB RAM
- **Recommended**: 8GB+ RAM

### Elasticsearch Configuration

- Single-node cluster for development
- Security disabled for local testing
- 1GB JVM heap size (adjust based on available memory)

### Environment Variables

Create `.env` file in docker directory:

```bash
# Elasticsearch
ES_JAVA_OPTS=-Xms2g -Xmx2g
ELASTIC_PASSWORD=changeme

# Kibana
KIBANA_PASSWORD=changeme

# SIEM Backend
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
```

## 🔍 **Health Checks**

All services include health checks:

- **Elasticsearch**: Cluster health API
- **Kibana**: Status API  
- **SIEM Backend**: Health endpoint
- **Logstash**: HTTP API

## 📊 **Data Persistence**

- Elasticsearch data is persisted in `elasticsearch-data` volume
- Configuration files mounted from host
- Logs accessible via `docker-compose logs`

## 🐛 **Troubleshooting**

### Common Issues

**1. Elasticsearch won't start:**

```bash
# Check available memory
docker stats
# Increase vm.max_map_count on Linux
sudo sysctl -w vm.max_map_count=262144
```

**2. Out of memory errors:**

```bash
# Reduce heap size in docker-compose.yml
ES_JAVA_OPTS=-Xms512m -Xmx512m
```

**3. Connection refused:**

```bash
# Check if services are running
docker-compose ps
# Check logs for errors
docker-compose logs elasticsearch
```

**4. Port conflicts:**

```bash
# Check what's using the ports
netstat -ano | findstr :9200
# Kill processes or change ports in docker-compose.yml
```

### Performance Tuning

**For Development:**

- Use smaller heap sizes
- Disable replicas
- Reduce refresh intervals

**For Production:**

- Enable security (X-Pack)
- Use dedicated master nodes
- Configure proper backup strategy

## 🔐 **Security Notes**

**Development Mode:**

- Security is disabled for easier setup
- All services accessible without authentication
- Not suitable for production

**Production Mode:**

- Enable X-Pack Security
- Configure TLS/SSL
- Set strong passwords
- Restrict network access

## 📁 **Directory Structure**

```
docker/
├── docker-compose.yml     # Main compose file
├── notes.md              # This file
├── logstash/
│   ├── config/           # Logstash configuration
│   └── pipeline/         # Pipeline definitions
└── .env                  # Environment variables
```

## 🚀 **Next Steps**

1. **Start the stack**: `docker-compose up -d`
2. **Verify services**: Check health endpoints
3. **Configure Beats**: Use beats-config/ templates
4. **Test API**: Send queries to backend service
5. **View data**: Access Kibana dashboard

## 📞 **Support**

For issues:

1. Check service logs: `docker-compose logs [service-name]`
2. Verify health checks: `docker-compose ps`
3. Check resource usage: `docker stats`
4. Review configuration files
