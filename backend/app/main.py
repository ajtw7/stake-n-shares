from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from backend.app.api.v1.compare import router as compare_router
from backend.app.api.v1.nfl_events import router as nfl_events_router

load_dotenv()  # Loads variables from .env

# Now you can access keys like:
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

app = FastAPI(title="Stake N' Shares — MDM")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(compare_router, prefix="/api/v1")
app.include_router(nfl_events_router, prefix="/api/v1")

