from __future__ import annotations

import json
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


def best_match(columns: list[str], options: list[str]) -> str | None:
    lowered = {c.lower(): c for c in columns}
    for opt in options:
        if opt in lowered:
            return lowered[opt]
    return None


def to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    phase_dir = Path(__file__).resolve().parent
    json_report = phase_dir / "dataset_profile_report.json"
    md_summary = phase_dir / "dataset_profile_summary.md"

    report: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "dataset_file": DATASET_FILE,
        "edge_case_checklist_run": {
            "p0_dataset_unavailable_or_throttled": "pending",
            "p0_schema_drift": "pending",
        },
    }

    try:
        csv_path = hf_hub_download(repo_id=DATASET_ID, repo_type="dataset", filename=DATASET_FILE)
        df = pd.read_csv(csv_path)
        report["edge_case_checklist_run"]["p0_dataset_unavailable_or_throttled"] = "pass"
    except Exception as exc:
        report["edge_case_checklist_run"]["p0_dataset_unavailable_or_throttled"] = "fail"
        report["dataset_load_error"] = str(exc)
        json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_summary.write_text(
            "# Dataset Profile Summary\n\nDataset load failed. See JSON report for details.\n",
            encoding="utf-8",
        )
        return 1

    columns = list(df.columns)

    field_mapping: dict[str, str | None] = {
        canonical: best_match(columns, options)
        for canonical, options in CANONICAL_OPTIONS.items()
    }

    missing_canonical = [k for k, v in field_mapping.items() if v is None]
    schema_pass = len(missing_canonical) == 0
    report["edge_case_checklist_run"]["p0_schema_drift"] = "pass" if schema_pass else "fail"

    prof: dict[str, Any] = {
        "row_count": int(len(df)),
        "column_count": int(len(columns)),
        "columns": columns,
        "canonical_mapping": field_mapping,
        "missing_canonical_fields": missing_canonical,
        "field_stats": {},
    }

    for canonical, source in field_mapping.items():
        if source is None:
            prof["field_stats"][canonical] = {"status": "missing"}
            continue

        s = df[source]
        null_count = int(s.isna().sum())
        unique_count = int(s.nunique(dropna=True))
        sample_values = [str(x) for x in s.dropna().head(5).tolist()]

        field_info: dict[str, Any] = {
            "source_column": source,
            "null_count": null_count,
            "null_pct": round((null_count / max(len(df), 1)) * 100, 2),
            "unique_count": unique_count,
            "sample_values": sample_values,
        }

        if canonical in {"average_cost_for_two", "rating"}:
            numeric = s.apply(to_float).dropna()
            field_info["parseable_numeric_count"] = int(len(numeric))
            field_info["numeric_parse_pct"] = round((len(numeric) / max(len(s), 1)) * 100, 2)
            if not numeric.empty:
                field_info["min"] = float(numeric.min())
                field_info["max"] = float(numeric.max())
                field_info["mean"] = float(round(numeric.mean(), 3))

        prof["field_stats"][canonical] = field_info

    report["profile"] = prof

    json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# Dataset Profile Summary",
        "",
        f"- Dataset: `{DATASET_ID}` (`{DATASET_FILE}`)",
        f"- Rows: `{prof['row_count']}`",
        f"- Columns: `{prof['column_count']}`",
        f"- P0 dataset availability: `{report['edge_case_checklist_run']['p0_dataset_unavailable_or_throttled']}`",
        f"- P0 schema drift: `{report['edge_case_checklist_run']['p0_schema_drift']}`",
        "",
        "## Canonical Mapping",
    ]
    for canonical, source in field_mapping.items():
        summary_lines.append(f"- `{canonical}` -> `{source}`")

    if missing_canonical:
        summary_lines.extend(
            [
                "",
                "## Missing Canonical Fields",
                f"- {', '.join(missing_canonical)}",
            ]
        )

    md_summary.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
