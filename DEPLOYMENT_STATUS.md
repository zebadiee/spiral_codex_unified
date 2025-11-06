# 🌀 Spiral Codex v2.0 - Deployment Status

**Date:** 2025-11-06  
**Build:** cbff571 + local changes

## ✅ Completed

1. **Session handoff saved** → `docs/HANDOFF_SESSION.md`
2. **Python environment** → `.venv/` created with dependencies
3. **Local config** → `.env.local` with wean strategy (40% local)
4. **Directory structure** → `data/`, `ledger/`, `logs/`
5. **Makefile** → Simplified working version
6. **Git commits** → 24 total, clean session handoff commit

## 🔄 In Progress

- **Ollama model** → qwen2.5:7b-instruct downloading (57% complete, ~5min)

## 📋 Next Steps (Once Ollama Ready)

```bash
# Start Ollama (if not running)
pgrep -f "ollama serve" || (ollama serve &)

# Start FastAPI
cd ~/Documents/spiral_codex_unified
make run &

# Smoke test endpoints
curl localhost:8000/health
curl -X POST localhost:8000/v1/brain/plan \
  -H 'content-type: application/json' \
  -d '{"goal":"Test wean policy","max_steps":2}'
```

## 🎯 Micro-Tasks Ready

1. **Ledger sink** - Add JSONL logging to `/v1/converse/run`
2. **Privacy filter** - Skip `#private` notes in OMAi ingest
3. **Wean telemetry** - Log provider + latency to `logs/wean.csv`
4. **RAG stub** - Inject top-k snippets if embeddings exist
5. **Makefile help** - Already working! Run `make help`

## 📊 System Specs

- **Python:** 3.x with venv
- **FastAPI port:** 8000
- **Ollama model:** qwen2.5:7b-instruct (7B parameters)
- **Wean strategy:** 40% local → 70% → 100% over time
- **Obsidian vault:** ~/Obsidian (configured)

