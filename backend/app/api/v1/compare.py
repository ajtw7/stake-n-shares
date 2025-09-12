from fastapi import APIRouter, Query, Body, HTTPException
from datetime import datetime, date
import logging
from backend.app.schemas import CompareRequestInput, Bet
from backend.app.services import build_compare_request_with_live_data, execute_compare

router = APIRouter()
logger = logging.getLogger(__name__)

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
    logger.info("compare_request received start=%s end=%s odds_date=%s equity_symbol=%s equity_weight=%s",
                start, end, odds_date, payload.equity_symbol, payload.equity_weight)
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
            bet_data=bet_obj.model_dump(),
            start=start,
            end=end,
            odds_date=snapshot
        )
        result = execute_compare(req)

        # Enrich response with odds metadata
        result["odds_meta"] = {
            "snapshot_timestamp": snapshot,                 # None => live/no snapshot requested
            "resolved_odds": req.bet.odds,                  # odds actually used in calculation
            "fallback_used": getattr(req.bet, "_fallback", False)
        }
        logger.info("compare_response roi_pct=%s resolved_odds=%s snapshot=%s fallback=%s",
                    result["roi_pct"], result["odds_meta"]["resolved_odds"],
                    result["odds_meta"]["snapshot_timestamp"], result["odds_meta"]["fallback_used"])
        return result
    except HTTPException:
        logger.warning("compare_request failed validation")
        raise
    except Exception as e:
        logger.exception("compare_processing_error")
        raise HTTPException(status_code=502, detail=f"Processing error: {e}")