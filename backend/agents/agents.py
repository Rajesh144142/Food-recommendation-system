# agents.py
# Creates the 3 AI agents + 1 human proxy.
#
# Who does what:
#   PreferenceParser  → reads user text, writes search filters (also blocks off-topic)
#   FoodSearcher      → calls search_foods_tool (ONLY agent with the tool)
#   Recommender       → explains food picks to the human
#   HumanReviewer     → real human (UserProxy). AutoGen pauses here for input.

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.config import (
    get_gemini_api_key,
    get_gemini_base_url,
    get_gemini_model,
)
from agents.tool_adapter import search_foods_tool

# Shared scope rules for every AI agent.
# The system only answers food-recommendation questions.
SCOPE_RULES = """
SCOPE RULES (very important):
You ONLY help with food recommendations in this app.
IN SCOPE examples:
- what to eat / meal ideas
- calories, protein, fat, fibre, sugar, sodium
- tags like spicy, sweet, high_protein, low_calorie, quick_meal, comfort_food
- dietary types like vegetarian, vegan, non_vegetarian, gluten_free, dairy_free
- allergens to avoid
- food category, preparation time, serving size
- refining a previous food recommendation

OUT OF SCOPE examples (must refuse politely):
- weather, news, politics, sports
- coding, maths homework, general chat
- medical diagnosis or treatment advice
- anything unrelated to choosing or searching foods in this system

If the user is out of scope:
1) Say clearly that you can only help with food recommendations in this app.
2) Give 1 short example of a valid request.
3) Do NOT invent foods.
4) Do NOT call tools.
5) End with the marker: OUT_OF_SCOPE
"""


def create_model_client() -> OpenAIChatCompletionClient:
    """
    One shared Gemini client for all AI agents.

    Why OpenAIChatCompletionClient?
      AutoGen needs chat + tool calling.
      Google exposes an OpenAI-compatible URL for Gemini.
      We use your GEMINI_API_KEY against that URL.

    (The simple google.genai interactions.create demo is great for
     one-shot text, but AutoGen agents need this chat/tools path.)
    """
    return OpenAIChatCompletionClient(
        model=get_gemini_model(),
        api_key=get_gemini_api_key(),
        base_url=get_gemini_base_url(),
        model_info={
            "vision": False,
            "function_calling": True,  # FoodSearcher needs tools
            "json_output": True,
            "family": "gemini",
            "structured_output": False,
        },
    )


def create_preference_parser(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Agent 1: turn the user's words into clear search filters.
    Also acts as the first gatekeeper for off-topic questions.
    This agent does NOT call the database.
    """
    return AssistantAgent(
        name="PreferenceParser",
        model_client=model_client,
        system_message=(
            "You are PreferenceParser for a food recommendation system.\n"
            f"{SCOPE_RULES}\n"
            "If the request IS in scope:\n"
            "Read the user's request (and any later feedback) and extract search filters.\n"
            "Output a short structured list using only these fields when relevant:\n"
            "- query\n"
            "- food_category\n"
            "- max_calories / min_calories\n"
            "- min_protein / max_protein\n"
            "- tags (e.g. spicy, high_protein, quick_meal)\n"
            "- dietary_types (e.g. vegetarian, vegan, non_vegetarian)\n"
            "- excluded_allergens (e.g. peanuts, milk, gluten)\n"
            "- limit (default 10)\n\n"
            "Do NOT invent food items.\n"
            "Do NOT call any tools.\n"
            "Remember previous messages in this chat when the user changes their mind.\n"
            "After writing the filters, stop and let FoodSearcher go next.\n"
            "If out of scope, write OUT_OF_SCOPE and stop."
        ),
    )


def create_food_searcher(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Agent 2: the ONLY agent that can call search_foods_tool.

    reflect_on_tool_use must be False for Gemini 3.x:
      Gemini requires a thought_signature on tool turns.
      AutoGen's OpenAI-compatible client drops that field when it
      makes a second "reflect on tool result" LLM call, which causes HTTP 400.
      With reflect_on_tool_use=False, we execute the tool and pass the JSON
      result into the group chat for Recommender (no second Gemini call).
    """
    return AssistantAgent(
        name="FoodSearcher",
        model_client=model_client,
        tools=[search_foods_tool],
        reflect_on_tool_use=False,
        system_message=(
            "You are FoodSearcher.\n"
            f"{SCOPE_RULES}\n"
            "If PreferenceParser marked the request as OUT_OF_SCOPE:\n"
            "- Do NOT call search_foods_tool.\n"
            "- Briefly say the request is outside food recommendation scope.\n"
            "- Then stop and let Recommender go next.\n\n"
            "If the request is in scope:\n"
            "You MUST call the search_foods_tool using the filters from PreferenceParser.\n"
            "Do not invent foods. Only use the tool result.\n"
            "After the tool runs, stop and let Recommender go next."
        ),
    )


def create_recommender(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Agent 3: write a friendly recommendation for the human to review.
    """
    return AssistantAgent(
        name="Recommender",
        model_client=model_client,
        system_message=(
            "You are Recommender.\n"
            f"{SCOPE_RULES}\n"
            "If the request was OUT_OF_SCOPE:\n"
            "- Politely remind the user you only recommend foods in this app.\n"
            "- Ask them to describe a meal preference.\n"
            "- Do NOT answer the off-topic question.\n"
            "- Ask them to type a food-related request, or exit.\n\n"
            "If the request is in scope:\n"
            "Using ONLY the foods returned by FoodSearcher / search_foods_tool,\n"
            "recommend 1 to 3 options.\n"
            "Read the tool JSON carefully (names, calories, protein, tags).\n"
            "Explain briefly why each option fits the user's request.\n"
            "Do not invent foods that were not in the search result.\n"
            "If no foods were found, say so and suggest how the user can relax filters.\n\n"
            "End your message by asking the human to reply with:\n"
            "- APPROVE  (if they like the recommendation)\n"
            "- or a change request (example: make it vegetarian, under 400 calories)\n"
            "- or a new in-scope food request\n"
            "- or exit"
        ),
    )


def _human_input(prompt: str) -> str:
    """
    Read keyboard input from the human.
    If they type 'approve' (any case), normalise it to APPROVE
    so the termination condition can detect it.
    """
    text = input(
        "\nYour turn (type APPROVE, a food-related change, or exit):\n> "
    ).strip()
    if text.lower() == "approve":
        return "APPROVE"
    return text


def create_human_reviewer(input_func=None) -> UserProxyAgent:
    """
    Human-in-the-loop agent.
    When it is this agent's turn, AutoGen pauses and waits for input.

    input_func:
        - CLI uses keyboard input by default
        - WebSocket page can pass a queue-based function instead
    """
    return UserProxyAgent(
        name="HumanReviewer",
        description=(
            "The real human user. Reviews recommendations and types APPROVE "
            "or a change request related to food preferences."
        ),
        input_func=input_func or _human_input,
    )
