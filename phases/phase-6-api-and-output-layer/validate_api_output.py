import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.main import app

client = TestClient(app)

def run_tests():
    print("Running Phase 6 API Contract and Exception Tests...")
    
    # 1. Test Response Schema
    payload = {
        "location": "New York",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "top_n": 3
    }
    
    response = client.post("/recommend", json=payload)
    if response.status_code == 200:
        data = response.json()
        assert "recommendations" in data
        assert "llm_provider_used" in data
        assert "fallback_applied" in data
        assert "filter_strategy" in data
        
        recos = data["recommendations"]
        if len(recos) > 0:
            for reco in recos:
                assert "restaurant_name" in reco
                assert "cuisine" in reco
                assert "rating" in reco
                assert "estimated_cost" in reco
                assert "explanation" in reco
        print("Contract Test Passed: Response schema contains all required fields.")
    else:
        print(f"API request failed with {response.status_code}: {response.text}")

    # 2. Test Exception Sanitization
    bad_payload = {"location": 123} # Invalid type
    response = client.post("/recommend", json=bad_payload)
    data = response.json()
    assert "detail" in data
    # Ensure no stack trace in output
    assert "Traceback" not in str(data)
    print("Exception Sanitization Passed: Stack traces are not leaked.")

if __name__ == "__main__":
    run_tests()
