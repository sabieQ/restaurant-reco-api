# Edge-Case Register (Phase-Wise)

This register is organized for execution use.  
Sort order used in each phase:
1. `P0-Critical` (blocks delivery or causes invalid outputs)
2. `P1-High` (major quality/reliability risk)
3. `P2-Medium` (degrades UX/perf/maintainability)
4. `P3-Low` (minor issue, polish-level)

Use this as a pre-flight and in-phase checklist.

---

## Phase 0: Alignment and Scope Lock

### P0-Critical
- **Ambiguous success metric**
  - Symptom: Team cannot decide whether "good recommendation" means relevance, cost-fit, or rating-fit.
  - Risk: Rework across filtering and LLM ranking.
  - Pre-check: Freeze acceptance criteria (for example, precision@5 proxy + manual rubric).

- **Undefined fallback behavior**
  - Symptom: Conflicting implementations when no strict matches exist.
  - Risk: Non-deterministic outcomes and test failures.
  - Pre-check: Confirm exact fallback order (already set: relax rating by 0.5, then widen cuisine).

### P1-High
- **Top-N mismatch across stakeholders**
  - Symptom: API returns 5, UI expects 3.
  - Risk: Client-side errors and product inconsistency.
  - Pre-check: Lock allowed range (`3-5`) in contract.

- **Unclear location granularity**
  - Symptom: "Delhi" vs "New Delhi" vs neighborhood-level expectations mismatch.
  - Risk: False "no matches."
  - Pre-check: Document canonical location matching policy.

### P2-Medium
- **Undefined explanation style**
  - Symptom: LLM output too long/too generic.
  - Risk: Poor UX and token waste.
  - Pre-check: Set explanation length (1-2 lines) and tone.

---

## Phase 1: Environment and Repo Setup

### P0-Critical
- **Python runtime mismatch**
  - Symptom: App runs on 3.14 locally, breaks on 3.11 target.
  - Risk: Inconsistent behavior and deployment failures.
  - Mitigation: Pin and validate against Python 3.11 in venv and docs.

- **Secrets hardcoded or committed**
  - Symptom: API keys appear in source control.
  - Risk: Security incident and account abuse.
  - Mitigation: `.env` only; keep `.env` untracked.

### P1-High
- **Dependency drift**
  - Symptom: Different machines install incompatible package versions.
  - Risk: Non-reproducible bugs.
  - Mitigation: Introduce locked dependency file during stabilization.

- **No startup health verification**
  - Symptom: Server boots but hidden import/config errors remain.
  - Risk: Late discovery in integration phase.
  - Mitigation: Keep `/health` + startup checks in CI/local smoke tests.

### P2-Medium
- **Windows path and shell inconsistencies**
  - Symptom: Commands differ between PowerShell and bash.
  - Risk: Onboarding friction.
  - Mitigation: Add OS-specific command snippets in README.

---

## Phase 2: Data Ingestion and Profiling

### P0-Critical
- **Dataset unavailable or throttled**
  - Symptom: Load failures/timeouts from source.
  - Risk: Full pipeline blocked.
  - Mitigation: Add retry strategy and optional cached snapshot path.

- **Schema drift in dataset columns**
  - Symptom: Expected columns renamed/removed.
  - Risk: Silent bad mappings and invalid recommendations.
  - Mitigation: Explicit mapping audit + fail-fast warning logs.

### P1-High
- **Mixed data types in numeric fields**
  - Symptom: Ratings/cost include strings, commas, symbols.
  - Risk: Incorrect filtering/scoring.
  - Mitigation: Robust parsing + invalid-value counters.

- **Massive missingness in key fields**
  - Symptom: Many rows have empty location/cuisine/rating.
  - Risk: Low candidate quality and sparse outputs.
  - Mitigation: Null-threshold alarms and fallback policy adjustment.

### P2-Medium
- **Duplicate restaurant records**
  - Symptom: Same restaurant repeated with slight text variations.
  - Risk: Recommendation list repeats near-identical choices.
  - Mitigation: Normalize + deduplicate by name/location/cuisine signatures.

---

## Phase 3: Data Cleaning and Normalization

### P0-Critical
- **Over-aggressive cleaning drops valid rows**
  - Symptom: Candidate pool shrinks sharply after cleaning.
  - Risk: Frequent no-match scenarios.
  - Mitigation: Track row-retention metrics per cleaning step.

- **Incorrect budget mapping**
  - Symptom: Medium-budget users receive premium-only suggestions.
  - Risk: Core business logic failure.
  - Mitigation: Unit-test budget bands and edge thresholds.

### P1-High
- **Location normalization collisions**
  - Symptom: Distinct areas collapse into one token.
  - Risk: Irrelevant recommendations.
  - Mitigation: Maintain normalization dictionary with exceptions.

- **Cuisine tokenization errors**
  - Symptom: "North Indian, Chinese" split badly.
  - Risk: Semi-strict cuisine scoring becomes noisy.
  - Mitigation: Use robust delimiter and token cleanup.

### P2-Medium
- **Rating scale inconsistencies**
  - Symptom: Some ratings parsed as 0-100 and others 0-5.
  - Risk: Rank distortion.
  - Mitigation: Detect and normalize scale before scoring.

---

## Phase 4: Preference Filtering Engine

### P0-Critical
- **Strict filters return empty set too often**
  - Symptom: Most requests trigger fallback immediately.
  - Risk: Perceived poor system quality.
  - Mitigation: Telemetry on fallback frequency; tune matching thresholds.

- **Fallback order implemented incorrectly**
  - Symptom: Cuisine widens before rating relaxes.
  - Risk: Violates agreed policy.
  - Mitigation: Unit tests for fallback sequence path.

### P1-High
- **Semi-strict cuisine scoring too permissive**
  - Symptom: Weakly related cuisines ranked too high.
  - Risk: Relevance drop.
  - Mitigation: Minimum cuisine-score floor before final ranking.

- **Budget flexibility overwhelms relevance**
  - Symptom: Out-of-budget options dominate due to high ratings.
  - Risk: User dissatisfaction.
  - Mitigation: Cap budget penalty and reweight rank components.

### P2-Medium
- **Case/spacing mismatch in location matching**
  - Symptom: "new delhi" misses "New Delhi ".
  - Risk: False negatives.
  - Mitigation: Normalize + strip + accent-safe matching.

---

## Phase 5: LLM Ranking and Explanation

### P0-Critical
- **LLM returns non-JSON or malformed JSON**
  - Symptom: Parsing failures in production.
  - Risk: Endpoint failure or empty responses.
  - Mitigation: Strict prompt schema + parser guard + deterministic fallback.

- **Hallucinated restaurants not in candidates**
  - Symptom: Response includes unknown restaurant names.
  - Risk: Trust failure.
  - Mitigation: Post-validate output against candidate set before returning.

### P1-High
- **Primary provider downtime / quota exhaustion**
  - Symptom: OpenRouter free route fails intermittently.
  - Risk: Service instability.
  - Mitigation: Automatic Groq fallback + timeout/retry budget.

- **Fallback provider also unavailable**
  - Symptom: Both API calls fail.
  - Risk: Full recommendation outage.
  - Mitigation: Deterministic ranking fallback and explicit provider status.

### P2-Medium
- **Prompt token bloat**
  - Symptom: Long latency/cost due to too many candidates.
  - Risk: Slow responses and quota waste.
  - Mitigation: Hard cap candidate count and compress metadata.

- **Overly generic explanations**
  - Symptom: Explanations do not mention user preferences.
  - Risk: Low perceived intelligence.
  - Mitigation: Rubric checks in prompt and output validator.

---

## Phase 6: API and Output Layer

### P0-Critical
- **Response schema drift**
  - Symptom: Missing required fields (`estimated_cost`, `explanation`).
  - Risk: Client breakage.
  - Mitigation: Pydantic response model enforcement + contract tests.

- **Unhandled exceptions leak internal details**
  - Symptom: Raw stack traces in API responses.
  - Risk: Security and UX issues.
  - Mitigation: Central error handler and safe error messages.

### P1-High
- **Long request latency**
  - Symptom: Timeout under moderate load.
  - Risk: Unusable API.
  - Mitigation: Timeout controls, async clients, and candidate cap.

- **Inconsistent `top_n` behavior**
  - Symptom: Returns fewer/more items than requested without explanation.
  - Risk: Product inconsistency.
  - Mitigation: Enforce bounds and include reason when fewer available.

### P2-Medium
- **Floating-point display noise**
  - Symptom: Costs/ratings return with awkward precision.
  - Risk: UI polish issues.
  - Mitigation: Standardize output rounding.

---

## Phase 7: Quality, Testing, and Handover

### P0-Critical
- **No tests for fallback paths**
  - Symptom: Edge paths break unnoticed.
  - Risk: Production incidents under quota/provider failures.
  - Mitigation: Add unit + integration tests for all fallback branches.

- **No reproducible run instructions**
  - Symptom: Another engineer cannot run app from scratch.
  - Risk: Handover failure.
  - Mitigation: Verify README from clean environment.

### P1-High
- **Insufficient test data diversity**
  - Symptom: Tests pass for only ideal inputs.
  - Risk: Hidden regressions.
  - Mitigation: Include adversarial and sparse-data scenarios.

- **No observability for failure reasons**
  - Symptom: Hard to diagnose "bad recommendation" reports.
  - Risk: Slow incident resolution.
  - Mitigation: Structured logs for filtering path and provider used.

### P2-Medium
- **No baseline quality benchmark**
  - Symptom: Improvements cannot be measured.
  - Risk: Optimization without evidence.
  - Mitigation: Keep a fixed evaluation set and compare across versions.

---

## Cross-Phase Scenario Tests (Run Repeatedly)

- User asks for a location with zero rows in dataset.
- User sets `min_rating=5.0` and strict filters eliminate all candidates.
- Cuisine typo from user input (for example, "Itallian").
- OpenRouter key invalid; Groq key valid.
- OpenRouter and Groq both fail; deterministic fallback must still return top-N.
- Dataset contains malformed cost/rating text values.
- Requested `top_n=5`, but only 2 valid candidates remain after all filtering.

---

## Execution Use Pattern

Before each phase:
1. Scan this phase's `P0-Critical` items.
2. Add explicit checks/tests for each `P0`.
3. Perform explicit `P1/P2` review and record status (`pass|partial|deferred|fail`) in the phase gate evidence doc.
4. Record owner + target phase for each deferred `P1/P2` item.
5. Carry unresolved `P1/P2` items forward and re-check in every subsequent phase.
6. Close `P2/P3` during hardening before delivery sign-off.
