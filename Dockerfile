# Spiral Codex Unified - Docker Image
# Version 2.1.0 - Local Intelligence Release
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    API_PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project structure
COPY . .

# Create necessary directories
RUN mkdir -p \
    logs \
    codex_root/brain \
    ledger/conversations \
    ledger/reflections

# Set permissions
RUN chmod +x reflection_training.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run command
CMD ["python", "-m", "uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]