# web_server.py
# Simple FastAPI + WebSocket page to watch agent communication.
#
# How it works (beginner version):
#   1) Browser opens the HTML page and connects with WebSocket.
#   2) User sends a food request.
#   3) Agents run in the background.
#   4) Each agent message is put into an asyncio.Queue.
#   5) A small loop reads the queue and sends messages to the browser.
#   6) When HumanReviewer needs input, we send input_required.
#   7) User reply goes into another queue, and the team continues.
#
# Run from the backend folder:
#   uvicorn agents.web_server:app --reload --port 8000

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Make sure backend/ is on the path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from agents.team import create_food_recommendation_team

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Food Recommendation Agents UI", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def chat_page():
    """Serve the simple HTML page."""
    return FileResponse(STATIC_DIR / "chat.html")


def _pretty_json_if_possible(text: str) -> str:
    """If text is JSON, return indented JSON. Otherwise return as-is."""
    try:
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return text


def _format_foods_summary(foods_payload: Dict[str, Any]) -> str:
    """Turn search_foods JSON into a short readable list for the UI."""
    foods = foods_payload.get("foods") or []
    if not foods:
        return "No foods found for those filters."

    lines = [f"Found {len(foods)} food(s):", ""]
    for index, food in enumerate(foods, start=1):
        nutrition = food.get("nutrition") or {}
        tags = ", ".join(food.get("tags") or []) or "—"
        lines.append(
            f"{index}. {food.get('name', 'Unknown')}\n"
            f"   {food.get('description', '')}\n"
            f"   Calories: {nutrition.get('calories', '—')} | "
            f"Protein: {nutrition.get('protein_g', '—')}g\n"
            f"   Tags: {tags}"
        )
        lines.append("")
    return "\n".join(lines).strip()


def _format_tool_calls(content: Any) -> Optional[str]:
    """Format FunctionCall list into a short readable line."""
    items = content if isinstance(content, list) else [content]
    lines = []
    for item in items:
        name = getattr(item, "name", None) or (item.get("name") if isinstance(item, dict) else None)
        arguments = getattr(item, "arguments", None)
        if arguments is None and isinstance(item, dict):
            arguments = item.get("arguments")
        if not name:
            continue
        # arguments is often a JSON string
        try:
            args_obj = json.loads(arguments) if isinstance(arguments, str) else arguments
            args_text = json.dumps(args_obj, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            args_text = str(arguments)
        lines.append(f"Calling tool: {name}\nArguments: {args_text}")
    return "\n\n".join(lines) if lines else None


def _format_tool_results(content: Any) -> Optional[str]:
    """Format FunctionExecutionResult list into a food summary when possible."""
    items = content if isinstance(content, list) else [content]
    parts = []
    for item in items:
        raw = getattr(item, "content", None)
        if raw is None and isinstance(item, dict):
            raw = item.get("content")
        if raw is None:
            continue
        if not isinstance(raw, str):
            raw = str(raw)
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict) and "foods" in payload:
                parts.append(_format_foods_summary(payload))
            else:
                parts.append(_pretty_json_if_possible(raw))
        except json.JSONDecodeError:
            parts.append(raw)
    return "\n\n".join(parts) if parts else None


def _message_to_dict(message: Any) -> Optional[Dict[str, Any]]:
    """
    Convert an AutoGen stream item into a clean UI-friendly dict.
    Hides raw FunctionCall dumps and shows readable tool / chat text.
    """
    class_name = message.__class__.__name__

    if class_name == "TaskResult":
        stop_reason = getattr(message, "stop_reason", None)
        return {
            "type": "end",
            "source": "System",
            "content": f"Team finished. Reason: {stop_reason or 'completed'}",
            "stop_reason": stop_reason,
        }

    # Skip noisy internal events
    if class_name in {"UserInputRequestedEvent", "ThoughtEvent"}:
        return None

    source = getattr(message, "source", None) or "unknown"
    content = getattr(message, "content", None)
    msg_type = getattr(message, "type", class_name)

    if content is None:
        return None

    # Tool call request → short readable text
    if class_name in {"ToolCallRequestEvent", "FunctionCall"} or (
        isinstance(content, list)
        and content
        and content[0].__class__.__name__ == "FunctionCall"
    ):
        formatted = _format_tool_calls(content)
        if not formatted:
            return None
        return {
            "type": "tool_call",
            "source": source,
            "content": formatted,
            "message_type": msg_type,
        }

    # Tool execution result → food summary
    if class_name in {"ToolCallExecutionEvent", "FunctionExecutionResult"} or (
        isinstance(content, list)
        and content
        and content[0].__class__.__name__ == "FunctionExecutionResult"
    ):
        formatted = _format_tool_results(content)
        if not formatted:
            return None
        return {
            "type": "tool_result",
            "source": source,
            "content": formatted,
            "message_type": msg_type,
        }

    # Normal text (or accidental JSON string)
    if isinstance(content, str):
        text = content.strip()
        if not text:
            return None
        # Skip ugly repr dumps that slipped through as strings
        if text.startswith("[") and "FunctionCall(" in text:
            return None
        if "call_id=" in text and "is_error=" in text:
            return None
        # If the agent pasted raw foods JSON, skip it —
        # ToolCallExecutionEvent already shows a clean food summary.
        try:
            payload = json.loads(text)
            if isinstance(payload, dict) and "foods" in payload:
                return None
        except json.JSONDecodeError:
            pass
        return {
            "type": "message",
            "source": source,
            "content": text,
            "message_type": msg_type,
        }

    # Other structured content
    try:
        text = json.dumps(content, indent=2, default=str, ensure_ascii=False)
    except TypeError:
        text = str(content)
    text = text.strip()
    if not text:
        return None
    return {
        "type": "message",
        "source": source,
        "content": text,
        "message_type": msg_type,
    }


@app.websocket("/ws/agents")
async def agents_websocket(websocket: WebSocket):
    """
    One WebSocket connection = one chat session.

    Client → server JSON:
      {"type": "start", "text": "spicy high protein under 500 calories"}
      {"type": "human_reply", "text": "APPROVE"}
      {"type": "human_reply", "text": "make it vegetarian"}

    Server → client JSON:
      {"type": "message", "source": "PreferenceParser", "content": "..."}
      {"type": "input_required", "content": "Please reply..."}
      {"type": "end", "content": "...", "stop_reason": "..."}
      {"type": "error", "content": "..."}
    """
    await websocket.accept()

    # Queue of messages going TO the browser
    output_queue: asyncio.Queue = asyncio.Queue()
    # Queue of human replies coming FROM the browser
    input_queue: asyncio.Queue = asyncio.Queue()

    team_task: Optional[asyncio.Task] = None
    model_client = None

    async def human_input_from_queue(prompt: str, cancellation_token=None) -> str:
        """
        Called when HumanReviewer needs the user.
        Put a notice in output_queue, then wait for the browser reply.
        """
        await output_queue.put(
            {
                "type": "input_required",
                "source": "HumanReviewer",
                "content": (
                    "Your turn. Type APPROVE, a food-related change, "
                    "or a new in-scope request."
                ),
            }
        )
        reply = await input_queue.get()
        reply = (reply or "").strip()
        if reply.lower() == "approve":
            return "APPROVE"
        return reply

    async def forward_queue_to_websocket():
        """Keep sending queue items to the browser until the socket closes."""
        while True:
            item = await output_queue.get()
            await websocket.send_json(item)
            if item.get("type") in {"end", "error", "session_closed"}:
                # Keep listening for more starts in the same socket,
                # so do not break on end — only on session_closed.
                if item.get("type") == "session_closed":
                    break

    async def run_team(task_text: str):
        """Run the AutoGen team and push every useful message into the queue."""
        nonlocal model_client
        try:
            team, model_client = create_food_recommendation_team(
                human_input_func=human_input_from_queue
            )
            await output_queue.put(
                {
                    "type": "status",
                    "source": "System",
                    "content": "Agents started...",
                }
            )

            async for message in team.run_stream(task=task_text):
                payload = _message_to_dict(message)
                if payload:
                    await output_queue.put(payload)
                    if payload.get("type") == "end":
                        return

            await output_queue.put(
                {
                    "type": "end",
                    "source": "System",
                    "content": "Team run complete.",
                }
            )
        except Exception as error:
            error_text = str(error)
            # Make OpenRouter rate-limit errors easier to understand
            if "429" in error_text or "rate-limited" in error_text.lower() or "RateLimitError" in type(error).__name__:
                error_text = (
                    "OpenRouter rate limit (429): the free model is temporarily busy.\n"
                    "Wait a minute and try again, or change OPENROUTER_MODEL in backend/.env "
                    "to another free model (for example meta-llama/llama-3.3-70b-instruct:free)."
                )
            await output_queue.put(
                {
                    "type": "error",
                    "source": "System",
                    "content": error_text,
                }
            )
        finally:
            if model_client is not None:
                await model_client.close()
                model_client = None

    forwarder = asyncio.create_task(forward_queue_to_websocket())

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await output_queue.put(
                    {
                        "type": "error",
                        "source": "System",
                        "content": "Invalid JSON from browser.",
                    }
                )
                continue

            msg_type = data.get("type")
            text = (data.get("text") or "").strip()

            if msg_type == "start":
                if not text:
                    await output_queue.put(
                        {
                            "type": "error",
                            "source": "System",
                            "content": "Please enter a food request first.",
                        }
                    )
                    continue

                # Show the user's message on the page too
                await output_queue.put(
                    {
                        "type": "message",
                        "source": "You",
                        "content": text,
                    }
                )

                # Start agents (one run at a time)
                if team_task and not team_task.done():
                    await output_queue.put(
                        {
                            "type": "status",
                            "source": "System",
                            "content": "A run is already in progress. Use human reply instead.",
                        }
                    )
                    continue

                team_task = asyncio.create_task(run_team(text))

            elif msg_type == "human_reply":
                if not text:
                    continue
                await output_queue.put(
                    {
                        "type": "message",
                        "source": "You",
                        "content": text,
                    }
                )
                await input_queue.put(text)

            else:
                await output_queue.put(
                    {
                        "type": "error",
                        "source": "System",
                        "content": f"Unknown message type: {msg_type}",
                    }
                )

    except WebSocketDisconnect:
        # Unblock human_input if it is waiting
        await input_queue.put("exit")
        await output_queue.put({"type": "session_closed", "source": "System", "content": "closed"})
        if team_task and not team_task.done():
            team_task.cancel()
        forwarder.cancel()
    except Exception as error:
        await output_queue.put(
            {
                "type": "error",
                "source": "System",
                "content": str(error),
            }
        )
        forwarder.cancel()
