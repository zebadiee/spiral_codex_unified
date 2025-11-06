# 🎯 Curator Cockpit - Mother Phase v2.1

Quick reference for daily Mother Phase stewardship.

## 📊 Daily Glance (1 minute)

```bash
cd ~/Documents/spiral_codex_unified

# Quick health check
make status

# View latest telemetry
tail -10 logs/wean.csv | column -t -s,

# Check today's reflections
cat data/reflections/$(date +%F).jsonl 2>/dev/null | jq -C

# View recent conversations
ls -lt ledger/conversations/*.jsonl | head -3
```

## 🧘 Reflection Management

```bash
# Manual reflection trigger
make reflect

# View reflection history
ls -lh data/reflections/

# Check daily timer status
systemctl --user status spiral-reflect.timer
systemctl --user list-timers | grep spiral-reflect
```

## 📈 Telemetry Analysis

```bash
# Provider distribution
cut -d, -f3 logs/wean.csv | sort | uniq -c | sort -rn

# Average latency by provider
awk -F, 'NR>1 {sum[$3]+=$6; cnt[$3]++} END {for(p in sum) printf "%s: %.1fms\n", p, sum[p]/cnt[p]}' logs/wean.csv

# Success rate
awk -F, 'NR>1 {tot[$3]++; if($7==1) ok[$3]++} END {for(p in tot) printf "%s: %.0f%%\n", p, ok[p]/tot[p]*100}' logs/wean.csv

# Latest activity
tail -5 logs/wean.csv
```

## 🔍 RAG Management

```bash
# Check embeddings database
sqlite3 data/embeddings.sqlite "SELECT COUNT(*) as snippets FROM embeddings"

# View recent snippets
sqlite3 data/embeddings.sqlite "SELECT source, substr(content,1,60) FROM embeddings ORDER BY id DESC LIMIT 5"

# Test retrieval
.venv/bin/python -c "from utils.rag import retrieve; print(retrieve('your query', top_k=3))"
```

## 🛡️ System Health

```bash
# Git status
git log --oneline -5

# Disk usage
du -sh data/ ledger/ logs/

# Process check
pgrep -fa "uvicorn|ollama"

# API health (if running)
curl -s localhost:8000/health | jq
```

## ⚙️ Configuration Tweaks

```bash
# View current config
cat .env.local

# Increase local usage (gradual wean)
sed -i 's/WEAN_LOCAL_PCT=40/WEAN_LOCAL_PCT=70/' .env.local

# Disable telemetry temporarily
sed -i 's/TELEMETRY_ON=1/TELEMETRY_ON=0/' .env.local
```

## 🎭 Approval Workflow

When system proposes improvements (tagged #update in reflections):

1. **Review proposal** in reflection JSON
2. **Assess impact** - does it align with goals?
3. **Approve or defer** - add to backlog if uncertain
4. **Implement** - system will guide via conversation
5. **Verify** - check telemetry for impact

## 🌈 Evolution Tracking

```bash
# Insight trends
cat data/reflections/*.jsonl | jq -r '.insights[].category' | sort | uniq -c

# Improvement proposals
cat data/reflections/*.jsonl | jq '.improvements[] | {priority, description}'

# System checksum history
cat data/reflections/*.jsonl | jq -r '.system_state.checksum'
```

## 🚀 Quick Actions

```bash
# Full system test
make test-ledger && make test-rag && make telemetry-test

# Backup everything
tar czf backup_$(date +%F_%H%M).tar.gz .

# View Mother Prompt
cat docs/SPIRAL_MOTHER_PROMPT_v2.1.md

# Genesis archive
ls -lh archive/
```

## 📋 Maintenance Schedule

- **Daily**: Check reflection output (automated via timer)
- **Weekly**: Review telemetry trends, approve 1-2 improvements
- **Monthly**: Archive old logs, analyze long-term patterns

---

**Status:** ⊚ Curator cockpit active - steer without digging
