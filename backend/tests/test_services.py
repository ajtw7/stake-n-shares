from backend.app.schemas import CompareRequest, Bet
from backend.app.services import compute_compare

def test_simple_win():
    req = CompareRequest(starting_capital=1000, equity_symbol="SPY", equity_weight=0.8, equity_return_pct=0.05,
                         bet=Bet(league="NFL", event_id="E1", stake=100, odds=2.5, outcome="win"))
    out = compute_compare(req)
    assert "roi_pct" in out
    assert out["bet"]["pnl"] == 150.0 or out["bet"]["pnl"] == 150  # stake*(odds-1)