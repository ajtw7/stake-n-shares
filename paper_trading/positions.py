from typing import List, Any, Dict
import json
import sys

from .account import get_trading_client


def _pos_to_dict(pos: Any) -> Dict:
    # pydantic model (alpaca-py v1+)
    if hasattr(pos, "model_dump"):
        return pos.model_dump()
    # common .dict() accessor
    if hasattr(pos, "dict"):
        return pos.dict()
    # plain object -> filter private attrs
    if hasattr(pos, "__dict__"):
        return {k: v for k, v in pos.__dict__.items() if not k.startswith("_")}
    # already a dict
    if isinstance(pos, dict):
        return pos
    # fallback
    return {"value": str(pos)}


def get_current_positions() -> List[Dict]:
    client = get_trading_client()
    if hasattr(client, "get_all_positions"):
        raw = client.get_all_positions()
    elif hasattr(client, "get_positions"):
        raw = client.get_positions()
    else:
        raise SystemExit("TradingClient has no get_all_positions/get_positions method")

    positions = list(raw)
    return [_pos_to_dict(p) for p in positions]


if __name__ == "__main__":
    try:
        positions = get_current_positions()
    except Exception as e:
        print("Failed to fetch positions:", e, file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(positions)} positions.")
    # pretty-print JSON for easy inspection
    print(json.dumps(positions, indent=2))