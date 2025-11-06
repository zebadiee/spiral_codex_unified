# Spiral Codex - Deployment Guide

## ⊚ Quick Start

The Spiral Codex Unified system is built and ready for deployment. Follow these steps to get it running.

---

## 1. Install Dependencies

Since this is Arch/Manjaro, use system packages:

```bash
cd ~/Documents/spiral_codex_unified

# Install Python packages via pacman
sudo pacman -S python-fastapi python-uvicorn python-pydantic \
               python-yaml python-httpx python-dotenv

# Verify installation
python3 -c "import fastapi, pydantic, yaml; print('✅ All imports OK')"
```

**Alternative: Virtual Environment** (if you prefer isolation)

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
make install  # if pip is available in venv
```

---

## 2. Test Components

### Test Agent System
```bash
python3 agent_orchestrator.py
```

Expected output:
```
🌌 Spiral Codex Agent System
Initialized: {'status': 'initialized', 'agent_count': 4, ...}
⊕ Codex Response: {...}
⊨ Claude Response: {...}
🔮 Collaboration Result: {...}
```

### Test Glyph Engine
```bash
python3 -c "
from kernel.glyph_engine import GlyphEngine
engine = GlyphEngine()
for g in engine.list_glyphs():
    print(f'{g[\"symbol\"]} {g[\"name\"]} → {g[\"agent\"]}')"
```

---

## 3. Run the API Server

### Option A: Using Makefile
```bash
make run
```

### Option B: Direct uvicorn
```bash
uvicorn fastapi_app:app --reload --port 8000
```

### Option C: Python script
```bash
python3 fastapi_app.py
```

Server will start at: **http://127.0.0.1:8000**

---

## 4. Test Endpoints

### Health Check
```bash
curl http://127.0.0.1:8000/health | jq
```

### System Info
```bash
curl http://127.0.0.1:8000/ | jq
```

### Brain API Health
```bash
curl http://127.0.0.1:8000/v1/brain/health | jq
```

### Planning Endpoint
```bash
curl -X POST http://127.0.0.1:8000/v1/brain/plan \
  -H 'content-type: application/json' \
  -d '{
    "goal": "Build FastAPI brain endpoint",
    "max_steps": 3,
    "context": {"env": "production"},
    "hints": ["use agents", "validate input"]
  }' | jq
```

### Inference Endpoint
```bash
curl -X POST http://127.0.0.1:8000/v1/brain/infer \
  -H 'content-type: application/json' \
  -d '{"task": "analyze code", "agent": "ƒCODEX"}' | jq
```

### Ledger Stats
```bash
curl http://127.0.0.1:8000/v1/brain/stats | jq
```

### OpenAPI Docs
Open in browser: **http://127.0.0.1:8000/docs**

---

## 5. Using the Agent System Programmatically

```python
from agent_orchestrator import AgentOrchestrator

# Initialize
orch = AgentOrchestrator()
orch.initialize_agents()

# Use Codex for code generation
result = orch.route_task({
    "task_type": "code_generation",
    "language": "python",
    "context": {"feature": "Add API authentication"}
})

# Use Claude for planning
plan = orch.route_task({
    "task_type": "planning",
    "depth": "comprehensive",
    "context": {"project": "Add user management"}
})

# Multi-agent collaboration
collab = orch.collaborate({
    "project": "Build recommendation engine",
    "complexity": "high",
    "entropy": 0.4
})
```

---

## 6. Development Workflow

### Run tests
```bash
make test
# or
python -m pytest tests/ -v
```

### Lock dependencies
```bash
make lock
```

### Clean cache
```bash
make clean
```

### View all make targets
```bash
make help
```

---

## 7. API Routes Reference

### Core Routes
- `GET /` - System status and glyph info
- `GET /health` - Health check

### Brain API (`/v1/brain`)
- `GET  /health` - Brain service health
- `POST /plan` - Multi-step planning
- `POST /infer` - Agent inference
- `GET  /ledger` - Get all ledger entries
- `GET  /ledger/{record_id}` - Get specific record
- `POST /record` - Add new glyph record
- `GET  /stats` - Ledger statistics

---

## 8. Agent Mapping

| Glyph | Agent | Element | Specialty |
|-------|-------|---------|-----------|
| ⊕ | ƒCODEX | Fire | Code synthesis & debugging |
| ⊨ | ƒCLAUDE | Ice | Strategic analysis & planning |
| ⊠ | ƒVIBE_KEEPER | Air | Entropy monitoring |
| ⊡ | ƒARCHIVIST | Water | Memory archival |
| ⊚ | - | Void | Continuum/Integration |

---

## 9. Environment Variables (Optional)

Create `.env` file:
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Logging
LOG_LEVEL=INFO

# Brain Configuration
BRAIN_LEDGER_PATH=codex_root/brain/codex_immutable_ledger.json
```

---

## 10. Production Deployment

### Using systemd service

Create `/etc/systemd/system/spiral-codex.service`:
```ini
[Unit]
Description=Spiral Codex Unified API
After=network.target

[Service]
Type=simple
User=zebadiee
WorkingDirectory=/home/zebadiee/Documents/spiral_codex_unified
ExecStart=/usr/bin/uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable spiral-codex
sudo systemctl start spiral-codex
sudo systemctl status spiral-codex
```

### Using Docker (if needed)

Create `Dockerfile`:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t spiral-codex .
docker run -p 8000:8000 spiral-codex
```

---

## 11. Troubleshooting

### Import errors
```bash
# Verify Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Check installed packages
pacman -Qi python-fastapi python-pydantic python-yaml
```

### Port already in use
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill it
sudo kill <PID>
```

### YAML import error
```bash
sudo pacman -S python-yaml
```

---

## 12. Next Steps

- **Add Authentication**: Implement JWT or API key auth
- **Database Integration**: Connect to PostgreSQL/MongoDB
- **Real Agent Integration**: Wire actual LLM APIs (OpenAI, Anthropic)
- **Monitoring**: Add Prometheus/Grafana metrics
- **Testing**: Expand test coverage
- **Documentation**: Generate API client libraries

---

**Status:** ⊚ System Ready for Deployment

Built with ƒCLAUDE (strategic planning) + ƒCODEX (implementation)
