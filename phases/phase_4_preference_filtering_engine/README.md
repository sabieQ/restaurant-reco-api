# Phase 4 - Preference Filtering Engine

This phase validates deterministic filtering behavior and fallback sequencing.

## Outputs
- `filter_engine_validation_report.json`
- `filter_engine_validation_summary.md`
- `phase-4-gate-evidence.md`

## Run
```powershell
py -3.11 .\validate_filtering.py
```

## P0 checks in this phase
1. Strict filters do not return empty set too often.
2. Fallback order is exactly: relax rating by 0.5, then widen cuisine.
