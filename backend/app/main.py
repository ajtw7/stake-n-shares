from contextlib import asynccontextmanager
import os
import socket
from urllib.parse import urlparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.app.api.v1.compare import router as compare_router
from backend.app.api.v1.nfl_events import router as nfl_events_router
from .db.init_db import init_db

load_dotenv()  # Loads variables from .env

def validate_env(required: list[str]) -> None:
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # quick DB host:port reachability check for postgres-like DATABASE_URL
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and db_url.startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
        parsed = urlparse(db_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        try:
            sock = socket.create_connection((host, port), timeout=2)
            sock.close()
        except Exception as e:
            raise RuntimeError(f"Cannot reach database at {host}:{port} — {e}")

# Now you can access keys like:
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: validate env and fail fast if something is wrong
    validate_env(["ALPACA_API_KEY", "ALPACA_API_SECRET", "ALPACA_BASE_URL", "DATABASE_URL"])
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
