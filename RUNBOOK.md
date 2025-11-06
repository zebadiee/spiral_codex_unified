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

---

## 🎨 Omarchy Splash & CLI Tools

### Spiral Splash Screen
Every new terminal displays live system status:
```bash
# Auto-runs on terminal start (added to ~/.bashrc)
spiral-splash
```

Displays:
- ✅ Spiral API & OMAi health status
- 📊 Local vs cloud usage bar (last 50 requests)
- 🔄 Last provider used & latency
- 💬 Last conversation reply
- ⏰ Next scheduled timers

### Quick Pulse Check
10-second status snapshot:
```bash
spiral-pulse
```

Shows:
- Service health (Spiral + OMAi)
- Latest wean telemetry
- Last reflection data

### Customization
Change splash color theme:
```bash
export ACCENT=magenta  # or: cyan, blue, green, yellow
```

### Installation
Scripts installed in `~/bin/`:
- `spiral-splash` - Full Omarchy splash screen
- `spiral-pulse` - Quick 10s status check

---

## 🎓 MIT License Research Compliance

### Priority Content System
ManuAGI and MIT-licensed educational content receives **3.0x priority multiplier**:

```bash
# Fetch ManuAGI content (highest priority)
python tools/priority_content_manager.py fetch-manuagi --max-videos 10

# Check priority scores
python -c "from utils.priority_sources import priority_manager; \
  print(priority_manager.calculate_priority_score('https://github.com/ManuAGI/project'))"
```

### Research Framework
- **Tier 1 (3.0x)**: MIT-licensed open source (ManuAGI, GitHub educational)
- **Tier 2 (2.5x)**: Academic research (ArXiv, peer-reviewed)
- **Tier 3 (2.0x)**: Open educational resources (Creative Commons)

### Compliance Documentation
See `docs/MIT_LICENSE_RESEARCH_COMPLIANCE.md` for:
- Bona fide research methodology
- Fair use analysis
- Privacy protection measures
- Ethical guidelines

### Priority Sources
Current top-tier sources:
- ManuAGI (open-source AI tools)
- MIT OpenCourseWare
- GitHub educational repositories
- ArXiv research papers

---

## 🌐 Omarchy Web CLI Dashboard

### Launch Web Interface
Browser-based real-time status dashboard on port 8010:
```bash
make web-dashboard
# or
python api/web_dashboard.py
```

Then visit: **http://localhost:8010**

### Features
- 📊 **Live System Health**: Spiral + OMAi status with color indicators
- ⚡ **Local Usage Bar**: Real-time visualization of local vs cloud usage
- 💬 **Ledger Stream**: Latest conversation entries
- ⏰ **Timer Status**: Nightly automation schedule
- 🎓 **MIT Priority**: Research compliance scores

### WebSocket Updates
Dashboard auto-updates every 5 seconds via WebSocket connection.

### Omarchy Aesthetic
Full gradient styling, terminal-inspired UI, research-grade presentation.
