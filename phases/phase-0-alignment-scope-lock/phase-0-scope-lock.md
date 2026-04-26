# Phase 0 - Alignment and Scope Lock

Status: Complete  
Date: 2026-04-20

## 1) MVP Scope (Locked)

The MVP includes:
- FastAPI backend service for recommendations.
- Data ingestion from Hugging Face dataset `ManikaSaini/zomato-restaurant-recommendation`.
- Deterministic filtering using policy:
  - strict location
  - strict rating
  - semi-strict cuisine
  - flexible budget
- LLM-based ranking and explanation:
  - primary: OpenRouter free-first
  - fallback: Groq free tier
- Deterministic non-LLM fallback if both providers are unavailable.
- Output top `3-5` recommendations with required fields.

Out of scope for MVP:
- Authentication/authorization
- Admin dashboards
- Real-time feedback learning loop
- Multi-city geo-distance calculations
- Production-grade deployment infra (autoscaling, load balancers)

## 2) Acceptance Criteria (Locked)

### Functional
- API accepts: `location`, `budget`, `cuisine`, `min_rating`, optional preferences, `top_n`.
- API returns `3-5` recommendations when possible.
- Every recommendation includes:
  - `restaurant_name`
  - `cuisine`
  - `rating`
  - `estimated_cost`
  - `explanation`

### Policy Correctness
- Filtering precedence is applied in fixed order.
- If no match:
  1. Relax rating by `0.5`
  2. Widen cuisine
- If LLM providers fail, deterministic fallback still returns ranked results.

### Reliability
- Health endpoint returns service status.
- API handles malformed/empty data gracefully without crashing.

## 3) Top-N Contract (Locked)

- Supported input range: `top_n` in `[3, 5]`
- Default: `5`
- If fewer than `top_n` valid candidates exist after filtering/fallback, return available count with stable schema.

## 4) Location Granularity Policy (Locked)

- Matching is city/locality text-based using normalized string containment.
- Canonicalization rules:
  - trim whitespace
  - lowercase for matching
  - tolerate simple spacing variations
- Future enhancement note: add alias dictionary for city variants (`new delhi`/`delhi`) if precision issues are observed.

## 5) Explanation Style Policy (Locked)

- Length: 1-2 concise lines
- Include at least one direct reason linked to user preferences (location, cuisine, rating, budget fit or trade-off).
- Avoid generic claims and avoid inventing non-candidate restaurants.

## 6) Decision Gates Closed

- Stack/runtime locked: Python 3.11 + FastAPI + pip
- Filter policy locked with precedence and fallback order
- LLM strategy locked: OpenRouter free-first + Groq fallback
