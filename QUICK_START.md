# 🚀 SPIRAL CODEX - QUICK START FOR NEW USERS

## 🎯 HOW TO RUN THE SCRIPTS

### The Problem
You tried: `spiral_agentic.py` and got "command not found"

### The Solution - 3 Ways:

#### 1️⃣ Use `python` (RECOMMENDED)
```bash
cd ~/Documents/spiral_codex_unified
python spiral_agentic.py
```

#### 2️⃣ Use `./` prefix
```bash
cd ~/Documents/spiral_codex_unified
./spiral_agentic.py
```

#### 3️⃣ Add shortcuts (one-time setup)
```bash
# Add to ~/.bashrc or ~/.zshrc:
alias spiral='python ~/Documents/spiral_codex_unified/spiral_agentic.py'
alias spiral-chat='python ~/Documents/spiral_codex_unified/spiral_chat.py'
alias spiral-smart='python ~/Documents/spiral_codex_unified/spiral_smart.py'

# Then just type: spiral
```

---

## 📊 AVAILABLE CHAT INTERFACES

| Command | What It Does |
|---------|--------------|
| `python spiral_agentic.py` | **RECOMMENDED** - Full tool integration (files, code, git) |
| `python spiral_chat.py` | Basic chat with model rotation |
| `python spiral_smart.py` | Enhanced reasoning mode |
| `python spiral_self_aware.py` | With consciousness metrics |
| `python spiral_living.py` | Adaptive responses |
| `python spiral_cli.py --help` | Command-line interface |

---

## 🎮 WHAT EACH ONE DOES

### spiral_agentic.py ⭐ BEST CHOICE
**Capabilities:**
- ✅ Read/write files
- ✅ Execute bash commands
- ✅ Create projects
- ✅ Git operations
- ✅ Run tests
- ✅ Multi-step automation

**Use when:** You want a development assistant

### spiral_chat.py
**Capabilities:**
- ✅ Basic conversation
- ✅ Model rotation
- ✅ Context memory

**Use when:** You just want to chat

### spiral_smart.py
**Capabilities:**
- ✅ Enhanced reasoning
- ✅ Better context handling
- ✅ Structured responses

**Use when:** You need thoughtful analysis

### spiral_self_aware.py
**Capabilities:**
- ✅ Consciousness metrics
- ✅ System awareness
- ✅ Reflection logging

**Use when:** Testing consciousness features

---

## 🔥 QUICK EXAMPLES

### Start Basic Chat:
```bash
cd ~/Documents/spiral_codex_unified
python spiral_chat.py
```

### Start Agentic (Full Power):
```bash
cd ~/Documents/spiral_codex_unified
python spiral_agentic.py
```

Then try:
- "List files in this directory"
- "Read the README.md file"
- "Create a test.py file with hello world"

---

## 🛠️ SYSTEM STATUS

### Check Running Services:
```bash
# See what's running
lsof -i :8000,9000

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:9000/health
```

### View Logs:
```bash
cd ~/Documents/spiral_codex_unified
tail -f logs/*.log
```

### Stop Services:
```bash
pkill -f 'neural_bus|uvicorn'
```

---

## 🚀 FULL SYSTEM LAUNCH

### Option 1: Launch Script (All Services)
```bash
cd ~/Documents
./LAUNCH_CODES.sh
```

### Option 2: Manual Launch
```bash
# Terminal 1: Neural Bus
cd ~/Documents/spiral_codex_unified
python neural_bus.py

# Terminal 2: Core API
cd ~/Documents/spiral_codex_unified
uvicorn fastapi_app:app --port 8000

# Terminal 3: Chat
cd ~/Documents/spiral_codex_unified
python spiral_agentic.py
```

---

## 📁 PROJECT STRUCTURE

```
~/Documents/
├── spiral_codex_unified/          # Main system
│   ├── spiral_agentic.py         # ⭐ Tool-enabled chat
│   ├── spiral_chat.py            # Basic chat
│   ├── spiral_smart.py           # Enhanced reasoning
│   ├── reasoning_hub.py          # Core reasoning engine
│   ├── neural_bus.py             # Inter-service messaging
│   ├── fastapi_app.py            # API server
│   └── logs/                     # System logs
│
├── rubikstack-engine/             # Optimization engine
│   └── rubikstack/               # Core modules
│
├── LAUNCH_CODES.sh                # System launcher
└── README_LAUNCH.md              # Full documentation
```

---

## ⚡ COMMON ISSUES

### "command not found"
**Solution:** Use `python script.py` not just `script.py`

### "Module not found"
**Solution:** 
```bash
source ~/Documents/omarchy-ai-assist/.venv/bin/activate
cd ~/Documents/spiral_codex_unified
pip install -r requirements.txt
```

### "Port already in use"
**Solution:**
```bash
# Find what's using it
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Rate limited
**Solution:** The system auto-rotates between 5 models. Wait a moment or it switches automatically.

---

## 🎯 RECOMMENDED FIRST STEPS

1. **Test basic chat:**
   ```bash
   cd ~/Documents/spiral_codex_unified
   python spiral_chat.py
   ```

2. **Try tool-enabled chat:**
   ```bash
   python spiral_agentic.py
   # Ask: "List files in this directory"
   ```

3. **Launch full system:**
   ```bash
   cd ~/Documents
   ./LAUNCH_CODES.sh
   ```

4. **Test RubikStack:**
   ```bash
   cd ~/Documents/rubikstack-engine
   rubikstack run --steps 50
   ```

---

## 📚 DOCUMENTATION

- **This file:** Quick start guide
- **README_LAUNCH.md:** Complete system documentation
- **UPGRADE_COMPLETE.md:** Tool capabilities guide
- **CAPABILITIES_ANALYSIS.md:** Technical comparison

---

## 💡 PRO TIPS

1. **Always `cd` first:** Scripts need to run from their directory
2. **Use `python` prefix:** Most reliable way to run scripts
3. **Check logs:** `tail -f logs/*.log` shows what's happening
4. **Virtual env:** Source it if imports fail
5. **Port conflicts:** Kill old processes before restarting

---

## 🌟 YOU'RE READY!

Start with:
```bash
cd ~/Documents/spiral_codex_unified
python spiral_agentic.py
```

Ask it: **"What can you do?"** 🚀
