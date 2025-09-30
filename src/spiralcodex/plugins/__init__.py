
"""
🔌 Spiral Codex Plugin System - Extensible Agent Architecture

The mystical plugin system that allows agents to be dynamically discovered,
loaded, and managed as modular components in the recursive framework.
"""

from .plugin_core import PluginCore, PluginConfig, PluginStatus
from .plugin_manager import PluginManager, PluginInfo
from .agent_plugin import AgentPlugin, AgentPluginBase
from .plugin_registry import PluginRegistry
from .plugin_loader import PluginLoader, PluginLoadError

__all__ = [
    'PluginCore',
    'PluginConfig', 
    'PluginStatus',
    'PluginManager',
    'PluginInfo',
    'AgentPlugin',
    'AgentPluginBase',
    'PluginRegistry',
    'PluginLoader',
    'PluginLoadError'
]
