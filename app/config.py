from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Restaurant Recommendation API"
    app_env: str = "dev"

    dataset_id: str = "ManikaSaini/zomato-restaurant-recommendation"
    dataset_split: str = "train"
    max_candidates_for_llm: int = 15

    # LLM provider keys and endpoints
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openrouter/free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"

    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1/chat/completions"

    request_timeout_seconds: float = 30.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
