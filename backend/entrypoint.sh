#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until python -c "import psycopg2; psycopg2.connect('${DATABASE_URL/+asyncpg/}')" 2>/dev/null; do
    echo "Database not ready, retrying in 2s..."
    sleep 2
done

echo "Running database migrations..."
alembic upgrade head

if [ "${PREPARE_DATA_ON_START:-false}" = "true" ]; then
    echo "Preparing NLP dataset..."
    python -m app.nlp.scripts.prepare_data
fi

if [ "${PREPROCESS_DATA_ON_START:-false}" = "true" ]; then
    echo "Preprocessing NLP dataset..."
    python -m app.nlp.scripts.preprocess_data
fi

if [ "${FEATURE_EXTRACTION_ON_START:-false}" = "true" ]; then
    echo "Extracting features from NLP dataset..."
    python -m app.nlp.scripts.feature_extraction
fi

if [ "${TRAIN_CLASSIFIER_ON_START:-false}" = "true" ]; then
    echo "Training classifier on NLP dataset..."
    python -m app.nlp.scripts.train_classifier
fi

if [ "${EVALUATE_CLASSIFIER_ON_START:-false}" = "true" ]; then
    echo "Evaluating classifier on NLP dataset..."
    python -m app.nlp.scripts.evaluate_classifier
fi

echo "Starting application..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -