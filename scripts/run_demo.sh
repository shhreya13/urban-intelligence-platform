#!/usr/bin/env bash
# scripts/run_demo.sh — starts backend and frontend together for a live demo.
# Backend runs in the background; frontend runs in the foreground so Ctrl+C
# stops the demo cleanly. Kills the backend on exit.
set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
  echo "Stopping backend..."
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then python -m venv venv; fi
source venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --port 8000 &
BACKEND_PID=$!

echo "Backend running (PID $BACKEND_PID) — waiting for it to come up..."
sleep 2

cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then npm install; fi
if [ ! -f ".env" ]; then cp .env.example .env; fi
npm run dev
