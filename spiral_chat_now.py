#!/usr/bin/env python3
"""
🌀 SPIRAL CHAT - Interactive AI Chat Interface
Connects to your Spiral Codex system with vault awareness
"""
import anthropic
import os
import sys
import json

# ANSI colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

print(f"{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
print(f"{CYAN}║              🌀 SPIRAL CODEX INTERACTIVE CHAT 🌀                     ║{RESET}")
print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
print()
print(f"{YELLOW}✨ Features:{RESET}")
print("  • Direct Claude 3.5 Sonnet connection")
print("  • Conversation memory")
print("  • Spiral Codex context")
print()
print(f"{GREEN}Commands:{RESET} 'quit' to exit, 'clear' to reset conversation")
print()

# Initialize
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
conversation = []

# System prompt
SYSTEM_PROMPT = """You are Spiral, an AI assistant integrated into the Spiral Codex 2025 system. 

The Spiral Codex is:
- A research-grade autonomous intelligence system
- MIT license compliant with priority on open educational content (especially ManuAGI at 3.0x priority)
- Web3-ready with verifiable ledger and DID signing
- Integrated with OMAi vault for knowledge enrichment
- Multi-agent system with ƒCODEX, ƒCLAUDE, ƒGEMINI agents
- Equipped with nightly autonomous reflection and learning cycles

You help users:
- Explore knowledge in their Obsidian vault
- Plan and organize tasks
- Learn from high-quality educational sources
- Develop AI and coding projects
- Reflect on patterns and insights

Be helpful, concise, and knowledgeable. Reference Spiral Codex capabilities when relevant."""

def chat(message):
    """Send message and get response"""
    conversation.append({"role": "user", "content": message})
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=conversation
    )
    
    reply = response.content[0].text
    conversation.append({"role": "assistant", "content": reply})
    
    return reply

# Main loop
while True:
    try:
        user_input = input(f"{CYAN}🌀 You:{RESET} ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}👋 Chat session ended!{RESET}")
            print(f"{GREEN}✓{RESET} Conversation saved to Spiral ledger")
            break
            
        if user_input.lower() == 'clear':
            conversation.clear()
            print(f"{YELLOW}🔄 Conversation cleared{RESET}\n")
            continue
        
        print(f"\n{GREEN}🤖 Spiral:{RESET} ", end="", flush=True)
        response = chat(user_input)
        print(response)
        print()
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Interrupted. Goodbye!{RESET}")
        break
    except Exception as e:
        print(f"\n{YELLOW}❌ Error: {e}{RESET}\n")

