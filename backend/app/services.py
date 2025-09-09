import os
import requests
from .schemas import CompareRequest

def compute_compare(req: CompareRequest):
    start = req.starting_capital
    equity_cap = start * req.equity_weight
    bet_cap = start * (1 - req.equity_weight)

    equity_pnl = equity_cap * req.equity_return_pct
    bet_pnl = req.bet.stake * (req.bet.odds - 1) if req.bet.outcome == "win" else -req.bet.stake

    final_equity = equity_cap + equity_pnl
    final_bet = bet_cap + bet_pnl
    combined = final_equity + final_bet
    roi_pct = (combined - start) / start * 100.0

    return {
        "starting_capital": start,
        "equity": {"symbol": req.equity_symbol, "allocated": round(equity_cap,2), "pnl": round(equity_pnl,2), "final": round(final_equity,2)},
        "bet": {"event": f"{req.bet.league}:{req.bet.event_id}", "allocated": round(bet_cap,2), "pnl": round(bet_pnl,2), "final": round(final_bet,2)},
        "combined_final": round(combined,2),
        "roi_pct": round(roi_pct,2)
    }

def fetch_equity_return_pct(symbol: str, start: str, end: str) -> float | None:
    """
    Fetches daily bars for the symbol from Alpaca and computes return_pct:
    (last_close - first_open) / first_open
    Args:
        symbol: e.g. "SPY"
        start: ISO8601 date string, e.g. "2024-09-01"
        end: ISO8601 date string, e.g. "2024-09-08"
    Returns:
        return_pct as float (e.g. 0.05 for +5%), or None if not enough data
    """
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
    ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
    BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    DATA_URL = "https://data.alpaca.markets/v2/stocks"

    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_API_SECRET,
    }
    params = {
        "start": start,
        "end": end,
        "timeframe": "1Day",
        "limit": 100,
    }
    url = f"{DATA_URL}/{symbol}/bars"
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    bars = resp.json().get("bars", [])
    if len(bars) < 2:
        return None
    first_open = bars[0]["o"]
    last_close = bars[-1]["c"]
    return (last_close - first_open) / first_open

def build_compare_request_with_live_data(
    starting_capital: float,
    equity_symbol: str,
    equity_weight: float,
    bet_data: dict,
    start: str,
    end: str
) -> CompareRequest:
    """
    Returns a CompareRequest, using live equity_return_pct if USE_EXTERNAL_APIS is true.
    """
    USE_EXTERNAL_APIS = os.getenv("USE_EXTERNAL_APIS", "false").lower() in ("1", "true", "yes")
    if USE_EXTERNAL_APIS:
        equity_return_pct = fetch_equity_return_pct(equity_symbol, start, end)
        if equity_return_pct is None:
            raise ValueError("Could not fetch live return_pct for symbol/date range.")
    else:
        equity_return_pct = bet_data.get("equity_return_pct", 0.05)  # fallback

    from .schemas import CompareRequest, Bet
    bet = Bet(**bet_data)
    return CompareRequest(
        starting_capital=starting_capital,
        equity_symbol=equity_symbol,
        equity_weight=equity_weight,
        equity_return_pct=equity_return_pct,
        bet=bet
    )