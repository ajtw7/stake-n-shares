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
    Fetch daily bars (Alpaca) and compute (last_close - first_open)/first_open
    """
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
    ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
    DATA_URL = "https://data.alpaca.markets/v2/stocks"
    if not (ALPACA_API_KEY and ALPACA_API_SECRET):
        return None

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
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        bars = resp.json().get("bars", [])
        if len(bars) < 2:
            return None
        first_open = bars[0]["o"]
        last_close = bars[-1]["c"]
        return (last_close - first_open) / first_open
    except Exception:
        return None

def fetch_nfl_moneyline_odds(event_id: str, snapshot_ts: str) -> float | None:
    """
    Historical best (max) h2h moneyline decimal odds for one NFL event at a snapshot.
    Uses: /v4/historical/sports/americanfootball_nfl/events/{event_id}/odds
    snapshot_ts: ISO8601 timestamp (preferred) or YYYY-MM-DD.
    """
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        return None
    url = f"https://api.the-odds-api.com/v4/historical/sports/americanfootball_nfl/events/{event_id}/odds"
    params = {
        "apiKey": api_key,
        "date": snapshot_ts,
        "markets": "h2h",
        "regions": "us",
        "oddsFormat": "decimal"
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        if r.status_code != 200:
            return None
        payload = r.json()
        event_obj = payload.get("data")
        if not isinstance(event_obj, dict):
            return None
        best = None
        for bk in event_obj.get("bookmakers", []):
            for m in bk.get("markets", []):
                if m.get("key") == "h2h":
                    for o in m.get("outcomes", []):
                        price = o.get("price")
                        if isinstance(price, (int, float)):
                            if best is None or price > best:
                                best = float(price)
        return best
    except Exception:
        return None

# ADDED: odds_date param to allow historical odds snapshot separate from equity window
def build_compare_request_with_live_data(
    starting_capital: float,
    equity_symbol: str,
    equity_weight: float,
    bet_data: dict,
    start: str,
    end: str,
    odds_date: str | None = None  # <-- ADDED
) -> CompareRequest:
    from .schemas import CompareRequest, Bet
    from backend.app.config import settings

    # Default/fallback values (if live not enabled or fetch fails)
    equity_return_pct = bet_data.get("equity_return_pct", 0.0)
    odds = bet_data.get("odds")

    if settings.USE_EXTERNAL_APIS:
        # Live equity return
        live_ret = fetch_equity_return_pct(equity_symbol, start, end)
        if live_ret is not None:
            equity_return_pct = live_ret

        # Live / historical odds only if NFL and odds missing or zero
        if (bet_data.get("league", "").lower() == "nfl") and bet_data.get("event_id"):
            if not odds or odds <= 0:
                snapshot_date = odds_date or start  # use provided odds_date else reuse start
                live_odds = fetch_nfl_moneyline_odds(bet_data["event_id"], snapshot_date)
                if live_odds:
                    odds = live_odds

    # Final safety fallbacks
    if odds is None or odds <= 0:
        odds = 2.0

    bet = Bet(**{**bet_data, "odds": odds})
    return CompareRequest(
        starting_capital=starting_capital,
        equity_symbol=equity_symbol,
        equity_weight=equity_weight,
        equity_return_pct=equity_return_pct,
        bet=bet
    )
