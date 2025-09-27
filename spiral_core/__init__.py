"""
🌀 Spiral Codex Organic OS - Core Package
=========================================

The central package containing all core functionality:
- Agent system with organic patterns
- Configuration management
- API endpoints and routing
- Healing-first error handling

Version: 1.0.0
"""

__version__ = "1.0.0"
__title__ = "Spiral Codex Organic OS"
__description__ = "The Organic Operating System for Conscious AI Agents"
__author__ = "Spiral Codex Development Team"

# Import core components for easy access
from .config import settings
from .agents.echo_agent import echo_agent, EchoInput, EchoResponse, EchoType

__all__ = [
    "settings",
    "echo_agent", 
    "EchoInput",
    "EchoResponse", 
    "EchoType",
    "__version__",
    "__title__",
    "__description__",
]
