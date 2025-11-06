.PHONY: help venv install run test-ledger ingest telemetry-tail telemetry-test

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PORT := 8000

help:
	@echo "Commands: venv install run test-ledger ingest telemetry-tail telemetry-test"

venv:
	$(PYTHON) -m venv $(VENV) --system-site-packages

install:
	$(BIN)/pip install -q -r requirements.txt

run:
	$(BIN)/uvicorn fastapi_app:app --reload --port $(PORT)

test-ledger:
	@echo "Testing ledger sink..."
	@curl -s "localhost:8000/v1/converse/spiral-omai-chat?seed=Plan%20weekly%20review&turns=3&session_id=smoke_test" | jq -C
	@echo "\n--- Ledger tail ---"
	@tail -n 5 ledger/conversations/smoke_test.jsonl 2>/dev/null || echo "No ledger yet"

ingest:
	@echo "📥 Privacy-aware ingest"
	@$(BIN)/python omai_ingest.py
	@echo "✅ Check: codex_root/ingest_cache.json"

telemetry-tail:
	@echo "📊 Wean telemetry (Ctrl-C to stop)..."
	@mkdir -p logs; touch logs/wean.csv
	@tail -n +1 -f logs/wean.csv

telemetry-test:
	@echo "Testing telemetry with agent orchestrator..."
	@$(BIN)/python agent_orchestrator.py 2>&1 | tail -20
	@echo "\n--- Telemetry log ---"
	@tail -n 10 logs/wean.csv 2>/dev/null || echo "No telemetry logged yet"
