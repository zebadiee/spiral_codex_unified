# 🚀 Go-Live Checklist - Spiral Codex v1.0.0

**Status:** Production Ready  
**Date:** 2025-11-06

---

## ✅ Pre-Flight Checks

### 1. Dependencies Installed
```bash
python3 -c "import fastapi, pydantic, yaml, uvicorn; print('✓ OK')"
```
- [ ] All Python packages available
- [ ] No import errors

### 2. Agent Orchestrator
```bash
python3 agent_orchestrator.py
```
- [ ] All 4 agents load successfully
- [ ] No initialization errors
- [ ] Task routing works

### 3. API Health
```bash
python3 -c "from api.brain_api import router; from fastapi_app import app; print('✓')"
```
- [ ] FastAPI imports clean
- [ ] No module errors
- [ ] Routes registered

### 4. Glyph Engine
```bash
python3 -c "from kernel.glyph_engine import GlyphEngine; print(len(GlyphEngine().list_glyphs()))"
```
- [ ] 5 glyphs loaded
- [ ] Agent mappings present

---

## 🔧 Configuration

### Environment Setup
```bash
cp .env.example .env
# Edit .env with your settings
```
- [ ] .env file created
- [ ] API_PORT configured
- [ ] LOG_LEVEL set

### Lock Dependencies
```bash
pip freeze > requirements.lock
```
- [ ] requirements.lock generated
- [ ] Version pinning complete

---

## 🚀 Deployment Options

### Option A: Direct Run
```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```
- [ ] Server starts clean
- [ ] No port conflicts
- [ ] Logs show "Application startup complete"

### Option B: Makefile
```bash
make run
```
- [ ] Makefile commands work
- [ ] Server starts via make

### Option C: Docker
```bash
make docker-build
make docker-run
```
- [ ] Docker image builds
- [ ] Container runs
- [ ] Health checks pass

---

## ✅ Smoke Tests

### 1. Health Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/brain/health
```
- [ ] Root health returns 200
- [ ] Brain health returns 200
- [ ] JSON response valid

### 2. Brain Planning
```bash
curl -X POST http://localhost:8000/v1/brain/plan \
  -H 'content-type: application/json' \
  -d '{"goal":"Test endpoint","max_steps":3}'
```
- [ ] Planning endpoint works
- [ ] Returns BrainResponse
- [ ] Steps generated

### 3. Brain Inference
```bash
curl -X POST http://localhost:8000/v1/brain/infer \
  -H 'content-type: application/json' \
  -d '{"task":"test"}'
```
- [ ] Inference endpoint works
- [ ] Echo response received

### 4. OpenAPI Docs
```bash
curl http://localhost:8000/docs
```
- [ ] Swagger UI loads
- [ ] All endpoints visible
- [ ] Schemas rendered

---

## 🧪 Agent Tests

### Codex (Code Generation)
```bash
python3 - <<'PY'
from agent_orchestrator import AgentOrchestrator
result = AgentOrchestrator().route_task({
    "task_type": "code_generation",
    "language": "python"
})
print(f"✓ {result['agent']} | {result['status']}")
PY
```
- [ ] Codex responds
- [ ] Status: ready
- [ ] Glyph: ⊕

### Claude (Planning)
```bash
python3 - <<'PY'
from agent_orchestrator import AgentOrchestrator
result = AgentOrchestrator().route_task({
    "task_type": "planning",
    "context": {"test": "go-live"}
})
print(f"✓ {result['agent']} | {result['action']}")
PY
```
- [ ] Claude responds
- [ ] Action: strategic_planning
- [ ] Glyph: ⊨

### Multi-Agent Collaboration
```bash
python3 - <<'PY'
from agent_orchestrator import AgentOrchestrator
result = AgentOrchestrator().collaborate({
    "project": "Go-live validation",
    "entropy": 0.2
})
print(f"✓ {result['status']} | {len(result['steps'])} steps")
PY
```
- [ ] Collaboration works
- [ ] 3 agents participate
- [ ] Status: collaboration_complete

---

## 🐳 Docker Validation

### Build
```bash
docker build -t spiral-codex:latest .
```
- [ ] Build succeeds
- [ ] No layer errors
- [ ] Image created

### Run
```bash
docker run -d --name spiral-test -p 8001:8000 spiral-codex:latest
curl http://localhost:8001/health
docker stop spiral-test && docker rm spiral-test
```
- [ ] Container starts
- [ ] Health check passes
- [ ] Clean shutdown

### Compose
```bash
docker compose up -d
docker compose ps
curl http://localhost:8000/health
docker compose down
```
- [ ] Compose up works
- [ ] Services healthy
- [ ] Clean teardown

---

## 📊 Performance Checks

### Response Times
```bash
time curl http://localhost:8000/health
```
- [ ] < 100ms for health
- [ ] < 500ms for planning
- [ ] No timeouts

### Memory Usage
```bash
ps aux | grep uvicorn
```
- [ ] Reasonable memory usage
- [ ] No memory leaks visible

---

## 🔒 Security Checks

### API Keys (if configured)
- [ ] API_KEY set in .env
- [ ] Not committed to git
- [ ] Strong random value

### CORS Settings
- [ ] CORS configured for your domain
- [ ] No wildcard (*) in production
- [ ] Allowed origins specified

### Ports
- [ ] Firewall configured
- [ ] Only necessary ports open
- [ ] Localhost vs 0.0.0.0 decision made

---

## 📝 Documentation Verified

- [ ] README.md accurate
- [ ] QUICKSTART.md tested
- [ ] DEPLOYMENT.md followed
- [ ] AGENT_USAGE_GUIDE.md clear
- [ ] All examples work

---

## 🎯 Go-Live Decision

**All checks passed?** ✅

**Ready to deploy?** ✅

**Monitoring in place?** ⬜ (Optional)

**Backup plan?** ⬜ (Optional)

---

## 🚀 Launch Commands

### Development
```bash
cd ~/Documents/spiral_codex_unified
source .venv/bin/activate  # if using venv
make run
```

### Production (systemd)
```bash
sudo systemctl start spiral-codex
sudo systemctl status spiral-codex
```

### Production (Docker)
```bash
docker compose up -d
docker compose logs -f
```

---

## 📞 Post-Launch

### Monitor
```bash
# Logs
tail -f /var/log/spiral-codex.log  # if configured

# Docker
docker compose logs -f

# Direct
# Watch uvicorn output
```

### Test
```bash
# Run smoke test
./SMOKE_TEST.sh

# Check agents
python3 agent_orchestrator.py
```

### Validate
- [ ] Health endpoints responding
- [ ] Agents routing correctly
- [ ] No errors in logs
- [ ] Response times acceptable

---

## 🐛 Troubleshooting

### Port in use
```bash
lsof -i :8000
kill <PID>
```

### Import errors
```bash
pip install -r requirements.txt
python3 -c "import fastapi, pydantic, yaml"
```

### Agent not responding
```bash
python3 agent_orchestrator.py  # Check initialization
```

### Docker issues
```bash
docker logs spiral-codex-api
docker restart spiral-codex-api
```

---

**⊚ Spiral Codex v1.0.0 - Production Checklist**

*Last Updated: 2025-11-06*
