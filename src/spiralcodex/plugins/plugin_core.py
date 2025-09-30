
"""
🔌 Plugin Core - The Heart of Extensibility

Central orchestrator for the plugin system, managing the lifecycle
of agent plugins and their mystical capabilities.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class PluginStatus(Enum):
    """Status states for plugins"""
    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class PluginConfig:
    """Configuration for the plugin system"""
    plugins_directory: str = "agents"
    auto_discover: bool = True
    auto_load: bool = True
    auto_activate: bool = False
    config_file: str = "plugin_config.json"
    disabled_plugins: List[str] = None
    plugin_timeout: float = 30.0
    max_plugins: int = 100
    
    def __post_init__(self):
        if self.disabled_plugins is None:
            self.disabled_plugins = []

@dataclass
class PluginMetadata:
    """Metadata for a plugin"""
    name: str
    version: str
    description: str
    author: str
    capabilities: List[str]
    dependencies: List[str]
    config_schema: Dict[str, Any]
    min_codex_version: str = "1.0.0"
    max_codex_version: str = "2.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """Create from dictionary"""
        return cls(**data)

class PluginCore:
    """
    🔌 The Core of Plugin Mysticism
    
    Orchestrates the discovery, loading, and management of agent plugins,
    creating a dynamic and extensible ritual framework.
    """
    
    def __init__(self, config: PluginConfig):
        self.config = config
        self.plugins: Dict[str, Any] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}
        self.plugin_instances: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        
        # Ensure plugins directory exists
        self.plugins_path = Path(config.plugins_directory)
        self.plugins_path.mkdir(exist_ok=True)
        
        # Load configuration
        self._load_plugin_config()
        
        logger.info(f"🔌 Plugin Core initialized - Directory: {self.plugins_path}")
    
    def start(self):
        """Start the plugin system"""
        if self.running:
            return
        
        logger.info("🔌 Starting Plugin System...")
        self.running = True
        
        if self.config.auto_discover:
            self.discover_plugins()
        
        if self.config.auto_load:
            self.load_all_plugins()
        
        if self.config.auto_activate:
            self.activate_all_plugins()
        
        logger.info(f"✨ Plugin System Active - {len(self.plugins)} plugins loaded")
    
    def stop(self):
        """Stop the plugin system"""
        if not self.running:
            return
        
        logger.info("🔌 Stopping Plugin System...")
        
        # Deactivate all plugins
        for plugin_name in list(self.plugin_instances.keys()):
            self.deactivate_plugin(plugin_name)
        
        # Unload all plugins
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        self.running = False
        logger.info("🌙 Plugin System Dormant")
    
    def discover_plugins(self) -> List[str]:
        """Discover plugins in the plugins directory"""
        discovered = []
        
        logger.info(f"🔍 Discovering plugins in {self.plugins_path}")
        
        # Look for Python files in the plugins directory
        for plugin_file in self.plugins_path.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            plugin_name = plugin_file.stem
            
            # Skip disabled plugins
            if plugin_name in self.config.disabled_plugins:
                logger.info(f"⏭️ Skipping disabled plugin: {plugin_name}")
                continue
            
            try:
                # Check if it's a valid plugin
                if self._is_valid_plugin(plugin_file):
                    self.plugin_status[plugin_name] = PluginStatus.DISCOVERED
                    discovered.append(plugin_name)
                    logger.info(f"🔍 Discovered plugin: {plugin_name}")
                else:
                    logger.debug(f"⚠️ Invalid plugin file: {plugin_file}")
            
            except Exception as e:
                logger.error(f"❌ Error discovering plugin {plugin_name}: {e}")
                self.plugin_status[plugin_name] = PluginStatus.ERROR
        
        logger.info(f"✅ Discovered {len(discovered)} plugins")
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        if plugin_name in self.plugins:
            logger.debug(f"Plugin {plugin_name} already loaded")
            return True
        
        if plugin_name in self.config.disabled_plugins:
            logger.info(f"⏭️ Plugin {plugin_name} is disabled")
            return False
        
        try:
            logger.info(f"📦 Loading plugin: {plugin_name}")
            self.plugin_status[plugin_name] = PluginStatus.LOADING
            
            # Import the plugin module
            plugin_path = self.plugins_path / f"{plugin_name}.py"
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for {plugin_name}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the plugin class
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                raise ValueError(f"No valid plugin class found in {plugin_name}")
            
            # Extract metadata
            metadata = self._extract_metadata(plugin_class)
            
            # Store plugin information
            self.plugins[plugin_name] = plugin_class
            self.plugin_metadata[plugin_name] = metadata
            self.plugin_status[plugin_name] = PluginStatus.LOADED
            
            logger.info(f"✅ Plugin loaded: {plugin_name} v{metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        try:
            # Deactivate first if active
            if plugin_name in self.plugin_instances:
                self.deactivate_plugin(plugin_name)
            
            # Remove from loaded plugins
            if plugin_name in self.plugins:
                del self.plugins[plugin_name]
            
            if plugin_name in self.plugin_metadata:
                del self.plugin_metadata[plugin_name]
            
            self.plugin_status[plugin_name] = PluginStatus.DISCOVERED
            
            logger.info(f"📤 Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def activate_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Activate a loaded plugin"""
        if plugin_name not in self.plugins:
            logger.error(f"❌ Plugin {plugin_name} not loaded")
            return False
        
        if plugin_name in self.plugin_instances:
            logger.debug(f"Plugin {plugin_name} already active")
            return True
        
        try:
            logger.info(f"🚀 Activating plugin: {plugin_name}")
            
            plugin_class = self.plugins[plugin_name]
            
            # Create plugin instance
            if config:
                instance = plugin_class(config)
            else:
                instance = plugin_class()
            
            # Initialize the plugin
            if hasattr(instance, 'initialize'):
                instance.initialize()
            
            # Store instance
            self.plugin_instances[plugin_name] = instance
            self.plugin_status[plugin_name] = PluginStatus.ACTIVE
            
            # Register event handlers if available
            self._register_plugin_handlers(plugin_name, instance)
            
            logger.info(f"✅ Plugin activated: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to activate plugin {plugin_name}: {e}")
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate an active plugin"""
        if plugin_name not in self.plugin_instances:
            logger.debug(f"Plugin {plugin_name} not active")
            return True
        
        try:
            logger.info(f"⏹️ Deactivating plugin: {plugin_name}")
            
            instance = self.plugin_instances[plugin_name]
            
            # Cleanup the plugin
            if hasattr(instance, 'cleanup'):
                instance.cleanup()
            
            # Unregister event handlers
            self._unregister_plugin_handlers(plugin_name)
            
            # Remove instance
            del self.plugin_instances[plugin_name]
            self.plugin_status[plugin_name] = PluginStatus.INACTIVE
            
            logger.info(f"✅ Plugin deactivated: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deactivate plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins"""
        results = {}
        
        for plugin_name, status in self.plugin_status.items():
            if status == PluginStatus.DISCOVERED:
                results[plugin_name] = self.load_plugin(plugin_name)
        
        return results
    
    def activate_all_plugins(self) -> Dict[str, bool]:
        """Activate all loaded plugins"""
        results = {}
        
        for plugin_name, status in self.plugin_status.items():
            if status == PluginStatus.LOADED:
                results[plugin_name] = self.activate_plugin(plugin_name)
        
        return results
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin"""
        if plugin_name not in self.plugin_status:
            return None
        
        info = {
            "name": plugin_name,
            "status": self.plugin_status[plugin_name].value,
            "loaded": plugin_name in self.plugins,
            "active": plugin_name in self.plugin_instances
        }
        
        if plugin_name in self.plugin_metadata:
            metadata = self.plugin_metadata[plugin_name]
            info.update({
                "version": metadata.version,
                "description": metadata.description,
                "author": metadata.author,
                "capabilities": metadata.capabilities,
                "dependencies": metadata.dependencies
            })
        
        return info
    
    def list_plugins(self, status_filter: Optional[PluginStatus] = None) -> List[Dict[str, Any]]:
        """List all plugins with optional status filter"""
        plugins = []
        
        for plugin_name in self.plugin_status:
            if status_filter and self.plugin_status[plugin_name] != status_filter:
                continue
            
            plugin_info = self.get_plugin_info(plugin_name)
            if plugin_info:
                plugins.append(plugin_info)
        
        return plugins
    
    def get_plugins_by_capability(self, capability: str) -> List[str]:
        """Get plugins that have a specific capability"""
        matching_plugins = []
        
        for plugin_name, metadata in self.plugin_metadata.items():
            if capability in metadata.capabilities:
                matching_plugins.append(plugin_name)
        
        return matching_plugins
    
    def call_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """Call a method on an active plugin"""
        if plugin_name not in self.plugin_instances:
            raise ValueError(f"Plugin {plugin_name} is not active")
        
        instance = self.plugin_instances[plugin_name]
        
        if not hasattr(instance, method_name):
            raise AttributeError(f"Plugin {plugin_name} has no method {method_name}")
        
        method = getattr(instance, method_name)
        return method(*args, **kwargs)
    
    def _is_valid_plugin(self, plugin_file: Path) -> bool:
        """Check if a file contains a valid plugin"""
        try:
            with open(plugin_file, 'r') as f:
                content = f.read()
            
            # Basic checks for plugin structure
            return (
                'class' in content and
                ('AgentPlugin' in content or 'Plugin' in content) and
                'def ' in content
            )
        except Exception:
            return False
    
    def _find_plugin_class(self, module) -> Optional[Type]:
        """Find the main plugin class in a module"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Look for classes that inherit from a plugin base class
            if hasattr(obj, '__bases__'):
                for base in obj.__bases__:
                    if 'Plugin' in base.__name__:
                        return obj
        
        # Fallback: look for any class with 'Plugin' in the name
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if 'Plugin' in name or 'Agent' in name:
                return obj
        
        return None
    
    def _extract_metadata(self, plugin_class: Type) -> PluginMetadata:
        """Extract metadata from a plugin class"""
        # Default metadata
        metadata = PluginMetadata(
            name=plugin_class.__name__,
            version="1.0.0",
            description=plugin_class.__doc__ or "No description available",
            author="Unknown",
            capabilities=[],
            dependencies=[],
            config_schema={}
        )
        
        # Override with class attributes if available
        if hasattr(plugin_class, 'PLUGIN_NAME'):
            metadata.name = plugin_class.PLUGIN_NAME
        
        if hasattr(plugin_class, 'PLUGIN_VERSION'):
            metadata.version = plugin_class.PLUGIN_VERSION
        
        if hasattr(plugin_class, 'PLUGIN_DESCRIPTION'):
            metadata.description = plugin_class.PLUGIN_DESCRIPTION
        
        if hasattr(plugin_class, 'PLUGIN_AUTHOR'):
            metadata.author = plugin_class.PLUGIN_AUTHOR
        
        if hasattr(plugin_class, 'PLUGIN_CAPABILITIES'):
            metadata.capabilities = plugin_class.PLUGIN_CAPABILITIES
        
        if hasattr(plugin_class, 'PLUGIN_DEPENDENCIES'):
            metadata.dependencies = plugin_class.PLUGIN_DEPENDENCIES
        
        if hasattr(plugin_class, 'PLUGIN_CONFIG_SCHEMA'):
            metadata.config_schema = plugin_class.PLUGIN_CONFIG_SCHEMA
        
        return metadata
    
    def _register_plugin_handlers(self, plugin_name: str, instance: Any):
        """Register event handlers for a plugin"""
        # Look for event handler methods
        for method_name in dir(instance):
            if method_name.startswith('on_'):
                event_type = method_name[3:]  # Remove 'on_' prefix
                
                if event_type not in self.event_handlers:
                    self.event_handlers[event_type] = []
                
                handler = getattr(instance, method_name)
                self.event_handlers[event_type].append((plugin_name, handler))
                
                logger.debug(f"📡 Registered handler: {plugin_name}.{method_name}")
    
    def _unregister_plugin_handlers(self, plugin_name: str):
        """Unregister event handlers for a plugin"""
        for event_type, handlers in self.event_handlers.items():
            self.event_handlers[event_type] = [
                (name, handler) for name, handler in handlers 
                if name != plugin_name
            ]
    
    def _load_plugin_config(self):
        """Load plugin configuration from file"""
        config_path = Path(self.config.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update disabled plugins list
                if 'disabled_plugins' in config_data:
                    self.config.disabled_plugins = config_data['disabled_plugins']
                
                logger.info(f"📋 Loaded plugin configuration from {config_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load plugin config: {e}")
    
    def save_plugin_config(self):
        """Save current plugin configuration to file"""
        config_data = {
            'disabled_plugins': self.config.disabled_plugins,
            'auto_discover': self.config.auto_discover,
            'auto_load': self.config.auto_load,
            'auto_activate': self.config.auto_activate
        }
        
        try:
            with open(self.config.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"💾 Saved plugin configuration to {self.config.config_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save plugin config: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive plugin system status"""
        status_counts = {}
        for status in self.plugin_status.values():
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
        
        return {
            "running": self.running,
            "plugins_directory": str(self.plugins_path),
            "total_plugins": len(self.plugin_status),
            "loaded_plugins": len(self.plugins),
            "active_plugins": len(self.plugin_instances),
            "status_breakdown": status_counts,
            "disabled_plugins": self.config.disabled_plugins,
            "auto_discover": self.config.auto_discover,
            "auto_load": self.config.auto_load,
            "auto_activate": self.config.auto_activate
        }
