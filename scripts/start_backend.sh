#!/usr/bin/env bash
# scripts/start_backend.sh — installs deps (if needed) and runs the FastAPI backend.
set -e
cd "$(dirname "$0")/../backend"

if [ ! -d "venv" ]; then
  python -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --reload --port 8000
