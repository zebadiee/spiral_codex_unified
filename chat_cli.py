#!/usr/bin/env python3
"""
Spiral Chat CLI - Interactive chat with vault enrichment
"""
import requests
import json
import sys
from datetime import datetime

SPIRAL_URL = "http://localhost:8000"
SESSION_ID = f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def chat(message: str, vault_query: bool = True) -> dict:
    """Send message to Spiral chat endpoint"""
    try:
        resp = requests.post(
            f"{SPIRAL_URL}/v1/chat",
            headers={"content-type": "application/json"},
            json={
                "message": message,
                "session_id": SESSION_ID,
                "vault_query": vault_query,
                "max_snips": 5
            },
            timeout=30
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              🌀 SPIRAL CODEX INTERACTIVE CHAT 🌀                     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Session: {SESSION_ID}")
    print("Type 'quit' or 'exit' to end, 'help' for commands")
    print()
    
    while True:
        try:
            user_input = input("🌀 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Session saved to ledger.")
                break
                
            if user_input.lower() == 'help':
                print("""
Commands:
  quit/exit/q  - End chat session
  help         - Show this help
  
Features:
  ✓ Vault-aware responses (enriched from Obsidian)
  ✓ Multi-agent routing (ƒCODEX, ƒCLAUDE, etc.)
  ✓ Session memory and context
  ✓ MIT priority sources (ManuAGI 3.0x)
                """)
                continue
            
            print("🤖 Spiral: ", end="", flush=True)
            result = chat(user_input)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                # Display response
                print(json.dumps(result, indent=2))
                
                # Show vault context if available
                if result.get("vault", {}).get("count", 0) > 0:
                    print(f"\n📚 Found {result['vault']['count']} vault references")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
if __name__ == "__main__":
    main()
