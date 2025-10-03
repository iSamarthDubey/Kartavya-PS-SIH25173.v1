# Docker Setup for Kartavya SIEM Assistant

This directory contains Docker configurations for running the complete Kartavya SIEM Assistant stack.

## Quick Start

1. **Start the entire stack:**

   ```bash
   docker-compose up -d
   ```

2. **Access the services:**
   - SIEM Assistant: <http://localhost:8501>
   - Elasticsearch: <http://localhost:9200>
   - Kibana: <http://localhost:5601>

3. **Stop the stack:**

   ```bash
   docker-compose down
   ```

## Services Included

- **Elasticsearch**: SIEM data storage and search
- **Kibana**: Data visualization and analysis
- **Kartavya App**: Main SIEM assistant application
- **Redis**: Session and cache storage

## Configuration

Edit the `.env` file to customize:

- Elasticsearch credentials
- Application settings
- Network configuration

## Data Persistence

Elasticsearch data is persisted in Docker volumes:

- `es_data`: Elasticsearch data
- `redis_data`: Redis data

## Troubleshooting

1. **Port conflicts**: Modify ports in docker-compose.yml
2. **Memory issues**: Increase Docker memory allocation
3. **Logs**: Check logs with `docker-compose logs -f [service_name]`
