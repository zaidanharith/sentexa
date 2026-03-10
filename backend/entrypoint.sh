#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until python -c "import psycopg2; psycopg2.connect('${DATABASE_URL/+asyncpg/}')" 2>/dev/null; do
    echo "Database not ready, retrying in 2s..."
    sleep 2
done

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
