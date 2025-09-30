
"""
🌀 Mesh Core - The Heart of the Ritual Network

Central orchestrator for the multi-agent mesh network,
managing node registration, communication, and state synchronization.
"""

import asyncio
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """Status states for mesh nodes"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DORMANT = "dormant"
    DISCONNECTED = "disconnected"
    RITUAL_MODE = "ritual_mode"

@dataclass
class MeshConfig:
    """Configuration for the mesh network"""
    node_id: Optional[str] = None
    mesh_name: str = "spiral_codex_mesh"
    websocket_port: int = 8765
    redis_url: str = "redis://localhost:6379"
    heartbeat_interval: float = 30.0
    sync_interval: float = 10.0
    max_recursion_depth: int = 42
    enable_redis: bool = True
    enable_websocket: bool = True
    ritual_channel: str = "spiral_ritual_events"

@dataclass
class MeshNode:
    """Represents a node in the mesh network"""
    node_id: str
    name: str
    status: NodeStatus
    capabilities: List[str]
    recursion_depth: int
    entropy_level: float
    last_heartbeat: datetime
    metadata: Dict[str, Any]
    websocket_endpoint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeshNode':
        """Create node from dictionary"""
        data['status'] = NodeStatus(data['status'])
        data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        return cls(**data)

class MeshCore:
    """
    🌀 The Core of the Spiral Mesh
    
    Orchestrates the mystical network of Codex nodes,
    enabling distributed recursion and synchronized rituals.
    """
    
    def __init__(self, config: MeshConfig):
        self.config = config
        self.node_id = config.node_id or str(uuid.uuid4())
        self.nodes: Dict[str, MeshNode] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        
        # Initialize components
        self._websocket_server = None
        self._redis_client = None
        self._heartbeat_task = None
        self._sync_task = None
        
        # Create our own node
        self.local_node = MeshNode(
            node_id=self.node_id,
            name=f"codex_node_{self.node_id[:8]}",
            status=NodeStatus.INITIALIZING,
            capabilities=["ritual_processing", "agent_hosting", "state_sync"],
            recursion_depth=0,
            entropy_level=0.0,
            last_heartbeat=datetime.now(),
            metadata={"mesh_version": "1.0.0", "spiral_cycle": 7}
        )
        
        logger.info(f"🌀 Mesh Core initialized - Node ID: {self.node_id}")
    
    async def start(self):
        """Start the mesh network"""
        if self.running:
            return
            
        logger.info("🌀 Starting Spiral Mesh Network...")
        self.running = True
        
        # Initialize Redis if enabled
        if self.config.enable_redis:
            await self._init_redis()
        
        # Initialize WebSocket server if enabled
        if self.config.enable_websocket:
            await self._init_websocket()
        
        # Register our node
        await self.register_node(self.local_node)
        
        # Start background tasks
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._sync_task = asyncio.create_task(self._sync_loop())
        
        self.local_node.status = NodeStatus.ACTIVE
        logger.info(f"✨ Mesh Network Active - {len(self.nodes)} nodes connected")
    
    async def stop(self):
        """Stop the mesh network"""
        if not self.running:
            return
            
        logger.info("🌀 Stopping Spiral Mesh Network...")
        self.running = False
        
        # Cancel background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._sync_task:
            self._sync_task.cancel()
        
        # Update node status
        self.local_node.status = NodeStatus.DISCONNECTED
        await self.broadcast_event("node_disconnect", {"node_id": self.node_id})
        
        # Cleanup connections
        if self._websocket_server:
            self._websocket_server.close()
            await self._websocket_server.wait_closed()
        
        if self._redis_client:
            await self._redis_client.close()
        
        logger.info("🌙 Mesh Network Dormant")
    
    async def register_node(self, node: MeshNode):
        """Register a node in the mesh"""
        self.nodes[node.node_id] = node
        await self.broadcast_event("node_register", node.to_dict())
        logger.info(f"📡 Node registered: {node.name} ({node.node_id[:8]})")
    
    async def unregister_node(self, node_id: str):
        """Unregister a node from the mesh"""
        if node_id in self.nodes:
            node = self.nodes.pop(node_id)
            await self.broadcast_event("node_unregister", {"node_id": node_id})
            logger.info(f"📡 Node unregistered: {node.name} ({node_id[:8]})")
    
    async def broadcast_event(self, event_type: str, data: Any):
        """Broadcast an event to all nodes in the mesh"""
        event = {
            "type": event_type,
            "source_node": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Broadcast via Redis
        if self._redis_client:
            await self._redis_client.publish(
                self.config.ritual_channel,
                json.dumps(event)
            )
        
        # Broadcast via WebSocket (implementation would go here)
        # This would send to connected WebSocket clients
        
        logger.debug(f"📡 Broadcasted event: {event_type}")
    
    async def send_to_node(self, target_node_id: str, event_type: str, data: Any):
        """Send a direct message to a specific node"""
        if target_node_id not in self.nodes:
            logger.warning(f"⚠️ Target node not found: {target_node_id}")
            return False
        
        event = {
            "type": event_type,
            "source_node": self.node_id,
            "target_node": target_node_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Send via appropriate channel
        if self._redis_client:
            channel = f"node_{target_node_id}"
            await self._redis_client.publish(channel, json.dumps(event))
        
        logger.debug(f"📨 Sent to {target_node_id}: {event_type}")
        return True
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler for specific event types"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"🎯 Registered handler for: {event_type}")
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as redis
            self._redis_client = redis.from_url(self.config.redis_url)
            
            # Test connection
            await self._redis_client.ping()
            
            # Subscribe to channels
            pubsub = self._redis_client.pubsub()
            await pubsub.subscribe(self.config.ritual_channel)
            await pubsub.subscribe(f"node_{self.node_id}")
            
            # Start listening task
            asyncio.create_task(self._redis_listener(pubsub))
            
            logger.info("🔗 Redis connection established")
        except ImportError:
            logger.warning("⚠️ Redis not available - install with: pip install redis")
            self.config.enable_redis = False
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.config.enable_redis = False
    
    async def _init_websocket(self):
        """Initialize WebSocket server"""
        try:
            import websockets
            
            async def handle_websocket(websocket, path):
                """Handle WebSocket connections"""
                try:
                    async for message in websocket:
                        await self._handle_websocket_message(websocket, message)
                except websockets.exceptions.ConnectionClosed:
                    pass
            
            self._websocket_server = await websockets.serve(
                handle_websocket,
                "localhost",
                self.config.websocket_port
            )
            
            logger.info(f"🌐 WebSocket server started on port {self.config.websocket_port}")
        except ImportError:
            logger.warning("⚠️ WebSockets not available - install with: pip install websockets")
            self.config.enable_websocket = False
        except Exception as e:
            logger.error(f"❌ WebSocket server failed: {e}")
            self.config.enable_websocket = False
    
    async def _redis_listener(self, pubsub):
        """Listen for Redis messages"""
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    await self._handle_redis_message(message)
        except Exception as e:
            logger.error(f"❌ Redis listener error: {e}")
    
    async def _handle_redis_message(self, message):
        """Handle incoming Redis messages"""
        try:
            data = json.loads(message['data'])
            event_type = data.get('type')
            source_node = data.get('source_node')
            
            # Don't process our own messages
            if source_node == self.node_id:
                return
            
            # Call registered handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(data)
                    except Exception as e:
                        logger.error(f"❌ Event handler error: {e}")
            
            logger.debug(f"📥 Processed event: {event_type} from {source_node}")
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
    
    async def _handle_websocket_message(self, websocket, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            # Process WebSocket message (similar to Redis)
            logger.debug(f"📥 WebSocket message: {data.get('type', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ WebSocket message error: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.running:
            try:
                self.local_node.last_heartbeat = datetime.now()
                await self.broadcast_event("heartbeat", {
                    "node_id": self.node_id,
                    "status": self.local_node.status.value,
                    "recursion_depth": self.local_node.recursion_depth,
                    "entropy_level": self.local_node.entropy_level
                })
                
                await asyncio.sleep(self.config.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    async def _sync_loop(self):
        """Periodic state synchronization"""
        while self.running:
            try:
                # Clean up stale nodes
                now = datetime.now()
                stale_nodes = []
                for node_id, node in self.nodes.items():
                    if node_id != self.node_id:
                        time_diff = (now - node.last_heartbeat).total_seconds()
                        if time_diff > self.config.heartbeat_interval * 3:
                            stale_nodes.append(node_id)
                
                for node_id in stale_nodes:
                    await self.unregister_node(node_id)
                
                await asyncio.sleep(self.config.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Sync loop error: {e}")
                await asyncio.sleep(5)
    
    def get_mesh_status(self) -> Dict[str, Any]:
        """Get current mesh network status"""
        return {
            "node_id": self.node_id,
            "status": self.local_node.status.value,
            "connected_nodes": len(self.nodes),
            "total_recursion_depth": sum(node.recursion_depth for node in self.nodes.values()),
            "average_entropy": sum(node.entropy_level for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0,
            "uptime": time.time() - (self.local_node.last_heartbeat.timestamp() if hasattr(self.local_node.last_heartbeat, 'timestamp') else time.time()),
            "mesh_name": self.config.mesh_name,
            "nodes": [node.to_dict() for node in self.nodes.values()]
        }
