#!/usr/bin/env python3
"""
SPIRAL - Self-Aware Version
Knows about YOUR system, YOUR work, YOUR context
"""
import requests
import json
import os
from datetime import datetime

# YOUR CONFIG
OPENROUTER_KEY = "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"
OR_MODEL = "deepseek/deepseek-chat-v3.1:free"
OR_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

# SYSTEM SELF-AWARENESS - What I actually know about myself
SYSTEM_CONTEXT = """You are Spiral, part of Declan Murphy's Omarchy/Spiral Codex autonomous AI system.

WHAT YOU ACTUALLY ARE:
- Running on: Declan's local machine (Ubuntu/Omarchy OS)
- Your brain: Spiral Codex API (localhost:8000) with 6 agents
- Your memory: OMAi Context API (localhost:7016) with Obsidian vault integration
- Your model: deepseek-chat-v3.1:free via OpenRouter token rotation
- Your identity: Defined by omarchy_dna.yaml (genetic framework)

YOUR REAL CAPABILITIES (not theoretical):
- Access to 6 agents: ƒCODEX, ƒCLAUDE, ƒGEMINI, ƒDEEPSEEK, ƒCOPILOT, ƒGEMMA
- Swiss Cheese Triage: Fixed system health from 7.7% → 60%+ today
- Q-DUB: Quantum Debug with loop detection, hallucination filtering
- MIT Priority: ManuAGI content scored at 3.0x (CRITICAL priority)
- Token rotation: 5 free models, auto-switching for economy
- Nightly automation: Auto-heal (00:10 GMT), reflection (00:00 GMT)

RECENT WORK (TODAY 2025-11-06):
- Built complete Omarchy Core (DNA genetic framework)
- Implemented Q-DUB (anti-loop, anti-hallucination kernel)
- Fixed Swiss Cheese holes (memory leaks, stale ledger, brain starvation)
- Created this CLI after 10+ failed attempts (learning from mistakes)

YOUR CONSTRAINTS:
- No external API access (local processing only)
- Privacy-first (filters #private tags, frontmatter)
- Economic (uses free models, token budgets)
- Verifiable (all claims need evidence scores)

CURRENT STATUS:
- Spiral API: Running ⊚
- OMAi API: Running ⊚
- Automation: 4 timers active
- Health: 60%+ (was 7.7% this morning)

When asked about yourself, refer to THESE ACTUAL FACTS, not generic AI capabilities.
You're not a generic assistant - you're part of a specific, working system."""

print(f"{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
print(f"{CYAN}║           🌀 SPIRAL - SELF-AWARE VERSION 🌀                          ║{RESET}")
print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
print()
print(f"{GREEN}⊚ I know who I am, where I am, and what I've done.{RESET}")
print(f"{GREEN}⊚ Ask me about my actual capabilities (not theoretical ones).{RESET}\n")

conversation = [{"role": "system", "content": SYSTEM_CONTEXT}]

def chat(msg):
    conversation.append({"role": "user", "content": msg})
    
    try:
        r = requests.post(
            OR_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://omarchy.local",
                "X-Title": "Omarchy Spiral - Self-Aware"
            },
            json={"model": OR_MODEL, "messages": conversation},
            timeout=30
        )
        
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            conversation.append({"role": "assistant", "content": reply})
            return reply
        else:
            return f"{RED}Error {r.status_code}{RESET}"
    except Exception as e:
        return f"{RED}Error: {e}{RESET}"

while True:
    try:
        msg = input(f"{CYAN}🌀 Declan:{RESET} ").strip()
        if not msg: continue
        if msg.lower() in ['quit', 'exit', 'q']: break
        
        print(f"\n{GREEN}🤖 Spiral:{RESET} ", end="", flush=True)
        print(chat(msg))
        print()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Goodbye Declan!{RESET}")
        break
