from pathlib import Path
import os
from typing import Dict, Optional
from dotenv import load_dotenv
import inspect
import json

try:
    from alpaca.trading.client import TradingClient
except ModuleNotFoundError:
    raise SystemExit(
        "Missing dependency 'alpaca-py'. Install it in your venv:\n\n"
        "  source .venv/bin/activate\n"
        "  pip install alpaca-py\n"
    )

# load repo root .env then prefer paper_trading/.env
repo_root = Path(__file__).resolve().parents[1]
root_env = repo_root / ".env"
local_env = Path(__file__).resolve().parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=str(root_env), override=False)
if local_env.exists():
    load_dotenv(dotenv_path=str(local_env), override=True)

def _strip(v: Optional[str]) -> Optional[str]:
    return v.strip().strip('"').strip("'") if v else None

ALPACA_API_KEY = _strip(os.getenv("ALPACA_API_KEY"))
ALPACA_SECRET_KEY = _strip(
    os.getenv("ALPACA_SECRET_KEY")
    or os.getenv("ALPACA_API_SECRET")
    or os.getenv("ALPACA_SECRET")
)
ALPACA_BASE_URL = _strip(os.getenv("ALPACA_BASE_URL"))
ALPACA_PAPER = _strip(os.getenv("ALPACA_PAPER")) or "true"

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise SystemExit("ALPACA_API_KEY and ALPACA_SECRET must be set in environment or .env file")

# determine base_url
if ALPACA_BASE_URL:
    _base_url = ALPACA_BASE_URL
else:
    _base_url = "https://paper-api.alpaca.markets" if ALPACA_PAPER.lower() in ("1", "true", "yes") else "https://api.alpaca.markets"

_client = None  # cache

def get_trading_client(*, require_trading_enabled: bool = False):
    base = os.getenv("ALPACA_BASE_URL")
    key = os.getenv("ALPACA_API_KEY")
    secret = os.getenv("ALPACA_API_SECRET")
    if not (base and key and secret):
        raise RuntimeError("Missing Alpaca credentials — set ALPACA_BASE_URL/ALPACA_API_KEY/ALPACA_API_SECRET")
    enabled = os.getenv("ENABLE_TRADING", "false").lower() in ("1","true","yes")
    if require_trading_enabled and not enabled:
        raise RuntimeError("Trading is disabled: set ENABLE_TRADING=true to enable live trading")
    return TradingClient(key, secret, base_url=base)

def get_account_info() -> Dict[str, str]:
    client = get_trading_client()
    try:
        account = client.get_account()
    except Exception as e:
        raise SystemExit(f"Failed to fetch account: {e}")
    return {
        "account_number": getattr(account, "account_number", ""),
        "status": getattr(account, "status", ""),
        "trading_blocked": str(getattr(account, "trading_blocked", False)),
        "buying_power": str(getattr(account, "buying_power", "0")),
        "cash": str(getattr(account, "cash", "0")),
    }

def fetch_account_configurations() -> dict:
    """
    Call TradingClient.get_account_configurations() and return a plain dict.
    Uses the cached get_trading_client() so no duplicate client logic.
    """
    client = get_trading_client()
    try:
        cfg = client.get_account_configurations()
    except Exception as e:
        raise SystemExit(f"Failed to fetch account configurations: {e}")

    # If the SDK returns a pydantic model, convert to dict; otherwise return as-is
    if hasattr(cfg, "model_dump"):
        return cfg.model_dump()
    try:
        return dict(cfg)
    except Exception:
        return cfg

if __name__ == "__main__":
    info = get_account_info()
    if info["trading_blocked"].lower() == "true":
        print("Account is currently restricted from trading.")
    print(f'${info["buying_power"]} is available as buying power.')
    print("Account info:", info)

    # Print account configurations using the existing TradingClient.get_account_configurations()
    try:
        cfg = fetch_account_configurations()
        print("\nAccount configurations:")
        print(json.dumps(cfg, indent=2))
    except SystemExit as e:
        print("Failed to fetch account configurations:", e)

