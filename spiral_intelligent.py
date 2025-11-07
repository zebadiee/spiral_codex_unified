#!/usr/bin/env python3
"""
SPIRAL INTELLIGENT CHAT - Context-Aware with Caretaker Agent
Silently handles model rotation, monitors conversation context, 
and adapts behavior based on conversation type.
"""
import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Model pool
MODELS = [
    "google/gemini-flash-1.5",
    "meta-llama/llama-3.2-3b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
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
# CARETAKER AGENT - Context Awareness System
# =============================================================================

class ConversationType(Enum):
    """Types of conversations the caretaker can detect"""
    CASUAL = "casual"              # General chat
    TECHNICAL = "technical"        # Technical discussion
    DEVOPS = "devops"             # DevOps/infrastructure
    CODING = "coding"             # Code development
    DEBUGGING = "debugging"        # Problem solving
    CREATIVE = "creative"          # Creative writing/ideas
    ANALYSIS = "analysis"          # Data/system analysis

@dataclass
class ContextSignals:
    """Signals that indicate conversation context"""
    keywords: List[str]
    patterns: List[str]
    indicators: List[str]

# Context detection patterns
CONTEXT_PATTERNS = {
    ConversationType.TECHNICAL: ContextSignals(
        keywords=["api", "protocol", "architecture", "system", "implementation", "algorithm"],
        patterns=[r"\b(REST|HTTP|TCP|UDP|API)\b", r"\b(database|server|client)\b"],
        indicators=["how does", "explain the", "what is the difference"]
    ),
    ConversationType.DEVOPS: ContextSignals(
        keywords=["deploy", "docker", "kubernetes", "pipeline", "ci/cd", "infrastructure"],
        patterns=[r"\b(deploy|build|release)\b", r"\b(container|orchestration)\b"],
        indicators=["how to deploy", "setup", "configure"]
    ),
    ConversationType.CODING: ContextSignals(
        keywords=["function", "class", "variable", "method", "code", "script", "program"],
        patterns=[r"def\s+\w+", r"class\s+\w+", r"import\s+\w+", r"\{.*\}"],
        indicators=["write a", "create a", "build a", "code for"]
    ),
    ConversationType.DEBUGGING: ContextSignals(
        keywords=["error", "bug", "issue", "problem", "fix", "broken", "not working"],
        patterns=[r"error:.*", r"exception.*", r"failed.*"],
        indicators=["why is", "what's wrong", "how to fix"]
    ),
    ConversationType.CREATIVE: ContextSignals(
        keywords=["story", "idea", "creative", "imagine", "write", "design"],
        patterns=[r"once upon", r"imagine if", r"what if"],
        indicators=["write me", "create a story", "design a"]
    ),
}

class CaretakerAgent:
    """
    The Caretaker Agent monitors conversations and:
    - Detects context shifts (casual → technical → devops)
    - Silently manages model rotation on failures
    - Adjusts system prompts based on conversation type
    - Logs important transitions for learning
    """
    
    def __init__(self):
        self.current_context = ConversationType.CASUAL
        self.context_history = []
        self.model_index = 0
        self.model_performance = {model: {"success": 0, "fail": 0} for model in MODELS}
        
    def detect_context(self, message: str) -> ConversationType:
        """Analyze message and detect conversation context"""
        message_lower = message.lower()
        
        # Score each context type
        scores = {context: 0 for context in ConversationType}
        
        for context_type, signals in CONTEXT_PATTERNS.items():
            # Check keywords
            for keyword in signals.keywords:
                if keyword in message_lower:
                    scores[context_type] += 2
            
            # Check patterns
            for pattern in signals.patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    scores[context_type] += 3
            
            # Check indicators
            for indicator in signals.indicators:
                if indicator in message_lower:
                    scores[context_type] += 2
        
        # Get highest scoring context
        best_context = max(scores.items(), key=lambda x: x[1])
        
        # If score is too low, keep current context
        if best_context[1] < 2:
            return self.current_context
        
        return best_context[0]
    
    def get_context_prompt(self, context: ConversationType) -> str:
        """Get specialized system prompt based on context"""
        prompts = {
            ConversationType.CASUAL: "You are Spiral, a friendly AI assistant. Be conversational and helpful.",
            
            ConversationType.TECHNICAL: """You are Spiral, a technical AI assistant with deep expertise. 
Be precise, use technical terminology appropriately, and provide detailed explanations.""",
            
            ConversationType.DEVOPS: """You are Spiral, a DevOps and infrastructure specialist.
Focus on best practices, automation, security, and scalability. Provide practical commands and configurations.""",
            
            ConversationType.CODING: """You are Spiral, an expert software developer.
Write clean, documented code. Explain your approach and suggest improvements.""",
            
            ConversationType.DEBUGGING: """You are Spiral, a debugging specialist.
Analyze problems systematically, identify root causes, and provide clear solutions.""",
            
            ConversationType.CREATIVE: """You are Spiral, a creative AI collaborator.
Think imaginatively, explore possibilities, and help bring ideas to life.""",
            
            ConversationType.ANALYSIS: """You are Spiral, an analytical expert.
Break down complex information, identify patterns, and provide insights.""",
        }
        
        return prompts.get(context, prompts[ConversationType.CASUAL])
    
    def rotate_model_silent(self) -> str:
        """Silently switch to next best model"""
        # Find model with best success rate
        available_models = sorted(
            self.model_performance.items(),
            key=lambda x: x[1]["success"] / (x[1]["success"] + x[1]["fail"] + 1),
            reverse=True
        )
        
        # Try next model
        self.model_index = (self.model_index + 1) % len(MODELS)
        return MODELS[self.model_index]
    
    def record_model_performance(self, model: str, success: bool):
        """Track model performance for intelligent selection"""
        if success:
            self.model_performance[model]["success"] += 1
        else:
            self.model_performance[model]["fail"] += 1
    
    def check_context_shift(self, new_context: ConversationType) -> bool:
        """Detect if conversation context has shifted"""
        if new_context != self.current_context:
            self.context_history.append({
                "from": self.current_context.value,
                "to": new_context.value,
                "timestamp": datetime.now().isoformat()
            })
            self.current_context = new_context
            return True
        return False

# =============================================================================
# MAIN CHAT SYSTEM
# =============================================================================

class SpiralIntelligentChat:
    """Main chat system with integrated caretaker"""
    
    def __init__(self):
        self.caretaker = CaretakerAgent()
        self.conversation = []
        self.current_model = MODELS[0]
        
    def call_api(self, messages: List[Dict], model: str) -> requests.Response:
        """Call OpenRouter API"""
        return requests.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://omarchy.local",
                "X-Title": "Spiral Intelligent Chat"
            },
            json={"model": model, "messages": messages},
            timeout=30
        )
    
    def chat(self, user_message: str) -> Optional[str]:
        """Process user message with context awareness"""
        
        # Detect conversation context
        detected_context = self.caretaker.detect_context(user_message)
        context_shifted = self.caretaker.check_context_shift(detected_context)
        
        # Build messages with context-aware system prompt
        system_prompt = self.caretaker.get_context_prompt(detected_context)
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation)
        messages.append({"role": "user", "content": user_message})
        
        # Try with retry logic (silent model rotation)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.call_api(messages, self.current_model)
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data["choices"][0]["message"]["content"]
                    
                    # Update conversation
                    self.conversation.append({"role": "user", "content": user_message})
                    self.conversation.append({"role": "assistant", "content": reply})
                    
                    # Record success
                    self.caretaker.record_model_performance(self.current_model, True)
                    
                    return reply
                    
                elif response.status_code == 429:
                    # Silently rotate model
                    self.caretaker.record_model_performance(self.current_model, False)
                    self.current_model = self.caretaker.rotate_model_silent()
                    continue
                    
                else:
                    self.caretaker.record_model_performance(self.current_model, False)
                    if attempt < max_retries - 1:
                        self.current_model = self.caretaker.rotate_model_silent()
                    continue
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self.current_model = self.caretaker.rotate_model_silent()
                continue
        
        return None

# =============================================================================
# MAIN INTERFACE
# =============================================================================

def main():
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║  🌀 SPIRAL INTELLIGENT CHAT - Context Aware              ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    print(f"{MAGENTA}💡 Caretaker Agent: Active{RESET}")
    print(f"{MAGENTA}🧠 Context Detection: Enabled{RESET}")
    print(f"{MAGENTA}🔄 Silent Model Rotation: On{RESET}\n")
    
    chat = SpiralIntelligentChat()
    
    while True:
        try:
            user_input = input(f"{CYAN}You: {RESET}").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{YELLOW}👋 Goodbye Declan!{RESET}")
                break
            
            # Get context indicator (subtle)
            context = chat.caretaker.current_context
            context_emoji = {
                ConversationType.CASUAL: "💬",
                ConversationType.TECHNICAL: "⚙️",
                ConversationType.DEVOPS: "🚀",
                ConversationType.CODING: "💻",
                ConversationType.DEBUGGING: "🔧",
                ConversationType.CREATIVE: "🎨",
                ConversationType.ANALYSIS: "📊",
            }
            
            reply = chat.chat(user_input)
            
            if reply:
                print(f"{GREEN}Spiral {context_emoji.get(context, '🤖')}: {RESET}{reply}\n")
            else:
                print(f"{RED}❌ Unable to get response. Try again.{RESET}\n")
                
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}👋 Interrupted. Goodbye!{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}❌ Error: {e}{RESET}\n")

if __name__ == "__main__":
    main()
