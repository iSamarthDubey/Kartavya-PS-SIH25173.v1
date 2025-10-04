# Security Policy

## 🔐 Reporting Security Vulnerabilities

We take the security of the Kartavya SIEM NLP Assistant seriously. If you discover a security vulnerability, please report it responsibly.

### 📧 How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security issues by:

1. **Email**: Send details to the project maintainers (create a private security advisory on GitHub)
2. **GitHub Security Advisory**: Use GitHub's [private vulnerability reporting](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/security/advisories/new)

### 📋 What to Include

When reporting a vulnerability, please include:

- **Type of vulnerability** (e.g., SQL injection, XSS, CSRF)
- **Location** in the code (file and line number)
- **Impact** of the vulnerability
- **Steps to reproduce** the issue
- **Proof of concept** code (if applicable)
- **Suggested fix** (if you have one)

### ⏱️ Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: Next release cycle

## 🛡️ Security Measures

### Current Security Features

✅ **Input Validation**: All user inputs are sanitized
✅ **Parameterized Queries**: Prevents query injection
✅ **Connection Encryption**: SSL/TLS for all connections
✅ **Error Handling**: No sensitive data in error messages
✅ **Dependency Scanning**: Regular security audits

### Planned Security Features

⏳ **Authentication**: API key-based authentication
⏳ **Authorization**: Role-based access control (RBAC)
⏳ **Rate Limiting**: Prevent API abuse
⏳ **Audit Logging**: Track all security-relevant events
⏳ **Session Management**: Secure session handling

## 🔍 Security Best Practices

### For Developers

1. **Never commit secrets** (API keys, passwords, tokens)
2. **Use environment variables** for configuration
3. **Validate all inputs** before processing
4. **Use parameterized queries** for database operations
5. **Keep dependencies updated** regularly
6. **Follow secure coding guidelines**

### For Users

1. **Use strong passwords** for SIEM connections
2. **Keep software updated** to latest version
3. **Use HTTPS** for all connections
4. **Review access logs** regularly
5. **Limit network exposure** when possible

## 📦 Dependency Security

We regularly update dependencies to patch security vulnerabilities:

```bash
# Check for security vulnerabilities
pip install safety
safety check -r requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Known Dependencies with Security Considerations

- **Elasticsearch Client**: Ensure SSL/TLS enabled
- **FastAPI**: Keep updated for security patches
- **Streamlit**: Review for XSS vulnerabilities
- **Requests**: Verify SSL certificates

## 🔐 Data Privacy

### Data Storage

- **Conversation Context**: Stored in SQLite (local)
- **Query History**: Stored in memory/database
- **SIEM Credentials**: Stored in environment variables
- **User Data**: No personal data collected by default

### Data Retention

- **Context Data**: 30 days (configurable)
- **Query Logs**: 90 days (configurable)
- **Error Logs**: 30 days

### Data Deletion

Users can request data deletion by:
1. Clearing conversation history in UI
2. Deleting `siem_contexts.db` file
3. Contacting administrators

## 🚨 Known Issues

### Current Known Issues

No critical security issues at this time.

### Fixed Issues

| Issue | Severity | Fixed In | Description |
|-------|----------|----------|-------------|
| - | - | - | - |

## 🔄 Security Updates

### How to Stay Updated

- **GitHub Watch**: Enable security alerts
- **Release Notes**: Check for security updates
- **Security Advisories**: Monitor GitHub security tab

### Update Process

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
docker-compose restart
```

## 📚 Security Resources

### External Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Project Documentation

- [Architecture Diagram](./docs/ARCHITECTURE_DIAGRAM.md)
- [API Documentation](./docs/README.md#-api-documentation)
- [Deployment Guide](./docs/README.md#-deployment-guide)

## 🏆 Security Hall of Fame

We acknowledge security researchers who responsibly disclose vulnerabilities:

| Researcher | Vulnerability | Date |
|------------|---------------|------|
| - | - | - |

## 📞 Contact

For security concerns:
- GitHub Security Advisory: [Create Advisory](https://github.com/iSamarthDubey/Kartavya-PS-SIH25173.v1/security/advisories/new)
- Email: Use GitHub's private reporting feature

## ✅ Security Checklist

### Before Deployment

- [ ] All secrets removed from code
- [ ] Environment variables configured
- [ ] SSL/TLS enabled for all connections
- [ ] Input validation implemented
- [ ] Error handling reviewed
- [ ] Dependencies updated
- [ ] Security scan completed
- [ ] Logs reviewed for sensitive data

### After Deployment

- [ ] Monitor for suspicious activity
- [ ] Review access logs regularly
- [ ] Keep dependencies updated
- [ ] Perform security audits
- [ ] Test incident response plan

---

**Last Updated**: October 5, 2025  
**Version**: 1.0.0  
**Security Contact**: GitHub Security Advisory

---

**Team Kartavya** | **SIH 2025** | **Problem Statement: SIH25173**

Thank you for helping keep our project secure! 🔒
