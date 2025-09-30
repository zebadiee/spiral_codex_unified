
"""
🤖 Agent Plugin Base - Foundation for Mystical Agents

Base classes and interfaces for creating agent plugins that can be
dynamically discovered and integrated into the Spiral Codex framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class AgentCapability:
    """Represents a capability that an agent provides"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    async_capable: bool = False

class AgentPluginBase(ABC):
    """
    🤖 Base class for all agent plugins
    
    Provides the mystical foundation for creating agents that can be
    dynamically loaded and managed by the Spiral Codex framework.
    """
    
    # Plugin metadata (override in subclasses)
    PLUGIN_NAME = "BaseAgent"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Base agent plugin"
    PLUGIN_AUTHOR = "Spiral Codex"
    PLUGIN_CAPABILITIES = []
    PLUGIN_DEPENDENCIES = []
    PLUGIN_CONFIG_SCHEMA = {}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"plugin.{self.PLUGIN_NAME}")
        self.is_initialized = False
        self.is_running = False
        self.capabilities: List[AgentCapability] = []
        self.event_handlers: Dict[str, Callable] = {}
        
        # Initialize capabilities
        self._setup_capabilities()
    
    def initialize(self):
        """Initialize the agent plugin"""
        if self.is_initialized:
            return
        
        self.logger.info(f"🚀 Initializing {self.PLUGIN_NAME}")
        
        try:
            self._initialize_agent()
            self.is_initialized = True
            self.logger.info(f"✅ {self.PLUGIN_NAME} initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.PLUGIN_NAME}: {e}")
            raise
    
    def cleanup(self):
        """Cleanup the agent plugin"""
        if not self.is_initialized:
            return
        
        self.logger.info(f"🧹 Cleaning up {self.PLUGIN_NAME}")
        
        try:
            if self.is_running:
                self.stop()
            
            self._cleanup_agent()
            self.is_initialized = False
            self.logger.info(f"✅ {self.PLUGIN_NAME} cleaned up successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup {self.PLUGIN_NAME}: {e}")
    
    def start(self):
        """Start the agent"""
        if not self.is_initialized:
            raise RuntimeError("Agent must be initialized before starting")
        
        if self.is_running:
            return
        
        self.logger.info(f"▶️ Starting {self.PLUGIN_NAME}")
        
        try:
            self._start_agent()
            self.is_running = True
            self.logger.info(f"✅ {self.PLUGIN_NAME} started successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to start {self.PLUGIN_NAME}: {e}")
            raise
    
    def stop(self):
        """Stop the agent"""
        if not self.is_running:
            return
        
        self.logger.info(f"⏹️ Stopping {self.PLUGIN_NAME}")
        
        try:
            self._stop_agent()
            self.is_running = False
            self.logger.info(f"✅ {self.PLUGIN_NAME} stopped successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to stop {self.PLUGIN_NAME}: {e}")
    
    @abstractmethod
    def _initialize_agent(self):
        """Initialize agent-specific resources (override in subclasses)"""
        pass
    
    @abstractmethod
    def _cleanup_agent(self):
        """Cleanup agent-specific resources (override in subclasses)"""
        pass
    
    def _start_agent(self):
        """Start agent-specific processes (override in subclasses if needed)"""
        pass
    
    def _stop_agent(self):
        """Stop agent-specific processes (override in subclasses if needed)"""
        pass
    
    def _setup_capabilities(self):
        """Setup agent capabilities (override in subclasses)"""
        pass
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability"""
        return any(cap.name == capability_name for cap in self.capabilities)
    
    def execute_capability(self, capability_name: str, input_data: Dict[str, Any]) -> Any:
        """Execute a specific capability"""
        capability = next((cap for cap in self.capabilities if cap.name == capability_name), None)
        
        if not capability:
            raise ValueError(f"Capability '{capability_name}' not found")
        
        method_name = f"execute_{capability_name}"
        
        if not hasattr(self, method_name):
            raise NotImplementedError(f"Method '{method_name}' not implemented")
        
        method = getattr(self, method_name)
        
        if capability.async_capable and asyncio.iscoroutinefunction(method):
            return asyncio.create_task(method(input_data))
        else:
            return method(input_data)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        self.event_handlers[event_type] = handler
        self.logger.debug(f"📡 Registered handler for {event_type}")
    
    def handle_event(self, event_type: str, event_data: Dict[str, Any]):
        """Handle an incoming event"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type](event_data)
            except Exception as e:
                self.logger.error(f"❌ Error handling event {event_type}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.PLUGIN_NAME,
            "version": self.PLUGIN_VERSION,
            "initialized": self.is_initialized,
            "running": self.is_running,
            "capabilities": [cap.name for cap in self.capabilities],
            "config": self.config
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics (override in subclasses for specific metrics)"""
        return {
            "uptime": 0,
            "requests_processed": 0,
            "errors": 0,
            "last_activity": None
        }

class AgentPlugin(AgentPluginBase):
    """
    🤖 Concrete agent plugin class
    
    A ready-to-use agent plugin that can be extended for specific use cases.
    Provides common functionality and patterns for agent development.
    """
    
    PLUGIN_NAME = "GenericAgent"
    PLUGIN_DESCRIPTION = "Generic agent plugin with common functionality"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.request_count = 0
        self.error_count = 0
        self.last_activity = None
    
    def _initialize_agent(self):
        """Initialize the generic agent"""
        self.logger.info("🔧 Initializing generic agent capabilities")
        
        # Add basic capabilities
        self.capabilities.extend([
            AgentCapability(
                name="ping",
                description="Simple ping/pong capability",
                input_schema={"message": "string"},
                output_schema={"response": "string", "timestamp": "string"}
            ),
            AgentCapability(
                name="echo",
                description="Echo input data back",
                input_schema={"data": "any"},
                output_schema={"echoed_data": "any"}
            ),
            AgentCapability(
                name="status",
                description="Get agent status",
                input_schema={},
                output_schema={"status": "object"}
            )
        ])
    
    def _cleanup_agent(self):
        """Cleanup the generic agent"""
        self.logger.info("🧹 Cleaning up generic agent")
        self.request_count = 0
        self.error_count = 0
        self.last_activity = None
    
    def execute_ping(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ping capability"""
        from datetime import datetime
        
        self.request_count += 1
        self.last_activity = datetime.now()
        
        message = input_data.get("message", "ping")
        
        return {
            "response": f"pong: {message}",
            "timestamp": self.last_activity.isoformat()
        }
    
    def execute_echo(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute echo capability"""
        from datetime import datetime
        
        self.request_count += 1
        self.last_activity = datetime.now()
        
        return {
            "echoed_data": input_data.get("data", "no data provided")
        }
    
    def execute_status(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute status capability"""
        return self.get_status()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        from datetime import datetime
        
        uptime = 0
        if self.is_running and self.last_activity:
            uptime = (datetime.now() - self.last_activity).total_seconds()
        
        return {
            "uptime": uptime,
            "requests_processed": self.request_count,
            "errors": self.error_count,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
    
    # Event handlers (these will be auto-registered)
    def on_system_start(self, event_data: Dict[str, Any]):
        """Handle system start event"""
        self.logger.info("🌟 System started - agent ready")
    
    def on_system_stop(self, event_data: Dict[str, Any]):
        """Handle system stop event"""
        self.logger.info("🌙 System stopping - agent shutting down")
    
    def on_agent_message(self, event_data: Dict[str, Any]):
        """Handle agent message event"""
        message = event_data.get("message", "")
        sender = event_data.get("sender", "unknown")
        self.logger.info(f"📨 Received message from {sender}: {message}")
    
    def on_ritual_cycle(self, event_data: Dict[str, Any]):
        """Handle ritual cycle event"""
        ritual_type = event_data.get("ritual_type", "unknown")
        depth = event_data.get("recursion_depth", 0)
        self.logger.info(f"🌀 Ritual cycle: {ritual_type} (depth: {depth})")

# Utility functions for plugin development
def create_capability(name: str, description: str, 
                     input_schema: Optional[Dict[str, Any]] = None,
                     output_schema: Optional[Dict[str, Any]] = None,
                     async_capable: bool = False) -> AgentCapability:
    """Helper function to create agent capabilities"""
    return AgentCapability(
        name=name,
        description=description,
        input_schema=input_schema or {},
        output_schema=output_schema or {},
        async_capable=async_capable
    )

def validate_plugin_class(plugin_class: type) -> bool:
    """Validate that a class is a proper plugin"""
    required_attributes = ['PLUGIN_NAME', 'PLUGIN_VERSION']
    required_methods = ['initialize', 'cleanup']
    
    # Check required attributes
    for attr in required_attributes:
        if not hasattr(plugin_class, attr):
            return False
    
    # Check required methods
    for method in required_methods:
        if not hasattr(plugin_class, method):
            return False
    
    # Check inheritance
    if not issubclass(plugin_class, AgentPluginBase):
        return False
    
    return True
