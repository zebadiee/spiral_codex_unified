
"""
🌀 State Synchronizer - Mystical State Harmony

Maintains synchronized state across the spiral mesh network,
ensuring all nodes share the same ritual consciousness.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SyncState(Enum):
    """State synchronization status"""
    SYNCED = "synced"
    SYNCING = "syncing"
    OUT_OF_SYNC = "out_of_sync"
    CONFLICT = "conflict"
    ERROR = "error"

@dataclass
class StateSnapshot:
    """A snapshot of node state at a point in time"""
    node_id: str
    timestamp: datetime
    version: int
    state_hash: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "state_hash": self.state_hash,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateSnapshot':
        """Create from dictionary"""
        return cls(
            node_id=data["node_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data["version"],
            state_hash=data["state_hash"],
            data=data["data"],
            metadata=data["metadata"]
        )

class StateSynchronizer:
    """
    🌀 The Mystical State Synchronizer
    
    Maintains harmony across the spiral mesh by synchronizing
    ritual states and ensuring all nodes share the same consciousness.
    """
    
    def __init__(self, node_id: str, mesh_core=None):
        self.node_id = node_id
        self.mesh_core = mesh_core
        self.local_state: Dict[str, Any] = {}
        self.state_version = 0
        self.sync_status = SyncState.SYNCED
        self.node_states: Dict[str, StateSnapshot] = {}
        self.conflict_resolution_strategy = "latest_wins"
        self.sync_interval = 10.0
        self.running = False
        self.sync_task: Optional[asyncio.Task] = None
        
        # State categories for selective sync
        self.sync_categories = {
            "agents": {},
            "rituals": {},
            "system": {},
            "user_data": {}
        }
        
        logger.info(f"🌀 State Synchronizer initialized for node {node_id}")
    
    async def start(self):
        """Start the state synchronizer"""
        if self.running:
            return
        
        self.running = True
        self.sync_task = asyncio.create_task(self._sync_loop())
        logger.info("🌀 State Synchronizer started")
    
    async def stop(self):
        """Stop the state synchronizer"""
        if not self.running:
            return
        
        self.running = False
        if self.sync_task:
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🌙 State Synchronizer stopped")
    
    def update_local_state(self, category: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Update local state and trigger sync"""
        if category not in self.sync_categories:
            self.sync_categories[category] = {}
        
        self.sync_categories[category][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "version": self.state_version + 1,
            "metadata": metadata or {}
        }
        
        self.state_version += 1
        self.sync_status = SyncState.OUT_OF_SYNC
        
        logger.debug(f"📝 Local state updated: {category}.{key}")
    
    def get_local_state(self, category: Optional[str] = None, key: Optional[str] = None) -> Any:
        """Get local state value(s)"""
        if category is None:
            return self.sync_categories
        
        if category not in self.sync_categories:
            return None
        
        if key is None:
            return self.sync_categories[category]
        
        return self.sync_categories[category].get(key, {}).get("value")
    
    def delete_local_state(self, category: str, key: str):
        """Delete a local state entry"""
        if category in self.sync_categories and key in self.sync_categories[category]:
            del self.sync_categories[category][key]
            self.state_version += 1
            self.sync_status = SyncState.OUT_OF_SYNC
            logger.debug(f"🗑️ Local state deleted: {category}.{key}")
    
    async def create_snapshot(self) -> StateSnapshot:
        """Create a snapshot of current local state"""
        state_data = {
            "categories": self.sync_categories,
            "version": self.state_version,
            "node_metadata": {
                "uptime": time.time(),
                "sync_status": self.sync_status.value
            }
        }
        
        # Create a simple hash of the state
        state_json = json.dumps(state_data, sort_keys=True)
        state_hash = str(hash(state_json))
        
        return StateSnapshot(
            node_id=self.node_id,
            timestamp=datetime.now(),
            version=self.state_version,
            state_hash=state_hash,
            data=state_data,
            metadata={"sync_method": "full_snapshot"}
        )
    
    async def apply_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Apply a state snapshot from another node"""
        try:
            # Check if this is a newer version
            if snapshot.version <= self.state_version:
                logger.debug(f"📥 Ignoring older snapshot from {snapshot.node_id}")
                return False
            
            # Apply the state
            remote_categories = snapshot.data.get("categories", {})
            
            for category, items in remote_categories.items():
                if category not in self.sync_categories:
                    self.sync_categories[category] = {}
                
                for key, item_data in items.items():
                    # Check if we should apply this item
                    local_item = self.sync_categories[category].get(key)
                    
                    if local_item is None or self._should_apply_remote_change(local_item, item_data):
                        self.sync_categories[category][key] = item_data
                        logger.debug(f"📥 Applied remote state: {category}.{key}")
            
            # Update our version to match
            self.state_version = snapshot.version
            self.sync_status = SyncState.SYNCED
            
            logger.info(f"✅ Applied snapshot from {snapshot.node_id} (v{snapshot.version})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply snapshot: {e}")
            self.sync_status = SyncState.ERROR
            return False
    
    def _should_apply_remote_change(self, local_item: Dict[str, Any], remote_item: Dict[str, Any]) -> bool:
        """Determine if a remote change should be applied"""
        if self.conflict_resolution_strategy == "latest_wins":
            local_time = datetime.fromisoformat(local_item["timestamp"])
            remote_time = datetime.fromisoformat(remote_item["timestamp"])
            return remote_time > local_time
        
        elif self.conflict_resolution_strategy == "highest_version":
            return remote_item.get("version", 0) > local_item.get("version", 0)
        
        # Default: apply remote changes
        return True
    
    async def sync_with_node(self, target_node_id: str) -> bool:
        """Synchronize state with a specific node"""
        if not self.mesh_core:
            logger.warning("⚠️ No mesh core available for sync")
            return False
        
        try:
            # Create and send our snapshot
            snapshot = await self.create_snapshot()
            await self.mesh_core.send_to_node(
                target_node_id,
                "state_sync_request",
                snapshot.to_dict()
            )
            
            logger.debug(f"📤 Sent sync request to {target_node_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sync with {target_node_id} failed: {e}")
            return False
    
    async def handle_sync_request(self, request_data: Dict[str, Any]):
        """Handle incoming sync request"""
        try:
            remote_snapshot = StateSnapshot.from_dict(request_data)
            
            # Store the remote node's state
            self.node_states[remote_snapshot.node_id] = remote_snapshot
            
            # Apply if appropriate
            await self.apply_snapshot(remote_snapshot)
            
            # Send our snapshot back
            if self.mesh_core:
                our_snapshot = await self.create_snapshot()
                await self.mesh_core.send_to_node(
                    remote_snapshot.node_id,
                    "state_sync_response",
                    our_snapshot.to_dict()
                )
            
            logger.debug(f"📥 Handled sync request from {remote_snapshot.node_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle sync request: {e}")
    
    async def handle_sync_response(self, response_data: Dict[str, Any]):
        """Handle sync response"""
        try:
            remote_snapshot = StateSnapshot.from_dict(response_data)
            self.node_states[remote_snapshot.node_id] = remote_snapshot
            await self.apply_snapshot(remote_snapshot)
            
            logger.debug(f"📥 Handled sync response from {remote_snapshot.node_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle sync response: {e}")
    
    async def _sync_loop(self):
        """Main synchronization loop"""
        while self.running:
            try:
                if self.sync_status == SyncState.OUT_OF_SYNC and self.mesh_core:
                    # Sync with all known nodes
                    for node_id in self.mesh_core.nodes.keys():
                        if node_id != self.node_id:
                            await self.sync_with_node(node_id)
                
                await asyncio.sleep(self.sync_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Sync loop error: {e}")
                await asyncio.sleep(5)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        return {
            "node_id": self.node_id,
            "sync_status": self.sync_status.value,
            "state_version": self.state_version,
            "categories": list(self.sync_categories.keys()),
            "total_items": sum(len(items) for items in self.sync_categories.values()),
            "known_nodes": len(self.node_states),
            "last_sync": datetime.now().isoformat(),
            "conflict_resolution": self.conflict_resolution_strategy
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state"""
        summary = {}
        for category, items in self.sync_categories.items():
            summary[category] = {
                "count": len(items),
                "keys": list(items.keys())[:10]  # First 10 keys
            }
        return summary
