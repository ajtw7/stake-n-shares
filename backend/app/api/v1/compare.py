from __future__ import annotations

from datetime import datetime, date
import logging
from typing import Any

from fastapi import APIRouter, Query, Body, HTTPException

from backend.app.schemas import CompareRequestInput, Bet, HistoryOut
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
            # allow full ISO; normalize Z to +00:00
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=422, detail=f"Invalid {label} timestamp")
    return value


def _try_history_imports():
    try:
        # Import only when needed; surface exact error if something is missing
        from backend.app.db.session import SessionLocal
        from backend.app.crud import history as history_crud
        return SessionLocal, history_crud
    except Exception as e:
        raise RuntimeError(str(e))


def _save_history(payload_dict: dict, result_dict: dict, params_dict: dict) -> None:
    try:
        SessionLocal, history_crud = _try_history_imports()
    except RuntimeError as e:
        logger.warning("history disabled (import error): %s", e)
        return
    try:
        db = SessionLocal()
        try:
            history_crud.create_history(db, payload=payload_dict, result=result_dict, params=params_dict)
        finally:
            db.close()
    except Exception as e:
        logger.warning("history save failed: %s", e)


@router.post("/compare")
def compare_handler(
    start: str = Query(..., description="Equity start date YYYY-MM-DD"),
    end: str = Query(..., description="Equity end date YYYY-MM-DD"),
    odds_date: str | None = Query(None, description="Historical odds snapshot ISO timestamp or YYYY-MM-DD"),
    payload: CompareRequestInput = Body(...)
):
    # validate dates
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
            odds_date=snapshot,
        )
        result = execute_compare(req)

        # add odds metadata
        result["odds_meta"] = {
            "snapshot_timestamp": snapshot,
            "resolved_odds": req.bet.odds,
            "fallback_used": getattr(req.bet, "_fallback", False),
        }

        # persist history if possible
        params_dict = {"start": start, "end": end, **({"odds_date": snapshot} if snapshot else {})}
        payload_dict = {
            "starting_capital": payload.starting_capital,
            "equity_symbol": payload.equity_symbol,
            "equity_weight": payload.equity_weight,
            "bet": bet_obj.model_dump(),
        }
        _save_history(payload_dict, result, params_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("compare_processing_error")
        raise HTTPException(status_code=502, detail=f"Processing error: {e}")


@router.get("/compare/history", response_model=list[HistoryOut])
def get_compare_history(limit: int = 50, offset: int = 0):
    try:
        SessionLocal, history_crud = _try_history_imports()
    except RuntimeError as e:
        raise HTTPException(status_code=501, detail=f"History not configured: {e}")
    db = SessionLocal()
    try:
        return history_crud.list_history(db, limit=limit, offset=offset)
    finally:
        db.close()