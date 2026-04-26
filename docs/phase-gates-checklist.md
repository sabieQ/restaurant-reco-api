# Phase Gates Checklist (P0 Pre-Flight)

Purpose: turn all `P0-Critical` risks into a tickable checklist to complete **before** and **during** each phase.

How to use:
- Mark each item `[x]` only after objective evidence exists (test, config, log, or doc update).
- Do not start the next phase until all current phase items are complete or explicitly accepted as risk.

---

## Phase 0 - Alignment and Scope Lock

- [x] **Success metric is frozen**
  - Evidence: Written acceptance criteria covering relevance, cost-fit, and explanation quality.
- [x] **Fallback behavior is frozen**
  - Evidence: Policy documented as: strict location + strict rating + semi-strict cuisine + flexible budget; fallback = relax rating by 0.5, then widen cuisine.

Gate decision:
- [x] Approved to proceed to Phase 1

---

## Phase 1 - Environment and Repo Setup

- [x] **Runtime pinned to Python 3.11**
  - Evidence: local venv uses 3.11 and setup docs specify 3.11.
- [x] **Secrets are never hardcoded**
  - Evidence: `.env` pattern in place, keys loaded from env vars, no secrets in tracked files.

Gate decision:
- [x] Approved to proceed to Phase 2

---

## Phase 2 - Data Ingestion and Profiling

- [x] **Dataset access is resilient**
  - Evidence: ingestion handles availability issues (retry and/or cached snapshot path documented).
- [x] **Schema mapping validated**
  - Evidence: canonical mapping for `restaurant_name`, `location`, `cuisine`, `average_cost_for_two`, `rating` is verified; mismatch produces fail-fast signal.

Gate decision:
- [x] Approved to proceed to Phase 3

---

## Phase 3 - Data Cleaning and Normalization

- [x] **Cleaning does not over-drop valid rows**
  - Evidence: row-retention metrics captured per cleaning step and within acceptable threshold.
- [x] **Budget mapping is correct**
  - Evidence: threshold tests pass for low/medium/high boundary values.

Gate decision:
- [x] Approved to proceed to Phase 4

---

## Phase 4 - Preference Filtering Engine

- [x] **Strict filters do not collapse coverage**
  - Evidence: fallback frequency measured and within acceptable range on sample scenarios.
- [x] **Fallback order is correct**
  - Evidence: tests confirm sequence is exactly: relax rating by 0.5, then widen cuisine.

Gate decision:
- [x] Approved to proceed to Phase 5

---

## Phase 5 - LLM Ranking and Explanation

- [x] **Malformed LLM output is safely handled**
  - Evidence: parser guard catches non-JSON and triggers deterministic fallback without crashing API.
- [x] **Hallucination guard is active**
  - Evidence: response post-validation ensures recommended restaurants exist in candidate list.

Gate decision:
- [x] Approved to proceed to Phase 6

---

## Phase 6 - API and Output Layer

- [x] **Response schema is enforced**
  - Evidence: contract test verifies required fields (`restaurant_name`, `cuisine`, `rating`, `estimated_cost`, `explanation`).
- [x] **Exceptions are sanitized**
  - Evidence: centralized error handling prevents stack traces/internal details from leaking.

Gate decision:
- [x] Approved to proceed to Phase 7

---

## Phase 7 - Quality, Testing, and Handover

- [ ] **Fallback paths are fully tested**
  - Evidence: unit + integration tests cover OpenRouter failure, Groq fallback, and deterministic fallback.
- [ ] **Runbook is reproducible**
  - Evidence: README verified from clean environment by a second run-through.

Gate decision:
- [ ] Approved for delivery / handover complete

---

## Sign-Off Log

- Date:
- Reviewer:
- Current phase:
- Blockers (if any):
- Approved exception(s) (if any):
