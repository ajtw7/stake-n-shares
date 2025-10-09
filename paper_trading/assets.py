from typing import List
try:
    from alpaca.trading.requests import GetAssetsRequest
    from alpaca.trading.enums import AssetClass
except ModuleNotFoundError:
    raise SystemExit("Missing dependency 'alpaca-py'. Install it in your venv: pip install alpaca-py")

# use package-relative import
from .account import get_trading_client

def get_us_equities() -> List[dict]:
    client = get_trading_client()
    req = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
    if hasattr(client, "get_all_assets"):
        assets = client.get_all_assets(req)
    elif hasattr(client, "get_assets"):
        assets = client.get_assets(req)
    else:
        raise SystemExit("TradingClient has no get_all_assets/get_assets method")
    return list(assets)

if __name__ == "__main__":
    assets = get_us_equities()
    print(f"Found {len(assets)} US equity assets.")
    for a in assets[:20]:
        sym = getattr(a, "symbol", None) or (a.get("symbol") if isinstance(a, dict) else None)
        name = getattr(a, "name", None) or (a.get("name") if isinstance(a, dict) else None)
        print(f"- {sym} — {name}")

