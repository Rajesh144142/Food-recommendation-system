# test_search_foods.py
# Simple test script for the search_foods tool.
# This does NOT use OpenAI. It calls the tool function directly.
#
# How to run (from the backend folder):
#   python test_search_foods.py

import json

from app.ai.tools.food_tools import SEARCH_FOODS_TOOL_DEFINITION, search_foods
from app.database.session import SessionLocal


def main():
    print("=" * 60)
    print("1) Tool definition (what an LLM will later read)")
    print("=" * 60)
    print(json.dumps(SEARCH_FOODS_TOOL_DEFINITION, indent=2))

    print("\n" + "=" * 60)
    print("2) Calling search_foods tool directly")
    print("   Example: max_calories=500, min_protein=30, tags=['spicy']")
    print("=" * 60)

    # Open a database session
    db = SessionLocal()

    try:
        # Call the tool exactly like a future LLM tool call would
        result = search_foods(
            db=db,
            max_calories=500,
            min_protein=30,
            tags=["spicy"],
        )

        # Pretty-print the structured JSON result
        print(json.dumps(result, indent=2))

    finally:
        # Always close the database session
        db.close()


if __name__ == "__main__":
    main()
