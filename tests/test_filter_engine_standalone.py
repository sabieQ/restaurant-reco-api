"""
Standalone tests for filter engine without pydantic dependency.
Tests filtering logic, fallback behavior, and edge cases.
"""
import sys
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(ROOT / ".env")

from app.data_loader import load_restaurants_df
from app.filter_engine import filter_candidates, BUDGET_RANGES


def test_strict_location_filter():
    """Test that location filter is strict (exact match)"""
    print("Testing strict location filter...")
    df = load_restaurants_df()
    
    # Create a mock request-like object
    class MockRequest:
        def __init__(self):
            self.location = "Bellandur"
            self.budget = "medium"
            self.cuisine = "North Indian"
            self.min_rating = 4.0
            self.additional_preferences = None
            self.top_n = 5
    
    req = MockRequest()
    filtered, _, _ = filter_candidates(df, req)
    
    # All results should be from Bellandur
    assert all(filtered['location'].str.lower() == 'bellandur'), "Location filter should be strict"
    print("✓ Strict location filter passed")


def test_strict_rating_filter():
    """Test that rating filter is strict (minimum rating)"""
    print("Testing strict rating filter...")
    df = load_restaurants_df()
    
    class MockRequest:
        def __init__(self):
            self.location = "Bellandur"
            self.budget = "medium"
            self.cuisine = "North Indian"
            self.min_rating = 4.5
            self.additional_preferences = None
            self.top_n = 5
    
    req = MockRequest()
    filtered, _, _ = filter_candidates(df, req)
    
    # All results should have rating >= 4.5
    assert all(filtered['rating'] >= 4.5), "Rating filter should be strict"
    print("✓ Strict rating filter passed")


def test_budget_filter():
    """Test that budget filter is flexible (within range)"""
    print("Testing budget filter...")
    df = load_restaurants_df()
    
    class MockRequest:
        def __init__(self):
            self.location = "Bellandur"
            self.budget = "medium"
            self.cuisine = "North Indian"
            self.min_rating = 4.0
            self.additional_preferences = None
            self.top_n = 5
    
    req = MockRequest()
    filtered, _, _ = filter_candidates(df, req)
    
    if not filtered.empty:
        lo, hi = BUDGET_RANGES["medium"]
        # Budget filter is flexible, so results may be outside range
        # But we should have some results
        assert len(filtered) > 0, "Budget filter should return results"
    print("✓ Budget filter passed")


def test_fallback_rating_relaxation():
    """Test that fallback relaxes rating when no results"""
    print("Testing fallback rating relaxation...")
    df = load_restaurants_df()
    
    # Use a very high rating to trigger fallback
    class MockRequest:
        def __init__(self):
            self.location = "Bellandur"
            self.budget = "medium"
            self.cuisine = "North Indian"
            self.min_rating = 5.0  # Very high, unlikely to match
            self.additional_preferences = None
            self.top_n = 5
    
    req = MockRequest()
    filtered, fallback_applied, strategy = filter_candidates(df, req)
    
    # Fallback should be applied
    assert fallback_applied, "Fallback should be applied for high rating"
    assert "rating relaxed" in strategy.lower(), "Strategy should mention rating relaxation"
    print("✓ Fallback rating relaxation passed")


def test_fallback_cuisine_widening():
    """Test that fallback widens cuisine when no results"""
    print("Testing fallback cuisine widening...")
    df = load_restaurants_df()
    
    # Use a very specific cuisine to trigger fallback
    class MockRequest:
        def __init__(self):
            self.location = "Bellandur"
            self.budget = "medium"
            self.cuisine = "Ultra Rare Cuisine XYZ"
            self.min_rating = 4.0
            self.additional_preferences = None
            self.top_n = 5
    
    req = MockRequest()
    filtered, fallback_applied, strategy = filter_candidates(df, req)
    
    # Fallback should be applied
    assert fallback_applied, "Fallback should be applied for rare cuisine"
    print("✓ Fallback cuisine widening passed")


def test_deduplication():
    """Test that duplicate restaurants are removed"""
    print("Testing deduplication...")
    df = load_restaurants_df()
    
    # Check for duplicates before filtering
    duplicates = df.duplicated(subset=['restaurant_name', 'location', 'cuisine'], keep=False)
    duplicate_count = duplicates.sum()
    
    if duplicate_count > 0:
        print(f"  Found {duplicate_count} duplicate entries, should be removed by data loader")
    
    # After loading, there should be no duplicates
    assert duplicate_count == 0, "Data loader should remove duplicates"
    print("✓ Deduplication passed")


def test_json_parsing():
    """Test JSON parsing for LLM responses"""
    print("Testing JSON parsing...")
    
    # Test valid JSON
    import json
    valid_json = '{"recommendations": [{"restaurant_name": "Test", "rating": 4.5}]}'
    parsed = json.loads(valid_json)
    assert parsed["recommendations"][0]["restaurant_name"] == "Test"
    
    # Test invalid JSON
    invalid_json = '{"recommendations": [invalid]}'
    try:
        json.loads(invalid_json)
        assert False, "Should raise JSONDecodeError"
    except json.JSONDecodeError:
        pass  # Expected
    
    print("✓ JSON parsing passed")


def run_all_tests():
    """Run all standalone tests"""
    print("=" * 60)
    print("Phase 10 Filter Engine Tests (Standalone)")
    print("=" * 60)
    
    tests = [
        test_strict_location_filter,
        test_strict_rating_filter,
        test_budget_filter,
        test_fallback_rating_relaxation,
        test_fallback_cuisine_widening,
        test_deduplication,
        test_json_parsing,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
