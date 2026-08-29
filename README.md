# Food Recommendation System

Beginner-friendly Python backend that shows how an LLM uses a **tool** to read food data — without connecting to the database itself.

## What this project includes

1. **Database layer** — SQLAlchemy + SQLite (default)
2. **`search_foods` tool** — Tool → Service → Repository → DB
3. **AutoGen agents** (RoundRobin, no supervisor):
   - PreferenceParser → FoodSearcher → Recommender → HumanReviewer
4. **HTML + WebSocket UI** — watch agent chat live
5. **Factories** — reusable builders for rate limiters, model clients, and teams
6. **Rate limiter module** — ready to use; **not wired into the chat yet**

---

## What you need

- Python 3.12+
- A [Google AI Studio](https://aistudio.google.com/apikey) Gemini API key
- No PostgreSQL required for local use

---

## Quick start (Windows PowerShell)

### 1. Open the backend folder

```powershell
cd backend
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install packages

```powershell
pip install -r requirements.txt
```

### 4. Create `.env`

```powershell
copy .env.example .env
```

Edit `.env`:

```text
DATABASE_URL=sqlite:///./food_recommendation.db
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.6-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

Optional key check:

```powershell
python test_gemini_key.py
```

### 5. Create tables + sample foods

```powershell
alembic upgrade head
python seed_sample_data.py
```

Sample menu tables: [FOOD_CATALOGUE.md](FOOD_CATALOGUE.md)

### 6. (Optional) Test the tool only (no agents)

```powershell
python test_search_foods.py
```

Flow: `search_foods` → FoodService → FoodRepository → SQLite → JSON

### 7. Run the chat UI

```powershell
uvicorn agents.web_server:app --host 127.0.0.1 --port 8001
```

Open: [http://127.0.0.1:8001](http://127.0.0.1:8001)

If port 8001 is busy, use `--port 8002`.

### How to use the page

1. Ask for food, e.g. `spicy, at least 30g protein, under 500 calories`
2. Watch agents:
   - **PreferenceParser** — builds filters
   - **FoodSearcher** — calls `search_foods`
   - **Recommender** — explains options
   - **HumanReviewer** — your turn
3. Reply with `APPROVE`, or a change like `make it vegetarian`
4. Truly off-topic asks (weather, coding, etc.) should be refused

### Alternative: CLI (no browser)

```powershell
python -m agents.run_chat
```

---

## Agents (important)

| Agent | Role | Uses DB tool? |
|-------|------|----------------|
| PreferenceParser | Turns user text into filters | No |
| FoodSearcher | Calls `search_foods_tool` | **Yes** |
| Recommender | Writes food recommendations | No |
| HumanReviewer | You approve / change | No |

Order is fixed (**RoundRobin**). There is **no supervisor agent**.

---

## Architecture

```text
User (browser / CLI)
  → AutoGen agents (RoundRobin)
  → FoodSearcher calls search_foods tool
  → FoodService
  → FoodRepository
  → SQLAlchemy
  → SQLite (food_recommendation.db)
  → JSON back to the agent / UI
```

The LLM never connects to the database. It only calls the tool.

---

## Factory pattern (project convention)

Use factories for swapable pieces:

| Factory | Purpose | Example types |
|---------|---------|----------------|
| `RateLimiterFactory` | Limit how often an action runs | `fixed_window`, `token_bucket` |
| `ModelClientFactory` | Build LLM clients | `gemini` |
| `TeamFactory` | Build agent teams | `food_recommendation` |

```python
from app.rate_limiting import RateLimiterFactory
from agents.model_client_factory import ModelClientFactory
from agents.team_factory import TeamFactory

limiter = RateLimiterFactory.create("fixed_window", max_requests=5, window_seconds=60)
client = ModelClientFactory.create("gemini")
team, client = TeamFactory.create("food_recommendation")
```

**Note:** The rate limiter is a separate module. It is **not** plugged into the chat UI yet. You can attach it wherever you want (chat starts, tool calls, Gemini calls, etc.).

---

## Project layout

```text
backend/
├── app/
│   ├── database/           # SQLAlchemy engine + session
│   ├── models/             # tables
│   ├── schemas/            # Pydantic input/output shapes
│   ├── repositories/       # DB queries
│   ├── services/           # business logic
│   ├── ai/tools/           # search_foods tool
│   └── rate_limiting/      # RateLimiterFactory + limiters
├── agents/
│   ├── agents.py           # PreferenceParser, FoodSearcher, Recommender, HumanReviewer
│   ├── team.py             # RoundRobin team wiring
│   ├── team_factory.py     # TeamFactory
│   ├── model_client_factory.py
│   ├── tool_adapter.py     # AutoGen → search_foods
│   ├── web_server.py       # WebSocket + HTML UI
│   ├── run_chat.py         # CLI chat
│   └── static/chat.html
├── alembic/
├── seed_sample_data.py
├── test_search_foods.py
├── test_gemini_key.py
├── requirements.txt
└── .env.example
```

---

## Optional: PostgreSQL later

1. Create DB `food_recommendation`
2. `pip install psycopg2-binary`
3. In `.env`:

```text
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/food_recommendation
```

4. Run:

```powershell
alembic upgrade head
python seed_sample_data.py
```

SQLAlchemy code stays the same; only the URL changes.

---

## Troubleshooting

| Problem | Fix |
|--------|-----|
| `GEMINI_API_KEY is missing` | Put your key in `backend/.env` |
| Empty food results | Run `python seed_sample_data.py` |
| WebSocket errors | Ensure `uvicorn[standard]` / `websockets` installed |
| Port busy | Use another port, e.g. `--port 8002` |
| Tables missing | Run `alembic upgrade head` from `backend/` |
| Model 404 / old Gemini name | Set `GEMINI_MODEL=gemini-3.6-flash` |
| Thought signature / tool 400 | FoodSearcher uses `reflect_on_tool_use=False` (already set) |
| Go to Definition not working | Select interpreter `backend/.venv` (see `.vscode/settings.json`) |
