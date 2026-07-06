#!/usr/bin/env bash
set -e

echo "[entrypoint] Applying database migrations..."
alembic upgrade head

echo "[entrypoint] Starting API on 0.0.0.0:8000..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
