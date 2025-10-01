from __future__ import annotations
from typing import Literal, Any, Optional
from datetime import datetime
from uuid import UUID
import re

from pydantic import BaseModel, Field, field_validator, ConfigDict

HEX32_RE = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)
SUPPORTED_LEAGUES = {"nfl"}


class Bet(BaseModel):
    league: str = Field(..., description="League code, e.g. NFL")
    event_id: str = Field(..., description="Event identifier (32-char hex)")
    stake: float = Field(..., gt=0, description="Stake amount (>0)")
    odds: float | None = Field(
        None,
        gt=1,
        description="Optional fixed odds (>1) to bypass fetch; if omitted system fetches historical/live",
    )
    outcome: Literal["win", "loss"] = Field(..., description="'win' or 'loss'")

    @field_validator("league")
    def league_supported(cls, v: str) -> str:
        if v.lower() not in SUPPORTED_LEAGUES:
            raise ValueError("Unsupported league")
        return v.upper()

    @field_validator("event_id")
    def event_id_format(cls, v: str) -> str:
        if not HEX32_RE.match(v):
            raise ValueError("event_id must be 32-char hex")
        return v.lower()


class CompareRequest(BaseModel):
    starting_capital: float
    equity_symbol: str
    equity_weight: float
    equity_return_pct: float
    bet: Bet


class CompareRequestInput(BaseModel):
    """Input schema before enrichment (no equity_return_pct)."""
    starting_capital: float = Field(..., gt=0, description="Total starting capital (>0)")
    equity_symbol: str = Field(..., min_length=1, description="Equity ticker symbol")
    equity_weight: float = Field(..., ge=0, le=1, description="Fraction of capital allocated to equity (0-1)")
    bet: Bet

    @field_validator("equity_symbol")
    def symbol_trim(cls, v: str) -> str:
        return v.strip().upper()


class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    payload: Any
    result: Any
    params: Optional[Any] = None
    notes: Optional[str] = None