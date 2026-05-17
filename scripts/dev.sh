#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export DATABASE_URL="${DATABASE_URL:-postgresql://quarterback:quarterback@localhost:55432/quarterback}"
export WEB_ORIGINS="${WEB_ORIGINS:-http://localhost:5173,http://127.0.0.1:5173}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://localhost:8000}"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"

docker compose up -d --wait postgis

uv run uvicorn gallatin_api.main:app \
  --app-dir apps/api/src \
  --host 0.0.0.0 \
  --port "$API_PORT" \
  --reload &
API_PID=$!

npm --workspace apps/web run dev -- --host 0.0.0.0 --port "$WEB_PORT" &
WEB_PID=$!

cleanup() {
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

while true; do
  if ! kill -0 "$API_PID" 2>/dev/null; then
    wait "$API_PID"
    exit $?
  fi

  if ! kill -0 "$WEB_PID" 2>/dev/null; then
    wait "$WEB_PID"
    exit $?
  fi

  sleep 1
done
