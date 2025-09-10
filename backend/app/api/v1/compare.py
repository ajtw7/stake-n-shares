from fastapi import APIRouter, Query
from backend.app.schemas import CompareRequest
from backend.app.services import compute_compare, build_compare_request_with_live_data
from backend.app.config import settings

router = APIRouter()

@router.post("/compare")
def compare_endpoint(
    req: CompareRequest,
    start: str = Query(None, description="Equity return start date (YYYY-MM-DD)"),
    end: str = Query(None, description="Equity return end date (YYYY-MM-DD)"),
    odds_date: str = Query(None, description="Historical odds snapshot date (YYYY-MM-DD)")  # <-- ADDED
):
    """
    If USE_EXTERNAL_APIS=true and start/end provided:
      - Replace equity_return_pct with live Alpaca-derived return
      - If NFL + odds missing (or <=0) and odds_date provided (or fallback to start), fetch historical moneyline odds
    """
    if settings.USE_EXTERNAL_APIS and start and end:
        req = build_compare_request_with_live_data(
            starting_capital=req.starting_capital,
            equity_symbol=req.equity_symbol,
            equity_weight=req.equity_weight,
            bet_data=req.bet.dict(),
            start=start,
            end=end,
            odds_date=odds_date  # <-- ADDED
        )
    return compute_compare(req)