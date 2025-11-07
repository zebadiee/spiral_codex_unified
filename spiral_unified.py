#!/usr/bin/env python3
"""
SPIRAL UNIFIED - One chat to rule them all
Persistent, multi-agent, tool-enabled, context-aware
No more jumping between chats!
"""
import requests
import json
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum

# Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Service endpoints (if available)
OMAI_ENDPOINT = "http://localhost:7016"
NEURAL_BUS = "http://localhost:9000"
REASONING_HUB = "http://localhost:8000"

MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]

# Colors
C = "\033[36m"  # Cyan
G = "\033[32m"  # Green
Y = "\033[33m"  # Yellow
R = "\033[31m"  # Red
B = "\033[34m"  # Blue
M = "\033[35m"  # Magenta
BOLD = "\033[1m"
RESET = "\033[0m"

# =============================================================================
# MULTI-AGENT SYSTEM
# =============================================================================

class AgentType(Enum):
    CHAT = "chat"           # General conversation
    DEVOPS = "devops"       # Infrastructure, deployment
    CODER = "coder"         # Code generation
    DEBUGGER = "debugger"   # Problem solving
    RESEARCHER = "researcher"  # Knowledge retrieval

class Agent:
    """Base agent with specific expertise"""
    
    def __init__(self, agent_type: AgentType, model: str):
        self.type = agent_type
        self.model = model
        self.system_prompts = {
            AgentType.CHAT: "You are Spiral, a friendly AI assistant.",
            AgentType.DEVOPS: "You are a DevOps expert. Focus on infrastructure, deployment, CI/CD, containers, and automation.",
            AgentType.CODER: "You are an expert developer. Write clean, production-ready code with proper error handling.",
            AgentType.DEBUGGER: "You are a debugging specialist. Analyze problems systematically and provide solutions.",
            AgentType.RESEARCHER: "You are a research assistant. Provide detailed, accurate information with context.",
        }
    
    def get_system_prompt(self) -> str:
        return self.system_prompts.get(self.type, self.system_prompts[AgentType.CHAT])

# =============================================================================
# TOOL SYSTEM
# =============================================================================

class Tools:
    """All available tools"""
    
    @staticmethod
    def create_file(filename: str, content: str) -> str:
        try:
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)
            lines = len(content.split('\n'))
            return f"✅ Created {filename} ({len(content)} bytes, {lines} lines)"
        except Exception as e:
            return f"❌ Error: {e}"
    
    @staticmethod
    def read_file(filename: str) -> str:
        try:
            content = Path(filename).read_text()
            lines = len(content.split('\n'))
            preview = content[:500] + "..." if len(content) > 500 else content
            return f"✅ {filename} ({len(content)} bytes, {lines} lines)\n\n{preview}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    @staticmethod
    def list_files(directory: str = ".") -> str:
        try:
            files = list(Path(directory).iterdir())
            file_list = "\n".join(f"  {'📁' if f.is_dir() else '📄'} {f.name}" for f in sorted(files)[:30])
            return f"✅ {directory}/ ({len(files)} items):\n{file_list}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    @staticmethod
    def execute_bash(command: str) -> str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=10
            )
            output = (result.stdout + result.stderr).strip()
            return f"✅ Executed: {command}\n{output[:500]}"
        except subprocess.TimeoutExpired:
            return f"⏱️ Timeout: {command}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    @staticmethod
    def check_services() -> str:
        """Check if backend services are available"""
        status = []
        for name, url in [("OMAi", OMAI_ENDPOINT), ("Neural Bus", NEURAL_BUS), ("Reasoning", REASONING_HUB)]:
            try:
                resp = requests.get(f"{url}/health", timeout=2)
                status.append(f"✅ {name}")
            except:
                status.append(f"❌ {name} (offline)")
        return "\n".join(status)

# =============================================================================
# UNIFIED AGENT ORCHESTRATOR
# =============================================================================

class UnifiedAgent:
    """One agent that coordinates everything"""
    
    def __init__(self):
        self.agents = {
            AgentType.CHAT: Agent(AgentType.CHAT, MODELS[0]),
            AgentType.DEVOPS: Agent(AgentType.DEVOPS, MODELS[0]),
            AgentType.CODER: Agent(AgentType.CODER, MODELS[0]),
            AgentType.DEBUGGER: Agent(AgentType.DEBUGGER, MODELS[0]),
            AgentType.RESEARCHER: Agent(AgentType.RESEARCHER, MODELS[0]),
        }
        self.conversation = []
        self.current_agent = self.agents[AgentType.CHAT]
        self.tools = Tools()
        
    def detect_intent(self, message: str) -> Tuple[AgentType, bool]:
        """Detect which agent to use and if tools are needed"""
        msg = message.lower()
        
        # Check for file operations
        needs_tools = any(word in msg for word in [
            'create', 'write', 'save', 'read', 'show', 'file', 
            'execute', 'run', 'list', 'directory'
        ])
        
        # Detect agent type
        if any(word in msg for word in ['deploy', 'docker', 'kubernetes', 'ci/cd', 'infrastructure', 'container']):
            return AgentType.DEVOPS, needs_tools
        elif any(word in msg for word in ['code', 'function', 'class', 'write', 'implement', 'build']):
            return AgentType.CODER, needs_tools
        elif any(word in msg for word in ['error', 'bug', 'fix', 'problem', 'debug', 'not working']):
            return AgentType.DEBUGGER, needs_tools
        elif any(word in msg for word in ['explain', 'what is', 'research', 'tell me about']):
            return AgentType.RESEARCHER, needs_tools
        else:
            return AgentType.CHAT, needs_tools
    
    def execute_tool(self, message: str) -> Optional[str]:
        """Execute tool if needed"""
        msg = message.lower()
        
        # File creation
        if 'create' in msg and 'file' in msg:
            # Extract filename
            match = re.search(r'(?:create|write|save).*?(?:file)?\s+(?:called\s+)?["\']?(\w+\.\w+)["\']?', message, re.I)
            if match:
                filename = match.group(1)
                return f"NEED_CODE_FOR:{filename}"
        
        # File reading
        if 'read' in msg or 'show' in msg:
            match = re.search(r'(\w+\.\w+)', message)
            if match:
                return self.tools.read_file(match.group(1))
        
        # List directory
        if 'list' in msg and ('file' in msg or 'directory' in msg):
            return self.tools.list_files()
        
        # Execute command
        if 'execute' in msg or 'run' in msg:
            match = re.search(r'(?:execute|run)[:\s]+(.+)', message, re.I)
            if match:
                return self.tools.execute_bash(match.group(1).strip())
        
        return None
    
    def call_llm(self, agent: Agent, user_message: str) -> str:
        """Call LLM with specific agent context"""
        messages = [{"role": "system", "content": agent.get_system_prompt()}]
        messages.extend(self.conversation[-10:])  # Last 10 messages for context
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": agent.model, "messages": messages, "max_tokens": 2000},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"].get("content", "").strip()
        except Exception as e:
            pass
        
        return ""
    
    def process(self, user_message: str) -> str:
        """Process message with full capability"""
        
        # 1. Detect intent
        agent_type, needs_tools = self.detect_intent(user_message)
        self.current_agent = self.agents[agent_type]
        
        agent_emoji = {
            AgentType.CHAT: "💬",
            AgentType.DEVOPS: "🚀",
            AgentType.CODER: "💻",
            AgentType.DEBUGGER: "🔧",
            AgentType.RESEARCHER: "📚",
        }
        
        print(f"{B}🤖 Agent: {agent_emoji[agent_type]} {agent_type.value}{RESET}")
        
        # 2. Check if tool execution needed
        if needs_tools:
            tool_result = self.execute_tool(user_message)
            
            if tool_result:
                if tool_result.startswith("NEED_CODE_FOR:"):
                    filename = tool_result.split(":")[1]
                    print(f"{Y}🔧 Generating code for {filename}...{RESET}")
                    
                    # Get code from LLM
                    code = self.call_llm(self.agents[AgentType.CODER], user_message)
                    
                    # Extract code block
                    match = re.search(r'```(?:python)?\n(.*?)```', code, re.DOTALL)
                    if match:
                        code_content = match.group(1)
                        result = self.tools.create_file(filename, code_content)
                        
                        # Update conversation
                        self.conversation.append({"role": "user", "content": user_message})
                        self.conversation.append({"role": "assistant", "content": f"Created {filename} with generated code"})
                        
                        return f"{result}\n\n{G}Preview:{RESET}\n{code_content[:300]}..."
                    else:
                        return f"Generated response but no code block found:\n{code[:200]}"
                else:
                    # Direct tool result
                    self.conversation.append({"role": "user", "content": user_message})
                    self.conversation.append({"role": "assistant", "content": tool_result})
                    return tool_result
        
        # 3. Regular conversation
        response = self.call_llm(self.current_agent, user_message)
        
        if response:
            self.conversation.append({"role": "user", "content": user_message})
            self.conversation.append({"role": "assistant", "content": response})
            return response
        
        return "❌ No response generated"

# =============================================================================
# MAIN
# =============================================================================

def main():
    print(f"{BOLD}{C}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{C}║  🌀 SPIRAL UNIFIED - One Chat, All Powers                ║{RESET}")
    print(f"{BOLD}{C}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    
    agent = UnifiedAgent()
    
    # Check services
    print(f"{M}Checking backend services...{RESET}")
    print(agent.tools.check_services())
    
    print(f"\n{M}💬 Chat • 🚀 DevOps • 💻 Coder • 🔧 Debugger • 📚 Researcher{RESET}")
    print(f"{M}🔧 Tools: file ops, bash, multi-agent coordination{RESET}\n")
    
    while True:
        try:
            user_input = input(f"{C}You: {RESET}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Y}👋 Goodbye Declan!{RESET}")
                break
            
            # Special commands
            if user_input == '/services':
                print(agent.tools.check_services())
                continue
            elif user_input == '/files':
                print(agent.tools.list_files())
                continue
            
            response = agent.process(user_input)
            print(f"{G}Spiral: {RESET}{response}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Y}👋 Goodbye!{RESET}")
            break
        except Exception as e:
            print(f"{R}Error: {e}{RESET}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
