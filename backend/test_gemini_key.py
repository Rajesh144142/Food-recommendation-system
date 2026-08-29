# test_gemini_key.py
# Optional smoke test using the google.genai SDK (same key as the agents).
#
# How to run (from backend/):
#   pip install google-genai
#   python test_gemini_key.py
#
# This does NOT use AutoGen. It only checks that your GEMINI_API_KEY works.

import os

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing in .env")

    from google import genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents="Reply with one short sentence: Gemini key works.",
    )
    print("Model:", model)
    print("Reply:", getattr(response, "text", None) or response)


if __name__ == "__main__":
    main()
