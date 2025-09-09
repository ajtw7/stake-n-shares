from fastapi import APIRouter, Request, Query
from backend.app.schemas import CompareRequest
from backend.app.services import compute_compare, build_compare_request_with_live_data

router = APIRouter()

@router.post("/compare")
def compare_endpoint(
    req: CompareRequest,
    start: str = Query(None, description="Start date for equity return (YYYY-MM-DD)"),
    end: str = Query(None, description="End date for equity return (YYYY-MM-DD)")
):
    # If using live data, build the request with live return_pct
    from backend.app.config import settings
    if settings.USE_EXTERNAL_APIS and start and end:
        req = build_compare_request_with_live_data(
            starting_capital=req.starting_capital,
            equity_symbol=req.equity_symbol,
            equity_weight=req.equity_weight,
            bet_data=req.bet.dict(),
            start=start,
            end=end
        )
    return compute_compare(req)