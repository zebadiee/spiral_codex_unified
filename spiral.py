#!/usr/bin/env python3
"""
SPIRAL - The One True Chat
Online → Local fallback | Auto-logs to Obsidian | Multi-agent | Tools
"""
import requests, json, re, subprocess, os
from pathlib import Path
from datetime import datetime

# ===== CONFIG =====
OPENROUTER_KEY = "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"
MODELS = ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.2-3b-instruct:free", "microsoft/phi-3-mini-128k-instruct:free"]
OLLAMA_MODEL = "llama3.1:8b"
OBSIDIAN = Path.home() / "Documents/Obsidian/OMAi/Spiral"

# Colors
C, G, Y, R, M, BOLD, X = "\033[36m", "\033[32m", "\033[33m", "\033[31m", "\033[35m", "\033[1m", "\033[0m"

# ===== SETUP =====
OBSIDIAN.mkdir(parents=True, exist_ok=True)
SESSION = OBSIDIAN / f"{datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
SESSION.write_text(f"# Spiral Session\n{datetime.now()}\n\n")

conversation, stats = [], {"online": 0, "local": 0, "files": 0}
current_model = 0

# ===== CORE FUNCTIONS =====
def log(user, ai, agent):
    """Log to Obsidian"""
    SESSION.write_text(SESSION.read_text() + f"\n### {datetime.now().strftime('%H:%M')} - {agent}\n**You:** {user}\n**Spiral:** {ai}\n\n")

def call_online(msgs):
    """Try online models"""
    global current_model, stats
    for _ in range(len(MODELS)):
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={"model": MODELS[current_model], "messages": msgs, "max_tokens": 2000}, timeout=30)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"].strip()
                if content:
                    stats["online"] += 1
                    return content, "online"
        except: pass
        current_model = (current_model + 1) % len(MODELS)
    return None, None

def call_local(msgs):
    """Fallback to Ollama"""
    global stats
    try:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in msgs])
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=60)
        if r.status_code == 200:
            stats["local"] += 1
            return r.json().get("response", ""), "local"
    except: pass
    return "", "failed"

def detect_agent(msg):
    """Detect which agent to use"""
    m = msg.lower()
    if any(w in m for w in ['deploy', 'docker', 'kubernetes']): return "🚀 DevOps"
    if any(w in m for w in ['code', 'function', 'write']): return "💻 Coder"
    if any(w in m for w in ['error', 'bug', 'fix']): return "🔧 Debug"
    return "💬 Chat"

def create_file(filename, content):
    """Create file"""
    global stats
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    Path(filename).write_text(content)
    stats["files"] += 1
    return f"✅ Created {filename}"

def read_file(filename):
    """Read file"""
    return Path(filename).read_text()[:500]

def run_bash(cmd):
    """Execute command"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout[:500]

# ===== MAIN =====
print(f"{BOLD}{C}╔════════════════════════════════════════════════╗{X}")
print(f"{BOLD}{C}║  🌀 SPIRAL - One Chat Does It All            ║{X}")
print(f"{BOLD}{C}╚════════════════════════════════════════════════╝{X}\n")
print(f"{G}✅ Online: 3 models | ✅ Local: Ollama | ✅ Obsidian: {SESSION.name}{X}\n")

while True:
    try:
        user_input = input(f"{C}You: {X}").strip()
        if not user_input or user_input.lower() in ['quit', 'exit', 'q']: break
        
        # Detect agent
        agent = detect_agent(user_input)
        print(f"{M}{agent}{X}")
        
        # Handle file creation
        if 'create' in user_input.lower() and 'file' in user_input.lower():
            match = re.search(r'(\w+\.\w+)', user_input)
            if match:
                filename = match.group(1)
                # Generate code
                msgs = [{"role": "system", "content": "Generate clean code. Use ```python blocks."},
                        {"role": "user", "content": user_input}]
                response, source = call_online(msgs) or call_local(msgs)
                
                # Extract code
                code_match = re.search(r'```(?:python)?\n(.*?)```', response, re.DOTALL)
                if code_match:
                    result = create_file(filename, code_match.group(1))
                    print(f"{G}Spiral: {result}{X}\n")
                    log(user_input, result, agent)
                    continue
        
        # Handle file reading
        if 'read' in user_input.lower():
            match = re.search(r'(\w+\.\w+)', user_input)
            if match:
                result = read_file(match.group(1))
                print(f"{G}Spiral: {result}{X}\n")
                continue
        
        # Regular chat
        msgs = [{"role": "system", "content": "You are Spiral. Be helpful and concise."}]
        msgs.extend(conversation[-5:])
        msgs.append({"role": "user", "content": user_input})
        
        response, source = call_online(msgs)
        if not response:
            print(f"{Y}⚠️ Using local Ollama...{X}")
            response, source = call_local(msgs)
        
        if response:
            conversation.append({"role": "user", "content": user_input})
            conversation.append({"role": "assistant", "content": response})
            print(f"{G}Spiral: {response}{X}\n")
            log(user_input, response, agent)
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"{R}Error: {e}{X}\n")

# Session summary
SESSION.write_text(SESSION.read_text() + f"\n---\n**Stats:** Online: {stats['online']} | Local: {stats['local']} | Files: {stats['files']}\n")
print(f"\n{Y}Session saved: {SESSION}{X}")
