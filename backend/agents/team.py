# team.py
# Builds the RoundRobin team.
#
# Speaking order (always the same):
#   PreferenceParser → FoodSearcher → Recommender → HumanReviewer → (repeat)
#
# CONTEXT / MEMORY:
#   Keep ONE team object and call run_stream() again with new user text.
#   AutoGen keeps the previous messages inside that team object,
#   so agents still remember earlier filters and recommendations.
#   Do NOT create a new team on every message if you want memory.

from __future__ import annotations

from typing import Callable, Optional, Tuple

from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.agents import (
    create_food_searcher,
    create_human_reviewer,
    create_model_client,
    create_preference_parser,
    create_recommender,
)


def create_food_recommendation_team(
    model_client: Optional[OpenAIChatCompletionClient] = None,
    human_input_func: Optional[Callable] = None,
) -> Tuple[RoundRobinGroupChat, OpenAIChatCompletionClient]:
    """
    Create the multi-agent team + model client.

    human_input_func:
        Optional custom human input (used by the WebSocket page).
        If None, the CLI keyboard input is used.

    Returns:
        (team, model_client)
    """
    if model_client is None:
        model_client = create_model_client()

    preference_parser = create_preference_parser(model_client)
    food_searcher = create_food_searcher(model_client)
    recommender = create_recommender(model_client)
    human_reviewer = create_human_reviewer(input_func=human_input_func)

    # Stop when the human types APPROVE (case-sensitive mention check;
    # we also handle "approve" in run_chat.py for friendliness).
    termination = TextMentionTermination("APPROVE")

    team = RoundRobinGroupChat(
        participants=[
            preference_parser,
            food_searcher,
            recommender,
            human_reviewer,
        ],
        termination_condition=termination,
        max_turns=12,  # safety stop so the loop cannot run forever
    )

    return team, model_client
