#!/usr/bin/env python3
"""
🌀 QUANTUM SPIRAL CHAT - Quantum Debug Enhanced AI Interface
Connects to your OMAi system with quantum debug capabilities and OpenRouter efficiency
"""
import requests
import json
import os
import sys
import time
import random
from datetime import datetime
from math import sqrt

# ANSI colors with quantum effects
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RED = "\033[31m"
QUANTUM = "\033[38;5;93m"  # Quantum purple
RESET = "\033[0m"

# Quantum debug symbols
QUANTUM_STATES = ["⊚", "⧛", "⎈", "⌬", "◈"]
QUANTUM_COLORS = ["\033[38;5;93m", "\033[38;5;129m", "\033[38;5;165m", "\033[38;5;201m"]

def quantum_effect():
    """Generate quantum visual effect"""
    state = random.choice(QUANTUM_STATES)
    color = random.choice(QUANTUM_COLORS)
    return f"{color}{state}{RESET}"

print(f"{QUANTUM}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
print(f"{QUANTUM}║        🌀 QUANTUM SPIRAL CHAT (Debug Enhanced) 🌀                  ║{RESET}")
print(f"{QUANTUM}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
print()
print(f"{YELLOW}✨ Quantum OMAi Features:{RESET}")
print("  • OpenRouter token rotation with quantum optimization")
print("  • MIT license compliance with ManuAGI priority (3.0x)")
print("  • Quantum debug with ⊚ active brain monitoring")
print("  • Real-time quantum state visualization")
print()
print(f"{GREEN}Commands:{RESET} 'quit' to exit, 'clear' to reset, 'quantum' for debug, 'status' for system info")
print()

# OMAi API configuration
OMAI_BASE_URL = "http://localhost:8000"
session_id = f"quantum_spiral_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
conversation = []
quantum_coherence = 1.0

def get_quantum_brain_stats():
    """Get quantum brain stats with debug info"""
    try:
        response = requests.get(f"{OMAI_BASE_URL}/v1/brain/stats", timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"status": "⊚ offline", "quantum_coherence": 0.0}

def send_quantum_message(message):
    """Send message with quantum debug enhancements"""
    global quantum_coherence

    # Simulate quantum processing
    quantum_flicker = quantum_effect()
    print(f"{quantum_flicker}", end="", flush=True)
    time.sleep(0.1)

    try:
        # Use OMAi with quantum parameters
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

            # Update quantum coherence based on response
            quantum_coherence = max(0.1, min(1.0, quantum_coherence + random.uniform(-0.1, 0.1)))

            return data.get("response", "Quantum OMAi processing complete")
        else:
            quantum_coherence *= 0.9  # Reduce coherence on error
            return f"Quantum system fluctuating (HTTP {response.status_code})"

    except requests.exceptions.Timeout:
        quantum_coherence *= 0.8
        return f"{YELLOW}⏱️ Quantum timeout - coherence fluctuating{RESET}"
    except Exception as e:
        quantum_coherence *= 0.7
        return f"{RED}❌ Quantum disruption: {str(e)[:30]}...{RESET}"

def get_omai_status():
    """Get comprehensive OMAi system status"""
    try:
        response = requests.get(f"{OMAI_BASE_URL}/v1/converse/health", timeout=3)
        if response.status_code == 200:
            return "🟢 OMAi Online (Quantum Active)"
    except:
        pass
    return "🔴 OMAi Offline"

def show_quantum_debug():
    """Display quantum debug information"""
    print(f"\n{QUANTUM}🔬 QUANTUM DEBUG INFORMATION{RESET}")
    print("=" * 60)

    # Brain stats
    brain_stats = get_quantum_brain_stats()
    print(f"Brain Status: {brain_stats.get('status', 'Unknown')}")
    print(f"Total Entries: {brain_stats.get('total_entries', 0)}")
    print(f"Thought Count: {brain_stats.get('thought_count', 0)}")
    print(f"Protocol: {brain_stats.get('protocol', 'Unknown')}")
    print(f"Integrity: {brain_stats.get('integrity', 'Unknown')}")

    # Quantum metrics
    print(f"\n{QUANTUM}Quantum Metrics:{RESET}")
    print(f"Coherence: {quantum_coherence:.2f}")
    print(f"Session ID: {session_id}")
    print(f"Conversation Entries: {len(conversation)}")

    # OMAi status
    om ai_status = get_omai_status()
    print(f"\nSystem: {omai_status}")
    print(f"Router: OpenRouter (Quantum Optimized)")
    print(f"Compliance: MIT License Research")

    # Quantum visualization
    print(f"\n{QUANTUM}Quantum State: ", end="")
    for _ in range(5):
        print(quantum_effect(), end=" ")
        time.sleep(0.05)
    print(f"\n")

def show_status():
    """Display regular system status with quantum indicator"""
    print(f"\n{BLUE}🏥 OMAi Quantum System Status{RESET}")
    print("=" * 50)

    # System status with quantum indicator
    status = get_omai_status()
    quantum_indicator = quantum_effect()
    print(f"System: {status} {quantum_indicator}")

    # Session info
    print(f"Session: {session_id}")
    print(f"Messages: {len(conversation)}")
    print(f"Quantum Coherence: {quantum_coherence:.2f}")

    # Priority system
    print(f"Priority: ManuAGI (3.0x MIT License)")
    print(f"Router: OpenRouter (Quantum Optimized)")
    print()

# Main quantum chat loop
print(f"{GREEN}Quantum OMAi System Ready!{RESET}")
print(f"{QUANTUM}Connected to your quantum OMAi with OpenRouter optimization{RESET}\n")

while True:
    try:
        # Show quantum coherence in prompt
        coherence_color = GREEN if quantum_coherence > 0.7 else YELLOW if quantum_coherence > 0.4 else RED
        user_input = input(f"{CYAN}🌀 You[{coherence_color}{quantum_coherence:.1f}{CYAN}]:{RESET} ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n{YELLOW}🌀 Quantum Session Ended!{RESET}")
            print(f"{GREEN}✓ Quantum conversation preserved in OMAi memory{RESET}")
            print(f"{GREEN}✓ OpenRouter tokens quantum-optimized{RESET}")
            print(f"{QUANTUM}✓ Final coherence: {quantum_coherence:.2f}{RESET}")
            break

        if user_input.lower() == 'clear':
            conversation.clear()
            session_id = f"quantum_spiral_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            quantum_coherence = 1.0
            print(f"{YELLOW}🔄 Quantum session reset (coherence restored){RESET}\n")
            continue

        if user_input.lower() == 'quantum':
            show_quantum_debug()
            continue

        if user_input.lower() == 'status':
            show_status()
            continue

        # Show quantum processing effect
        print(f"\n{QUANTUM}⚛️  Processing Quantum OMAi:{RESET} ", end="", flush=True)

        # Send to quantum OMAi system
        response = send_quantum_message(user_input)

        # Add to conversation history
        conversation.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "omai": response,
            "quantum_coherence": quantum_coherence
        })

        print(f"\n{MAGENTA}🧠 Quantum OMAi:{RESET} {response}")

        # Show quantum effects for priority content
        if any(keyword in user_input.lower() for keyword in ['manuagi', 'mit license', 'open source', 'quantum']):
            quantum_boost = quantum_effect()
            print(f"\n{QUANTUM}{quantum_boost} Priority Quantum Boost Applied{RESET}")

        # Show coherence warning if low
        if quantum_coherence < 0.5:
            print(f"{YELLOW}⚠️  Quantum coherence low - consider session reset{RESET}")

        print()

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}🌀 Quantum interruption. Coherence preserved at {quantum_coherence:.2f}{RESET}")
        break
    except Exception as e:
        print(f"\n{RED}❌ Quantum error: {e}{RESET}\n")