
"""
RL Resource Manager - Reinforcement learning-based resource allocation
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class ResourceType(Enum):
    """Types of resources that can be allocated"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"


@dataclass
class ResourceAllocation:
    """Resource allocation result"""
    ritual_id: str
    allocated_resources: Dict[str, Any]
    allocation_confidence: float
    estimated_cost: float
    allocation_metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class ResourceState:
    """Current state of system resources"""
    available_cpu: float
    available_memory: float
    available_storage: float
    available_network: float
    available_gpu: float
    total_cpu: float
    total_memory: float
    total_storage: float
    total_network: float
    total_gpu: float
    utilization_cpu: float
    utilization_memory: float
    utilization_storage: float
    utilization_network: float
    utilization_gpu: float


class RLResourceManager:
    """
    Reinforcement Learning-based Resource Manager
    Uses Q-learning to optimize resource allocation decisions
    """
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.9):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = 0.1  # Exploration rate
        
        # Q-table for resource allocation decisions
        # State: (resource_demand_level, system_load_level, priority_level)
        # Action: (cpu_allocation_level, memory_allocation_level, storage_allocation_level)
        self.q_table = {}
        
        # Resource allocation history for learning
        self.allocation_history: List[Dict[str, Any]] = []
        self.feedback_history: List[Dict[str, Any]] = []
        
        # Resource limits and defaults
        self.resource_limits = {
            'cpu': 100.0,  # CPU cores
            'memory': 1024.0,  # GB
            'storage': 10000.0,  # GB
            'network': 10.0,  # Gbps
            'gpu': 8.0  # GPU units
        }
        
        self.default_allocations = {
            'low': {'cpu': 1, 'memory': 512, 'storage': 100, 'network': 0.1, 'gpu': 0},
            'medium': {'cpu': 2, 'memory': 1024, 'storage': 500, 'network': 0.5, 'gpu': 0.5},
            'high': {'cpu': 4, 'memory': 2048, 'storage': 1000, 'network': 1.0, 'gpu': 1.0}
        }
        
        # Current resource state
        self.current_state = ResourceState(
            available_cpu=90.0, available_memory=800.0, available_storage=8000.0,
            available_network=8.0, available_gpu=6.0,
            total_cpu=100.0, total_memory=1024.0, total_storage=10000.0,
            total_network=10.0, total_gpu=8.0,
            utilization_cpu=0.1, utilization_memory=0.22, utilization_storage=0.2,
            utilization_network=0.2, utilization_gpu=0.25
        )
    
    async def allocate_resources(self, allocation_request: Dict[str, Any]) -> ResourceAllocation:
        """Allocate resources using RL-based decision making"""
        try:
            ritual_id = allocation_request['ritual_id']
            
            # Extract state features
            state = self._extract_state_features(allocation_request)
            
            # Choose action using epsilon-greedy policy
            action = self._choose_action(state)
            
            # Convert action to resource allocation
            allocated_resources = self._action_to_allocation(action, allocation_request)
            
            # Calculate allocation confidence and cost
            allocation_confidence = self._calculate_allocation_confidence(
                allocated_resources, allocation_request
            )
            estimated_cost = self._calculate_estimated_cost(allocated_resources)
            
            # Create allocation result
            allocation = ResourceAllocation(
                ritual_id=ritual_id,
                allocated_resources=allocated_resources,
                allocation_confidence=allocation_confidence,
                estimated_cost=estimated_cost,
                allocation_metadata={
                    'state': state,
                    'action': action,
                    'strategy': allocation_request.get('strategy', 'adaptive')
                }
            )
            
            # Store allocation for learning
            self.allocation_history.append({
                'ritual_id': ritual_id,
                'state': state,
                'action': action,
                'allocation': asdict(allocation),
                'timestamp': datetime.now(timezone.utc)
            })
            
            # Update resource state
            await self._update_resource_state(allocated_resources, 'allocate')
            
            return allocation
            
        except Exception as e:
            print(f"Error allocating resources: {e}")
            # Return default allocation
            return ResourceAllocation(
                ritual_id=allocation_request.get('ritual_id', 'unknown'),
                allocated_resources=self.default_allocations['medium'].copy(),
                allocation_confidence=0.5,
                estimated_cost=1.0,
                allocation_metadata={'error': str(e)}
            )
    
    async def update_from_feedback(
        self,
        ritual_id: str,
        success: bool,
        performance_metrics: Dict[str, Any]
    ):
        """Update Q-table based on execution feedback"""
        try:
            # Find corresponding allocation
            allocation_record = None
            for record in reversed(self.allocation_history):
                if record['ritual_id'] == ritual_id:
                    allocation_record = record
                    break
            
            if not allocation_record:
                print(f"No allocation record found for ritual {ritual_id}")
                return
            
            # Calculate reward based on performance
            reward = self._calculate_reward(success, performance_metrics)
            
            # Store feedback
            feedback = {
                'ritual_id': ritual_id,
                'state': allocation_record['state'],
                'action': allocation_record['action'],
                'reward': reward,
                'success': success,
                'performance_metrics': performance_metrics,
                'timestamp': datetime.now(timezone.utc)
            }
            
            self.feedback_history.append(feedback)
            
            # Update Q-table
            self._update_q_table(
                allocation_record['state'],
                allocation_record['action'],
                reward
            )
            
            # Release allocated resources
            allocated_resources = allocation_record['allocation']['allocated_resources']
            await self._update_resource_state(allocated_resources, 'release')
            
        except Exception as e:
            print(f"Error updating from feedback: {e}")
    
    def _extract_state_features(self, allocation_request: Dict[str, Any]) -> Tuple[int, int, int]:
        """Extract state features for RL decision making"""
        try:
            # Resource demand level (0: low, 1: medium, 2: high)
            complexity_score = allocation_request.get('complexity_score', 0.5)
            resource_intensity = allocation_request.get('resource_intensity', 'medium')
            
            if resource_intensity == 'low' or complexity_score < 0.3:
                demand_level = 0
            elif resource_intensity == 'high' or complexity_score > 0.7:
                demand_level = 2
            else:
                demand_level = 1
            
            # System load level (0: low, 1: medium, 2: high)
            avg_utilization = (
                self.current_state.utilization_cpu +
                self.current_state.utilization_memory +
                self.current_state.utilization_storage
            ) / 3
            
            if avg_utilization < 0.3:
                load_level = 0
            elif avg_utilization > 0.7:
                load_level = 2
            else:
                load_level = 1
            
            # Priority level (0: low, 1: medium, 2: high)
            priority = allocation_request.get('priority', 5)
            if priority <= 3:
                priority_level = 0
            elif priority >= 8:
                priority_level = 2
            else:
                priority_level = 1
            
            return (demand_level, load_level, priority_level)
            
        except Exception as e:
            print(f"Error extracting state features: {e}")
            return (1, 1, 1)  # Default medium state
    
    def _choose_action(self, state: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Choose action using epsilon-greedy policy"""
        try:
            # Epsilon-greedy exploration
            if np.random.random() < self.epsilon:
                # Random action (exploration)
                cpu_level = np.random.randint(0, 3)
                memory_level = np.random.randint(0, 3)
                storage_level = np.random.randint(0, 3)
                return (cpu_level, memory_level, storage_level)
            
            # Greedy action (exploitation)
            best_action = None
            best_q_value = float('-inf')
            
            # Try all possible actions
            for cpu_level in range(3):
                for memory_level in range(3):
                    for storage_level in range(3):
                        action = (cpu_level, memory_level, storage_level)
                        q_value = self.q_table.get((state, action), 0.0)
                        
                        if q_value > best_q_value:
                            best_q_value = q_value
                            best_action = action
            
            return best_action or (1, 1, 1)  # Default medium action
            
        except Exception as e:
            print(f"Error choosing action: {e}")
            return (1, 1, 1)  # Default medium action
    
    def _action_to_allocation(
        self,
        action: Tuple[int, int, int],
        allocation_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert RL action to actual resource allocation"""
        try:
            cpu_level, memory_level, storage_level = action
            
            # Base allocations for each level
            cpu_allocations = [1, 2, 4]  # cores
            memory_allocations = [512, 1024, 2048]  # MB
            storage_allocations = [100, 500, 1000]  # MB
            
            # Get base allocation
            allocated_resources = {
                'cpu': cpu_allocations[cpu_level],
                'memory': memory_allocations[memory_level],
                'storage': storage_allocations[storage_level],
                'network': 0.1 + (cpu_level * 0.2),  # Scale network with CPU
                'gpu': 0.0 if cpu_level == 0 else (0.5 + cpu_level * 0.25)  # GPU for higher levels
            }
            
            # Adjust based on request specifics
            strategy = allocation_request.get('strategy', 'balanced')
            
            if strategy == 'performance_optimized':
                # Increase all allocations by 50%
                for resource in allocated_resources:
                    allocated_resources[resource] *= 1.5
            elif strategy == 'resource_efficient':
                # Decrease all allocations by 25%
                for resource in allocated_resources:
                    allocated_resources[resource] *= 0.75
            
            # Ensure allocations don't exceed available resources
            allocated_resources['cpu'] = min(allocated_resources['cpu'], self.current_state.available_cpu)
            allocated_resources['memory'] = min(allocated_resources['memory'], self.current_state.available_memory)
            allocated_resources['storage'] = min(allocated_resources['storage'], self.current_state.available_storage)
            allocated_resources['network'] = min(allocated_resources['network'], self.current_state.available_network)
            allocated_resources['gpu'] = min(allocated_resources['gpu'], self.current_state.available_gpu)
            
            return allocated_resources
            
        except Exception as e:
            print(f"Error converting action to allocation: {e}")
            return self.default_allocations['medium'].copy()
    
    def _calculate_allocation_confidence(
        self,
        allocated_resources: Dict[str, Any],
        allocation_request: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the resource allocation"""
        try:
            # Base confidence from resource availability
            resource_confidence = 0.0
            resource_count = 0
            
            for resource, amount in allocated_resources.items():
                if resource in ['cpu', 'memory', 'storage', 'network', 'gpu']:
                    available = getattr(self.current_state, f'available_{resource}', 0)
                    if available > 0:
                        utilization_ratio = amount / available
                        # Higher confidence for moderate utilization
                        if utilization_ratio < 0.1:
                            resource_confidence += 0.6  # Under-utilization
                        elif utilization_ratio < 0.5:
                            resource_confidence += 1.0  # Good utilization
                        elif utilization_ratio < 0.8:
                            resource_confidence += 0.8  # High utilization
                        else:
                            resource_confidence += 0.4  # Over-utilization
                        resource_count += 1
            
            base_confidence = resource_confidence / resource_count if resource_count > 0 else 0.5
            
            # Adjust based on request complexity
            complexity_score = allocation_request.get('complexity_score', 0.5)
            complexity_adjustment = 1.0 - (complexity_score * 0.2)  # Reduce confidence for complex requests
            
            # Adjust based on system load
            avg_utilization = (
                self.current_state.utilization_cpu +
                self.current_state.utilization_memory +
                self.current_state.utilization_storage
            ) / 3
            load_adjustment = 1.0 - (avg_utilization * 0.3)  # Reduce confidence for high load
            
            final_confidence = base_confidence * complexity_adjustment * load_adjustment
            return max(0.1, min(1.0, final_confidence))
            
        except Exception as e:
            print(f"Error calculating allocation confidence: {e}")
            return 0.5
    
    def _calculate_estimated_cost(self, allocated_resources: Dict[str, Any]) -> float:
        """Calculate estimated cost of resource allocation"""
        try:
            # Cost per unit (arbitrary units)
            cost_per_unit = {
                'cpu': 0.1,  # per core
                'memory': 0.001,  # per MB
                'storage': 0.0001,  # per MB
                'network': 0.05,  # per Gbps
                'gpu': 0.5  # per GPU unit
            }
            
            total_cost = 0.0
            for resource, amount in allocated_resources.items():
                if resource in cost_per_unit:
                    total_cost += amount * cost_per_unit[resource]
            
            return total_cost
            
        except Exception as e:
            print(f"Error calculating estimated cost: {e}")
            return 1.0
    
    async def _update_resource_state(self, allocated_resources: Dict[str, Any], operation: str):
        """Update current resource state based on allocation/release"""
        try:
            multiplier = -1 if operation == 'allocate' else 1
            
            for resource, amount in allocated_resources.items():
                if resource == 'cpu':
                    self.current_state.available_cpu += multiplier * amount
                    self.current_state.utilization_cpu = 1.0 - (self.current_state.available_cpu / self.current_state.total_cpu)
                elif resource == 'memory':
                    self.current_state.available_memory += multiplier * amount
                    self.current_state.utilization_memory = 1.0 - (self.current_state.available_memory / self.current_state.total_memory)
                elif resource == 'storage':
                    self.current_state.available_storage += multiplier * amount
                    self.current_state.utilization_storage = 1.0 - (self.current_state.available_storage / self.current_state.total_storage)
                elif resource == 'network':
                    self.current_state.available_network += multiplier * amount
                    self.current_state.utilization_network = 1.0 - (self.current_state.available_network / self.current_state.total_network)
                elif resource == 'gpu':
                    self.current_state.available_gpu += multiplier * amount
                    self.current_state.utilization_gpu = 1.0 - (self.current_state.available_gpu / self.current_state.total_gpu)
            
            # Ensure non-negative values
            self.current_state.available_cpu = max(0, self.current_state.available_cpu)
            self.current_state.available_memory = max(0, self.current_state.available_memory)
            self.current_state.available_storage = max(0, self.current_state.available_storage)
            self.current_state.available_network = max(0, self.current_state.available_network)
            self.current_state.available_gpu = max(0, self.current_state.available_gpu)
            
        except Exception as e:
            print(f"Error updating resource state: {e}")
    
    def _calculate_reward(self, success: bool, performance_metrics: Dict[str, Any]) -> float:
        """Calculate reward for RL learning"""
        try:
            if not success:
                return -1.0  # Negative reward for failure
            
            # Base reward for success
            reward = 1.0
            
            # Bonus for good performance
            performance_score = performance_metrics.get('performance_score', 0.5)
            reward += performance_score
            
            # Bonus for resource efficiency
            resource_efficiency = performance_metrics.get('resource_efficiency', 0.5)
            reward += resource_efficiency * 0.5
            
            # Penalty for long execution time
            execution_time = performance_metrics.get('execution_time', 1.0)
            if execution_time > 5.0:  # Penalty for executions longer than 5 seconds
                reward -= (execution_time - 5.0) * 0.1
            
            return max(-2.0, min(3.0, reward))  # Clamp reward between -2 and 3
            
        except Exception as e:
            print(f"Error calculating reward: {e}")
            return 0.0
    
    def _update_q_table(self, state: Tuple[int, int, int], action: Tuple[int, int, int], reward: float):
        """Update Q-table using Q-learning algorithm"""
        try:
            state_action = (state, action)
            
            # Current Q-value
            current_q = self.q_table.get(state_action, 0.0)
            
            # For simplicity, assume next state has Q-value of 0 (terminal state)
            # In a more complex implementation, you would calculate the max Q-value for the next state
            next_q_max = 0.0
            
            # Q-learning update rule
            new_q = current_q + self.learning_rate * (reward + self.discount_factor * next_q_max - current_q)
            
            self.q_table[state_action] = new_q
            
        except Exception as e:
            print(f"Error updating Q-table: {e}")
    
    async def apply_optimizations(self, optimizations: Dict[str, Any]):
        """Apply optimizations from evolutionary algorithm"""
        try:
            if 'learning_rate' in optimizations:
                self.learning_rate = max(0.01, min(0.5, optimizations['learning_rate']))
            
            if 'epsilon' in optimizations:
                self.epsilon = max(0.01, min(0.3, optimizations['epsilon']))
            
            if 'discount_factor' in optimizations:
                self.discount_factor = max(0.5, min(0.99, optimizations['discount_factor']))
            
            print(f"Applied resource manager optimizations: {list(optimizations.keys())}")
            
        except Exception as e:
            print(f"Error applying optimizations: {e}")
    
    async def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource manager statistics"""
        try:
            return {
                'current_state': asdict(self.current_state),
                'q_table_size': len(self.q_table),
                'allocation_history_size': len(self.allocation_history),
                'feedback_history_size': len(self.feedback_history),
                'learning_parameters': {
                    'learning_rate': self.learning_rate,
                    'discount_factor': self.discount_factor,
                    'epsilon': self.epsilon
                },
                'resource_limits': self.resource_limits,
                'recent_performance': self._calculate_recent_performance()
            }
            
        except Exception as e:
            print(f"Error getting resource stats: {e}")
            return {'error': str(e)}
    
    def _calculate_recent_performance(self) -> Dict[str, float]:
        """Calculate recent performance metrics"""
        try:
            if not self.feedback_history:
                return {'avg_reward': 0.0, 'success_rate': 0.0}
            
            recent_feedback = self.feedback_history[-20:]  # Last 20 feedback entries
            
            avg_reward = np.mean([f['reward'] for f in recent_feedback])
            success_rate = sum(1 for f in recent_feedback if f['success']) / len(recent_feedback)
            
            return {
                'avg_reward': avg_reward,
                'success_rate': success_rate,
                'feedback_count': len(recent_feedback)
            }
            
        except Exception as e:
            print(f"Error calculating recent performance: {e}")
            return {'avg_reward': 0.0, 'success_rate': 0.0}
