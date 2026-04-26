from __future__ import annotations

from functools import lru_cache
import re
from typing import Any

import pandas as pd
from huggingface_hub import hf_hub_download

from .config import get_settings


EXPECTED_CANONICAL_COLUMNS = [
    "restaurant_name",
    "location",
    "cuisine",
    "average_cost_for_two",
    "rating",
]


def _best_match_column(columns: list[str], options: list[str]) -> str | None:
    lowered = {c.lower(): c for c in columns}
    for opt in options:
        if opt in lowered:
            return lowered[opt]
    return None


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_rating(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip().upper()
    if text in {"NEW", "-", "NAN", ""}:
        return default
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    text = re.sub(r"[^0-9.]", "", text)
    if not text:
        return default
    try:
        val = float(text)
    except ValueError:
        return default
    if val > 5.0:
        return default
    return val


@lru_cache(maxsize=1)
def load_restaurants_df() -> pd.DataFrame:
    settings = get_settings()

    # Use CSV download path to avoid parquet loader restrictions on locked-down Windows setups.
    csv_path = hf_hub_download(
        repo_id=settings.dataset_id, repo_type="dataset", filename="zomato.csv"
    )
    df = pd.read_csv(csv_path)

    columns = list(df.columns)
    mapping = {
        "restaurant_name": _best_match_column(columns, ["restaurant_name", "name", "restaurant"]),
        "location": _best_match_column(columns, ["location", "city", "locality"]),
        "cuisine": _best_match_column(columns, ["cuisine", "cuisines"]),
        "average_cost_for_two": _best_match_column(
            columns,
            ["average_cost_for_two", "cost_for_two", "average cost for two", "approx_cost(for two people)"],
        ),
        "rating": _best_match_column(columns, ["rating", "aggregate_rating", "user_rating", "rate"]),
    }

    for canonical_col, source_col in mapping.items():
        if source_col is None:
            df[canonical_col] = None
        else:
            df[canonical_col] = df[source_col]

    df = df[EXPECTED_CANONICAL_COLUMNS].copy()

    # Normalize core columns used by filter policy.
    df["restaurant_name"] = df["restaurant_name"].fillna("Unknown").astype(str).str.strip()
    df["location"] = df["location"].fillna("").astype(str).str.strip()
    df["cuisine"] = df["cuisine"].fillna("").astype(str).str.strip()
    df["average_cost_for_two"] = df["average_cost_for_two"].apply(_to_float)
    df["rating"] = df["rating"].apply(_parse_rating)

    # Filter out rows with unusable mandatory fields.
    df = df[(df["restaurant_name"] != "") & (df["location"] != "")]

    # Deduplicate restaurants based on name, location, and cuisine
    # Keep the entry with the highest rating when duplicates exist
    df = df.sort_values("rating", ascending=False).drop_duplicates(
        subset=["restaurant_name", "location", "cuisine"], keep="first"
    )

    return df.reset_index(drop=True)
