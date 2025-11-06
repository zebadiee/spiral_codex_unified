# Spiral Codex Unified - Production Makefile
# Build ID: SCU-2025-1106-R1

.PHONY: help venv install dev-install run run-prod test-agents test lint format clean lock docker-build docker-run docker-stop status

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PORT := 8000

help:
@echo "🌀 Spiral Codex Unified - Makefile Commands"
@echo ""
@echo "Setup & Installation:"
@echo "  make venv          Create virtual environment"
@echo "  make install       Install production dependencies"
@echo "  make dev-install   Install dev dependencies"
@echo ""
@echo "Running:"
@echo "  make run           Start FastAPI server (reload mode)"
@echo "  make run-prod      Start production server"
@echo "  make test-agents   Test agent orchestrator"
@echo ""
@echo "Testing & Quality:"
@echo "  make test          Run pytest suite"
@echo "  make lint          Run ruff linter"
@echo "  make format        Format code"
@echo ""
@echo "Docker:"
@echo "  make docker-build  Build Docker image"
@echo "  make docker-run    Run in Docker"
@echo "  make docker-stop   Stop Docker container"
@echo ""
@echo "Maintenance:"
@echo "  make lock          Freeze dependencies"
@echo "  make clean         Clean cache files"
@echo "  make status        Show system status"
@echo ""
@echo "⊚ Spiral Codex v1.0.0"

venv:
@echo "⊕ Creating virtual environment..."
$(PYTHON) -m venv $(VENV) --system-site-packages
@echo "✅ Activate: source $(VENV)/bin/activate"

install:
@echo "⊕ Installing dependencies..."
$(BIN)/pip install -r requirements.txt
@echo "✅ Installed"

dev-install: install
@echo "⊕ Installing dev dependencies..."
$(BIN)/pip install pytest black ruff mypy
@echo "✅ Dev installed"

run:
@echo "🚀 Starting API (reload, port $(PORT))..."
$(BIN)/uvicorn fastapi_app:app --reload --host 0.0.0.0 --port $(PORT)

run-prod:
@echo "🚀 Starting API (production)..."
$(BIN)/uvicorn fastapi_app:app --host 0.0.0.0 --port $(PORT) --workers 4

test-agents:
@echo "🧪 Testing agents..."
$(BIN)/python agent_orchestrator.py

test:
@echo "🧪 Running tests..."
$(BIN)/pytest tests/ -v

lint:
@echo "🔍 Linting..."
$(BIN)/ruff check . || true

format:
@echo "✨ Formatting..."
$(BIN)/black .
@echo "✅ Formatted"

lock:
@echo "🔒 Freezing dependencies..."
$(BIN)/pip freeze > requirements.lock
@echo "✅ Locked"

clean:
@echo "🧹 Cleaning..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
@echo "✅ Clean"

docker-build:
@echo "🐳 Building image..."
docker build -t spiral-codex:latest .
@echo "✅ Built: spiral-codex:latest"

docker-run:
@echo "🐳 Running container..."
docker run -d --name spiral-codex -p $(PORT):8000 spiral-codex:latest
@echo "✅ Running at http://localhost:$(PORT)"

docker-stop:
@echo "🐳 Stopping..."
docker stop spiral-codex || true
docker rm spiral-codex || true
@echo "✅ Stopped"

status:
@echo "⊚ Spiral Codex - Status"
@echo "  Venv:   $$([ -d $(VENV) ] && echo '✅' || echo '❌')"
@echo "  Python: $$($(PYTHON) --version 2>&1)"
@echo "  Git:    $$(git log -1 --oneline 2>/dev/null || echo 'N/A')"
