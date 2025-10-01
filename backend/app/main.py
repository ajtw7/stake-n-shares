from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.app.api.v1.compare import router as compare_router
from backend.app.api.v1.nfl_events import router as nfl_events_router
from .db.init_db import init_db

load_dotenv()  # Loads variables from .env

# Now you can access keys like:
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    yield
    # Shutdown (optional cleanup)

app = FastAPI(title="Stake N' Shares — MDM", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compare_router, prefix="/api/v1")
app.include_router(nfl_events_router, prefix="/api/v1")
