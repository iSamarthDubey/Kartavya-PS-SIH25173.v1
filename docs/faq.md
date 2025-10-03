# ❓ Frequently Asked Questions

Common questions and answers about the SIEM NLP Assistant.

## General Questions

### What is the SIEM NLP Assistant?

The SIEM NLP Assistant is an intelligent cybersecurity analysis tool that allows security analysts to query SIEM data using natural language. Instead of writing complex Elasticsearch queries, you can ask questions like "Show me failed login attempts from last week" and get immediate, contextual responses.

### Who is this tool for?

- **Security Analysts**: Primary users who need to investigate security events
- **SOC Teams**: Teams monitoring security operations centers
- **IT Administrators**: System administrators tracking security metrics
- **Compliance Officers**: Personnel conducting security audits
- **Developers**: Those building security monitoring solutions

### What makes this different from other SIEM tools?

- **Natural Language Interface**: Query in plain English, no need to learn query languages
- **Conversational Memory**: Multi-turn conversations with context retention
- **Intelligent Analysis**: Automatic threat pattern detection and correlation
- **Easy Integration**: Works with existing Elasticsearch/Kibana setups
- **Open Source**: MIT licensed, fully customizable

## Technical Questions

### What SIEM systems does it support?

Currently supported:

- **Elasticsearch + Kibana** (primary)
- **Wazuh** (integration available)

Planned support:

- **Splunk** (roadmap item)
- **QRadar** (community request)
- **ArcSight** (enterprise feature)

### What are the system requirements?

**Minimum:**

- 8GB RAM, 4 CPU cores
- Python 3.10+, Docker
- 10GB storage

**Recommended:**

- 16GB+ RAM, 8+ CPU cores
- SSD storage
- Dedicated network

### How does the context management work?

The system uses SQLite with WAL mode to store conversation context:

- **Thread-safe operations** with RLock
- **TTL support** for automatic cleanup
- **In-memory caching** for performance
- **Namespace isolation** for multi-user support

Example:

```text
User: "Show failed logins"
System: [Stores: query_type=security, focus=authentication]

User: "From last hour only"
System: [Retrieves context, applies time filter]
```

### Can I use it with existing log data?

Yes! The system works with:

- **Existing Elasticsearch indices**
- **Standard log formats** (JSON, CEF, Syslog)
- **Security event logs** (Windows Event Log, Syslog)
- **Custom log formats** (with configuration)

## Setup and Installation

### Do I need Docker?

**For production**: Yes, Docker Compose is the recommended setup method.

**For development**: Optional, you can run components separately:

- Python backend (local)
- Elasticsearch (Docker or native)
- Kibana (Docker or native)

### How long does setup take?

- **Docker setup**: 10-15 minutes
- **Local development**: 20-30 minutes
- **Production deployment**: 1-2 hours

### What if I don't have sample data?

The system includes:

- **Sample security logs** for testing
- **Data generation scripts** for simulation
- **Integration guides** for common log sources

You can start testing immediately with included sample data.

### Can I run this on Windows?

Yes! Supported on:

- **Windows 10/11** (Docker Desktop required)
- **Windows Server 2019/2022**
- **WSL2** (Linux subsystem)

Special Windows features:

- **Winlogbeat integration** for Windows Event Logs
- **Active Directory log parsing**
- **PowerShell execution logs**

## Usage Questions

### What types of queries can I ask?

**Security Analysis:**

- "Show failed login attempts from last 24 hours"
- "Find suspicious network connections"
- "What users accessed admin accounts today?"

**System Monitoring:**

- "Check system performance metrics"
- "Show disk space warnings"
- "Find service restart events"

**Threat Hunting:**

- "Look for lateral movement indicators"
- "Find processes with unusual network activity"
- "Show file access patterns for user John"

**Compliance:**

- "Show all admin privilege changes this month"
- "Find data access outside business hours"
- "Generate audit trail for user permissions"

### How accurate are the responses?

Accuracy depends on:

- **Query complexity**: Simple queries ~95% accuracy
- **Data quality**: Clean logs = better results
- **Context availability**: More context = better understanding

The system provides:

- **Confidence scores** for results
- **Source queries** for verification
- **Raw data access** for manual review

### Can I customize the responses?

Yes, through:

- **Response templates** in `models/prompts/`
- **Custom formatters** in `backend/services/`
- **Plugin architecture** for extensions

Example customization:

```python
# Custom response formatter
def format_security_alert(data):
    return f"🚨 ALERT: {data['severity']} - {data['description']}"
```

### How do I handle false positives?

- **Feedback system**: Mark results as correct/incorrect
- **Context refinement**: Add more specific context
- **Custom filters**: Create user-specific filters
- **Learning mode**: System improves over time

## Performance and Scaling

### How many queries per second can it handle?

**Single instance:**

- ~100 concurrent users
- ~500 queries per minute
- Response time: 100-500ms

**Scaled deployment:**

- Load balancer + multiple instances
- Shared context database
- Elasticsearch cluster

### How much storage does it use?

**Context database:**

- ~1MB per 1000 conversations
- Automatic cleanup with TTL
- Configurable retention

**Elasticsearch:**

- Depends on log volume
- Typical: 1-10GB per day
- Index lifecycle management recommended

### Can I deploy this in the cloud?

Yes, supported on:

- **AWS**: ECS, EKS, EC2
- **Azure**: Container Instances, AKS
- **GCP**: Cloud Run, GKE
- **Private cloud**: Kubernetes

See [Deployment Guide](./deployment.md) for details.

## Security and Privacy

### Is my data secure?

Security measures:

- **Local deployment**: Data never leaves your environment
- **Encrypted connections**: TLS for all communications
- **Access controls**: Integration with existing auth systems
- **Audit logging**: Full activity logging

### What about compliance?

The system supports:

- **GDPR**: Data retention controls, right to deletion
- **SOX**: Audit trails and access logging
- **HIPAA**: Secure deployment options
- **PCI DSS**: Network isolation and encryption

### How is context data stored?

- **SQLite database**: Local file-based storage
- **No cloud dependencies**: Everything runs locally
- **Encrypted at rest**: Optional disk encryption
- **Regular cleanup**: Automatic TTL expiration

## Troubleshooting

### The system is slow, what can I do?

**Quick fixes:**

1. Check Elasticsearch health: `curl localhost:9200/_cluster/health`
2. Restart context manager: Clear SQLite WAL files
3. Increase memory: Docker memory allocation
4. Check logs: Look for error patterns

**Performance tuning:**

- Increase context cache size
- Optimize Elasticsearch indices
- Use SSD storage
- Scale horizontally

### I'm getting connection errors

**Common solutions:**

1. **Port conflicts**: Check if ports 8000, 9200, 5601 are free
2. **Docker issues**: Restart Docker Desktop
3. **Firewall**: Allow required ports
4. **Network**: Check localhost/container networking

**Debug steps:**

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs elasticsearch
docker-compose logs kibana

# Test connectivity
curl http://localhost:9200
curl http://localhost:8000/health
```

### The responses don't make sense

**Possible causes:**

1. **Poor data quality**: Clean your log data
2. **Missing context**: Provide more specific queries
3. **Wrong time range**: Check timestamp fields
4. **Index problems**: Verify Elasticsearch indices

**Improvement steps:**

- Use more specific queries
- Check Elasticsearch mapping
- Review sample data quality
- Enable debug logging

## Development and Customization

### Can I add custom query types?

Yes! Add new query types in:

- `backend/services/nlp_parser.py` - Intent recognition
- `backend/services/query_generator.py` - Query generation
- `models/prompts/query_template.json` - Response templates

### How do I contribute?

1. **Fork the repository**
2. **Create feature branch**
3. **Follow coding standards** (black, flake8)
4. **Add tests** for new features
5. **Submit pull request**

See [Development Guide](./development.md) for details.

### Can I integrate with other tools?

Yes, through:

- **REST API**: Standard HTTP endpoints
- **Webhooks**: Real-time notifications
- **Plugin system**: Custom extensions
- **SDK libraries**: Python, JavaScript clients

### Is commercial support available?

Currently:

- **Community support**: GitHub issues and discussions
- **Documentation**: Comprehensive guides
- **Self-service**: Open source, full access

Planned:

- **Professional support**: Commercial offering
- **Custom development**: Enterprise features
- **Training**: Team workshops

## Licensing and Legal

### What license is this under?

**MIT License** - You can:

- Use commercially
- Modify freely
- Distribute copies
- Include in proprietary software

Requirements:

- Include license notice
- Include copyright notice

### Can I use this in my company?

Yes! The MIT license allows:

- **Internal use**: Deploy in your organization
- **Commercial use**: Include in products
- **Modification**: Customize as needed
- **Distribution**: Share with clients

### What about third-party dependencies?

All dependencies are compatible:

- **FastAPI**: MIT License
- **Elasticsearch**: Elastic License 2.0
- **SQLite**: Public Domain
- **Python libraries**: Various open source licenses

## Getting Help

### Where can I get support?

1. **Documentation**: Check all guides first
2. **GitHub Issues**: Report bugs and feature requests
3. **GitHub Discussions**: Community Q&A
4. **Email**: <team@kartavya.dev> for urgent issues

### How do I report bugs?

1. **Check existing issues** first
2. **Provide detailed information**:
   - System details (OS, Python version)
   - Error messages and logs
   - Steps to reproduce
   - Expected vs actual behavior

3. **Include relevant files**:
   - Configuration files
   - Log excerpts
   - Sample queries

### Can I request features?

Yes! We welcome:

- **Feature requests**: New capabilities
- **Integration requests**: Additional SIEM support
- **Performance improvements**: Optimization ideas
- **UI enhancements**: Better user experience

Use GitHub Discussions for feature discussions.

---

Still have questions? [Create an issue](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/issues) or [start a discussion](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/discussions)!
