from typing import Any, Dict
import json
import sys
import inspect
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from .account import get_trading_client

# Try to import SDK request classes
try:
    from alpaca.trading.requests import (
        OrderRequest,
        MarketOrderRequest,
        LimitOrderRequest,
        StopLimitOrderRequest,
        StopOrderRequest,
        TrailingStopOrderRequest,
    )
except Exception:
    # If SDK models aren't available, we'll fall back to raw POST/submit
    OrderRequest = None
    MarketOrderRequest = None
    LimitOrderRequest = None
    StopLimitOrderRequest = None
    StopOrderRequest = None
    TrailingStopOrderRequest = None


def _to_plain(obj: Any) -> Dict:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    return {"value": str(obj)}


# new helper: recursively convert common non-JSON types to serializable ones
def _make_json_serializable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_make_json_serializable(v) for v in obj]
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        try:
            return obj.decode()
        except Exception:
            return list(obj)
    # fallback: return as-is (json may still fail for unknown types)
    return obj


_ORDER_CLASS_MAP = {
    "market": MarketOrderRequest,
    "limit": LimitOrderRequest,
    "stop_limit": StopLimitOrderRequest,
    "stop": StopOrderRequest,
    "trailing_stop": TrailingStopOrderRequest,
}


def create_order(payload: Dict[str, Any]) -> Dict:
    """
    Create an order dynamically.

    Required in payload:
      - type (e.g. "market", "limit", "stop_limit", "stop", "trailing_stop")
      - time_in_force

    Must include 'symbol' and either 'qty' or 'notional' (SDK enforces).
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    if "type" not in payload:
        raise ValueError("payload missing required field: type")
    if "time_in_force" not in payload:
        raise ValueError("payload missing required field: time_in_force")

    client = get_trading_client()
    t = str(payload["type"]).lower().replace("-", "_")

    # If we have the SDK request classes, prefer constructing the specific subclass
    RequestCls = _ORDER_CLASS_MAP.get(t)

    if RequestCls is not None:
        try:
            req = RequestCls(**payload)  # SDK will validate required fields per type
            # prefer high-level submit_order if available
            if hasattr(client, "submit_order"):
                resp = client.submit_order(req)
            else:
                # fallback to raw post using the model dict
                resp = client.post("/orders", req.model_dump() if hasattr(req, "model_dump") else req.dict())
            return _to_plain(resp)
        except Exception as e:
            # if validation fails or SDK not cooperating, fall back to raw behavior below
            fallback_err = e

    # If we reach here, try generic OrderRequest (if available) or raw submit/post
    if OrderRequest is not None:
        try:
            req = OrderRequest(**payload)
            if hasattr(client, "submit_order"):
                resp = client.submit_order(req)
            else:
                resp = client.post("/orders", req.model_dump() if hasattr(req, "model_dump") else req.dict())
            return _to_plain(resp)
        except Exception:
            pass

    # Last resort: try submit_order with raw payload or low-level post
    if hasattr(client, "submit_order"):
        try:
            resp = client.submit_order(payload)  # type: ignore
            return _to_plain(resp)
        except Exception:
            pass

    if hasattr(client, "post"):
        resp = client.post("/orders", payload)
        return _to_plain(resp)

    raise SystemExit("Unable to construct or submit order with this TradingClient.")


if __name__ == "__main__":
    # Example usage:
    # python -m paper_trading.orders '{"symbol":"TSLA","qty":1,"side":"buy","type":"market","time_in_force":"day"}'
    try:
        if len(sys.argv) > 1:
            payload = json.loads(sys.argv[1])
        else:
            payload = json.load(sys.stdin)
    except Exception:
        print("Provide JSON payload via arg or stdin.", file=sys.stderr)
        sys.exit(2)

    try:
        order = create_order(payload)
    except Exception as e:
        print("Order creation failed:", e, file=sys.stderr)
        sys.exit(1)

    # ensure UUID/datetime/decimal inside the response are string/number serializable
    serializable = _make_json_serializable(order)
    print(json.dumps(serializable, indent=2))