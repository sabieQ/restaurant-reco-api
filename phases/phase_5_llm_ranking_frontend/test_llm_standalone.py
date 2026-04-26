from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables from root directory
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


class StandaloneLLMClient:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.groq_base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")
        self.timeout = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

    async def rank_with_fallback(self, prompt: str) -> tuple[dict[str, Any], str]:
        # OpenRouter is primary (free-first).
        if self.openrouter_api_key:
            payload = {
                "model": self.openrouter_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
            }
            try:
                data = await self._post_json(self.openrouter_base_url, headers, payload)
                parsed = self._extract_json_output(data)
                return parsed, "openrouter"
            except Exception as e:
                print(f"OpenRouter failed: {e}")
                # Continue to fallback provider.
                pass

        if self.groq_api_key:
            payload = {
                "model": self.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json",
            }
            try:
                data = await self._post_json(self.groq_base_url, headers, payload)
                parsed = self._extract_json_output(data)
                return parsed, "groq"
            except Exception as e:
                print(f"Groq failed: {e}")

        raise RuntimeError("No LLM API key configured. Set OPENROUTER_API_KEY or GROQ_API_KEY.")

    async def _post_json(self, url: str, headers: dict, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    def _extract_json_output(self, response: dict) -> dict:
        try:
            raw = response["choices"][0]["message"]["content"]
            return json.loads(raw)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Unable to parse LLM JSON output: {exc}") from exc


async def test_llm_integration():
    print("Testing LLM Integration (Standalone)")
    print("=" * 50)
    
    print(f"\nConfiguration:")
    print(f"  OpenRouter API Key: {'Set' if os.getenv('OPENROUTER_API_KEY') else 'Not set'}")
    print(f"  Groq API Key: {'Set' if os.getenv('GROQ_API_KEY') else 'Not set'}")
    print(f"  OpenRouter Model: {os.getenv('OPENROUTER_MODEL', 'openrouter/free')}")
    print(f"  Groq Model: {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')}")
    
    llm_client = StandaloneLLMClient()
    
    # Test prompt
    test_prompt = """
You are a restaurant recommendation assistant.
User preferences:
- location: Bellandur
- budget: medium
- preferred cuisine: American
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
        print(f"\n[OK] LLM call successful!")
        print(f"  Provider used: {provider}")
        print(f"\nResponse:")
        print(json.dumps(result, indent=2))
        return True
    except Exception as e:
        print(f"\n[FAIL] LLM call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_llm_integration())
    import sys
    sys.exit(0 if success else 1)
