# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project: Kartavya SIEM NLP Assistant (Python)

Core tooling
- Runtime: Python 3.10+
- Web: FastAPI (backend + assistant API), Streamlit (UI)
- Search: Elasticsearch (via docker-compose)
- Tests: pytest (async-friendly)
- Lint/format: flake8, black

Common commands
- First-time setup
  - Install deps
    - pip install -r requirements.txt
    - pip install -r backend/requirements.txt
    - python -m spacy download en_core_web_sm
  - Or run the guided setup:
    - python setup.py

- Launch everything (orchestrator)
  - python app.py
  - Behavior: starts backend API via uvicorn (assistant on 8001) and Streamlit UI (8501), handles port conflicts, and tails logs to logs/.

- Run services individually (development)
  - Assistant API (auth, RBAC, rate limiting):
    - uvicorn assistant.main:app --host 0.0.0.0 --port 8001
  - Core NLP Backend API (query processing, health, suggestions):
    - uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir backend --reload-dir siem_connector
  - Streamlit UI:
    - streamlit run ui_dashboard/streamlit_app.py --server.port 8501 --server.headless true

- Docker services (local search stack + backend container)
  - docker compose -f docker/docker-compose.yml up -d
  - Exposes: Elasticsearch 9200, Kibana 5601, backend 8000

- Tests
  - All tests: pytest -q
  - Single file: pytest tests/unit/test_pipeline_mock_data.py -q
  - Single test: pytest tests/unit/test_pipeline_mock_data.py::test_pipeline_uses_mock_data_when_no_sources -q
  - Full system check: python tests/run_complete_tests.py
  - Coverage: pytest --cov=. tests/

- Lint/format
  - black .
  - flake8 .

- Useful environment variables (PowerShell syntax shown; set as needed, do not echo secrets)
  - $env:SIEM_BACKEND_PORT = "8001"     # assistant/main.py
  - $env:SIEM_FRONTEND_PORT = "8501"    # app.py Streamlit
  - $env:ELASTICSEARCH_HOST = "localhost"  # backend/main.py (or docker network name)
  - $env:ELASTICSEARCH_PORT = "9200"
  - $env:SIEM_PLATFORM = "elasticsearch"   # backend/main.py switch for connectors
  - $env:ASSISTANT_ADMIN_PASSWORD = "{{ADMIN_PASSWORD}}"  # override bootstrap admin (see README)

Big-picture architecture
- User Interface (ui_dashboard/streamlit_app.py)
  - Streamlit front-end used for demo/development. Talks to the Assistant API (port 8001 by default) and renders narratives, tables, and charts.

- Assistant API (assistant/main.py)
  - FastAPI app exposing /assistant endpoints: auth (login/logout), ask, health, conversation history.
  - Security-first surface: session tokens, RBAC (require_permission/require_rate_limited_permission), rate limits, audit logging.
  - Depends on ConversationalPipeline (assistant/pipeline.py) to orchestrate end-to-end flow.
  - Typical flow: sanitize input -> infer intent/entities via backend NLP -> build/execute SIEM queries -> format -> update conversation context.

- Core NLP + Query Backend (backend/main.py)
  - FastAPI app exposing /query, /parser/info, /suggestions, /health for NLP-centric operations and direct SIEM querying.
  - Composes:
    - NLP: backend/nlp/intent_classifier.py, backend/nlp/entity_extractor.py
    - Query building: backend/query_builder.py (async build of Elasticsearch DSL/KQL)
    - Connectors: siem_connector/ (ElasticConnector, WazuhConnector) via create_siem_processor
    - Response formatting: backend/response_formatter/* (text, chart, dashboard exports)
  - Fallback behavior: if SIEM not available, generates mock results for a seamless demo experience.

- Connectors (siem_connector/)
  - Normalized interfaces to SIEM platforms (Elasticsearch, Wazuh). Provide health, indices listing, query execution, and normalized result metadata.

- RAG/Vector components (rag_pipeline/)
  - Optional Retrieval-Augmented Generation pipeline (if available). backend/main.py initializes it when present; otherwise runs in degraded mode.

- Security modules (src/security/)
  - Auth manager, RBAC, rate limiter, validators/sanitizers, and audit logger. Assistant API depends on this layer to enforce policies across routes.

- Orchestration (app.py)
  - Developer-friendly launcher that:
    - Ensures deps (uvicorn/streamlit) are present
    - Starts Assistant API (8001) and Streamlit UI (8501)
    - Detects/kills conflicting processes on ports when needed
    - Writes logs to logs/backend.log and logs/frontend.log

- Data and external services
  - Elasticsearch + Kibana via docker/docker-compose.yml for local development.
  - Beats sample configs under beats-config/ (optional dev tooling).

Development workflow notes
- For iterative backend NLP work, run uvicorn backend.main:app with --reload and focus changes under backend/nlp, backend/query_builder.py, and siem_connector/.
- For end-to-end flows and auth/RBAC testing, prefer uvicorn assistant.main:app and use Streamlit UI or call /assistant endpoints.
- When real Elasticsearch isn’t running, both assistant and backend degrade gracefully using mock data for demos and tests.

Key references from repository docs
- README.md (root): Quick Start, security/auth notes (bootstrap admin user, bearer tokens, RBAC/rate limits).
- .github/DOCS.md: Pointers to detailed guides (architecture, quick reference, NLP, SIEM integration, deployment, testing). Use it to navigate the broader documentation set if present in your environment.

Notes
- No existing WARP.md was found; this is the initial version tailored to this codebase.
- Secrets: never print or commit secrets. Use environment variables (e.g., $env:ASSISTANT_ADMIN_PASSWORD = "{{ADMIN_PASSWORD}}") and avoid echoing their values.
