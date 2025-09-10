import os
import time
import json
import sys
import requests
import datetime
from typing import Optional, Dict, Any, List

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
BASE = "https://api.the-odds-api.com/v4/historical/sports/americanfootball_nfl"

if not ODDS_API_KEY:
    print("ERROR: ODDS_API_KEY not set in environment.")
    sys.exit(1)

def fetch_events_snapshot(ts: str) -> Optional[Dict[str, Any]]:
    params = {"apiKey": ODDS_API_KEY, "date": ts}
    try:
        r = requests.get(f"{BASE}/events", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[events] {ts} error: {e}")
        return None

def fetch_single_event_odds(event_id: str, ts: str) -> Optional[Dict[str, Any]]:
    params = {
        "apiKey": ODDS_API_KEY,
        "date": ts,
        "markets": "h2h",
        "regions": "us",
        "oddsFormat": "decimal"
    }
    url = f"{BASE}/events/{event_id}/odds"
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[odds] {ts} error: {e}")
        return None

def extract_best_h2h(odds_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    event_obj = odds_payload.get("data")
    if not isinstance(event_obj, dict):
        return None
    if "bookmakers" not in event_obj:
        return None
    best_price = None
    best_team = None
    best_bookmaker = None
    all_prices = []
    for bk in event_obj.get("bookmakers", []):
        for m in bk.get("markets", []):
            if m.get("key") == "h2h":
                for o in m.get("outcomes", []):
                    price = o.get("price")
                    name = o.get("name")
                    if isinstance(price, (int, float)):
                        all_prices.append(price)
                        if best_price is None or price > best_price:
                            best_price = float(price)
                            best_team = name
                            best_bookmaker = bk.get("key")
    if best_price is None:
        return None
    return {
        "best_price": best_price,
        "best_team": best_team,
        "best_bookmaker": best_bookmaker,
        "distinct_price_count": len(set(all_prices))
    }

def snapshot_contains_event(snapshot_payload: Dict[str, Any], event_id: str) -> bool:
    data = snapshot_payload.get("data", [])
    if not isinstance(data, list):
        return False
    return any(ev.get("id") == event_id for ev in data)

# ------------------ ADDED: Previous-day probe ------------------
def probe_previous_day(event_id: str,
                       start_timestamp: str,
                       probe_hours: List[int]) -> Optional[str]:
    """
    Coarse probe for event presence on the previous UTC day.
    Returns the LATEST probe timestamp (on previous day) that contained the event,
    or None if no probes found it.
    """
    try:
        start_dt = datetime.datetime.fromisoformat(start_timestamp.replace("Z", "+00:00"))
    except Exception:
        print("[probe] Invalid start timestamp format; skipping probe.")
        return None

    prev_day = (start_dt - datetime.timedelta(days=1)).date()
    found_ts = None
    print(f"[probe] Previous UTC day: {prev_day}")
    for hour in sorted(probe_hours):
        ts = datetime.datetime(prev_day.year, prev_day.month, prev_day.day,
                               hour, 0, 0, tzinfo=datetime.timezone.utc
                               ).isoformat().replace("+00:00", "Z")
        snap = fetch_events_snapshot(ts)
        if not snap:
            print(f"[probe] {ts} -> (no snapshot / error)")
            continue
        present = snapshot_contains_event(snap, event_id)
        print(f"[probe] {ts} -> event_present={present}")
        if present:
            found_ts = ts  # keep latest that worked
    if found_ts:
        print(f"[probe] SUCCESS: event found on previous day (latest probe) at {found_ts}")
    else:
        print("[probe] No previous-day probes contained the event.")
    return found_ts
# ---------------------------------------------------------------

# ------------------ ADDED: multi-day previous probing ------------------
def deep_probe_previous_days(event_id: str,
                             start_timestamp: str,
                             probe_hours: List[int],
                             max_days: int) -> str:
    """
    Repeatedly probe earlier UTC days (up to max_days) to find the earliest
    day containing the event at any of the probe_hours. Returns the earliest
    snapshot timestamp discovered (latest matching probe hour on that earliest day),
    or the original start_timestamp if no earlier day had the event.
    """
    earliest = start_timestamp
    for _ in range(max_days):
        found_prev_ts = probe_previous_day(event_id, earliest, probe_hours)
        if not found_prev_ts:
            break  # no earlier day presence
        # Shift to earlier day snapshot and continue probing further back
        earliest = found_prev_ts
        print(f"[deep-probe] Continuing to probe before {earliest}")
    return earliest
# -----------------------------------------------------------------------

def crawl_snapshots(event_id: str,
                    start_timestamp: str,
                    max_back: int = 15,
                    max_forward: int = 15,
                    sleep_sec: float = 0.6) -> List[Dict[str, Any]]:
    visited = {}
    queue = [(start_timestamp, "origin")]
    results = []

    def enqueue(ts: Optional[str], direction: str):
        if ts and ts not in visited:
            queue.append((ts, direction))

    back_count = 0
    fwd_count = 0

    try:
        start_day = datetime.datetime.fromisoformat(start_timestamp.replace("Z","+00:00")).date()
    except Exception:
        start_day = None

    crossed_previous_day = False

    while queue:
        ts, direction = queue.pop(0)
        if ts in visited:
            continue
        snap = fetch_events_snapshot(ts)
        visited[ts] = True
        if snap is None:
            continue

        has_event = snapshot_contains_event(snap, event_id)
        best_block = None
        if has_event:
            odds_payload = fetch_single_event_odds(event_id, ts)
            best_block = extract_best_h2h(odds_payload) if odds_payload else None

        snapshot_ts = snap.get("timestamp", ts)

        if start_day:
            try:
                snap_day = datetime.datetime.fromisoformat(snapshot_ts.replace("Z","+00:00")).date()
                if snap_day < start_day and not crossed_previous_day:
                    print(f"[info] Crossed into previous day at snapshot {snapshot_ts}")
                    crossed_previous_day = True
            except Exception:
                pass

        results.append({
            "snapshot_timestamp": snapshot_ts,
            "requested_timestamp": ts,
            "direction": direction,
            "previous_timestamp": snap.get("previous_timestamp"),
            "next_timestamp": snap.get("next_timestamp"),
            "event_present": has_event,
            "odds": best_block
        })

        prev_ts = snap.get("previous_timestamp")
        next_ts = snap.get("next_timestamp")

        if direction in ("origin", "forward") and fwd_count < max_forward and next_ts:
            enqueue(next_ts, "forward")
            fwd_count += 1
        if direction in ("origin", "backward") and back_count < max_back and prev_ts:
            enqueue(prev_ts, "backward")
            back_count += 1

        time.sleep(sleep_sec)

    results.sort(key=lambda r: r["snapshot_timestamp"])
    return results

def summarize(results: List[Dict[str, Any]]):
    present = [r for r in results if r["event_present"]]
    with_odds = [r for r in present if r.get("odds")]
    distinct_best_prices = sorted({r["odds"]["best_price"] for r in with_odds if r.get("odds")})
    earliest = present[0]["snapshot_timestamp"] if present else None
    latest = present[-1]["snapshot_timestamp"] if present else None
    print("\n=== Historical Coverage Summary ===")
    print(f"Total snapshots crawled: {len(results)}")
    print(f"Snapshots with event:    {len(present)}")
    print(f"Snapshots with odds:     {len(with_odds)}")
    print(f"Distinct best prices:    {distinct_best_prices}")
    print(f"Earliest snapshot:       {earliest}")
    print(f"Latest snapshot:         {latest}")
    if with_odds:
        last = with_odds[-1]
        print("Sample (last odds snapshot):")
        print(f"  Timestamp: {last['snapshot_timestamp']}")
        print(f"  Best price: {last['odds']['best_price']} ({last['odds']['best_team']}) via {last['odds']['best_bookmaker']}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python historcal_coverage.py <EVENT_ID> <START_SNAPSHOT_TIMESTAMP> "
              "[--max-back N] [--max-forward N] [--json out.json] "
              "[--probe-prev] [--probe-hours h1,h2,...] "
              "[--multi-day-prev] [--max-prev-days D]")
        print("Example:")
        print("  python historcal_coverage.py 3fd7cba821568399920fcea4dadad30d 2025-02-09T22:25:38Z "
              "--probe-prev --probe-hours 10,12,14,16,18,20,22 --max-back 120 --json coverage.json")
        sys.exit(1)

    event_id = sys.argv[1].strip()
    start_ts = sys.argv[2].strip()

    max_back = 15
    max_forward = 15
    out_path = None
    do_probe = False
    multi_day_prev = False        # <-- ADDED
    max_prev_days = 7             # <-- ADDED (limit how many days to chain)
    probe_hours = [12, 16, 18, 20, 22]

    args = sys.argv[3:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--max-back" and i + 1 < len(args):
            max_back = int(args[i+1]); i += 2
        elif arg == "--max-forward" and i + 1 < len(args):
            max_forward = int(args[i+1]); i += 2
        elif arg == "--json" and i + 1 < len(args):
            out_path = args[i+1]; i += 2
        elif arg == "--probe-prev":
            do_probe = True; i += 1
        elif arg == "--probe-hours" and i + 1 < len(args):
            probe_hours = [int(h.strip()) for h in args[i+1].split(",") if h.strip().isdigit()]
            i += 2
        elif arg == "--multi-day-prev":          # <-- ADDED
            multi_day_prev = True; i += 1
        elif arg == "--max-prev-days" and i + 1 < len(args):  # <-- ADDED
            max_prev_days = int(args[i+1]); i += 2
        else:
            i += 1

    print(f"[run] event_id={event_id} start={start_ts} max_back={max_back} max_forward={max_forward} "
          f"probe={do_probe} multi_day_prev={multi_day_prev} max_prev_days={max_prev_days}")

    if do_probe:
        if multi_day_prev:
            # Continuous multi-day probing
            earliest = deep_probe_previous_days(event_id, start_ts, probe_hours, max_prev_days)
            if earliest != start_ts:
                print(f"[run] Multi-day earliest start identified: {earliest}")
                start_ts = earliest
            else:
                print("[run] No earlier day snapshots discovered via deep probe.")
        else:
            # Single previous-day probe only
            found_prev_ts = probe_previous_day(event_id, start_ts, probe_hours)
            if found_prev_ts:
                print(f"[run] Using previous-day found snapshot as new start: {found_prev_ts}")
                start_ts = found_prev_ts
            else:
                print("[run] No previous-day presence detected (continuing with original start).")

    results = crawl_snapshots(event_id, start_ts, max_back=max_back, max_forward=max_forward)
    summarize(results)

    if out_path:
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Wrote JSON: {out_path}")

if __name__ == "__main__":
    main()