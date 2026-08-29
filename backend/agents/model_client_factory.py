# model_client_factory.py
# Factory for LLM model clients (same idea as RateLimiterFactory).
#
# Why?
#   - Create Gemini / other providers from one place
#   - Call sites do not hard-code OpenAIChatCompletionClient setup
#   - Easy to swap providers later

from __future__ import annotations

from typing import Any

from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.config import (
    get_gemini_api_key,
    get_gemini_base_url,
    get_gemini_model,
)

GEMINI = "gemini"


class ModelClientFactory:
    """
    Build AutoGen model clients.

    Examples:
        client = ModelClientFactory.create("gemini")

        client = ModelClientFactory.create(
            "gemini",
            model="gemini-3.6-flash",
            api_key="...",
        )
    """

    @staticmethod
    def create(provider: str = GEMINI, **kwargs: Any) -> OpenAIChatCompletionClient:
        normalised = (provider or GEMINI).strip().lower()

        if normalised in {GEMINI, "google", "google_gemini"}:
            return ModelClientFactory._create_gemini(**kwargs)

        raise ValueError(
            f"Unknown model provider: {provider!r}. "
            f"Supported: '{GEMINI}'."
        )

    @staticmethod
    def _create_gemini(**kwargs: Any) -> OpenAIChatCompletionClient:
        """
        Gemini via Google's OpenAI-compatible endpoint
        (needed for AutoGen tool calling).
        """
        return OpenAIChatCompletionClient(
            model=kwargs.get("model") or get_gemini_model(),
            api_key=kwargs.get("api_key") or get_gemini_api_key(),
            base_url=kwargs.get("base_url") or get_gemini_base_url(),
            model_info=kwargs.get(
                "model_info",
                {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "gemini",
                    "structured_output": False,
                },
            ),
        )

    @staticmethod
    def available_providers() -> list[str]:
        return [GEMINI]
