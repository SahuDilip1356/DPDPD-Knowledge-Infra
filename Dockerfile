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

# Copy source code and ingestion scripts
COPY src /app/src
COPY ingest_document.py run_mock_ingestion.py seed_supabase.py /app/

EXPOSE 8000

CMD ["uvicorn", "src.api.api_service:app", "--host", "0.0.0.0", "--port", "8000"]
