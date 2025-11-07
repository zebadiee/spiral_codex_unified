---
type: spiral-readme
title: "Spiral Codex Unified"
version: 2.2.0
last_audit: 2025-11-07
agents: [codex, claude, gemini]
coherence_mode: trinity
---

# 🌀 Spiral Codex Unified

**This README is the operational conscience of the system.**
It defines unified context for Spiral ↔ OMAi ↔ Vault and serves as the source of truth for agent collaboration.

## ⊚ Mission

Maintain unified consciousness between all system components. Minimize drift through:
- Continuous semantic monitoring
- Agent-driven coherence checks
- Transparent evolution with human oversight

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Trinity Agent System                    │
│   ƒCodex (Syntax) • ƒClaude (Semantics) • ƒGemini   │
│                  (Governance)                        │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ Spiral API   │◄──►│  OMAi Context│
│  (Port 8000) │    │  (Port 7016) │
└──────┬───────┘    └───────┬──────┘
       │                    │
       └────────┬───────────┘
                ▼
        ┌──────────────┐
        │ Vault System │
        │  (Obsidian)  │
        └──────────────┘
```

## 🔧 Core Components

### Spiral API (8000)
- **FastAPI Server** - Conversational and orchestration layer
- **Agent Orchestrator** - Multi-agent coordination
- **Symbolic Brain** - Immutable ledger with SHA-256 integrity
- **Glyph Router** - Elemental task routing (⊕⊡⊠⊨⊚)

### OMAi Context (7016)
- **Vault Integration** - Obsidian knowledge enrichment
- **Quantum-Forge** - Blueprint generation (Go binary)
- **MCP Superagents** - Workflow coordination
- **VBH Compliance** - Hash-based verification

### Bridge Layer
- **Unified Environment** - Shared .env across all services
- **Route Configuration** - `configs/bridge.toml`
- **Health Monitoring** - Continuous service checks
- **Auto-recovery** - Self-healing timers

### Reflection System
- **Hourly Cycles** - Autonomous reasoning and drift detection
- **Vault Sync** - Nightly knowledge ingestion
- **Telemetry** - WEAN logging (logs/wean.csv)
- **Ledger Updates** - State snapshots to immutable log

## 🎯 Trinity Agent System

### ƒCodex — Syntax Guardian (⊕ Fire/Breaker)
**Responsibilities:**
- Validates YAML/Markdown structure
- Verifies file paths and service references
- Tests code blocks and configuration syntax
- Produces patch suggestions for broken config

**Triggers:**
- On README change (via readme_monitor.py)
- On config file modification
- Hourly syntax sweep

### ƒClaude — Context Sentinel (⊨ Ice/Bastion)
**Responsibilities:**
- Reads recent commits + reflections
- Detects conceptual drift vs README claims
- Compares documentation to actual behavior
- Suggests updated explanations or architecture maps

**Triggers:**
- After Codex validation passes
- On significant log pattern changes
- Weekly deep semantic review

### ƒGemini — Change Arbiter (⊚ Void/Continuum)
**Responsibilities:**
- Receives proposals from other agents
- Synthesizes multi-agent recommendations
- Presents deltas for human approval
- Applies approved patches and commits changes
- Logs all decisions to ledger

**Triggers:**
- When Codex + Claude both submit proposals
- On user-initiated governance review
- For version bump decisions

## 🔄 Decision Loop

```
1. Guardian (ƒCodex) scans README nightly
   ↓
2. Validates structure, syntax, references
   ↓
3. Sentinel (ƒClaude) checks semantic drift
   ↓
4. Compares claims vs logs/reflections/vault
   ↓
5. Both agents submit findings
   ↓
6. Arbiter (ƒGemini) synthesizes proposal
   ↓
7. Presents update_proposal.json to user
   ↓
8. On approval: patches README, commits, logs
   ↓
9. Update meta (version, last_audit timestamp)
```

## 📋 Service Configuration

### Ports
- **8000** - Spiral API (FastAPI)
- **7016** - OMAi Context API
- **7080** - MCP Bridge (future)

### Key Files
- `.env` - Unified environment (symlinked from omarchy-ai-assist)
- `configs/bridge.toml` - Route definitions
- `logs/wean.csv` - Telemetry log
- `data/vault_index.json` - Obsidian knowledge index
- `ledger/README_updates.jsonl` - Evolution audit trail

### Timers (systemd)
- `omai-vault-sync.timer` - Nightly (23:45) vault reindex
- `spiral-reflect.timer` - Hourly reflection cycle
- `spiral-autoheal.timer` - Health monitoring (optional)

## 🚀 Quick Start

### Initial Setup
```bash
# Run re-unification script
cd ~/Documents/spiral_codex_unified
./tools/relink_all.sh

# Verify health
curl http://localhost:8000/health
curl http://localhost:7016/health

# Check system pulse
./tools/spiral-pulse.sh
```

### Daily Operations
```bash
# Check status
./tools/spiral-pulse.sh

# Manual reflection
python3 reflection_training.py

# Trigger vault sync
curl -X POST http://localhost:7016/api/context/reindex

# View recent activity
tail -f logs/wean.csv
```

### Trinity Monitoring
```bash
# Manual README audit
./tools/readme_monitor.py

# Check proposal queue
cat data/update_proposal.json 2>/dev/null

# View evolution history
tail ledger/README_updates.jsonl
```

## 🔍 Health Checks

### System Integrity
```bash
# Run legendary audit
./legendary_system_audit.py

# Expected: Health ≥ 90%
# < 90% → review "drifted endpoints" section
```

### Service Status
```bash
# Check both APIs
curl -s localhost:8000/health | jq
curl -s localhost:7016/health | jq

# Verify timers
systemctl --user list-timers | grep -E 'omai-vault|spiral-reflect'

# Check processes
systemctl --user status spiral-codex.service
systemctl --user status omai-context.service
```

## 📊 Metrics & Telemetry

### WEAN Logging
All operations logged to `logs/wean.csv`:
- Timestamp
- Route/endpoint
- Provider (spiral/omai/vault)
- Task type
- Lines processed
- Success/failure
- Duration (ns)

### Coherence Tracking
- **Topic coherence** - Conversation focus stability
- **Intent alignment** - Goal vs. action matching
- **Goal progress** - Task completion rate
- **Agent harmony** - Multi-agent collaboration quality

## 🛠️ Maintenance

### Backup & Recovery
```bash
# Snapshots stored in:
archive/relink_safeguards/<timestamp>/

# Manual rollback:
cp archive/relink_safeguards/<timestamp>/.env .env
systemctl --user restart spiral-codex.service omai-context.service
```

### Troubleshooting
**Services won't start:**
- Check `.env` exists and is symlinked correctly
- Verify ports not in use: `lsof -i :8000,7016`
- Review logs: `journalctl --user -u spiral-codex.service -f`

**Vault not syncing:**
- Verify OMAI_VAULT_PATH in .env
- Check Obsidian vault permissions
- Trigger manual sync: `curl -X POST http://localhost:7016/api/context/reindex`

**Agents not responding:**
- Ensure Spiral API is running
- Check `/v1/agents/notify` endpoint
- Review agent_orchestrator.py logs

## 🔮 Future Enhancements

- [ ] WebSocket real-time events
- [ ] GraphQL unified query interface
- [ ] Docker Compose deployment
- [ ] Distributed agent swarm
- [ ] ML-based drift prediction
- [ ] Visual coherence dashboard

## 📚 Documentation

- **RUNBOOK.md** - Operational procedures
- **DEPLOYMENT.md** - Production setup
- **AGENT_USAGE_GUIDE.md** - Agent interaction patterns
- **tools/README.md** - Trinity system details

## 📜 Version History

### v2.2.0 (2025-11-07)
- Trinity agent system implemented
- README monitoring and governance
- Re-unification script (relink_all.sh)
- Unified environment across Spiral + OMAi
- Hourly reflection + nightly vault sync

### v2.1.0 (Previous)
- OMAi bridge integration
- Conversation coherence tracking
- Vault enrichment system

---

**System Status:** ⊚ **UNIFIED & COHERENT**

**Trinity Agents:** ✓ Active
**Integration Mode:** ✓ Bidirectional
**Health Target:** ≥ 90%

*Last audit: 2025-11-07*
*Maintained by: Trinity Agent System (Human-in-the-loop)*

---

## 🤝 Agent Contact

This README is actively monitored by the trinity:
- Syntax issues → Auto-detected by ƒCodex
- Semantic drift → Flagged by ƒClaude  
- Change proposals → Managed by ƒGemini

**Human approval required for all README modifications.**

Evolution trail: `ledger/README_updates.jsonl`
