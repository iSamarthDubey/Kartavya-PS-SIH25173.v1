# Project Details

> _This project is being developed for the Smart India Hackathon (SIH) 2025, under the following problem statement:_

> _**Problem Statement Title:** Conversational SIEM Assistant for Investigation and Automated Threat Reporting using NLP  <br>
> **PS Number:** SIH25173  <br>
> **Organization:** Indian Space Research Organisation (ISRO)  <br>
> **Department:** Department of Space (DoS)  <br>
> **Theme:** Blockchain & Cybersecurity  <br>_

The goal is to provide a natural language interface for ELK-based SIEMs (Elastic SIEM, Wazuh), enabling conversational investigations and automated threat reporting without requiring users to know query syntax.

---

## Overview

SIEM NLP Assistant bridges the gap between users and ELK-based SIEMs (Elastic SIEM, Wazuh) by enabling natural language investigations and automated threat reporting. Users can ask questions or request reports in plain English, and the assistant translates these into optimized SIEM queries—no query syntax required.

**Key Capabilities:**

- Multi-turn, context-aware conversational investigations
- Automated report generation (text, tables, charts)
- Works with both Elastic SIEM and Wazuh (via APIs)
- No changes required to SIEM core

---

## Features

- 🔍 **Conversational Investigations:**
  - Multi-turn queries (e.g., “What suspicious login attempts occurred yesterday?” → “Filter only VPN-related attempts.”)
  - Context preserved across follow-ups
  - Translates natural language to Elasticsearch DSL/KQL

- 📊 **Automated Report Generation:**
  - Request summaries or charts in natural language
  - Aggregates and presents results as narratives, tables, or visuals

- 🧠 **NLP & Query Engine:**
  - Advanced entity/intent extraction
  - Handles ambiguous/relative terms (“last week”, “unusual activity”)
  - Intelligent error handling and feedback

- ⚡ **SIEM Integration:**
  - Connects to Elastic SIEM and Wazuh via REST APIs
  - Efficient, optimized query generation
- 🔐 **Security-First API Surface:**
  - Token-based authentication with role-based access control
  - Per-route rate limiting and audit logging for sensitive actions
  - Query sanitization guards against injection-style payloads

---

## Architecture

- **NLP Parser:** Understands natural language inputs
- **Query Generator:** Maps parsed intent to Elasticsearch DSL/KQL
- **SIEM Connector:** Interfaces with Elastic/Wazuh APIs
- **Response Formatter:** Converts results to text, tables, or charts
- **Context Manager:** Maintains dialogue history for iterative queries

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Docker & Docker Compose (recommended)
- Elastic SIEM and/or Wazuh instance (local or remote)

### 2. Automated Setup

Run the following command in your project directory:

```bash
python setup.py
```

This script will:

- Check/install all Python dependencies
- Set up Docker containers (if you choose)
- Prepare the environment for first use
- Optionally launch the app for you

**Note:** If you encounter any issues, see the README or run the manual steps below.

### 3. Manual Steps (if needed)

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Download spaCy model:**

```bash
python -m spacy download en_core_web_sm
```

**Start Docker services:**

```bash
cd docker
docker-compose up -d
```

**Launch the app:**

```bash
python app.py
```

The default demo interface is Streamlit. (A dedicated dashboard is planned for production.)

---

## Security & Authentication

- **Bootstrap Admin:** The service auto-creates an `admin` user on first launch.
  - Username: `admin`
  - Password: `Admin!2025` (override via `ASSISTANT_ADMIN_PASSWORD` env var)
- **Session Tokens:** Call `/assistant/auth/login` to retrieve a bearer token, then send it via the `Authorization: Bearer <token>` header on every request.
- **RBAC:** Core endpoints enforce permissions such as `queries:run`, `users:create`, and `audit:view`.
- **Rate Limits:** Built-in throttles protect login and query actions; customize via `ASSISTANT_QUERY_RATE`, `ASSISTANT_QUERY_WINDOW`, `ASSISTANT_LOGIN_RATE`, and `ASSISTANT_LOGIN_WINDOW`.
- **Audit Trail:** All authentication, authorization, and query events are appended to `logs/audit.log`.

---

## Deployment

- **Docker (Recommended):**
  - Use the provided `docker-compose.yml` for easy setup of all services.
- **Local Python:**
  - Install dependencies and run as above for development or testing.

---

## Contributors & Contact

- Project Lead: [Samarth Dubey](https://github.com/iSamarthDubey)
- For questions or contributions, open an issue or contact the maintainer.

---

## Disclaimer

This project here is only for research and demonstration purposes. Not production-hardened. Use at your own risk.

---

## License

MIT License. See [LICENSE](LICENSE) file for details.

---

> **From questions to insights - your SIEM, now truly conversational. Security made simple, powerful, and human-centric.**

> _"Project by **Team Kartavya**. Made with passion, for (SIH) 2025"._
