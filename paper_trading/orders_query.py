from typing import Any, Dict, List, Optional
import json
import sys
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from .account import get_trading_client

# Prefer the SDK request models when available
try:
    from alpaca.trading.requests import GetOrdersRequest, GetOrderByIdRequest
except Exception:
    GetOrdersRequest = None  # type: ignore
    GetOrderByIdRequest = None  # type: ignore


def _to_plain(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    return obj


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
    return obj


def list_orders(
    status: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[datetime] = None,
    until: Optional[datetime] = None,
    direction: Optional[str] = None,
    nested: Optional[bool] = None,
    side: Optional[str] = None,
    symbols: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Return all orders using TradingClient.get_orders(), optionally filtered.

    Parameters accept the same fields as the SDK GetOrdersRequest. `status`, `direction`
    and `side` are accepted as strings and will be passed into the SDK model (the SDK
    will coerce/validate enums).
    """
    client = get_trading_client()
    if not hasattr(client, "get_orders"):
        raise SystemExit("TradingClient does not implement get_orders()")

    payload: Dict[str, Any] = {}
    if status is not None:
        payload["status"] = status
    if limit is not None:
        payload["limit"] = limit
    if after is not None:
        payload["after"] = after
    if until is not None:
        payload["until"] = until
    if direction is not None:
        payload["direction"] = direction
    if nested is not None:
        payload["nested"] = nested
    if side is not None:
        payload["side"] = side
    if symbols is not None:
        payload["symbols"] = symbols

    # Prefer building the SDK GetOrdersRequest so the SDK validates/converts values
    if GetOrdersRequest is not None:
        try:
            req = GetOrdersRequest(**payload)
            raw = client.get_orders(req)
        except Exception:
            # fallback to passing raw dict as filter
            raw = client.get_orders(payload)
    else:
        raw = client.get_orders(payload)

    orders = list(raw) if not isinstance(raw, list) else raw
    return [_to_plain(o) for o in orders]


def get_order_by_id(order_id: str, nested: Optional[bool] = None) -> Dict:
    """
    Return a single order by id using TradingClient.get_order_by_id().
    If `nested` is provided and SDK GetOrderByIdRequest is available it will be used.
    """
    client = get_trading_client()
    if not hasattr(client, "get_order_by_id"):
        raise SystemExit("TradingClient does not implement get_order_by_id()")

    if GetOrderByIdRequest is not None and nested is not None:
        try:
            req = GetOrderByIdRequest(nested=nested)
            raw = client.get_order_by_id(order_id, req)
        except Exception:
            raw = client.get_order_by_id(order_id)
    else:
        raw = client.get_order_by_id(order_id)

    return _to_plain(raw)


if __name__ == "__main__":
    # CLI:
    #  - no args => list orders
    #  - --status=open --limit=50 --symbols=AAPL,TSLA  => list with filters
    #  - <order_id> => fetch single order by id
    try:
        if len(sys.argv) == 1:
            out = list_orders()
        else:
            first = sys.argv[1]
            if first.startswith("--"):
                # parse simple --key=value args for list_orders
                opts: Dict[str, Any] = {}
                for a in sys.argv[1:]:
                    if not a.startswith("--"):
                        continue
                    if "=" in a:
                        k, v = a[2:].split("=", 1)
                    else:
                        k, v = a[2:], "true"
                    if k == "limit":
                        opts[k] = int(v)
                    elif k in ("nested",):
                        opts[k] = v.lower() in ("1", "true", "yes")
                    elif k == "symbols":
                        opts[k] = v.split(",") if v else []
                    else:
                        opts[k] = v
                out = list_orders(**opts)
            else:
                out = get_order_by_id(first)
        print(json.dumps(_make_json_serializable(out), indent=2))
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

