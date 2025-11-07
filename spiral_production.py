#!/usr/bin/env python3
"""
SPIRAL PRODUCTION - The Final Form
Online-first hybrid with Obsidian logging, DevOps caretaker, hallucination tracking
"""
import requests
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import os

# Configuration
OPENROUTER_KEY = "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"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_ENDPOINT = "http://localhost:11434"
OMAI_ENDPOINT = "http://localhost:7016"

# Obsidian Integration
OBSIDIAN_VAULT = Path.home() / "Documents/Obsidian"
OBSIDIAN_SPIRAL = OBSIDIAN_VAULT / "OMAi" / "Spiral-Sessions"
OBSIDIAN_LEARNING = OBSIDIAN_VAULT / "Agent-Training"
OBSIDIAN_BUILD_LOGS = OBSIDIAN_VAULT / "Build-Logs"

# Online models (PRIORITY)
ONLINE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]

# Local models (FALLBACK)
LOCAL_MODELS = {"smart": "llama3.1:8b", "fast": "mistral:latest"}

# Colors
C, G, Y, R, B, M, BOLD, RESET = "\033[36m", "\033[32m", "\033[33m", "\033[31m", "\033[34m", "\033[35m", "\033[1m", "\033[0m"

# =============================================================================
# OBSIDIAN LOGGER - Seamless Knowledge Capture
# =============================================================================

class ObsidianLogger:
    """Logs everything to Obsidian for learning and hallucination tracking"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = OBSIDIAN_SPIRAL / f"Session-{self.session_id}.md"
        self.hallucination_log = OBSIDIAN_LEARNING / "Hallucination-Tracking.md"
        self.devops_log = OBSIDIAN_BUILD_LOGS / f"DevOps-{datetime.now().strftime('%Y-%m-%d')}.md"
        
        # Ensure directories exist
        for path in [OBSIDIAN_SPIRAL, OBSIDIAN_LEARNING, OBSIDIAN_BUILD_LOGS]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize session
        self._init_session()
    
    def _init_session(self):
        """Initialize session log"""
        header = f"""# Spiral Session - {self.session_id}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Type: Production Chat with Hybrid Routing

## Configuration
- Online Models: {len(ONLINE_MODELS)} (priority)
- Local Models: Ollama (fallback)
- DevOps Caretaker: Active
- Hallucination Tracking: Enabled

## Conversation

"""
        self.session_file.write_text(header)
    
    def log_interaction(self, user_msg: str, ai_response: str, agent_type: str, source: str, context: List[str] = None):
        """Log a complete interaction"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = f"""### {timestamp} - {agent_type} Agent (via {source})

**User:** {user_msg}

"""
        if context:
            entry += f"**Context Retrieved:**\n"
            for ctx in context:
                entry += f"- {ctx}\n"
            entry += "\n"
        
        entry += f"**Spiral:** {ai_response}\n\n"
        entry += "---\n\n"
        
        # Append to session
        with open(self.session_file, "a") as f:
            f.write(entry)
    
    def log_file_operation(self, operation: str, filename: str, success: bool, details: str = ""):
        """Log file operations for DevOps tracking"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        entry = f"""### {timestamp} - {operation}
File: `{filename}`
Status: {"✅ Success" if success else "❌ Failed"}
{f"Details: {details}" if details else ""}

"""
        # Append to DevOps log
        with open(self.devops_log, "a") as f:
            if not self.devops_log.exists() or self.devops_log.stat().st_size == 0:
                f.write(f"# DevOps Log - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(entry)
    
    def track_hallucination(self, user_msg: str, response: str, issue: str):
        """Track potential hallucinations for training"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"""## {timestamp}
**User Query:** {user_msg}
**Response:** {response[:200]}...
**Issue:** {issue}
**Session:** [[Session-{self.session_id}]]

---

"""
        with open(self.hallucination_log, "a") as f:
            if not self.hallucination_log.exists():
                f.write("# Hallucination Tracking\n\nTracking incorrect/hallucinated responses for model improvement.\n\n")
            f.write(entry)
    
    def log_session_summary(self, stats: Dict):
        """Log session summary at end"""
        summary = f"""\n## Session Summary

**Statistics:**
- Total interactions: {stats.get('total', 0)}
- Online requests: {stats.get('online', 0)}
- Local fallbacks: {stats.get('local', 0)}
- File operations: {stats.get('files', 0)}
- Hallucinations tracked: {stats.get('hallucinations', 0)}

**Agent Usage:**
"""
        for agent, count in stats.get('agents', {}).items():
            summary += f"- {agent}: {count}\n"
        
        with open(self.session_file, "a") as f:
            f.write(summary)

# =============================================================================
# ... (rest of the code continues with HybridRouter, Agents, Tools, etc.)
# =============================================================================
