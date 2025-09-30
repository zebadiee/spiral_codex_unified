
"""
🔌 Tests for Spiral Codex Plugin System

Test suite for the plugin architecture, ensuring agents can be
dynamically discovered, loaded, and managed with mystical precision.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import json

from spiralcodex.plugins import (
    PluginCore, PluginConfig, PluginStatus,
    PluginManager, PluginInfo,
    AgentPlugin, AgentPluginBase, create_capability,
    PluginRegistry, RegistryEntry,
    PluginLoader, PluginLoadError
)

class TestPluginCore:
    """Test the core plugin system functionality"""
    
    @pytest.fixture
    def temp_plugins_dir(self):
        """Create a temporary plugins directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def plugin_config(self, temp_plugins_dir):
        """Create a test plugin configuration"""
        return PluginConfig(
            plugins_directory=temp_plugins_dir,
            auto_discover=True,
            auto_load=False,
            auto_activate=False
        )
    
    @pytest.fixture
    def plugin_core(self, plugin_config):
        """Create a test plugin core instance"""
        return PluginCore(plugin_config)
    
    def test_plugin_core_initialization(self, plugin_core, temp_plugins_dir):
        """Test plugin core initializes correctly"""
        assert plugin_core.config.plugins_directory == temp_plugins_dir
        assert plugin_core.plugins == {}
        assert plugin_core.plugin_status == {}
        assert not plugin_core.running
        assert Path(temp_plugins_dir).exists()
    
    def test_plugin_discovery(self, plugin_core, temp_plugins_dir):
        """Test plugin discovery"""
        # Create a test plugin file
        plugin_file = Path(temp_plugins_dir) / "test_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase

class TestPlugin(AgentPluginBase):
    PLUGIN_NAME = "TestPlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        # Discover plugins
        discovered = plugin_core.discover_plugins()
        
        assert "test_plugin" in discovered
        assert plugin_core.plugin_status["test_plugin"] == PluginStatus.DISCOVERED
    
    def test_plugin_loading(self, plugin_core, temp_plugins_dir):
        """Test plugin loading"""
        # Create a test plugin file
        plugin_file = Path(temp_plugins_dir) / "loadable_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase

class LoadablePlugin(AgentPluginBase):
    PLUGIN_NAME = "LoadablePlugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Test plugin for loading"
    PLUGIN_AUTHOR = "Test Author"
    PLUGIN_CAPABILITIES = ["test_capability"]
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        # Discover and load
        plugin_core.discover_plugins()
        success = plugin_core.load_plugin("loadable_plugin")
        
        assert success
        assert "loadable_plugin" in plugin_core.plugins
        assert plugin_core.plugin_status["loadable_plugin"] == PluginStatus.LOADED
        assert "loadable_plugin" in plugin_core.plugin_metadata
    
    def test_plugin_activation(self, plugin_core, temp_plugins_dir):
        """Test plugin activation"""
        # Create and load a plugin
        plugin_file = Path(temp_plugins_dir) / "activatable_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase

class ActivatablePlugin(AgentPluginBase):
    PLUGIN_NAME = "ActivatablePlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def _initialize_agent(self):
        self.test_value = "initialized"
    
    def _cleanup_agent(self):
        self.test_value = None
'''
        plugin_file.write_text(plugin_content)
        
        plugin_core.discover_plugins()
        plugin_core.load_plugin("activatable_plugin")
        
        # Activate plugin
        success = plugin_core.activate_plugin("activatable_plugin")
        
        assert success
        assert "activatable_plugin" in plugin_core.plugin_instances
        assert plugin_core.plugin_status["activatable_plugin"] == PluginStatus.ACTIVE
        
        # Check instance
        instance = plugin_core.plugin_instances["activatable_plugin"]
        assert instance.test_value == "initialized"
    
    def test_plugin_deactivation(self, plugin_core, temp_plugins_dir):
        """Test plugin deactivation"""
        # Create, load, and activate a plugin
        plugin_file = Path(temp_plugins_dir) / "deactivatable_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase

class DeactivatablePlugin(AgentPluginBase):
    PLUGIN_NAME = "DeactivatablePlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        plugin_core.discover_plugins()
        plugin_core.load_plugin("deactivatable_plugin")
        plugin_core.activate_plugin("deactivatable_plugin")
        
        # Deactivate plugin
        success = plugin_core.deactivate_plugin("deactivatable_plugin")
        
        assert success
        assert "deactivatable_plugin" not in plugin_core.plugin_instances
        assert plugin_core.plugin_status["deactivatable_plugin"] == PluginStatus.INACTIVE
    
    def test_system_status(self, plugin_core):
        """Test system status reporting"""
        status = plugin_core.get_system_status()
        
        assert "running" in status
        assert "plugins_directory" in status
        assert "total_plugins" in status
        assert "loaded_plugins" in status
        assert "active_plugins" in status

class TestAgentPlugin:
    """Test the agent plugin base classes"""
    
    def test_agent_plugin_base_initialization(self):
        """Test agent plugin base initialization"""
        config = {"test_setting": "test_value"}
        plugin = AgentPlugin(config)
        
        assert plugin.config == config
        assert not plugin.is_initialized
        assert not plugin.is_running
        assert plugin.capabilities == []
    
    def test_agent_plugin_lifecycle(self):
        """Test agent plugin lifecycle"""
        plugin = AgentPlugin()
        
        # Initialize
        plugin.initialize()
        assert plugin.is_initialized
        assert len(plugin.capabilities) > 0
        
        # Start
        plugin.start()
        assert plugin.is_running
        
        # Stop
        plugin.stop()
        assert not plugin.is_running
        
        # Cleanup
        plugin.cleanup()
        assert not plugin.is_initialized
    
    def test_capability_execution(self):
        """Test capability execution"""
        plugin = AgentPlugin()
        plugin.initialize()
        
        # Test ping capability
        result = plugin.execute_capability("ping", {"message": "test"})
        
        assert "response" in result
        assert "timestamp" in result
        assert "test" in result["response"]
    
    def test_capability_creation(self):
        """Test capability creation helper"""
        capability = create_capability(
            name="test_capability",
            description="Test capability",
            input_schema={"input": "string"},
            output_schema={"output": "string"}
        )
        
        assert capability.name == "test_capability"
        assert capability.description == "Test capability"
        assert capability.input_schema == {"input": "string"}
        assert capability.output_schema == {"output": "string"}
    
    def test_event_handling(self):
        """Test event handling"""
        plugin = AgentPlugin()
        plugin.initialize()
        
        # Test event handler registration
        test_events = []
        
        def test_handler(event_data):
            test_events.append(event_data)
        
        plugin.register_event_handler("test_event", test_handler)
        
        # Handle event
        plugin.handle_event("test_event", {"test": "data"})
        
        assert len(test_events) == 1
        assert test_events[0]["test"] == "data"

class TestPluginManager:
    """Test the plugin manager"""
    
    @pytest.fixture
    def temp_plugins_dir(self):
        """Create a temporary plugins directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def plugin_manager(self, temp_plugins_dir):
        """Create a test plugin manager"""
        return PluginManager(temp_plugins_dir)
    
    def test_plugin_manager_initialization(self, plugin_manager, temp_plugins_dir):
        """Test plugin manager initialization"""
        assert plugin_manager.config.plugins_directory == temp_plugins_dir
        assert not plugin_manager.core.running
    
    def test_plugin_enable_disable(self, plugin_manager, temp_plugins_dir):
        """Test plugin enable/disable functionality"""
        # Create a test plugin
        plugin_file = Path(temp_plugins_dir) / "manageable_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase

class ManageablePlugin(AgentPluginBase):
    PLUGIN_NAME = "ManageablePlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        plugin_manager.start()
        
        # Enable plugin
        success = plugin_manager.enable("manageable_plugin")
        assert success
        
        # Check if active
        active_plugins = plugin_manager.get_active_plugins()
        assert len(active_plugins) == 1
        assert active_plugins[0].name == "ManageablePlugin"
        
        # Disable plugin
        success = plugin_manager.disable("manageable_plugin")
        assert success
        
        # Check if disabled
        active_plugins = plugin_manager.get_active_plugins()
        assert len(active_plugins) == 0
        
        plugin_manager.stop()
    
    def test_health_check(self, plugin_manager):
        """Test plugin health check"""
        plugin_manager.start()
        
        health = plugin_manager.health_check()
        
        assert "overall_status" in health
        assert "total_plugins" in health
        assert "active_plugins" in health
        assert "plugin_health" in health
        
        plugin_manager.stop()
    
    def test_event_broadcasting(self, plugin_manager, temp_plugins_dir):
        """Test event broadcasting to plugins"""
        # Create a test plugin with event handler
        plugin_file = Path(temp_plugins_dir) / "event_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase

class EventPlugin(AgentPluginBase):
    PLUGIN_NAME = "EventPlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.received_events = []
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
    
    def on_test_event(self, event_data):
        self.received_events.append(event_data)
'''
        plugin_file.write_text(plugin_content)
        
        plugin_manager.start()
        plugin_manager.enable("event_plugin")
        
        # Broadcast event
        plugin_manager.broadcast_event("test_event", {"message": "test"})
        
        # Check if event was received
        instance = plugin_manager.core.plugin_instances["event_plugin"]
        assert len(instance.received_events) == 1
        assert instance.received_events[0]["message"] == "test"
        
        plugin_manager.stop()

class TestPluginRegistry:
    """Test the plugin registry"""
    
    @pytest.fixture
    def temp_registry_file(self):
        """Create a temporary registry file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_file.close()
        yield temp_file.name
        Path(temp_file.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def plugin_registry(self, temp_registry_file):
        """Create a test plugin registry"""
        return PluginRegistry(temp_registry_file)
    
    @pytest.fixture
    def test_entry(self):
        """Create a test registry entry"""
        from datetime import datetime
        return RegistryEntry(
            name="TestPlugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            file_path="/test/path.py",
            capabilities=["test_capability"],
            dependencies=[],
            config_schema={},
            last_modified=datetime.now(),
            checksum="test_checksum"
        )
    
    def test_registry_initialization(self, plugin_registry, temp_registry_file):
        """Test registry initialization"""
        assert plugin_registry.registry_file == Path(temp_registry_file)
        assert plugin_registry.entries == {}
        assert plugin_registry.capability_index == {}
    
    def test_plugin_registration(self, plugin_registry, test_entry):
        """Test plugin registration"""
        success = plugin_registry.register_plugin(test_entry)
        
        assert success
        assert "TestPlugin" in plugin_registry.entries
        assert "test_capability" in plugin_registry.capability_index
        assert "TestPlugin" in plugin_registry.capability_index["test_capability"]
    
    def test_capability_search(self, plugin_registry, test_entry):
        """Test finding plugins by capability"""
        plugin_registry.register_plugin(test_entry)
        
        plugins = plugin_registry.find_by_capability("test_capability")
        
        assert len(plugins) == 1
        assert plugins[0].name == "TestPlugin"
    
    def test_registry_persistence(self, plugin_registry, test_entry, temp_registry_file):
        """Test registry persistence"""
        # Register plugin
        plugin_registry.register_plugin(test_entry)
        
        # Create new registry instance
        new_registry = PluginRegistry(temp_registry_file)
        
        # Check if plugin was loaded
        assert "TestPlugin" in new_registry.entries
        assert "test_capability" in new_registry.capability_index
    
    def test_dependency_resolution(self, plugin_registry):
        """Test dependency resolution"""
        from datetime import datetime
        
        # Create plugins with dependencies
        plugin_a = RegistryEntry(
            name="PluginA",
            version="1.0.0",
            description="Plugin A",
            author="Test",
            file_path="/a.py",
            capabilities=[],
            dependencies=["PluginB", "PluginC"],
            config_schema={},
            last_modified=datetime.now(),
            checksum="a"
        )
        
        plugin_b = RegistryEntry(
            name="PluginB",
            version="1.0.0",
            description="Plugin B",
            author="Test",
            file_path="/b.py",
            capabilities=[],
            dependencies=["PluginC"],
            config_schema={},
            last_modified=datetime.now(),
            checksum="b"
        )
        
        plugin_c = RegistryEntry(
            name="PluginC",
            version="1.0.0",
            description="Plugin C",
            author="Test",
            file_path="/c.py",
            capabilities=[],
            dependencies=[],
            config_schema={},
            last_modified=datetime.now(),
            checksum="c"
        )
        
        plugin_registry.register_plugin(plugin_a)
        plugin_registry.register_plugin(plugin_b)
        plugin_registry.register_plugin(plugin_c)
        
        # Resolve dependencies
        deps = plugin_registry.resolve_dependencies("PluginA")
        
        assert "PluginC" in deps
        assert "PluginB" in deps
        assert deps.index("PluginC") < deps.index("PluginB")  # C should come before B

class TestPluginLoader:
    """Test the plugin loader"""
    
    @pytest.fixture
    def temp_plugins_dir(self):
        """Create a temporary plugins directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def plugin_loader(self, temp_plugins_dir):
        """Create a test plugin loader"""
        return PluginLoader(temp_plugins_dir)
    
    def test_plugin_discovery(self, plugin_loader, temp_plugins_dir):
        """Test plugin discovery"""
        # Create test plugin files
        plugin_file = Path(temp_plugins_dir) / "discoverable_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase

class DiscoverablePlugin(AgentPluginBase):
    PLUGIN_NAME = "DiscoverablePlugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Discoverable test plugin"
    PLUGIN_AUTHOR = "Test Author"
    PLUGIN_CAPABILITIES = ["discovery_test"]
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        plugin_file.write_text(plugin_content)
        
        # Discover plugins
        discovered = plugin_loader.discover_plugins()
        
        assert "discoverable_plugin" in discovered
        
        # Check registry
        entry = plugin_loader.registry.get_plugin("discoverable_plugin")
        assert entry is not None
        assert entry.name == "DiscoverablePlugin"
        assert entry.version == "1.0.0"
        assert "discovery_test" in entry.capabilities
    
    def test_plugin_validation(self, plugin_loader, temp_plugins_dir):
        """Test plugin file validation"""
        # Valid plugin
        valid_plugin = Path(temp_plugins_dir) / "valid_plugin.py"
        valid_content = '''
from spiralcodex.plugins import AgentPluginBase

class ValidPlugin(AgentPluginBase):
    PLUGIN_NAME = "ValidPlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        valid_plugin.write_text(valid_content)
        
        # Invalid plugin (syntax error)
        invalid_plugin = Path(temp_plugins_dir) / "invalid_plugin.py"
        invalid_content = '''
from spiralcodex.plugins import AgentPluginBase

class InvalidPlugin(AgentPluginBase):
    PLUGIN_NAME = "InvalidPlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
    
    # Syntax error: missing closing parenthesis
    def broken_method(self:
        pass
'''
        invalid_plugin.write_text(invalid_content)
        
        # Test validation
        valid_result, valid_errors = plugin_loader.validate_plugin_file(valid_plugin)
        invalid_result, invalid_errors = plugin_loader.validate_plugin_file(invalid_plugin)
        
        assert valid_result
        assert len(valid_errors) == 0
        
        assert not invalid_result
        assert len(invalid_errors) > 0
        assert "syntax error" in invalid_errors[0].lower()
    
    def test_plugin_loading_with_dependencies(self, plugin_loader, temp_plugins_dir):
        """Test loading plugins with dependencies"""
        # Create dependency plugin
        dep_plugin = Path(temp_plugins_dir) / "dependency_plugin.py"
        dep_content = '''
from spiralcodex.plugins import AgentPluginBase

class DependencyPlugin(AgentPluginBase):
    PLUGIN_NAME = "DependencyPlugin"
    PLUGIN_VERSION = "1.0.0"
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        dep_plugin.write_text(dep_content)
        
        # Create main plugin with dependency
        main_plugin = Path(temp_plugins_dir) / "main_plugin.py"
        main_content = '''
from spiralcodex.plugins import AgentPluginBase

class MainPlugin(AgentPluginBase):
    PLUGIN_NAME = "MainPlugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DEPENDENCIES = ["DependencyPlugin"]
    
    def _initialize_agent(self):
        pass
    
    def _cleanup_agent(self):
        pass
'''
        main_plugin.write_text(main_content)
        
        # Discover plugins
        plugin_loader.discover_plugins()
        
        # Load main plugin (should load dependency first)
        main_class = plugin_loader.load_plugin("main_plugin")
        
        assert main_class is not None
        assert "dependency_plugin" in plugin_loader.plugin_classes
        assert "main_plugin" in plugin_loader.plugin_classes

# Integration tests
class TestPluginIntegration:
    """Integration tests for the complete plugin system"""
    
    @pytest.fixture
    def temp_plugins_dir(self):
        """Create a temporary plugins directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_plugin_lifecycle(self, temp_plugins_dir):
        """Test complete plugin lifecycle"""
        # Create a comprehensive test plugin
        plugin_file = Path(temp_plugins_dir) / "lifecycle_plugin.py"
        plugin_content = '''
from spiralcodex.plugins import AgentPluginBase, create_capability
from typing import Dict, Any

class LifecyclePlugin(AgentPluginBase):
    PLUGIN_NAME = "LifecyclePlugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Plugin for testing complete lifecycle"
    PLUGIN_AUTHOR = "Test Suite"
    PLUGIN_CAPABILITIES = ["lifecycle_test", "echo_test"]
    
    def _initialize_agent(self):
        self.test_state = "initialized"
        self.capabilities.extend([
            create_capability(
                name="lifecycle_test",
                description="Test lifecycle capability",
                input_schema={"action": "string"},
                output_schema={"result": "string", "state": "string"}
            ),
            create_capability(
                name="echo_test",
                description="Echo input data",
                input_schema={"data": "any"},
                output_schema={"echoed": "any"}
            )
        ])
    
    def _cleanup_agent(self):
        self.test_state = "cleaned"
    
    def _start_agent(self):
        self.test_state = "running"
    
    def _stop_agent(self):
        self.test_state = "stopped"
    
    def execute_lifecycle_test(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "status")
        return {
            "result": f"Executed {action}",
            "state": self.test_state
        }
    
    def execute_echo_test(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "echoed": input_data.get("data", "no data")
        }
    
    def on_test_event(self, event_data: Dict[str, Any]):
        self.test_state = f"event_received_{event_data.get('type', 'unknown')}"
'''
        plugin_file.write_text(plugin_content)
        
        # Test complete lifecycle
        manager = PluginManager(temp_plugins_dir)
        manager.start()
        
        # Plugin should be discovered and loaded
        plugins = manager.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "LifecyclePlugin"
        
        # Enable plugin
        success = manager.enable("lifecycle_plugin")
        assert success
        
        # Test capability execution
        result = manager.execute_plugin_capability(
            "lifecycle_plugin", 
            "lifecycle_test", 
            {"action": "test"}
        )
        assert result["result"] == "Executed test"
        assert result["state"] == "running"
        
        # Test event broadcasting
        manager.broadcast_event("test_event", {"type": "integration"})
        
        # Check event was handled
        instance = manager.core.plugin_instances["lifecycle_plugin"]
        assert instance.test_state == "event_received_integration"
        
        # Test health check
        health = manager.health_check()
        assert health["overall_status"] == "healthy"
        assert health["active_plugins"] == 1
        
        # Disable plugin
        success = manager.disable("lifecycle_plugin")
        assert success
        
        # Check final state
        active_plugins = manager.get_active_plugins()
        assert len(active_plugins) == 0
        
        manager.stop()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
