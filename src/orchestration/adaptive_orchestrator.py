
"""
Adaptive Orchestrator - Main orchestration engine with self-optimizing capabilities
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from .resource_manager import RLResourceManager, ResourceAllocation
from .load_balancer import ContextAwareBalancer, NodeSelection
from .evolution_engine import GeneticOptimizer, OptimizationResult
from .performance_monitor import SystemMonitor, SystemMetrics


class OrchestrationStrategy(Enum):
    """Orchestration strategies"""
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    RESOURCE_EFFICIENT = "resource_efficient"
    BALANCED = "balanced"
    ADAPTIVE = "adaptive"
    FAULT_TOLERANT = "fault_tolerant"


@dataclass
class RitualRequest:
    """Request for ritual execution"""
    ritual_id: str
    ritual_type: str
    context: Dict[str, Any]
    parameters: Dict[str, Any]
    priority: int = 5  # 1-10, 10 being highest
    deadline: Optional[datetime] = None
    resource_requirements: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OrchestrationResult:
    """Result of orchestrated ritual execution"""
    ritual_id: str
    success: bool
    result: Dict[str, Any]
    execution_time: float
    resources_used: Dict[str, Any]
    nodes_used: List[str]
    performance_metrics: Dict[str, Any]
    optimization_applied: bool
    timestamp: datetime


class AdaptiveOrchestrator:
    """
    Main orchestration engine that coordinates resource management, load balancing,
    and evolutionary optimization for optimal system performance
    """
    
    def __init__(
        self,
        resource_manager: Optional[RLResourceManager] = None,
        load_balancer: Optional[ContextAwareBalancer] = None,
        evolution_engine: Optional[GeneticOptimizer] = None,
        performance_monitor: Optional[SystemMonitor] = None,
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE
    ):
        self.resource_manager = resource_manager or RLResourceManager()
        self.load_balancer = load_balancer or ContextAwareBalancer()
        self.evolution_engine = evolution_engine or GeneticOptimizer()
        self.performance_monitor = performance_monitor or SystemMonitor()
        
        self.strategy = strategy
        self.execution_history: List[OrchestrationResult] = []
        self.optimization_schedule = timedelta(hours=1)  # Optimize every hour
        self.last_optimization = datetime.now(timezone.utc)
        
        # Adaptive parameters
        self.adaptation_threshold = 0.8  # Trigger adaptation when performance drops below this
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        
        # Performance tracking
        self.performance_window = 100  # Track last 100 executions
        self.target_metrics = {
            'success_rate': 0.95,
            'avg_response_time': 2.0,  # seconds
            'resource_efficiency': 0.8
        }
    
    async def orchestrate_ritual(
        self,
        ritual_request: RitualRequest,
        strategy_override: Optional[OrchestrationStrategy] = None
    ) -> OrchestrationResult:
        """Orchestrate the execution of a ritual with adaptive optimization"""
        try:
            start_time = datetime.now(timezone.utc)
            strategy = strategy_override or self.strategy
            
            # Get current system state
            system_state = await self.performance_monitor.get_current_metrics()
            
            # Analyze ritual requirements
            ritual_analysis = await self._analyze_ritual_requirements(ritual_request)
            
            # Allocate resources based on strategy
            resource_allocation = await self._allocate_resources(
                ritual_request, ritual_analysis, system_state, strategy
            )
            
            # Select optimal execution nodes
            node_selection = await self._select_execution_nodes(
                ritual_request, resource_allocation, system_state, strategy
            )
            
            # Execute ritual with monitoring
            execution_result = await self._execute_with_monitoring(
                ritual_request, resource_allocation, node_selection
            )
            
            # Calculate performance metrics
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds()
            
            performance_metrics = await self._calculate_performance_metrics(
                execution_result, execution_time, resource_allocation, node_selection
            )
            
            # Create orchestration result
            orchestration_result = OrchestrationResult(
                ritual_id=ritual_request.ritual_id,
                success=execution_result.get('success', False),
                result=execution_result,
                execution_time=execution_time,
                resources_used=resource_allocation.allocated_resources,
                nodes_used=node_selection.selected_nodes,
                performance_metrics=performance_metrics,
                optimization_applied=False,  # Will be updated if optimization occurs
                timestamp=end_time
            )
            
            # Store execution history
            self.execution_history.append(orchestration_result)
            if len(self.execution_history) > self.performance_window:
                self.execution_history = self.execution_history[-self.performance_window:]
            
            # Learn from execution
            await self._learn_from_execution(orchestration_result)
            
            # Check if optimization is needed
            if await self._should_optimize():
                optimization_result = await self._trigger_optimization()
                orchestration_result.optimization_applied = optimization_result.success
            
            return orchestration_result
            
        except Exception as e:
            return OrchestrationResult(
                ritual_id=ritual_request.ritual_id,
                success=False,
                result={'error': str(e)},
                execution_time=0.0,
                resources_used={},
                nodes_used=[],
                performance_metrics={},
                optimization_applied=False,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _analyze_ritual_requirements(self, ritual_request: RitualRequest) -> Dict[str, Any]:
        """Analyze ritual requirements for optimal orchestration"""
        try:
            analysis = {
                'complexity_score': 0.0,
                'resource_intensity': 'medium',
                'parallelizable': True,
                'memory_requirements': 'standard',
                'cpu_requirements': 'standard',
                'io_requirements': 'standard',
                'estimated_duration': 1.0,  # seconds
                'dependencies': []
            }
            
            # Analyze based on ritual type
            ritual_type = ritual_request.ritual_type.lower()
            
            if 'multimodal' in ritual_type:
                analysis['complexity_score'] = 0.8
                analysis['resource_intensity'] = 'high'
                analysis['memory_requirements'] = 'high'
                analysis['estimated_duration'] = 3.0
            elif 'memory' in ritual_type:
                analysis['complexity_score'] = 0.6
                analysis['memory_requirements'] = 'high'
                analysis['io_requirements'] = 'high'
                analysis['estimated_duration'] = 2.0
            elif 'distributed' in ritual_type:
                analysis['complexity_score'] = 0.9
                analysis['resource_intensity'] = 'high'
                analysis['parallelizable'] = True
                analysis['estimated_duration'] = 4.0
            
            # Analyze context complexity
            context_size = len(str(ritual_request.context))
            if context_size > 10000:
                analysis['complexity_score'] += 0.2
                analysis['memory_requirements'] = 'high'
            
            # Analyze parameters
            param_count = len(ritual_request.parameters)
            if param_count > 20:
                analysis['complexity_score'] += 0.1
            
            # Consider priority
            if ritual_request.priority > 8:
                analysis['resource_intensity'] = 'high'
            elif ritual_request.priority < 3:
                analysis['resource_intensity'] = 'low'
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing ritual requirements: {e}")
            return {'complexity_score': 0.5, 'resource_intensity': 'medium'}
    
    async def _allocate_resources(
        self,
        ritual_request: RitualRequest,
        ritual_analysis: Dict[str, Any],
        system_state: SystemMetrics,
        strategy: OrchestrationStrategy
    ) -> ResourceAllocation:
        """Allocate resources based on strategy and system state"""
        try:
            # Prepare allocation request
            allocation_request = {
                'ritual_id': ritual_request.ritual_id,
                'complexity_score': ritual_analysis['complexity_score'],
                'resource_intensity': ritual_analysis['resource_intensity'],
                'priority': ritual_request.priority,
                'estimated_duration': ritual_analysis['estimated_duration'],
                'strategy': strategy.value,
                'system_state': asdict(system_state)
            }
            
            # Use resource manager to allocate
            allocation = await self.resource_manager.allocate_resources(allocation_request)
            
            return allocation
            
        except Exception as e:
            print(f"Error allocating resources: {e}")
            # Return default allocation
            return ResourceAllocation(
                ritual_id=ritual_request.ritual_id,
                allocated_resources={'cpu': 1, 'memory': 512, 'storage': 100},
                allocation_confidence=0.5,
                estimated_cost=1.0,
                allocation_metadata={'error': str(e)}
            )
    
    async def _select_execution_nodes(
        self,
        ritual_request: RitualRequest,
        resource_allocation: ResourceAllocation,
        system_state: SystemMetrics,
        strategy: OrchestrationStrategy
    ) -> NodeSelection:
        """Select optimal execution nodes"""
        try:
            # Prepare node selection request
            selection_request = {
                'ritual_id': ritual_request.ritual_id,
                'ritual_type': ritual_request.ritual_type,
                'resource_requirements': resource_allocation.allocated_resources,
                'priority': ritual_request.priority,
                'strategy': strategy.value,
                'system_state': asdict(system_state),
                'deadline': ritual_request.deadline.isoformat() if ritual_request.deadline else None
            }
            
            # Use load balancer to select nodes
            node_selection = await self.load_balancer.select_nodes(selection_request)
            
            return node_selection
            
        except Exception as e:
            print(f"Error selecting execution nodes: {e}")
            # Return default node selection
            return NodeSelection(
                ritual_id=ritual_request.ritual_id,
                selected_nodes=['default_node'],
                node_assignments={},
                load_distribution={},
                selection_confidence=0.5,
                selection_metadata={'error': str(e)}
            )
    
    async def _execute_with_monitoring(
        self,
        ritual_request: RitualRequest,
        resource_allocation: ResourceAllocation,
        node_selection: NodeSelection
    ) -> Dict[str, Any]:
        """Execute ritual with real-time monitoring"""
        try:
            # Start monitoring
            monitoring_task = asyncio.create_task(
                self.performance_monitor.monitor_execution(ritual_request.ritual_id)
            )
            
            # Simulate ritual execution (in real implementation, this would call actual ritual logic)
            execution_result = await self._simulate_ritual_execution(
                ritual_request, resource_allocation, node_selection
            )
            
            # Stop monitoring
            monitoring_task.cancel()
            
            return execution_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _simulate_ritual_execution(
        self,
        ritual_request: RitualRequest,
        resource_allocation: ResourceAllocation,
        node_selection: NodeSelection
    ) -> Dict[str, Any]:
        """Simulate ritual execution (placeholder for actual execution logic)"""
        try:
            # Simulate execution time based on complexity
            complexity = ritual_request.parameters.get('complexity', 0.5)
            execution_time = complexity * 2.0 + np.random.normal(0, 0.5)
            execution_time = max(0.1, execution_time)  # Minimum 0.1 seconds
            
            await asyncio.sleep(execution_time)
            
            # Simulate success/failure based on resource allocation quality
            allocation_quality = resource_allocation.allocation_confidence
            node_quality = node_selection.selection_confidence
            
            overall_quality = (allocation_quality + node_quality) / 2
            success_probability = overall_quality * 0.9 + 0.1  # 10% base success rate
            
            success = np.random.random() < success_probability
            
            if success:
                return {
                    'success': True,
                    'result': {
                        'ritual_type': ritual_request.ritual_type,
                        'execution_time': execution_time,
                        'nodes_used': node_selection.selected_nodes,
                        'resources_used': resource_allocation.allocated_resources
                    },
                    'performance_score': overall_quality
                }
            else:
                return {
                    'success': False,
                    'error': 'Simulated execution failure',
                    'performance_score': overall_quality * 0.5
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _calculate_performance_metrics(
        self,
        execution_result: Dict[str, Any],
        execution_time: float,
        resource_allocation: ResourceAllocation,
        node_selection: NodeSelection
    ) -> Dict[str, Any]:
        """Calculate performance metrics for the execution"""
        try:
            metrics = {
                'execution_time': execution_time,
                'success': execution_result.get('success', False),
                'performance_score': execution_result.get('performance_score', 0.0),
                'resource_efficiency': 0.0,
                'node_efficiency': 0.0,
                'overall_efficiency': 0.0
            }
            
            # Calculate resource efficiency
            allocated_resources = resource_allocation.allocated_resources
            total_allocated = sum(allocated_resources.values()) if allocated_resources else 1
            
            if execution_result.get('success', False):
                # Higher efficiency for successful executions with reasonable resource usage
                metrics['resource_efficiency'] = min(1.0, 1.0 / (total_allocated / 1000))
            else:
                # Lower efficiency for failed executions
                metrics['resource_efficiency'] = 0.1
            
            # Calculate node efficiency
            node_count = len(node_selection.selected_nodes)
            if node_count > 0:
                metrics['node_efficiency'] = node_selection.selection_confidence
            
            # Calculate overall efficiency
            metrics['overall_efficiency'] = (
                metrics['resource_efficiency'] * 0.4 +
                metrics['node_efficiency'] * 0.3 +
                metrics['performance_score'] * 0.3
            )
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating performance metrics: {e}")
            return {'execution_time': execution_time, 'success': False}
    
    async def _learn_from_execution(self, orchestration_result: OrchestrationResult):
        """Learn from execution results to improve future orchestration"""
        try:
            # Update resource manager with execution feedback
            await self.resource_manager.update_from_feedback(
                orchestration_result.ritual_id,
                orchestration_result.success,
                orchestration_result.performance_metrics
            )
            
            # Update load balancer with execution feedback
            await self.load_balancer.update_from_feedback(
                orchestration_result.ritual_id,
                orchestration_result.nodes_used,
                orchestration_result.success,
                orchestration_result.performance_metrics
            )
            
            # Update performance monitor
            await self.performance_monitor.record_execution(orchestration_result)
            
        except Exception as e:
            print(f"Error learning from execution: {e}")
    
    async def _should_optimize(self) -> bool:
        """Determine if optimization should be triggered"""
        try:
            # Check time-based optimization schedule
            now = datetime.now(timezone.utc)
            if now - self.last_optimization > self.optimization_schedule:
                return True
            
            # Check performance-based optimization triggers
            if len(self.execution_history) >= 10:
                recent_executions = self.execution_history[-10:]
                
                # Calculate recent performance metrics
                success_rate = sum(1 for e in recent_executions if e.success) / len(recent_executions)
                avg_response_time = np.mean([e.execution_time for e in recent_executions])
                avg_efficiency = np.mean([
                    e.performance_metrics.get('overall_efficiency', 0.0) 
                    for e in recent_executions
                ])
                
                # Trigger optimization if performance drops below thresholds
                if (success_rate < self.target_metrics['success_rate'] or
                    avg_response_time > self.target_metrics['avg_response_time'] or
                    avg_efficiency < self.target_metrics['resource_efficiency']):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking optimization trigger: {e}")
            return False
    
    async def _trigger_optimization(self) -> OptimizationResult:
        """Trigger system optimization using evolutionary algorithms"""
        try:
            # Prepare optimization data
            optimization_data = {
                'execution_history': [asdict(e) for e in self.execution_history[-50:]],  # Last 50 executions
                'current_performance': await self._calculate_current_performance(),
                'target_metrics': self.target_metrics,
                'system_state': asdict(await self.performance_monitor.get_current_metrics())
            }
            
            # Run optimization
            optimization_result = await self.evolution_engine.optimize_system(optimization_data)
            
            # Apply optimization results
            if optimization_result.success:
                await self._apply_optimization_results(optimization_result)
                self.last_optimization = datetime.now(timezone.utc)
            
            return optimization_result
            
        except Exception as e:
            print(f"Error triggering optimization: {e}")
            return OptimizationResult(
                success=False,
                optimization_type='system_optimization',
                improvements={},
                performance_gain=0.0,
                optimization_metadata={'error': str(e)}
            )
    
    async def _calculate_current_performance(self) -> Dict[str, float]:
        """Calculate current system performance metrics"""
        try:
            if not self.execution_history:
                return {'success_rate': 0.0, 'avg_response_time': 0.0, 'resource_efficiency': 0.0}
            
            recent_executions = self.execution_history[-20:]  # Last 20 executions
            
            success_rate = sum(1 for e in recent_executions if e.success) / len(recent_executions)
            avg_response_time = np.mean([e.execution_time for e in recent_executions])
            resource_efficiency = np.mean([
                e.performance_metrics.get('resource_efficiency', 0.0) 
                for e in recent_executions
            ])
            
            return {
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'resource_efficiency': resource_efficiency
            }
            
        except Exception as e:
            print(f"Error calculating current performance: {e}")
            return {'success_rate': 0.0, 'avg_response_time': 0.0, 'resource_efficiency': 0.0}
    
    async def _apply_optimization_results(self, optimization_result: OptimizationResult):
        """Apply optimization results to system components"""
        try:
            improvements = optimization_result.improvements
            
            # Apply resource manager optimizations
            if 'resource_manager' in improvements:
                await self.resource_manager.apply_optimizations(
                    improvements['resource_manager']
                )
            
            # Apply load balancer optimizations
            if 'load_balancer' in improvements:
                await self.load_balancer.apply_optimizations(
                    improvements['load_balancer']
                )
            
            # Apply orchestrator optimizations
            if 'orchestrator' in improvements:
                orchestrator_improvements = improvements['orchestrator']
                
                if 'learning_rate' in orchestrator_improvements:
                    self.learning_rate = orchestrator_improvements['learning_rate']
                
                if 'exploration_rate' in orchestrator_improvements:
                    self.exploration_rate = orchestrator_improvements['exploration_rate']
                
                if 'adaptation_threshold' in orchestrator_improvements:
                    self.adaptation_threshold = orchestrator_improvements['adaptation_threshold']
            
            print(f"Applied optimization improvements: {list(improvements.keys())}")
            
        except Exception as e:
            print(f"Error applying optimization results: {e}")
    
    async def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics and performance metrics"""
        try:
            current_performance = await self._calculate_current_performance()
            
            stats = {
                'total_executions': len(self.execution_history),
                'current_performance': current_performance,
                'target_metrics': self.target_metrics,
                'strategy': self.strategy.value,
                'last_optimization': self.last_optimization.isoformat(),
                'optimization_schedule_hours': self.optimization_schedule.total_seconds() / 3600,
                'adaptive_parameters': {
                    'learning_rate': self.learning_rate,
                    'exploration_rate': self.exploration_rate,
                    'adaptation_threshold': self.adaptation_threshold
                }
            }
            
            # Add recent execution statistics
            if self.execution_history:
                recent_executions = self.execution_history[-10:]
                stats['recent_executions'] = {
                    'count': len(recent_executions),
                    'success_rate': sum(1 for e in recent_executions if e.success) / len(recent_executions),
                    'avg_execution_time': np.mean([e.execution_time for e in recent_executions]),
                    'avg_performance_score': np.mean([
                        e.performance_metrics.get('performance_score', 0.0) 
                        for e in recent_executions
                    ])
                }
            
            return stats
            
        except Exception as e:
            print(f"Error getting orchestration stats: {e}")
            return {'error': str(e)}
    
    async def set_strategy(self, strategy: OrchestrationStrategy):
        """Set the orchestration strategy"""
        self.strategy = strategy
        print(f"Orchestration strategy set to: {strategy.value}")
    
    async def update_target_metrics(self, new_targets: Dict[str, float]):
        """Update target performance metrics"""
        self.target_metrics.update(new_targets)
        print(f"Updated target metrics: {self.target_metrics}")
    
    async def force_optimization(self) -> OptimizationResult:
        """Force immediate system optimization"""
        return await self._trigger_optimization()


# Factory function
def create_ritual_request(
    ritual_id: str,
    ritual_type: str,
    context: Dict[str, Any],
    parameters: Dict[str, Any],
    priority: int = 5,
    deadline: Optional[datetime] = None,
    resource_requirements: Optional[Dict[str, Any]] = None
) -> RitualRequest:
    """Factory function to create a ritual request"""
    return RitualRequest(
        ritual_id=ritual_id,
        ritual_type=ritual_type,
        context=context,
        parameters=parameters,
        priority=priority,
        deadline=deadline,
        resource_requirements=resource_requirements
    )
