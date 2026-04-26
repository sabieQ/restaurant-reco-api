# Phase Architecture Document

This document outlines the complete phase architecture for the Restaurant Recommendation API project, including completed phases (0-6) and planned phases (7-10).

## Completed Phases

### Phase 0 — Alignment and Scope Lock
- **Concern**: Define MVP scope, acceptance criteria, and success metrics
- **Approach**: Freeze success metrics, fallback behavior, top-N contract, location granularity policy, explanation style policy
- **Status**: ✅ Completed
- **Evidence**: `phases/phase-0-alignment-scope-lock/`

### Phase 1 — Environment and Repo Setup
- **Concern**: Pin Python 3.11 runtime, create virtual environment, install dependencies, configure secrets
- **Approach**: Environment setup with secure handling of API keys via environment variables
- **Status**: ✅ Completed
- **Evidence**: `phases/phase-1-environment-repo-setup/`

### Phase 2 — Data Ingestion and Profiling
- **Concern**: Validate dataset accessibility, detect schema drift, generate profiling report
- **Approach**: Load Zomato dataset from Hugging Face, validate schema, profile data distribution
- **Status**: ✅ Completed
- **Evidence**: `phases/phase-2-data-ingestion-profiling/`

### Phase 3 — Data Cleaning and Normalization
- **Concern**: Standardize restaurant records, ensure cleaning does not over-drop valid rows
- **Approach**: Normalize text fields, parse ratings and costs, filter invalid entries, deduplicate
- **Status**: ✅ Completed
- **Evidence**: `phases/phase-3-data-cleaning-normalization/`

### Phase 4 — Preference Filtering Engine
- **Concern**: Validate deterministic filtering behavior and fallback sequencing
- **Approach**: Implement strict location + strict rating + semi-strict cuisine + flexible budget with fallback
- **Status**: ✅ Completed
- **Evidence**: `phases/phase-4-preference-filtering-engine/`

### Phase 5 — LLM Ranking, Explanation, and Frontend
- **Concern**: Implement LLM-based ranking and explanation generation, create frontend web interface
- **Approach**: 
  - LLM ranking using OpenRouter (primary) and Groq (fallback)
  - Generate personalized explanations
  - React-based frontend with modern UI
  - CORS configuration for frontend-backend communication
- **Status**: ✅ Completed
- **Evidence**: `phases/phase-5-llm-ranking-frontend/`, `frontend/`

### Phase 6 — API and Output Layer
- **Concern**: Validate API contract, exception handling, and output schema enforcement
- **Approach**: 
  - Verify response schema contains all required fields
  - Ensure exceptions are sanitized (no stack traces leaked)
  - Validate CORS configuration
  - Test health endpoint availability
- **Status**: ✅ Completed
- **Evidence**: `phases/phase-6-api-and-output-layer/`

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

### Phase 9 — Deployment using Streamlit (Optional)
- **Concern**: Single-process Python app for demos and stakeholder previews without Node build or separate SPA host
- **Approach**:
  - Secrets via Streamlit secrets (st.secrets) or environment variables
  - Forms with st.selectbox / st.text_input / st.slider for preferences
  - st.spinner while model runs
  - Match empty-state copy from Phase 5
- **Deployment**: Streamlit Community Cloud (free tier) or Docker image on Render/Fly
- **Relationship to Phase 7-8**: Complementary - Phase 7 remains the primary UI; Phase 9 ideal for demos and fast sharing without operating Vite + CORS + two deployables. You may implement Streamlit without calling the HTTP API by importing milestone1 directly (duplication of orchestration is acceptable if thin); alternatively call POST /api/v1/recommendations if you want one orchestration path.
- **UX scope**
- Forms with st.selectbox / st.text_input / st.slider for location, cuisines, budget, minimum rating, and additional text; st.spinner while the model runs; st.expander for raw JSON or telemetry if useful. Match empty-state copy from Phase 5 where practical.
- **Exit criteria**: README (or a short docs/streamlit-deploy.md) documents how to run locally (streamlit run …) and how to deploy to Community Cloud (repo layout, secrets names, branch); a reviewer can open the hosted URL and complete one successful recommendation or see an intentional empty state.
- **Status**: ✅ Completed
- **Implementation Target**: `phases/phase-9-streamlit-deployment/` (app.py), repo root `streamlit_app.py` (Cloud entrypoint), streamlit and nest-asyncio in requirements.txt, and docs/streamlit-deploy.md.

### Phase 10 — Hardening and Handoff (Optional but Recommended)
- **Concern**: Automated tests, comprehensive documentation, cost/latency notes
- **Approach**:
  - Automated tests for filters, prompt shape, JSON parsing (fixtures with fake LLM responses)
  - API contract tests (golden JSON for happy/empty/error paths)
  - README: install, set GROQ_API_KEY, run API + UI, CLI fallbacks, limitations
  - Cost/latency notes: candidate cap, model id, when to raise load limits, caching strategy
- **Exit Criteria**: Complete test suite, comprehensive documentation, handoff-ready
- **Status**: ✅ Completed
- **Implementation Target**: Test suite in `tests/`, updated README with deployment guide, `docs/cost-latency-notes.md`

## Phase Dependencies

```
Phase 0 (Scope) → Phase 1 (Env) → Phase 2 (Data) → Phase 3 (Cleaning) → Phase 4 (Filtering) → Phase 5 (LLM + Frontend) → Phase 6 (API Layer) → Phase 7 (HTTP API) → Phase 8 (Web UI) → Phase 9 (Streamlit) → Phase 10 (Hardening)
```

## Current Status Summary

- **Completed**: Phases 0-10
- **All phases complete and ready for handoff**

## Notes

- Phase 7-8 are already partially implemented through the existing FastAPI backend and React frontend
- Phase 10 is the final quality assurance phase before handoff
- All phases maintain the same core filtering and LLM ranking logic established in Phases 4-5
