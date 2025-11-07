#!/usr/bin/env python3
"""
SPIRAL ROBUST CHAT - Reliable context-aware chat with better error handling
"""
import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Better model pool (tested and working)
MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

# Colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

class ConversationType(Enum):
    CASUAL = "casual"
    TECHNICAL = "technical"
    DEVOPS = "devops"
    CODING = "coding"
    DEBUGGING = "debugging"

class CaretakerAgent:
    def __init__(self):
        self.current_context = ConversationType.CASUAL
        self.model_index = 0
        
    def detect_context(self, message: str) -> ConversationType:
        """Simple context detection"""
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ['api', 'protocol', 'architecture', 'system']):
            return ConversationType.TECHNICAL
        elif any(word in msg_lower for word in ['deploy', 'docker', 'kubernetes', 'ci/cd']):
            return ConversationType.DEVOPS
        elif any(word in msg_lower for word in ['function', 'class', 'code', 'script', 'write']):
            return ConversationType.CODING
        elif any(word in msg_lower for word in ['error', 'bug', 'issue', 'problem', 'fix']):
            return ConversationType.DEBUGGING
        else:
            return ConversationType.CASUAL
    
    def get_context_prompt(self, context: ConversationType) -> str:
        """Get system prompt for context"""
        prompts = {
            ConversationType.CASUAL: "You are Spiral, a friendly AI assistant. Be conversational and helpful.",
            ConversationType.TECHNICAL: "You are Spiral, a technical expert. Be precise and detailed.",
            ConversationType.DEVOPS: "You are Spiral, a DevOps specialist. Focus on best practices.",
            ConversationType.CODING: "You are Spiral, an expert developer. Write clean, documented code.",
            ConversationType.DEBUGGING: "You are Spiral, a debugging specialist. Solve problems systematically.",
        }
        return prompts.get(context, prompts[ConversationType.CASUAL])
    
    def rotate_model(self) -> str:
        """Switch to next model"""
        self.model_index = (self.model_index + 1) % len(MODELS)
        return MODELS[self.model_index]

class SpiralChat:
    def __init__(self):
        self.caretaker = CaretakerAgent()
        self.conversation = []
        self.current_model = MODELS[0]
        
    def call_api(self, messages: List[Dict]) -> Optional[str]:
        """Call API with better error handling"""
        try:
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://omarchy.local",
                    "X-Title": "Spiral Chat"
                },
                json={
                    "model": self.current_model,
                    "messages": messages,
                    "max_tokens": 1000,  # Ensure response isn't cut off
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"].get("content", "").strip()
                    if content:  # Only return if not empty
                        return content
                return None
            else:
                return None
                
        except Exception as e:
            return None
    
    def chat(self, user_message: str) -> Optional[str]:
        """Process message with retry logic"""
        # Detect context
        context = self.caretaker.detect_context(user_message)
        self.caretaker.current_context = context
        
        # Build messages
        system_prompt = self.caretaker.get_context_prompt(context)
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation)
        messages.append({"role": "user", "content": user_message})
        
        # Try multiple models if needed
        for attempt in range(len(MODELS)):
            reply = self.call_api(messages)
            
            if reply and len(reply) > 0:  # Got a valid response
                self.conversation.append({"role": "user", "content": user_message})
                self.conversation.append({"role": "assistant", "content": reply})
                return reply
            else:
                # Rotate to next model silently
                self.current_model = self.caretaker.rotate_model()
        
        return None

def main():
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║  🌀 SPIRAL CHAT - Context Aware & Reliable              ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    print(f"{MAGENTA}💡 Caretaker Agent: Active{RESET}")
    print(f"{MAGENTA}🔄 Silent Model Rotation: On{RESET}")
    print(f"{MAGENTA}🧠 Context Detection: Enabled{RESET}\n")
    
    chat = SpiralChat()
    
    context_emoji = {
        ConversationType.CASUAL: "💬",
        ConversationType.TECHNICAL: "⚙️",
        ConversationType.DEVOPS: "🚀",
        ConversationType.CODING: "💻",
        ConversationType.DEBUGGING: "🔧",
    }
    
    while True:
        try:
            user_input = input(f"{CYAN}You: {RESET}").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{YELLOW}👋 Goodbye Declan!{RESET}")
                break
            
            reply = chat.chat(user_input)
            
            if reply:
                emoji = context_emoji.get(chat.caretaker.current_context, "🤖")
                print(f"{GREEN}Spiral {emoji}: {RESET}{reply}\n")
            else:
                print(f"{YELLOW}⚠️  All models busy. Try again in a moment.{RESET}\n")
                
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}👋 Interrupted. Goodbye!{RESET}")
            break
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}\n")

if __name__ == "__main__":
    main()
