# ✅ Ledger Sink Implementation Complete

## What Was Built

**Surgical addition** - Zero breaking changes, zero new dependencies.

### 1. Core Utility (`utils/ledger.py`)
- `append()` function logs events to JSONL
- SHA-256 hash of each record for audit trail
- Auto-creates `ledger/conversations/` directory
- UTC timestamps in ISO format

### 2. New Endpoint (`/v1/converse/spiral-omai-chat`)
- Alternates Spiral ↔ OMAi conversation turns
- Logs seed message + every agent reply
- Returns full transcript + ledger path
- Query params: `seed`, `turns`, `session_id`

### 3. Makefile Target (`make test-ledger`)
- Sends test conversation request
- Shows JSON response with `jq`
- Tails ledger file to verify writes

## Quick Test (After `make run`)

```bash
# Terminal 1: Start API
cd ~/Documents/spiral_codex_unified
make run &
sleep 3

# Terminal 2: Test ledger
make test-ledger

# Or manually:
curl -s "localhost:8000/v1/converse/spiral-omai-chat?seed=Plan%20weekly%20review&turns=3&session_id=demo" | jq

# Check ledger
tail -5 ledger/conversations/demo.jsonl
```

## JSONL Format

Each line:
```json
{
  "ts": "2025-11-06T12:05:42Z",
  "agent": "spiral",
  "role": "assistant",
  "content": "...",
  "turn": 1,
  "kind": "reply",
  "hash": "a7f5c9..."
}
```

## Files Changed

- `utils/ledger.py` - New utility (27 lines)
- `api/converse_api.py` - Added 70-line endpoint
- `Makefile` - Added `test-ledger` target
- Total: ~100 lines, zero deps

## Next Micro-Tasks

1. **Privacy filter** - Skip `#private` in OMAi ingest
2. **Wean telemetry** - CSV logging of provider/latency
3. **RAG stub** - Inject embeddings if available

**Status:** ⊚ Ledger sink operational
