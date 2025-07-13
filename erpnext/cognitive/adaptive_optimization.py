#!/usr/bin/env python3
"""
Adaptive Optimization Module

Implements continuous benchmarking, self-tuning of kernels and agents with
real-time adaptation based on performance trajectories and fitness landscapes.
This module specifically addresses the "Adaptive Optimization" component
of Phase 5 requirements.
"""

import numpy as np
import time
import json
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import queue

from evolutionary_optimizer import EvolutionaryOptimizer, Genome
from feedback_self_analysis import FeedbackDrivenSelfAnalysis
from meta_cognitive import MetaCognitive, MetaLayer


class AdaptationStrategy(Enum):
    """Types of adaptive optimization strategies"""
    CONSERVATIVE = "conservative"  # Small, safe adaptations
    AGGRESSIVE = "aggressive"     # Large, rapid adaptations  
    BALANCED = "balanced"         # Moderate adaptation rate
    DYNAMIC = "dynamic"          # Adaptation rate based on context


@dataclass
class PerformanceTrajectory:
    """Tracks performance trajectory over time"""
    metric_name: str
    timestamps: List[float] = field(default_factory=list)
    values: List[float] = field(default_factory=list)
    trend_direction: float = 0.0  # -1 to 1 (declining to improving)
    trend_strength: float = 0.0   # 0 to 1 (weak to strong trend)
    volatility: float = 0.0       # 0 to 1 (stable to highly variable)
    
    def add_measurement(self, value: float, timestamp: float = None):
        """Add new performance measurement"""
        if timestamp is None:
            timestamp = time.time()
            
        self.timestamps.append(timestamp)
        self.values.append(value)
        
        # Keep only recent measurements (last 100)
        if len(self.values) > 100:
            self.timestamps = self.timestamps[-100:]
            self.values = self.values[-100:]
            
        self._update_trend_analysis()
        
    def _update_trend_analysis(self):
        """Update trend analysis based on recent measurements"""
        if len(self.values) < 3:
            return
            
        # Calculate trend direction using linear regression
        recent_values = np.array(self.values[-20:])  # Last 20 measurements
        x = np.arange(len(recent_values))
        
        if len(recent_values) > 1:
            slope, _ = np.polyfit(x, recent_values, 1)
            self.trend_direction = np.tanh(slope * 10)  # Normalize to [-1, 1]
            
            # Calculate trend strength (R² correlation)
            predicted = slope * x + recent_values[0]
            ss_res = np.sum((recent_values - predicted) ** 2)
            ss_tot = np.sum((recent_values - np.mean(recent_values)) ** 2)
            self.trend_strength = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Calculate volatility (coefficient of variation)
            mean_val = np.mean(recent_values)
            self.volatility = np.std(recent_values) / mean_val if mean_val > 0 else 0


@dataclass
class FitnessLandscape:
    """Represents the fitness landscape for optimization"""
    parameter_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    sampled_points: List[Tuple[Dict[str, float], float]] = field(default_factory=list)
    local_optima: List[Dict[str, float]] = field(default_factory=list)
    global_optimum: Optional[Dict[str, float]] = None
    landscape_roughness: float = 0.0  # 0 to 1 (smooth to very rough)
    exploration_completeness: float = 0.0  # 0 to 1 (unexplored to well-explored)
    
    def add_sample_point(self, parameters: Dict[str, float], fitness: float):
        """Add a sampled point to the fitness landscape"""
        self.sampled_points.append((parameters.copy(), fitness))
        
        # Keep only recent samples (last 1000)
        if len(self.sampled_points) > 1000:
            self.sampled_points = self.sampled_points[-1000:]
            
        self._update_landscape_analysis()
        
    def _update_landscape_analysis(self):
        """Update landscape analysis based on sampled points"""
        if len(self.sampled_points) < 10:
            return
            
        # Extract fitness values
        fitness_values = [fitness for _, fitness in self.sampled_points]
        
        # Update global optimum
        best_idx = np.argmax(fitness_values)
        self.global_optimum = self.sampled_points[best_idx][0].copy()
        
        # Calculate landscape roughness (based on fitness variance)
        self.landscape_roughness = min(1.0, np.std(fitness_values) / np.mean(fitness_values))
        
        # Estimate exploration completeness (simplified)
        unique_params = set()
        for params, _ in self.sampled_points:
            param_tuple = tuple(sorted(params.items()))
            unique_params.add(param_tuple)
        self.exploration_completeness = min(1.0, len(unique_params) / 100)  # Assume 100 is "complete"


class ContinuousBenchmark:
    """Continuous benchmarking system for real-time performance tracking"""
    
    def __init__(self, benchmark_interval: float = 10.0):
        self.benchmark_interval = benchmark_interval
        self.trajectories: Dict[str, PerformanceTrajectory] = {}
        self.fitness_landscape = FitnessLandscape()
        self.benchmarking_active = False
        self.benchmark_thread: Optional[threading.Thread] = None
        
    def start_continuous_benchmarking(self, meta_cognitive: MetaCognitive):
        """Start continuous benchmarking of the cognitive system"""
        self.benchmarking_active = True
        self.benchmark_thread = threading.Thread(
            target=self._benchmarking_loop,
            args=(meta_cognitive,),
            daemon=True
        )
        self.benchmark_thread.start()
        print(f"📊 Started continuous benchmarking (interval: {self.benchmark_interval}s)")
        
    def stop_continuous_benchmarking(self):
        """Stop continuous benchmarking"""
        self.benchmarking_active = False
        if self.benchmark_thread and self.benchmark_thread.is_alive():
            self.benchmark_thread.join(timeout=5.0)
        print("⏹️ Stopped continuous benchmarking")
        
    def _benchmarking_loop(self, meta_cognitive: MetaCognitive):
        """Main benchmarking loop"""
        while self.benchmarking_active:
            try:
                # Capture current system metrics
                system_stats = meta_cognitive.get_system_stats()
                health_report = meta_cognitive.diagnose_system_health()
                
                # Record performance trajectories
                metrics = {
                    'system_health': health_report.get('stability_score', 0.5),
                    'coherence_score': health_report.get('coherence_score', 0.5),
                    'layers_active': health_report.get('layers_active', 0) / 10.0,  # Normalize
                    'monitoring_active': 1.0 if system_stats.get('monitoring_active', False) else 0.0
                }
                
                current_time = time.time()
                for metric_name, value in metrics.items():
                    if metric_name not in self.trajectories:
                        self.trajectories[metric_name] = PerformanceTrajectory(metric_name)
                    self.trajectories[metric_name].add_measurement(value, current_time)
                    
                time.sleep(self.benchmark_interval)
                
            except Exception as e:
                print(f"❌ Benchmarking error: {e}")
                time.sleep(self.benchmark_interval)
                
    def get_performance_trends(self) -> Dict[str, Dict[str, float]]:
        """Get current performance trends"""
        trends = {}
        for metric_name, trajectory in self.trajectories.items():
            trends[metric_name] = {
                'direction': trajectory.trend_direction,
                'strength': trajectory.trend_strength,
                'volatility': trajectory.volatility,
                'current_value': trajectory.values[-1] if trajectory.values else 0.0
            }
        return trends
        
    def get_landscape_analysis(self) -> Dict[str, Any]:
        """Get fitness landscape analysis"""
        return {
            'roughness': self.fitness_landscape.landscape_roughness,
            'exploration_completeness': self.fitness_landscape.exploration_completeness,
            'global_optimum': self.fitness_landscape.global_optimum,
            'local_optima_count': len(self.fitness_landscape.local_optima),
            'sample_count': len(self.fitness_landscape.sampled_points)
        }


class KernelAutoTuner:
    """Automatic tuning system for cognitive kernels"""
    
    def __init__(self):
        self.tuning_history: List[Dict[str, Any]] = []
        self.optimal_configurations: Dict[str, Dict[str, float]] = {}
        self.tuning_strategies: Dict[str, AdaptationStrategy] = {}
        
    def auto_tune_kernel(self, 
                        kernel_name: str,
                        current_config: Dict[str, float],
                        performance_trajectory: PerformanceTrajectory,
                        strategy: AdaptationStrategy = AdaptationStrategy.BALANCED) -> Dict[str, float]:
        """
        Automatically tune kernel parameters based on performance trajectory
        
        Args:
            kernel_name: Name of the kernel to tune
            current_config: Current parameter configuration
            performance_trajectory: Performance history
            strategy: Adaptation strategy to use
            
        Returns:
            Optimized configuration
        """
        print(f"🔧 Auto-tuning {kernel_name} with {strategy.value} strategy...")
        
        # Analyze performance trend to determine tuning direction
        if len(performance_trajectory.values) < 3:
            print(f"   ⚠️ Insufficient data for {kernel_name} tuning")
            return current_config.copy()
            
        trend_direction = performance_trajectory.trend_direction
        trend_strength = performance_trajectory.trend_strength
        volatility = performance_trajectory.volatility
        
        # Determine adaptation magnitude based on strategy
        adaptation_magnitude = self._calculate_adaptation_magnitude(
            strategy, trend_direction, trend_strength, volatility
        )
        
        # Apply parameter adjustments
        new_config = current_config.copy()
        
        if trend_direction < -0.2:  # Performance declining
            # Apply corrective tuning
            new_config = self._apply_corrective_tuning(
                kernel_name, new_config, adaptation_magnitude
            )
        elif trend_direction > 0.2:  # Performance improving
            # Continue in same direction with smaller steps
            new_config = self._apply_progressive_tuning(
                kernel_name, new_config, adaptation_magnitude * 0.5
            )
        else:  # Performance stable
            # Apply exploratory tuning
            new_config = self._apply_exploratory_tuning(
                kernel_name, new_config, adaptation_magnitude * 0.3
            )
            
        # Record tuning operation
        self.tuning_history.append({
            'timestamp': time.time(),
            'kernel_name': kernel_name,
            'strategy': strategy.value,
            'old_config': current_config,
            'new_config': new_config,
            'trend_direction': trend_direction,
            'adaptation_magnitude': adaptation_magnitude
        })
        
        # Update optimal configuration if this is the best so far
        current_performance = performance_trajectory.values[-1]
        if (kernel_name not in self.optimal_configurations or 
            current_performance > performance_trajectory.values[-10:][0]):  # Better than 10 steps ago
            self.optimal_configurations[kernel_name] = new_config.copy()
            
        print(f"   ✅ {kernel_name} tuned: {len([k for k in new_config if new_config[k] != current_config[k]])} parameters adjusted")
        return new_config
        
    def _calculate_adaptation_magnitude(self, 
                                      strategy: AdaptationStrategy,
                                      trend_direction: float,
                                      trend_strength: float,
                                      volatility: float) -> float:
        """Calculate how much to adapt parameters"""
        base_magnitude = {
            AdaptationStrategy.CONSERVATIVE: 0.01,
            AdaptationStrategy.BALANCED: 0.05,
            AdaptationStrategy.AGGRESSIVE: 0.15,
            AdaptationStrategy.DYNAMIC: 0.05  # Will be adjusted based on context
        }[strategy]
        
        if strategy == AdaptationStrategy.DYNAMIC:
            # Adapt magnitude based on performance characteristics
            if abs(trend_direction) > 0.5 and trend_strength > 0.7:
                # Strong clear trend - larger adaptation
                base_magnitude *= 2.0
            elif volatility > 0.5:
                # High volatility - smaller, more careful adaptation
                base_magnitude *= 0.5
                
        return base_magnitude
        
    def _apply_corrective_tuning(self, 
                               kernel_name: str,
                               config: Dict[str, float],
                               magnitude: float) -> Dict[str, float]:
        """Apply corrective tuning for declining performance"""
        new_config = config.copy()
        
        # Reduce learning rates if they exist (prevent overshooting)
        for param in config:
            if 'learning_rate' in param.lower():
                new_config[param] = max(0.0001, config[param] * (1 - magnitude))
                
        # Increase regularization if it exists (prevent overfitting)
        for param in config:
            if 'regularization' in param.lower() or 'decay' in param.lower():
                new_config[param] = min(0.999, config[param] * (1 + magnitude))
                
        return new_config
        
    def _apply_progressive_tuning(self, 
                                kernel_name: str,
                                config: Dict[str, float],
                                magnitude: float) -> Dict[str, float]:
        """Apply progressive tuning for improving performance"""
        new_config = config.copy()
        
        # Continue current trends with smaller adjustments
        for param in config:
            if 'threshold' in param.lower():
                # Slightly adjust thresholds in direction of improvement
                new_config[param] = np.clip(
                    config[param] * (1 + np.random.normal(0, magnitude)),
                    0.0, 1.0
                )
                
        return new_config
        
    def _apply_exploratory_tuning(self, 
                                kernel_name: str,
                                config: Dict[str, float],
                                magnitude: float) -> Dict[str, float]:
        """Apply exploratory tuning for stable performance"""
        new_config = config.copy()
        
        # Small random perturbations to explore parameter space
        for param in config:
            noise = np.random.normal(0, magnitude)
            if 'learning_rate' in param.lower():
                new_config[param] = np.clip(config[param] * (1 + noise), 0.0001, 0.1)
            elif 'threshold' in param.lower():
                new_config[param] = np.clip(config[param] + noise, 0.0, 1.0)
            else:
                new_config[param] = config[param] * (1 + noise)
                
        return new_config


class AdaptiveOptimizer:
    """Main adaptive optimization system combining benchmarking and tuning"""
    
    def __init__(self, 
                 meta_cognitive: MetaCognitive,
                 benchmark_interval: float = 15.0,
                 adaptation_threshold: float = 0.1):
        self.meta_cognitive = meta_cognitive
        self.benchmark_interval = benchmark_interval
        self.adaptation_threshold = adaptation_threshold
        
        self.continuous_benchmark = ContinuousBenchmark(benchmark_interval)
        self.kernel_tuner = KernelAutoTuner()
        self.evolutionary_optimizer = EvolutionaryOptimizer(
            population_size=15,
            max_generations=10
        )
        
        self.optimization_active = False
        self.optimization_thread: Optional[threading.Thread] = None
        self.adaptation_history: List[Dict[str, Any]] = []
        
    def start_adaptive_optimization(self):
        """Start the adaptive optimization system"""
        print("🚀 Starting Adaptive Optimization System")
        
        # Start continuous benchmarking
        self.continuous_benchmark.start_continuous_benchmarking(self.meta_cognitive)
        
        # Start optimization loop
        self.optimization_active = True
        self.optimization_thread = threading.Thread(
            target=self._adaptive_optimization_loop,
            daemon=True
        )
        self.optimization_thread.start()
        
        print("✅ Adaptive optimization system started")
        
    def stop_adaptive_optimization(self):
        """Stop the adaptive optimization system"""
        print("⏹️ Stopping adaptive optimization...")
        
        self.optimization_active = False
        if self.optimization_thread and self.optimization_thread.is_alive():
            self.optimization_thread.join(timeout=10.0)
            
        self.continuous_benchmark.stop_continuous_benchmarking()
        
        print("✅ Adaptive optimization stopped")
        
    def _adaptive_optimization_loop(self):
        """Main adaptive optimization loop"""
        while self.optimization_active:
            try:
                # Wait for sufficient benchmark data
                time.sleep(self.benchmark_interval * 3)  # Wait for 3 benchmark cycles
                
                # Analyze performance trends
                trends = self.continuous_benchmark.get_performance_trends()
                
                # Check if adaptation is needed
                adaptation_needed = self._should_adapt(trends)
                
                if adaptation_needed:
                    print("🔄 Performance degradation detected - triggering adaptation")
                    self._perform_adaptive_optimization(trends)
                else:
                    print("📈 Performance stable - continuing monitoring")
                    
                # Wait before next check
                time.sleep(self.benchmark_interval * 2)
                
            except Exception as e:
                print(f"❌ Adaptive optimization error: {e}")
                time.sleep(self.benchmark_interval)
                
    def _should_adapt(self, trends: Dict[str, Dict[str, float]]) -> bool:
        """Determine if adaptation is needed based on performance trends"""
        declining_metrics = 0
        total_metrics = 0
        
        for metric_name, trend_data in trends.items():
            if trend_data['direction'] < -self.adaptation_threshold:
                declining_metrics += 1
            total_metrics += 1
            
        # Adapt if more than 30% of metrics are declining
        adaptation_ratio = declining_metrics / total_metrics if total_metrics > 0 else 0
        return adaptation_ratio > 0.3
        
    def _perform_adaptive_optimization(self, trends: Dict[str, Dict[str, float]]):
        """Perform adaptive optimization based on performance trends"""
        adaptation_record = {
            'timestamp': time.time(),
            'trigger_trends': trends.copy(),
            'optimizations_applied': []
        }
        
        # 1. Auto-tune individual kernels
        for trajectory_name, trajectory in self.continuous_benchmark.trajectories.items():
            if trends[trajectory_name]['direction'] < -0.2:  # Declining performance
                # Extract current configuration (simplified)
                current_config = self._extract_kernel_config(trajectory_name)
                
                # Determine adaptation strategy based on volatility
                if trends[trajectory_name]['volatility'] > 0.5:
                    strategy = AdaptationStrategy.CONSERVATIVE
                elif trends[trajectory_name]['strength'] > 0.7:
                    strategy = AdaptationStrategy.AGGRESSIVE
                else:
                    strategy = AdaptationStrategy.BALANCED
                    
                # Perform auto-tuning
                new_config = self.kernel_tuner.auto_tune_kernel(
                    trajectory_name, current_config, trajectory, strategy
                )
                
                # Apply configuration (simplified)
                self._apply_kernel_config(trajectory_name, new_config)
                
                adaptation_record['optimizations_applied'].append({
                    'type': 'kernel_tuning',
                    'kernel': trajectory_name,
                    'strategy': strategy.value,
                    'config_changes': len([k for k in new_config if new_config[k] != current_config[k]])
                })
                
        # 2. Run evolutionary optimization if multiple metrics declining
        declining_count = sum(1 for trend in trends.values() if trend['direction'] < -0.2)
        
        if declining_count >= 2:
            print("🧬 Multiple metrics declining - running evolutionary optimization")
            
            # Create genome from current system state
            current_genome = self._create_genome_from_current_state()
            
            # Initialize and run evolutionary optimization
            self.evolutionary_optimizer.initialize_population(
                target_system=self.meta_cognitive,
                seed_genomes=[current_genome]
            )
            
            best_genome = self.evolutionary_optimizer.evolve(
                target_system=self.meta_cognitive,
                convergence_threshold=0.01
            )
            
            # Apply best configuration
            if best_genome.fitness_score > current_genome.fitness_score:
                self._apply_evolutionary_result(best_genome)
                
                adaptation_record['optimizations_applied'].append({
                    'type': 'evolutionary_optimization',
                    'fitness_improvement': best_genome.fitness_score - current_genome.fitness_score,
                    'generations': best_genome.generation
                })
                
        # Record adaptation
        self.adaptation_history.append(adaptation_record)
        
        print(f"✅ Adaptive optimization complete: {len(adaptation_record['optimizations_applied'])} optimizations applied")
        
    def _extract_kernel_config(self, kernel_name: str) -> Dict[str, float]:
        """Extract current configuration for a kernel (simplified implementation)"""
        return {
            'learning_rate': 0.01,
            'threshold': 0.5,
            'regularization': 0.1,
            'weight_decay': 0.99
        }
        
    def _apply_kernel_config(self, kernel_name: str, config: Dict[str, float]):
        """Apply configuration to a kernel (simplified implementation)"""
        # In a real implementation, this would configure the actual kernel
        pass
        
    def _create_genome_from_current_state(self) -> Genome:
        """Create genome representing current system state"""
        genome = Genome(config_id="current_adaptive_state")
        
        # Extract system parameters
        health_report = self.meta_cognitive.diagnose_system_health()
        
        genome.parameters = {
            'adaptation_rate': 0.05,
            'stability_threshold': health_report.get('stability_score', 0.5),
            'coherence_weight': health_report.get('coherence_score', 0.5),
            'monitoring_intensity': 1.0
        }
        
        return genome
        
    def _apply_evolutionary_result(self, genome: Genome):
        """Apply evolutionary optimization result to system"""
        # In a real implementation, this would configure the system based on genome
        print(f"🔧 Applying evolutionary optimization result: {genome.config_id}")
        
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of adaptive optimization performance"""
        return {
            'total_adaptations': len(self.adaptation_history),
            'benchmark_metrics': len(self.continuous_benchmark.trajectories),
            'tuning_operations': len(self.kernel_tuner.tuning_history),
            'optimal_configurations': len(self.kernel_tuner.optimal_configurations),
            'fitness_landscape': self.continuous_benchmark.get_landscape_analysis(),
            'recent_trends': self.continuous_benchmark.get_performance_trends()
        }