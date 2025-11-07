#!/usr/bin/env python3
"""
🌀 SPIRAL CHAT - Uses YOUR OMAi System (Already Configured!)
"""
import requests
import os
import sys
from datetime import datetime

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"

print(f"{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
print(f"{CYAN}{BOLD}║        🌀 SPIRAL CHAT - Using Your OMAi System 🌀                   ║{RESET}")
print(f"{CYAN}{BOLD}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
print()
print(f"{GREEN}✓ No API keys needed - uses your existing OMAi setup{RESET}")
print()

SPIRAL_URL = "http://localhost:8000"
conversation = []
session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def chat_via_spiral(message: str) -> str:
    """Chat using Spiral's converse API"""
    try:
        response = requests.get(
            f"{SPIRAL_URL}/v1/converse/run",
            params={
                "seed": message,
                "turns": 1,
                "session_id": session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract reply from response
            if isinstance(data, list) and len(data) > 0:
                return data[0].get('content', str(data[0]))
            elif isinstance(data, dict):
                return data.get('reply', data.get('content', str(data)))
            return str(data)
        else:
            return f"{RED}Error: {response.status_code}{RESET}"
    except requests.exceptions.ConnectionError:
        return f"{RED}❌ Can't connect to Spiral API (localhost:8000)\nIs it running? Try: make run{RESET}"
    except Exception as e:
        return f"{RED}❌ Error: {e}{RESET}"

# Check if Spiral is running
try:
    r = requests.get(f"{SPIRAL_URL}/health", timeout=2)
    if r.status_code != 200:
        print(f"{RED}❌ Spiral API not healthy{RESET}")
        sys.exit(1)
except:
    print(f"{RED}❌ Spiral API not running at {SPIRAL_URL}{RESET}")
    print(f"{YELLOW}Start it with: cd ~/Documents/spiral_codex_unified && make run{RESET}")
    sys.exit(1)

print(f"{GREEN}⊚ Ready Declan! I'm Spiral.{RESET}\n")

while True:
    try:
        user_input = input(f"{CYAN}🌀 You:{RESET} ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}👋 Goodbye Declan!{RESET}")
            break
        
        if user_input.lower() == 'clear':
            conversation.clear()
            print(f"{YELLOW}🔄 Conversation cleared{RESET}\n")
            continue
        
        print(f"\n{GREEN}�� Spiral:{RESET} ", end="", flush=True)
        response = chat_via_spiral(user_input)
        print(response)
        print()
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Goodbye Declan!{RESET}")
        break
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}\n")
