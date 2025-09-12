import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
import logging
logger = logging.getLogger("tests.compare.validation")

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
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["odds"] = None
    expected_equity_alloc = 700.0
    expected_bet_alloc = 300.0
    logger.info("TEST start=happy_path_success_win expected_equity_alloc=%s expected_bet_alloc=%s fallback_odds=2.0",
                expected_equity_alloc, expected_bet_alloc)
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    logger.info("RESPONSE status=%s body=%s", r.status_code, r.text)
    assert r.status_code == 200
    data = r.json()
    assert data["starting_capital"] == 1000
    assert data["equity"]["allocated"] == expected_equity_alloc
    assert data["equity"]["pnl"] == 0.0
    assert data["bet"]["allocated"] == expected_bet_alloc
    assert data["bet"]["pnl"] == 100.0
    assert data["combined_final"] == 1100.0
    assert data["roi_pct"] == 10.0
    logger.info("ASSERT success roi_pct=%s", data["roi_pct"])

def test_happy_path_outcome_loss():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["outcome"] = "loss"
    body["bet"]["odds"] = None
    logger.info("TEST start=happy_path_outcome_loss expecting zero bet pnl")
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    logger.info("RESPONSE status=%s body=%s", r.status_code, r.text)
    assert r.status_code == 200
    data = r.json()
    assert data["bet"]["pnl"] == 0.0
    assert data["combined_final"] == 1000.0
    logger.info("ASSERT success combined_final=%s", data["combined_final"])

def test_metadata_no_snapshot_fallback():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["odds"] = None
    logger.info("TEST metadata_no_snapshot_fallback expecting fallback_used=True")
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    meta = r.json()["odds_meta"]
    logger.info("META %s", meta)
    assert meta["snapshot_timestamp"] is None
    assert meta["resolved_odds"] == 2.0
    assert meta["fallback_used"] is True

def test_metadata_no_snapshot_explicit_odds():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["odds"] = 2.25
    logger.info("TEST metadata_no_snapshot_explicit_odds expecting fallback_used=False")
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    meta = r.json()["odds_meta"]
    logger.info("META %s", meta)
    assert meta["snapshot_timestamp"] is None
    assert meta["resolved_odds"] == 2.25
    assert meta["fallback_used"] is False

def test_metadata_with_snapshot_fallback():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["odds"] = None
    snap = "2025-02-09T22:25:38Z"
    logger.info("TEST metadata_with_snapshot_fallback snapshot=%s", snap)
    r = client.post(f"/api/v1/compare?start=2025-02-02&end=2025-02-10&odds_date={snap}", json=body)
    meta = r.json()["odds_meta"]
    logger.info("META %s", meta)
    assert meta["snapshot_timestamp"] == snap
    assert meta["resolved_odds"] == 2.0
    assert meta["fallback_used"] is True

def test_metadata_explicit_odds_no_fallback():
    body = BASE_BODY.copy()
    body["bet"] = body["bet"].copy()
    body["bet"]["odds"] = 2.3   # explicit fixed odds
    r = client.post("/api/v1/compare?start=2025-02-02&end=2025-02-10", json=body)
    assert r.status_code == 200
    meta = r.json()["odds_meta"]
    assert meta["snapshot_timestamp"] is None
    assert meta["resolved_odds"] == 2.3
    assert meta["fallback_used"] is False