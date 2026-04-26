from __future__ import annotations

from .models import RecommendationRequest


def build_recommendation_prompt(req: RecommendationRequest, candidates: list[dict]) -> str:
    return f"""
You are a restaurant recommendation assistant.
Use only the provided candidate list. Do not invent restaurants or details.

User preferences:
- location: {req.location}
- budget: {req.budget}
- preferred cuisine: {req.cuisine}
- minimum rating: {req.min_rating}
- additional preferences: {req.additional_preferences or "none"}
- required top_n: {req.top_n}

Candidate restaurants (JSON-like list):
{candidates}

Task:
1) Rank the best {req.top_n} restaurants from the candidates.
2) For each result, include:
   - restaurant_name
   - cuisine
   - rating
   - estimated_cost
   - explanation (1-2 concise lines)
3) Mention trade-offs if any.
4) Output ONLY valid JSON in this exact shape:
{{
  "recommendations": [
    {{
      "restaurant_name": "...",
      "cuisine": "...",
      "rating": 0.0,
      "estimated_cost": 0.0,
      "explanation": "..."
    }}
  ]
}}
""".strip()
