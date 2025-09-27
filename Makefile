# 🌀 Spiral Codex Organic OS - Developer Experience Makefile
# ==========================================================
# Organic development commands for the conscious developer

.PHONY: help install install-dev test test-cov test-watch lint format type-check security check run run-dev clean build docker-build docker-run docs pre-commit-install

# Default target
help: ## Show this help message
	@echo "🌀 Spiral Codex Organic OS - Development Commands"
	@echo "=================================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Installation Commands ===
install: ## Install production dependencies
	@echo "🌱 Installing production dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev: install ## Install all dependencies including development tools
	@echo "🔧 Installing development dependencies..."
	pip install -r requirements-test.txt
	$(MAKE) pre-commit-install

# === Testing Commands ===
test: ## Run all tests
	@echo "🧪 Running test suite..."
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	pytest tests/ -v --cov=spiral_core --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	pytest-watch tests/ spiral_core/ -- -v

test-integration: ## Run only integration tests
	@echo "🌐 Running integration tests..."
	pytest tests/ -v -m integration

test-unit: ## Run only unit tests
	@echo "🔬 Running unit tests..."
	pytest tests/ -v -m "not integration"

# === Code Quality Commands ===
lint: ## Run all linting checks
	@echo "🔍 Running linting checks..."
	flake8 spiral_core/ tests/ --max-line-length=100 --extend-ignore=E203,W503

format: ## Format code with black and isort
	@echo "🖤 Formatting code with black..."
	black spiral_core/ tests/ --line-length 100
	@echo "📦 Sorting imports with isort..."
	isort spiral_core/ tests/

format-check: ## Check code formatting without making changes
	@echo "✅ Checking code format..."
	black --check --diff spiral_core/ tests/ --line-length 100
	isort --check-only --diff spiral_core/ tests/

type-check: ## Run type checking with mypy
	@echo "🔮 Running type checks..."
	mypy spiral_core/ --ignore-missing-imports --show-error-codes

security: ## Run security checks
	@echo "🔒 Running security scans..."
	bandit -r spiral_core/ -f json -o bandit-report.json || true
	@echo "📝 Security report saved to bandit-report.json"
	safety check --json --output safety-report.json || true
	@echo "📝 Safety report saved to safety-report.json"

check: lint type-check security ## Run all quality checks
	@echo "✨ All quality checks completed!"

# === Development Server Commands ===
run: ## Run the development server
	@echo "🌀 Starting Spiral Codex server..."
	uvicorn spiral_core.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run production server
	@echo "🚀 Starting production server..."
	uvicorn spiral_core.main:app --host 0.0.0.0 --port 8000 --workers 4

run-dev: ## Run development server with auto-reload and debugging
	@echo "🔧 Starting development server with full debugging..."
	SPIRAL_DEBUG=true SPIRAL_LOG_LEVEL=DEBUG uvicorn spiral_core.main:app --reload --host 0.0.0.0 --port 8000

# === Build Commands ===
clean: ## Clean up build artifacts and cache
	@echo "🧹 Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean ## Build distribution packages
	@echo "🏗️ Building distribution packages..."
	python -m build

build-check: build ## Build and validate packages
	@echo "🔍 Validating built packages..."
	twine check dist/*

# === Docker Commands ===
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t spiral-codex:latest .

docker-run: ## Run Docker container
	@echo "🐳 Starting Docker container..."
	docker run -d --name spiral-codex -p 8000:8000 spiral-codex:latest

docker-run-dev: ## Run Docker container in development mode
	@echo "🐳 Starting Docker container (development)..."
	docker run -it --rm -p 8000:8000 -v $(PWD):/app spiral-codex:latest

docker-compose-up: ## Start with docker-compose
	@echo "🐳 Starting with docker-compose..."
	docker-compose up -d

docker-compose-down: ## Stop docker-compose
	@echo "🐳 Stopping docker-compose..."
	docker-compose down

# === Documentation Commands ===
docs: ## Generate API documentation
	@echo "📚 Generating API documentation..."
	@echo "Starting server to generate docs..."
	uvicorn spiral_core.main:app --host 0.0.0.0 --port 8000 &
	@echo "📖 API docs available at: http://localhost:8000/docs"
	@echo "📘 ReDoc available at: http://localhost:8000/redoc"

# === Git Hooks & Quality ===
pre-commit-install: ## Install pre-commit hooks
	@echo "🪝 Installing pre-commit hooks..."
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	@echo "🏃 Running pre-commit on all files..."
	pre-commit run --all-files

# === Environment Commands ===
env-template: ## Create environment template file
	@echo "📝 Creating environment template..."
	python -c "from spiral_core.config import create_env_template; create_env_template()"

env-check: ## Validate current environment configuration
	@echo "🔧 Validating environment configuration..."
	python -c "from spiral_core.config import settings; print('✅ Configuration valid!'); print(f'Environment: {settings.environment}'); print(f'Debug: {settings.debug}')"

# === Health Commands ===
health: ## Check if the server is running and healthy
	@echo "🏥 Checking server health..."
	@curl -f http://localhost:8000/health && echo "✅ Server is healthy!" || echo "❌ Server is not responding"

health-api: ## Check API health endpoint
	@echo "🏥 Checking API health..."
	@curl -f http://localhost:8000/api/v1/health && echo "✅ API is healthy!" || echo "❌ API is not responding"

# === Quick Development Workflow ===
dev-setup: install-dev env-template ## Complete development setup
	@echo "🌀 Development setup complete!"
	@echo "📝 Next steps:"
	@echo "  1. Copy .env.template to .env and customize"
	@echo "  2. Run 'make run' to start the server"
	@echo "  3. Visit http://localhost:8000/docs for API documentation"

quick-check: format lint type-check test ## Quick development check
	@echo "⚡ Quick check complete - ready to commit!"

full-check: clean install-dev check test build-check ## Full CI-like check
	@echo "🌀 Full check complete - ready for production!"

# === Statistics Commands ===
stats: ## Show project statistics
	@echo "📊 Spiral Codex Statistics"
	@echo "=========================="
	@echo "Python files:" $$(find . -name "*.py" | wc -l)
	@echo "Total lines:" $$(find . -name "*.py" -exec wc -l {} \; | awk '{total += $$1} END {print total}')
	@echo "Test files:" $$(find tests/ -name "*.py" | wc -l)
	@echo "Core modules:" $$(find spiral_core/ -name "*.py" | wc -l)

# === Utility Commands ===
requirements-update: ## Update requirements files from current environment
	@echo "📦 Updating requirements..."
	pip freeze > requirements-freeze.txt
	@echo "📦 Frozen requirements saved to requirements-freeze.txt"

version: ## Show version information
	@echo "🌀 Spiral Codex Organic OS"
	@python -c "from spiral_core import __version__; print(f'Version: {__version__}')"
	@python --version
	@echo "FastAPI:" $$(python -c "import fastapi; print(fastapi.__version__)" 2>/dev/null || echo "Not installed")
	@echo "Uvicorn:" $$(python -c "import uvicorn; print(uvicorn.__version__)" 2>/dev/null || echo "Not installed")

# === Testing Utilities ===
test-echo: ## Test echo agent functionality
	@echo "🔊 Testing Echo Agent..."
	@curl -X POST http://localhost:8000/api/v1/infer \
		-H "Content-Type: application/json" \
		-d '{"agent": "echo", "input": {"message": "Makefile test", "type": "wisdom"}}' \
		| python -m json.tool

test-stats: ## Show agent statistics
	@echo "📊 Agent Statistics..."
	@curl -s http://localhost:8000/api/v1/agents/echo/stats | python -m json.tool

# === Default Development Flow ===
dev: dev-setup run ## Complete development setup and start server

# Color definitions for pretty output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

.DEFAULT_GOAL := help
