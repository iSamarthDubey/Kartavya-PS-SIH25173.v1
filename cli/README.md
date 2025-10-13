# Kartavya CLI

🔒 **Production-ready command line interface for the Kartavya SIEM NLP Assistant**

A comprehensive CLI tool for interacting with the Kartavya SIEM NLP Assistant, enabling security operations, threat hunting, and incident response through natural language queries and automated reporting.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🤖 AI-Powered Chat Interface**: Natural language queries for security investigations
- **🔍 Platform Events**: Query authentication, network, system, and process events
- **📊 Automated Reports**: Generate, schedule, and export security reports
- **⚡ Query Optimization**: Translate and optimize SIEM queries
- **📈 Dashboard Integration**: Access metrics, alerts, and system status  
- **⚙️ Admin Tools**: User management and audit logging
- **🎨 Rich Output**: Beautiful tables, JSON, CSV formats with colored output
- **🔧 Flexible Configuration**: File-based and environment variable configuration

## 🚀 Quick Start

### Installation

#### Option 1: Install from PyPI (Recommended)
```bash
pip install kartavya-cli
```

#### Option 2: Install from Source
```bash
git clone <repository-url>
cd cli
pip install -e .
```

#### Option 3: Using pipx (Isolated Installation)
```bash
pipx install kartavya-cli
```

### Initial Setup

1. **Configure the CLI:**
   ```bash
   kartavya setup
   ```
   
2. **Test connectivity:**
   ```bash
   kartavya health
   ```

3. **Start chatting with the AI:**
   ```bash
   kartavya chat ask "show failed login attempts from last hour"
   ```

## 📖 Usage Examples

### Interactive Chat
```bash
# Start interactive chat session
kartavya chat interactive

# Ask specific questions
kartavya chat ask "What are the top security threats today?"
kartavya chat ask "Show malware alerts with high severity"
```

### Platform Events
```bash
# Get authentication events
kartavya events auth --time-range 1h --limit 50

# Search failed logins
kartavya events failed-logins --query "admin" --time-range 24h

# Network activity analysis
kartavya events network --time-range 30m --output json
```

### Reports
```bash
# Generate security summary
kartavya reports security-summary --time-range 24h --save report.json

# Create incident report
kartavya reports incident-report --severity critical --save incidents.pdf

# Schedule daily reports
kartavya reports schedule security_summary --schedule daily --email admin@company.com
```

### Query Operations
```bash
# Execute natural language query
kartavya query execute "find suspicious PowerShell execution"

# Translate to SIEM query
kartavya query translate "failed SSH logins from external IPs"

# Get query suggestions
kartavya query suggestions --category security_events

# Optimize existing query
kartavya query optimize "select * from events where severity=high"
```

### Dashboard & Monitoring
```bash
# Get security metrics
kartavya dashboard metrics --time-range 7d

# View active alerts
kartavya dashboard alerts --severity critical --limit 20

# Check system status
kartavya dashboard status
```

## 🔧 Configuration

### Configuration File
The CLI stores configuration in a TOML file:
- **Windows**: `%APPDATA%\kartavya-cli\config.toml`
- **macOS**: `~/Library/Application Support/kartavya-cli/config.toml`  
- **Linux**: `~/.config/kartavya-cli/config.toml`

### Environment Variables
Override settings using environment variables:
```bash
export KARTAVYA_API_URL="https://your-api.com"
export KARTAVYA_API_TOKEN="your-secret-token"
export KARTAVYA_OUTPUT_FORMAT="json"
export KARTAVYA_COLOR="true"
```

### Configuration Commands
```bash
# Show current configuration
kartavya config show

# Set configuration values
kartavya config set --api-url "http://localhost:8000" --token "your-token"

# Validate configuration
kartavya config validate

# Reset to defaults
kartavya config reset
```

## 🌐 Deployment Options

### 1. Replit Deployment

[![Run on Replit](https://replit.com/badge/github/@yourusername/kartavya-cli)](https://replit.com/@yourusername/kartavya-cli)

1. Fork this repository on Replit
2. Install dependencies: `pip install -e .`
3. Configure: `kartavya setup`
4. Start using: `kartavya chat interactive`

### 2. Render Deployment

Deploy as a web service on Render:

1. Connect your GitHub repository to Render
2. Use the provided `render.yaml` configuration
3. Set environment variables in Render dashboard
4. Access via web terminal or API

### 3. Docker Deployment

```bash
# Build image
docker build -t kartavya-cli .

# Run interactively
docker run -it kartavya-cli kartavya chat interactive

# Run with mounted config
docker run -it -v ~/.config/kartavya-cli:/root/.config/kartavya-cli kartavya-cli
```

## 🎯 Command Reference

### Main Commands
- `kartavya chat` - Chat with AI assistant
- `kartavya events` - Query platform security events
- `kartavya reports` - Generate and manage reports
- `kartavya query` - Execute and optimize queries
- `kartavya dashboard` - Dashboard metrics and alerts
- `kartavya admin` - Administrative commands
- `kartavya config` - Configuration management

### Global Options
- `--verbose, -v` - Enable verbose output
- `--output, -o` - Output format (table, json, csv)
- `--no-color` - Disable colored output
- `--api-url` - Override API URL
- `--token` - Override API token

### Help System
- `kartavya --help` - Main help
- `kartavya COMMAND --help` - Command-specific help
- `kartavya COMMAND SUBCOMMAND --help` - Subcommand help

## 🔗 API Integration

The CLI communicates with the Kartavya SIEM NLP Assistant API. Supported endpoints:

- **Chat**: `/api/assistant/chat`
- **Platform Events**: `/api/events/*`
- **Reports**: `/api/reports/*`
- **Queries**: `/api/query/*`
- **Dashboard**: `/api/dashboard/*`
- **Admin**: `/api/admin/*`

## 🛡️ Security Features

- **Token-based Authentication**: Secure API access
- **Credential Management**: Safe storage of sensitive data
- **Input Validation**: Query safety and validation
- **Audit Logging**: Track all administrative actions
- **Environment Isolation**: Support for multiple environments

## 🎨 Output Formats

### Table Format (Default)
Beautiful, colored tables with proper alignment:
```
┌─────────────────┬──────────────┬──────────┐
│ Timestamp       │ Event Type   │ Severity │
├─────────────────┼──────────────┼──────────┤
│ 2024-01-15 10:30│ Failed Login │ High     │
└─────────────────┴──────────────┴──────────┘
```

### JSON Format
Perfect for scripting and automation:
```json
{
  "success": true,
  "data": {
    "events": [...]
  }
}
```

### CSV Format
Easy import into spreadsheets:
```csv
timestamp,event_type,severity
2024-01-15 10:30,Failed Login,High
```

## 🚨 Error Handling

The CLI provides comprehensive error handling:
- **Connection Errors**: Clear messages for API connectivity issues
- **Authentication Errors**: Guidance for token configuration
- **Validation Errors**: Helpful suggestions for query improvements
- **Rate Limiting**: Automatic retry with backoff
- **Timeout Handling**: Configurable timeout settings

## 🔄 Automation & Scripting

### Bash/PowerShell Integration
```bash
# Get critical alerts and save to file
kartavya dashboard alerts --severity critical --output json > alerts.json

# Generate daily report
kartavya reports security-summary --time-range 24h --save "report-$(date +%Y-%m-%d).json"

# Check system health in scripts
if kartavya health --quiet; then
  echo "System is healthy"
else
  echo "System has issues"
fi
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Security Scan
  run: |
    kartavya config set --api-url "${{ secrets.KARTAVYA_URL }}" --token "${{ secrets.KARTAVYA_TOKEN }}"
    kartavya query execute "security scan results" --output json > security-report.json
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**
   ```bash
   kartavya health --verbose
   kartavya config validate
   ```

2. **Authentication Issues**
   ```bash
   kartavya config set --token "your-new-token"
   ```

3. **Configuration Problems**
   ```bash
   kartavya config show
   kartavya config reset
   ```

4. **Performance Issues**
   ```bash
   kartavya config set --timeout 60
   ```

### Debug Mode
```bash
export KARTAVYA_VERBOSE=true
kartavya --verbose COMMAND
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone <repository-url>
cd cli
pip install -e ".[dev]"
pre-commit install
```

### Running Tests
```bash
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.kartavya.dev](https://docs.kartavya.dev)
- **Issues**: [GitHub Issues](https://github.com/kartavya-team/kartavya-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kartavya-team/kartavya-cli/discussions)
- **Email**: support@kartavya.dev

## 🎯 Roadmap

- [ ] Plugin system for custom commands
- [ ] Multi-language support
- [ ] Advanced visualization features
- [ ] Integration with more SIEM platforms
- [ ] Mobile app companion
- [ ] AI-powered query suggestions

---

**Made with ❤️ by the Kartavya Team**

*Kartavya CLI - Empowering security operations through intelligent automation*
