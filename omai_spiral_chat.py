#!/usr/bin/env python3
"""
🌀 OMAi SPIRAL CHAT - Local AI Chat Interface
Connects to your OMAi Spiral Codex system with local philosophy
"""
import requests
import json
import os
import sys
from datetime import datetime

# ANSI colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

print(f"{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
print(f"{CYAN}║            🌀 OMAi SPIRAL CODEX LOCAL CHAT 🌀                     ║{RESET}")
print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
print()
print(f"{YELLOW}✨ OMAi Philosophy:{RESET}")
print("  • Local intelligence with MIT license compliance")
print("  • Priority on ManuAGI and open-source educational content")
print("  • Web3-ready with verifiable ledger")
print("  • Multi-agent system with reflection cycles")
print()
print(f"{GREEN}Commands:{RESET} 'quit' to exit, 'clear' to reset, 'status' for system info")
print()

# OMAi API configuration
OMAI_BASE_URL = "http://localhost:8000"
session_id = None
conversation = []

def create_session():
    """Create new OMAi chat session"""
    global session_id
    try:
        response = requests.post(f"{OMAI_BASE_URL}/v1/converse/session/create")
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            print(f"{GREEN}✓ Session created: {session_id[:8]}...{RESET}")
            return True
    except Exception as e:
        print(f"{YELLOW}⚠️ Session creation failed: {e}{RESET}")
    return False

def send_message(message):
    """Send message to OMAi system"""
    if not session_id:
        if not create_session():
            return None

    try:
        payload = {
            "message": message,
            "session_id": session_id
        }

        response = requests.post(
            f"{OMAI_BASE_URL}/v1/converse/session/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"{YELLOW}⚠️ API Error: {response.status_code}{RESET}")

    except Exception as e:
        print(f"{YELLOW}⚠️ Connection error: {e}{RESET}")

    return None

def get_system_status():
    """Get OMAi system status"""
    try:
        response = requests.get(f"{OMAI_BASE_URL}/v1/converse/health")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"status": "offline"}

def show_status():
    """Display system status"""
    print(f"\n{BLUE}🏥 OMAi System Status{RESET}")
    print("=" * 40)

    status = get_system_status()
    print(f"Status: {GREEN}● Online{RESET}" if status.get("status") != "offline" else f"{YELLOW}● Offline{RESET}")
    print(f"Session: {session_id[:8] + '...' if session_id else 'None'}")
    print(f"Messages: {len(conversation)}")

    # Check if priority system is available
    try:
        priority_response = requests.get(f"{OMAI_BASE_URL}/v1/converse/status")
        if priority_response.status_code == 200:
            priority_data = priority_response.json()
            print(f"Priority System: {GREEN}● Active{RESET}")
    except:
        print(f"Priority System: {YELLOW}● Unknown{RESET}")

    print()

# Initialize session
create_session()

# Main loop
while True:
    try:
        user_input = input(f"{CYAN}🌀 You:{RESET} ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}🌀 OMAi session ended!{RESET}")
            print(f"{GREEN}✓{RESET} Conversation preserved in local OMAi memory")
            break

        if user_input.lower() == 'clear':
            conversation.clear()
            session_id = None
            create_session()
            print(f"{YELLOW}🔄 Session reset{RESET}\n")
            continue

        if user_input.lower() == 'status':
            show_status()
            continue

        print(f"\n{MAGENTA}🧠 OMAi Spiral:{RESET} ", end="", flush=True)

        # Send to OMAi system
        response = send_message(user_input)

        if response:
            reply = response.get("response", "No response")
            conversation.append({"user": user_input, "omai": reply})
            print(reply)

            # Show priority info if available
            if response.get("priority_score"):
                score = response["priority_score"]
                level = response.get("priority_level", "UNKNOWN")
                print(f"\n{CYAN}📊 Priority: {level} ({score:.1f}x){RESET}")
        else:
            print(f"{YELLOW}OMAi system unavailable. Check if FastAPI server is running.{RESET}")

        print()

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}🌀 Interrupted. OMAi memory preserved.{RESET}")
        break
    except Exception as e:
        print(f"\n{YELLOW}❌ Error: {e}{RESET}\n")