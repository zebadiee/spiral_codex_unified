#!/usr/bin/env python3
"""
SPIRAL FIXED CHAT - Auto model rotation on rate limits
"""
import requests
import json

# Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Model pool (will rotate on 429)
MODELS = [
    "google/gemini-flash-1.5",
    "meta-llama/llama-3.2-3b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
]

current_model_idx = 0
CURRENT_MODEL = MODELS[current_model_idx]

# Colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"

print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
print(f"{BOLD}{CYAN}║  🌀 SPIRAL CHAT - Auto Model Rotation                   ║{RESET}")
print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")
print(f"{GREEN}Starting Model: {CURRENT_MODEL}{RESET}")
print(f"{GREEN}Models Available: {len(MODELS)}{RESET}\n")

conversation = []

def call_api(messages, model):
    """Call OpenRouter API"""
    try:
        response = requests.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://omarchy.local",
                "X-Title": "Spiral Chat"
            },
            json={
                "model": model,
                "messages": messages
            },
            timeout=30
        )
        return response
    except Exception as e:
        return {"error": str(e)}

def rotate_model():
    """Switch to next model"""
    global current_model_idx, CURRENT_MODEL
    current_model_idx = (current_model_idx + 1) % len(MODELS)
    CURRENT_MODEL = MODELS[current_model_idx]
    print(f"{YELLOW}🔄 Switched to: {CURRENT_MODEL}{RESET}")
    return CURRENT_MODEL

def chat_with_retry(user_msg, max_retries=3):
    """Try chat with automatic model rotation on rate limits"""
    conversation.append({"role": "user", "content": user_msg})
    
    for attempt in range(max_retries):
        response = call_api(conversation, CURRENT_MODEL)
        
        if isinstance(response, dict) and "error" in response:
            print(f"{RED}❌ Error: {response['error']}{RESET}")
            if attempt < max_retries - 1:
                rotate_model()
            continue
            
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            conversation.append({"role": "assistant", "content": reply})
            return reply
        elif response.status_code == 429:
            print(f"{YELLOW}⚠️  Rate limited on {CURRENT_MODEL}{RESET}")
            if attempt < max_retries - 1:
                rotate_model()
            continue
        else:
            print(f"{RED}❌ Error {response.status_code}: {response.text[:100]}{RESET}")
            if attempt < max_retries - 1:
                rotate_model()
            continue
    
    conversation.pop()  # Remove failed message
    return None

# Main loop
while True:
    try:
        user_input = input(f"{CYAN}🧠 You: {RESET}").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}👋 Goodbye Declan!{RESET}")
            break
        
        reply = chat_with_retry(user_input)
        
        if reply:
            print(f"{GREEN}🤖 Spiral: {RESET}{reply}\n")
        else:
            print(f"{RED}❌ All models failed. Try again later.{RESET}\n")
            
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Interrupted. Goodbye!{RESET}")
        break
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}\n")

