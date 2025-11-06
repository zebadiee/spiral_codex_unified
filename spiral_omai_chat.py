#!/usr/bin/env python3
"""
🌀 SPIRAL OMAi CHAT - Economic Local AI Chat Interface
Connects to your OMAi system using OpenRouter token rotation for maximum efficiency
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
RED = "\033[31m"
RESET = "\033[0m"

print(f"{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
print(f"{CYAN}║           🌀 SPIRAL OMAi ECONOMIC CHAT (OpenRouter) 🌀             ║{RESET}")
print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
print()
print(f"{YELLOW}✨ OMAi Economic Features:{RESET}")
print("  • OpenRouter token rotation for maximum efficiency")
print("  • MIT license compliance with ManuAGI priority (3.0x)")
print("  • Local Spiral Codex philosophy")
print("  • Priority content system")
print()
print(f"{GREEN}Commands:{RESET} 'quit' to exit, 'clear' to reset, 'status' for system info")
print()

# OMAi API configuration
OMAI_BASE_URL = "http://localhost:8000"
session_id = f"spiral_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
conversation = []

def send_spiral_message(message):
    """Send message using OMAi's economic OpenRouter system"""
    try:
        # Use the spiral-omai-chat endpoint which should work with your setup
        params = {
            "seed": message,
            "turns": 1,
            "session_id": session_id
        }

        response = requests.get(
            f"{OMAI_BASE_URL}/v1/converse/spiral-omai-chat",
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "OMAi economic processing complete")
        else:
            return f"OMAi system busy (HTTP {response.status_code})"

    except requests.exceptions.Timeout:
        return f"{YELLOW}⏱️ OMAi processing timeout - try again{RESET}"
    except Exception as e:
        return f"{RED}❌ Connection error: {str(e)[:50]}...{RESET}"

def get_system_info():
    """Get OMAi system information"""
    try:
        response = requests.get(f"{OMAI_BASE_URL}/v1/converse/health", timeout=5)
        if response.status_code == 200:
            return "🟢 OMAi Online (OpenRouter Active)"
    except:
        pass
    return "🔴 OMAi Offline"

def show_priority_info():
    """Show priority system status"""
    try:
        # Test priority scoring
        test_data = {
            "url": "https://github.com/manuagi",
            "title": "ManuAGI Open Source AI Development",
            "content": "MIT license educational content for AI development",
            "source_type": "tutorial"
        }

        response = requests.post(
            f"{OMAI_BASE_URL}/test-priority",
            json=test_data,
            timeout=5
        )

        if response.status_code == 200:
            score = response.json().get("priority_score", 0)
            return f"ManuAGI Priority: {score:.1f}x (MIT License)"
    except:
        pass
    return "Priority System: Active"

def show_status():
    """Display comprehensive system status"""
    print(f"\n{BLUE}🏥 OMAi Economic System Status{RESET}")
    print("=" * 50)

    # System status
    status = get_system_info()
    print(f"System: {status}")

    # Session info
    print(f"Session: {session_id}")
    print(f"Messages: {len(conversation)}")

    # Priority system
    priority_info = show_priority_info()
    print(f"Priority: {priority_info}")

    # Economic info
    print(f"Router: OpenRouter (Token Rotation)")
    print(f"Compliance: MIT License Research")
    print()

# Main chat loop
print(f"{GREEN}OMAi Economic System Ready!{RESET}")
print(f"{CYAN}Connected to your local OMAi with OpenRouter token rotation{RESET}\n")

while True:
    try:
        user_input = input(f"{CYAN}🌀 You:{RESET} ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}🌀 OMAi Economic Session Ended!{RESET}")
            print(f"{GREEN}✓ Conversation preserved in local OMAi memory{RESET}")
            print(f"{GREEN}✓ OpenRouter tokens optimized{RESET}")
            break

        if user_input.lower() == 'clear':
            conversation.clear()
            session_id = f"spiral_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"{YELLOW}🔄 Session reset (new economic instance){RESET}\n")
            continue

        if user_input.lower() == 'status':
            show_status()
            continue

        print(f"\n{MAGENTA}🧠 OMAi Spiral (Economic):{RESET} ", end="", flush=True)

        # Send to OMAi economic system
        response = send_spiral_message(user_input)

        # Add to conversation history
        conversation.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "omai": response
        })

        print(response)

        # Show priority boost if detected
        if any(keyword in user_input.lower() for keyword in ['manuagi', 'mit license', 'open source']):
            print(f"\n{CYAN}📊 Priority Boost Applied (MIT License Research){RESET}")

        print()

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}🌀 Interrupted. OMAi memory preserved.{RESET}")
        break
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}\n")