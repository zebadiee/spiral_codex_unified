.PHONY: help venv install run test-ledger

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PORT := 8000

help:
	@echo "Quick commands: venv install run test-ledger"

venv:
	$(PYTHON) -m venv $(VENV) --system-site-packages

install:
	$(BIN)/pip install -q -r requirements.txt

run:
	$(BIN)/uvicorn fastapi_app:app --reload --port $(PORT)

test-ledger:
	@echo "Testing ledger sink..."
	@curl -s "localhost:8000/v1/converse/spiral-omai-chat?seed=Plan%20weekly%20review&turns=3&session_id=smoke_test" | jq
	@echo "\n--- Ledger tail ---"
	@tail -n 5 ledger/conversations/smoke_test.jsonl
