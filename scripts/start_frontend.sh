#!/usr/bin/env bash
# scripts/start_frontend.sh — installs deps (if needed) and runs the Vite dev server.
set -e
cd "$(dirname "$0")/../frontend"

if [ ! -d "node_modules" ]; then
  npm install
fi
if [ ! -f ".env" ]; then
  cp .env.example .env
fi
npm run dev
