# Spiral × OMAi Runbook

## Health
- Spiral:  curl http://localhost:8000/health
- OMAi:    curl http://localhost:7016/health

## Day-to-day (Curator)
- tail -20 logs/wean.csv | column -t -s,
- cat data/reflections/$(date +%F).jsonl | jq

## Tools
- Plan:       POST /v1/brain/plan {"goal":"...", "max_steps":2}
- Agents:     GET  /v1/converse/agents
- Collaborate POST /v1/converse/collaborate {"task":"...", "agents":[...]}
- Converse:   GET  /v1/converse/run?seed=...&turns=2&session_id=...

## OMAi Vault Enrichment
- Query:  POST /api/context/query {"query":"...", "limit":5}
- Reindex:POST /api/context/reindex

## Services
- Start/stop (user): systemctl --user status|restart omai-context.service spiral-codex.service
- Reflection timer:  systemctl --user list-timers | grep spiral-reflect

## Logs
- Telemetry: logs/wean.csv
- Ledger:    ledger/conversations/*.jsonl
- Ingest:    logs/ingest_trials.jsonl (trials & errors)

## Notes
- Respect privacy filters (#private, frontmatter private: true)
- Provenance required for external content

---

## 🧠 Learning Infrastructure

### Automated Data Collection
Every fetch/ingest attempt is logged to `logs/ingest_trials.jsonl` for training:
```bash
# View recent trials
tail -20 logs/ingest_trials.jsonl | jq '.url, .status, .error'

# Analyze failure patterns
jq 'select(.status == "failed")' logs/ingest_trials.jsonl | jq -s 'group_by(.error) | map({error: .[0].error, count: length})'
```

### Nightly Vault Reindex
OMAi vault auto-reindexes at **23:45** daily (before Spiral's midnight reflection):
```bash
# Check timer status
systemctl --user list-timers | grep omai-reindex

# Manual trigger
systemctl --user start spiral-omai-reindex.service

# View reindex logs
tail -50 logs/omai_reindex.log
```

### Training Workflow
1. **Collect** - Fetchers auto-log trials to `ingest_trials.jsonl`
2. **Reflect** - Midnight reflection analyzes patterns in `data/reflections/`
3. **Improve** - Failure classifier learns from `ok=0` entries in `wean.csv`
4. **Optimize** - WEAN telemetry tracks provider performance over time

### Custom Fetcher Integration
```python
from fetchers.base_with_logging import LoggingFetcher

fetcher = LoggingFetcher(timeout=15)
result = fetcher.fetch("https://example.com", provenance="my_workflow")
# Automatically logs to ingest_trials.jsonl
```
