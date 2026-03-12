# CLAUDE.md — Stake N' Shares

## Project Overview

Stake N' Shares is a full-stack investment and sports-betting analytics dashboard. Users compare equity returns (via Alpaca) against betting outcomes (via The Odds API) over a date range, seeing combined ROI, PnL, and performance metrics.

## Architecture

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
  - `backend/app/` — FastAPI application (routes, services, schemas, models, config)
  - `paper_trading/` — Alpaca paper-trading SDK wrapper (account, orders, positions)
- **Frontend**: React 18, TypeScript, Vite, Chakra UI
  - `frontend/src/` — React SPA with compare form, result display, and comparison history
- **Database**: PostgreSQL 16 (local via docker-compose on port 5433)

## Development Setup

```bash
# 1. Python venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Start PostgreSQL
docker-compose up -d

# 3. Configure environment
cp .env.example .env   # then fill in your API keys

# 4. Run dev servers (backend + frontend concurrently)
npm run dev
# Or backend only:
uvicorn backend.app.main:app --reload --port 8000
```

## Running Tests

### Backend (from repo root)
```bash
pytest -q                                      # all tests
pytest -q -m "not integration"                 # skip integration tests (no real API keys needed)
pytest -q --cov=paper_trading --cov=backend    # with coverage
```

### Frontend
```bash
cd frontend && npm test
```

## Environment Variables

| Variable | Used By | Description |
|---|---|---|
| `ALPACA_API_KEY` | backend, paper_trading | Alpaca API key |
| `ALPACA_API_SECRET` | backend | Alpaca API secret (backend uses this name) |
| `ALPACA_SECRET_KEY` | paper_trading | Alpaca API secret (paper_trading accepts this or `ALPACA_API_SECRET`) |
| `ALPACA_BASE_URL` | backend, paper_trading | Alpaca base URL |
| `DATABASE_URL` | backend | PostgreSQL connection string |
| `ODDS_API_KEY` | backend | The Odds API key |
| `USE_EXTERNAL_APIS` | backend | `true` to hit real APIs; `false` for stub/fallback mode |

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml`:
- **test** job: Python 3.11, PostgreSQL 16 service, runs pytest with coverage on `paper_trading` and `backend`
- **frontend-test** job: Node 20, runs vitest and Vite build

Integration tests (marked `@pytest.mark.integration`) are skipped in CI.

## Key Conventions

- Two separate Pydantic Settings classes: `backend/app/config.py` (API keys) and `backend/app/core/settings.py` (DATABASE_URL).
- Tests in `tests/` cover the `paper_trading` module; tests in `backend/tests/` cover the FastAPI backend.
- `backend/tests/conftest.py` auto-disables external APIs via monkeypatch for deterministic unit tests.
- Frontend tests use vitest + React Testing Library + jsdom.
- Frontend success/fallback tests render `App` (not `CompareForm` standalone) because `CompareForm` delegates API calls to its parent via `onSubmit` prop. Results render via `ResultCard` in `App`, not via `ResultPanel` inside `CompareForm`.

## Update Policy

Update this file after every commit that changes project structure, dependencies, test configuration, or CI/CD setup.
