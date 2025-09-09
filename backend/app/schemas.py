from pydantic import BaseModel, Field
from typing import Literal

class Bet(BaseModel):
    league: str = Field(..., json_schema_extra={"example": "NFL"})
    event_id: str = Field(..., json_schema_extra={"example": "2025-09-14-NE-GB"})
    stake: float = Field(..., json_schema_extra={"example": 100.0})
    odds: float = Field(..., json_schema_extra={"example": 2.5})
    outcome: Literal["win", "lose"] = Field(..., json_schema_extra={"example": "win"})

class CompareRequest(BaseModel):
    starting_capital: float = Field(1000.0, json_schema_extra={"example": 1000.0})
    equity_symbol: str = Field("SPY", json_schema_extra={"example": "SPY"})
    equity_weight: float = Field(0.8, ge=0.0, le=1.0, json_schema_extra={"example": 0.8})
    equity_return_pct: float = Field(0.05, json_schema_extra={"example": 0.05})
    bet: Bet