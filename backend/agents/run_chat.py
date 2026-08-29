# run_chat.py
# Simple CLI to test the AutoGen food recommendation team.
#
# How to run (from the backend folder):
#   .\.venv\Scripts\Activate.ps1
#   python -m agents.run_chat
#
# CONTEXT / HOW MEMORY WORKS (beginner explanation):
#   1. We create the team ONCE.
#   2. Every new user message is sent with team.run_stream(task=...).
#   3. Because we reuse the SAME team object, AutoGen keeps the chat history.
#   4. So if you later say "make it vegetarian", PreferenceParser still knows
#      you previously asked for spicy + high protein.
#
#   If we created a brand-new team every time, context would be forgotten.
#
# Human-in-the-loop:
#   After Recommender speaks, HumanReviewer pauses for your keyboard input.
#   Type APPROVE to finish, or type a change request to continue.

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make sure "backend/" is on the Python path when running this file.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from autogen_agentchat.ui import Console

from agents.team_factory import TeamFactory


async def main() -> None:
    print("=" * 60)
    print("Food Recommendation Agents (AutoGen)")
    print("Agents: PreferenceParser → FoodSearcher → Recommender → HumanReviewer")
    print("Type APPROVE when you like a recommendation.")
    print("Type exit to quit.")
    print("=" * 60)

    # IMPORTANT FOR CONTEXT:
    # Create the team once. Reuse it for every message below.
    team, model_client = TeamFactory.create("food_recommendation")

    try:
        first_message = input(
            "\nWhat would you like to eat?\n"
            "(example: spicy, at least 30g protein, under 500 calories)\n> "
        ).strip()

        if not first_message or first_message.lower() == "exit":
            print("Bye.")
            return

        # First run: start with the user's food request
        await Console(team.run_stream(task=first_message))

        # Later runs: keep using the SAME team so history is remembered.
        # HumanReviewer already collects feedback during the round-robin.
        # This outer loop is only needed if the team stopped (APPROVE / max_turns)
        # and the user wants to start another request in the same session.
        while True:
            next_message = input(
                "\nContinue this chat (agents still remember context),\n"
                "or type a new request. Type exit to quit.\n> "
            ).strip()

            if not next_message or next_message.lower() == "exit":
                print("Bye.")
                break

            # Passing the next message into the SAME team preserves context.
            await Console(team.run_stream(task=next_message))

    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
