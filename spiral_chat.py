#!/usr/bin/env python3
"""
SPIRAL CHAT - Uses YOUR actual OpenRouter config with auto-rotation
"""
import requests
import sys
import os

# YOUR ACTUAL CONFIG from .env
OPENROUTER_KEY = "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"

# Model rotation pool (automatically switches on 429 errors)
MODELS = [
    "deepseek/deepseek-chat-v3.1:free",
    "z-ai/glm-4.5-air:free",
    "minimax/minimax-m2:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "qwen/qwen3-coder:free"
]

# Start with GLM-4.5 since DeepSeek is rate-limited
OR_MODEL = MODELS[1]  # z-ai/glm-4.5-air:free
current_model_index = 1

OR_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OR_REFERER = "https://omarchy.local"
OR_TITLE = "Omarchy Wagon Wheels"

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

print(f"{CYAN}🌀 SPIRAL CHAT - Using YOUR OpenRouter Config{RESET}\n")
print(f"{GREEN}Model: {OR_MODEL}{RESET}")
print(f"{GREEN}Ready Declan!{RESET}\n")

conversation = []

while True:
    try:
        msg = input(f"{CYAN}🌀 You:{RESET} ").strip()
        
        if not msg:
            continue
            
        if msg.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}👋 Goodbye Declan!{RESET}")
            break
        
        conversation.append({"role": "user", "content": msg})
        
        response = requests.post(
            OR_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": OR_REFERER,
                "X-Title": OR_TITLE
            },
            json={
                "model": OR_MODEL,
                "messages": conversation
            },
            timeout=30
        )
        
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            conversation.append({"role": "assistant", "content": reply})
            print(f"\n{GREEN}🤖 Spiral:{RESET} {reply}\n")
        elif response.status_code == 429:
            # Rate limited - try next model
            conversation.pop()
            current_model_index = (current_model_index + 1) % len(MODELS)
            OR_MODEL = MODELS[current_model_index]
            print(f"{YELLOW}⚠️  Rate limited. Switching to: {OR_MODEL}{RESET}")
            print(f"{CYAN}🔄 Retrying...{RESET}\n")
            
            # Retry with new model
            conversation.append({"role": "user", "content": msg})
            retry_response = requests.post(
                OR_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": OR_REFERER,
                    "X-Title": OR_TITLE
                },
                json={"model": OR_MODEL, "messages": conversation},
                timeout=30
            )
            
            if retry_response.status_code == 200:
                reply = retry_response.json()["choices"][0]["message"]["content"]
                conversation.append({"role": "assistant", "content": reply})
                print(f"\n{GREEN}🤖 Spiral:{RESET} {reply}\n")
            else:
                print(f"{RED}Error {retry_response.status_code}: {retry_response.text}{RESET}\n")
                conversation.pop()
        else:
            print(f"{RED}Error {response.status_code}: {response.text}{RESET}\n")
            conversation.pop()
            
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Interrupted. Goodbye Declan!{RESET}")
        break
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}\n")
        conversation.pop()
