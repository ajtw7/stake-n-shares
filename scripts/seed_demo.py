#!/usr/bin/env python3
import json
import os
import sys
from pprint import pprint

# optional runtime import
try:
    import requests
except Exception:
    requests = None

payload = {
    "starting_capital": 1000,
    "equity_symbol": "SPY",
    "equity_weight": 0.8,
    "equity_return_pct": 0.05,
    "bet": {
        "league": "NFL",
        "event_id": "2025-09-14-NE-GB",
        "stake": 100,
        "odds": 2.5,
        "outcome": "win"
    }
}

def main():
    print("=== Demo payload ===")
    print(json.dumps(payload, indent=2))
    # To POST, set POST_PAYLOAD=1 and optionally SEED_POST_URL
    post_flag = os.getenv("POST_PAYLOAD", "0")
    post_url = os.getenv("SEED_POST_URL", "http://localhost:8000/api/v1/compare")
    if post_flag in ("1", "true", "True"):
        if not requests:
            print("requests not installed. Install with: pip install requests", file=sys.stderr)
            sys.exit(1)
        print(f"\nPosting to {post_url} ...")
        r = requests.post(post_url, json=payload, timeout=10)
        print(f"Status: {r.status_code}")
        try:
            pprint(r.json())
        except Exception:
            print(r.text)

if __name__ == "__main__":
    main()