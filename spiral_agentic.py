#!/usr/bin/env python3
"""
SPIRAL AGENTIC CHAT - Full Tool-Enabled AI Assistant
Connects all Genesis v2 components with file ops, code execution, and reasoning
"""
import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Models that support function calling
TOOL_CAPABLE_MODELS = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4-turbo",
    "google/gemini-pro",
    "deepseek/deepseek-chat-v3.1:free",
]

CURRENT_MODEL = TOOL_CAPABLE_MODELS[3]  # DeepSeek supports tools

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
# TOOL DEFINITIONS
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Execute a bash command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Bash command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List contents of a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Create a new project with scaffolding",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "type": {
                        "type": "string",
                        "description": "Project type (python, node, go, etc)",
                        "enum": ["python", "node", "go", "rust", "web"]
                    }
                },
                "required": ["name", "type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run tests in a project",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Project path"
                    },
                    "test_command": {
                        "type": "string",
                        "description": "Test command (pytest, npm test, etc)"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Check git status of a repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Repository path"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Commit changes to git",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Repository path"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message"
                    }
                },
                "required": ["path", "message"]
            }
        }
    }
]

# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================

def read_file(path: str) -> str:
    """Read file contents"""
    try:
        with open(path, 'r') as f:
            content = f.read()
        return f"✅ Read {len(content)} chars from {path}\n\n{content[:500]}..."
    except Exception as e:
        return f"❌ Error reading {path}: {e}"

def write_file(path: str, content: str) -> str:
    """Write content to file"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"✅ Wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"❌ Error writing {path}: {e}"

def execute_bash(command: str) -> str:
    """Execute bash command"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return f"✅ Executed: {command}\n\n{output[:1000]}"
    except subprocess.TimeoutExpired:
        return f"⏱️ Command timed out: {command}"
    except Exception as e:
        return f"❌ Error executing: {e}"

def list_directory(path: str) -> str:
    """List directory contents"""
    try:
        items = os.listdir(path)
        return f"✅ Directory {path}:\n" + "\n".join(f"  • {item}" for item in sorted(items)[:50])
    except Exception as e:
        return f"❌ Error listing {path}: {e}"

def create_project(name: str, type: str) -> str:
    """Create project scaffolding"""
    try:
        project_path = Path(name)
        project_path.mkdir(exist_ok=True)
        
        if type == "python":
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "tests").mkdir(exist_ok=True)
            (project_path / "README.md").write_text(f"# {name}\n\nPython project")
            (project_path / "requirements.txt").write_text("")
            (project_path / "setup.py").write_text(f'from setuptools import setup\nsetup(name="{name}")')
        elif type == "node":
            subprocess.run(["npm", "init", "-y"], cwd=project_path, capture_output=True)
        
        return f"✅ Created {type} project: {name}"
    except Exception as e:
        return f"❌ Error creating project: {e}"

def run_tests(path: str, test_command: str = None) -> str:
    """Run tests"""
    try:
        cmd = test_command or "pytest"
        result = subprocess.run(cmd, shell=True, cwd=path, capture_output=True, text=True, timeout=60)
        return f"✅ Tests:\n{result.stdout[:1000]}"
    except Exception as e:
        return f"❌ Test error: {e}"

def git_status(path: str) -> str:
    """Git status"""
    try:
        result = subprocess.run(["git", "status", "--short"], cwd=path, capture_output=True, text=True)
        return f"✅ Git status:\n{result.stdout}"
    except Exception as e:
        return f"❌ Git error: {e}"

def git_commit(path: str, message: str) -> str:
    """Git commit"""
    try:
        subprocess.run(["git", "add", "-A"], cwd=path, check=True)
        result = subprocess.run(["git", "commit", "-m", message], cwd=path, capture_output=True, text=True)
        return f"✅ Committed: {message}\n{result.stdout}"
    except Exception as e:
        return f"❌ Commit error: {e}"

# Tool dispatcher
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "execute_bash": execute_bash,
    "list_directory": list_directory,
    "create_project": create_project,
    "run_tests": run_tests,
    "git_status": git_status,
    "git_commit": git_commit,
}

# =============================================================================
# MAIN CHAT LOOP
# =============================================================================

def call_openrouter(messages: List[Dict], use_tools: bool = True) -> Dict:
    """Call OpenRouter API with optional tools"""
    payload = {
        "model": CURRENT_MODEL,
        "messages": messages
    }
    
    if use_tools:
        payload["tools"] = TOOLS
        payload["tool_choice"] = "auto"
    
    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://omarchy.local",
            "X-Title": "Spiral Agentic Chat"
        },
        json=payload,
        timeout=60
    )
    
    return response.json()

def execute_tool_calls(tool_calls: List[Dict]) -> List[Dict]:
    """Execute tool calls and return results"""
    results = []
    
    for tool_call in tool_calls:
        func_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        print(f"{YELLOW}🔧 Calling: {func_name}({arguments}){RESET}")
        
        if func_name in TOOL_FUNCTIONS:
            result = TOOL_FUNCTIONS[func_name](**arguments)
            print(f"{BLUE}{result[:200]}...{RESET}\n")
            
            results.append({
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": func_name,
                "content": result
            })
        else:
            results.append({
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": func_name,
                "content": f"❌ Unknown tool: {func_name}"
            })
    
    return results

def main():
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║  🌀 SPIRAL AGENTIC CHAT - Full Tool Integration         ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    
    print(f"{GREEN}Model: {CURRENT_MODEL}{RESET}")
    print(f"{GREEN}Tools: {len(TOOLS)} functions available{RESET}")
    print(f"{MAGENTA}I can read/write files, execute code, manage git, and more!{RESET}\n")
    
    conversation = [
        {
            "role": "system",
            "content": """You are Spiral, an advanced AI assistant with tool-using capabilities.

You can:
- Read and write files
- Execute bash commands
- Create and manage projects
- Run tests and manage git repositories

When a user asks you to perform actions, use your tools proactively.
Be helpful, precise, and always confirm actions before executing them.
You're running on the Spiral Codex Genesis Architecture v2."""
        }
    ]
    
    while True:
        try:
            user_input = input(f"{CYAN}🌀 You:{RESET} ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{YELLOW}👋 Shutting down Spiral Agentic Chat{RESET}")
                break
            
            conversation.append({"role": "user", "content": user_input})
            
            # Main reasoning loop with tool use
            max_iterations = 5
            for iteration in range(max_iterations):
                response = call_openrouter(conversation)
                
                if "error" in response:
                    print(f"{RED}❌ API Error: {response['error']}{RESET}\n")
                    conversation.pop()
                    break
                
                message = response["choices"][0]["message"]
                
                # Check if AI wants to use tools
                if message.get("tool_calls"):
                    conversation.append(message)
                    
                    # Execute tools
                    tool_results = execute_tool_calls(message["tool_calls"])
                    conversation.extend(tool_results)
                    
                    # Continue loop to get final response
                    continue
                
                # No more tools, final response
                if message.get("content"):
                    conversation.append(message)
                    print(f"\n{GREEN}🤖 Spiral:{RESET} {message['content']}\n")
                
                break
            
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}👋 Interrupted. Goodbye!{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}❌ Error: {e}{RESET}\n")
            if conversation and conversation[-1]["role"] == "user":
                conversation.pop()

if __name__ == "__main__":
    main()
