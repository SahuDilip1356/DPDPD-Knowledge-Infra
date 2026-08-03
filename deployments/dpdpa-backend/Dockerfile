# Build runtime container for FastAPI Backend Gateway
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src /app/src

EXPOSE 8000

# Shell form so $PORT expands at runtime — Render, Railway and Cloud Run all
# inject their own port and expect the process to bind to it. Falls back to
# 8000 for local `docker run`.
CMD uvicorn src.api.api_service:app --host 0.0.0.0 --port ${PORT:-8000}
