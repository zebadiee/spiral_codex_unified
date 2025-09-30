
"""
Genetic Optimizer - Evolutionary algorithms for system improvement
"""

import asyncio
import json
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class OptimizationType(Enum):
    """Types of optimization"""
    SYSTEM_PARAMETERS = "system_parameters"
    RESOURCE_ALLOCATION = "resource_allocation"
    LOAD_BALANCING = "load_balancing"
    ORCHESTRATION = "orchestration"
    HYBRID = "hybrid"


@dataclass
class Individual:
    """Represents an individual in the genetic algorithm"""
    genes: Dict[str, float]
    fitness: float
    generation: int
    metadata: Dict[str, Any]


@dataclass
class OptimizationResult:
    """Result of evolutionary optimization"""
    success: bool
    optimization_type: str
    improvements: Dict[str, Any]
    performance_gain: float
    generations_evolved: int
    best_fitness: float
    optimization_metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class GeneticOptimizer:
    """
    Genetic Algorithm-based optimizer for system parameters
    Uses evolutionary algorithms to continuously improve system performance
    """
    
    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism_rate: float = 0.2
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_rate = elitism_rate
        
        # Evolution parameters
        self.max_generations = 100
        self.convergence_threshold = 0.001
        self.stagnation_limit = 10
        
        # Parameter bounds for different optimization types
        self.parameter_bounds = {
            'resource_manager': {
                'learning_rate': (0.01, 0.5),
                'epsilon': (0.01, 0.3),
                'discount_factor': (0.5, 0.99)
            },
            'load_balancer': {
                'exploration_factor': (0.5, 3.0)
            },
            'orchestrator': {
                'learning_rate': (0.01, 0.3),
                'exploration_rate': (0.05, 0.4),
                'adaptation_threshold': (0.5, 0.95)
            }
        }
        
        # Optimization history
        self.optimization_history: List[OptimizationResult] = []
        self.current_population: List[Individual] = []
        self.generation_count = 0
        
        # Performance tracking
        self.baseline_performance = {}
        self.best_individual = None
    
    async def optimize_system(self, optimization_data: Dict[str, Any]) -> OptimizationResult:
        """Run genetic algorithm optimization on system parameters"""
        try:
            optimization_type = optimization_data.get('optimization_type', 'system_parameters')
            
            # Set baseline performance
            self.baseline_performance = optimization_data.get('current_performance', {})
            target_metrics = optimization_data.get('target_metrics', {})
            
            # Initialize population
            await self._initialize_population(optimization_type, optimization_data)
            
            # Evolution loop
            best_fitness_history = []
            stagnation_count = 0
            
            for generation in range(self.max_generations):
                self.generation_count = generation
                
                # Evaluate fitness for all individuals
                await self._evaluate_population(optimization_data)
                
                # Track best fitness
                current_best_fitness = max(ind.fitness for ind in self.current_population)
                best_fitness_history.append(current_best_fitness)
                
                # Check for convergence
                if len(best_fitness_history) > 1:
                    improvement = current_best_fitness - best_fitness_history[-2]
                    if improvement < self.convergence_threshold:
                        stagnation_count += 1
                    else:
                        stagnation_count = 0
                    
                    if stagnation_count >= self.stagnation_limit:
                        print(f"Convergence reached at generation {generation}")
                        break
                
                # Create next generation
                await self._create_next_generation()
            
            # Get best individual
            self.best_individual = max(self.current_population, key=lambda x: x.fitness)
            
            # Calculate improvements
            improvements = await self._extract_improvements(self.best_individual, optimization_type)
            performance_gain = await self._calculate_performance_gain(self.best_individual)
            
            # Create optimization result
            result = OptimizationResult(
                success=True,
                optimization_type=optimization_type,
                improvements=improvements,
                performance_gain=performance_gain,
                generations_evolved=self.generation_count + 1,
                best_fitness=self.best_individual.fitness,
                optimization_metadata={
                    'population_size': self.population_size,
                    'final_generation': self.generation_count,
                    'convergence_history': best_fitness_history,
                    'baseline_performance': self.baseline_performance
                }
            )
            
            # Store optimization history
            self.optimization_history.append(result)
            
            return result
            
        except Exception as e:
            print(f"Error in genetic optimization: {e}")
            return OptimizationResult(
                success=False,
                optimization_type=optimization_data.get('optimization_type', 'unknown'),
                improvements={},
                performance_gain=0.0,
                generations_evolved=0,
                best_fitness=0.0,
                optimization_metadata={'error': str(e)}
            )
    
    async def _initialize_population(self, optimization_type: str, optimization_data: Dict[str, Any]):
        """Initialize the population with random individuals"""
        try:
            self.current_population = []
            
            for i in range(self.population_size):
                # Generate random genes within bounds
                genes = {}
                
                if optimization_type in ['system_parameters', 'hybrid']:
                    # Include parameters from all components
                    for component, params in self.parameter_bounds.items():
                        for param, (min_val, max_val) in params.items():
                            genes[f"{component}_{param}"] = random.uniform(min_val, max_val)
                else:
                    # Include parameters for specific component
                    if optimization_type == 'resource_allocation' and 'resource_manager' in self.parameter_bounds:
                        for param, (min_val, max_val) in self.parameter_bounds['resource_manager'].items():
                            genes[f"resource_manager_{param}"] = random.uniform(min_val, max_val)
                    elif optimization_type == 'load_balancing' and 'load_balancer' in self.parameter_bounds:
                        for param, (min_val, max_val) in self.parameter_bounds['load_balancer'].items():
                            genes[f"load_balancer_{param}"] = random.uniform(min_val, max_val)
                    elif optimization_type == 'orchestration' and 'orchestrator' in self.parameter_bounds:
                        for param, (min_val, max_val) in self.parameter_bounds['orchestrator'].items():
                            genes[f"orchestrator_{param}"] = random.uniform(min_val, max_val)
                
                # Create individual
                individual = Individual(
                    genes=genes,
                    fitness=0.0,
                    generation=0,
                    metadata={'individual_id': i}
                )
                
                self.current_population.append(individual)
            
        except Exception as e:
            print(f"Error initializing population: {e}")
    
    async def _evaluate_population(self, optimization_data: Dict[str, Any]):
        """Evaluate fitness for all individuals in the population"""
        try:
            execution_history = optimization_data.get('execution_history', [])
            target_metrics = optimization_data.get('target_metrics', {})
            
            for individual in self.current_population:
                individual.fitness = await self._calculate_fitness(
                    individual, execution_history, target_metrics
                )
            
        except Exception as e:
            print(f"Error evaluating population: {e}")
    
    async def _calculate_fitness(
        self,
        individual: Individual,
        execution_history: List[Dict[str, Any]],
        target_metrics: Dict[str, float]
    ) -> float:
        """Calculate fitness score for an individual"""
        try:
            # Simulate performance with individual's parameters
            simulated_performance = await self._simulate_performance(individual, execution_history)
            
            # Calculate fitness based on how well it meets target metrics
            fitness = 0.0
            metric_count = 0
            
            for metric, target_value in target_metrics.items():
                if metric in simulated_performance:
                    actual_value = simulated_performance[metric]
                    
                    # Calculate normalized score (closer to target = higher fitness)
                    if target_value > 0:
                        if metric in ['success_rate', 'resource_efficiency']:
                            # Higher is better
                            score = min(1.0, actual_value / target_value)
                        elif metric in ['avg_response_time']:
                            # Lower is better
                            score = min(1.0, target_value / actual_value) if actual_value > 0 else 0.0
                        else:
                            # General case: closer to target is better
                            diff = abs(actual_value - target_value)
                            max_diff = max(target_value, 1.0)
                            score = max(0.0, 1.0 - (diff / max_diff))
                        
                        fitness += score
                        metric_count += 1
            
            # Average fitness across all metrics
            if metric_count > 0:
                fitness /= metric_count
            else:
                fitness = 0.5  # Default fitness if no metrics
            
            # Add bonus for parameter diversity (avoid local optima)
            diversity_bonus = self._calculate_diversity_bonus(individual)
            fitness += diversity_bonus * 0.1
            
            return max(0.0, min(1.0, fitness))
            
        except Exception as e:
            print(f"Error calculating fitness: {e}")
            return 0.0
    
    async def _simulate_performance(
        self,
        individual: Individual,
        execution_history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Simulate system performance with individual's parameters"""
        try:
            # Extract parameter adjustments from genes
            param_adjustments = {}
            
            for gene_name, gene_value in individual.genes.items():
                if 'learning_rate' in gene_name:
                    param_adjustments['learning_rate_factor'] = gene_value / 0.1  # Normalize to base learning rate
                elif 'epsilon' in gene_name:
                    param_adjustments['exploration_factor'] = gene_value / 0.1
                elif 'adaptation_threshold' in gene_name:
                    param_adjustments['adaptation_factor'] = gene_value / 0.8
            
            # Simulate performance based on recent execution history
            if not execution_history:
                return {'success_rate': 0.8, 'avg_response_time': 2.0, 'resource_efficiency': 0.7}
            
            recent_executions = execution_history[-20:]  # Last 20 executions
            
            # Base performance from history
            base_success_rate = sum(1 for e in recent_executions if e.get('success', False)) / len(recent_executions)
            base_response_time = np.mean([e.get('execution_time', 2.0) for e in recent_executions])
            base_efficiency = np.mean([
                e.get('performance_metrics', {}).get('overall_efficiency', 0.5) 
                for e in recent_executions
            ])
            
            # Apply parameter adjustments
            learning_factor = param_adjustments.get('learning_rate_factor', 1.0)
            exploration_factor = param_adjustments.get('exploration_factor', 1.0)
            adaptation_factor = param_adjustments.get('adaptation_factor', 1.0)
            
            # Simulate improvements
            success_rate = min(1.0, base_success_rate * (1.0 + learning_factor * 0.1))
            response_time = base_response_time * (1.0 - exploration_factor * 0.05)
            efficiency = min(1.0, base_efficiency * (1.0 + adaptation_factor * 0.1))
            
            return {
                'success_rate': success_rate,
                'avg_response_time': max(0.1, response_time),
                'resource_efficiency': efficiency
            }
            
        except Exception as e:
            print(f"Error simulating performance: {e}")
            return {'success_rate': 0.5, 'avg_response_time': 2.0, 'resource_efficiency': 0.5}
    
    def _calculate_diversity_bonus(self, individual: Individual) -> float:
        """Calculate diversity bonus to encourage exploration"""
        try:
            if not self.current_population or len(self.current_population) < 2:
                return 0.0
            
            # Calculate average distance from other individuals
            total_distance = 0.0
            comparison_count = 0
            
            for other in self.current_population:
                if other != individual:
                    distance = self._calculate_gene_distance(individual.genes, other.genes)
                    total_distance += distance
                    comparison_count += 1
            
            if comparison_count > 0:
                avg_distance = total_distance / comparison_count
                return min(0.2, avg_distance)  # Cap diversity bonus at 0.2
            
            return 0.0
            
        except Exception as e:
            print(f"Error calculating diversity bonus: {e}")
            return 0.0
    
    def _calculate_gene_distance(self, genes1: Dict[str, float], genes2: Dict[str, float]) -> float:
        """Calculate Euclidean distance between two gene sets"""
        try:
            common_genes = set(genes1.keys()) & set(genes2.keys())
            
            if not common_genes:
                return 0.0
            
            distance = 0.0
            for gene in common_genes:
                distance += (genes1[gene] - genes2[gene]) ** 2
            
            return np.sqrt(distance / len(common_genes))
            
        except Exception as e:
            print(f"Error calculating gene distance: {e}")
            return 0.0
    
    async def _create_next_generation(self):
        """Create the next generation using selection, crossover, and mutation"""
        try:
            # Sort population by fitness (descending)
            self.current_population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Elitism: keep top individuals
            elite_count = int(self.population_size * self.elitism_rate)
            next_generation = self.current_population[:elite_count].copy()
            
            # Update generation number for elite individuals
            for individual in next_generation:
                individual.generation = self.generation_count + 1
            
            # Generate offspring to fill the rest of the population
            while len(next_generation) < self.population_size:
                # Selection
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                # Mutation
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                # Add children to next generation
                child1.generation = self.generation_count + 1
                child2.generation = self.generation_count + 1
                
                next_generation.extend([child1, child2])
            
            # Trim to exact population size
            self.current_population = next_generation[:self.population_size]
            
        except Exception as e:
            print(f"Error creating next generation: {e}")
    
    def _tournament_selection(self, tournament_size: int = 3) -> Individual:
        """Select individual using tournament selection"""
        try:
            tournament = random.sample(self.current_population, min(tournament_size, len(self.current_population)))
            return max(tournament, key=lambda x: x.fitness)
            
        except Exception as e:
            print(f"Error in tournament selection: {e}")
            return random.choice(self.current_population)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Perform crossover between two parents"""
        try:
            # Single-point crossover
            common_genes = set(parent1.genes.keys()) & set(parent2.genes.keys())
            
            if not common_genes:
                return parent1, parent2
            
            genes_list = list(common_genes)
            crossover_point = random.randint(1, len(genes_list) - 1)
            
            # Create children
            child1_genes = {}
            child2_genes = {}
            
            for i, gene in enumerate(genes_list):
                if i < crossover_point:
                    child1_genes[gene] = parent1.genes[gene]
                    child2_genes[gene] = parent2.genes[gene]
                else:
                    child1_genes[gene] = parent2.genes[gene]
                    child2_genes[gene] = parent1.genes[gene]
            
            # Add any unique genes
            for gene in parent1.genes:
                if gene not in child1_genes:
                    child1_genes[gene] = parent1.genes[gene]
            
            for gene in parent2.genes:
                if gene not in child2_genes:
                    child2_genes[gene] = parent2.genes[gene]
            
            child1 = Individual(
                genes=child1_genes,
                fitness=0.0,
                generation=0,
                metadata={'parents': [parent1.metadata.get('individual_id'), parent2.metadata.get('individual_id')]}
            )
            
            child2 = Individual(
                genes=child2_genes,
                fitness=0.0,
                generation=0,
                metadata={'parents': [parent1.metadata.get('individual_id'), parent2.metadata.get('individual_id')]}
            )
            
            return child1, child2
            
        except Exception as e:
            print(f"Error in crossover: {e}")
            return parent1, parent2
    
    def _mutate(self, individual: Individual) -> Individual:
        """Apply mutation to an individual"""
        try:
            mutated_genes = individual.genes.copy()
            
            for gene_name, gene_value in mutated_genes.items():
                if random.random() < self.mutation_rate:
                    # Find parameter bounds
                    bounds = None
                    for component, params in self.parameter_bounds.items():
                        for param, param_bounds in params.items():
                            if f"{component}_{param}" == gene_name:
                                bounds = param_bounds
                                break
                        if bounds:
                            break
                    
                    if bounds:
                        min_val, max_val = bounds
                        # Gaussian mutation with bounds checking
                        mutation_strength = (max_val - min_val) * 0.1
                        mutated_value = gene_value + random.gauss(0, mutation_strength)
                        mutated_genes[gene_name] = max(min_val, min(max_val, mutated_value))
            
            return Individual(
                genes=mutated_genes,
                fitness=0.0,
                generation=individual.generation,
                metadata=individual.metadata.copy()
            )
            
        except Exception as e:
            print(f"Error in mutation: {e}")
            return individual
    
    async def _extract_improvements(self, best_individual: Individual, optimization_type: str) -> Dict[str, Any]:
        """Extract improvements from the best individual"""
        try:
            improvements = {}
            
            for gene_name, gene_value in best_individual.genes.items():
                # Parse gene name to extract component and parameter
                parts = gene_name.split('_', 1)
                if len(parts) == 2:
                    component, parameter = parts
                    
                    if component not in improvements:
                        improvements[component] = {}
                    
                    improvements[component][parameter] = gene_value
            
            return improvements
            
        except Exception as e:
            print(f"Error extracting improvements: {e}")
            return {}
    
    async def _calculate_performance_gain(self, best_individual: Individual) -> float:
        """Calculate performance gain from optimization"""
        try:
            if not self.baseline_performance:
                return 0.0
            
            # Estimate performance gain based on fitness improvement
            baseline_fitness = 0.5  # Assume baseline fitness of 0.5
            performance_gain = (best_individual.fitness - baseline_fitness) * 100  # Convert to percentage
            
            return max(0.0, performance_gain)
            
        except Exception as e:
            print(f"Error calculating performance gain: {e}")
            return 0.0
    
    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        try:
            return {
                'total_optimizations': len(self.optimization_history),
                'current_generation': self.generation_count,
                'population_size': self.population_size,
                'genetic_parameters': {
                    'mutation_rate': self.mutation_rate,
                    'crossover_rate': self.crossover_rate,
                    'elitism_rate': self.elitism_rate
                },
                'evolution_parameters': {
                    'max_generations': self.max_generations,
                    'convergence_threshold': self.convergence_threshold,
                    'stagnation_limit': self.stagnation_limit
                },
                'best_individual': {
                    'fitness': self.best_individual.fitness if self.best_individual else 0.0,
                    'generation': self.best_individual.generation if self.best_individual else 0,
                    'genes': self.best_individual.genes if self.best_individual else {}
                } if self.best_individual else None,
                'recent_optimizations': [
                    {
                        'optimization_type': opt.optimization_type,
                        'performance_gain': opt.performance_gain,
                        'generations_evolved': opt.generations_evolved,
                        'timestamp': opt.timestamp.isoformat()
                    }
                    for opt in self.optimization_history[-5:]  # Last 5 optimizations
                ]
            }
            
        except Exception as e:
            print(f"Error getting optimization stats: {e}")
            return {'error': str(e)}
    
    async def set_parameters(
        self,
        population_size: Optional[int] = None,
        mutation_rate: Optional[float] = None,
        crossover_rate: Optional[float] = None,
        elitism_rate: Optional[float] = None
    ):
        """Update genetic algorithm parameters"""
        try:
            if population_size is not None:
                self.population_size = max(10, min(200, population_size))
            
            if mutation_rate is not None:
                self.mutation_rate = max(0.01, min(0.5, mutation_rate))
            
            if crossover_rate is not None:
                self.crossover_rate = max(0.1, min(1.0, crossover_rate))
            
            if elitism_rate is not None:
                self.elitism_rate = max(0.0, min(0.5, elitism_rate))
            
            print("Updated genetic algorithm parameters")
            
        except Exception as e:
            print(f"Error setting parameters: {e}")
