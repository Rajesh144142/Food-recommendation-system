# config.py
# Reads settings for the AutoGen agents from the .env file.
#
# We use the Gemini API key from Google AI Studio.
# AutoGen talks to Gemini through Google's OpenAI-compatible endpoint
# so tool calling (search_foods) still works.
#
# Same API key as:
#   from google import genai
#   client = genai.Client(api_key=...)

import os

from dotenv import load_dotenv

load_dotenv()

# Google Gemini OpenAI-compatible Chat Completions endpoint
GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def get_gemini_api_key() -> str:
    """
    Return the Gemini API key from Google AI Studio.

    Set in .env:
      GEMINI_API_KEY=...
    """
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add it to backend/.env (see .env.example)."
        )
    return api_key


def get_gemini_model() -> str:
    """Gemini model id used by all agents."""
    return os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def get_gemini_base_url() -> str:
    """
    Base URL for AutoGen's OpenAI-compatible client.

    This is NOT OpenRouter. It is Google's Gemini OpenAI bridge.
    """
    return os.getenv("GEMINI_BASE_URL", GEMINI_OPENAI_BASE_URL)
