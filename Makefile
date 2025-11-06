.PHONY: help venv install run

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PORT := 8000

help:
	@echo "Quick commands: make venv install run"

venv:
	$(PYTHON) -m venv $(VENV) --system-site-packages

install:
	$(BIN)/pip install -q -r requirements.txt

run:
	$(BIN)/uvicorn fastapi_app:app --reload --port $(PORT)
