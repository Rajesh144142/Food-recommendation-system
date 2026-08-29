# Food Recommendation System

Python backend with:

1. **Database layer** (SQLAlchemy + SQLite by default)
2. **`search_foods` tool** (LLM does not talk to the DB directly)
3. **AutoGen agents** (PreferenceParser → FoodSearcher → Recommender → HumanReviewer)
4. **Simple HTML + WebSocket page** to watch agent chat

---

## What you need

- Python 3.12+
- A [Google AI Studio](https://aistudio.google.com/apikey) Gemini API key
- No PostgreSQL install required (we use a local SQLite file via SQLAlchemy)

---

## 1. Go to the backend folder

```powershell
cd D:\Plumfin\food-recommendation-system\backend
```

## 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install packages

```powershell
pip install -r requirements.txt
```

## 4. Create your `.env` file

```powershell
copy .env.example .env
```

Edit `.env` and set your Gemini key:

```text
DATABASE_URL=sqlite:///./food_recommendation.db
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.6-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

`DATABASE_URL` points to a SQLite file. SQLAlchemy creates/uses `food_recommendation.db` in the `backend` folder.

Agents use your **Gemini API key** through Google’s OpenAI-compatible chat endpoint (so AutoGen tool calling works). The LLM still never talks to the database — only `search_foods` does.

Optional key check:

```powershell
python test_gemini_key.py
```

## 5. Create database tables

```powershell
alembic upgrade head
```

## 6. Insert sample foods

```powershell
python seed_sample_data.py
```

See the full sample menu tables in [FOOD_CATALOGUE.md](FOOD_CATALOGUE.md).

## 7. (Optional) Test the tool without AutoGen

```powershell
python test_search_foods.py
```

This calls:

`search_foods` → FoodService → FoodRepository → SQLite → JSON

---

## 8. Run the agent chat web page

```powershell
uvicorn agents.web_server:app --host 127.0.0.1 --port 8001
```

Open in your browser:

[http://127.0.0.1:8001](http://127.0.0.1:8001)

### How to use the page

1. Type a food request, for example:  
   `spicy, at least 30g protein, under 500 calories`
2. Watch the agents talk:
   - PreferenceParser
   - FoodSearcher (calls `search_foods`)
   - Recommender
   - HumanReviewer (your turn)
3. When asked, reply with:
   - `APPROVE` to finish
   - or a change like `make it vegetarian`
4. Off-topic questions are refused (food recommendations only)

---

## Alternative: CLI chat (no browser)

```powershell
python -m agents.run_chat
```

---

## Project layout (simple)

```text
backend/
├── app/
│   ├── database/          # SQLAlchemy engine + session
│   ├── models/            # tables
│   ├── schemas/           # Pydantic shapes
│   ├── repositories/      # DB queries
│   ├── services/          # business logic
│   └── ai/tools/          # search_foods tool
├── agents/
│   ├── agents.py          # AutoGen agents
│   ├── team.py            # RoundRobin team
│   ├── tool_adapter.py    # wraps search_foods for AutoGen
│   ├── web_server.py      # HTML + WebSocket UI
│   └── static/chat.html   # the page you open
├── alembic/               # table migrations
├── seed_sample_data.py
├── test_search_foods.py
├── requirements.txt
└── .env.example
```

---

## Architecture (important idea)

```text
User (browser / CLI)
  → AutoGen agents
  → FoodSearcher calls search_foods tool
  → FoodService
  → FoodRepository
  → SQLAlchemy
  → SQLite file (food_recommendation.db)
  → JSON result back to the agent
```

The LLM never connects to the database. It only calls the tool.

### Factory pattern (project convention)

Swapable pieces are created through factories so you can reuse them anywhere:

| Factory | Example |
|---------|---------|
| `RateLimiterFactory` | `RateLimiterFactory.create("fixed_window", max_requests=5, window_seconds=60)` |
| `ModelClientFactory` | `ModelClientFactory.create("gemini")` |
| `TeamFactory` | `TeamFactory.create("food_recommendation")` |

```python
from app.rate_limiting import RateLimiterFactory
from agents.team_factory import TeamFactory

limiter = RateLimiterFactory.create("token_bucket", capacity=10, refill_rate_per_second=1)
team, client = TeamFactory.create("food_recommendation")
```

---

## Optional: use PostgreSQL later

If you want PostgreSQL instead of SQLite:

1. Install PostgreSQL and create a database named `food_recommendation`
2. `pip install psycopg2-binary`
3. In `.env`:

```text
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/food_recommendation
```

4. Run again:

```powershell
alembic upgrade head
python seed_sample_data.py
```

SQLAlchemy code stays the same; only the URL changes.

---

## Quick troubleshooting

| Problem | Fix |
|--------|-----|
| `GEMINI_API_KEY is missing` | Put your Google AI Studio key in `backend/.env` |
| Empty food results | Run `python seed_sample_data.py` |
| WebSocket not working | Use `uvicorn[standard]` / `websockets` (already in requirements) |
| Port 8001 busy | Try `--port 8002` |
| Tables missing | Run `alembic upgrade head` from `backend/` |
| FoodSearcher never calls the tool | Try `GEMINI_MODEL=gemini-3.6-flash` |
