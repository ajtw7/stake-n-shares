from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
import re

HEX32_RE = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)


class Bet(BaseModel):
    league: str = Field(..., description="League code, e.g. NFL")
    event_id: str = Field(..., description="Event identifier (32-char hex)")
    stake: float = Field(..., gt=0, description="Stake amount (>0)")
    odds: float | None = Field(
        None,
        gt=1,
        description="Optional fixed odds (>1) to bypass fetch; if omitted system fetches historical/live"
    )
    outcome: str = Field(..., description="'win' or 'loss'")

    @field_validator("league")
    def league_supported(cls, v: str) -> str:
        if v.lower() not in {"nfl"}:
            raise ValueError("Unsupported league")
        return v.upper()

    @field_validator("event_id")
    def event_id_format(cls, v: str) -> str:
        if not HEX32_RE.match(v):
            raise ValueError("event_id must be 32-char hex")
        return v.lower()

    @field_validator("outcome")
    def outcome_valid(cls, v: str) -> str:
        if v not in {"win", "loss"}:
            raise ValueError("outcome must be 'win' or 'loss'")
        return v


class CompareRequest(BaseModel):
    starting_capital: float
    equity_symbol: str
    equity_weight: float
    equity_return_pct: float
    bet: Bet


class CompareRequestInput(BaseModel):
    """
    Input schema from API caller BEFORE enrichment (no equity_return_pct yet).
    """
    starting_capital: float = Field(..., gt=0, description="Total starting capital (>0)")
    equity_symbol: str = Field(..., min_length=1, description="Equity ticker symbol")
    equity_weight: float = Field(..., ge=0, le=1, description="Fraction of capital allocated to equity (0-1)")
    bet: Bet

    @field_validator("equity_symbol")
    def symbol_trim(cls, v: str) -> str:
        return v.strip().upper()