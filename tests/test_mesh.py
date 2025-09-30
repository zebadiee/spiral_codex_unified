
"""
🌀 Tests for Spiral Codex Mesh Network

Test suite for the multi-agent ritual mesh system,
ensuring the mystical network operates with perfect harmony.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from spiralcodex.mesh import (
    MeshCore, MeshNode, MeshConfig, NodeStatus,
    EventBus, RitualEvent, EventType,
    StateSynchronizer, SyncState,
    MeshRegistry
)

class TestMeshCore:
    """Test the core mesh networking functionality"""
    
    @pytest.fixture
    def mesh_config(self):
        """Create a test mesh configuration"""
        return MeshConfig(
            node_id="test_node_123",
            mesh_name="test_mesh",
            websocket_port=8766,
            redis_url="redis://localhost:6379",
            enable_redis=False,  # Disable for testing
            enable_websocket=False,  # Disable for testing
            heartbeat_interval=1.0,
            sync_interval=0.5
        )
    
    @pytest.fixture
    def mesh_core(self, mesh_config):
        """Create a test mesh core instance"""
        return MeshCore(mesh_config)
    
    def test_mesh_core_initialization(self, mesh_core):
        """Test mesh core initializes correctly"""
        assert mesh_core.node_id == "test_node_123"
        assert mesh_core.config.mesh_name == "test_mesh"
        assert mesh_core.local_node.node_id == "test_node_123"
        assert mesh_core.local_node.status == NodeStatus.INITIALIZING
        assert not mesh_core.running
    
    @pytest.mark.asyncio
    async def test_mesh_start_stop(self, mesh_core):
        """Test mesh network start and stop"""
        # Start the mesh
        await mesh_core.start()
        assert mesh_core.running
        assert mesh_core.local_node.status == NodeStatus.ACTIVE
        assert mesh_core.node_id in mesh_core.nodes
        
        # Stop the mesh
        await mesh_core.stop()
        assert not mesh_core.running
        assert mesh_core.local_node.status == NodeStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_node_registration(self, mesh_core):
        """Test node registration and unregistration"""
        await mesh_core.start()
        
        # Create a test node
        test_node = MeshNode(
            node_id="test_remote_node",
            name="Remote Test Node",
            status=NodeStatus.ACTIVE,
            capabilities=["test_capability"],
            recursion_depth=1,
            entropy_level=0.5,
            last_heartbeat=datetime.now(),
            metadata={"test": True}
        )
        
        # Register the node
        await mesh_core.register_node(test_node)
        assert "test_remote_node" in mesh_core.nodes
        assert mesh_core.nodes["test_remote_node"] == test_node
        
        # Unregister the node
        await mesh_core.unregister_node("test_remote_node")
        assert "test_remote_node" not in mesh_core.nodes
        
        await mesh_core.stop()
    
    def test_mesh_status(self, mesh_core):
        """Test mesh status reporting"""
        status = mesh_core.get_mesh_status()
        
        assert "node_id" in status
        assert "status" in status
        assert "connected_nodes" in status
        assert "mesh_name" in status
        assert status["mesh_name"] == "test_mesh"

class TestEventBus:
    """Test the event bus system"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a test event bus"""
        return EventBus("test_node")
    
    @pytest.mark.asyncio
    async def test_event_bus_start_stop(self, event_bus):
        """Test event bus lifecycle"""
        await event_bus.start()
        assert event_bus.running
        
        await event_bus.stop()
        assert not event_bus.running
    
    @pytest.mark.asyncio
    async def test_event_publishing(self, event_bus):
        """Test event publishing and handling"""
        await event_bus.start()
        
        # Subscribe to events
        received_events = []
        
        def event_handler(event):
            received_events.append(event)
        
        event_bus.subscribe(EventType.AGENT_MESSAGE, event_handler)
        
        # Publish an event
        event_id = await event_bus.publish(
            EventType.AGENT_MESSAGE,
            {"message": "test message", "agent_id": "test_agent"}
        )
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        assert len(received_events) == 1
        assert received_events[0].event_id == event_id
        assert received_events[0].data["message"] == "test message"
        
        await event_bus.stop()
    
    @pytest.mark.asyncio
    async def test_event_ttl(self, event_bus):
        """Test event time-to-live functionality"""
        await event_bus.start()
        
        # Publish event with short TTL
        await event_bus.publish(
            EventType.SYSTEM_ALERT,
            {"alert": "test"},
            ttl=0  # Immediate expiry
        )
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Event should be expired and not processed
        stats = event_bus.get_event_stats()
        assert stats["total_events"] == 0  # Should be 0 due to expiry
        
        await event_bus.stop()
    
    def test_event_serialization(self):
        """Test event serialization and deserialization"""
        event = RitualEvent(
            event_id="test_123",
            event_type=EventType.RITUAL_START,
            source_node="node_1",
            target_node="node_2",
            timestamp=datetime.now(),
            data={"ritual": "test"},
            metadata={"priority": "high"},
            priority=8
        )
        
        # Serialize
        event_dict = event.to_dict()
        assert event_dict["event_id"] == "test_123"
        assert event_dict["event_type"] == "ritual_start"
        
        # Deserialize
        restored_event = RitualEvent.from_dict(event_dict)
        assert restored_event.event_id == event.event_id
        assert restored_event.event_type == event.event_type
        assert restored_event.data == event.data

class TestStateSynchronizer:
    """Test the state synchronization system"""
    
    @pytest.fixture
    def state_sync(self):
        """Create a test state synchronizer"""
        return StateSynchronizer("test_node")
    
    @pytest.mark.asyncio
    async def test_state_sync_lifecycle(self, state_sync):
        """Test state synchronizer start/stop"""
        await state_sync.start()
        assert state_sync.running
        
        await state_sync.stop()
        assert not state_sync.running
    
    def test_local_state_management(self, state_sync):
        """Test local state updates"""
        # Update state
        state_sync.update_local_state("agents", "agent_1", {"status": "active"})
        
        # Retrieve state
        agent_state = state_sync.get_local_state("agents", "agent_1")
        assert agent_state["status"] == "active"
        
        # Delete state
        state_sync.delete_local_state("agents", "agent_1")
        deleted_state = state_sync.get_local_state("agents", "agent_1")
        assert deleted_state is None
    
    @pytest.mark.asyncio
    async def test_state_snapshot(self, state_sync):
        """Test state snapshot creation"""
        # Add some state
        state_sync.update_local_state("agents", "agent_1", {"status": "active"})
        state_sync.update_local_state("rituals", "ritual_1", {"phase": "beginning"})
        
        # Create snapshot
        snapshot = await state_sync.create_snapshot()
        
        assert snapshot.node_id == "test_node"
        assert snapshot.version == state_sync.state_version
        assert "categories" in snapshot.data
        assert "agents" in snapshot.data["categories"]
        assert "rituals" in snapshot.data["categories"]
    
    def test_sync_status(self, state_sync):
        """Test synchronization status reporting"""
        status = state_sync.get_sync_status()
        
        assert "node_id" in status
        assert "sync_status" in status
        assert "state_version" in status
        assert status["node_id"] == "test_node"

class TestMeshRegistry:
    """Test the mesh registry system"""
    
    @pytest.fixture
    def registry(self):
        """Create a test mesh registry"""
        return MeshRegistry("test_node")
    
    @pytest.fixture
    def test_node(self):
        """Create a test node"""
        return MeshNode(
            node_id="remote_node_123",
            name="Remote Test Node",
            status=NodeStatus.ACTIVE,
            capabilities=["ritual_processing", "agent_hosting"],
            recursion_depth=2,
            entropy_level=0.3,
            last_heartbeat=datetime.now(),
            metadata={"version": "1.0.0"}
        )
    
    def test_node_registration(self, registry, test_node):
        """Test node registration in registry"""
        # Register node
        success = registry.register_node(test_node)
        assert success
        assert test_node.node_id in registry.nodes
        
        # Retrieve node
        retrieved_node = registry.get_node(test_node.node_id)
        assert retrieved_node == test_node
        
        # Unregister node
        success = registry.unregister_node(test_node.node_id)
        assert success
        assert test_node.node_id not in registry.nodes
    
    def test_capability_search(self, registry, test_node):
        """Test finding nodes by capability"""
        registry.register_node(test_node)
        
        # Find nodes with specific capability
        ritual_nodes = registry.get_nodes_by_capability("ritual_processing")
        assert len(ritual_nodes) == 1
        assert ritual_nodes[0] == test_node
        
        # Find nodes with non-existent capability
        missing_nodes = registry.get_nodes_by_capability("non_existent")
        assert len(missing_nodes) == 0
    
    def test_status_filtering(self, registry, test_node):
        """Test filtering nodes by status"""
        registry.register_node(test_node)
        
        # Find active nodes
        active_nodes = registry.get_nodes_by_status(NodeStatus.ACTIVE)
        assert len(active_nodes) == 1
        assert active_nodes[0] == test_node
        
        # Find dormant nodes (should be empty)
        dormant_nodes = registry.get_nodes_by_status(NodeStatus.DORMANT)
        assert len(dormant_nodes) == 0
    
    def test_heartbeat_updates(self, registry, test_node):
        """Test heartbeat updates"""
        registry.register_node(test_node)
        
        # Update heartbeat
        heartbeat_data = {
            "status": "ritual_mode",
            "recursion_depth": 5,
            "entropy_level": 0.8
        }
        
        success = registry.update_node_heartbeat(test_node.node_id, heartbeat_data)
        assert success
        
        # Check updates
        updated_node = registry.get_node(test_node.node_id)
        assert updated_node.status == NodeStatus.RITUAL_MODE
        assert updated_node.recursion_depth == 5
        assert updated_node.entropy_level == 0.8
    
    def test_stale_node_cleanup(self, registry):
        """Test cleanup of stale nodes"""
        # Create a stale node (old heartbeat)
        stale_node = MeshNode(
            node_id="stale_node",
            name="Stale Node",
            status=NodeStatus.ACTIVE,
            capabilities=["test"],
            recursion_depth=0,
            entropy_level=0.0,
            last_heartbeat=datetime.now() - timedelta(minutes=5),  # 5 minutes ago
            metadata={}
        )
        
        registry.register_node(stale_node)
        assert "stale_node" in registry.nodes
        
        # Cleanup stale nodes
        stale_nodes = registry.cleanup_stale_nodes()
        assert "stale_node" in stale_nodes
        assert "stale_node" not in registry.nodes
    
    def test_network_health(self, registry, test_node):
        """Test network health calculation"""
        # Empty network
        health = registry._calculate_network_health()
        assert health == 0.0
        
        # Add active node
        registry.register_node(test_node)
        health = registry._calculate_network_health()
        assert health > 0.0
        
        # Network health should be reasonable
        assert 0.0 <= health <= 100.0
    
    def test_topology_reporting(self, registry, test_node):
        """Test mesh topology reporting"""
        registry.register_node(test_node)
        
        topology = registry.get_mesh_topology()
        
        assert "total_nodes" in topology
        assert "active_nodes" in topology
        assert "node_statuses" in topology
        assert "capabilities" in topology
        assert "network_health" in topology
        
        assert topology["total_nodes"] == 1
        assert "active" in topology["node_statuses"]
        assert "ritual_processing" in topology["capabilities"]

# Integration tests
class TestMeshIntegration:
    """Integration tests for the complete mesh system"""
    
    @pytest.mark.asyncio
    async def test_mesh_with_event_bus(self):
        """Test mesh core with integrated event bus"""
        config = MeshConfig(
            enable_redis=False,
            enable_websocket=False,
            heartbeat_interval=0.1,
            sync_interval=0.1
        )
        
        mesh = MeshCore(config)
        await mesh.start()
        
        # Test event handling
        received_events = []
        
        def event_handler(event_data):
            received_events.append(event_data)
        
        mesh.register_event_handler("test_event", event_handler)
        
        # Simulate event
        await mesh.broadcast_event("test_event", {"test": "data"})
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        await mesh.stop()
    
    @pytest.mark.asyncio
    async def test_multi_node_mesh(self):
        """Test multiple mesh nodes working together"""
        # Create two mesh nodes
        config1 = MeshConfig(
            node_id="node_1",
            enable_redis=False,
            enable_websocket=False
        )
        config2 = MeshConfig(
            node_id="node_2", 
            enable_redis=False,
            enable_websocket=False
        )
        
        mesh1 = MeshCore(config1)
        mesh2 = MeshCore(config2)
        
        await mesh1.start()
        await mesh2.start()
        
        # Register nodes with each other
        await mesh1.register_node(mesh2.local_node)
        await mesh2.register_node(mesh1.local_node)
        
        # Verify registration
        assert mesh2.node_id in mesh1.nodes
        assert mesh1.node_id in mesh2.nodes
        
        await mesh1.stop()
        await mesh2.stop()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
