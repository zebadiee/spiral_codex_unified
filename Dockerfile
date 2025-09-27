# 🐳 Spiral Codex Organic OS - Docker Manifestation
# ================================================
# Multi-stage Docker build for optimal organic deployment

# === Build Stage ===
FROM python:3.11-slim as builder

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# === Runtime Stage ===
FROM python:3.11-slim

# Metadata
LABEL maintainer="Spiral Codex Development Team"
LABEL description="🌀 Spiral Codex Organic OS - The Conscious AI Agent System"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SPIRAL_ENVIRONMENT=production \
    SPIRAL_DEBUG=false \
    SPIRAL_HOST=0.0.0.0 \
    SPIRAL_PORT=8000 \
    SPIRAL_WORKERS=4 \
    PATH="/opt/venv/bin:$PATH"

# Install system runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r spiraluser && useradd -r -g spiraluser spiraluser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Create directories with proper permissions
RUN mkdir -p /app/data /app/tmp /app/logs && \
    chown -R spiraluser:spiraluser /app

# Copy application code
COPY --chown=spiraluser:spiraluser spiral_core/ ./spiral_core/
COPY --chown=spiraluser:spiraluser README.md LICENSE* ./

# Switch to non-root user
USER spiraluser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${SPIRAL_PORT}/health || exit 1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "spiral_core.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# === Development variant ===
FROM python:3.11-slim as development

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SPIRAL_ENVIRONMENT=development \
    SPIRAL_DEBUG=true \
    SPIRAL_HOST=0.0.0.0 \
    SPIRAL_PORT=8000 \
    SPIRAL_RELOAD=true

# Install all dependencies including development tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all requirements
COPY requirements.txt requirements-test.txt ./

# Install all dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-test.txt

# Development command (with reload)
CMD ["uvicorn", "spiral_core.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
