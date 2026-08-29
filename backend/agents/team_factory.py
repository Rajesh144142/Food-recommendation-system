# team_factory.py
# Factory for AutoGen agent teams.
#
# Same factory style as RateLimiterFactory / ModelClientFactory:
#   team, client = TeamFactory.create("food_recommendation")

from __future__ import annotations

from typing import Any, Callable, Optional, Tuple

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.team import create_food_recommendation_team

FOOD_RECOMMENDATION = "food_recommendation"


class TeamFactory:
    """
    Build agent teams from a type name.

    Example:
        team, model_client = TeamFactory.create(
            "food_recommendation",
            human_input_func=my_input_func,
        )
    """

    @staticmethod
    def create(
        team_type: str = FOOD_RECOMMENDATION,
        *,
        model_client: Optional[OpenAIChatCompletionClient] = None,
        human_input_func: Optional[Callable] = None,
        **kwargs: Any,
    ) -> Tuple[RoundRobinGroupChat, OpenAIChatCompletionClient]:
        normalised = (team_type or FOOD_RECOMMENDATION).strip().lower()

        if normalised in {FOOD_RECOMMENDATION, "food", "food_agents"}:
            return create_food_recommendation_team(
                model_client=model_client,
                human_input_func=human_input_func,
            )

        raise ValueError(
            f"Unknown team type: {team_type!r}. "
            f"Supported: '{FOOD_RECOMMENDATION}'."
        )

    @staticmethod
    def available_types() -> list[str]:
        return [FOOD_RECOMMENDATION]
