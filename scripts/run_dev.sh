#!/usr/bin/env bash
set -euo pipefail

# run from repo root
cd "$(dirname "$0")/.."

# activate .venv if present
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

# start FastAPI dev server
exec uvicorn backend.app.main:app --reload --port 8000