from __future__ import annotations

import pandas as pd
from huggingface_hub import hf_hub_download

# Direct data loading without pydantic dependency
def load_restaurants_df_standalone() -> pd.DataFrame:
    dataset_id = "ManikaSaini/zomato-restaurant-recommendation"
    csv_path = hf_hub_download(repo_id=dataset_id, repo_type="dataset", filename="zomato.csv")
    df = pd.read_csv(csv_path)

    columns = list(df.columns)
    
    def _best_match_column(columns: list[str], options: list[str]) -> str | None:
        lowered = {c.lower(): c for c in columns}
        for opt in options:
            if opt in lowered:
                return lowered[opt]
        return None

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

    df = df[["restaurant_name", "location", "cuisine", "average_cost_for_two", "rating"]].copy()

    # Normalize core columns
    df["restaurant_name"] = df["restaurant_name"].fillna("Unknown").astype(str).str.strip()
    df["location"] = df["location"].fillna("").astype(str).str.strip()
    df["cuisine"] = df["cuisine"].fillna("").astype(str).str.strip()
    
    def _to_float(value, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            if isinstance(value, str):
                value = value.replace(",", "").strip()
            return float(value)
        except (TypeError, ValueError):
            return default

    def _parse_rating(value, default: float = 0.0) -> float:
        if value is None:
            return default
        text = str(value).strip().upper()
        if text in {"NEW", "-", "NAN", ""}:
            return default
        if "/" in text:
            text = text.split("/", 1)[0].strip()
        import re
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

    df["average_cost_for_two"] = df["average_cost_for_two"].apply(_to_float)
    df["rating"] = df["rating"].apply(_parse_rating)

    df = df[(df["restaurant_name"] != "") & (df["location"] != "")]

    # Deduplicate restaurants based on name, location, and cuisine
    # Keep the entry with the highest rating when duplicates exist
    df = df.sort_values("rating", ascending=False).drop_duplicates(
        subset=["restaurant_name", "location", "cuisine"], keep="first"
    )

    return df.reset_index(drop=True)


# Simplified filter logic
BUDGET_RANGES = {
    "low": (0, 800),
    "medium": (801, 2000),
    "high": (2001, float("inf")),
}

def filter_candidates_standalone(df: pd.DataFrame, request: dict) -> tuple[pd.DataFrame, bool, str]:
    location = request["location"].lower().strip()
    budget = request["budget"]
    cuisine = request.get("cuisine", "").lower().strip()
    min_rating = request["min_rating"]

    # Strict location
    filtered = df[df["location"].str.lower().str.contains(location, na=False)].copy()

    # Strict rating
    filtered = filtered[filtered["rating"] >= min_rating].copy()

    # Semi-strict cuisine
    if cuisine:
        filtered["cuisine_score"] = filtered["cuisine"].apply(
            lambda x: 1.0 if cuisine in x.lower() else 0.3 if any(c in x.lower() for c in cuisine.split()) else 0.0
        )
        filtered = filtered[filtered["cuisine_score"] > 0].copy()
    else:
        filtered["cuisine_score"] = 1.0

    # Flexible budget
    lo, hi = BUDGET_RANGES.get(budget, (0, float("inf")))
    filtered["budget_penalty"] = filtered["average_cost_for_two"].apply(
        lambda x: 0.0 if lo <= x <= hi else 0.5
    )

    # Scoring
    filtered["score"] = (
        filtered["rating"] * 0.5 +
        filtered["cuisine_score"] * 0.3 +
        (1 - filtered["budget_penalty"]) * 0.2
    )
    filtered = filtered.sort_values("score", ascending=False)

    fallback_applied = False
    strategy = "strict location + strict rating + semi-strict cuisine + flexible budget"

    if len(filtered) == 0:
        fallback_applied = True
        # Relax rating
        relaxed_rating = max(0, min_rating - 0.5)
        filtered = df[df["location"].str.lower().str.contains(location, na=False)].copy()
        filtered = filtered[filtered["rating"] >= relaxed_rating].copy()
        if cuisine:
            filtered["cuisine_score"] = filtered["cuisine"].apply(
                lambda x: 1.0 if cuisine in x.lower() else 0.3 if any(c in x.lower() for c in cuisine.split()) else 0.0
            )
            filtered = filtered[filtered["cuisine_score"] > 0].copy()
        else:
            filtered["cuisine_score"] = 1.0

        if len(filtered) == 0:
            # Widen cuisine
            filtered = df[df["location"].str.lower().str.contains(location, na=False)].copy()
            filtered = filtered[filtered["rating"] >= relaxed_rating].copy()
            filtered["cuisine_score"] = 1.0
            strategy = "rating relaxed + cuisine widened"
        else:
            strategy = "rating relaxed"
    else:
        strategy = "strict location + strict rating + semi-strict cuisine + flexible budget"

    return filtered, fallback_applied, strategy


def main():
    print("Testing Phase 4 Filtering Engine")
    print("=" * 50)
    
    # Load data
    print("\nLoading dataset...")
    df = load_restaurants_df_standalone()
    print(f"Total restaurants in dataset: {len(df)}")
    
    # Test with Bellandur, budget 2000, rating 4.0
    test_request = {
        "location": "Bellandur",
        "budget": 2000,
        "cuisine": "",  # No cuisine specified
        "min_rating": 4.0,
        "top_n": 5
    }
    
    print(f"\nTest Request:")
    print(f"  Location: {test_request['location']}")
    print(f"  Budget: {test_request['budget']}")
    print(f"  Min Rating: {test_request['min_rating']}")
    print(f"  Cuisine: {test_request['cuisine'] or 'Any'}")
    
    # Determine budget band
    if test_request["budget"] <= 800:
        budget_band = "low"
    elif test_request["budget"] <= 2000:
        budget_band = "medium"
    else:
        budget_band = "high"
    
    test_request["budget"] = budget_band
    print(f"  Budget Band: {budget_band}")
    
    # Run filtering
    print("\nRunning filter...")
    filtered, fallback_applied, strategy = filter_candidates_standalone(df, test_request)
    
    print(f"\nResults:")
    print(f"  Total candidates found: {len(filtered)}")
    print(f"  Fallback applied: {fallback_applied}")
    print(f"  Strategy used: {strategy}")
    
    if len(filtered) > 0:
        print(f"\nTop 5 Recommendations:")
        print("-" * 80)
        for idx, row in filtered.head(5).iterrows():
            print(f"\n{idx + 1}. {row['restaurant_name']}")
            print(f"   Cuisine: {row['cuisine']}")
            print(f"   Rating: {row['rating']}")
            print(f"   Cost for Two: Rs.{row['average_cost_for_two']:.0f}")
            print(f"   Location: {row['location']}")
            print(f"   Score: {row['score']:.3f}")
    else:
        print("\nNo candidates found matching the criteria.")


if __name__ == "__main__":
    main()
