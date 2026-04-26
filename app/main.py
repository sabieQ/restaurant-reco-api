from __future__ import annotations

import time
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .data_loader import load_restaurants_df
from .filter_engine import filter_candidates
from .llm_client import LLMClient
from .models import RecommendationItem, RecommendationRequest, RecommendationResponse
from .prompting import build_recommendation_prompt

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Restaurant Recommendation API", version="1.0.0")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."}
    )

settings = get_settings()
llm_client = LLMClient(settings)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env,
        "version": "1.0.0",
        "keys_configured": {
            "openrouter": bool(settings.openrouter_api_key),
            "groq": bool(settings.groq_api_key)
        }
    }


@app.get("/api/v1/meta")
def get_meta() -> dict:
    """Get metadata for form hints (e.g., sample allowed cities)"""
    return {
        "max_top_n": 5,
        "min_top_n": 3,
        "allowed_budget_levels": ["low", "medium", "high"],
        "rating_range": {"min": 0.0, "max": 5.0},
        "max_additional_preferences_length": 500
    }


@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
async def recommend_v1(req: RecommendationRequest) -> RecommendationResponse:
    start_time = time.time()
    
    # Validate request size limits
    if req.additional_preferences and len(req.additional_preferences) > 500:
        raise HTTPException(
            status_code=400,
            detail="Additional preferences exceed maximum length of 500 characters"
        )
    
    logger.info(
        f"Recommendation request",
        extra={
            "location": req.location,
            "budget": req.budget,
            "cuisine": req.cuisine,
            "min_rating": req.min_rating,
            "top_n": req.top_n
        }
    )
    
    try:
        df = load_restaurants_df()
    except Exception as exc:
        logger.error(f"Dataset load failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Dataset load failed: {exc}") from exc

    filtered, fallback_applied, strategy = filter_candidates(df, req)
    candidate_limit = settings.max_candidates_for_llm
    candidate_df = filtered.head(candidate_limit)

    logger.info(
        f"Filtering completed",
        extra={
            "total_candidates": len(filtered),
            "llm_candidates": len(candidate_df),
            "fallback_applied": fallback_applied,
            "strategy": strategy
        }
    )

    if candidate_df.empty:
        logger.warning("No candidates found after filtering")
        raise HTTPException(status_code=404, detail="No candidates found after filtering.")

    candidates = [
        {
            "restaurant_name": row["restaurant_name"],
            "location": row["location"],
            "cuisine": row["cuisine"],
            "rating": float(row["rating"]),
            "estimated_cost": float(row["average_cost_for_two"]),
        }
        for _, row in candidate_df.iterrows()
    ]

    prompt = build_recommendation_prompt(req, candidates)

    try:
        llm_data, llm_provider = await llm_client.rank_with_fallback(prompt)
        
        if not isinstance(llm_data, dict):
            raise ValueError("LLM output is not a JSON object")
            
        raw_recommendations = llm_data.get("recommendations", [])
        if not isinstance(raw_recommendations, list):
            raise ValueError("'recommendations' is not a list")

        # Hallucination guard: ensure recommended restaurants exist in candidates
        candidate_names = {c["restaurant_name"] for c in candidates}
        llm_recommendations = []
        for rec in raw_recommendations:
            if isinstance(rec, dict) and rec.get("restaurant_name") in candidate_names:
                llm_recommendations.append(rec)
                
        logger.info(
            f"LLM ranking completed",
            extra={
                "provider": llm_provider,
                "recommendations_count": len(llm_recommendations)
            }
        )
                
    except Exception as exc:
        # Deterministic fallback if LLM is unavailable or output is malformed.
        logger.warning(f"Triggering fallback due to LLM error/malformed output: {exc}")
        llm_provider = "none"
        llm_recommendations = []

    if not llm_recommendations:
        # Fallback response built from deterministic ranking.
        llm_recommendations = [
            {
                "restaurant_name": c["restaurant_name"],
                "cuisine": c["cuisine"],
                "rating": c["rating"],
                "estimated_cost": c["estimated_cost"],
                "explanation": (
                    f"Strong match for {req.location} with rating {c['rating']:.1f}; "
                    "selected by deterministic filters due to LLM unavailability."
                ),
            }
            for c in candidates[: req.top_n]
        ]

    recommendations = [
        RecommendationItem(
            restaurant_name=item["restaurant_name"],
            cuisine=item["cuisine"],
            rating=float(item["rating"]),
            estimated_cost=float(item["estimated_cost"]),
            explanation=str(item["explanation"]),
        )
        for item in llm_recommendations[: req.top_n]
    ]

    latency_ms = (time.time() - start_time) * 1000
    logger.info(
        f"Request completed",
        extra={
            "latency_ms": round(latency_ms, 2),
            "recommendations_returned": len(recommendations)
        }
    )

    return RecommendationResponse(
        recommendations=recommendations,
        llm_provider_used=llm_provider,
        fallback_applied=fallback_applied,
        filter_strategy=strategy,
    )


# Legacy endpoint for backward compatibility
@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_legacy(req: RecommendationRequest) -> RecommendationResponse:
    return await recommend_v1(req)
