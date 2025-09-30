
"""
Context-Aware Load Balancer - Intelligent task distribution across nodes
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class NodeStatus(Enum):
    """Node status types"""
    ACTIVE = "active"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


@dataclass
class Node:
    """Represents a compute node in the system"""
    node_id: str
    node_name: str
    capabilities: List[str]
    capacity: Dict[str, float]
    current_load: Dict[str, float]
    status: NodeStatus
    location: Optional[str] = None
    last_seen: Optional[datetime] = None
    performance_history: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = []
        if self.last_seen is None:
            self.last_seen = datetime.now(timezone.utc)


@dataclass
class NodeSelection:
    """Result of node selection process"""
    ritual_id: str
    selected_nodes: List[str]
    node_assignments: Dict[str, Dict[str, Any]]
    load_distribution: Dict[str, float]
    selection_confidence: float
    selection_metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class ContextAwareBalancer:
    """
    Context-aware load balancer that intelligently distributes tasks
    across nodes based on context, node capabilities, and current load
    """
    
    def __init__(self):
        # Node registry
        self.nodes: Dict[str, Node] = {}
        
        # Load balancing algorithms
        self.algorithms = {
            'round_robin': self._round_robin_selection,
            'least_loaded': self._least_loaded_selection,
            'capability_based': self._capability_based_selection,
            'performance_based': self._performance_based_selection,
            'context_aware': self._context_aware_selection,
            'multi_armed_bandit': self._multi_armed_bandit_selection
        }
        
        # Multi-armed bandit parameters
        self.node_rewards: Dict[str, List[float]] = {}
        self.node_selections: Dict[str, int] = {}
        self.exploration_factor = 1.4  # UCB1 exploration parameter
        
        # Selection history for learning
        self.selection_history: List[Dict[str, Any]] = []
        self.feedback_history: List[Dict[str, Any]] = []
        
        # Default algorithm
        self.default_algorithm = 'context_aware'
        
        # Initialize with some default nodes
        self._initialize_default_nodes()
    
    def _initialize_default_nodes(self):
        """Initialize with default nodes for testing"""
        try:
            default_nodes = [
                Node(
                    node_id="node_1",
                    node_name="Primary Compute Node",
                    capabilities=["multimodal", "memory", "general"],
                    capacity={"cpu": 8, "memory": 16384, "storage": 1000, "gpu": 2},
                    current_load={"cpu": 2, "memory": 4096, "storage": 200, "gpu": 0.5},
                    status=NodeStatus.ACTIVE,
                    location="datacenter_1"
                ),
                Node(
                    node_id="node_2",
                    node_name="Memory Specialist Node",
                    capabilities=["memory", "distributed", "general"],
                    capacity={"cpu": 4, "memory": 32768, "storage": 2000, "gpu": 0},
                    current_load={"cpu": 1, "memory": 8192, "storage": 400, "gpu": 0},
                    status=NodeStatus.ACTIVE,
                    location="datacenter_1"
                ),
                Node(
                    node_id="node_3",
                    node_name="GPU Accelerated Node",
                    capabilities=["multimodal", "vision", "audio", "general"],
                    capacity={"cpu": 6, "memory": 12288, "storage": 500, "gpu": 4},
                    current_load={"cpu": 3, "memory": 6144, "storage": 100, "gpu": 1},
                    status=NodeStatus.ACTIVE,
                    location="datacenter_2"
                ),
                Node(
                    node_id="node_4",
                    node_name="Distributed Processing Node",
                    capabilities=["distributed", "orchestration", "general"],
                    capacity={"cpu": 12, "memory": 8192, "storage": 3000, "gpu": 0},
                    current_load={"cpu": 4, "memory": 2048, "storage": 600, "gpu": 0},
                    status=NodeStatus.ACTIVE,
                    location="datacenter_2"
                )
            ]
            
            for node in default_nodes:
                self.nodes[node.node_id] = node
                self.node_rewards[node.node_id] = [0.8]  # Initial reward
                self.node_selections[node.node_id] = 1
            
        except Exception as e:
            print(f"Error initializing default nodes: {e}")
    
    async def select_nodes(self, selection_request: Dict[str, Any]) -> NodeSelection:
        """Select optimal nodes for task execution"""
        try:
            ritual_id = selection_request['ritual_id']
            
            # Determine selection algorithm
            algorithm = self._determine_algorithm(selection_request)
            
            # Select nodes using chosen algorithm
            if algorithm in self.algorithms:
                selected_nodes, node_assignments, load_distribution, confidence = await self.algorithms[algorithm](
                    selection_request
                )
            else:
                # Fallback to context-aware selection
                selected_nodes, node_assignments, load_distribution, confidence = await self._context_aware_selection(
                    selection_request
                )
            
            # Create node selection result
            node_selection = NodeSelection(
                ritual_id=ritual_id,
                selected_nodes=selected_nodes,
                node_assignments=node_assignments,
                load_distribution=load_distribution,
                selection_confidence=confidence,
                selection_metadata={
                    'algorithm_used': algorithm,
                    'total_nodes_available': len([n for n in self.nodes.values() if n.status == NodeStatus.ACTIVE]),
                    'selection_criteria': selection_request.get('strategy', 'balanced')
                }
            )
            
            # Store selection for learning
            self.selection_history.append({
                'ritual_id': ritual_id,
                'selection_request': selection_request,
                'node_selection': asdict(node_selection),
                'timestamp': datetime.now(timezone.utc)
            })
            
            # Update node selection counts
            for node_id in selected_nodes:
                self.node_selections[node_id] = self.node_selections.get(node_id, 0) + 1
            
            return node_selection
            
        except Exception as e:
            print(f"Error selecting nodes: {e}")
            # Return default selection
            active_nodes = [node_id for node_id, node in self.nodes.items() if node.status == NodeStatus.ACTIVE]
            default_node = active_nodes[0] if active_nodes else "node_1"
            
            return NodeSelection(
                ritual_id=selection_request.get('ritual_id', 'unknown'),
                selected_nodes=[default_node],
                node_assignments={default_node: {'role': 'primary'}},
                load_distribution={default_node: 1.0},
                selection_confidence=0.5,
                selection_metadata={'error': str(e)}
            )
    
    def _determine_algorithm(self, selection_request: Dict[str, Any]) -> str:
        """Determine the best algorithm for node selection"""
        try:
            strategy = selection_request.get('strategy', 'balanced')
            ritual_type = selection_request.get('ritual_type', '').lower()
            
            # Strategy-based algorithm selection
            if strategy == 'performance_optimized':
                return 'performance_based'
            elif strategy == 'resource_efficient':
                return 'least_loaded'
            elif strategy == 'fault_tolerant':
                return 'multi_armed_bandit'
            
            # Ritual type-based algorithm selection
            if 'multimodal' in ritual_type:
                return 'capability_based'
            elif 'distributed' in ritual_type:
                return 'context_aware'
            
            return self.default_algorithm
            
        except Exception as e:
            print(f"Error determining algorithm: {e}")
            return self.default_algorithm
    
    async def _round_robin_selection(
        self,
        selection_request: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, float], float]:
        """Round-robin node selection"""
        try:
            active_nodes = [node_id for node_id, node in self.nodes.items() if node.status == NodeStatus.ACTIVE]
            
            if not active_nodes:
                return [], {}, {}, 0.0
            
            # Simple round-robin based on total selections
            total_selections = sum(self.node_selections.values())
            selected_node = active_nodes[total_selections % len(active_nodes)]
            
            return (
                [selected_node],
                {selected_node: {'role': 'primary', 'algorithm': 'round_robin'}},
                {selected_node: 1.0},
                0.7  # Moderate confidence for round-robin
            )
            
        except Exception as e:
            print(f"Error in round-robin selection: {e}")
            return [], {}, {}, 0.0
    
    async def _least_loaded_selection(
        self,
        selection_request: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, float], float]:
        """Select least loaded nodes"""
        try:
            active_nodes = [(node_id, node) for node_id, node in self.nodes.items() if node.status == NodeStatus.ACTIVE]
            
            if not active_nodes:
                return [], {}, {}, 0.0
            
            # Calculate load scores for each node
            node_loads = []
            for node_id, node in active_nodes:
                total_load = 0.0
                total_capacity = 0.0
                
                for resource in ['cpu', 'memory', 'storage']:
                    if resource in node.current_load and resource in node.capacity:
                        load_ratio = node.current_load[resource] / node.capacity[resource]
                        total_load += load_ratio
                        total_capacity += 1.0
                
                avg_load = total_load / total_capacity if total_capacity > 0 else 0.5
                node_loads.append((node_id, avg_load))
            
            # Sort by load (ascending)
            node_loads.sort(key=lambda x: x[1])
            
            # Select the least loaded node
            selected_node = node_loads[0][0]
            load_score = node_loads[0][1]
            
            confidence = 1.0 - load_score  # Higher confidence for lower load
            
            return (
                [selected_node],
                {selected_node: {'role': 'primary', 'algorithm': 'least_loaded', 'load_score': load_score}},
                {selected_node: 1.0},
                confidence
            )
            
        except Exception as e:
            print(f"Error in least loaded selection: {e}")
            return [], {}, {}, 0.0
    
    async def _capability_based_selection(
        self,
        selection_request: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, float], float]:
        """Select nodes based on required capabilities"""
        try:
            ritual_type = selection_request.get('ritual_type', '').lower()
            
            # Determine required capabilities
            required_capabilities = []
            if 'multimodal' in ritual_type:
                required_capabilities.extend(['multimodal', 'vision', 'audio'])
            if 'memory' in ritual_type:
                required_capabilities.append('memory')
            if 'distributed' in ritual_type:
                required_capabilities.append('distributed')
            
            if not required_capabilities:
                required_capabilities = ['general']
            
            # Find nodes with matching capabilities
            matching_nodes = []
            for node_id, node in self.nodes.items():
                if node.status != NodeStatus.ACTIVE:
                    continue
                
                capability_match_score = 0.0
                for req_cap in required_capabilities:
                    if req_cap in node.capabilities:
                        capability_match_score += 1.0
                
                if capability_match_score > 0:
                    capability_match_score /= len(required_capabilities)
                    matching_nodes.append((node_id, capability_match_score))
            
            if not matching_nodes:
                # Fallback to any active node
                active_nodes = [node_id for node_id, node in self.nodes.items() if node.status == NodeStatus.ACTIVE]
                if active_nodes:
                    return (
                        [active_nodes[0]],
                        {active_nodes[0]: {'role': 'primary', 'algorithm': 'capability_based', 'fallback': True}},
                        {active_nodes[0]: 1.0},
                        0.3
                    )
                return [], {}, {}, 0.0
            
            # Sort by capability match score (descending)
            matching_nodes.sort(key=lambda x: x[1], reverse=True)
            
            # Select the best matching node
            selected_node = matching_nodes[0][0]
            match_score = matching_nodes[0][1]
            
            return (
                [selected_node],
                {selected_node: {'role': 'primary', 'algorithm': 'capability_based', 'match_score': match_score}},
                {selected_node: 1.0},
                match_score
            )
            
        except Exception as e:
            print(f"Error in capability-based selection: {e}")
            return [], {}, {}, 0.0
    
    async def _performance_based_selection(
        self,
        selection_request: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, float], float]:
        """Select nodes based on historical performance"""
        try:
            active_nodes = [(node_id, node) for node_id, node in self.nodes.items() if node.status == NodeStatus.ACTIVE]
            
            if not active_nodes:
                return [], {}, {}, 0.0
            
            # Calculate performance scores
            node_performances = []
            for node_id, node in active_nodes:
                if node.performance_history:
                    avg_performance = np.mean(node.performance_history[-10:])  # Last 10 performances
                else:
                    avg_performance = 0.5  # Default performance
                
                node_performances.append((node_id, avg_performance))
            
            # Sort by performance (descending)
            node_performances.sort(key=lambda x: x[1], reverse=True)
            
            # Select the best performing node
            selected_node = node_performances[0][0]
            performance_score = node_performances[0][1]
            
            return (
                [selected_node],
                {selected_node: {'role': 'primary', 'algorithm': 'performance_based', 'performance_score': performance_score}},
                {selected_node: 1.0},
                performance_score
            )
            
        except Exception as e:
            print(f"Error in performance-based selection: {e}")
            return [], {}, {}, 0.0
    
    async def _context_aware_selection(
        self,
        selection_request: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, float], float]:
        """Context-aware node selection combining multiple factors"""
        try:
            active_nodes = [(node_id, node) for node_id, node in self.nodes.items() if node.status == NodeStatus.ACTIVE]
            
            if not active_nodes:
                return [], {}, {}, 0.0
            
            ritual_type = selection_request.get('ritual_type', '').lower()
            priority = selection_request.get('priority', 5)
            resource_requirements = selection_request.get('resource_requirements', {})
            
            # Score each node based on multiple factors
            node_scores = []
            
            for node_id, node in active_nodes:
                score = 0.0
                
                # Capability matching (30% weight)
                capability_score = 0.0
                if 'multimodal' in ritual_type and 'multimodal' in node.capabilities:
                    capability_score += 0.4
                if 'memory' in ritual_type and 'memory' in node.capabilities:
                    capability_score += 0.3
                if 'distributed' in ritual_type and 'distributed' in node.capabilities:
                    capability_score += 0.3
                if 'general' in node.capabilities:
                    capability_score += 0.2
                
                score += capability_score * 0.3
                
                # Load balancing (25% weight)
                total_load = 0.0
                total_capacity = 0.0
                for resource in ['cpu', 'memory', 'storage']:
                    if resource in node.current_load and resource in node.capacity:
                        load_ratio = node.current_load[resource] / node.capacity[resource]
                        total_load += load_ratio
                        total_capacity += 1.0
                
                avg_load = total_load / total_capacity if total_capacity > 0 else 0.5
                load_score = 1.0 - avg_load  # Higher score for lower load
                score += load_score * 0.25
                
                # Performance history (25% weight)
                if node.performance_history:
                    performance_score = np.mean(node.performance_history[-5:])  # Last 5 performances
                else:
                    performance_score = 0.5
                score += performance_score * 0.25
                
                # Resource availability (20% weight)
                resource_score = 0.0
                resource_count = 0
                for resource, required in resource_requirements.items():
                    if resource in node.capacity:
                        available = node.capacity[resource] - node.current_load.get(resource, 0)
                        if available >= required:
                            resource_score += 1.0
                        else:
                            resource_score += available / required
                        resource_count += 1
                
                if resource_count > 0:
                    resource_score /= resource_count
                else:
                    resource_score = 0.8  # Default if no specific requirements
                
                score += resource_score * 0.2
                
                node_scores.append((node_id, score))
            
            # Sort by score (descending)
            node_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select the highest scoring node
            selected_node = node_scores[0][0]
            context_score = node_scores[0][1]
            
            return (
                [selected_node],
                {selected_node: {'role': 'primary', 'algorithm': 'context_aware', 'context_score': context_score}},
                {selected_node: 1.0},
                context_score
            )
            
        except Exception as e:
            print(f"Error in context-aware selection: {e}")
            return [], {}, {}, 0.0
    
    async def _multi_armed_bandit_selection(
        self,
        selection_request: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Dict[str, Any]], Dict[str, float], float]:
        """Multi-armed bandit node selection using UCB1 algorithm"""
        try:
            active_nodes = [node_id for node_id, node in self.nodes.items() if node.status == NodeStatus.ACTIVE]
            
            if not active_nodes:
                return [], {}, {}, 0.0
            
            total_selections = sum(self.node_selections.values())
            
            # Calculate UCB1 scores for each node
            ucb_scores = []
            for node_id in active_nodes:
                if node_id not in self.node_rewards or not self.node_rewards[node_id]:
                    # New node, give it high priority
                    ucb_score = float('inf')
                else:
                    avg_reward = np.mean(self.node_rewards[node_id])
                    selections = self.node_selections.get(node_id, 1)
                    
                    if selections == 0:
                        ucb_score = float('inf')
                    else:
                        exploration_term = self.exploration_factor * np.sqrt(np.log(total_selections) / selections)
                        ucb_score = avg_reward + exploration_term
                
                ucb_scores.append((node_id, ucb_score))
            
            # Sort by UCB score (descending)
            ucb_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select the node with highest UCB score
            selected_node = ucb_scores[0][0]
            ucb_score = ucb_scores[0][1]
            
            # Calculate confidence based on exploration vs exploitation
            if ucb_score == float('inf'):
                confidence = 0.5  # Moderate confidence for exploration
            else:
                avg_reward = np.mean(self.node_rewards[selected_node])
                confidence = min(1.0, avg_reward + 0.2)  # Boost confidence slightly
            
            return (
                [selected_node],
                {selected_node: {'role': 'primary', 'algorithm': 'multi_armed_bandit', 'ucb_score': ucb_score}},
                {selected_node: 1.0},
                confidence
            )
            
        except Exception as e:
            print(f"Error in multi-armed bandit selection: {e}")
            return [], {}, {}, 0.0
    
    async def update_from_feedback(
        self,
        ritual_id: str,
        nodes_used: List[str],
        success: bool,
        performance_metrics: Dict[str, Any]
    ):
        """Update node performance based on execution feedback"""
        try:
            # Calculate reward based on performance
            reward = self._calculate_node_reward(success, performance_metrics)
            
            # Update node rewards and performance history
            for node_id in nodes_used:
                if node_id in self.nodes:
                    # Update multi-armed bandit rewards
                    if node_id not in self.node_rewards:
                        self.node_rewards[node_id] = []
                    self.node_rewards[node_id].append(reward)
                    
                    # Keep only recent rewards (last 50)
                    if len(self.node_rewards[node_id]) > 50:
                        self.node_rewards[node_id] = self.node_rewards[node_id][-50:]
                    
                    # Update node performance history
                    performance_score = performance_metrics.get('performance_score', reward)
                    self.nodes[node_id].performance_history.append(performance_score)
                    
                    # Keep only recent performance history (last 20)
                    if len(self.nodes[node_id].performance_history) > 20:
                        self.nodes[node_id].performance_history = self.nodes[node_id].performance_history[-20:]
            
            # Store feedback
            feedback = {
                'ritual_id': ritual_id,
                'nodes_used': nodes_used,
                'success': success,
                'performance_metrics': performance_metrics,
                'reward': reward,
                'timestamp': datetime.now(timezone.utc)
            }
            
            self.feedback_history.append(feedback)
            
            # Keep only recent feedback (last 100)
            if len(self.feedback_history) > 100:
                self.feedback_history = self.feedback_history[-100:]
            
        except Exception as e:
            print(f"Error updating from feedback: {e}")
    
    def _calculate_node_reward(self, success: bool, performance_metrics: Dict[str, Any]) -> float:
        """Calculate reward for node performance"""
        try:
            if not success:
                return 0.1  # Small positive reward to avoid completely avoiding nodes
            
            # Base reward for success
            reward = 0.7
            
            # Bonus for good performance
            performance_score = performance_metrics.get('performance_score', 0.5)
            reward += performance_score * 0.2
            
            # Bonus for efficiency
            efficiency = performance_metrics.get('overall_efficiency', 0.5)
            reward += efficiency * 0.1
            
            return min(1.0, reward)
            
        except Exception as e:
            print(f"Error calculating node reward: {e}")
            return 0.5
    
    async def add_node(self, node: Node) -> bool:
        """Add a new node to the load balancer"""
        try:
            self.nodes[node.node_id] = node
            self.node_rewards[node.node_id] = [0.5]  # Initial neutral reward
            self.node_selections[node.node_id] = 0
            
            print(f"Added node: {node.node_name} ({node.node_id})")
            return True
            
        except Exception as e:
            print(f"Error adding node: {e}")
            return False
    
    async def remove_node(self, node_id: str) -> bool:
        """Remove a node from the load balancer"""
        try:
            if node_id in self.nodes:
                del self.nodes[node_id]
                if node_id in self.node_rewards:
                    del self.node_rewards[node_id]
                if node_id in self.node_selections:
                    del self.node_selections[node_id]
                
                print(f"Removed node: {node_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error removing node: {e}")
            return False
    
    async def update_node_status(self, node_id: str, status: NodeStatus):
        """Update node status"""
        try:
            if node_id in self.nodes:
                self.nodes[node_id].status = status
                self.nodes[node_id].last_seen = datetime.now(timezone.utc)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating node status: {e}")
            return False
    
    async def apply_optimizations(self, optimizations: Dict[str, Any]):
        """Apply optimizations from evolutionary algorithm"""
        try:
            if 'exploration_factor' in optimizations:
                self.exploration_factor = max(0.5, min(3.0, optimizations['exploration_factor']))
            
            if 'default_algorithm' in optimizations:
                if optimizations['default_algorithm'] in self.algorithms:
                    self.default_algorithm = optimizations['default_algorithm']
            
            print(f"Applied load balancer optimizations: {list(optimizations.keys())}")
            
        except Exception as e:
            print(f"Error applying optimizations: {e}")
    
    async def get_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        try:
            active_nodes = [node for node in self.nodes.values() if node.status == NodeStatus.ACTIVE]
            
            return {
                'total_nodes': len(self.nodes),
                'active_nodes': len(active_nodes),
                'node_status_distribution': {
                    status.value: len([n for n in self.nodes.values() if n.status == status])
                    for status in NodeStatus
                },
                'algorithms_available': list(self.algorithms.keys()),
                'default_algorithm': self.default_algorithm,
                'selection_history_size': len(self.selection_history),
                'feedback_history_size': len(self.feedback_history),
                'node_performance_summary': {
                    node_id: {
                        'avg_reward': np.mean(self.node_rewards.get(node_id, [0.5])),
                        'selections': self.node_selections.get(node_id, 0),
                        'status': node.status.value
                    }
                    for node_id, node in self.nodes.items()
                },
                'multi_armed_bandit_params': {
                    'exploration_factor': self.exploration_factor
                }
            }
            
        except Exception as e:
            print(f"Error getting balancer stats: {e}")
            return {'error': str(e)}
