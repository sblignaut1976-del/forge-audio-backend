FROM python:3.11-slim

WORKDIR /code

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and migration files
COPY ./app /code/app
COPY ./migrations /code/migrations
COPY alembic.ini /code/alembic.ini

# Expose port (Railway will override this with $PORT)
EXPOSE 8000

# Run application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
