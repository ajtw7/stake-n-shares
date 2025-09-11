import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import config

client = TestClient(app)

@pytest.mark.integration
def test_compare_live_external_apis(monkeypatch):
    """
    Integration test hitting real external APIs.
    Skips automatically if required env keys not present.
    """
    # Require at least one key to proceed (adjust if equity source doesn't need both)
    alpaca_key = os.getenv("ALPACA_API_KEY")
    odds_key = os.getenv("ODDS_API_KEY")
    if not alpaca_key or not odds_key:
        pytest.skip("Missing ALPACA_API_KEY or ODDS_API_KEY; skipping live integration test")

    # Override autouse fixture effect
    monkeypatch.setattr(config.settings, "USE_EXTERNAL_APIS", True)

    body = {
        "starting_capital": 1000,
        "equity_symbol": "AAPL",
        "equity_weight": 0.7,
        "bet": {
            "league": "NFL",
            "event_id": "3fd7cba821568399920fcea4dadad30d",  # known event id you’ve been using
            "stake": 100,
            "odds": None,          # force live/historical fetch
            "outcome": "win"
        }
    }

    # Use a historical snapshot you know exists
    odds_date = "2025-02-09T22:25:38Z"
    r = client.post(f"/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date={odds_date}", json=body)
    assert r.status_code == 200, r.text

    data = r.json()
    # Structural assertions (avoid brittle exact numbers)
    assert data["starting_capital"] == 1000
    assert "equity" in data and "bet" in data
    assert data["equity"]["allocated"] == 700.0
    assert data["bet"]["allocated"] == 300.0
    # Odds-derived PnL should be >= 100 if odds > 2.0 (or exactly 100 if fallback 2.0 triggered)
    assert data["bet"]["pnl"] >= 100.0
    # Combined final should exceed starting capital for a win
    assert data["combined_final"] > 1000

@pytest.mark.integration
def test_compare_two_snapshots(monkeypatch):
    alpaca_key = os.getenv("ALPACA_API_KEY")
    odds_key = os.getenv("ODDS_API_KEY")
    if not alpaca_key or not odds_key:
        pytest.skip("Missing ALPACA_API_KEY or ODDS_API_KEY")

    from backend.app import config
    monkeypatch.setattr(config.settings, "USE_EXTERNAL_APIS", True)

    base_body = {
        "starting_capital": 1000,
        "equity_symbol": "AAPL",
        "equity_weight": 0.7,
        "bet": {
            "league": "NFL",
            "event_id": "3fd7cba821568399920fcea4dadad30d",
            "stake": 100,
            "odds": None,
            "outcome": "win"
        }
    }

    r1 = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date=2025-02-08T22:00:00Z", json=base_body)
    r2 = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date=2025-02-09T22:25:38Z", json=base_body)
    assert r1.status_code == 200 and r2.status_code == 200
    d1, d2 = r1.json(), r2.json()
    # Expect later snapshot could have equal or higher odds (bet pnl difference proves dynamic behavior)
    assert d2["bet"]["pnl"] >= d1["bet"]["pnl"]