#!/usr/bin/env python3
"""
🌀 SPIRAL ENHANCED CHAT - Advanced Token-Aware Chat Interface
Integrates with AI Token Manager for intelligent API rotation, timeout handling, and fallback mechanisms
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add AI token manager to path
sys.path.append(str(Path(__file__).parents[1] / "ai-token-manager" / "tokens"))

try:
    from enhanced_api_client import get_enhanced_client
    AI_TOKEN_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI Token Manager not available: {e}")
    AI_TOKEN_MANAGER_AVAILABLE = False

import requests

# ANSI colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RED = "\033[31m"
RESET = "\033[0m"

def print_header():
    print(f"{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║           🌀 SPIRAL ENHANCED CHAT (Token-Aware) 🌀                ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
    print()

    if AI_TOKEN_MANAGER_AVAILABLE:
        print(f"{GREEN}✨ Enhanced Features:{RESET}")
        print("  • AI Token Manager integration for intelligent API rotation")
        print("  • Automatic timeout handling with exponential backoff")
        print("  • Circuit breaker pattern for failed providers")
        print("  • Hybrid local LLM fallback when external APIs fail")
        print("  • Request queuing for automatic retry when services recover")
        print("  • Conservative timeouts: 5s health checks, 15s API calls")
    else:
        print(f"{YELLOW}⚠️  AI Token Manager unavailable - using basic OpenRouter rotation{RESET}")

    print()
    print(f"{GREEN}Commands:{RESET} 'quit' to exit, 'clear' to reset, 'status' for system info, 'health' for provider health")
    print()

class SpiralEnhancedChat:
    def __init__(self):
        self.conversation = []
        self.session_id = f"spiral_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize enhanced API client if available
        if AI_TOKEN_MANAGER_AVAILABLE:
            self.api_client = get_enhanced_client()
            print(f"{GREEN}✅ Enhanced API client initialized{RESET}")
        else:
            self.api_client = None
            self._init_basic_openrouter()

        print_header()

    def _init_basic_openrouter(self):
        """Initialize basic OpenRouter configuration as fallback"""
        # Load from environment (same as original spiral_chat.py)
        self.OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")
        self.OR_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
        self.OR_REFERER = "https://omarchy.local"
        self.OR_TITLE = "Omarchy Wagon Wheels - Enhanced"

        # Model rotation from environment
        self.MODELS = [
            os.getenv("OR_MODEL_1", "z-ai/glm-4.5-air:free"),
            os.getenv("OR_MODEL_2", "deepseek/deepseek-chat-v3.1:free"),
            os.getenv("OR_MODEL_3", "minimax/minimax-m2:free"),
            os.getenv("OR_MODEL_4", "nvidia/nemotron-nano-9b-v2:free"),
            os.getenv("OR_MODEL_5", "qwen/qwen3-coder:free")
        ]

        # Start with preferred model from environment or default
        current_index = int(os.getenv("OR_CURRENT_MODEL_INDEX", "1"))
        self.current_model_index = current_index % len(self.MODELS)
        self.OR_MODEL = self.MODELS[self.current_model_index]

    def send_message_enhanced(self, message):
        """Send message using enhanced API client with intelligent fallback"""
        if not self.api_client:
            return self.send_message_basic(message)

        try:
            # Prepare messages for API
            messages = self.conversation + [{"role": "user", "content": message}]

            # Use enhanced client
            result = self.api_client.chat_completion(
                messages=messages,
                model=None,  # Let client choose best model
                preferred_provider="openrouter"  # Prefer OpenRouter but allow fallback
            )

            if result.get("success"):
                response = result["response"]
                provider = result.get("provider", "unknown")
                model = result.get("model", "unknown")
                fallback = result.get("fallback", False)

                # Update conversation
                self.conversation.append({"role": "user", "content": message})
                self.conversation.append({"role": "assistant", "content": response})

                # Format response
                if fallback:
                    print(f"{GREEN}🤖 Spiral ({provider}-fallback):{RESET} {response}\n")
                else:
                    print(f"{GREEN}🤖 Spiral ({provider} via {model}):{RESET} {response}\n")

                return response
            else:
                # Enhanced client failed
                error = result.get("error", "Unknown error")
                error_type = result.get("error_type", "unknown")
                queued = result.get("queued", False)

                if queued:
                    print(f"{YELLOW}⏳ All providers busy - request queued for retry{RESET}")
                    print(f"{YELLOW}💡 Try again in a moment or use 'status' to see system health{RESET}\n")
                else:
                    print(f"{RED}❌ Enhanced API failed ({error_type}): {error}{RESET}")
                    print(f"{YELLOW}💡 Falling back to basic OpenRouter...{RESET}")
                    return self.send_message_basic(message)

                return None

        except Exception as e:
            print(f"{RED}❌ Enhanced client error: {e}{RESET}")
            print(f"{YELLOW}💡 Falling back to basic OpenRouter...{RESET}")
            return self.send_message_basic(message)

    def send_message_basic(self, message):
        """Fallback to basic OpenRouter implementation (same as original spiral_chat.py)"""
        if not hasattr(self, 'OPENROUTER_KEY') or not self.OPENROUTER_KEY:
            print(f"{RED}❌ No OpenRouter API key configured{RESET}")
            return None

        try:
            self.conversation.append({"role": "user", "content": message})

            # Make request to OpenRouter
            response = requests.post(
                self.OR_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {self.OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.OR_REFERER,
                    "X-Title": self.OR_TITLE
                },
                json={"model": self.OR_MODEL, "messages": self.conversation},
                timeout=15  # Conservative timeout
            )

            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                self.conversation.append({"role": "assistant", "content": reply})
                print(f"\n{GREEN}🤖 Spiral ({self.OR_MODEL}):{RESET} {reply}\n")
                return reply

            elif response.status_code == 429:
                # Rate limited - try next model
                self.conversation.pop()  # Remove user message to retry
                self.current_model_index = (self.current_model_index + 1) % len(self.MODELS)
                self.OR_MODEL = self.MODELS[self.current_model_index]
                print(f"{YELLOW}⚠️  Rate limited. Switching to: {self.OR_MODEL}{RESET}")
                print(f"{CYAN}🔄 Retrying...{RESET}\n")

                # Retry with new model
                return self.send_message_basic(message)

            else:
                print(f"{RED}Error {response.status_code}: {response.text}{RESET}\n")
                self.conversation.pop()  # Remove failed user message
                return None

        except requests.exceptions.Timeout:
            print(f"{YELLOW}⏱️ Request timeout - try again{RESET}\n")
            self.conversation.pop()
            return None
        except Exception as e:
            print(f"{RED}❌ Error: {str(e)[:50]}...{RESET}\n")
            self.conversation.pop()
            return None

    def show_status(self):
        """Show system status and health"""
        print(f"{BLUE}📊 System Status{RESET}")
        print("=" * 50)

        if self.api_client:
            # Show enhanced client status
            health = self.api_client.health_check()

            print(f"Overall Status: {GREEN}{health['overall_status'].upper()}{RESET}")
            print(f"Request Queue: {health['queue_size']} items")
            print()

            print("Provider Health:")
            for provider, status in health['providers'].items():
                if status['status'] == 'healthy':
                    status_color = GREEN
                    status_icon = "✅"
                else:
                    status_color = RED
                    status_icon = "❌"

                print(f"  {status_icon} {provider.title()}: {status_color}{status['status']}{RESET}")
                if 'reason' in status:
                    print(f"    Reason: {status['reason']}")
                if 'response_time_ms' in status:
                    print(f"    Response Time: {status['response_time_ms']:.0f}ms")
            print()
        else:
            print(f"{RED}❌ Enhanced API client not available{RESET}")
            print(f"Using basic OpenRouter with model: {self.OR_MODEL}")
            print()

        print(f"Session ID: {self.session_id}")
        print(f"Conversation Length: {len(self.conversation)} messages")
        print()

    def process_queued_requests(self):
        """Process any queued requests"""
        if self.api_client:
            processed = self.api_client.process_queued_requests()
            if processed > 0:
                print(f"{GREEN}✅ Processed {processed} queued requests{RESET}")
            elif processed == 0:
                print(f"{BLUE}ℹ️  No queued requests to process{RESET}")

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation = []
        print(f"{BLUE}🧹 Conversation cleared{RESET}\n")

    def run(self):
        """Main chat loop"""
        print(f"{CYAN}Ready to chat! Type your message and press Enter.{RESET}\n")

        while True:
            try:
                msg = input(f"{MAGENTA}You:{RESET} ").strip()

                if msg.lower() == 'quit':
                    print(f"{CYAN}👋 Goodbye!{RESET}")
                    break
                elif msg.lower() == 'clear':
                    self.clear_conversation()
                    continue
                elif msg.lower() == 'status':
                    self.show_status()
                    continue
                elif msg.lower() == 'health':
                    self.show_status()
                    continue
                elif msg.lower() == 'process-queue':
                    self.process_queued_requests()
                    continue
                elif not msg:
                    print(f"{YELLOW}💡 Please enter a message or command{RESET}")
                    continue

                # Send message
                self.send_message_enhanced(msg)

            except KeyboardInterrupt:
                print(f"\n{CYAN}👋 Goodbye!{RESET}")
                break
            except EOFError:
                print(f"\n{CYAN}👋 Goodbye!{RESET}")
                break
            except Exception as e:
                print(f"{RED}❌ Unexpected error: {e}{RESET}")

if __name__ == "__main__":
    chat = SpiralEnhancedChat()
    chat.run()