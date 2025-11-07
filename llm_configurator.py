#!/usr/bin/env python3
"""
🔧 LLM CONFIGURATOR - Local Model Integration
Configure and integrate Ollama models with Spiral Codex systems
"""

import os
import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# Colors
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[34m"
BOLD = "\033[1m"
RESET = "\033[0m"

class LLMConfigurator:
    """Configure and manage local LLM models"""

    def __init__(self):
        self.ollama_base_url = "http://localhost:11434"
        self.recommended_models = [
            {"name": "qwen2.5:7b", "type": "general", "size": "7B", "description": "Strong reasoning & instructions"},
            {"name": "deepseek-coder-v2:base", "type": "coding", "size": "base", "description": "Excellent for code & complex reasoning"},
            {"name": "llama3.1:8b", "type": "general", "size": "8B", "description": "Great all-around performer"},
            {"name": "qwen2.5-coder:7b", "type": "coding", "size": "7B", "description": "Best for coding + reasoning"},
            {"name": "llama3.2:3b", "type": "lightweight", "size": "3B", "description": "Fast for simple tasks"},
            {"name": "codellama:13b", "type": "coding", "size": "13B", "description": "Complex technical tasks"},
        ]

    def check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_installed_models(self) -> List[str]:
        """Get list of installed Ollama models"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama"""
        print(f"{YELLOW}📦 Pulling {model_name}...{RESET}")

        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )

            if result.returncode == 0:
                print(f"{GREEN}✅ Successfully pulled {model_name}{RESET}")
                return True
            else:
                print(f"{RED}❌ Failed to pull {model_name}: {result.stderr}{RESET}")
                return False

        except subprocess.TimeoutExpired:
            print(f"{RED}❌ Pull timeout for {model_name}{RESET}")
            return False
        except Exception as e:
            print(f"{RED}❌ Error pulling {model_name}: {e}{RESET}")
            return False

    def test_model(self, model_name: str) -> bool:
        """Test a model with a simple query"""
        try:
            payload = {
                "model": model_name,
                "prompt": "Hello! Respond with just 'OK' to confirm you're working.",
                "stream": False
            }

            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return "ok" in result.get("response", "").lower()

        except Exception as e:
            print(f"{RED}❌ Error testing {model_name}: {e}{RESET}")

        return False

    def setup_recommended_models(self):
        """Setup the recommended models for Spiral Codex"""
        print(f"{BOLD}{CYAN}🚀 Setting up Spiral Codex Local Models{RESET}")
        print(f"{CYAN}{'='*60}{RESET}\n")

        # Check Ollama status
        if not self.check_ollama_status():
            print(f"{RED}❌ Ollama is not running!{RESET}")
            print(f"{YELLOW}Please start Ollama first: {RESET}ollama serve")
            return False

        print(f"{GREEN}✅ Ollama is running!{RESET}\n")

        # Get current models
        installed = self.get_installed_models()
        print(f"{BLUE}📋 Currently installed models:{RESET}")
        if installed:
            for model in installed:
                print(f"  • {model}")
        else:
            print("  None found")
        print()

        # Install recommended models
        print(f"{YELLOW}🎯 Installing recommended models for Spiral Codex:{RESET}\n")

        successful_installs = []

        for model_info in self.recommended_models[:4]:  # Install top 4 recommended
            model_name = model_info["name"]

            if model_name in installed:
                print(f"{GREEN}✅ {model_name} already installed{RESET}")
                successful_installs.append(model_name)
            else:
                print(f"{CYAN}📦 Installing {model_name} ({model_info['description']}){RESET}")
                if self.pull_model(model_name):
                    successful_installs.append(model_name)

                    # Test the model
                    print(f"{BLUE}🧪 Testing {model_name}...{RESET}", end="")
                    if self.test_model(model_name):
                        print(f" {GREEN}✅ Working!{RESET}")
                    else:
                        print(f" {YELLOW}⚠️  May need testing{RESET}")

            print()

        # Create configuration
        config = {
            "ollama_url": self.ollama_base_url,
            "installed_models": successful_installs,
            "recommended_models": self.recommended_models,
            "setup_complete": True,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }

        config_file = Path("llm_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"{GREEN}✅ Configuration saved to {config_file}{RESET}")
        return len(successful_installs) > 0

    def create_hybrid_chat_system(self):
        """Create a hybrid chat system that uses both local and cloud models"""

        config_content = '''#!/usr/bin/env python3
"""
🌟 SPIRAL HYBRID CHAT - Local + Cloud Models
Intelligently switches between local Ollama and cloud OpenRouter models
"""

import requests
import sys
import json
import time
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

# OpenRouter Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"

# Model Configuration
LOCAL_MODELS = [
    {"name": "qwen2.5:7b", "type": "reasoning", "strength": "complex_reasoning"},
    {"name": "deepseek-coder-v2:base", "type": "coding", "strength": "code_generation"},
    {"name": "llama3.1:8b", "type": "general", "strength": "balanced"},
]

CLOUD_MODELS = [
    {"name": "anthropic/claude-3.5-sonnet", "type": "advanced", "strength": "complex_tasks"},
    {"name": "deepseek/deepseek-chat-v3.1:free", "type": "general", "strength": "balanced"},
]

# Colors
CYAN = "\\033[36m"
GREEN = "\\033[32m"
YELLOW = "\\033[33m"
RED = "\\033[31m"
BLUE = "\\033[34m"
MAGENTA = "\\033[35m"
BOLD = "\\033[1m"
RESET = "\\033[0m"

# =============================================================================
# HYBRID CHAT SYSTEM
# =============================================================================

class HybridChatSystem:
    """Intelligently switches between local and cloud models"""

    def __init__(self):
        self.conversation = []
        self.local_available = self.check_local_models()
        self.cloud_available = True  # Assume OpenRouter works
        self.prefer_local = True  # Start with preference for local models

    def check_local_models(self) -> bool:
        """Check which local models are available"""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                available = [m for m in LOCAL_MODELS if m["name"] in model_names]
                LOCAL_MODELS.clear()
                LOCAL_MODELS.extend(available)
                return len(available) > 0
        except:
            pass
        return False

    def select_best_model(self, message: str) -> Dict:
        """Select the best model for the given message"""
        message_lower = message.lower()

        # Check for specific task types
        if any(word in message_lower for word in ["code", "program", "debug", "function"]):
            # Prefer coding models
            for model in LOCAL_MODELS:
                if model["type"] == "coding" and self.local_available and self.prefer_local:
                    return {"model": model["name"], "source": "local", "reason": "coding task"}
            for model in CLOUD_MODELS:
                if model["type"] == "advanced":
                    return {"model": model["name"], "source": "cloud", "reason": "complex coding task"}

        elif any(word in message_lower for word in ["analyze", "reason", "think", "complex"]):
            # Prefer reasoning models
            for model in LOCAL_MODELS:
                if model["type"] == "reasoning" and self.local_available and self.prefer_local:
                    return {"model": model["name"], "source": "local", "reason": "reasoning task"}
            for model in CLOUD_MODELS:
                if model["type"] == "advanced":
                    return {"model": model["name"], "source": "cloud", "reason": "complex reasoning task"}

        # Default selection
        if self.local_available and self.prefer_local:
            return {"model": LOCAL_MODELS[0]["name"], "source": "local", "reason": "default local model"}
        else:
            return {"model": CLOUD_MODELS[1]["name"], "source": "cloud", "reason": "default cloud model"}

    def query_local_model(self, model_name: str, messages: List[Dict]) -> str:
        """Query a local Ollama model"""
        try:
            # Convert OpenRouter format to Ollama format
            user_message = messages[-1]["content"] if messages else "Hello"

            payload = {
                "model": model_name,
                "prompt": user_message,
                "stream": False
            }

            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                return response.json().get("response", "Error: No response")
            else:
                raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            raise Exception(f"Local model error: {e}")

    def query_cloud_model(self, model_name: str, messages: List[Dict]) -> str:
        """Query a cloud model via OpenRouter"""
        try:
            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": 2000
            }

            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://spiral.codex.local",
                    "X-Title": "Spiral Hybrid Chat"
                },
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(f"Cloud model error: {e}")

    def get_response(self, message: str) -> str:
        """Get response using the best available model"""
        selection = self.select_best_model(message)

        print(f"{MAGENTA}🎯 Using: {selection['model']} ({selection['source']}) - {selection['reason']}{RESET}")

        try:
            if selection["source"] == "local":
                response = self.query_local_model(selection["model"], self.conversation)
            else:
                response = self.query_cloud_model(selection["model"], self.conversation)

            # Add to conversation
            self.conversation.append({"role": "user", "content": message})
            self.conversation.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            # Fallback logic
            if selection["source"] == "local":
                print(f"{YELLOW}⚠️  Local model failed, trying cloud...{RESET}")
                try:
                    fallback_model = CLOUD_MODELS[1]["name"]
                    response = self.query_cloud_model(fallback_model, self.conversation)
                    self.conversation.append({"role": "user", "content": message})
                    self.conversation.append({"role": "assistant", "content": response})
                    return response
                except:
                    pass
            elif selection["source"] == "cloud":
                print(f"{YELLOW}⚠️  Cloud model failed, trying local...{RESET}")
                try:
                    if LOCAL_MODELS:
                        response = self.query_local_model(LOCAL_MODELS[0]["name"], self.conversation)
                        self.conversation.append({"role": "user", "content": message})
                        self.conversation.append({"role": "assistant", "content": response})
                        return response
                except:
                    pass

            return f"❌ Error: All models failed - {str(e)}"

    def run(self):
        """Run the hybrid chat system"""
        print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{CYAN}║  🌟 SPIRAL HYBRID CHAT - Local + Cloud Intelligence    ║{RESET}")
        print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\\n")

        print(f"{GREEN}🤖 Local Models Available: {len(LOCAL_MODELS)}{RESET}")
        for model in LOCAL_MODELS:
            print(f"  • {model['name']} ({model['type']})")

        print(f"{GREEN}☁️  Cloud Models Available: {len(CLOUD_MODELS)}{RESET}")
        for model in CLOUD_MODELS:
            print(f"  • {model['name']} ({model['type']})")

        print(f"\\n{BLUE}💡 I'll automatically choose the best model for each task!{RESET}")
        print(f"{YELLOW}Type 'toggle' to switch preference, 'quit' to exit.{RESET}\\n")

        while True:
            try:
                message = input(f"{CYAN}🌀 You:{RESET} ").strip()

                if not message:
                    continue

                if message.lower() in ['quit', 'exit', 'q']:
                    print(f"\\n{YELLOW}👋 Goodbye!{RESET}")
                    break

                if message.lower() == 'toggle':
                    self.prefer_local = not self.prefer_local
                    preference = "local" if self.prefer_local else "cloud"
                    print(f"{GREEN}✅ Preference switched to: {preference} models{RESET}")
                    continue

                print(f"{BLUE}🤔 Thinking...{RESET}", end="", flush=True)

                start_time = time.time()
                response = self.get_response(message)
                response_time = time.time() - start_time

                print(f"\\r{' ' * 20}\\r", end="")
                print(f"{GREEN}🤖 Assistant ({response_time:.1f}s):{RESET} {response}\\n")

            except KeyboardInterrupt:
                print(f"\\n\\n{YELLOW}👋 Interrupted. Goodbye!{RESET}")
                break
            except Exception as e:
                print(f"\\n{RED}❌ Error: {e}{RESET}\\n")

if __name__ == "__main__":
    chat = HybridChatSystem()
    chat.run()
'''

        hybrid_file = Path("spiral_hybrid_chat.py")
        with open(hybrid_file, 'w') as f:
            f.write(config_content)

        print(f"{GREEN}✅ Created spiral_hybrid_chat.py - Hybrid local + cloud system!{RESET}")

    def main(self):
        """Main setup function"""
        print(f"{BOLD}{CYAN}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║       🔧 SPIRAL CODEX LLM CONFIGURATOR                  ║")
        print("║           Local Model Integration Setup                 ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(f"{RESET}")

        # Setup models
        if self.setup_recommended_models():
            print(f"\n{GREEN}🎉 Model setup successful!{RESET}")

            # Create hybrid system
            self.create_hybrid_chat_system()

            print(f"\n{BOLD}{YELLOW}🚀 Ready to use local models!{RESET}")
            print(f"{CYAN}Try these commands:{RESET}")
            print(f"  • python spiral_hybrid_chat.py    # Hybrid local + cloud")
            print(f"  • ollama list                     # See installed models")
            print(f"  • ollama run qwen2.5:7b           # Test model directly")

        else:
            print(f"\n{RED}❌ Model setup failed. Check Ollama installation.{RESET}")

if __name__ == "__main__":
    configurator = LLMConfigurator()
    configurator.main()