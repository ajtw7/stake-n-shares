from fastapi import FastAPI
from dotenv import load_dotenv
import os
from backend.app.api.v1.compare import router as compare_router
from backend.app.services import fetch_equity_return_pct

load_dotenv()  # Loads variables from .env

# Now you can access keys like:
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

app = FastAPI(title="Stake N' Shares — MDM")
app.include_router(compare_router, prefix="/api/v1")

# Add this to backend/app/main.py for a quick check
# @app.get("/debug/env")
# def debug_env():
#     return {"ALPACA_API_KEY": ALPACA_API_KEY is not None}

# @app.get("/debug/return_pct")
# def debug_return_pct(symbol: str = "TSLA", start: str = "2024-09-01", end: str = "2025-01-01"):
#     pct = fetch_equity_return_pct(symbol, start, end)
#     return {"symbol": symbol, "start": start, "end": end, "return_pct": pct}