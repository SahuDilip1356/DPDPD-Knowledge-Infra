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

# Root compatibility image: always build the canonical deployable backend.
COPY deployments/dpdpa-backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy canonical source and reference content.
COPY deployments/dpdpa-backend/src /app/src
COPY deployments/dpdpa-backend/DPDPA_BIBLE.md /app/DPDPA_BIBLE.md

EXPOSE 8000

CMD uvicorn src.api.api_service:app --host 0.0.0.0 --port ${PORT:-8000}
