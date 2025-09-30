
"""
🎛️ Plugin Manager - Orchestrator of Agent Plugins

High-level management interface for the plugin system,
providing convenient methods for plugin lifecycle management.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging

from .plugin_core import PluginCore, PluginConfig, PluginStatus
from .agent_plugin import AgentPluginBase

logger = logging.getLogger(__name__)

@dataclass
class PluginInfo:
    """Information about a plugin"""
    name: str
    version: str
    description: str
    author: str
    status: PluginStatus
    capabilities: List[str]
    dependencies: List[str]
    loaded: bool
    active: bool
    error_message: Optional[str] = None

class PluginManager:
    """
    🎛️ The Plugin Manager
    
    High-level interface for managing the lifecycle of agent plugins,
    providing convenient methods for discovery, loading, and orchestration.
    """
    
    def __init__(self, plugins_directory: str = "agents", config: Optional[PluginConfig] = None):
        self.config = config or PluginConfig(plugins_directory=plugins_directory)
        self.core = PluginCore(self.config)
        self.event_subscribers: Dict[str, List[Callable]] = {}
        
        logger.info(f"🎛️ Plugin Manager initialized - Directory: {plugins_directory}")
    
    def start(self):
        """Start the plugin manager"""
        self.core.start()
        logger.info("🎛️ Plugin Manager started")
    
    def stop(self):
        """Stop the plugin manager"""
        self.core.stop()
        logger.info("🎛️ Plugin Manager stopped")
    
    def discover(self) -> List[str]:
        """Discover available plugins"""
        return self.core.discover_plugins()
    
    def load(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        return self.core.load_plugin(plugin_name)
    
    def unload(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        return self.core.unload_plugin(plugin_name)
    
    def enable(self, plugin_name: str) -> bool:
        """Enable a plugin (load and activate)"""
        success = True
        
        # Remove from disabled list if present
        if plugin_name in self.config.disabled_plugins:
            self.config.disabled_plugins.remove(plugin_name)
            self.core.save_plugin_config()
        
        # Load the plugin
        if not self.core.load_plugin(plugin_name):
            success = False
        
        # Activate the plugin
        if success and not self.core.activate_plugin(plugin_name):
            success = False
        
        if success:
            logger.info(f"✅ Plugin enabled: {plugin_name}")
        else:
            logger.error(f"❌ Failed to enable plugin: {plugin_name}")
        
        return success
    
    def disable(self, plugin_name: str) -> bool:
        """Disable a plugin (deactivate and add to disabled list)"""
        success = True
        
        # Deactivate the plugin
        if not self.core.deactivate_plugin(plugin_name):
            success = False
        
        # Add to disabled list
        if plugin_name not in self.config.disabled_plugins:
            self.config.disabled_plugins.append(plugin_name)
            self.core.save_plugin_config()
        
        if success:
            logger.info(f"✅ Plugin disabled: {plugin_name}")
        else:
            logger.error(f"❌ Failed to disable plugin: {plugin_name}")
        
        return success
    
    def activate(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Activate a loaded plugin"""
        return self.core.activate_plugin(plugin_name, config)
    
    def deactivate(self, plugin_name: str) -> bool:
        """Deactivate an active plugin"""
        return self.core.deactivate_plugin(plugin_name)
    
    def reload(self, plugin_name: str) -> bool:
        """Reload a plugin (unload and load again)"""
        was_active = plugin_name in self.core.plugin_instances
        config = None
        
        # Store config if active
        if was_active:
            instance = self.core.plugin_instances[plugin_name]
            config = getattr(instance, 'config', None)
            self.deactivate(plugin_name)
        
        # Unload and reload
        if not self.unload(plugin_name):
            return False
        
        if not self.load(plugin_name):
            return False
        
        # Reactivate if it was active before
        if was_active:
            return self.activate(plugin_name, config)
        
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin"""
        info_dict = self.core.get_plugin_info(plugin_name)
        
        if not info_dict:
            return None
        
        return PluginInfo(
            name=info_dict["name"],
            version=info_dict.get("version", "unknown"),
            description=info_dict.get("description", "No description"),
            author=info_dict.get("author", "Unknown"),
            status=PluginStatus(info_dict["status"]),
            capabilities=info_dict.get("capabilities", []),
            dependencies=info_dict.get("dependencies", []),
            loaded=info_dict["loaded"],
            active=info_dict["active"]
        )
    
    def list_plugins(self, status_filter: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """List all plugins with optional status filter"""
        plugins = []
        
        for info_dict in self.core.list_plugins(status_filter):
            plugin_info = PluginInfo(
                name=info_dict["name"],
                version=info_dict.get("version", "unknown"),
                description=info_dict.get("description", "No description"),
                author=info_dict.get("author", "Unknown"),
                status=PluginStatus(info_dict["status"]),
                capabilities=info_dict.get("capabilities", []),
                dependencies=info_dict.get("dependencies", []),
                loaded=info_dict["loaded"],
                active=info_dict["active"]
            )
            plugins.append(plugin_info)
        
        return plugins
    
    def get_active_plugins(self) -> List[PluginInfo]:
        """Get all active plugins"""
        return self.list_plugins(PluginStatus.ACTIVE)
    
    def get_loaded_plugins(self) -> List[PluginInfo]:
        """Get all loaded plugins"""
        return self.list_plugins(PluginStatus.LOADED)
    
    def find_plugins_by_capability(self, capability: str) -> List[PluginInfo]:
        """Find plugins that have a specific capability"""
        matching_plugins = []
        plugin_names = self.core.get_plugins_by_capability(capability)
        
        for plugin_name in plugin_names:
            plugin_info = self.get_plugin(plugin_name)
            if plugin_info:
                matching_plugins.append(plugin_info)
        
        return matching_plugins
    
    def execute_plugin_capability(self, plugin_name: str, capability: str, input_data: Dict[str, Any]) -> Any:
        """Execute a capability on a specific plugin"""
        if plugin_name not in self.core.plugin_instances:
            raise ValueError(f"Plugin {plugin_name} is not active")
        
        instance = self.core.plugin_instances[plugin_name]
        
        if not isinstance(instance, AgentPluginBase):
            raise TypeError(f"Plugin {plugin_name} is not an agent plugin")
        
        return instance.execute_capability(capability, input_data)
    
    def broadcast_event(self, event_type: str, event_data: Dict[str, Any]):
        """Broadcast an event to all active plugins"""
        for plugin_name, instance in self.core.plugin_instances.items():
            try:
                if isinstance(instance, AgentPluginBase):
                    instance.handle_event(event_type, event_data)
                
                # Also call specific event handlers if they exist
                if event_type in self.core.event_handlers:
                    for handler_plugin_name, handler in self.core.event_handlers[event_type]:
                        if handler_plugin_name == plugin_name:
                            handler(event_data)
            
            except Exception as e:
                logger.error(f"❌ Error broadcasting event to {plugin_name}: {e}")
        
        # Also notify external subscribers
        if event_type in self.event_subscribers:
            for subscriber in self.event_subscribers[event_type]:
                try:
                    subscriber(event_data)
                except Exception as e:
                    logger.error(f"❌ Error notifying event subscriber: {e}")
    
    def subscribe_to_events(self, event_type: str, callback: Callable):
        """Subscribe to plugin events"""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        
        self.event_subscribers[event_type].append(callback)
        logger.debug(f"📡 Subscribed to {event_type} events")
    
    def unsubscribe_from_events(self, event_type: str, callback: Callable):
        """Unsubscribe from plugin events"""
        if event_type in self.event_subscribers:
            try:
                self.event_subscribers[event_type].remove(callback)
                logger.debug(f"📡 Unsubscribed from {event_type} events")
            except ValueError:
                pass
    
    def get_plugin_metrics(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific plugin"""
        if plugin_name not in self.core.plugin_instances:
            return None
        
        instance = self.core.plugin_instances[plugin_name]
        
        if isinstance(instance, AgentPluginBase):
            return instance.get_metrics()
        
        return None
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all active plugins"""
        metrics = {}
        
        for plugin_name in self.core.plugin_instances:
            plugin_metrics = self.get_plugin_metrics(plugin_name)
            if plugin_metrics:
                metrics[plugin_name] = plugin_metrics
        
        return metrics
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on all plugins"""
        health_status = {
            "overall_status": "healthy",
            "total_plugins": len(self.core.plugin_status),
            "active_plugins": len(self.core.plugin_instances),
            "plugin_health": {}
        }
        
        unhealthy_count = 0
        
        for plugin_name, status in self.core.plugin_status.items():
            plugin_health = {
                "status": status.value,
                "healthy": status not in [PluginStatus.ERROR, PluginStatus.DISABLED]
            }
            
            # Get additional health info for active plugins
            if plugin_name in self.core.plugin_instances:
                try:
                    instance = self.core.plugin_instances[plugin_name]
                    if isinstance(instance, AgentPluginBase):
                        plugin_health.update({
                            "initialized": instance.is_initialized,
                            "running": instance.is_running,
                            "capabilities_count": len(instance.capabilities)
                        })
                except Exception as e:
                    plugin_health["error"] = str(e)
                    plugin_health["healthy"] = False
            
            if not plugin_health["healthy"]:
                unhealthy_count += 1
            
            health_status["plugin_health"][plugin_name] = plugin_health
        
        # Determine overall status
        if unhealthy_count == 0:
            health_status["overall_status"] = "healthy"
        elif unhealthy_count < len(self.core.plugin_status) / 2:
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "unhealthy"
        
        health_status["unhealthy_count"] = unhealthy_count
        
        return health_status
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "plugin_manager": {
                "running": self.core.running,
                "plugins_directory": str(self.core.plugins_path),
                "config": {
                    "auto_discover": self.config.auto_discover,
                    "auto_load": self.config.auto_load,
                    "auto_activate": self.config.auto_activate,
                    "disabled_plugins": self.config.disabled_plugins
                }
            },
            "plugin_system": self.core.get_system_status(),
            "health": self.health_check(),
            "metrics": self.get_all_metrics()
        }
    
    async def async_execute_capability(self, plugin_name: str, capability: str, input_data: Dict[str, Any]) -> Any:
        """Execute a capability asynchronously"""
        if plugin_name not in self.core.plugin_instances:
            raise ValueError(f"Plugin {plugin_name} is not active")
        
        instance = self.core.plugin_instances[plugin_name]
        
        if not isinstance(instance, AgentPluginBase):
            raise TypeError(f"Plugin {plugin_name} is not an agent plugin")
        
        # Check if capability supports async execution
        capability_obj = next((cap for cap in instance.capabilities if cap.name == capability), None)
        
        if not capability_obj:
            raise ValueError(f"Capability '{capability}' not found in plugin {plugin_name}")
        
        if capability_obj.async_capable:
            method_name = f"execute_{capability}"
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)
                if asyncio.iscoroutinefunction(method):
                    return await method(input_data)
        
        # Fallback to sync execution
        return instance.execute_capability(capability, input_data)
    
    def create_plugin_template(self, plugin_name: str, author: str = "Unknown") -> str:
        """Create a template for a new plugin"""
        template = f'''"""
🤖 {plugin_name} - Mystical Agent Plugin

A custom agent plugin for the Spiral Codex framework.
"""

from spiralcodex.plugins import AgentPluginBase, create_capability
from typing import Dict, Any, Optional
import logging

class {plugin_name}Plugin(AgentPluginBase):
    """
    🤖 {plugin_name} Agent Plugin
    
    Custom agent with mystical capabilities for the Spiral Codex.
    """
    
    PLUGIN_NAME = "{plugin_name}"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Custom {plugin_name} agent plugin"
    PLUGIN_AUTHOR = "{author}"
    PLUGIN_CAPABILITIES = ["custom_action", "process_data"]
    PLUGIN_DEPENDENCIES = []
    PLUGIN_CONFIG_SCHEMA = {{
        "setting1": {{"type": "string", "default": "default_value"}},
        "setting2": {{"type": "integer", "default": 42}}
    }}
    
    def _initialize_agent(self):
        """Initialize the {plugin_name} agent"""
        self.logger.info("🔧 Initializing {plugin_name} agent")
        
        # Add custom capabilities
        self.capabilities.extend([
            create_capability(
                name="custom_action",
                description="Perform a custom action",
                input_schema={{"action": "string", "parameters": "object"}},
                output_schema={{"result": "string", "success": "boolean"}}
            ),
            create_capability(
                name="process_data",
                description="Process input data",
                input_schema={{"data": "any"}},
                output_schema={{"processed_data": "any"}}
            )
        ])
        
        # Initialize custom resources
        self.custom_state = {{}}
    
    def _cleanup_agent(self):
        """Cleanup the {plugin_name} agent"""
        self.logger.info("🧹 Cleaning up {plugin_name} agent")
        self.custom_state = {{}}
    
    def execute_custom_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom action capability"""
        action = input_data.get("action", "default")
        parameters = input_data.get("parameters", {{}})
        
        self.logger.info(f"🎯 Executing custom action: {{action}}")
        
        # Implement your custom logic here
        result = f"Executed {{action}} with parameters {{parameters}}"
        
        return {{
            "result": result,
            "success": True
        }}
    
    def execute_process_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute process data capability"""
        data = input_data.get("data")
        
        self.logger.info("📊 Processing data")
        
        # Implement your data processing logic here
        processed_data = f"Processed: {{data}}"
        
        return {{
            "processed_data": processed_data
        }}
    
    # Event handlers
    def on_ritual_cycle(self, event_data: Dict[str, Any]):
        """Handle ritual cycle events"""
        ritual_type = event_data.get("ritual_type", "unknown")
        self.logger.info(f"🌀 Participating in ritual: {{ritual_type}}")
    
    def on_agent_message(self, event_data: Dict[str, Any]):
        """Handle agent messages"""
        message = event_data.get("message", "")
        sender = event_data.get("sender", "unknown")
        self.logger.info(f"📨 Received message from {{sender}}: {{message}}")

# Plugin entry point
def create_plugin(config: Optional[Dict[str, Any]] = None) -> {plugin_name}Plugin:
    """Create and return the plugin instance"""
    return {plugin_name}Plugin(config)
'''
        
        return template
