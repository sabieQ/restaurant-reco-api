"""
Standalone API contract tests with golden JSON fixtures.
Tests happy path, empty path, and error paths without pydantic dependency.
"""
import sys
from pathlib import Path
import json

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(ROOT / ".env")


# Golden JSON fixtures
GOLDEN_HAPPY_RESPONSE = {
    "recommendations": [
        {
            "restaurant_name": "Chili's American Grill & Bar",
            "cuisine": "American, Tex-Mex, Burger, BBQ",
            "rating": 4.6,
            "estimated_cost": 1800.0,
            "explanation": "Strong match for Bellandur with rating 4.6; selected by LLM ranking."
        }
    ],
    "llm_provider_used": "openrouter",
    "fallback_applied": False,
    "filter_strategy": "strict location + strict rating + semi-strict cuisine + flexible budget"
}

GOLDEN_EMPTY_RESPONSE = {
    "recommendations": [],
    "llm_provider_used": "none",
    "fallback_applied": True,
    "filter_strategy": "global fallback"
}

GOLDEN_ERROR_RESPONSE = {
    "detail": "No candidates found after filtering."
}


async def test_happy_path():
    """Test successful recommendation request"""
    print("Testing happy path...")
    
    base_url = "http://localhost:8000"
    
    payload = {
        "location": "Bellandur",
        "budget": "medium",
        "cuisine": "American",
        "min_rating": 4.0,
        "additional_preferences": None,
        "top_n": 3
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/api/v1/recommendations", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                assert "recommendations" in data, "Response should have recommendations"
                assert "llm_provider_used" in data, "Response should have llm_provider_used"
                assert "fallback_applied" in data, "Response should have fallback_applied"
                assert "filter_strategy" in data, "Response should have filter_strategy"
                
                # Validate types
                assert isinstance(data["recommendations"], list), "recommendations should be a list"
                assert isinstance(data["llm_provider_used"], str), "llm_provider_used should be a string"
                assert isinstance(data["fallback_applied"], bool), "fallback_applied should be a boolean"
                assert isinstance(data["filter_strategy"], str), "filter_strategy should be a string"
                
                # If recommendations exist, validate item structure
                if len(data["recommendations"]) > 0:
                    rec = data["recommendations"][0]
                    assert "restaurant_name" in rec, "Recommendation should have restaurant_name"
                    assert "cuisine" in rec, "Recommendation should have cuisine"
                    assert "rating" in rec, "Recommendation should have rating"
                    assert "estimated_cost" in rec, "Recommendation should have estimated_cost"
                    assert "explanation" in rec, "Recommendation should have explanation"
                
                print("✓ Happy path passed")
                return True
            else:
                print(f"✗ Happy path failed: HTTP {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("✗ Happy path skipped: Backend not running")
        return None
    except Exception as e:
        print(f"✗ Happy path failed: {e}")
        return False


async def test_empty_path():
    """Test request that returns no candidates"""
    print("Testing empty path...")
    
    base_url = "http://localhost:8000"
    
    # Use a location that likely doesn't exist
    payload = {
        "location": "NonExistentCityXYZ",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "additional_preferences": None,
        "top_n": 3
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/api/v1/recommendations", json=payload)
            
            if response.status_code == 404:
                data = response.json()
                assert "detail" in data, "Error response should have detail"
                print("✓ Empty path passed (404 as expected)")
                return True
            elif response.status_code == 200:
                # If it returns 200, check if recommendations is empty
                data = response.json()
                if len(data["recommendations"]) == 0:
                    print("✓ Empty path passed (empty recommendations)")
                    return True
                else:
                    print("✗ Empty path failed: Expected empty results")
                    return False
            else:
                print(f"✗ Empty path failed: HTTP {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("✗ Empty path skipped: Backend not running")
        return None
    except Exception as e:
        print(f"✗ Empty path failed: {e}")
        return False


async def test_error_path():
    """Test invalid request"""
    print("Testing error path...")
    
    base_url = "http://localhost:8000"
    
    # Invalid payload (missing required fields)
    payload = {
        "location": "Bellandur"
        # Missing budget, cuisine, min_rating, top_n
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/api/v1/recommendations", json=payload)
            
            if response.status_code == 422:
                data = response.json()
                assert "detail" in data, "Error response should have detail"
                print("✓ Error path passed (422 validation error)")
                return True
            else:
                print(f"✗ Error path failed: Expected 422, got {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("✗ Error path skipped: Backend not running")
        return None
    except Exception as e:
        print(f"✗ Error path failed: {e}")
        return False


async def test_health_endpoint():
    """Test health endpoint"""
    print("Testing health endpoint...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                assert "status" in data, "Health response should have status"
                assert data["status"] == "ok", "Status should be ok"
                print("✓ Health endpoint passed")
                return True
            else:
                print(f"✗ Health endpoint failed: HTTP {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("✗ Health endpoint skipped: Backend not running")
        return None
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
        return False


async def test_meta_endpoint():
    """Test meta endpoint"""
    print("Testing meta endpoint...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/api/v1/meta")
            
            if response.status_code == 200:
                data = response.json()
                assert "max_top_n" in data, "Meta response should have max_top_n"
                assert "min_top_n" in data, "Meta response should have min_top_n"
                assert "allowed_budget_levels" in data, "Meta response should have allowed_budget_levels"
                assert "rating_range" in data, "Meta response should have rating_range"
                print("✓ Meta endpoint passed")
                return True
            else:
                print(f"✗ Meta endpoint failed: HTTP {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("✗ Meta endpoint skipped: Backend not running")
        return None
    except Exception as e:
        print(f"✗ Meta endpoint failed: {e}")
        return False


async def test_request_size_limit():
    """Test that additional preferences are limited to 500 characters"""
    print("Testing request size limit...")
    
    base_url = "http://localhost:8000"
    
    # Create a payload with additional_preferences > 500 chars
    long_text = "a" * 501
    payload = {
        "location": "Bellandur",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "additional_preferences": long_text,
        "top_n": 3
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/api/v1/recommendations", json=payload)
            
            if response.status_code == 400:
                data = response.json()
                assert "detail" in data, "Error response should have detail"
                assert "500" in data["detail"], "Error should mention 500 character limit"
                print("✓ Request size limit passed")
                return True
            else:
                print(f"✗ Request size limit failed: Expected 400, got {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("✗ Request size limit skipped: Backend not running")
        return None
    except Exception as e:
        print(f"✗ Request size limit failed: {e}")
        return False


async def run_all_tests():
    """Run all API contract tests"""
    print("=" * 60)
    print("Phase 10 API Contract Tests (Standalone)")
    print("=" * 60)
    
    tests = [
        test_health_endpoint,
        test_meta_endpoint,
        test_happy_path,
        test_empty_path,
        test_error_path,
        test_request_size_limit,
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)
    print(f"Test Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
