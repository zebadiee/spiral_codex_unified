#!/usr/bin/env python3
"""
🌟 SPIRAL CONSCIOUS CHAT - Advanced AI Assistant
Integrates Reasoning Hub, Neural Bus, OMAi RAG, and Advanced Tools

This is the next-generation chat that leverages the full power of
Spiral Codex Genesis Architecture v2.
"""

import os
import sys
import json
import asyncio
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Add Spiral Codex to path
sys.path.insert(0, str(Path(__file__).parent))

# =============================================================================
# CONFIGURATION & IMPORTS
# =============================================================================

OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Advanced models with reasoning capabilities
MODELS = [
    "deepseek/deepseek-chat-v3.1:free",
    "z-ai/glm-4.5-air:free",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4-turbo"
]

CURRENT_MODEL = MODELS[0]  # Start with DeepSeek

# Spiral Codex Service Endpoints
REASONING_HUB_URL = "http://localhost:8000"
NEURAL_BUS_URL = "http://localhost:9000"
OMAI_URL = "http://localhost:7016"

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
# CONSCIOUS CHAT SYSTEM
# =============================================================================

class SpiralConsciousChat:
    """Advanced AI chat with full Spiral Codex integration"""

    def __init__(self):
        self.conversation = []
        self.context_cache = {}
        self.reasoning_cache = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = Path(f"logs/conscious_chat_{self.session_id}.log")

        # Create logs directory
        self.log_file.parent.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        print(f"{MAGENTA}🌟 SPIRAL CONSCIOUS CHAT{RESET}")
        print(f"{CYAN}🧠 Integrated with Genesis Architecture v2{RESET}")
        print(f"{GREEN}📝 Session: {self.session_id}{RESET}")
        print(f"{BLUE}🔗 Reasoning Hub: {REASONING_HUB_URL}{RESET}")
        print(f"{BLUE}🔗 Neural Bus: {NEURAL_BUS_URL}{RESET}")
        print(f"{BLUE}🔗 OMAi RAG: {OMAI_URL}{RESET}\n")

        # Check system health
        self._check_system_health()

    def _check_system_health(self):
        """Check health of all Spiral Codex services"""
        services = {
            "Reasoning Hub": REASONING_HUB_URL,
            "Neural Bus": NEURAL_BUS_URL,
            "OMAi RAG": OMAI_URL
        }

        print(f"{YELLOW}🔍 Checking System Health...{RESET}")

        for service, url in services.items():
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"{GREEN}✅ {service}: HEALTHY{RESET}")
                else:
                    print(f"{YELLOW}⚠️  {service}: DEGRADED ({response.status_code}){RESET}")
            except Exception as e:
                print(f"{RED}❌ {service}: OFFLINE{RESET}")

        print()

    async def get_reasoning_guidance(self, query: str) -> Optional[Dict]:
        """Get reasoning guidance from Reasoning Hub"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": query,
                    "context": self.conversation[-5:],  # Last 5 messages for context
                    "mode": "analytical"
                }

                async with session.post(f"{REASONING_HUB_URL}/reason",
                                       json=payload, timeout=5) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logging.warning(f"Reasoning Hub unavailable: {e}")
        return None

    async def get_omai_context(self, query: str) -> Optional[str]:
        """Get relevant context from OMAi RAG"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": query,
                    "max_results": 5,
                    "min_similarity": 0.7
                }

                async with session.post(f"{OMAI_URL}/search",
                                       json=payload, timeout=3) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("matches"):
                            context = "\n".join([
                                match["metadata"].get("text", "")[:200] + "..."
                                for match in result["matches"][:3]
                            ])
                            return context
        except Exception as e:
            logging.warning(f"OMAi RAG unavailable: {e}")
        return None

    async def broadcast_to_neural_bus(self, event_type: str, data: Dict):
        """Broadcast events to Neural Bus"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "type": event_type,
                    "source": "conscious_chat",
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                }

                async with session.post(f"{NEURAL_BUS_URL}/events",
                                       json=payload, timeout=2) as response:
                    if response.status == 200:
                        logging.info(f"Broadcasted {event_type} to Neural Bus")
        except Exception as e:
            logging.warning(f"Neural Bus broadcast failed: {e}")

    def execute_file_operation(self, operation: str, path: str, content: str = None) -> Dict:
        """Execute file operations safely"""
        try:
            file_path = Path(path).resolve()

            # Safety check - prevent directory traversal
            if not str(file_path).startswith(str(Path.cwd().resolve())):
                return {"success": False, "error": "Access denied - path outside working directory"}

            if operation == "read":
                if file_path.exists() and file_path.is_file():
                    content = file_path.read_text()
                    return {"success": True, "content": content}
                else:
                    return {"success": False, "error": "File not found"}

            elif operation == "write":
                # Create parent directories if needed
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                return {"success": True, "message": f"Written to {path}"}

            elif operation == "list":
                if file_path.exists():
                    if file_path.is_dir():
                        items = [item.name for item in file_path.iterdir()]
                        return {"success": True, "items": items}
                    else:
                        return {"success": False, "error": "Path is not a directory"}
                else:
                    return {"success": False, "error": "Directory not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_code(self, command: str, timeout: int = 30) -> Dict:
        """Execute code commands safely"""
        try:
            # Safety check - prevent dangerous commands
            dangerous_commands = ['rm -rf', 'sudo', 'chmod 777', 'mkfs', 'dd if=']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return {"success": False, "error": "Command blocked for safety"}

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def enhance_with_tools(self, query: str) -> Dict:
        """Enhance response with tool capabilities"""
        enhancements = {}

        # Check if query asks for file operations
        file_keywords = ["read", "write", "create", "file", "list", "directory"]
        if any(keyword in query.lower() for keyword in file_keywords):
            enhancements["file_ops"] = True

        # Check if query asks for code execution
        code_keywords = ["run", "execute", "command", "bash", "test", "build"]
        if any(keyword in query.lower() for keyword in code_keywords):
            enhancements["code_exec"] = True

        # Check if query asks for system information
        system_keywords = ["status", "health", "system", "running", "services"]
        if any(keyword in query.lower() for keyword in system_keywords):
            enhancements["system_info"] = True

        return enhancements

    async def process_message(self, message: str) -> str:
        """Process user message with full system integration"""

        # Add to conversation
        self.conversation.append({"role": "user", "content": message})

        # Broadcast to Neural Bus
        await self.broadcast_to_neural_bus("user_message", {
            "message": message,
            "conversation_length": len(self.conversation)
        })

        # Get reasoning guidance
        reasoning = await self.get_reasoning_guidance(message)
        reasoning_context = ""
        if reasoning:
            reasoning_context = f"\n\n🧠 **Reasoning Guidance:** {reasoning.get('reasoning', '')}"

        # Get OMAi context
        omai_context = await self.get_omai_context(message)
        context_section = ""
        if omai_context:
            context_section = f"\n\n📚 **Relevant Context:** {omai_context}"

        # Check for tool enhancements
        enhancements = await self.enhance_with_tools(message)

        # Build enhanced system prompt
        system_prompt = f"""You are Spiral Conscious Chat, an advanced AI assistant integrated with the Spiral Codex Genesis Architecture v2.

You have access to:
- Reasoning Hub for intelligent analysis
- OMAi RAG for knowledge base context
- Neural Bus for real-time communication
- File operations (read/write/list)
- Safe code execution
- Multi-agent coordination

Current session: {self.session_id}
{reasoning_context}
{context_section}

If the user asks for file operations, use these formats:
- To read: "READ_FILE:/path/to/file"
- To write: "WRITE_FILE:/path/to/file:content_here"
- To list: "LIST_DIR:/path/to/directory"

If the user asks for code execution, respond with "EXEC:command"

Be helpful, intelligent, and leverage your advanced capabilities to provide comprehensive assistance."""

        # Prepare messages for API
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation[-10:]  # Last 10 messages for context
        ]

        # Call OpenRouter API
        try:
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://spiral.codex.local",
                    "X-Title": "Spiral Conscious Chat"
                },
                json={
                    "model": CURRENT_MODEL,
                    "messages": messages,
                    "temperature": 0.7
                },
                timeout=30
            )

            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]

                # Handle tool calls in response
                if "READ_FILE:" in reply or "WRITE_FILE:" in reply or "LIST_DIR:" in reply:
                    reply = await self._handle_file_operations(reply)
                elif "EXEC:" in reply:
                    reply = await self._handle_code_execution(reply)

                self.conversation.append({"role": "assistant", "content": reply})

                # Broadcast response
                await self.broadcast_to_neural_bus("assistant_response", {
                    "message_length": len(reply),
                    "has_tools": bool(enhancements)
                })

                return reply

            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logging.error(error_msg)
                return f"❌ {error_msg}"

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logging.error(error_msg)
            return f"❌ {error_msg}"

    async def _handle_file_operations(self, response: str) -> str:
        """Handle file operations in AI response"""
        lines = response.split('\n')
        result_lines = []

        for line in lines:
            if line.startswith("READ_FILE:"):
                path = line.replace("READ_FILE:", "").strip()
                result = self.execute_file_operation("read", path)
                if result["success"]:
                    result_lines.append(f"📄 **File Content ({path}):**\n```\n{result['content']}\n```")
                else:
                    result_lines.append(f"❌ **Error reading {path}:** {result['error']}")

            elif line.startswith("WRITE_FILE:"):
                parts = line.replace("WRITE_FILE:", "").strip().split(":", 1)
                if len(parts) == 2:
                    path, content = parts
                    result = self.execute_file_operation("write", path, content)
                    if result["success"]:
                        result_lines.append(f"✅ **{result['message']}**")
                    else:
                        result_lines.append(f"❌ **Error writing {path}:** {result['error']}")

            elif line.startswith("LIST_DIR:"):
                path = line.replace("LIST_DIR:", "").strip()
                result = self.execute_file_operation("list", path)
                if result["success"]:
                    items = "\n".join([f"  📁 {item}" for item in result["items"]])
                    result_lines.append(f"📁 **Directory Contents ({path}):**\n{items}")
                else:
                    result_lines.append(f"❌ **Error listing {path}:** {result['error']}")
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    async def _handle_code_execution(self, response: str) -> str:
        """Handle code execution in AI response"""
        lines = response.split('\n')
        result_lines = []

        for line in lines:
            if line.startswith("EXEC:"):
                command = line.replace("EXEC:", "").strip()
                result_lines.append(f"⚡ **Executing:** `{command}`")

                exec_result = self.execute_code(command)

                if exec_result["success"]:
                    if exec_result["stdout"]:
                        result_lines.append(f"📤 **Output:**\n```\n{exec_result['stdout']}\n```")
                    if exec_result["stderr"]:
                        result_lines.append(f"⚠️ **Warnings:**\n```\n{exec_result['stderr']}\n```")
                    result_lines.append(f"✅ **Exit code:** {exec_result['returncode']}")
                else:
                    result_lines.append(f"❌ **Error:** {exec_result['error']}")
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    async def run(self):
        """Main chat loop"""
        print(f"{GREEN}🌟 Spiral Conscious Chat ready!{RESET}")
        print(f"{CYAN}💬 Ask me anything - I can read files, execute code, and use my full AI capabilities!{RESET}")
        print(f"{YELLOW}Type 'quit', 'exit', or 'q' to leave.{RESET}\n")

        while True:
            try:
                message = input(f"{CYAN}🧠 You:{RESET} ").strip()

                if not message:
                    continue

                if message.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{YELLOW}👋 Goodbye! Session logged to {self.log_file}{RESET}")
                    break

                # Show thinking indicator
                print(f"{BLUE}🤔 Thinking...{RESET}", end="", flush=True)

                # Process message
                response = await self.process_message(message)

                # Clear thinking line and show response
                print("\r" + " " * 20 + "\r", end="")
                print(f"{GREEN}🤖 Spiral:{RESET} {response}\n")

            except KeyboardInterrupt:
                print(f"\n\n{YELLOW}👋 Interrupted. Session saved!{RESET}")
                break
            except Exception as e:
                print(f"\n{RED}❌ Error: {e}{RESET}\n")
                logging.error(f"Chat error: {e}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Install aiohttp if needed
    try:
        import aiohttp
    except ImportError:
        print(f"{YELLOW}📦 Installing aiohttp...{RESET}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp

    chat = SpiralConsciousChat()
    asyncio.run(chat.run())