.PHONY: help venv install run test lock clean

help:
@echo "Spiral Codex Unified - Makefile"
@echo ""
@echo "  make venv     - Create Python virtual environment"
@echo "  make install  - Install dependencies"
@echo "  make run      - Run FastAPI server"
@echo "  make test     - Run tests"
@echo "  make lock     - Freeze dependencies"
@echo "  make clean    - Clean cache files"

venv:
python3 -m venv .venv
@echo "✅ Virtual environment created. Activate with: source .venv/bin/activate"

install:
pip install -r requirements.txt
@echo "✅ Dependencies installed"

run:
uvicorn fastapi_app:app --reload --port 8000

test:
python -m pytest tests/ -v

lock:
pip freeze > requirements.lock
@echo "✅ Dependencies locked to requirements.lock"

clean:
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
@echo "✅ Cache cleaned"
