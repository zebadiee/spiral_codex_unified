#!/usr/bin/env python3
"""
SPIRAL SELF-DELEGATING CHAT - Knows its limits and delegates automatically
When asked to do something beyond its capabilities, it invokes the right agent.
"""
import requests
import json
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path

# Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]

# Colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

# =============================================================================
# ACTION DETECTION - What the user is REALLY asking for
# =============================================================================

class ActionType(Enum):
    """Types of actions user might request"""
    CHAT = "chat"                    # Just talking
    CREATE_FILE = "create_file"      # Needs file creation
    EXECUTE_CODE = "execute_code"    # Needs code execution
    READ_FILE = "read_file"          # Needs file reading
    ANALYZE_CODE = "analyze_code"    # Code analysis
    DEBUG = "debug"                  # Debugging help

class ActionDetector:
    """Detects what action is REALLY needed"""
    
    ACTION_PATTERNS = {
        ActionType.CREATE_FILE: [
            r"create.*file", r"write.*file", r"save.*to.*file",
            r"put.*in.*file", r"make.*file", r"generate.*file"
        ],
        ActionType.EXECUTE_CODE: [
            r"run.*code", r"execute.*", r"test.*code",
            r"try.*code", r"run this"
        ],
        ActionType.READ_FILE: [
            r"read.*file", r"show.*file", r"what's in",
            r"content of", r"open.*file"
        ],
        ActionType.DEBUG: [
            r"error", r"bug", r"not working", r"broken",
            r"fix", r"problem", r"issue"
        ],
    }
    
    @staticmethod
    def detect(message: str) -> ActionType:
        """Detect what action the user really wants"""
        msg_lower = message.lower()
        
        for action_type, patterns in ActionDetector.ACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, msg_lower):
                    return action_type
        
        return ActionType.CHAT

# =============================================================================
# TOOL EXECUTOR - Actually does file operations
# =============================================================================

class ToolExecutor:
    """Executes file and code operations"""
    
    @staticmethod
    def create_file(filename: str, content: str) -> str:
        """Create a file with content"""
        try:
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)
            return f"✅ Created {filename} ({len(content)} bytes)"
        except Exception as e:
            return f"❌ Error creating file: {e}"
    
    @staticmethod
    def read_file(filename: str) -> str:
        """Read file contents"""
        try:
            content = Path(filename).read_text()
            return f"✅ Read {filename}:\n\n{content[:500]}..."
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    @staticmethod
    def execute_code(code: str, language: str = "python") -> str:
        """Execute code safely"""
        try:
            if language == "python":
                result = subprocess.run(
                    ["python", "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return f"✅ Execution result:\n{result.stdout}\n{result.stderr}"
            return "❌ Language not supported yet"
        except Exception as e:
            return f"❌ Execution error: {e}"

# =============================================================================
# SELF-AWARE DELEGATING AGENT
# =============================================================================

class SelfDelegatingAgent:
    """
    This agent:
    1. Detects what you REALLY want
    2. Knows its own capabilities
    3. Delegates to tools when needed
    4. Reports what it did
    """
    
    def __init__(self):
        self.conversation = []
        self.current_model = MODELS[0]
        self.tool_executor = ToolExecutor()
        
    def call_llm(self, messages: List[Dict]) -> Optional[str]:
        """Call LLM for text generation"""
        try:
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": self.current_model, "messages": messages},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"].get("content", "").strip()
            return None
        except:
            return None
    
    def extract_code_from_response(self, response: str) -> Optional[Tuple[str, str]]:
        """Extract code blocks from LLM response"""
        # Look for ```python ... ``` blocks
        pattern = r"```(?:python)?\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            return "python", matches[0]
        return None
    
    def extract_filename_from_message(self, message: str) -> Optional[str]:
        """Extract filename from user message"""
        # Look for common filename patterns
        patterns = [
            r"(?:create|write|save|make).*?(?:file|to)\s+['\"]?(\w+\.\w+)['\"]?",
            r"['\"]?(\w+\.\w+)['\"]?",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def process(self, user_message: str) -> str:
        """Process user message with self-awareness"""
        
        # 1. Detect what action is needed
        action = ActionDetector.detect(user_message)
        
        print(f"{BLUE}🔍 Detected action: {action.value}{RESET}")
        
        # 2. Handle based on detected action
        if action == ActionType.CREATE_FILE:
            return self.handle_file_creation(user_message)
        elif action == ActionType.EXECUTE_CODE:
            return self.handle_code_execution(user_message)
        elif action == ActionType.READ_FILE:
            return self.handle_file_reading(user_message)
        else:
            return self.handle_chat(user_message)
    
    def handle_file_creation(self, message: str) -> str:
        """Handle file creation request"""
        print(f"{YELLOW}🔧 Delegating to FileWriter tool...{RESET}")
        
        # Ask LLM to generate the code
        prompt = [
            {"role": "system", "content": "You are a code generator. Generate clean, working code based on the user's request."},
            {"role": "user", "content": message}
        ]
        
        code_response = self.call_llm(prompt)
        
        if not code_response:
            return "❌ Failed to generate code"
        
        # Extract code from response
        code_block = self.extract_code_from_response(code_response)
        
        if not code_block:
            return f"❌ No code block found in response:\n{code_response}"
        
        language, code = code_block
        
        # Extract filename
        filename = self.extract_filename_from_message(message) or "output.py"
        
        # Create the file
        result = self.tool_executor.create_file(filename, code)
        
        return f"{result}\n\n{GREEN}Preview:{RESET}\n{code[:300]}..."
    
    def handle_code_execution(self, message: str) -> str:
        """Handle code execution request"""
        print(f"{YELLOW}🔧 Delegating to CodeExecutor tool...{RESET}")
        
        # Extract code from message or previous context
        code_block = self.extract_code_from_response(message)
        
        if code_block:
            language, code = code_block
            return self.tool_executor.execute_code(code, language)
        
        return "❌ No code found to execute"
    
    def handle_file_reading(self, message: str) -> str:
        """Handle file reading request"""
        print(f"{YELLOW}🔧 Delegating to FileReader tool...{RESET}")
        
        filename = self.extract_filename_from_message(message)
        
        if filename:
            return self.tool_executor.read_file(filename)
        
        return "❌ No filename specified"
    
    def handle_chat(self, message: str) -> str:
        """Handle regular chat"""
        messages = [
            {"role": "system", "content": "You are Spiral, a helpful AI assistant."}
        ]
        messages.extend(self.conversation)
        messages.append({"role": "user", "content": message})
        
        response = self.call_llm(messages)
        
        if response:
            self.conversation.append({"role": "user", "content": message})
            self.conversation.append({"role": "assistant", "content": response})
            return response
        
        return "❌ Failed to get response"

# =============================================================================
# MAIN
# =============================================================================

def main():
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║  🧠 SPIRAL SELF-DELEGATING AGENT                        ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    print(f"{MAGENTA}🎯 Action Detection: ON{RESET}")
    print(f"{MAGENTA}🔧 Tool Delegation: AUTOMATIC{RESET}")
    print(f"{MAGENTA}🧠 Self-Awareness: ACTIVE{RESET}\n")
    
    agent = SelfDelegatingAgent()
    
    while True:
        try:
            user_input = input(f"{CYAN}You: {RESET}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{YELLOW}👋 Goodbye!{RESET}")
                break
            
            response = agent.process(user_input)
            print(f"{GREEN}Spiral: {RESET}{response}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}👋 Interrupted!{RESET}")
            break
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}\n")

if __name__ == "__main__":
    main()
