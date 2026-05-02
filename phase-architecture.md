# Phase Architecture Document

This document outlines the complete phase architecture for the Restaurant Recommendation API project, including completed phases (0-6) and planned phases (7-10).

## Completed Phases

### Phase 0 — Alignment and Scope Lock
- **Concern**: Define MVP scope, acceptance criteria, and success metrics
- **Approach**: Freeze success metrics, fallback behavior, top-N contract, location granularity policy, explanation style policy
- **Status**: ✅ Completed
- **Evidence**: `phases/phase_0_alignment_scope_lock/`

### Phase 1 — Environment and Repo Setup
- **Concern**: Pin Python 3.11 runtime, create virtual environment, install dependencies, configure secrets
- **Approach**: Environment setup with secure handling of API keys via environment variables
- **Status**: ✅ Completed
- **Evidence**: `phases/phase_1_environment_repo_setup/`

### Phase 2 — Data Ingestion and Profiling
- **Concern**: Validate dataset accessibility, detect schema drift, generate profiling report
- **Approach**: Load Zomato dataset from Hugging Face, validate schema, profile data distribution
- **Status**: ✅ Completed
- **Evidence**: `phases/phase_2_data_ingestion_profiling/`

### Phase 3 — Data Cleaning and Normalization
- **Concern**: Standardize restaurant records, ensure cleaning does not over-drop valid rows
- **Approach**: Normalize text fields, parse ratings and costs, filter invalid entries, deduplicate
- **Status**: ✅ Completed
- **Evidence**: `phases/phase_3_data_cleaning_normalization/`

### Phase 4 — Preference Filtering Engine
- **Concern**: Validate deterministic filtering behavior and fallback sequencing
- **Approach**: Implement strict location + strict rating + semi-strict cuisine + flexible budget with fallback
- **Status**: ✅ Completed
- **Evidence**: `phases/phase_4_preference_filtering_engine/`

### Phase 5 — LLM Ranking, Explanation, and Frontend
- **Concern**: Implement LLM-based ranking and explanation generation, create frontend web interface
- **Approach**: 
  - LLM ranking using OpenRouter (primary) and Groq (fallback)
  - Generate personalized explanations
  - React-based frontend with modern UI
  - CORS configuration for frontend-backend communication
- **Status**: ✅ Completed
- **Evidence**: `phases/phase_5_llm_ranking_frontend/`, `frontend/`

### Phase 6 — API and Output Layer
- **Concern**: Validate API contract, exception handling, and output schema enforcement
- **Approach**: 
  - Verify response schema contains all required fields
  - Ensure exceptions are sanitized (no stack traces leaked)
  - Validate CORS configuration
  - Test health endpoint availability
- **Status**: ✅ Completed
- **Evidence**: `phases/phase_6_api_and_output_layer/`

## Planned Phases

### Phase 7 — Backend (HTTP API)
- **Concern**: Thin HTTP service that owns server-side secrets, dataset access, and orchestration
- **Approach**: 
  - FastAPI backend with stable JSON request/response contract
  - Endpoints: POST /api/v1/recommendations, GET /health, optional GET /api/v1/meta
  - Structured server logs (counts, latency, token totals)
  - CORS restricted to dev frontend origin
  - Request size limits on free-text fields
- **Stack**: Python with FastAPI (sharing milestone1 library)
- **Exit Criteria**: Frontend can complete one recommendation flow using only the API; API returns same logical outcomes as milestone1 for same inputs
- **Status**: ✅ Completed
- **Implementation Target**: `app/main.py` with v1 endpoints, structured logging, and request validation

### Phase 8 — Frontend (Web UI)
- **Concern**: Primary user-facing surface with preference form + results list
- **Approach**:
  - Browser talks only to Phase 7 API
  - Map form fields to API JSON schema (location, budget band, cuisines, minimum rating, optional text)
  - Results show name, cuisines, rating, estimated cost, AI explanation
  - Clear empty-state semantics ("no filter match" vs "model returned no grounded picks")
  - Loading states, validation errors inline, disabled submit while pending
- **Stack**: React + Vite (SPA) or HTMX + server templates
- **Exit Criteria**: Demo path in README: start API + UI, submit preferences, see ranked results or intentional empty state
- **Status**: ✅ Completed
- **Implementation Target**: `frontend/` with Next.js 14, TypeScript, and Tailwind CSS

### Phase 9 — Deployment using Streamlit (Deprecated)
- **Status**: ❌ Deprecated
- **Reason**: Deployment architecture changed to Vercel (frontend) + Render (backend)
- **Note**: Phase 9 files have been removed from the repository

### Phase 10 — Hardening and Handoff (Optional but Recommended)
- **Concern**: Automated tests, comprehensive documentation, cost/latency notes
- **Approach**:
  - Automated tests for filters, prompt shape, JSON parsing (fixtures with fake LLM responses)
  - API contract tests (golden JSON for happy/empty/error paths)
  - README: install, set GROQ_API_KEY, run API + UI, CLI fallbacks, limitations
  - Cost/latency notes: candidate cap, model id, when to raise load limits, caching strategy
- **Exit Criteria**: Complete test suite, comprehensive documentation, handoff-ready
- **Status**: ✅ Completed
- **Implementation Target**: Test suite in `tests/`, updated README with deployment guide, `docs/cost-latency-notes.md`, `phases/phase_10_hardening_handoff/`

## Phase Dependencies

```
Phase 0 (Scope) → Phase 1 (Env) → Phase 2 (Data) → Phase 3 (Cleaning) → Phase 4 (Filtering) → Phase 5 (LLM + Frontend) → Phase 6 (API Layer) → Phase 7 (HTTP API) → Phase 8 (Web UI) → Phase 10 (Hardening)
```

## Current Status Summary

- **Completed**: Phases 0-8, 10
- **Deprecated**: Phase 9 (Streamlit deployment - replaced with Vercel/Render)
- **All active phases complete and ready for handoff**

## Notes

- Phase 7-8 are already partially implemented through the existing FastAPI backend and React frontend
- Phase 10 is the final quality assurance phase before handoff
- All phases maintain the same core filtering and LLM ranking logic established in Phases 4-5
