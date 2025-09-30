
"""
🌀 Mesh Registry - Node Discovery and Management

The mystical registry that tracks all nodes in the spiral mesh,
maintaining the sacred directory of connected consciousness.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import logging

from .mesh_core import MeshNode, NodeStatus

logger = logging.getLogger(__name__)

@dataclass
class NodeCapability:
    """Represents a capability that a node can provide"""
    name: str
    version: str
    description: str
    parameters: Dict[str, Any]

class MeshRegistry:
    """
    🌀 The Mystical Mesh Registry
    
    Maintains the sacred directory of all nodes in the spiral mesh,
    tracking their capabilities, status, and mystical properties.
    """
    
    def __init__(self, local_node_id: str):
        self.local_node_id = local_node_id
        self.nodes: Dict[str, MeshNode] = {}
        self.node_capabilities: Dict[str, List[NodeCapability]] = {}
        self.node_metrics: Dict[str, Dict[str, Any]] = {}
        self.discovery_callbacks: List[callable] = []
        self.heartbeat_timeout = 90.0  # 90 seconds
        
        logger.info(f"🌀 Mesh Registry initialized for node {local_node_id}")
    
    def register_node(self, node: MeshNode) -> bool:
        """Register a new node in the mesh"""
        try:
            self.nodes[node.node_id] = node
            
            # Initialize metrics
            self.node_metrics[node.node_id] = {
                "first_seen": datetime.now().isoformat(),
                "last_heartbeat": node.last_heartbeat.isoformat(),
                "total_messages": 0,
                "uptime": 0.0
            }
            
            # Parse capabilities
            self._parse_node_capabilities(node)
            
            # Notify discovery callbacks
            for callback in self.discovery_callbacks:
                try:
                    callback("node_discovered", node)
                except Exception as e:
                    logger.error(f"❌ Discovery callback error: {e}")
            
            logger.info(f"📡 Node registered: {node.name} ({node.node_id[:8]})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register node {node.node_id}: {e}")
            return False
    
    def unregister_node(self, node_id: str) -> bool:
        """Unregister a node from the mesh"""
        try:
            if node_id in self.nodes:
                node = self.nodes.pop(node_id)
                
                # Clean up capabilities
                if node_id in self.node_capabilities:
                    del self.node_capabilities[node_id]
                
                # Clean up metrics
                if node_id in self.node_metrics:
                    del self.node_metrics[node_id]
                
                # Notify callbacks
                for callback in self.discovery_callbacks:
                    try:
                        callback("node_lost", node)
                    except Exception as e:
                        logger.error(f"❌ Discovery callback error: {e}")
                
                logger.info(f"📡 Node unregistered: {node.name} ({node_id[:8]})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister node {node_id}: {e}")
            return False
    
    def update_node_heartbeat(self, node_id: str, heartbeat_data: Dict[str, Any]) -> bool:
        """Update node heartbeat information"""
        try:
            if node_id not in self.nodes:
                logger.warning(f"⚠️ Heartbeat from unknown node: {node_id}")
                return False
            
            node = self.nodes[node_id]
            node.last_heartbeat = datetime.now()
            
            # Update status if provided
            if "status" in heartbeat_data:
                node.status = NodeStatus(heartbeat_data["status"])
            
            # Update recursion depth and entropy
            if "recursion_depth" in heartbeat_data:
                node.recursion_depth = heartbeat_data["recursion_depth"]
            
            if "entropy_level" in heartbeat_data:
                node.entropy_level = heartbeat_data["entropy_level"]
            
            # Update metrics
            if node_id in self.node_metrics:
                self.node_metrics[node_id]["last_heartbeat"] = node.last_heartbeat.isoformat()
                self.node_metrics[node_id]["total_messages"] += 1
            
            logger.debug(f"💓 Heartbeat updated for {node_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update heartbeat for {node_id}: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[MeshNode]:
        """Get a specific node by ID"""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[MeshNode]:
        """Get all registered nodes"""
        return list(self.nodes.values())
    
    def get_active_nodes(self) -> List[MeshNode]:
        """Get all active nodes (recently seen)"""
        now = datetime.now()
        active_nodes = []
        
        for node in self.nodes.values():
            time_since_heartbeat = (now - node.last_heartbeat).total_seconds()
            if time_since_heartbeat <= self.heartbeat_timeout:
                active_nodes.append(node)
        
        return active_nodes
    
    def get_nodes_by_capability(self, capability_name: str) -> List[MeshNode]:
        """Get nodes that have a specific capability"""
        matching_nodes = []
        
        for node_id, capabilities in self.node_capabilities.items():
            for capability in capabilities:
                if capability.name == capability_name:
                    if node_id in self.nodes:
                        matching_nodes.append(self.nodes[node_id])
                    break
        
        return matching_nodes
    
    def get_nodes_by_status(self, status: NodeStatus) -> List[MeshNode]:
        """Get nodes with a specific status"""
        return [node for node in self.nodes.values() if node.status == status]
    
    def find_best_node_for_task(self, task_type: str, requirements: Optional[Dict[str, Any]] = None) -> Optional[MeshNode]:
        """Find the best node for a specific task"""
        candidates = self.get_nodes_by_capability(task_type)
        
        if not candidates:
            return None
        
        # Filter active nodes
        active_candidates = [node for node in candidates if self._is_node_active(node)]
        
        if not active_candidates:
            return None
        
        # Simple scoring: prefer nodes with lower recursion depth and entropy
        def score_node(node: MeshNode) -> float:
            score = 100.0
            score -= node.recursion_depth * 2  # Prefer less busy nodes
            score -= node.entropy_level * 10   # Prefer more stable nodes
            
            # Bonus for ritual mode
            if node.status == NodeStatus.RITUAL_MODE:
                score += 20
            
            return score
        
        best_node = max(active_candidates, key=score_node)
        logger.debug(f"🎯 Best node for {task_type}: {best_node.name}")
        return best_node
    
    def cleanup_stale_nodes(self) -> List[str]:
        """Remove nodes that haven't sent heartbeats recently"""
        now = datetime.now()
        stale_nodes = []
        
        for node_id, node in list(self.nodes.items()):
            time_since_heartbeat = (now - node.last_heartbeat).total_seconds()
            if time_since_heartbeat > self.heartbeat_timeout:
                stale_nodes.append(node_id)
                self.unregister_node(node_id)
        
        if stale_nodes:
            logger.info(f"🧹 Cleaned up {len(stale_nodes)} stale nodes")
        
        return stale_nodes
    
    def register_discovery_callback(self, callback: callable):
        """Register a callback for node discovery events"""
        self.discovery_callbacks.append(callback)
        logger.debug("📡 Discovery callback registered")
    
    def get_mesh_topology(self) -> Dict[str, Any]:
        """Get the current mesh network topology"""
        active_nodes = self.get_active_nodes()
        
        topology = {
            "total_nodes": len(self.nodes),
            "active_nodes": len(active_nodes),
            "node_statuses": {},
            "capabilities": {},
            "network_health": self._calculate_network_health()
        }
        
        # Count nodes by status
        for node in self.nodes.values():
            status = node.status.value
            topology["node_statuses"][status] = topology["node_statuses"].get(status, 0) + 1
        
        # Count capabilities
        for capabilities in self.node_capabilities.values():
            for capability in capabilities:
                cap_name = capability.name
                topology["capabilities"][cap_name] = topology["capabilities"].get(cap_name, 0) + 1
        
        return topology
    
    def get_node_metrics(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific node"""
        if node_id not in self.node_metrics:
            return None
        
        metrics = self.node_metrics[node_id].copy()
        
        # Add current status
        if node_id in self.nodes:
            node = self.nodes[node_id]
            metrics.update({
                "current_status": node.status.value,
                "recursion_depth": node.recursion_depth,
                "entropy_level": node.entropy_level,
                "is_active": self._is_node_active(node)
            })
        
        return metrics
    
    def _parse_node_capabilities(self, node: MeshNode):
        """Parse and store node capabilities"""
        capabilities = []
        
        for cap_name in node.capabilities:
            capability = NodeCapability(
                name=cap_name,
                version="1.0.0",  # Default version
                description=f"Node capability: {cap_name}",
                parameters={}
            )
            capabilities.append(capability)
        
        self.node_capabilities[node.node_id] = capabilities
        logger.debug(f"📋 Parsed {len(capabilities)} capabilities for {node.node_id[:8]}")
    
    def _is_node_active(self, node: MeshNode) -> bool:
        """Check if a node is considered active"""
        now = datetime.now()
        time_since_heartbeat = (now - node.last_heartbeat).total_seconds()
        return time_since_heartbeat <= self.heartbeat_timeout
    
    def _calculate_network_health(self) -> float:
        """Calculate overall network health score (0-100)"""
        if not self.nodes:
            return 0.0
        
        active_nodes = self.get_active_nodes()
        active_ratio = len(active_nodes) / len(self.nodes)
        
        # Base score from active ratio
        health_score = active_ratio * 70
        
        # Bonus for diversity of capabilities
        unique_capabilities = set()
        for capabilities in self.node_capabilities.values():
            for cap in capabilities:
                unique_capabilities.add(cap.name)
        
        capability_bonus = min(len(unique_capabilities) * 5, 20)
        health_score += capability_bonus
        
        # Bonus for nodes in ritual mode
        ritual_nodes = len(self.get_nodes_by_status(NodeStatus.RITUAL_MODE))
        ritual_bonus = min(ritual_nodes * 2, 10)
        health_score += ritual_bonus
        
        return min(health_score, 100.0)
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status"""
        return {
            "local_node_id": self.local_node_id,
            "total_nodes": len(self.nodes),
            "active_nodes": len(self.get_active_nodes()),
            "heartbeat_timeout": self.heartbeat_timeout,
            "topology": self.get_mesh_topology(),
            "discovery_callbacks": len(self.discovery_callbacks),
            "last_cleanup": datetime.now().isoformat()
        }
