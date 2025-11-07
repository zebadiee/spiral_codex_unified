#!/usr/bin/env python3
"""
SPIRAL CLI - Uses YOUR actual infrastructure
Calls Spiral API → Agents → OpenRouter (your config)
"""
import sys
import requests
import json

SPIRAL_API = "http://localhost:8000"

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

# Check Spiral is running
try:
    health = requests.get(f"{SPIRAL_API}/health", timeout=2).json()
    print(f"{GREEN}✓ Spiral API: {health.get('service', 'running')}{RESET}")
except:
    print(f"{RED}✗ Spiral API not running at {SPIRAL_API}{RESET}")
    print(f"{YELLOW}Start with: cd ~/Documents/spiral_codex_unified && make run{RESET}")
    sys.exit(1)

# Check available agents
try:
    agents = requests.get(f"{SPIRAL_API}/v1/converse/agents", timeout=2).json()
    print(f"{GREEN}✓ Agents: {', '.join([a['id'] for a in agents])}{RESET}")
except:
    print(f"{YELLOW}⚠ Could not get agent list{RESET}")

print(f"\n{CYAN}🌀 SPIRAL CLI - Connected to your infrastructure{RESET}")
print(f"{CYAN}Uses: Spiral API → Your Agents → OpenRouter (your config){RESET}\n")

def chat(message: str) -> dict:
    """Use Spiral's brain/plan endpoint with fallback"""
    providers = ["openrouter", "local"]  # Try OpenRouter first, then local fallback
    
    for provider in providers:
        try:
            response = requests.post(
                f"{SPIRAL_API}/v1/brain/plan",
                json={
                    "goal": message,
                    "max_steps": 1,
                    "provider": provider
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "provider": provider,
                    "data": data
                }
            else:
                print(f"{YELLOW}[{provider} failed: {response.status_code}]{RESET} ", end="", flush=True)
        except Exception as e:
            print(f"{YELLOW}[{provider} error]{RESET} ", end="", flush=True)
    
    return {"success": False, "error": "All providers failed"}

def extract_reply(data):
    """Extract the actual reply from Spiral response"""
    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if "steps" in first and len(first["steps"]) > 0:
            return first["steps"][0].get("action", str(first))
        return str(first)
    return str(data)

print(f"{GREEN}Ready Declan! (type 'quit' to exit){RESET}\n")

while True:
    try:
        msg = input(f"{CYAN}🌀 You:{RESET} ").strip()
        
        if not msg:
            continue
            
        if msg.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}👋 Goodbye Declan!{RESET}")
            break
        
        print(f"\n{GREEN}🤖 Spiral:{RESET} ", end="", flush=True)
        
        result = chat(msg)
        
        if result["success"]:
            reply = extract_reply(result["data"])
            print(f"[{result['provider']}] {reply}")
        else:
            print(f"{RED}Error: {result.get('error')}{RESET}")
        
        print()
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Goodbye Declan!{RESET}")
        break
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}\n")
