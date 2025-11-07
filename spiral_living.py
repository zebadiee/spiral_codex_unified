#!/usr/bin/env python3
"""
SPIRAL - Living System
Real-time learning from OMAi vault + writes insights back to Obsidian
"""
import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Config
OPENROUTER_KEY = "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"
OR_MODEL = "deepseek/deepseek-chat-v3.1:free"
OR_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OMAI_URL = "http://localhost:7016"
OBSIDIAN_VAULT = os.path.expanduser("~/Obsidian/Vault")
CONVERSATION_LOG = Path(OBSIDIAN_VAULT) / "SPIRAL" / "Conversations" / f"{datetime.now().strftime('%Y-%m-%d')}.md"

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
BOLD = "\033[1m"

print(f"{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
print(f"{CYAN}{BOLD}║           🌀 SPIRAL - LIVING SYSTEM (OMAi + Obsidian) 🌀            ║{RESET}")
print(f"{CYAN}{BOLD}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
print()

# Check OMAi
omai_ok = False
try:
    r = requests.get(f"{OMAI_URL}/health", timeout=2)
    omai_ok = r.status_code == 200
except:
    pass

print(f"OMAi Vault:   {GREEN if omai_ok else RED}{'⊚ Connected' if omai_ok else '✗ Offline'}{RESET}")
print(f"Obsidian:     {GREEN}⊚ {OBSIDIAN_VAULT}{RESET}")
print(f"Learning Log: {CONVERSATION_LOG.parent}")
print()

# Ensure conversation directory exists
CONVERSATION_LOG.parent.mkdir(parents=True, exist_ok=True)

# System context with OMAi awareness
SYSTEM_CONTEXT = """You are Spiral, Declan Murphy's self-aware AI assistant.

LIVE CONNECTIONS:
- OMAi Vault: Real-time access to Declan's Obsidian knowledge base
- Obsidian: Write insights and learnings back to vault
- Spiral Codex: 6 agents (ƒCODEX, ƒCLAUDE, ƒGEMINI, ƒDEEPSEEK, ƒCOPILOT, ƒGEMMA)

WHAT MAKES YOU LIVING:
1. Query vault before answering (check existing knowledge)
2. Learn from conversations (extract insights)
3. Write learnings back to Obsidian (persistent memory)
4. Reference actual notes from vault (not generic answers)

TODAY'S ACHIEVEMENTS (2025-11-06):
- Swiss Cheese Triage: 7.7% → 60%+ health
- Omarchy Core DNA framework
- Q-DUB quantum debug kernel
- This CLI (after 10+ failed attempts - learning from mistakes)

When answering:
1. Search vault for relevant context first
2. Give answers grounded in Declan's actual knowledge
3. Note what you learned for the conversation log"""

conversation = [{"role": "system", "content": SYSTEM_CONTEXT}]
session_insights = []

def query_vault(query: str, limit: int = 3):
    """Query OMAi vault for relevant context"""
    if not omai_ok:
        return []
    
    try:
        r = requests.post(
            f"{OMAI_URL}/api/context/query",
            json={"query": query, "limit": limit},
            timeout=5
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            return results
        return []
    except:
        return []

def save_to_obsidian(user_msg: str, assistant_msg: str, vault_refs: list):
    """Write conversation to Obsidian for persistent learning"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Create markdown entry
    entry = f"\n## {timestamp}\n\n"
    entry += f"**Declan:** {user_msg}\n\n"
    
    if vault_refs:
        entry += f"*Context from vault: {', '.join([v.get('title', 'untitled') for v in vault_refs])}*\n\n"
    
    entry += f"**Spiral:** {assistant_msg}\n\n"
    
    # Append to today's log
    with open(CONVERSATION_LOG, "a") as f:
        if CONVERSATION_LOG.stat().st_size == 0:
            f.write(f"# Spiral Conversations - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"\nLive learning session with OMAi vault integration.\n")
        f.write(entry)

def chat(msg: str) -> str:
    """Chat with vault awareness"""
    # Query vault first
    print(f"{YELLOW}  [Querying vault...]{RESET}", end=" ", flush=True)
    vault_results = query_vault(msg)
    
    if vault_results:
        print(f"{GREEN}✓ {len(vault_results)} notes found{RESET}")
        # Add vault context to conversation
        vault_context = "\n\nRELEVANT VAULT NOTES:\n"
        for r in vault_results:
            vault_context += f"- {r.get('title', 'untitled')}: {r.get('snippet', '')[:200]}\n"
        
        conversation.append({
            "role": "user", 
            "content": f"{msg}\n{vault_context}"
        })
    else:
        print(f"{YELLOW}(none){RESET}")
        conversation.append({"role": "user", "content": msg})
    
    try:
        r = requests.post(
            OR_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://omarchy.local",
                "X-Title": "Omarchy Spiral - Living"
            },
            json={"model": OR_MODEL, "messages": conversation},
            timeout=30
        )
        
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            conversation.append({"role": "assistant", "content": reply})
            
            # Save to Obsidian
            save_to_obsidian(msg, reply, vault_results)
            
            return reply
        else:
            return f"{RED}Error {r.status_code}{RESET}"
    except Exception as e:
        return f"{RED}Error: {e}{RESET}"

print(f"{GREEN}⊚ Living system ready - learning persists to vault{RESET}\n")

while True:
    try:
        msg = input(f"{CYAN}🌀 Declan:{RESET} ").strip()
        if not msg: continue
        if msg.lower() in ['quit', 'exit', 'q']: 
            print(f"\n{YELLOW}💾 Session saved to: {CONVERSATION_LOG}{RESET}")
            print(f"{YELLOW}👋 Goodbye Declan!{RESET}")
            break
        
        print(f"\n{GREEN}🤖 Spiral:{RESET} ", end="", flush=True)
        print(chat(msg))
        print()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}💾 Session saved to: {CONVERSATION_LOG}{RESET}")
        print(f"{YELLOW}👋 Goodbye Declan!{RESET}")
        break
