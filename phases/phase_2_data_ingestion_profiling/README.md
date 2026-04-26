# Phase 2 - Data Ingestion and Profiling

This phase validates dataset accessibility, detects schema drift, and produces a profiling report for canonical recommendation fields.

## Outputs
- `dataset_profile_report.json`
- `dataset_profile_summary.md`
- `phase-2-gate-evidence.md`

## Run (PowerShell)

```powershell
py -3.11 -m pip install -r ..\..\requirements.txt
py -3.11 .\profile_dataset.py
```

## Canonical Fields Checked
- `restaurant_name`
- `location`
- `cuisine`
- `average_cost_for_two`
- `rating`

## Edge-case-checklist run
This phase explicitly verifies the Phase 2 `P0` items:
1. Dataset unavailable or throttled
2. Schema drift in dataset columns
