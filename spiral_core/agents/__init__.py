"""
🧠 Spiral Codex Agents Package
==============================

The agent system - where organic intelligence patterns manifest:
- Echo Agent: The foundational consciousness
- Future agents: Expanding spiral of capabilities
- Organic error handling and healing patterns
- Statistics tracking and learning

Each agent embodies the spiral philosophy:
- Input transformation through organic patterns
- Healing-first error handling
- Structured responses with metadata
- Continuous learning and adaptation
"""

from .echo_agent import echo_agent, EchoAgent, EchoInput, EchoResponse, EchoType

__all__ = [
    "echo_agent",
    "EchoAgent", 
    "EchoInput",
    "EchoResponse",
    "EchoType",
]

# Agent registry for dynamic discovery
AVAILABLE_AGENTS = {
    "echo": echo_agent,
}

def get_agent(name: str):
    """
    Retrieve an agent by name with organic fallback.
    
    Args:
        name: Agent identifier
        
    Returns:
        Agent instance or None if not found
    """
    return AVAILABLE_AGENTS.get(name.lower())

def list_agents() -> list:
    """List all available agents."""
    return list(AVAILABLE_AGENTS.keys())
