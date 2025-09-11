import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# Reusable valid body (override fields per test)
BASE_BODY = {
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

def test_invalid_date_format():
    body = BASE_BODY.copy()
    r = client.post("/api/v1/compare?start=2025-02-30&end=2025-03-01", json=body)
    assert r.status_code == 422
    assert "Invalid start" in r.text

def test_reversed_range():
    body = BASE_BODY.copy()
    r = client.post("/api/v1/compare?start=2025-03-05&end=2025-03-01", json=body)
    assert r.status_code == 422
    assert "start must be <=" in r.text

def test_invalid_event_id():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["event_id"] = "BADID"
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    assert r.status_code == 422
    assert "event_id must be 32-char hex" in r.text

def test_missing_bet():
    body = {
        "starting_capital": 1000,
        "equity_symbol": "AAPL",
        "equity_weight": 0.6
    }
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    assert r.status_code == 422

def test_stake_zero():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["stake"] = 0
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    assert r.status_code == 422

def test_outcome_invalid():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["outcome"] = "draw"
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    assert r.status_code == 422

def test_malformed_odds_date():
    body = BASE_BODY.copy()
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date=2025-13-99", json=body)
    assert r.status_code == 422
    assert "Invalid odds_date" in r.text

# --- Success / happy-path & edge cases ---

def test_happy_path_success_win():
    """Valid request should return 200 and expected deterministic ROI with fallbacks (no external APIs)."""
    body = BASE_BODY.copy()
    # Ensure odds None so fallback (2.0) path exercised
    body["bet"] = body["bet"].copy()
    body["bet"]["odds"] = None
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    # With starting_capital=1000, equity_weight=0.7 => equity_alloc=700, bet_alloc=300
    # equity_return_pct fallback=0 => equity final 700 (pnl 0)
    # bet: stake 100, odds fallback 2.0, outcome win => pnl 100, bet final 400
    # combined = 1100, ROI = 10%
    assert data["starting_capital"] == 1000
    assert data["equity"]["allocated"] == 700.0
    assert data["equity"]["pnl"] == 0.0
    assert data["bet"]["allocated"] == 300.0
    assert data["bet"]["pnl"] == 100.0
    assert data["combined_final"] == 1100.0
    assert data["roi_pct"] == 10.0


def test_happy_path_outcome_loss():
    """Outcome loss should yield zero bet PnL and ROI 0 given zero equity return."""
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["outcome"] = "loss"
    body["bet"]["odds"] = None  # force fallback odds path (should not matter for loss)
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["bet"]["pnl"] == 0.0
    assert data["combined_final"] == 1000.0
    assert data["roi_pct"] == 0.0