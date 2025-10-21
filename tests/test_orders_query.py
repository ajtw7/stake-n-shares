import os
from typing import Any
import pytest

# ensure account import-time checks don't fail during tests
os.environ.setdefault("ALPACA_API_KEY", "test-key")
os.environ.setdefault("ALPACA_SECRET_KEY", "test-secret")
os.environ.setdefault("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

import paper_trading.orders_query as oq


class FakeOrder:
    def __init__(self, oid: str, symbol: str = "AAPL"):
        self._id = oid
        self.symbol = symbol

    # emulate SDK model_dump()
    def model_dump(self) -> dict:
        return {"id": self._id, "symbol": self.symbol}


class FakeClient:
    def __init__(self, orders):
        self._orders = orders

    def get_orders(self, *args, **kwargs):
        return self._orders

    def get_order_by_id(self, order_id, *args, **kwargs):
        # accept different id representations (UUID, str, model_dump dict)
        target = str(order_id)
        for o in self._orders:
            if hasattr(o, "model_dump"):
                oid = o.model_dump().get("id")
            else:
                oid = getattr(o, "_id", None)
            if oid is not None and str(oid) == target:
                return o
        raise KeyError("not found")


def test_list_orders_returns_plain_dicts(monkeypatch):
    fake = [FakeOrder("o1"), FakeOrder("o2")]
    monkeypatch.setattr(oq, "get_trading_client", lambda: FakeClient(fake))
    out = oq.list_orders()
    assert isinstance(out, list)
    assert out[0]["id"] == "o1"
    assert out[1]["symbol"] == "AAPL"


def test_get_order_by_id(monkeypatch):
    fake = [FakeOrder("target-123")]
    monkeypatch.setattr(oq, "get_trading_client", lambda: FakeClient(fake))
    out = oq.get_order_by_id("target-123")
    assert isinstance(out, dict)
    assert out["id"] == "target-123"