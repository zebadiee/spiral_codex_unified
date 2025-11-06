.PHONY: help venv install run test-ledger ingest telemetry-tail telemetry-test test-rag lessons health reflect digest mcp-spiral mcp-client mcp-setup

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PORT := 8000

help:
	@echo "Commands: venv install run test-ledger ingest telemetry-tail telemetry-test test-rag lessons health reflect digest mcp-spiral mcp-client mcp-setup"

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

test-rag:
	@echo "🔍 Testing RAG (Retrieval-Augmented Generation)..."
	@$(BIN)/python test_rag.py
	@echo "\n--- RAG database ---"
	@sqlite3 data/embeddings.sqlite "SELECT COUNT(*) as snippets FROM embeddings" 2>/dev/null || echo "No DB yet"

lessons:
	@echo "🧠 Extracting lessons from trials..."
	@$(BIN)/python tools/summarize_trials.py --hours 24
	@echo "\n--- Recent lessons ---"
	@tail -n 5 data/omai_lessons.jsonl 2>/dev/null || echo "No lessons yet"

health:
	@echo "🏥 System Health Check"
	@echo "\n📊 Trial Summary (24h):"
	@$(BIN)/python -c "from utils.trials import trial_summary; import json; print(json.dumps(trial_summary(24), indent=2))" 2>/dev/null || echo "No trials logged"
	@echo "\n📈 Telemetry (last 10):"
	@tail -n 10 logs/wean.csv 2>/dev/null || echo "No telemetry"
	@echo "\n🧠 OMAi Bridge:"
	@$(BIN)/python -c "from utils.omai_bridge import available; print('✅ ONLINE' if available() else '❌ OFFLINE')" 2>/dev/null

reflect:
	@echo "🌀 Running reflection cycle..."
	@$(BIN)/python tools/reflect_cycle.py

digest:
	@echo "📊 Generating curator daily digest..."
	@$(BIN)/python tools/curator_digest.py
	@echo "\n--- Latest Digest ---"
	@head -n 25 data/reports/digest_$$(date +%Y-%m-%d).md 2>/dev/null || echo "No digest yet"

mcp-spiral:
	@echo "🚀 Starting Spiral MCP server on :7020"
	@$(BIN)/uvicorn mcp_server:app --host 127.0.0.1 --port 7020 --reload

mcp-client:
	@echo "🔧 MCP Client operations"
	@$(BIN)/python mcp_client.py list

mcp-setup:
	@echo "⚙️ Setting up MCP configuration..."
	@mkdir -p ~/.config/mcp
	@echo "servers:" > ~/.config/mcp/servers.yaml
	@echo "  - id: spiral" >> ~/.config/mcp/servers.yaml
	@echo "    url: http://127.0.0.1:7020" >> ~/.config/mcp/servers.yaml
	@echo "  - id: omai" >> ~/.config/mcp/servers.yaml
	@echo "    url: http://127.0.0.1:7018" >> ~/.config/mcp/servers.yaml
	@echo "✅ MCP config created at ~/.config/mcp/servers.yaml"
