
"""
🔄 Plugin Loader - Dynamic Discovery and Loading

Advanced plugin loading system with dependency resolution,
validation, and error handling for the mystical agent framework.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Tuple
import logging
from datetime import datetime

from .agent_plugin import AgentPluginBase, validate_plugin_class
from .plugin_registry import PluginRegistry, RegistryEntry

logger = logging.getLogger(__name__)

class PluginLoadError(Exception):
    """Exception raised when plugin loading fails"""
    pass

class PluginLoader:
    """
    🔄 The Plugin Loader
    
    Handles the mystical process of discovering, validating, and loading
    agent plugins from the filesystem into the runtime environment.
    """
    
    def __init__(self, plugins_directory: str = "agents", registry: Optional[PluginRegistry] = None):
        self.plugins_directory = Path(plugins_directory)
        self.registry = registry or PluginRegistry()
        self.loaded_modules: Dict[str, Any] = {}
        self.plugin_classes: Dict[str, Type] = {}
        
        # Ensure plugins directory exists
        self.plugins_directory.mkdir(exist_ok=True)
        
        logger.info(f"🔄 Plugin Loader initialized - Directory: {self.plugins_directory}")
    
    def discover_plugins(self, force_refresh: bool = False) -> List[str]:
        """Discover all plugins in the plugins directory"""
        discovered = []
        
        logger.info(f"🔍 Discovering plugins in {self.plugins_directory}")
        
        # Scan for Python files
        for plugin_file in self.plugins_directory.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            plugin_name = plugin_file.stem
            
            try:
                # Check if plugin has changed or needs refresh
                if force_refresh or self._plugin_needs_update(plugin_name, plugin_file):
                    plugin_info = self._analyze_plugin_file(plugin_file)
                    
                    if plugin_info:
                        # Register in registry
                        entry = RegistryEntry(
                            name=plugin_name,
                            version=plugin_info['version'],
                            description=plugin_info['description'],
                            author=plugin_info['author'],
                            file_path=str(plugin_file),
                            capabilities=plugin_info['capabilities'],
                            dependencies=plugin_info['dependencies'],
                            config_schema=plugin_info['config_schema'],
                            last_modified=datetime.fromtimestamp(plugin_file.stat().st_mtime),
                            checksum=self._calculate_file_checksum(plugin_file)
                        )
                        
                        self.registry.register_plugin(entry)
                        discovered.append(plugin_name)
                        
                        logger.info(f"🔍 Discovered plugin: {plugin_name} v{plugin_info['version']}")
                    else:
                        logger.debug(f"⚠️ Invalid plugin file: {plugin_file}")
                else:
                    # Plugin already registered and up to date
                    discovered.append(plugin_name)
                    logger.debug(f"🔍 Plugin up to date: {plugin_name}")
            
            except Exception as e:
                logger.error(f"❌ Error discovering plugin {plugin_name}: {e}")
        
        logger.info(f"✅ Discovered {len(discovered)} plugins")
        return discovered
    
    def load_plugin(self, plugin_name: str) -> Optional[Type]:
        """Load a specific plugin class"""
        if plugin_name in self.plugin_classes:
            logger.debug(f"Plugin {plugin_name} already loaded")
            return self.plugin_classes[plugin_name]
        
        # Get plugin info from registry
        entry = self.registry.get_plugin(plugin_name)
        if not entry:
            raise PluginLoadError(f"Plugin {plugin_name} not found in registry")
        
        if not entry.enabled:
            raise PluginLoadError(f"Plugin {plugin_name} is disabled")
        
        try:
            logger.info(f"📦 Loading plugin: {plugin_name}")
            
            # Load dependencies first
            self._load_dependencies(plugin_name)
            
            # Load the plugin module
            plugin_file = Path(entry.file_path)
            module = self._load_module(plugin_name, plugin_file)
            
            # Find and validate plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                raise PluginLoadError(f"No valid plugin class found in {plugin_name}")
            
            # Validate plugin class
            if not validate_plugin_class(plugin_class):
                raise PluginLoadError(f"Plugin class validation failed for {plugin_name}")
            
            # Store loaded plugin
            self.loaded_modules[plugin_name] = module
            self.plugin_classes[plugin_name] = plugin_class
            
            logger.info(f"✅ Plugin loaded: {plugin_name}")
            return plugin_class
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
            raise PluginLoadError(f"Failed to load plugin {plugin_name}: {e}")
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        try:
            # Remove from loaded classes
            if plugin_name in self.plugin_classes:
                del self.plugin_classes[plugin_name]
            
            # Remove module from cache
            if plugin_name in self.loaded_modules:
                del self.loaded_modules[plugin_name]
            
            # Remove from sys.modules if present
            module_name = f"plugin_{plugin_name}"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            logger.info(f"📤 Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> Optional[Type]:
        """Reload a plugin (unload and load again)"""
        self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name)
    
    def load_all_plugins(self, ignore_errors: bool = True) -> Dict[str, bool]:
        """Load all discovered plugins"""
        results = {}
        plugins = self.registry.list_plugins(enabled_only=True)
        
        # Sort by dependency order
        sorted_plugins = self._sort_by_dependencies([p.name for p in plugins])
        
        for plugin_name in sorted_plugins:
            try:
                self.load_plugin(plugin_name)
                results[plugin_name] = True
            except Exception as e:
                logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
                results[plugin_name] = False
                
                if not ignore_errors:
                    break
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"📦 Loaded {successful}/{len(results)} plugins")
        
        return results
    
    def validate_plugin_file(self, plugin_file: Path) -> Tuple[bool, List[str]]:
        """Validate a plugin file"""
        errors = []
        
        try:
            # Check file exists and is readable
            if not plugin_file.exists():
                errors.append("File does not exist")
                return False, errors
            
            if not plugin_file.is_file():
                errors.append("Path is not a file")
                return False, errors
            
            # Try to parse the file
            try:
                with open(plugin_file, 'r') as f:
                    content = f.read()
            except Exception as e:
                errors.append(f"Cannot read file: {e}")
                return False, errors
            
            # Basic syntax check
            try:
                compile(content, str(plugin_file), 'exec')
            except SyntaxError as e:
                errors.append(f"Syntax error: {e}")
                return False, errors
            
            # Try to load and analyze
            try:
                plugin_info = self._analyze_plugin_file(plugin_file)
                if not plugin_info:
                    errors.append("No valid plugin class found")
                    return False, errors
            except Exception as e:
                errors.append(f"Analysis failed: {e}")
                return False, errors
            
            return True, []
            
        except Exception as e:
            errors.append(f"Validation failed: {e}")
            return False, errors
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin"""
        entry = self.registry.get_plugin(plugin_name)
        if not entry:
            return None
        
        info = {
            "name": entry.name,
            "version": entry.version,
            "description": entry.description,
            "author": entry.author,
            "file_path": entry.file_path,
            "capabilities": entry.capabilities,
            "dependencies": entry.dependencies,
            "config_schema": entry.config_schema,
            "last_modified": entry.last_modified.isoformat(),
            "checksum": entry.checksum,
            "enabled": entry.enabled,
            "loaded": plugin_name in self.plugin_classes
        }
        
        # Add runtime information if loaded
        if plugin_name in self.plugin_classes:
            plugin_class = self.plugin_classes[plugin_name]
            info.update({
                "class_name": plugin_class.__name__,
                "module_name": plugin_class.__module__,
                "base_classes": [base.__name__ for base in plugin_class.__bases__]
            })
        
        return info
    
    def _plugin_needs_update(self, plugin_name: str, plugin_file: Path) -> bool:
        """Check if a plugin needs to be updated in the registry"""
        entry = self.registry.get_plugin(plugin_name)
        
        if not entry:
            return True  # New plugin
        
        # Check file modification time
        file_mtime = datetime.fromtimestamp(plugin_file.stat().st_mtime)
        if file_mtime > entry.last_modified:
            return True
        
        # Check file checksum
        current_checksum = self._calculate_file_checksum(plugin_file)
        if current_checksum != entry.checksum:
            return True
        
        return False
    
    def _analyze_plugin_file(self, plugin_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a plugin file to extract metadata"""
        try:
            # Load the module temporarily for analysis
            spec = importlib.util.spec_from_file_location("temp_plugin", plugin_file)
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                return None
            
            # Extract metadata
            return {
                "version": getattr(plugin_class, 'PLUGIN_VERSION', '1.0.0'),
                "description": getattr(plugin_class, 'PLUGIN_DESCRIPTION', plugin_class.__doc__ or 'No description'),
                "author": getattr(plugin_class, 'PLUGIN_AUTHOR', 'Unknown'),
                "capabilities": getattr(plugin_class, 'PLUGIN_CAPABILITIES', []),
                "dependencies": getattr(plugin_class, 'PLUGIN_DEPENDENCIES', []),
                "config_schema": getattr(plugin_class, 'PLUGIN_CONFIG_SCHEMA', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze plugin file {plugin_file}: {e}")
            return None
    
    def _find_plugin_class(self, module) -> Optional[Type]:
        """Find the main plugin class in a module"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip imported classes
            if obj.__module__ != module.__name__:
                continue
            
            # Look for classes that inherit from AgentPluginBase
            if issubclass(obj, AgentPluginBase) and obj != AgentPluginBase:
                return obj
        
        return None
    
    def _load_module(self, plugin_name: str, plugin_file: Path):
        """Load a plugin module"""
        module_name = f"plugin_{plugin_name}"
        
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"Could not create module spec for {plugin_name}")
        
        module = importlib.util.module_from_spec(spec)
        
        # Add to sys.modules before execution
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            # Remove from sys.modules if execution failed
            if module_name in sys.modules:
                del sys.modules[module_name]
            raise PluginLoadError(f"Failed to execute module {plugin_name}: {e}")
    
    def _load_dependencies(self, plugin_name: str):
        """Load plugin dependencies"""
        dependencies = self.registry.get_dependencies(plugin_name)
        
        for dep in dependencies:
            if dep not in self.plugin_classes:
                logger.info(f"🔗 Loading dependency: {dep} for {plugin_name}")
                self.load_plugin(dep)
    
    def _sort_by_dependencies(self, plugin_names: List[str]) -> List[str]:
        """Sort plugins by dependency order (dependencies first)"""
        sorted_plugins = []
        visited = set()
        temp_visited = set()
        
        def visit(plugin: str):
            if plugin in temp_visited:
                # Circular dependency detected
                logger.warning(f"⚠️ Circular dependency detected involving {plugin}")
                return
            
            if plugin in visited:
                return
            
            temp_visited.add(plugin)
            
            # Visit dependencies first
            dependencies = self.registry.get_dependencies(plugin)
            for dep in dependencies:
                if dep in plugin_names:  # Only consider plugins we're loading
                    visit(dep)
            
            temp_visited.remove(plugin)
            visited.add(plugin)
            sorted_plugins.append(plugin)
        
        for plugin in plugin_names:
            if plugin not in visited:
                visit(plugin)
        
        return sorted_plugins
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def get_loader_stats(self) -> Dict[str, Any]:
        """Get loader statistics"""
        return {
            "plugins_directory": str(self.plugins_directory),
            "loaded_modules": len(self.loaded_modules),
            "loaded_classes": len(self.plugin_classes),
            "registry_plugins": len(self.registry.entries),
            "enabled_plugins": len(self.registry.list_plugins(enabled_only=True)),
            "circular_dependencies": len(self.registry.check_circular_dependencies())
        }
