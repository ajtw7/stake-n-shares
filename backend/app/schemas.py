from pydantic import BaseModel
from typing import Literal

class Bet(BaseModel):
    league: str
    event_id: str
    stake: float
    odds: float | None = None   # <-- CHANGED: allow null so we can fetch live odds
    outcome: Literal["win", "lose"]

class CompareRequest(BaseModel):
    starting_capital: float
    equity_symbol: str
    equity_weight: float
    equity_return_pct: float  # (can stay required; replaced if live)
    bet: Bet