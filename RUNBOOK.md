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
