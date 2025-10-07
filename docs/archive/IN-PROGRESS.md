# 🚀 Kartavya SIEM Assistant – Build Log & Roadmap

_Last updated: 2025-10-06 18:25 UTC_

## 📊 Status Dashboard

| Item | Details |
| --- | --- |
| Problem Statement | ISRO – Conversational SIEM Assistant (PS-SIH25173) |
| Delivery Focus | Lightweight, offline-first prototype with security-first refactor |
| Current Phase | Phase 1 – Security foundation & pipeline stabilization |
| Repo Snapshot | `main` branch; pending creation of `baseline-2025-10-06` safety tag |
| Constraints | No large downloads, test after each step, keep dependencies minimal |

## 🕒 Session Timeline

| Timestamp (UTC) | Summary |
| --- | --- |
| 2025-10-06 12:30 | Completed architecture/code review, captured mismatches vs. repo docs, highlighted blocking runtime issues, and chose lightweight options for auth, NLP, reporting, caching. |
| 2025-10-06 12:55 | Updated `repo-structure.txt` to mirror actual filesystem and target architecture. |
| 2025-10-06 15:20 | Deep-dived runtime paths, confirmed async/sync incompatibilities, identified broken tests, created `TO-UPDATE.md` tracker. |
| 2025-10-06 16:10 | Implemented lightweight security module suite (auth, sessions, RBAC, audit, rate limiting, validators), added unit coverage, and verified offline tests. |
| 2025-10-06 17:20 | Wired security context into FastAPI layer, shipped auth endpoints, enforced RBAC/rate limits, sanitized queries, and added integration tests. |
| 2025-10-06 17:50 | Added mock-data generator fallback with unit coverage so pipeline produces demo results offline. |
| 2025-10-06 18:20 | Patched pipeline mock-data metadata flag, refreshed security context to respect per-test env overrides, and reran unit suite (14/14 green). |

## ⚠️ Operating Constraints

- No large model downloads (BERT, GPT, large spaCy models, etc.).
- Solution must run offline; prompt before adding any dependency that needs the internet.
- Prefer pure-python or already-installed packages; keep additional installs under ~5 MB after approval.
- Execute and document tests after every meaningful change.

## 🎯 Phase Roadmap Overview

| Phase | Objective | Key Deliverables | Status | Notes |
| --- | --- | --- | --- | --- |
| 1. Security Foundation | Establish lightweight auth/RBAC + safe pipeline | Auth manager, RBAC, session store, audit log, synchronous-safe pipeline & connector adapters | ⚙️ In progress | No external packages required. |
| 2. Enhanced NLP | Improve rule-based NLP with confidence scoring and fuzzy matching | Advanced classifier, fuzzy extractor, context analyzer | ⏳ Pending | Remains offline-friendly; optional NLTK download deferred. |
| 3. Smart Query Generation | Template intelligence and caching | Template engine, decision tree, optimizer, cache manager | ⏳ Pending | Built on sqlite + stdlib. |
| 4. Reporting & UI | HTML reports, charts, secure Streamlit views | Report generator, chart builder, RBAC-aware UI | ⏳ Pending | PDF export optional (ReportLab). |
| 5. Performance Optimization | Async orchestration, resource tuning | Async/parallel executor, memory manager, batching | ⏳ Pending | Triggered after Phases 1–4 stabilize. |

## ✅ Deliverables Completed

- Accurate `repo-structure.txt` matching the actual tree and new architecture direction.
- `TO-UPDATE.md` created to track documentation changes tied to upcoming refactors.
- Comprehensive gap analysis between current implementation and ISRO-grade expectations.
- Lightweight security module suite (auth, RBAC, sessions, audit, validators, rate limiting) with targeted unit tests.

## 🚧 Active Work (Phase 1 Focus)

### 1.1 Basic Authentication Stack

**Goal:** Lightweight token-based auth with RBAC and audit logging (stdlib only).

| Artifact | Purpose | Status |
| --- | --- | --- |
| `src/security/auth_manager.py` | Credential storage + token issuing | ✅ Implemented (unit-tested) |
| `src/security/rbac.py` | Role mapping and permission checks | ✅ Implemented (unit-tested) |
| `src/security/session_manager.py` | In-memory session tracking | ✅ Implemented (unit-tested) |
| `src/security/audit_logger.py` | Append-only audit trail | ✅ Implemented (unit-tested) |

**Testing checklist:**

- [x] Register/login happy path (unit tests).
- [x] RBAC enforcement (admin / analyst / viewer).
- [x] Audit log entry emitted for sensitive actions.

### 1.2 Input Hardening & Rate Limiting

**Goal:** Protect the API surface with sanitizers and throttling.

| Artifact | Purpose | Status |
| --- | --- | --- |
| `src/security/validators.py` | Shared validation helpers | ✅ Implemented (unit-tested) |
| `src/security/sanitizer.py` | Query sanitization & canonicalization | ✅ Implemented (unit-tested) |
| `src/security/rate_limiter.py` | Simple token bucket per user/session | ✅ Implemented (unit-tested) |

**Testing checklist:**

- [x] Reject injection-style payloads (validator coverage).
- [x] Enforce per-user request ceilings (rate limiter coverage).
- [x] Sanitized payloads still reach downstream pipeline (sanitizer coverage).

### 1.3 Pipeline Stabilization

**Goal:** Replace the broken async orchestrator with a predictable synchronous flow plus offline-friendly connectors.

| Artifact | Purpose | Status |
| --- | --- | --- |
| `src/pipeline/orchestrator.py` | New orchestrator bridging NLP → query → connectors | ⬜ Planned |
| `src/connectors/elastic_adapter.py` | Safe, lazy, mockable Elasticsearch client | ⬜ Planned |
| `src/connectors/wazuh_adapter.py` | Same concept for Wazuh | ⬜ Planned |
| `tests/unit/test_orchestrator.py` | Smoke coverage for the new flow | ⬜ Planned |

**Testing checklist:**

- [ ] Offline mocks return deterministic results.
- [ ] Error handling/reporting matches API schema.
- [ ] Context manager updates conversation history correctly.

## 🧭 Implementation Strategy

1. Build the security foundation before touching UI/LLM components.
2. Swap in the new pipeline with mock-friendly adapters so tests can run offline.
3. Layer NLP improvements once the pipeline is stable.
4. Deliver HTML reporting + RBAC UI as soon as security + NLP lift is done.
5. Leave async/perf tuning for the end once everything else is functional.

## 📚 Lightweight Alternatives Cheat Sheet

| Heavy Tool | Replacement | Size Footprint |
| --- | --- | --- |
| BERT / GPT models | Enhanced regex + difflib scoring | 0 MB |
| spaCy large | Custom NER heuristics | 0 MB |
| PostgreSQL / MongoDB | SQLite (stdlib) | 0 MB |
| Redis cache | Python dict + `functools.lru_cache` | 0 MB |
| LangChain pipelines | Purpose-built orchestrator | 0 MB |

## 🧪 Test & Verification Commands

```bash
# Targeted unit tests
python -m pytest tests/unit/test_<component>.py -v

# Integration sweep by phase
python tests/integration/test_phase_<n>.py

# Security regression pass
python tests/security/test_auth.py

# Optional performance harness
python tests/performance/benchmark.py
```

## 📋 Validation Checklist (Run After Each Milestone)

- [x] Unit suite green.
- [ ] Integration suite green.
- [ ] No new heavyweight dependencies introduced.
- [ ] Offline requirement still satisfied.
- [ ] Performance within acceptable bounds (<2 s target for demo flows).
- [ ] Security hooks validated (auth + audit).
- [ ] Documentation (`IN-PROGRESS.md`, `TO-UPDATE.md`, READMEs) refreshed.

## 🎯 Success Criteria Snapshot

| Milestone | Definition of Done |
| --- | --- |
| MVP | Auth + RBAC, enhanced NLP (≥90 % intent accuracy in test set), working query builder, HTML report generation, audit logging. |
| Hackathon Demo | All MVP items plus demo scripts, <2 s response for canned scenarios, multi-turn conversations, live role demo, export showcase. |

## 🔜 Immediate Next Actions

1. Document security endpoints (OpenAPI summary + Streamlit integration notes) in `temp-docs/` and README trackers.
2. Introduce an orchestration module that works without awaiting synchronous connectors.
3. Capture results + update both this log and `TO-UPDATE.md` as tasks complete.

## 🧾 Decision Log (Needs Confirmation for Future Phases)

| Topic | Preferred Option | Alternative (Deferred) | Notes |
| --- | --- | --- | --- |
| Authentication | Token-based (stdlib) | JWT via `pyjwt` (50 KB download) | Upgrade path available once internet permitted. |
| NLP enhancements | Enhanced rules + difflib | NLTK minimal bundle (~31 MB) | Hold off unless accuracy targets not met. |
| Report export | HTML (inline CSS) | PDF via ReportLab (~2 MB) | Ask before adding dependency. |
| Caching | SQLite + in-memory dict | External Redis | SQLite satisfies offline durability. |

## 🤝 Working Agreement

- Every implementation step includes immediate testing.
- No downloads over 5 MB without explicit approval.
- Prioritize demo-ready stability over experimental features.
- Keep documentation in sync (update tables/checklists as tasks move).

Development mode: ACTIVE • Approach: Lightweight & offline-first
