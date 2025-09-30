
"""
📋 Plugin Registry - Central Directory of Mystical Agents

Maintains a centralized registry of all available plugins,
their capabilities, and metadata for discovery and management.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class RegistryEntry:
    """Entry in the plugin registry"""
    name: str
    version: str
    description: str
    author: str
    file_path: str
    capabilities: List[str]
    dependencies: List[str]
    config_schema: Dict[str, Any]
    last_modified: datetime
    checksum: str
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['last_modified'] = self.last_modified.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegistryEntry':
        """Create from dictionary"""
        data['last_modified'] = datetime.fromisoformat(data['last_modified'])
        return cls(**data)

class PluginRegistry:
    """
    📋 The Plugin Registry
    
    Maintains the sacred directory of all plugins, tracking their
    capabilities, dependencies, and mystical properties.
    """
    
    def __init__(self, registry_file: str = "plugin_registry.json"):
        self.registry_file = Path(registry_file)
        self.entries: Dict[str, RegistryEntry] = {}
        self.capability_index: Dict[str, Set[str]] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        # Load existing registry
        self._load_registry()
        
        logger.info(f"📋 Plugin Registry initialized - File: {self.registry_file}")
    
    def register_plugin(self, entry: RegistryEntry) -> bool:
        """Register a plugin in the registry"""
        try:
            # Update entry
            self.entries[entry.name] = entry
            
            # Update capability index
            for capability in entry.capabilities:
                if capability not in self.capability_index:
                    self.capability_index[capability] = set()
                self.capability_index[capability].add(entry.name)
            
            # Update dependency graph
            self.dependency_graph[entry.name] = set(entry.dependencies)
            
            # Save registry
            self._save_registry()
            
            logger.info(f"📋 Plugin registered: {entry.name} v{entry.version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register plugin {entry.name}: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin from the registry"""
        try:
            if plugin_name not in self.entries:
                logger.warning(f"⚠️ Plugin {plugin_name} not found in registry")
                return False
            
            entry = self.entries[plugin_name]
            
            # Remove from capability index
            for capability in entry.capabilities:
                if capability in self.capability_index:
                    self.capability_index[capability].discard(plugin_name)
                    if not self.capability_index[capability]:
                        del self.capability_index[capability]
            
            # Remove from dependency graph
            if plugin_name in self.dependency_graph:
                del self.dependency_graph[plugin_name]
            
            # Remove entry
            del self.entries[plugin_name]
            
            # Save registry
            self._save_registry()
            
            logger.info(f"📋 Plugin unregistered: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[RegistryEntry]:
        """Get a plugin entry by name"""
        return self.entries.get(plugin_name)
    
    def list_plugins(self, enabled_only: bool = False) -> List[RegistryEntry]:
        """List all plugins in the registry"""
        plugins = list(self.entries.values())
        
        if enabled_only:
            plugins = [p for p in plugins if p.enabled]
        
        return sorted(plugins, key=lambda p: p.name)
    
    def find_by_capability(self, capability: str) -> List[RegistryEntry]:
        """Find plugins that provide a specific capability"""
        if capability not in self.capability_index:
            return []
        
        plugin_names = self.capability_index[capability]
        return [self.entries[name] for name in plugin_names if name in self.entries]
    
    def find_by_author(self, author: str) -> List[RegistryEntry]:
        """Find plugins by author"""
        return [entry for entry in self.entries.values() if entry.author == author]
    
    def search_plugins(self, query: str) -> List[RegistryEntry]:
        """Search plugins by name, description, or capabilities"""
        query_lower = query.lower()
        matching_plugins = []
        
        for entry in self.entries.values():
            # Search in name
            if query_lower in entry.name.lower():
                matching_plugins.append(entry)
                continue
            
            # Search in description
            if query_lower in entry.description.lower():
                matching_plugins.append(entry)
                continue
            
            # Search in capabilities
            for capability in entry.capabilities:
                if query_lower in capability.lower():
                    matching_plugins.append(entry)
                    break
        
        return matching_plugins
    
    def get_dependencies(self, plugin_name: str) -> List[str]:
        """Get dependencies for a plugin"""
        if plugin_name not in self.dependency_graph:
            return []
        
        return list(self.dependency_graph[plugin_name])
    
    def get_dependents(self, plugin_name: str) -> List[str]:
        """Get plugins that depend on the given plugin"""
        dependents = []
        
        for plugin, deps in self.dependency_graph.items():
            if plugin_name in deps:
                dependents.append(plugin)
        
        return dependents
    
    def resolve_dependencies(self, plugin_name: str) -> List[str]:
        """Resolve the dependency chain for a plugin"""
        if plugin_name not in self.dependency_graph:
            return []
        
        resolved = []
        visited = set()
        
        def _resolve(name: str):
            if name in visited:
                return  # Avoid circular dependencies
            
            visited.add(name)
            
            if name in self.dependency_graph:
                for dep in self.dependency_graph[name]:
                    _resolve(dep)
                    if dep not in resolved:
                        resolved.append(dep)
        
        _resolve(plugin_name)
        return resolved
    
    def check_circular_dependencies(self) -> List[List[str]]:
        """Check for circular dependencies in the registry"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def _has_cycle(plugin: str, path: List[str]) -> bool:
            if plugin in rec_stack:
                # Found a cycle
                cycle_start = path.index(plugin)
                cycles.append(path[cycle_start:] + [plugin])
                return True
            
            if plugin in visited:
                return False
            
            visited.add(plugin)
            rec_stack.add(plugin)
            
            if plugin in self.dependency_graph:
                for dep in self.dependency_graph[plugin]:
                    if _has_cycle(dep, path + [plugin]):
                        return True
            
            rec_stack.remove(plugin)
            return False
        
        for plugin in self.dependency_graph:
            if plugin not in visited:
                _has_cycle(plugin, [])
        
        return cycles
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin in the registry"""
        if plugin_name not in self.entries:
            return False
        
        self.entries[plugin_name].enabled = True
        self._save_registry()
        
        logger.info(f"✅ Plugin enabled in registry: {plugin_name}")
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin in the registry"""
        if plugin_name not in self.entries:
            return False
        
        self.entries[plugin_name].enabled = False
        self._save_registry()
        
        logger.info(f"⏸️ Plugin disabled in registry: {plugin_name}")
        return True
    
    def update_plugin_metadata(self, plugin_name: str, metadata: Dict[str, Any]) -> bool:
        """Update plugin metadata"""
        if plugin_name not in self.entries:
            return False
        
        entry = self.entries[plugin_name]
        
        # Update allowed fields
        if 'description' in metadata:
            entry.description = metadata['description']
        
        if 'capabilities' in metadata:
            # Update capability index
            for old_cap in entry.capabilities:
                if old_cap in self.capability_index:
                    self.capability_index[old_cap].discard(plugin_name)
            
            entry.capabilities = metadata['capabilities']
            
            for new_cap in entry.capabilities:
                if new_cap not in self.capability_index:
                    self.capability_index[new_cap] = set()
                self.capability_index[new_cap].add(plugin_name)
        
        if 'dependencies' in metadata:
            entry.dependencies = metadata['dependencies']
            self.dependency_graph[plugin_name] = set(entry.dependencies)
        
        if 'config_schema' in metadata:
            entry.config_schema = metadata['config_schema']
        
        # Update last modified
        entry.last_modified = datetime.now()
        
        self._save_registry()
        
        logger.info(f"📝 Plugin metadata updated: {plugin_name}")
        return True
    
    def get_capability_stats(self) -> Dict[str, int]:
        """Get statistics about capabilities"""
        return {cap: len(plugins) for cap, plugins in self.capability_index.items()}
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        total_plugins = len(self.entries)
        enabled_plugins = sum(1 for entry in self.entries.values() if entry.enabled)
        
        authors = set(entry.author for entry in self.entries.values())
        capabilities = set()
        for entry in self.entries.values():
            capabilities.update(entry.capabilities)
        
        return {
            "total_plugins": total_plugins,
            "enabled_plugins": enabled_plugins,
            "disabled_plugins": total_plugins - enabled_plugins,
            "unique_authors": len(authors),
            "unique_capabilities": len(capabilities),
            "capability_stats": self.get_capability_stats(),
            "circular_dependencies": len(self.check_circular_dependencies()),
            "registry_file": str(self.registry_file),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_registry(self, export_path: Optional[Path] = None) -> bool:
        """Export registry to a file"""
        if export_path is None:
            export_path = self.registry_file.with_suffix('.export.json')
        
        try:
            export_data = {
                "metadata": {
                    "export_time": datetime.now().isoformat(),
                    "total_plugins": len(self.entries),
                    "registry_version": "1.0.0"
                },
                "plugins": [entry.to_dict() for entry in self.entries.values()],
                "capability_index": {cap: list(plugins) for cap, plugins in self.capability_index.items()},
                "dependency_graph": {plugin: list(deps) for plugin, deps in self.dependency_graph.items()}
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"📤 Registry exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export registry: {e}")
            return False
    
    def import_registry(self, import_path: Path, merge: bool = False) -> bool:
        """Import registry from a file"""
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            if not merge:
                # Clear existing registry
                self.entries.clear()
                self.capability_index.clear()
                self.dependency_graph.clear()
            
            # Import plugins
            for plugin_data in import_data.get("plugins", []):
                entry = RegistryEntry.from_dict(plugin_data)
                self.register_plugin(entry)
            
            logger.info(f"📥 Registry imported from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to import registry: {e}")
            return False
    
    def _load_registry(self):
        """Load registry from file"""
        if not self.registry_file.exists():
            logger.info("📋 No existing registry file found, starting fresh")
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
            
            # Load entries
            for plugin_name, entry_data in data.get("entries", {}).items():
                entry = RegistryEntry.from_dict(entry_data)
                self.entries[plugin_name] = entry
            
            # Rebuild indexes
            self._rebuild_indexes()
            
            logger.info(f"📋 Registry loaded: {len(self.entries)} plugins")
            
        except Exception as e:
            logger.error(f"❌ Failed to load registry: {e}")
    
    def _save_registry(self):
        """Save registry to file"""
        try:
            # Ensure directory exists
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "metadata": {
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "total_plugins": len(self.entries)
                },
                "entries": {name: entry.to_dict() for name, entry in self.entries.items()}
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"💾 Registry saved to {self.registry_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save registry: {e}")
    
    def _rebuild_indexes(self):
        """Rebuild capability and dependency indexes"""
        self.capability_index.clear()
        self.dependency_graph.clear()
        
        for plugin_name, entry in self.entries.items():
            # Rebuild capability index
            for capability in entry.capabilities:
                if capability not in self.capability_index:
                    self.capability_index[capability] = set()
                self.capability_index[capability].add(plugin_name)
            
            # Rebuild dependency graph
            self.dependency_graph[plugin_name] = set(entry.dependencies)
        
        logger.debug("🔄 Registry indexes rebuilt")
