from __future__ import annotations

import json
from typing import Any

import httpx

from .config import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def rank_with_fallback(self, prompt: str) -> tuple[dict[str, Any], str]:
        # OpenRouter is primary (free-first).
        if self.settings.openrouter_api_key:
            payload = {
                "model": self.settings.openrouter_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            headers = {
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
            }
            try:
                data = await self._post_json(self.settings.openrouter_base_url, headers, payload)
                parsed = self._extract_json_output(data)
                return parsed, "openrouter"
            except Exception:
                # Continue to fallback provider.
                pass

        if self.settings.groq_api_key:
            payload = {
                "model": self.settings.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            headers = {
                "Authorization": f"Bearer {self.settings.groq_api_key}",
                "Content-Type": "application/json",
            }
            data = await self._post_json(self.settings.groq_base_url, headers, payload)
            parsed = self._extract_json_output(data)
            return parsed, "groq"

        raise RuntimeError("No LLM API key configured. Set OPENROUTER_API_KEY or GROQ_API_KEY.")

    async def _post_json(self, url: str, headers: dict, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    def _extract_json_output(self, response: dict) -> dict:
        try:
            raw = response["choices"][0]["message"]["content"]
            return json.loads(raw)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Unable to parse LLM JSON output: {exc}") from exc
