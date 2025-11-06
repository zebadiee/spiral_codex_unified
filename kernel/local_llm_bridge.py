# kernel/local_llm_bridge.py
"""
LocalLLMBridge - Connects Spiral Codex to local LLM services
Supports Ollama and Jetson for local AI inference
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from pathlib import Path
import subprocess
import platform
from pydantic import BaseModel

class LLMConfig(BaseModel):
    """Configuration for LLM bridge"""
    provider: str = "ollama"  # ollama, jetson
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    timeout: int = 30
    max_tokens: int = 4096
    temperature: float = 0.7

class LocalLLMBridge:
    """Bridge to local LLM services (Ollama/Jetson)"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = None
        self.status = "initialized"
        self.last_check = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        await self._check_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _check_connection(self) -> bool:
        """Check if LLM service is available"""
        try:
            if self.config.provider == "ollama":
                # Check Ollama health
                async with self.session.get(f"{self.config.base_url}/api/tags") as response:
                    if response.status == 200:
                        self.status = "connected"
                        self.last_check = datetime.utcnow().isoformat()
                        return True
            elif self.config.provider == "jetson":
                # Check Jetson service (placeholder)
                self.status = "connected"
                self.last_check = datetime.utcnow().isoformat()
                return True

        except Exception as e:
            self.status = f"error: {str(e)}"
            return False

        self.status = "disconnected"
        return False

    async def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.session:
            raise RuntimeError("Bridge not initialized")

        try:
            if self.config.provider == "ollama":
                async with self.session.get(f"{self.config.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
            elif self.config.provider == "jetson":
                # Placeholder for Jetson models
                return ["jetson-model-1", "jetson-model-2"]

        except Exception as e:
            raise RuntimeError(f"Failed to get models: {str(e)}")

        return []

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Generate text from LLM"""
        if not self.session:
            raise RuntimeError("Bridge not initialized")

        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            if self.config.provider == "ollama":
                if stream:
                    return await self._stream_ollama(payload)
                else:
                    async with self.session.post(
                        f"{self.config.base_url}/api/generate",
                        json=payload
                    ) as response:
                        if response.status == 200:
                            # Handle ndjson response
                            content = await response.text()
                            result = {}
                            for line in content.strip().split('\n'):
                                if line:
                                    chunk = json.loads(line)
                                    result = chunk
                            return result.get("response", "")
                        else:
                            raise RuntimeError(f"LLM API error: {response.status}")

            elif self.config.provider == "jetson":
                # Placeholder for Jetson generation
                return f"[Jetson response to: {prompt[:50]}...]"

        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")

        return ""

    async def _stream_ollama(self, payload: Dict[str, Any]) -> str:
        """Stream generation from Ollama"""
        full_response = ""

        async with self.session.post(
            f"{self.config.base_url}/api/generate",
            json=payload
        ) as response:
            if response.status == 200:
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if "response" in chunk:
                                full_response += chunk["response"]
                        except json.JSONDecodeError:
                            continue
            else:
                raise RuntimeError(f"Stream error: {response.status}")

        return full_response

    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """Chat with LLM using message format"""
        if not self.session:
            raise RuntimeError("Bridge not initialized")

        payload = {
            "model": self.config.model,
            "messages": messages,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }

        try:
            if self.config.provider == "ollama":
                async with self.session.post(
                    f"{self.config.base_url}/api/chat",
                    json=payload
                ) as response:
                    if response.status == 200:
                        # Handle ndjson response
                        content = await response.text()
                        result = {}
                        for line in content.strip().split('\n'):
                            if line:
                                chunk = json.loads(line)
                                result = chunk
                        return result.get("message", {}).get("content", "")
                    else:
                        raise RuntimeError(f"Chat API error: {response.status}")

            elif self.config.provider == "jetson":
                # Placeholder for Jetson chat
                return f"[Jetson chat response to {len(messages)} messages]"

        except Exception as e:
            raise RuntimeError(f"Chat failed: {str(e)}")

        return ""

    def get_status(self) -> Dict[str, Any]:
        """Get bridge status"""
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "base_url": self.config.base_url,
            "status": self.status,
            "last_check": self.last_check,
            "config": self.config.dict()
        }

class OllamaManager:
    """Manages Ollama installation and models"""

    def __init__(self):
        self.platform = platform.system().lower()

    async def check_ollama_installation(self) -> bool:
        """Check if Ollama is installed"""
        try:
            # Check if ollama command exists
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    async def install_ollama(self) -> bool:
        """Install Ollama (Linux/macOS)"""
        if self.platform == "linux" or self.platform == "darwin":
            try:
                # Download and install Ollama
                install_script = "curl -fsSL https://ollama.com/install.sh | sh"
                result = subprocess.run(
                    install_script,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                return result.returncode == 0
            except subprocess.TimeoutExpired:
                return False
        return False

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama"""
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout for large models
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    async def start_ollama_service(self) -> bool:
        """Start Ollama service"""
        try:
            # Start ollama serve in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Give it a moment to start
            await asyncio.sleep(3)
            return True
        except Exception:
            return False

# Agent-specific LLM wrappers
class AgentLLMWrapper:
    """Wraps LLM bridge for specific agent use cases"""

    def __init__(self, bridge: LocalLLMBridge, agent_type: str):
        self.bridge = bridge
        self.agent_type = agent_type
        self.system_prompts = {
            "ƒCODEX": "You are ƒCODEX, a code generation and debugging expert. Focus on clean, efficient code implementation.",
            "ƒCLAUDE": "You are ƒCLAUDE, an analysis and planning expert. Provide thoughtful, comprehensive analysis.",
            "ƒCOPILOT": "You are ƒCOPILOT, a code completion and pattern matching expert.",
            "ƒGEMMA": "You are ƒGEMMA, a research and data analysis expert.",
            "ƒDEEPSEEK": "You are ƒDEEPSEEK, a deep reasoning and problem solving expert.",
            "ƒGEMINI": "You are ƒGEMINI, a multimodal synthesis and creative problem solving expert."
        }

    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate agent-specific response"""
        system_prompt = self.system_prompts.get(self.agent_type, "You are a helpful AI assistant.")

        # Add context to prompt if provided
        if context:
            context_str = json.dumps(context, indent=2)
            prompt = f"Context:\n{context_str}\n\nTask:\n{prompt}"

        return await self.bridge.generate(prompt, system_prompt)

    async def chat_with_history(self, messages: List[Dict[str, str]]) -> str:
        """Chat with conversation history"""
        # Add system message for agent type
        system_prompt = self.system_prompts.get(self.agent_type, "You are a helpful AI assistant.")

        full_messages = [{"role": "system", "content": system_prompt}] + messages

        return await self.bridge.chat(full_messages)

# Factory function
async def create_llm_bridge(provider: str = "ollama", model: str = "llama3.2") -> LocalLLMBridge:
    """Create and initialize LLM bridge"""
    config = LLMConfig(provider=provider, model=model)
    bridge = LocalLLMBridge(config)

    # Ensure service is available
    if provider == "ollama":
        manager = OllamaManager()
        if not await manager.check_ollama_installation():
            raise RuntimeError("Ollama not installed. Please install Ollama first.")

        if not await manager.start_ollama_service():
            raise RuntimeError("Failed to start Ollama service.")

    return bridge