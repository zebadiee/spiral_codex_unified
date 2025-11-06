#!/usr/bin/env python3
"""
Simple Spiral Chat - Uses /v1/converse/agents endpoint
"""
import sys
sys.path.insert(0, '.')

from agent_orchestrator import multi_agent_converse

print("╔══════════════════════════════════════════════════════════════════════╗")
print("║              🌀 SPIRAL CODEX CHAT INTERFACE 🌀                       ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()
print("Available agents: ƒCODEX, ƒCLAUDE, ƒGEMINI")
print("Type 'quit' to exit")
print()

session_id = "interactive_chat"
turn = 0

while True:
    user_input = input("🌀 You: ").strip()
    
    if not user_input:
        continue
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("\n👋 Chat session ended!")
        break
    
    turn += 1
    print("\n🤖 Spiral: ", end="", flush=True)
    
    try:
        # Use multi-agent conversation
        result = multi_agent_converse(
            task=user_input,
            agents=["ƒCODEX", "ƒCLAUDE"],
            turns=1,
            session_id=f"{session_id}_{turn}"
        )
        
        if result and 'summary' in result:
            print(result['summary'])
        elif result and 'exchanges' in result:
            for exchange in result['exchanges']:
                if 'response' in exchange:
                    print(exchange['response'])
        else:
            print(f"Response: {result}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print()

