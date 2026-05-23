#!/bin/bash
set -e

echo "Skipping database ping check..."

echo "Cleaning up Hugging Face cache lock files..."
find /app/.cache/huggingface -name "*.lock" -delete 2>/dev/null || true

echo "Starting application with Uvicorn..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info