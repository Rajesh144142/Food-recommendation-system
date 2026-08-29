# main.py
# Minimal FastAPI app entry point.
# No LLM setup here. The search_foods tool lives in app/ai/tools/food_tools.py

from fastapi import FastAPI

app = FastAPI(
    title="Food Recommendation System",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"status": "ok"}
