FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
     build-essential \
     gcc \
     libpq-dev \
     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
     pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
     libpq-dev \
     curl \
     && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

RUN groupadd -r appuser && useradd -r -g appuser appuser

# Salin semua file dari komputer ke dalam folder /app di container
COPY . /app/

# Download dependensi NLTK
RUN python -m nltk.downloader stopwords punkt averaged_perceptron_tagger -d /usr/local/share/nltk_data

# PERBAIKAN: Otomatis ubah line ending Windows (CRLF) ke Linux (LF),
# berikan hak akses eksekusi, dan atur kepemilikan file ke appuser.
RUN sed -i 's/\r$//' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
     PYTHONUNBUFFERED=1 \
     PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
     CMD curl -f http://localhost:8000/api/health || exit 1

# GUNAKAN BARIS INI:
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]