from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.llm_client import LLMClient


async def test_llm_integration():
    print("Testing LLM Integration")
    print("=" * 50)
    
    settings = get_settings()
    print(f"\nConfiguration:")
    print(f"  OpenRouter API Key: {'Set' if settings.openrouter_api_key else 'Not set'}")
    print(f"  Groq API Key: {'Set' if settings.groq_api_key else 'Not set'}")
    print(f"  OpenRouter Model: {settings.openrouter_model}")
    print(f"  Groq Model: {settings.groq_model}")
    
    llm_client = LLMClient(settings)
    
    # Test prompt
    test_prompt = """
You are a restaurant recommendation assistant.
User preferences:
- location: Bellandur
- budget: medium
- preferred cuisine: Italian
- minimum rating: 4.0
- additional preferences: family-friendly
- required top_n: 3

Candidate restaurants (JSON-like list):
[
  {"restaurant_name": "Chili's American Grill & Bar", "location": "Bellandur", "cuisine": "American, Tex-Mex, Burger, BBQ", "rating": 4.6, "estimated_cost": 1800},
  {"restaurant_name": "Tipsy Bull - The Bar Exchange", "location": "Bellandur", "cuisine": "North Indian, Chinese, Continental, Mexican", "rating": 4.4, "estimated_cost": 1400},
  {"restaurant_name": "eat.fit", "location": "Bellandur", "cuisine": "Healthy Food, North Indian, Biryani, Continental, Sandwich, Desserts", "rating": 4.5, "estimated_cost": 500}
]

Task:
1) Rank the best 3 restaurants from the candidates.
2) For each result, include:
   - restaurant_name
   - cuisine
   - rating
   - estimated_cost
   - explanation (1-2 concise lines)
3) Output ONLY valid JSON in this exact shape:
{
  "recommendations": [
    {
      "restaurant_name": "...",
      "cuisine": "...",
      "rating": 0.0,
      "estimated_cost": 0.0,
      "explanation": "..."
    }
  ]
}
""".strip()
    
    print(f"\nSending test prompt to LLM...")
    print(f"Prompt length: {len(test_prompt)} characters")
    
    try:
        result, provider = await llm_client.rank_with_fallback(test_prompt)
        print(f"\n✓ LLM call successful!")
        print(f"  Provider used: {provider}")
        print(f"\nResponse:")
        print(json.dumps(result, indent=2))
        return True
    except Exception as e:
        print(f"\n✗ LLM call failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_llm_integration())
    sys.exit(0 if success else 1)
