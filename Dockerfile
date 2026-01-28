# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /code

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies including a forced CPU-only torch to save massive space
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /code

# Install runtime dependencies (ffmpeg is essential)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ./app /code/app
COPY ./migrations /code/migrations
COPY alembic.ini /code/alembic.ini

# Create directories and non-root user
RUN mkdir -p /code/uploads /code/stems && \
    adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /code

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
