import sys
import os
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables from root directory
env_path = ROOT / ".env"
load_dotenv(env_path)


async def test_api_contract():
    """Test API response schema without pydantic dependency"""
    print("Running Phase 6 API Contract Test (Standalone)...")
    
    base_url = "http://localhost:8000"
    
    # Test payload with Indian location (dataset is Indian restaurants)
    payload = {
        "location": "Bellandur",
        "budget": "medium",
        "cuisine": "American",
        "min_rating": 4.0,
        "top_n": 3
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/recommend", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response schema
                required_fields = ["recommendations", "llm_provider_used", "fallback_applied", "filter_strategy"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"Contract Test Failed: Missing fields: {missing_fields}")
                    return False
                
                # Check recommendation item schema
                recos = data["recommendations"]
                if len(recos) > 0:
                    item_fields = ["restaurant_name", "cuisine", "rating", "estimated_cost", "explanation"]
                    for reco in recos:
                        missing_item_fields = [field for field in item_fields if field not in reco]
                        if missing_item_fields:
                            print(f"Contract Test Failed: Recommendation missing fields: {missing_item_fields}")
                            return False
                
                print("Contract Test Passed: Response schema contains all required fields.")
                print(f"  - Recommendations: {len(recos)}")
                print(f"  - LLM Provider: {data['llm_provider_used']}")
                print(f"  - Fallback Applied: {data['fallback_applied']}")
                print(f"  - Filter Strategy: {data['filter_strategy']}")
                return True
            else:
                print(f"API request failed with {response.status_code}: {response.text}")
                return False
                
    except httpx.ConnectError:
        print("Contract Test Skipped: Backend not running. Start with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return None
    except Exception as e:
        print(f"Contract Test Failed: {e}")
        return False


async def test_exception_sanitization():
    """Test that exceptions are sanitized and don't leak stack traces"""
    print("\nRunning Phase 6 Exception Sanitization Test (Standalone)...")
    
    base_url = "http://localhost:8000"
    
    # Test with invalid payload
    bad_payload = {"location": 123}  # Invalid type
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{base_url}/recommend", json=bad_payload)
            data = response.json()
            
            if "detail" in data:
                # Ensure no stack trace in output
                response_str = str(data)
                if "Traceback" in response_str or "File \"" in response_str:
                    print("Exception Sanitization Failed: Stack trace detected in response")
                    return False
                print("Exception Sanitization Passed: Stack traces are not leaked.")
                return True
            else:
                print("Exception Sanitization Failed: No detail field in error response")
                return False
                
    except httpx.ConnectError:
        print("Exception Sanitization Test Skipped: Backend not running.")
        return None
    except Exception as e:
        print(f"Exception Sanitization Test Failed: {e}")
        return False


async def test_health_endpoint():
    """Test health endpoint"""
    print("\nRunning Health Endpoint Test...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "ok":
                    print("Health Endpoint Test Passed.")
                    return True
                else:
                    print("Health Endpoint Test Failed: Unexpected response")
                    return False
            else:
                print(f"Health Endpoint Test Failed: {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("Health Endpoint Test Skipped: Backend not running.")
        return None
    except Exception as e:
        print(f"Health Endpoint Test Failed: {e}")
        return False


async def main():
    print("=" * 60)
    print("Phase 6 API and Output Layer Validation (Standalone)")
    print("=" * 60)
    
    results = {
        "health": await test_health_endpoint(),
        "contract": await test_api_contract(),
        "exception": await test_exception_sanitization()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "PASSED"
        else:
            status = "FAILED"
        print(f"{test_name.capitalize()}: {status}")
    
    # Return success if all non-skipped tests passed
    passed = all(r for r in results.values() if r is not None)
    return 0 if passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
