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
    INPUT_PATH="${NLP_INPUT_PATH:-app/nlp/data/raw/dataset.tsv}"
    OUTPUT_DIR="${NLP_OUTPUT_DIR:-app/nlp/data/processed}"
    TEXT_COLUMN="${NLP_TEXT_COLUMN:-text}"
    LABEL_COLUMN="${NLP_LABEL_COLUMN:-label}"
    SPLIT_MODE="${NLP_SPLIT_MODE:-train-val-test}"
    TEST_SIZE="${NLP_TEST_SIZE:-0.2}"
    VALIDATION_SIZE="${NLP_VALIDATION_SIZE:-0.1}"
    RANDOM_STATE="${NLP_RANDOM_STATE:-42}"

    if [ ! -f "$INPUT_PATH" ]; then
        echo "PREPARE_DATA_ON_START is true, but input file not found: $INPUT_PATH"
        exit 1
    fi

    PREPARE_ARGS=(
        --input "$INPUT_PATH"
        --output-dir "$OUTPUT_DIR"
        --text-column "$TEXT_COLUMN"
        --label-column "$LABEL_COLUMN"
        --split-mode "$SPLIT_MODE"
        --test-size "$TEST_SIZE"
        --validation-size "$VALIDATION_SIZE"
        --random-state "$RANDOM_STATE"
    )

    if [ "${NLP_LOWERCASE_TEXT:-false}" = "true" ]; then
        PREPARE_ARGS+=(--lowercase-text)
    fi
    if [ "${NLP_NO_STRATIFY:-false}" = "true" ]; then
        PREPARE_ARGS+=(--no-stratify)
    fi
    if [ "${NLP_KEEP_DUPLICATES:-false}" = "true" ]; then
        PREPARE_ARGS+=(--keep-duplicates)
    fi
    if [ "${NLP_AUTO_LABEL:-false}" = "true" ]; then
        PREPARE_ARGS+=(--auto-label)
    fi
    if [ "${NLP_ALLOW_CUSTOM_LABELS:-false}" = "true" ]; then
        PREPARE_ARGS+=(--allow-custom-labels)
    fi

    echo "Preparing NLP dataset from: $INPUT_PATH"
    python -m app.nlp.scripts.prepare_data "${PREPARE_ARGS[@]}"
fi

echo "Starting application..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
