from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import hf_hub_download

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
DATASET_FILE = "zomato.csv"

CANONICAL_OPTIONS = {
    "restaurant_name": ["restaurant_name", "name", "restaurant"],
    "location": ["location", "city", "locality"],
    "cuisine": ["cuisine", "cuisines"],
    "average_cost_for_two": [
        "average_cost_for_two",
        "cost_for_two",
        "average cost for two",
        "approx_cost(for two people)",
    ],
    "rating": ["rating", "aggregate_rating", "user_rating", "rate"],
}

BUDGET_BANDS = {
    "low": (0, 800),
    "medium": (801, 2000),
    "high": (2001, 10**9),
}


def best_match(columns: list[str], options: list[str]) -> str | None:
    lowered = {c.lower(): c for c in columns}
    for opt in options:
        if opt in lowered:
            return lowered[opt]
    return None


def parse_cost(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def parse_rating(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if text in {"NEW", "-", "NAN", ""}:
        return None
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    text = re.sub(r"[^0-9.]", "", text)
    if not text:
        return None
    try:
        val = float(text)
    except ValueError:
        return None
    if val > 5.0:
        return None
    return val


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def budget_bucket(cost_for_two: float | None) -> str | None:
    if cost_for_two is None:
        return None
    for label, (lo, hi) in BUDGET_BANDS.items():
        if lo <= cost_for_two <= hi:
            return label
    return None


def run_budget_boundary_tests() -> dict[str, Any]:
    tests = [
        (0, "low"),
        (800, "low"),
        (801, "medium"),
        (2000, "medium"),
        (2001, "high"),
    ]
    results = []
    all_pass = True
    for value, expected in tests:
        actual = budget_bucket(float(value))
        passed = actual == expected
        all_pass = all_pass and passed
        results.append({"input_cost": value, "expected": expected, "actual": actual, "pass": passed})
    return {"pass": all_pass, "cases": results}


def main() -> int:
    phase_dir = Path(__file__).resolve().parent
    report_path = phase_dir / "cleaning_report.json"
    summary_path = phase_dir / "cleaning_summary.md"
    preview_path = phase_dir / "cleaned_preview.csv"

    csv_path = hf_hub_download(repo_id=DATASET_ID, repo_type="dataset", filename=DATASET_FILE)
    raw_df = pd.read_csv(csv_path)
    row_counts: dict[str, int] = {"raw_rows": int(len(raw_df))}

    mapping = {k: best_match(list(raw_df.columns), v) for k, v in CANONICAL_OPTIONS.items()}
    missing = [k for k, v in mapping.items() if v is None]
    if missing:
        report = {"status": "fail", "reason": "schema_drift", "missing_canonical_fields": missing}
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        summary_path.write_text(
            "# Cleaning Summary\n\nSchema drift detected. Missing: " + ", ".join(missing) + "\n",
            encoding="utf-8",
        )
        return 1

    df = pd.DataFrame(
        {
            "restaurant_name": raw_df[mapping["restaurant_name"]].apply(normalize_text),
            "location": raw_df[mapping["location"]].apply(normalize_text),
            "cuisine": raw_df[mapping["cuisine"]].apply(normalize_text),
            "average_cost_for_two": raw_df[mapping["average_cost_for_two"]].apply(parse_cost),
            "rating": raw_df[mapping["rating"]].apply(parse_rating),
        }
    )
    row_counts["after_canonical_projection"] = int(len(df))

    # Drop only records that cannot participate in recommendations.
    cleaned = df[(df["restaurant_name"] != "") & (df["location"] != "")]
    row_counts["after_required_text_fields"] = int(len(cleaned))

    # Keep rows with at least one of rating/cost present to avoid excessive drops.
    cleaned = cleaned[
        cleaned["rating"].notna() | cleaned["average_cost_for_two"].notna()
    ].copy()
    row_counts["after_numeric_presence_filter"] = int(len(cleaned))

    cleaned["budget_bucket"] = cleaned["average_cost_for_two"].apply(budget_bucket)
    cleaned["location_norm"] = cleaned["location"].str.lower()
    cleaned["cuisine_norm"] = cleaned["cuisine"].str.lower()

    retention_pct = round((len(cleaned) / max(len(raw_df), 1)) * 100, 2)
    over_drop_pass = retention_pct >= 70.0
    budget_test = run_budget_boundary_tests()

    cleaned.head(200).to_csv(preview_path, index=False)

    report = {
        "status": "pass" if (over_drop_pass and budget_test["pass"]) else "fail",
        "dataset_id": DATASET_ID,
        "dataset_file": DATASET_FILE,
        "canonical_mapping": mapping,
        "row_counts": row_counts,
        "retention_pct": retention_pct,
        "edge_case_checklist_run": {
            "p0_over_aggressive_cleaning_drops_rows": {
                "pass": over_drop_pass,
                "threshold_pct": 70.0,
                "actual_retention_pct": retention_pct,
            },
            "p0_incorrect_budget_mapping": budget_test,
        },
        "null_stats_after_cleaning": {
            "rating_null_pct": round((cleaned["rating"].isna().mean()) * 100, 2),
            "cost_null_pct": round((cleaned["average_cost_for_two"].isna().mean()) * 100, 2),
        },
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# Cleaning Summary",
        "",
        f"- Dataset: `{DATASET_ID}` (`{DATASET_FILE}`)",
        f"- Raw rows: `{row_counts['raw_rows']}`",
        f"- Rows after required text fields: `{row_counts['after_required_text_fields']}`",
        f"- Rows after numeric presence filter: `{row_counts['after_numeric_presence_filter']}`",
        f"- Retention: `{retention_pct}%`",
        f"- P0 over-aggressive cleaning: `{'pass' if over_drop_pass else 'fail'}`",
        f"- P0 incorrect budget mapping: `{'pass' if budget_test['pass'] else 'fail'}`",
        "",
        "## Canonical Mapping",
    ]
    for k, v in mapping.items():
        summary_lines.append(f"- `{k}` -> `{v}`")
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
