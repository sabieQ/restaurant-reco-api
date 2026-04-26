from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


BudgetLevel = Literal["low", "medium", "high"]


class RecommendationRequest(BaseModel):
    location: str = Field(..., min_length=1, description="City or area")
    budget: BudgetLevel
    cuisine: str = Field(..., min_length=1, description="Preferred cuisine")
    min_rating: float = Field(..., ge=0.0, le=5.0)
    additional_preferences: Optional[str] = None
    top_n: int = Field(default=5, ge=3, le=5)

    @field_validator("location", "cuisine")
    @classmethod
    def normalize_strings(cls, value: str) -> str:
        return value.strip()


class CandidateRestaurant(BaseModel):
    restaurant_name: str
    location: str
    cuisine: str
    average_cost_for_two: float
    rating: float
    metadata: dict = Field(default_factory=dict)


class RecommendationItem(BaseModel):
    restaurant_name: str
    cuisine: str
    rating: float
    estimated_cost: float
    explanation: str


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
    llm_provider_used: str
    fallback_applied: bool
    filter_strategy: str
