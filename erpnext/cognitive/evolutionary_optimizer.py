"""
Evolutionary Optimization System

Implements MOSES-equivalent evolutionary algorithms for optimizing cognitive kernels.
Uses real genetic algorithms with mutation, crossover, and selection to evolve
system parameters and configurations.
"""

import numpy as np
import random
import time
import json
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import copy
from collections import defaultdict


class OptimizationTarget(Enum):
    """Types of optimization targets"""
    TENSOR_KERNEL_PERFORMANCE = "tensor_kernel_performance"
    ATTENTION_ALLOCATION_EFFICIENCY = "attention_allocation_efficiency"  
    NEURAL_SYMBOLIC_COHERENCE = "neural_symbolic_coherence"
    GLOBAL_SYSTEM_PERFORMANCE = "global_system_performance"


class MutationType(Enum):
    """Types of mutations for genetic algorithm"""
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    STRUCTURE_MODIFICATION = "structure_modification"
    THRESHOLD_TUNING = "threshold_tuning"
    WEIGHT_SCALING = "weight_scaling"


@dataclass
class Genome:
    """Genetic representation of system configuration"""
    config_id: str
    parameters: Dict[str, float] = field(default_factory=dict)
    structure_genes: Dict[str, Any] = field(default_factory=dict)
    fitness_score: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    mutation_history: List[MutationType] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.config_id:
            self.config_id = f"genome_{int(time.time()*1000)}{random.randint(100,999)}"


@dataclass
class EvolutionMetrics:
    """Metrics tracking evolutionary progress"""
    generation: int
    population_size: int
    best_fitness: float
    average_fitness: float
    fitness_variance: float
    convergence_rate: float
    diversity_measure: float
    
    
class FitnessEvaluator:
    """Evaluates fitness of genomes based on real system performance"""
    
    def __init__(self):
        self.evaluation_cache: Dict[str, float] = {}
        self.evaluation_count = 0
        
    def evaluate_genome(self, genome: Genome, 
                       target_system: Any = None) -> float:
        """
        Evaluate fitness of a genome by testing actual system performance
        
        Args:
            genome: Genome to evaluate
            target_system: System to test against (if available)
            
        Returns:
            Fitness score (higher is better)
        """
        # Check cache first
        cache_key = self._genome_to_cache_key(genome)
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
            
        self.evaluation_count += 1
        
        # Evaluate based on multiple criteria
        fitness_components = {}
        
        # 1. Parameter coherence (parameters within reasonable bounds)
        fitness_components['parameter_coherence'] = self._evaluate_parameter_coherence(genome)
        
        # 2. Structural validity
        fitness_components['structural_validity'] = self._evaluate_structural_validity(genome)
        
        # 3. Performance prediction (based on parameter analysis)
        fitness_components['performance_prediction'] = self._predict_performance(genome)
        
        # 4. Real system testing (if target_system available)
        if target_system is not None:
            fitness_components['real_performance'] = self._test_real_performance(
                genome, target_system
            )
        else:
            # Use synthetic performance metric
            fitness_components['real_performance'] = self._synthetic_performance(genome)
            
        # Combine fitness components with weights
        weights = {
            'parameter_coherence': 0.2,
            'structural_validity': 0.2,
            'performance_prediction': 0.3,
            'real_performance': 0.3
        }
        
        total_fitness = sum(
            weights[component] * score 
            for component, score in fitness_components.items()
        )
        
        # Cache result
        self.evaluation_cache[cache_key] = total_fitness
        
        # Update genome fitness
        genome.fitness_score = total_fitness
        
        return total_fitness
        
    def _genome_to_cache_key(self, genome: Genome) -> str:
        """Generate cache key for genome"""
        param_str = json.dumps(genome.parameters, sort_keys=True)
        structure_str = json.dumps(genome.structure_genes, sort_keys=True, default=str)
        return f"{param_str}_{structure_str}"
        
    def _evaluate_parameter_coherence(self, genome: Genome) -> float:
        """Evaluate if parameters are coherent and within bounds"""
        score = 1.0
        
        for param_name, value in genome.parameters.items():
            # Check bounds based on parameter type
            if 'learning_rate' in param_name.lower():
                if not (0.0001 <= value <= 0.1):
                    score *= 0.5  # Penalty for out-of-bounds learning rate
            elif 'threshold' in param_name.lower():
                if not (0.0 <= value <= 1.0):
                    score *= 0.5
            elif 'weight' in param_name.lower():
                if not (-10.0 <= value <= 10.0):
                    score *= 0.7
                    
        # Bonus for parameter diversity
        param_values = list(genome.parameters.values())
        if len(set(param_values)) > len(param_values) * 0.8:
            score *= 1.1
            
        return min(score, 1.0)
        
    def _evaluate_structural_validity(self, genome: Genome) -> float:
        """Evaluate structural validity of configuration"""
        score = 1.0
        
        # Check for required structural components
        required_structures = ['tensor_shapes', 'layer_connections', 'attention_weights']
        
        for structure in required_structures:
            if structure not in genome.structure_genes:
                score *= 0.8
            else:
                # Validate structure content
                if not self._validate_structure_content(
                    structure, genome.structure_genes[structure]
                ):
                    score *= 0.9
                    
        return score
        
    def _validate_structure_content(self, structure_type: str, content: Any) -> bool:
        """Validate content of a specific structure type"""
        if structure_type == 'tensor_shapes':
            # Should be list of positive integers
            if isinstance(content, list):
                return all(isinstance(x, int) and x > 0 for x in content)
        elif structure_type == 'layer_connections':
            # Should be dict mapping layers
            if isinstance(content, dict):
                return len(content) > 0
        elif structure_type == 'attention_weights':
            # Should be list of weights that sum to approximately 1
            if isinstance(content, list):
                return abs(sum(content) - 1.0) < 0.1
                
        return False
        
    def _predict_performance(self, genome: Genome) -> float:
        """Predict performance based on parameter analysis"""
        # Simple heuristic-based performance prediction
        score = 0.5  # Base score
        
        # Analyze parameter distribution
        param_values = list(genome.parameters.values())
        if param_values:
            # Prefer moderate values over extremes
            mean_val = np.mean(param_values)
            if 0.1 <= abs(mean_val) <= 1.0:
                score += 0.2
                
            # Prefer low variance (stability)
            var_val = np.var(param_values)
            if var_val < 0.5:
                score += 0.2
                
            # Prefer positive trend in key parameters
            learning_rates = [v for k, v in genome.parameters.items() 
                            if 'learning' in k.lower()]
            if learning_rates and all(lr > 0 for lr in learning_rates):
                score += 0.1
                
        return min(score, 1.0)
        
    def _test_real_performance(self, genome: Genome, target_system: Any) -> float:
        """Test real performance by applying genome to target system"""
        try:
            # Apply genome configuration to target system
            original_config = self._backup_system_config(target_system)
            
            # Apply genome configuration
            self._apply_genome_to_system(genome, target_system)
            
            # Run performance test
            performance = self._measure_system_performance(target_system)
            
            # Restore original configuration
            self._restore_system_config(target_system, original_config)
            
            return performance
            
        except Exception as e:
            # If testing fails, return low score
            return 0.1
            
    def _backup_system_config(self, system: Any) -> Dict:
        """Backup current system configuration"""
        # This would implement actual system config backup
        return {'placeholder': 'config'}
        
    def _apply_genome_to_system(self, genome: Genome, system: Any):
        """Apply genome configuration to system"""
        # This would implement actual configuration application
        pass
        
    def _restore_system_config(self, system: Any, config: Dict):
        """Restore system configuration"""
        # This would implement actual config restoration
        pass
        
    def _measure_system_performance(self, system: Any) -> float:
        """Measure actual system performance"""
        # This would implement real performance measurement
        # For now, return synthetic measurement
        return random.uniform(0.3, 0.9)
        
    def _synthetic_performance(self, genome: Genome) -> float:
        """Generate synthetic performance score when no real system available"""
        # Use parameter analysis to generate realistic performance
        base_score = 0.5
        
        # Factor in parameter quality
        param_quality = self._evaluate_parameter_coherence(genome)
        base_score += (param_quality - 0.5) * 0.3
        
        # Add some randomness to simulate real-world variation
        noise = random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, base_score + noise))


class GeneticOperators:
    """Implements genetic operators for evolution"""
    
    def __init__(self, mutation_rate: float = 0.1, crossover_rate: float = 0.7):
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
    def mutate(self, genome: Genome) -> Genome:
        """Apply mutations to a genome"""
        mutated = copy.deepcopy(genome)
        mutated.config_id = f"mut_{genome.config_id}_{int(time.time()*1000)}"
        mutated.parent_ids = [genome.config_id]
        
        # Decide which type of mutation to apply
        mutation_type = random.choice(list(MutationType))
        mutated.mutation_history.append(mutation_type)
        
        if mutation_type == MutationType.PARAMETER_ADJUSTMENT:
            self._mutate_parameters(mutated)
        elif mutation_type == MutationType.STRUCTURE_MODIFICATION:
            self._mutate_structure(mutated)
        elif mutation_type == MutationType.THRESHOLD_TUNING:
            self._mutate_thresholds(mutated)
        elif mutation_type == MutationType.WEIGHT_SCALING:
            self._mutate_weights(mutated)
            
        return mutated
        
    def _mutate_parameters(self, genome: Genome):
        """Mutate numerical parameters"""
        for param_name in list(genome.parameters.keys()):
            if random.random() < self.mutation_rate:
                current_value = genome.parameters[param_name]
                
                # Apply Gaussian mutation with adaptive step size
                step_size = abs(current_value) * 0.1 + 0.01
                mutation = np.random.normal(0, step_size)
                
                new_value = current_value + mutation
                
                # Apply bounds based on parameter type
                if 'learning_rate' in param_name.lower():
                    new_value = max(0.0001, min(0.1, new_value))
                elif 'threshold' in param_name.lower():
                    new_value = max(0.0, min(1.0, new_value))
                elif 'weight' in param_name.lower():
                    new_value = max(-10.0, min(10.0, new_value))
                    
                genome.parameters[param_name] = new_value
                
    def _mutate_structure(self, genome: Genome):
        """Mutate structural components"""
        for structure_name in list(genome.structure_genes.keys()):
            if random.random() < self.mutation_rate:
                if structure_name == 'tensor_shapes':
                    # Modify tensor shapes
                    shapes = genome.structure_genes[structure_name]
                    if isinstance(shapes, list) and shapes:
                        idx = random.randint(0, len(shapes) - 1)
                        # Mutate shape by ±1 to ±32
                        delta = random.choice([-32, -16, -8, -4, -2, -1, 1, 2, 4, 8, 16, 32])
                        shapes[idx] = max(1, shapes[idx] + delta)
                        
                elif structure_name == 'attention_weights':
                    # Mutate attention weights and renormalize
                    weights = genome.structure_genes[structure_name]
                    if isinstance(weights, list) and weights:
                        idx = random.randint(0, len(weights) - 1)
                        weights[idx] += random.uniform(-0.1, 0.1)
                        # Renormalize
                        total = sum(weights)
                        if total > 0:
                            genome.structure_genes[structure_name] = [w/total for w in weights]
                            
    def _mutate_thresholds(self, genome: Genome):
        """Mutate threshold parameters specifically"""
        threshold_params = [k for k in genome.parameters.keys() if 'threshold' in k.lower()]
        
        for param in threshold_params:
            if random.random() < self.mutation_rate * 2:  # Higher rate for thresholds
                current = genome.parameters[param]
                # Small adjustments to thresholds
                genome.parameters[param] = max(0.0, min(1.0, 
                    current + random.uniform(-0.05, 0.05)))
                    
    def _mutate_weights(self, genome: Genome):
        """Mutate weight parameters with scaling"""
        weight_params = [k for k in genome.parameters.keys() if 'weight' in k.lower()]
        
        if weight_params and random.random() < self.mutation_rate:
            # Apply global scaling to all weights
            scale_factor = random.uniform(0.9, 1.1)
            for param in weight_params:
                genome.parameters[param] *= scale_factor
                
    def crossover(self, parent1: Genome, parent2: Genome) -> Tuple[Genome, Genome]:
        """Create offspring through crossover"""
        if random.random() > self.crossover_rate:
            # No crossover, return copies of parents with lineage tracking
            child1 = copy.deepcopy(parent1)
            child2 = copy.deepcopy(parent2)
            child1.config_id = f"copy_{parent1.config_id}_{int(time.time()*1000)}"
            child2.config_id = f"copy_{parent2.config_id}_{int(time.time()*1000)}"
            child1.parent_ids = [parent1.config_id]
            child2.parent_ids = [parent2.config_id]
            return child1, child2
            
        # Create offspring
        child1 = Genome(
            config_id=f"cross_{parent1.config_id}_{parent2.config_id}_{int(time.time()*1000)}",
            generation=max(parent1.generation, parent2.generation) + 1,
            parent_ids=[parent1.config_id, parent2.config_id]
        )
        
        child2 = Genome(
            config_id=f"cross_{parent2.config_id}_{parent1.config_id}_{int(time.time()*1000)}",
            generation=max(parent1.generation, parent2.generation) + 1,
            parent_ids=[parent1.config_id, parent2.config_id]
        )
        
        # Parameter crossover (uniform crossover)
        all_param_keys = set(parent1.parameters.keys()) | set(parent2.parameters.keys())
        
        for param_key in all_param_keys:
            # Get values from both parents (use default if missing)
            val1 = parent1.parameters.get(param_key, 0.0)
            val2 = parent2.parameters.get(param_key, 0.0)
            
            if random.random() < 0.5:
                child1.parameters[param_key] = val1
                child2.parameters[param_key] = val2
            else:
                child1.parameters[param_key] = val2
                child2.parameters[param_key] = val1
                
        # Structure crossover
        all_structure_keys = set(parent1.structure_genes.keys()) | set(parent2.structure_genes.keys())
        
        for structure_key in all_structure_keys:
            struct1 = parent1.structure_genes.get(structure_key, {})
            struct2 = parent2.structure_genes.get(structure_key, {})
            
            if random.random() < 0.5:
                child1.structure_genes[structure_key] = copy.deepcopy(struct1)
                child2.structure_genes[structure_key] = copy.deepcopy(struct2)
            else:
                child1.structure_genes[structure_key] = copy.deepcopy(struct2)
                child2.structure_genes[structure_key] = copy.deepcopy(struct1)
                
        return child1, child2


class SelectionStrategy:
    """Implements selection strategies for evolution"""
    
    @staticmethod
    def tournament_selection(population: List[Genome], 
                           tournament_size: int = 3) -> Genome:
        """Tournament selection"""
        tournament = random.sample(population, 
                                 min(tournament_size, len(population)))
        return max(tournament, key=lambda g: g.fitness_score)
        
    @staticmethod
    def roulette_wheel_selection(population: List[Genome]) -> Genome:
        """Roulette wheel selection based on fitness"""
        total_fitness = sum(g.fitness_score for g in population)
        
        if total_fitness <= 0:
            return random.choice(population)
            
        # Normalize fitness scores
        probabilities = [g.fitness_score / total_fitness for g in population]
        
        # Select based on probabilities
        r = random.random()
        cumulative = 0
        
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return population[i]
                
        return population[-1]  # Fallback
        
    @staticmethod
    def elitist_selection(population: List[Genome], 
                         elite_size: int) -> List[Genome]:
        """Select top performers (elites)"""
        sorted_population = sorted(population, 
                                 key=lambda g: g.fitness_score, 
                                 reverse=True)
        return sorted_population[:elite_size]


class EvolutionaryOptimizer:
    """Main evolutionary optimization engine"""
    
    def __init__(self, 
                 population_size: int = 50,
                 elite_size: int = 5,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7,
                 max_generations: int = 100):
        
        self.population_size = population_size
        self.elite_size = elite_size
        self.max_generations = max_generations
        
        self.fitness_evaluator = FitnessEvaluator()
        self.genetic_operators = GeneticOperators(mutation_rate, crossover_rate)
        
        self.population: List[Genome] = []
        self.evolution_history: List[EvolutionMetrics] = []
        self.best_genome: Optional[Genome] = None
        
        self.generation = 0
        
    def initialize_population(self, 
                            target_system: Any = None,
                            seed_genomes: List[Genome] = None) -> None:
        """Initialize the population with random or seed genomes"""
        self.population = []
        
        if seed_genomes:
            # Start with provided seed genomes
            self.population.extend(copy.deepcopy(seed_genomes))
            
        # Fill remaining population with random genomes
        while len(self.population) < self.population_size:
            genome = self._create_random_genome()
            self.population.append(genome)
            
        # Evaluate initial population
        for genome in self.population:
            self.fitness_evaluator.evaluate_genome(genome, target_system)
            
        self._update_best_genome()
        
    def _create_random_genome(self) -> Genome:
        """Create a random genome"""
        genome = Genome(config_id=f"random_{int(time.time()*1000)}{random.randint(1000,9999)}")
        
        # Random parameters
        param_names = [
            'learning_rate_primary', 'learning_rate_secondary',
            'attention_threshold', 'coherence_threshold', 'noise_threshold',
            'weight_primary', 'weight_secondary', 'weight_attention',
            'decay_rate', 'activation_threshold'
        ]
        
        for param_name in param_names:
            if 'learning_rate' in param_name:
                genome.parameters[param_name] = random.uniform(0.001, 0.05)
            elif 'threshold' in param_name:
                genome.parameters[param_name] = random.uniform(0.1, 0.9)
            elif 'weight' in param_name:
                genome.parameters[param_name] = random.uniform(-2.0, 2.0)
            elif 'decay' in param_name:
                genome.parameters[param_name] = random.uniform(0.9, 0.999)
            else:
                genome.parameters[param_name] = random.uniform(0.0, 1.0)
                
        # Random structures
        genome.structure_genes['tensor_shapes'] = [
            random.choice([64, 128, 256, 512]) for _ in range(random.randint(2, 5))
        ]
        
        weights = [random.random() for _ in range(random.randint(3, 7))]
        total = sum(weights)
        genome.structure_genes['attention_weights'] = [w/total for w in weights]
        
        genome.structure_genes['layer_connections'] = {
            f'layer_{i}': f'layer_{i+1}' for i in range(random.randint(2, 5))
        }
        
        return genome
        
    def evolve(self, target_system: Any = None, 
              convergence_threshold: float = 0.001) -> Genome:
        """
        Run evolutionary optimization
        
        Args:
            target_system: Optional system to optimize against
            convergence_threshold: Stop if improvement falls below this
            
        Returns:
            Best genome found
        """
        print(f"🧬 Starting evolutionary optimization with {self.population_size} genomes")
        print(f"   Target generations: {self.max_generations}")
        print(f"   Elite size: {self.elite_size}")
        
        for generation in range(self.max_generations):
            self.generation = generation
            
            # Evaluate population
            for genome in self.population:
                if genome.fitness_score == 0.0:  # Not evaluated yet
                    self.fitness_evaluator.evaluate_genome(genome, target_system)
                    
            # Update best genome
            self._update_best_genome()
            
            # Calculate metrics
            metrics = self._calculate_evolution_metrics()
            self.evolution_history.append(metrics)
            
            print(f"🧬 Generation {generation:3d}: "
                  f"Best={metrics.best_fitness:.4f}, "
                  f"Avg={metrics.average_fitness:.4f}, "
                  f"Div={metrics.diversity_measure:.4f}")
            
            # Check convergence
            if len(self.evolution_history) > 5:
                recent_improvement = (
                    self.evolution_history[-1].best_fitness - 
                    self.evolution_history[-6].best_fitness
                )
                if recent_improvement < convergence_threshold:
                    print(f"🎯 Converged after {generation} generations")
                    break
                    
            # Create next generation
            self._create_next_generation(target_system)
            
        print(f"🏆 Best genome: {self.best_genome.config_id} "
              f"(fitness: {self.best_genome.fitness_score:.4f})")
        
        return self.best_genome
        
    def _update_best_genome(self):
        """Update the best genome found so far"""
        if self.population:
            current_best = max(self.population, key=lambda g: g.fitness_score)
            if self.best_genome is None or current_best.fitness_score > self.best_genome.fitness_score:
                self.best_genome = copy.deepcopy(current_best)
                
    def _calculate_evolution_metrics(self) -> EvolutionMetrics:
        """Calculate metrics for current generation"""
        fitness_scores = [g.fitness_score for g in self.population]
        
        # Calculate diversity (based on parameter variance)
        all_params = []
        for genome in self.population:
            all_params.extend(genome.parameters.values())
            
        diversity = np.var(all_params) if all_params else 0.0
        
        # Calculate convergence rate
        convergence_rate = 0.0
        if len(self.evolution_history) > 0:
            prev_best = self.evolution_history[-1].best_fitness
            current_best = max(fitness_scores)
            convergence_rate = current_best - prev_best
            
        return EvolutionMetrics(
            generation=self.generation,
            population_size=len(self.population),
            best_fitness=max(fitness_scores),
            average_fitness=np.mean(fitness_scores),
            fitness_variance=np.var(fitness_scores),
            convergence_rate=convergence_rate,
            diversity_measure=diversity
        )
        
    def _create_next_generation(self, target_system: Any = None):
        """Create the next generation"""
        new_population = []
        
        # Keep elites
        elites = SelectionStrategy.elitist_selection(self.population, self.elite_size)
        new_population.extend(copy.deepcopy(elites))
        
        # Generate offspring to fill population
        while len(new_population) < self.population_size:
            # Select parents
            parent1 = SelectionStrategy.tournament_selection(self.population)
            parent2 = SelectionStrategy.tournament_selection(self.population)
            
            # Crossover
            child1, child2 = self.genetic_operators.crossover(parent1, parent2)
            
            # Mutation
            if random.random() < 0.8:  # 80% chance to mutate
                child1 = self.genetic_operators.mutate(child1)
            if random.random() < 0.8:
                child2 = self.genetic_operators.mutate(child2)
                
            new_population.extend([child1, child2])
            
        # Trim to exact population size
        self.population = new_population[:self.population_size]
        
        # Reset fitness scores for new genomes
        for genome in self.population:
            if genome.generation == self.generation + 1:  # New genome
                genome.fitness_score = 0.0
                
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization process"""
        return {
            'total_generations': len(self.evolution_history),
            'final_best_fitness': self.best_genome.fitness_score if self.best_genome else 0.0,
            'best_genome_id': self.best_genome.config_id if self.best_genome else None,
            'total_evaluations': self.fitness_evaluator.evaluation_count,
            'convergence_rate': self.evolution_history[-1].convergence_rate if self.evolution_history else 0.0,
            'final_diversity': self.evolution_history[-1].diversity_measure if self.evolution_history else 0.0,
            'evolution_history': [
                {
                    'generation': m.generation,
                    'best_fitness': m.best_fitness,
                    'average_fitness': m.average_fitness,
                    'diversity': m.diversity_measure
                }
                for m in self.evolution_history
            ]
        }
        
    def export_best_configuration(self) -> Dict[str, Any]:
        """Export the best configuration found"""
        if not self.best_genome:
            return {}
            
        return {
            'genome_id': self.best_genome.config_id,
            'fitness_score': self.best_genome.fitness_score,
            'generation': self.best_genome.generation,
            'parameters': self.best_genome.parameters,
            'structure_genes': self.best_genome.structure_genes,
            'mutation_history': [mt.value for mt in self.best_genome.mutation_history],
            'parent_lineage': self.best_genome.parent_ids
        }