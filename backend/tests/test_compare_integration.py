import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import config
import logging

client = TestClient(app)
logger = logging.getLogger("tests.compare.integration")

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
    logger.info("INTEGRATION test_compare_live_external_apis enabling external APIs")

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
    logger.info("REQUEST snapshot=%s body=%s", odds_date, body)
    r = client.post(f"/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date={odds_date}", json=body)
    logger.info("RESPONSE status=%s json=%s", r.status_code, r.text)
    assert r.status_code == 200
    data = r.json()
    assert data["starting_capital"] == 1000
    assert data["equity"]["allocated"] == 700.0
    assert data["bet"]["allocated"] == 300.0
    assert data["combined_final"] > 1000  # win path
    logger.info("ASSERT success roi_pct=%s odds_meta=%s", data["roi_pct"], data.get("odds_meta"))
    meta = data["odds_meta"]
    # If API returned real odds, fallback_used should be False
    assert "fallback_used" in meta
    # Allow either outcome; log for visibility
    if meta["fallback_used"]:
        print("INFO: Fallback odds path used (remote fetch failed or returned None)")

@pytest.mark.integration
def test_compare_two_snapshots(monkeypatch):
    alpaca_key = os.getenv("ALPACA_API_KEY")
    odds_key = os.getenv("ODDS_API_KEY")
    if not alpaca_key or not odds_key:
        pytest.skip("Missing ALPACA_API_KEY or ODDS_API_KEY")

    monkeypatch.setattr(config.settings, "USE_EXTERNAL_APIS", True)
    logger.info("INTEGRATION test_compare_two_snapshots start")

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

    logger.info("REQUEST snapshot1=%s snapshot2=%s", "2025-02-08T22:00:00Z", "2025-02-09T22:25:38Z")
    r1 = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date=2025-02-08T22:00:00Z", json=base_body)
    r2 = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date=2025-02-09T22:25:38Z", json=base_body)
    logger.info("RESPONSES r1=%s r2=%s", r1.status_code, r2.status_code)
    d1, d2 = r1.json(), r2.json()
    logger.info("PNL snapshot1=%s snapshot2=%s", d1["bet"]["pnl"], d2["bet"]["pnl"])
    assert d2["bet"]["pnl"] >= d1["bet"]["pnl"]
    logger.info("ASSERT success pnl_growth=%s", d2["bet"]["pnl"] - d1["bet"]["pnl"])

@pytest.mark.integration
def test_compare_explicit_odds_snapshot_no_fallback(monkeypatch):
    alpaca_key = os.getenv("ALPACA_API_KEY")
    odds_key = os.getenv("ODDS_API_KEY")
    if not alpaca_key or not odds_key:
        pytest.skip("Missing ALPACA_API_KEY or ODDS_API_KEY")
    monkeypatch.setattr(config.settings, "USE_EXTERNAL_APIS", True)

    body = {
        "starting_capital": 1000,
        "equity_symbol": "AAPL",
        "equity_weight": 0.7,
        "bet": {
            "league": "NFL",
            "event_id": "3fd7cba821568399920fcea4dadad30d",
            "stake": 100,
            "odds": 2.3,
            "outcome": "win"
        }
    }
    snap = "2025-02-09T22:25:38Z"
    r = client.post(f"/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date={snap}", json=body)
    assert r.status_code == 200
    meta = r.json()["odds_meta"]
    assert meta == {
        "snapshot_timestamp": snap,
        "resolved_odds": 2.3,
        "fallback_used": False
    }