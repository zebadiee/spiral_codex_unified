#!/usr/bin/env python3
"""
🚀 SPIRAL AGENTIC ORCHESTRATOR - Multi-Agent Coordination System
Connects all Genesis v2 components with advanced multi-agent coordination
"""
import os
import sys
import json
import subprocess
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests
from datetime import datetime
import logging

# =============================================================================
# CONFIGURATION
# =============================================================================

OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Spiral Codex Service Endpoints
REASONING_HUB_URL = "http://localhost:8000"
NEURAL_BUS_URL = "http://localhost:9000"
OMAI_URL = "http://localhost:7016"

# Multi-Agent Models - Specialized for different tasks
SPECIALIZED_AGENTS = {
    "ƒCODEX": {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "specialty": "code_generation, debugging, architecture",
        "tools": ["read_file", "write_file", "execute_bash", "run_tests", "git_commit"]
    },
    "ƒCLAUDE": {
        "model": "anthropic/claude-3.5-sonnet",
        "specialty": "analysis, reasoning, planning",
        "tools": ["read_file", "write_file", "reasoning_analysis"]
    },
    "ƒOMAI": {
        "model": "z-ai/glm-4.5-air:free",
        "specialty": "knowledge, context, research",
        "tools": ["search_knowledge", "context_enrichment", "information_synthesis"]
    },
    "ƒEXECUTOR": {
        "model": "openai/gpt-4-turbo",
        "specialty": "task_execution, project_management",
        "tools": ["execute_bash", "create_project", "run_tests", "git_status", "git_commit"]
    }
}

DEFAULT_AGENT = "ƒCODEX"

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
# MULTI-AGENT COORDINATION SYSTEM
# =============================================================================

class MultiAgentOrchestrator:
    """Orchestrates multiple specialized AI agents"""

    def __init__(self):
        self.active_agents = {}
        self.task_queue = asyncio.Queue()
        self.results_cache = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def select_best_agent(self, task: str, context: str = "") -> str:
        """Select the best agent for a given task"""
        task_lower = task.lower()

        # Simple heuristic-based agent selection
        if any(keyword in task_lower for keyword in ["code", "debug", "program", "function", "class", "algorithm"]):
            return "ƒCODEX"
        elif any(keyword in task_lower for keyword in ["analyze", "plan", "reason", "think", "design", "architecture"]):
            return "ƒCLAUDE"
        elif any(keyword in task_lower for keyword in ["research", "search", "find", "context", "knowledge", "information"]):
            return "ƒOMAI"
        elif any(keyword in task_lower for keyword in ["execute", "run", "build", "test", "deploy", "project"]):
            return "ƒEXECUTOR"
        else:
            return DEFAULT_AGENT

    async def coordinate_agents(self, task: str, context: str = "") -> Dict:
        """Coordinate multiple agents for complex tasks"""
        # For now, use simple single-agent selection
        # Future: Implement multi-agent collaboration
        selected_agent = self.select_best_agent(task, context)

        return {
            "primary_agent": selected_agent,
            "model": SPECIALIZED_AGENTS[selected_agent]["model"],
            "specialty": SPECIALIZED_AGENTS[selected_agent]["specialty"],
            "tools": SPECIALIZED_AGENTS[selected_agent]["tools"]
        }

    async def broadcast_task_completion(self, task: str, agent: str, result: str):
        """Broadcast task completion to Neural Bus"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "type": "agent_task_completion",
                    "source": "agentic_orchestrator",
                    "agent": agent,
                    "task": task,
                    "result_summary": result[:200] + "..." if len(result) > 200 else result,
                    "timestamp": datetime.now().isoformat()
                }

                async with session.post(f"{NEURAL_BUS_URL}/events",
                                       json=payload, timeout=2) as response:
                    if response.status == 200:
                        logging.info(f"Broadcasted task completion from {agent}")
        except Exception as e:
            logging.warning(f"Failed to broadcast to Neural Bus: {e}")

# =============================================================================
# ENHANCED AI CAPABILITIES
# =============================================================================

async def get_reasoning_analysis(query: str, context: List[Dict]) -> Optional[Dict]:
    """Get analysis from Reasoning Hub"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query,
                "context": context,
                "mode": "systemic"
            }

            async with session.post(f"{REASONING_HUB_URL}/analyze",
                                   json=payload, timeout=5) as response:
                if response.status == 200:
                    return await response.json()
    except Exception as e:
        logging.warning(f"Reasoning Hub unavailable: {e}")
    return None

async def search_knowledge_base(query: str) -> Optional[List[Dict]]:
    """Search OMAi knowledge base"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query,
                "max_results": 5,
                "min_similarity": 0.6
            }

            async with session.post(f"{OMAI_URL}/search",
                                   json=payload, timeout=3) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("matches", [])
    except Exception as e:
        logging.warning(f"OMAi search failed: {e}")
    return None

# =============================================================================
# MAIN CHAT LOOP
# =============================================================================

def call_openrouter(messages: List[Dict], model: str = None, use_tools: bool = True) -> Dict:
    """Call OpenRouter API with optional tools"""
    payload = {
        "model": model or CURRENT_MODEL,
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
            "X-Title": "Spiral Agentic Orchestrator"
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

async def main():
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║  🚀 SPIRAL AGENTIC ORCHESTRATOR - Multi-Agent System      ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")

    print(f"{GREEN}🤖 Available Agents:{RESET}")
    for agent_name, agent_config in SPECIALIZED_AGENTS.items():
        print(f"  {MAGENTA}• {agent_name}{RESET}: {agent_config['specialty']}")
    print()

    print(f"{GREEN}🔗 Connected Services:{RESET}")
    print(f"  • Reasoning Hub: {REASONING_HUB_URL}")
    print(f"  • Neural Bus: {NEURAL_BUS_URL}")
    print(f"  • OMAi RAG: {OMAI_URL}")
    print()

    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()

    conversation = [
        {
            "role": "system",
            "content": f"""You are the Spiral Agentic Orchestrator, an advanced multi-agent coordination system.

Available Specialized Agents:
{json.dumps(SPECIALIZED_AGENTS, indent=2)}

You can:
- Select the best agent for each task
- Coordinate multiple agents for complex problems
- Read/write files, execute code, manage projects
- Access Reasoning Hub for analysis and OMAi for knowledge
- Use tools proactively to accomplish user goals

When given a task, analyze it and select the most appropriate agent.
Use tools and system integration to provide comprehensive assistance.
You're running on the Spiral Codex Genesis Architecture v2 with full multi-agent capabilities."""
        }
    ]

    while True:
        try:
            user_input = input(f"{CYAN}🌀 You:{RESET} ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{YELLOW}👋 Shutting down Spiral Agentic Orchestrator{RESET}")
                break

            # Select best agent for this task
            agent_selection = await orchestrator.coordinate_agents(user_input)
            selected_agent = agent_selection["primary_agent"]
            agent_model = agent_selection["model"]
            agent_specialty = agent_selection["specialty"]

            print(f"{MAGENTA}🎯 Selected Agent: {selected_agent} ({agent_specialty}){RESET}")

            # Get enhanced context from system services
            reasoning_analysis = await get_reasoning_analysis(user_input, conversation[-5:])
            knowledge_context = await search_knowledge_base(user_input)

            # Build enhanced system prompt with context
            enhanced_system_prompt = f"""You are {selected_agent}, a specialized AI agent.

Your specialty: {agent_specialty}
Your model: {agent_model}

Current task analysis from Reasoning Hub: {reasoning_analysis.get('analysis', 'Not available') if reasoning_analysis else 'Not available'}

Relevant knowledge from OMAi: {len(knowledge_context) if knowledge_context else 0} context items found

Use your specialized capabilities and available tools to help the user.
Be proactive in using tools when appropriate.
You're part of the Spiral Codex Genesis Architecture v2."""

            # Prepare messages with enhanced context
            enhanced_messages = [
                {"role": "system", "content": enhanced_system_prompt},
                *conversation[-10:]  # Last 10 messages for context
            ]

            conversation.append({"role": "user", "content": user_input})

            # Main reasoning loop with tool use and selected agent model
            max_iterations = 5
            for iteration in range(max_iterations):
                response = call_openrouter(enhanced_messages, model=agent_model)

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
                    enhanced_messages.extend(tool_results)

                    # Continue loop to get final response
                    continue

                # No more tools, final response
                if message.get("content"):
                    conversation.append(message)
                    print(f"\n{GREEN}🤖 {selected_agent}:{RESET} {message['content']}\n")

                    # Broadcast task completion
                    await orchestrator.broadcast_task_completion(user_input, selected_agent, message['content'])

                break

        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}👋 Interrupted. Goodbye!{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}❌ Error: {e}{RESET}\n")
            if conversation and conversation[-1]["role"] == "user":
                conversation.pop()

if __name__ == "__main__":
    # Install aiohttp if needed
    try:
        import aiohttp
    except ImportError:
        print(f"{YELLOW}📦 Installing aiohttp...{RESET}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp

    asyncio.run(main())
