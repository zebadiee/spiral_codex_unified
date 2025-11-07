#!/usr/bin/env python3
"""
SPIRAL HYBRID - Smart model selection
Priority: Online (fast) → Local (fallback)
"""
import requests
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time

# Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_ENDPOINT = "http://localhost:11434"

# Online models (PRIORITY - fast and good)
ONLINE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

# Local models (FALLBACK - slower but reliable)
LOCAL_MODELS = {
    "smart": "llama3.1:8b",
    "fast": "mistral:latest",
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
            AgentType.DEVOPS: "You are a DevOps expert. Focus on Docker, K8s, CI/CD, and infrastructure. Be practical and provide commands.",
            AgentType.CODER: "You are an expert developer. Write clean, production-ready code. Always use code blocks with ```python",
            AgentType.DEBUGGER: "You are a debugging specialist. Analyze problems systematically and provide solutions.",
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
# HYBRID MODEL ROUTER
# =============================================================================

class HybridRouter:
    """Smart router: tries online first, falls back to local"""
    
    def __init__(self):
        self.current_online_model = 0
        self.online_available = True
        self.local_available = self.check_ollama()
        self.last_online_check = 0
        self.stats = {"online_success": 0, "online_fail": 0, "local_used": 0}
    
    def check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            resp = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=2)
            return resp.status_code == 200
        except:
            return False
    
    def call_online(self, messages: List[Dict], max_retries: int = 3) -> Optional[str]:
        """Try online models with rotation"""
        for attempt in range(max_retries):
            model = ONLINE_MODELS[self.current_online_model]
            
            try:
                response = requests.post(
                    OPENROUTER_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"model": model, "messages": messages, "max_tokens": 2000},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"].get("content", "").strip()
                        if content:
                            self.stats["online_success"] += 1
                            return content
                
                # Rate limited or error - rotate
                if response.status_code == 429:
                    self.current_online_model = (self.current_online_model + 1) % len(ONLINE_MODELS)
                    continue
                    
            except Exception as e:
                pass
            
            self.current_online_model = (self.current_online_model + 1) % len(ONLINE_MODELS)
        
        self.stats["online_fail"] += 1
        return None
    
    def call_local(self, prompt: str, system: str = "") -> Optional[str]:
        """Use local Ollama model"""
        if not self.local_available:
            return None
        
        try:
            response = requests.post(
                f"{OLLAMA_ENDPOINT}/api/generate",
                json={
                    "model": LOCAL_MODELS["smart"],
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 2000}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                self.stats["local_used"] += 1
                return response.json().get("response", "")
        except:
            pass
        
        return None
    
    def generate(self, messages: List[Dict]) -> Tuple[str, str]:
        """
        Generate response with priority routing
        Returns: (response, source) where source is 'online' or 'local'
        """
        # Try online first (FAST!)
        response = self.call_online(messages)
        if response:
            return response, "online"
        
        # Fall back to local (RELIABLE!)
        print(f"{Y}⚠️  Online unavailable, using local Ollama...{RESET}")
        
        # Convert messages to prompt for Ollama
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages if m["role"] != "system"])
        
        response = self.call_local(prompt, system)
        if response:
            return response, "local"
        
        return "", "failed"
    
    def get_stats(self) -> str:
        """Get usage statistics"""
        total = self.stats["online_success"] + self.stats["local_used"]
        if total == 0:
            return "No requests yet"
        
        online_pct = (self.stats["online_success"] / total) * 100
        local_pct = (self.stats["local_used"] / total) * 100
        
        return f"Online: {self.stats['online_success']} ({online_pct:.0f}%) | Local: {self.stats['local_used']} ({local_pct:.0f}%)"

# =============================================================================
# UNIFIED HYBRID AGENT
# =============================================================================

class SpiralHybrid:
    def __init__(self):
        self.router = HybridRouter()
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
        """Process message with hybrid routing"""
        
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
                    
                    messages = [
                        {"role": "system", "content": agent.get_prompt()},
                        {"role": "user", "content": f"{user_message}\n\nGenerate ONLY the code with proper ```python blocks."}
                    ]
                    
                    response, source = self.router.generate(messages)
                    print(f"{M}📡 Source: {source}{RESET}")
                    
                    code = self.extract_code(response)
                    if code:
                        result = self.tools.create_file(filename, code)
                        self.conversation.append({"role": "user", "content": user_message})
                        self.conversation.append({"role": "assistant", "content": f"Created {filename}"})
                        return f"{result}\n\n{G}Preview:{RESET}\n{code[:300]}..."
                    else:
                        return f"Generated response but no code block:\n{response[:500]}"
            
            # File reading
            elif 'read' in user_message.lower() or 'show' in user_message.lower():
                match = re.search(r'(\w+\.\w+)', user_message)
                if match:
                    return self.tools.read_file(match.group(1))
            
            # List files
            elif 'list' in user_message.lower():
                return self.tools.list_files()
            
            # Execute command
            elif 'execute' in user_message.lower() or 'run' in user_message.lower():
                match = re.search(r'(?:execute|run)[:\s]+(.+)', user_message, re.I)
                if match:
                    return self.tools.execute_bash(match.group(1).strip())
        
        # Regular conversation
        messages = [{"role": "system", "content": agent.get_prompt()}]
        messages.extend(self.conversation[-5:])
        messages.append({"role": "user", "content": user_message})
        
        response, source = self.router.generate(messages)
        print(f"{M}📡 Source: {source}{RESET}")
        
        if response:
            self.conversation.append({"role": "user", "content": user_message})
            self.conversation.append({"role": "assistant", "content": response})
            return response
        
        return "❌ No response generated from online or local"

# =============================================================================
# MAIN
# =============================================================================

def main():
    print(f"{BOLD}{C}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{C}║  🌀 SPIRAL HYBRID - Smart Online/Local Routing          ║{RESET}")
    print(f"{BOLD}{C}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    
    agent = SpiralHybrid()
    
    # Show capabilities
    print(f"{G}✅ Online: OpenRouter (4 models){RESET}")
    if agent.router.local_available:
        print(f"{G}✅ Local: Ollama (fallback){RESET}")
    else:
        print(f"{Y}⚠️  Local: Ollama not available{RESET}")
    
    print(f"\n{M}💬 Chat • 🚀 DevOps • 💻 Coder • 🔧 Debugger{RESET}")
    print(f"{M}🔧 Tools: file ops, bash, hybrid routing{RESET}")
    print(f"{M}📊 Strategy: Online FIRST (fast) → Local FALLBACK (reliable){RESET}\n")
    
    while True:
        try:
            user_input = input(f"{C}You: {RESET}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Y}📊 Session stats: {agent.router.get_stats()}{RESET}")
                print(f"{Y}👋 Goodbye Declan!{RESET}")
                break
            
            if user_input == '/stats':
                print(agent.router.get_stats())
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

if __name__ == "__main__":
    main()
