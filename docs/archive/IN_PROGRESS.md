# IN_PROGRESS.md

Log of ongoing changes and decisions. Do not include secrets.

## 2025-10-05 23:06 UTC
- Switched canonical API to Assistant (assistant.main) and added /assistant/ping for unauthenticated liveness.
- Updated launcher (app.py) to start Assistant API and point health checks to /assistant/ping.
- Hardened README: removed default admin credentials; spaCy download marked optional.
- Added .env.example with safe defaults; no heavy downloads required.
- Added config/index_mappings.yaml (stub) for future index-aware field selection.

Next options:
- Add “clarify” step in pipeline when intent confidence is low; surface suggestions in metadata.
- (Optional) Integrate INDEX_CLASS hint into QueryBuilder to select fields per dataset.
- (Optional) UI polish: quick actions for common queries, show generated DSL for transparency.

## 2025-10-05 23:18 UTC
- Created repo-structure.txt documenting current layout, entry points, stability rationale, and a future reorg plan.

## 2025-10-05 23:25 UTC
- Added clarify step to assistant pipeline with metadata.needs_clarification and top-3 intent suggestions.
- Implemented index-aware field selection in QueryBuilder using config/index_mappings.yaml and INDEX_CLASS env.
- Enforced safer defaults: last-24h fallback time window, result cap via ASSISTANT_MAX_RESULTS, and optional offset.
- Added optional spaCy enrichment (ASSISTANT_USE_SPACY=true); gracefully falls back if model not installed.

## 2025-10-05 23:33 UTC
- Streamlit UI: liveness now uses /assistant/ping; added DSL preview expander and clarify suggestion buttons.
- Streamlit UI: wired pagination (limit/offset) with Prev/Next; forwards limit/offset/force_intent to the API.
- Assistant API: extended request model to accept filters, limit, offset, force_intent; merged into user_context.
- Pipeline: _generate_query can apply force_intent and limit/offset from user_context.

## 2025-10-05 23:49 UTC
- Streamlit UI: added Export Pack (ZIP) download (summary, results.json, siem_query.json, entities.json, metadata.json).
- Streamlit UI: Advanced tab shows spaCy enrichment status based on ASSISTANT_USE_SPACY.
- README: noted Clarify flow, DSL preview, and Export Pack features.

## 2025-10-05 23:51 UTC
- Streamlit UI: added top-level Investigate tab with guided workflows (Failed Logins, Security Alerts, Network Activity) and a Dashboard tab.
- Guided workflows map time presets to precise now-* windows and set filters in session_state.

## 2025-10-05 23:59 UTC
- Wired sidebar filters to API via transformation: time_range → time_window_gte (now-*), severity → ES severity, dataset → index_class override.
- Backend: QueryBuilder now honors filters.time_window_gte/severity and per-request filters.index_class override.
- Prepared Reports-ready foundation using Export Pack; can add a dedicated Reports tab next.

## 2025-10-06 00:09 UTC
- UI: Added Reports tab with pre-canned templates (Failed Logins 24h, High Severity Alerts 24h, Network Activity 24h) that generate reports and offer ZIP export.
- UI: Added Advanced setting to always show DSL by default; added About ribbon (SIH 2025 – ISRO).
- app.py: Loads .env automatically via python-dotenv.
