from __future__ import annotations

import re

import pandas as pd

from .models import RecommendationRequest


BUDGET_RANGES = {
    "low": (0, 800),
    "medium": (801, 2000),
    "high": (2001, 1_000_000),
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _location_match(df: pd.DataFrame, location: str) -> pd.DataFrame:
    needle = _normalize(location)
    return df[df["location"].str.lower().str.contains(needle, na=False)]


def _rating_match(df: pd.DataFrame, minimum_rating: float) -> pd.DataFrame:
    return df[df["rating"] >= minimum_rating]


def _cuisine_similarity_score(cuisine_text: str, preferred_cuisine: str) -> float:
    preferred = _normalize(preferred_cuisine)
    hay = _normalize(cuisine_text)
    if preferred in hay:
        return 1.0

    preferred_tokens = set(preferred.split())
    hay_tokens = set(hay.replace(",", " ").split())
    if not preferred_tokens or not hay_tokens:
        return 0.0
    overlap = len(preferred_tokens.intersection(hay_tokens))
    return overlap / len(preferred_tokens)


def _budget_score(cost_for_two: float, budget: str) -> float:
    lo, hi = BUDGET_RANGES[budget]
    if lo <= cost_for_two <= hi:
        return 1.0
    # Flexible budget: near-range restaurants are not discarded, only down-scored.
    if cost_for_two < lo:
        diff = lo - cost_for_two
    else:
        diff = cost_for_two - hi
    return max(0.0, 1.0 - (diff / max(hi, 1)))


def filter_candidates(df: pd.DataFrame, req: RecommendationRequest) -> tuple[pd.DataFrame, bool, str]:
    # Strict location and rating first.
    filtered = _location_match(df, req.location)
    filtered = _rating_match(filtered, req.min_rating)
    fallback_applied = False
    strategy = "strict location + strict rating + semi-strict cuisine + flexible budget"

    if filtered.empty:
        fallback_applied = True
        relaxed_rating = max(0.0, req.min_rating - 0.5)
        filtered = _location_match(df, req.location)
        filtered = _rating_match(filtered, relaxed_rating)
        strategy = "fallback: rating relaxed by 0.5"

    if filtered.empty:
        # Widen cuisine implicitly by using location + relaxed rating only.
        fallback_applied = True
        filtered = _location_match(df, req.location)
        strategy = "fallback: widened cuisine after rating relaxation"

    if filtered.empty:
        # Last fallback: keep best global options by rating.
        fallback_applied = True
        filtered = df.copy()
        strategy = "global fallback: no location hits, ranked globally"

    filtered = filtered.copy()
    filtered["cuisine_score"] = filtered["cuisine"].apply(
        lambda c: _cuisine_similarity_score(str(c), req.cuisine)
    )
    filtered["budget_score"] = filtered["average_cost_for_two"].apply(
        lambda cost: _budget_score(float(cost), req.budget)
    )
    filtered["rank_score"] = (
        (filtered["rating"] * 0.50)
        + (filtered["cuisine_score"] * 0.35 * 5.0)
        + (filtered["budget_score"] * 0.15 * 5.0)
    )

    # Semi-strict cuisine: prioritize close matches before low similarity rows.
    filtered = filtered.sort_values(
        by=["cuisine_score", "rank_score", "rating"], ascending=[False, False, False]
    )

    return filtered.reset_index(drop=True), fallback_applied, strategy
