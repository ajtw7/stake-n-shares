# Stake-n-Shares MVP Synopsis (As of Sept 12)


## 1. Plain-English (Non-Technical) Summary
This MVP lets you compare two simple choices for the same pool of money:
1. Put part of it into a stock (e.g. Apple).
2. Use the rest to place a single sports moneyline bet (e.g. NFL game).

You pick:
- How much total money you start with.
- What percent goes into the stock vs the bet.
- The event you’re betting on.
- (Optional) A historical timestamp to say: “Pretend I locked these odds at this earlier time.”

The system:
- Calculates how the stock portion would have changed over the date range you selected.
- Uses either the historical odds at that timestamp, explicit odds you supply, or a safe default if odds can’t be found.
- Shows combined result (win or loss scenario) and a simple ROI percent.
- Tells you which odds were actually used and whether a fallback default was needed.

## 2. Key Concepts (Lay Level)
| Concept | Meaning |
|---------|---------|
| Starting Capital | Total money you’re allocating. |
| Equity Weight | Percentage of capital put into the stock. |
| Bet Stake | Amount risked on the sports outcome (from the non-equity portion). |
| Historical Snapshot | A “photo” of what odds looked like at a specific past time. |
| Resolved Odds | The odds number actually used in the calculation. |
| Fallback | A default odds number (2.0) used if real odds weren’t available. |
| ROI % | How much your total changed (percentage) after the scenario. |

## 3. Technical Overview
The MVP exposes one POST endpoint: `/api/v1/compare`.

It treats:
- Equity leg as a time-range calculation (start date → end date).
- Bet leg as point-in-time (odds from a single snapshot or explicitly provided).

Metadata now returned:
```json
"odds_meta": {
  "snapshot_timestamp": "<ISO timestamp or null>",
  "resolved_odds": <float>,
  "fallback_used": <bool>
}
```

### Request (example)
```json
{
  "starting_capital": 1000,
  "equity_symbol": "AAPL",
  "equity_weight": 0.7,
  "bet": {
    "league": "NFL",
    "event_id": "3fd7cba821568399920fcea4dadad30d",
    "stake": 100,
    "odds": null,
    "outcome": "win"
  }
}
```
Query params:
- `start=YYYY-MM-DD`
- `end=YYYY-MM-DD`
- `odds_date` (optional ISO timestamp or YYYY-MM-DD)

### Response (shape)
```json
{
  "starting_capital": 1000,
  "equity": {
    "symbol": "AAPL",
    "allocated": 700.0,
    "pnl": 0.0,
    "final": 700.0
  },
  "bet": {
    "event": "NFL:3fd7cba821568399920fcea4dadad30d",
    "allocated": 300.0,
    "pnl": 100.0,
    "final": 400.0
  },
  "combined_final": 1100.0,
  "roi_pct": 10.0,
  "odds_meta": {
    "snapshot_timestamp": "2025-02-09T22:25:38Z",
    "resolved_odds": 2.0,
    "fallback_used": false
  }
}
```

### Fallback Logic
1. If user supplies `bet.odds` → use it (no fetch).
2. Else if `odds_date` provided → attempt historical API lookup.
3. Else (future enhancement: live lookup) → try live odds.
4. If all fail → set `resolved_odds = 2.0`, mark `fallback_used = true`.

### Validation & Safety
- Event ID must be 32-char hex.
- Equity weight must be between 0 and 1.
- Stake > 0.
- Outcome is “win” or “loss”.
- Date formats strictly parsed.
- Markers separate integration tests from unit tests.

### Test Coverage (MVP)
- Input validation (bad dates, reversed range, malformed IDs).
- Happy paths (win/loss).
- Metadata scenarios:
  - Explicit odds → no fallback.
  - Missing odds + fallback.
  - Snapshot passthrough.
- Integration tests (run only when API keys exist) toggle external fetch behavior.

## 4. What’s Implemented
- Single compare endpoint.
- Snapshot-aware odds resolution with metadata.
- Fallback detection.
- Clear test segregation (unit vs integration).
- Logging for request + response summary.
- Script (`historcal_coverage.py`) to explore multi-snapshot historical availability manually (not part of API).

## 5. Current Limitations
| Area | Limitation |
|------|------------|
| Odds Time Series | Only one snapshot used; no odds interpolation or multi-snapshot strategy. |
| Equity Data | Currently simplified / placeholder if external fetch disabled. |
| Strategies | Only single bet vs equity; no portfolio, no multiple events. |
| Persistence | No database; all derived per request. |
| Error Semantics | No granular fallback reason codes yet. |
| Live Odds | Live path not fully differentiated from historical fallback in current stub. |

## 6. Suggested Next Steps
| Priority | Enhancement | Benefit |
|----------|-------------|---------|
| High | Add fallback_reason field | Improves explainability. |
| High | README section (user guide) merge | Onboarding clarity. |
| Medium | Multi-snapshot compare option | Show odds drift / timing impact. |
| Medium | Distinguish “user omitted” vs “fetch failed” | Analytics & trust. |
| Low | Persistence / caching | Performance & audit history. |
| Low | Strategy variants (“earliest”, “best”, “average”) | Deeper what-if analysis. |

## 7. Frontend Integration Notes
- Use `odds_meta.snapshot_timestamp` to label: “Odds as of …” or “Current (live)” if null.
- Display a subtle badge when `fallback_used = true` (e.g. “Default odds applied”).
- Provide input controls:
  - Date range picker (equity).
  - Optional odds snapshot timestamp input.
  - Explicit odds override (disables snapshot fetch).
- Consider warning if date span > N days and only one snapshot given (timing risk).

## 8. Security & Ops
- Environment keys (Alpaca, Odds API) required only for integration tests / external fetch mode.
- `USE_EXTERNAL_APIS` gates outbound calls (unit tests force it off).
- No secrets stored in code; ensure `.env` in `.gitignore`.

## 9. For Engineers (Deeper)
| Component | Responsibility |
|-----------|----------------|
| `compare_handler` | Validates query + body, builds request model, invokes execution. |
| `build_compare_request_with_live_data` | (Future) resolves equity return + odds (with external toggling). |
| `execute_compare` | Pure calculation / deterministic summary. |
| `historcal_coverage.py` | Offline discovery of odds snapshots & distinct prices. |

Data flow (simplified):
Client → FastAPI route → validation → request model → (optional fetch) → execute_compare → response + odds_meta.

## 10. For Non-Engineers: Why This MVP Matters
- Shows feasibility: You can anchor a bet to a past point in time and see how that compares to just holding stock.
- Creates a foundation to demonstrate value of timing and allocation decisions.
- Keeps scope tight: one bet, one equity slice, clear output.

---

Questions or need a “multi-snapshot roadmap” draft? Ask anytime.