# 🛡️ Kartavya - Conversational SIEM Assistant

> **🚀 Smart India Hackathon 2025 | Problem Statement SIH25173**  
> **🎯 Organization:** Indian Space Research Organisation (ISRO)  
> **🏆 Mission-Critical Cybersecurity for India's Space Program**

---

## 📖 Project Overview

**Kartavya** is a next-generation conversational SIEM (Security Information and Event Management) assistant designed specifically for ISRO's cybersecurity operations. It transforms complex security queries into natural conversations, making advanced SIEM capabilities accessible to security analysts of all skill levels.

### ✨ Key Features

🗣️ **Natural Language Queries** - "Show me failed SSH logins from external IPs in the last hour"  
🔄 **Multi-turn Conversations** - Context-aware follow-up questions  
📊 **Real-time Dashboards** - Live security metrics and threat visualization  
📈 **Automated Reports** - Executive summaries with charts and recommendations  
🔒 **Enterprise Security** - ISRO-grade authentication, encryption, and audit logging  
🌐 **Dual Deployment** - Demo (cloud) and Production (air-gapped) modes

### 🏗️ Architecture Highlights

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Zustand
- **Backend**: FastAPI + Python + Advanced NLP Pipeline
- **SIEM Integration**: Elasticsearch, Wazuh, with extensible connectors
- **Security**: End-to-end encryption, JWT auth, comprehensive audit logging
- **Deployment**: Docker Compose with one-click setup scripts

---

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ & Docker Compose 2.0+
- Git 2.30+
- 8GB RAM minimum (32GB recommended for production)

### One-Click Deployment

```bash
# Clone the repository
git clone https://github.com/your-org/kartavya-siem-assistant.git
cd kartavya-siem-assistant

# Deploy in demo mode (perfect for hackathon)
chmod +x scripts/deploy.sh
./scripts/deploy.sh demo

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Example Queries to Try

```text
"Show me the top 10 security events from today"
"Find all failed login attempts in the last hour"
"What suspicious network activity occurred overnight?"
"Generate a security summary report for this week"
"Are there any malware detections with high severity?"
```

---

## 📚 Documentation

| Document | Description | Target Audience |
|----------|-------------|-----------------|
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Complete setup & deployment instructions | DevOps, IT Administrators |
| **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** | Architecture, APIs, database design | Developers, Architects |
| **[blueprint.txt](blueprint.txt)** | Original project architecture blueprint | Project Managers, Stakeholders |
| **[prompt.txt](prompt.txt)** | System design and requirements | Product Managers, Analysts |

---

## 🎯 Problem Statement: SIH25173

**Challenge**: Traditional SIEM systems are complex and require specialized knowledge, creating barriers for effective cybersecurity monitoring in critical infrastructure organizations like ISRO.

**Solution**: Kartavya transforms SIEM complexity into natural conversations, enabling:
- **Faster Threat Detection** - Natural language queries vs complex query languages
- **Improved Accessibility** - Non-experts can perform advanced security analysis  
- **Enhanced Productivity** - Automated report generation and contextual follow-ups
- **Mission-Critical Security** - Enterprise-grade security for space operations

---

## 🔒 Security & Compliance

### ISRO-Grade Security Features

✅ **Multi-Factor Authentication** - Hardware tokens, OTP support  
✅ **Role-Based Access Control** - Admin, Analyst, Operator, Viewer roles  
✅ **End-to-End Encryption** - AES-256 data encryption, TLS 1.3 transport  
✅ **Comprehensive Audit Logging** - 7-year retention, real-time monitoring  
✅ **Data Classification** - Public, Internal, Confidential, Secret levels  
✅ **Air-Gapped Deployment** - Offline production mode for sensitive environments  

### Compliance Standards
- **Indian Government IT Standards**
- **ISRO Cybersecurity Guidelines**  
- **ISO 27001 Information Security**
- **NIST Cybersecurity Framework**

---

## 🎭 Deployment Modes

### Demo Mode (Cloud-Connected)
Perfect for hackathon demonstrations and development:
- ☁️ Cloud database integrations (Supabase, MongoDB Atlas)
- 🤖 AI-powered features (Gemini/OpenAI APIs) 
- 📊 HuggingFace dataset integration
- 🔄 Real-time log simulation
- 🗺️ Interactive dashboards

### Production Mode (Air-Gapped)
Enterprise deployment for ISRO operations:
- 🔒 Local database instances (PostgreSQL, Redis)
- 🛡️ Enterprise authentication & authorization
- 📋 Comprehensive audit logging  
- 🔐 SSL/TLS encryption
- 🚫 No external dependencies

---

## 🏆 Team & Acknowledgments

**Developed by Team Kartavya for Smart India Hackathon 2025**

### Team Members
- **Samarth Dubey** - Project Lead & Full-Stack Developer
- **[Team Member 2]** - Backend Developer & Security Engineer  
- **[Team Member 3]** - Frontend Developer & UI/UX Designer
- **[Team Member 4]** - DevOps Engineer & System Architect
- **[Team Member 5]** - Data Scientist & NLP Engineer
- **[Team Member 6]** - QA Engineer & Documentation Specialist

### Special Thanks
- **ISRO** for the challenging and impactful problem statement
- **Smart India Hackathon** for fostering innovation in critical sectors
- **Open Source Community** for the amazing tools and libraries

---

## 📠 Support & Contact

### Technical Support
- **📧 Email**: tech-support@kartavya-siem.org
- **🐛 Issues**: [GitHub Issues](https://github.com/your-org/kartavya-siem-assistant/issues)
- **📖 Docs**: [Project Wiki](https://github.com/your-org/kartavya-siem-assistant/wiki)

### Demo & Presentation
- **🎥 Demo Video**: [YouTube Link](#)
- **📊 Presentation**: [Slides Link](#) 
- **🔗 Live Demo**: [Demo Environment](#)

---

## 📄 License

This project is developed for Smart India Hackathon 2025 under Problem Statement SIH25173 for the Indian Space Research Organisation (ISRO).

**All rights reserved.** This software contains proprietary security algorithms and ISRO-specific implementations. Distribution and commercial use require explicit permission.

---

## 🎯 Project Status: Production Ready ✅

> **"From questions to insights - your SIEM, now truly conversational.  
> Security made simple, powerful, and human-centric for ISRO's mission-critical operations."**

**🚀 Ready to secure India's space missions! 🇮🇳**

---

*Last Updated: January 8, 2025 | Version: 1.0.0 | Status: Production Ready*

[![Built with ❤️ for ISRO](https://img.shields.io/badge/Built%20with%20%E2%9D%A4%EF%B8%8F%20for-ISRO-orange.svg)](https://isro.gov.in/)
[![SIH 2025](https://img.shields.io/badge/SIH-2025-blue.svg)](https://sih.gov.in/)
[![Hackathon Winner](https://img.shields.io/badge/Hackathon-Winner-gold.svg)](#)
