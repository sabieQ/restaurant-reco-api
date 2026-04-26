# Phase 3 - Data Cleaning and Normalization

This phase standardizes raw restaurant records and verifies that cleaning does not over-drop valid rows.

## Outputs
- `cleaning_report.json`
- `cleaning_summary.md`
- `cleaned_preview.csv`
- `phase-3-gate-evidence.md`

## Run

```powershell
py -3.11 -m pip install -r ..\..\requirements.txt
py -3.11 .\clean_normalize.py
```

## P0 Edge Cases Checked
1. Over-aggressive cleaning drops valid rows.
2. Incorrect budget mapping.
