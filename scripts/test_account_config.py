import os, json, sys
import requests

ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL") or "https://paper-api.alpaca.markets"
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")

def main() -> int:
    if not API_KEY or not API_SECRET:
        print("Set ALPACA_API_KEY and ALPACA_SECRET_KEY in environment or .env", file=sys.stderr)
        return 2

    url = f"{ALPACA_BASE_URL.rstrip('/')}/v2/account/configurations"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
        "Accept": "application/json",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))
    # return 0 for success or non-zero for error
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())