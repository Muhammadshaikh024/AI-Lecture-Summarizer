#!/usr/bin/env bash
set -e

echo "Starting backend on :8000"
(cd backend && uvicorn app.main:app --reload --port 8000) &
BACK_PID=$!

echo "Starting frontend on :3000"
(cd frontend && npm run dev) &
FRONT_PID=$!

trap "kill $BACK_PID $FRONT_PID" EXIT
wait