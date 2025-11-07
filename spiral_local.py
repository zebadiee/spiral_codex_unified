#!/usr/bin/env python3
"""
SPIRAL LOCAL - Uses Ollama for FAST local inference
No more rate limits! 🚀
"""
import requests
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Ollama configuration
OLLAMA_ENDPOINT = "http://localhost:11434"
OLLAMA_MODELS = {
    "fast": "mistral:latest",      # Fast responses
    "smart": "llama3.1:8b",        # Better quality
}

# Colors
C = "\033[36m"
G = "\033[32m"
Y = "\033[33m"
R = "\033[31m"
B = "\033[34m"
M = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

# =============================================================================
# AGENTS
# =============================================================================

class AgentType(Enum):
    CHAT = "chat"
    DEVOPS = "devops"
    CODER = "coder"
    DEBUGGER = "debugger"

class Agent:
    def __init__(self, agent_type: AgentType):
        self.type = agent_type
        self.prompts = {
            AgentType.CHAT: "You are Spiral, a helpful AI assistant. Be concise and friendly.",
            AgentType.DEVOPS: "You are a DevOps expert. Focus on Docker, K8s, CI/CD, and infrastructure. Be practical.",
            AgentType.CODER: "You are an expert developer. Write clean, production-ready code. Always use code blocks with ```python",
            AgentType.DEBUGGER: "You are a debugging specialist. Analyze problems systematically.",
        }
    
    def get_prompt(self) -> str:
        return self.prompts.get(self.type, self.prompts[AgentType.CHAT])

# =============================================================================
# TOOLS
# =============================================================================

class Tools:
    @staticmethod
    def create_file(filename: str, content: str) -> str:
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            Path(filename).write_text(content)
            return f"✅ Created {filename} ({len(content)} bytes)"
        except Exception as e:
            return f"❌ Error: {e}"
    
    @staticmethod
    def read_file(filename: str) -> str:
        try:
            content = Path(filename).read_text()
            preview = content[:500] + "..." if len(content) > 500 else content
            return f"✅ {filename}:\n\n{preview}"
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
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = (result.stdout + result.stderr).strip()
            return f"✅ Executed: {command}\n{output[:500]}"
        except Exception as e:
            return f"❌ Error: {e}"

# =============================================================================
# OLLAMA CLIENT
# =============================================================================

class OllamaClient:
    def __init__(self, model: str = "smart"):
        self.model = OLLAMA_MODELS.get(model, OLLAMA_MODELS["smart"])
    
    def generate(self, prompt: str, system: str = "") -> str:
        """Generate response using Ollama"""
        try:
            response = requests.post(
                f"{OLLAMA_ENDPOINT}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2000,
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            return ""
        except Exception as e:
            return f"Error: {e}"

# =============================================================================
# UNIFIED LOCAL AGENT
# =============================================================================

class SpiralLocal:
    def __init__(self):
        self.ollama = OllamaClient("smart")
        self.agents = {
            AgentType.CHAT: Agent(AgentType.CHAT),
            AgentType.DEVOPS: Agent(AgentType.DEVOPS),
            AgentType.CODER: Agent(AgentType.CODER),
            AgentType.DEBUGGER: Agent(AgentType.DEBUGGER),
        }
        self.tools = Tools()
        self.conversation = []
    
    def detect_intent(self, message: str) -> Tuple[AgentType, bool]:
        """Detect agent and tool needs"""
        msg = message.lower()
        
        needs_tools = any(word in msg for word in [
            'create', 'write', 'save', 'read', 'show', 'file', 
            'execute', 'run', 'list'
        ])
        
        if any(word in msg for word in ['deploy', 'docker', 'kubernetes', 'container']):
            return AgentType.DEVOPS, needs_tools
        elif any(word in msg for word in ['code', 'function', 'write', 'build', 'implement']):
            return AgentType.CODER, needs_tools
        elif any(word in msg for word in ['error', 'bug', 'fix', 'problem', 'debug']):
            return AgentType.DEBUGGER, needs_tools
        else:
            return AgentType.CHAT, needs_tools
    
    def extract_code(self, text: str) -> Optional[str]:
        """Extract code from markdown blocks"""
        match = re.search(r'```(?:python)?\n(.*?)```', text, re.DOTALL)
        return match.group(1) if match else None
    
    def extract_filename(self, message: str) -> Optional[str]:
        """Extract filename from message"""
        match = re.search(r'(?:create|write|save).*?(?:file)?\s+(?:called\s+)?["\']?(\w+\.\w+)["\']?', message, re.I)
        return match.group(1) if match else None
    
    def process(self, user_message: str) -> str:
        """Process message with Ollama"""
        
        # Detect intent
        agent_type, needs_tools = self.detect_intent(user_message)
        agent = self.agents[agent_type]
        
        emoji = {
            AgentType.CHAT: "💬",
            AgentType.DEVOPS: "🚀",
            AgentType.CODER: "💻",
            AgentType.DEBUGGER: "🔧",
        }
        
        print(f"{B}🤖 Agent: {emoji[agent_type]} {agent_type.value}{RESET}")
        
        # Handle tool operations
        if needs_tools:
            # File creation
            if 'create' in user_message.lower() and 'file' in user_message.lower():
                filename = self.extract_filename(user_message)
                if filename:
                    print(f"{Y}🔧 Generating code for {filename}...{RESET}")
                    
                    # Build context
                    context = "\n".join([f"{m['role']}: {m['content'][:100]}" for m in self.conversation[-3:]])
                    prompt = f"Context:\n{context}\n\nUser request: {user_message}\n\nGenerate ONLY the code with proper ```python blocks."
                    
                    response = self.ollama.generate(prompt, agent.get_prompt())
                    
                    code = self.extract_code(response)
                    if code:
                        result = self.tools.create_file(filename, code)
                        self.conversation.append({"role": "user", "content": user_message})
                        self.conversation.append({"role": "assistant", "content": f"Created {filename}"})
                        return f"{result}\n\n{G}Preview:{RESET}\n{code[:300]}..."
                    else:
                        return f"Generated response:\n{response[:500]}"
            
            # File reading
            elif 'read' in user_message.lower() or 'show' in user_message.lower():
                filename = self.extract_filename(user_message)
                if filename:
                    return self.tools.read_file(filename)
            
            # List files
            elif 'list' in user_message.lower():
                return self.tools.list_files()
            
            # Execute command
            elif 'execute' in user_message.lower() or 'run' in user_message.lower():
                match = re.search(r'(?:execute|run)[:\s]+(.+)', user_message, re.I)
                if match:
                    return self.tools.execute_bash(match.group(1).strip())
        
        # Regular conversation
        context = "\n".join([f"{m['role']}: {m['content']}" for m in self.conversation[-5:]])
        prompt = f"{context}\n\nuser: {user_message}\n\nassistant:"
        
        response = self.ollama.generate(prompt, agent.get_prompt())
        
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
    print(f"{BOLD}{C}║  🌀 SPIRAL LOCAL - Ollama Powered (NO RATE LIMITS!)     ║{RESET}")
    print(f"{BOLD}{C}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    
    # Check Ollama
    try:
        resp = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=2)
        if resp.status_code == 200:
            print(f"{G}✅ Ollama: Connected{RESET}")
            models = resp.json().get("models", [])
            for model in models[:2]:
                print(f"{M}   • {model['name']}{RESET}")
        else:
            print(f"{R}❌ Ollama: Not responding{RESET}")
            return
    except:
        print(f"{R}❌ Ollama: Not running (start with: ollama serve){RESET}")
        return
    
    print(f"\n{M}💬 Chat • 🚀 DevOps • 💻 Coder • 🔧 Debugger{RESET}")
    print(f"{M}🔧 Tools: Local models, file ops, bash{RESET}\n")
    
    agent = SpiralLocal()
    
    while True:
        try:
            user_input = input(f"{C}You: {RESET}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Y}👋 Goodbye Declan!{RESET}")
                break
            
            if user_input == '/files':
                print(agent.tools.list_files())
                continue
            
            response = agent.process(user_input)
            print(f"{G}Spiral: {RESET}{response}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Y}👋 Goodbye!{RESET}")
            break
        except Exception as e:
            print(f"{R}Error: {e}{RESET}\n")

if __name__ == "__main__":
    main()
