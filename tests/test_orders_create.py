from typing import Any
import pytest

import paper_trading.orders as orders_mod


class FakeCreatedOrder:
    def __init__(self, oid: str):
        self._id = oid

    def model_dump(self):
        return {"id": self._id}


class SubmitClient:
    def submit_order(self, payload: dict) -> Any:
        # echo back something that create_order will convert
        return FakeCreatedOrder("created-1")


def test_create_order_uses_submit(monkeypatch):
    monkeypatch.setattr(orders_mod, "get_trading_client", lambda: SubmitClient())
    payload = {"symbol": "AAPL", "qty": 1, "side": "buy", "type": "market", "time_in_force": "day"}
    out = orders_mod.create_order(payload)
    assert isinstance(out, dict)
    assert out["id"] == "created-1"