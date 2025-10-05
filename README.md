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

- Clarification flow on ambiguous queries (top-3 intents) with one-click refine in the UI
- DSL transparency: UI can show the generated Elasticsearch DSL
- Export Pack: one-click ZIP export containing summary, results.json, siem_query.json, entities.json, and metadata.json

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

docker-compose up -d
## Getting Started

### Prerequisites

- Python 3.10 or newer (3.11 recommended)
- pip with the build tools required for Python packages
- (Optional) Docker & Docker Compose if you plan to bring up Elastic/Wazuh locally

Work inside a virtual environment if you can (`python -m venv .venv; .venv\\Scripts\\Activate.ps1` on Windows).

### Option A – One-command demo for Windows (recommended)

The repository ships with `scripts/run_demo.ps1`, a PowerShell helper that installs nothing but bootstraps the backend and Streamlit UI for you. From the project root:

```powershell
.\scripts
un_demo.ps1
```

What the script does:

- Runs `tests/run_complete_tests.py` unless you pass `-SkipTests`
- Starts the FastAPI backend with `uvicorn` (default host `0.0.0.0`, port `8100`)
- Sets `ASSISTANT_BACKEND_URL` so Streamlit talks to the correct port
- Launches the Streamlit UI on `http://localhost:8501`
- Stops both processes when you hit **Enter** in the terminal

Useful switches:

- `-SkipTests` &mdash; skip the pre-flight test suite
- `-NoFrontend` &mdash; run the API only (for Postman/cURL)
- `-BackendPort 8001` or `-FrontendPort 8600` &mdash; override default ports

### Option B – Manual start (any platform)

1. **Install dependencies** (root + backend):

  ```bash
  pip install -r requirements.txt
  pip install -r backend/requirements.txt
  ```

2. **(Optional) Enable spaCy enrichment** for better entity hints:

  ```bash
  pip install -U spacy
  python -m spacy download en_core_web_sm
  ```

  Set `ASSISTANT_USE_SPACY=true` before launching if you want it active.

3. **Start the FastAPI backend** (choose a port; defaults to `8001` if unset):

  ```bash
  ASSISTANT_HOST=0.0.0.0 ASSISTANT_PORT=8001 \ 
  python -m uvicorn assistant.main:app --host 0.0.0.0 --port 8001
  ```

4. **Start the Streamlit UI** in a second shell (pointing it at the backend):

  ```bash
  ASSISTANT_BACKEND_URL=http://localhost:8001 \ 
  python -m streamlit run ui_dashboard/streamlit_app.py --server.port 8501 --server.headless true
  ```

  On Windows PowerShell, use `$env:ASSISTANT_BACKEND_URL="http://localhost:8001"` before running the command.

Once both processes are up, open `http://localhost:8501` in your browser to chat with the assistant.

### Health checks & smoke tests

- Verify the public readiness probe: `http://localhost:8001/health`
- Authenticated health telemetry: `http://localhost:8001/assistant/health` (requires bearer token)
- Quick ask call (replace `<token>`): `curl -H "Authorization: Bearer <token>" -X POST http://localhost:8001/assistant/ask -d '{"query": "Show failed logins last 24h"}' -H "Content-Type: application/json"`

### Core environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `ASSISTANT_HOST` | `0.0.0.0` | Bind address for the FastAPI service |
| `ASSISTANT_PORT` | `8001` | API port (overridden to `8100` by `run_demo.ps1`) |
| `ASSISTANT_BACKEND_URL` | derived | Base URL Streamlit uses to talk to the API |
| `ASSISTANT_ADMIN_PASSWORD` | `Admin!2025` | Bootstrap admin password (set this yourself!) |
| `ASSISTANT_DEMO_USERNAME` | `admin` | Preferred username the Streamlit UI auto-fills |
| `ASSISTANT_DEMO_PASSWORD` | `Admin!2025` | Preferred password the Streamlit UI auto-fills |
| `ASSISTANT_QUERY_RATE` / `ASSISTANT_QUERY_WINDOW` | `30 / 60` | Query rate limit (hits per seconds window) |
| `ASSISTANT_LOGIN_RATE` / `ASSISTANT_LOGIN_WINDOW` | `5 / 300` | Login rate limit |
| `ASSISTANT_USE_SPACY` | unset | Enable spaCy enrichment when set to `true` |

Set or export these before launching the backend. The Streamlit UI reads the same values at startup.

---

## Security & Authentication

- **Bootstrap admin:** The backend guarantees an `admin` user exists. If you do not set `ASSISTANT_ADMIN_PASSWORD` before the first run it will use the public default `Admin!2025` and log a warning. Override it immediately for anything beyond a throwaway demo.
- **Session tokens:** Obtain a bearer token from `/assistant/auth/login` using JSON payload `{"username": "...", "password": "..."}`. Include `Authorization: Bearer <token>` on every protected request.
- **UI auto-login:** The Streamlit sidebar auto-logins using `ASSISTANT_DEMO_USERNAME`/`ASSISTANT_DEMO_PASSWORD` (or `admin`/`Admin!2025` if you keep the defaults). You can override the credentials in the sidebar or by changing the environment variables.
- **RBAC enforcement:** Endpoint permissions such as `queries:run`, `users:create`, and `audit:view` are enforced by the security layer.
- **Rate limiting:** Customise query/login throttles with `ASSISTANT_QUERY_RATE`, `ASSISTANT_QUERY_WINDOW`, `ASSISTANT_LOGIN_RATE`, and `ASSISTANT_LOGIN_WINDOW`.
- **Audit trail:** Authentication, authorization, and query outcomes are appended to `logs/audit.log` for review.
- **Health probes:** `/health` is unauthenticated for load balancers; `/assistant/health` requires a valid token and returns richer diagnostics.

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
