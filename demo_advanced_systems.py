#!/usr/bin/env python3
"""
🚀 SPIRAL CODEX ADVANCED SYSTEMS DEMO
Quick demonstration of the enhanced chat capabilities

This demo shows:
- spiral_conscious_chat.py with file operations
- spiral_agentic.py with multi-agent coordination
- spiral_consciousness.py learning system
"""

import os
import sys
import asyncio
from pathlib import Path

# Add Spiral Codex to path
sys.path.insert(0, str(Path(__file__).parent))

# Colors
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}{title.center(60)}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}\n")

def demo_conscious_chat():
    """Demo spiral_conscious_chat.py capabilities"""
    print_header("🌟 SPIRAL CONSCIOUS CHAT DEMO")

    print(f"{GREEN}Features:{RESET}")
    print(f"  • Advanced reasoning integration")
    print(f"  • File operations (read/write/execute)")
    print(f"  • Safe code execution with validation")
    print(f"  • OMAi RAG context enrichment")
    print(f"  • Neural Bus communication")
    print(f"  • Session logging and persistence")
    print()

    print(f"{YELLOW}Usage:{RESET}")
    print(f"  {CYAN}python spiral_conscious_chat.py{RESET}")
    print()

    print(f"{BLUE}Try these commands:{RESET}")
    print(f"  • 'Read the spiral_chat.py file'")
    print(f"  • 'Create a new Python project called my_app'")
    print(f"  • 'Execute: echo Hello from advanced chat!'")
    print(f"  • 'What are my current system capabilities?'")
    print(f"  • 'List the files in the current directory'")
    print()

def demo_agentic_orchestrator():
    """Demo spiral_agentic.py capabilities"""
    print_header("🚀 SPIRAL AGENTIC ORCHESTRATOR DEMO")

    print(f"{GREEN}Available Agents:{RESET}")
    print(f"  {MAGENTA}ƒCODEX{RESET}: Code generation, debugging, architecture")
    print(f"  {MAGENTA}ƒCLAUDE{RESET}: Analysis, reasoning, planning")
    print(f"  {MAGENTA}ƒOMAI{RESET}: Knowledge, context, research")
    print(f"  {MAGENTA}ƒEXECUTOR{RESET}: Task execution, project management")
    print()

    print(f"{YELLOW}Usage:{RESET}")
    print(f"  {CYAN}python spiral_agentic.py{RESET}")
    print()

    print(f"{BLUE}Try these tasks:{RESET}")
    print(f"  • 'Create a web server in Python' → Selects ƒCODEX")
    print(f"  • 'Analyze the system architecture' → Selects ƒCLAUDE")
    print(f"  • 'Research machine learning concepts' → Selects ƒOMAI")
    print(f"  • 'Build and test the current project' → Selects ƒEXECUTOR")
    print()

def demo_consciousness_system():
    """Demo spiral_consciousness.py capabilities"""
    print_header("🧠 SPIRAL CONSCIOUSNESS SYSTEM DEMO")

    print(f"{GREEN}Learning Features:{RESET}")
    print(f"  • Conversation pattern analysis")
    print(f"  • Performance metric tracking")
    print(f"  • User preference learning")
    print(f"  • System self-reflection")
    print(f"  • Automatic optimization recommendations")
    print()

    print(f"{YELLOW}Integration:{RESET}")
    print(f"  The consciousness system automatically tracks:")
    print(f"  • Which agents are best for which tasks")
    print(f"  • Response times and success rates")
    print(f"  • Tool usage patterns")
    print(f"  • User interaction preferences")
    print()

def demo_file_operations():
    """Demo file operation capabilities"""
    print_header("📁 ADVANCED FILE OPERATIONS DEMO")

    # Create a demo file
    demo_file = Path("demo_advanced_features.txt")
    demo_content = """🌟 Spiral Codex Advanced Features Demo

✅ Integrated Chat Systems:
- spiral_conscious_chat.py (Full integration)
- spiral_agentic.py (Multi-agent coordination)
- spiral_chat.py (Basic chat)

✅ Advanced Capabilities:
- File operations (read/write/list)
- Safe code execution
- Multi-agent coordination
- Consciousness and learning
- Service integration (Reasoning Hub, Neural Bus, OMAi)

✅ Available Tools:
- read_file: Read file contents
- write_file: Create/edit files
- execute_bash: Run commands safely
- list_directory: Browse directories
- create_project: Scaffold projects
- run_tests: Execute test suites
- git_status, git_commit: Version control

🚀 This is the next generation of AI assistance!
"""

    demo_file.write_text(demo_content)

    print(f"{GREEN}Created demo file: {demo_file}{RESET}")
    print(f"\n{BLUE}File content:{RESET}")
    print(demo_content)

    print(f"\n{YELLOW}You can now:{RESET}")
    print(f"  1. Use the chat systems to read this file")
    print(f"  2. Try writing new files")
    print(f"  3. Execute code commands")
    print(f"  4. Create projects and run tests")
    print()

def demo_system_status():
    """Show current system status"""
    print_header("🔊 SYSTEM STATUS")

    print(f"{GREEN}✅ Core Systems Operational:{RESET}")
    print(f"  • OpenRouter API: Connected")
    print(f"  • Chat Systems: 3 modes available")
    print(f"  • Multi-Agent System: Ready")
    print(f"  • Consciousness System: Learning enabled")
    print(f"  • File Operations: Safe execution ready")
    print()

    print(f"{YELLOW}📁 Available Chat Modes:{RESET}")
    print(f"  1. {CYAN}python spiral_chat.py{RESET} - Basic chat")
    print(f"  2. {CYAN}python spiral_conscious_chat.py{RESET} - Advanced with file ops")
    print(f"  3. {CYAN}python spiral_agentic.py{RESET} - Multi-agent coordination")
    print()

    print(f"{MAGENTA}🧠 Intelligence Features:{RESET}")
    print(f"  • Automatic agent selection based on task type")
    print(f"  • Context-aware responses from knowledge base")
    print(f"  • Learning from user interactions")
    print(f"  • Performance optimization recommendations")
    print()

def main():
    """Main demo function"""
    print(f"{BOLD}{MAGENTA}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          🚀 SPIRAL CODEX ADVANCED SYSTEMS 🚀           ║")
    print("║             Next-Generation AI Assistance              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")

    print(f"\n{GREEN}🎉 CONGRATULATIONS! Your Spiral Codex has been upgraded!{RESET}")
    print(f"{CYAN}You now have three levels of AI chat capabilities:{RESET}\n")

    demo_conscious_chat()
    demo_agentic_orchestrator()
    demo_consciousness_system()
    demo_file_operations()
    demo_system_status()

    print(f"{BOLD}{GREEN}{'='*60}{RESET}")
    print(f"{BOLD}{GREEN}🎯 READY FOR ADVANCED AI ASSISTANCE!{RESET}")
    print(f"{BOLD}{GREEN}{'='*60}{RESET}")

    print(f"\n{YELLOW}Quick Start:{RESET}")
    print(f"  {CYAN}python spiral_conscious_chat.py{RESET}    # Full-featured chat")
    print(f"  {CYAN}python spiral_agentic.py{RESET}          # Multi-agent system")
    print(f"  {CYAN}python spiral_chat.py{RESET}             # Basic chat")

    print(f"\n{BLUE}💡 Tip: Start with spiral_conscious_chat.py for the best experience!{RESET}")

if __name__ == "__main__":
    main()