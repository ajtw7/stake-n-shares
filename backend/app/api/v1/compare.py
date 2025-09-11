from fastapi import APIRouter, Query, Body, HTTPException
from datetime import datetime, date
from backend.app.schemas import CompareRequestInput, Bet
from backend.app.services import build_compare_request_with_live_data, execute_compare  # <- updated import

router = APIRouter()

def _parse_day(label: str, value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=422, detail=f"Invalid {label} (expected YYYY-MM-DD)")

def _parse_snapshot(label: str, value: str) -> str:
    try:
        if len(value) == 10:  # YYYY-MM-DD
            datetime.strptime(value, "%Y-%m-%d")
        else:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=422, detail=f"Invalid {label} timestamp")
    return value

@router.post("/compare")
def compare_handler(
    start: str = Query(..., description="Equity start date YYYY-MM-DD"),
    end: str = Query(..., description="Equity end date YYYY-MM-DD"),
    odds_date: str | None = Query(None, description="Historical odds snapshot ISO timestamp or YYYY-MM-DD"),
    payload: CompareRequestInput = Body(...)
):
    # Validate date range
    start_d = _parse_day("start", start)
    end_d = _parse_day("end", end)
    if start_d > end_d:
        raise HTTPException(status_code=422, detail="start must be <= end")

    snapshot = _parse_snapshot("odds_date", odds_date) if odds_date else None
    bet_obj: Bet = payload.bet

    try:
        req = build_compare_request_with_live_data(
            starting_capital=payload.starting_capital,
            equity_symbol=payload.equity_symbol,
            equity_weight=payload.equity_weight,
            bet_data=bet_obj.model_dump(),  # replaced .dict() -> model_dump()
            start=start,
            end=end,
            odds_date=snapshot
        )
        return execute_compare(req)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Processing error: {e}")