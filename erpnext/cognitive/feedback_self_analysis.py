"""
Feedback-Driven Self-Analysis System

Builds on the existing meta-cognitive system to implement recursive feedback loops
and self-analysis capabilities for Phase 5.
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

# Import existing meta-cognitive components
from meta_cognitive import (
    MetaCognitive, MetaLayer, MetaTensor, CognitiveState,
    MetaStateMonitor, RecursiveIntrospector
)
from evolutionary_optimizer import EvolutionaryOptimizer, Genome


class FeedbackType(Enum):
    """Types of feedback that can be generated"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_INEFFICIENCY = "resource_inefficiency"
    COHERENCE_LOSS = "coherence_loss"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"
    ERROR_PATTERN = "error_pattern"
    ADAPTATION_SUCCESS = "adaptation_success"


class AnalysisDepth(Enum):
    """Depth levels for self-analysis"""
    SURFACE = 1      # Basic metrics analysis
    INTERMEDIATE = 2 # Pattern recognition
    DEEP = 3        # Causal analysis
    RECURSIVE = 4   # Self-reflective analysis


@dataclass
class FeedbackSignal:
    """Represents a feedback signal from system analysis"""
    signal_id: str
    feedback_type: FeedbackType
    source_layer: MetaLayer
    timestamp: float
    severity: float  # 0.0 to 1.0
    description: str
    metrics: Dict[str, float] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    correlation_signals: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


@dataclass
class AnalysisReport:
    """Report from self-analysis process"""
    report_id: str
    analysis_depth: AnalysisDepth
    timestamp: float
    layers_analyzed: List[MetaLayer]
    feedback_signals: List[FeedbackSignal]
    system_health_score: float
    improvement_recommendations: List[str]
    predicted_outcomes: Dict[str, float]
    confidence_level: float
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


class PerformanceAnalyzer:
    """Analyzes system performance metrics and generates feedback"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metric_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self.baseline_metrics: Dict[str, float] = {}
        self.analysis_count = 0
        
    def update_metrics(self, metrics: Dict[str, float]):
        """Update performance metrics"""
        for metric_name, value in metrics.items():
            self.metric_history[metric_name].append(value)
            
            # Set baseline only once when we have enough initial data
            if metric_name not in self.baseline_metrics and len(self.metric_history[metric_name]) >= 3:
                initial_values = list(self.metric_history[metric_name])[:3]
                self.baseline_metrics[metric_name] = np.mean(initial_values)
            elif metric_name not in self.baseline_metrics:
                # Temporary baseline for very first measurement
                self.baseline_metrics[metric_name] = value
                
    def analyze_performance_trends(self) -> List[FeedbackSignal]:
        """Analyze performance trends and generate feedback signals"""
        self.analysis_count += 1
        signals = []
        
        for metric_name, history in self.metric_history.items():
            if len(history) < 3:  # Reduced minimum data requirement
                continue
                
            recent_values = list(history)
            
            # Detect performance degradation
            degradation_signal = self._detect_degradation(metric_name, recent_values)
            if degradation_signal:
                signals.append(degradation_signal)
                
            # Detect inefficiency patterns
            inefficiency_signal = self._detect_inefficiency(metric_name, recent_values)
            if inefficiency_signal:
                signals.append(inefficiency_signal)
                
            # Detect optimization opportunities
            optimization_signal = self._detect_optimization_opportunity(metric_name, recent_values)
            if optimization_signal:
                signals.append(optimization_signal)
                
        return signals
        
    def _detect_degradation(self, metric_name: str, values: List[float]) -> Optional[FeedbackSignal]:
        """Detect performance degradation"""
        if len(values) < 3:  # Reduced requirement
            return None
            
        # Compare recent vs baseline
        recent_avg = np.mean(values[-3:])  # Use last 3 values
        baseline = self.baseline_metrics.get(metric_name, recent_avg)
        
        # Check for significant degradation (more sensitive)
        degradation_threshold = 0.7 if 'performance' in metric_name.lower() else 0.85
        if baseline > 0 and recent_avg < baseline * degradation_threshold:
            severity = min(1.0, (baseline - recent_avg) / baseline)
            
            return FeedbackSignal(
                signal_id=f"degradation_{metric_name}_{int(time.time())}",
                feedback_type=FeedbackType.PERFORMANCE_DEGRADATION,
                source_layer=self._infer_source_layer(metric_name),
                timestamp=time.time(),
                severity=severity,
                description=f"Performance degradation detected in {metric_name}: "
                           f"{recent_avg:.4f} vs baseline {baseline:.4f}",
                metrics={
                    'current_value': recent_avg,
                    'baseline_value': baseline,
                    'degradation_percent': (1 - recent_avg/baseline) * 100
                },
                suggested_actions=[
                    f"Investigate {metric_name} computation path",
                    "Check for resource constraints",
                    "Consider parameter optimization"
                ]
            )
            
        return None
        
    def _detect_inefficiency(self, metric_name: str, values: List[float]) -> Optional[FeedbackSignal]:
        """Detect resource inefficiency patterns"""
        if 'resource' not in metric_name.lower() and 'memory' not in metric_name.lower():
            return None
            
        if len(values) < 10:
            return None
            
        # Look for high variance in resource usage
        variance = np.var(values)
        mean_val = np.mean(values)
        
        if mean_val > 0 and variance / mean_val > 0.5:  # High coefficient of variation
            return FeedbackSignal(
                signal_id=f"inefficiency_{metric_name}_{int(time.time())}",
                feedback_type=FeedbackType.RESOURCE_INEFFICIENCY,
                source_layer=self._infer_source_layer(metric_name),
                timestamp=time.time(),
                severity=min(1.0, variance / mean_val),
                description=f"Resource inefficiency detected in {metric_name}: "
                           f"high variance ({variance:.4f}) relative to mean ({mean_val:.4f})",
                metrics={
                    'variance': variance,
                    'mean': mean_val,
                    'coefficient_of_variation': variance / mean_val
                },
                suggested_actions=[
                    "Implement resource pooling",
                    "Add caching mechanisms",
                    "Optimize memory allocation patterns"
                ]
            )
            
        return None
        
    def _detect_optimization_opportunity(self, metric_name: str, values: List[float]) -> Optional[FeedbackSignal]:
        """Detect optimization opportunities"""
        if len(values) < 20:
            return None
            
        # Look for stable sub-optimal performance
        recent_values = values[-10:]
        recent_std = np.std(recent_values)
        recent_mean = np.mean(recent_values)
        
        # If performance is stable but low, suggest optimization
        if recent_std < recent_mean * 0.1 and recent_mean < 0.7:  # Stable but sub-optimal
            return FeedbackSignal(
                signal_id=f"optimization_{metric_name}_{int(time.time())}",
                feedback_type=FeedbackType.OPTIMIZATION_OPPORTUNITY,
                source_layer=self._infer_source_layer(metric_name),
                timestamp=time.time(),
                severity=0.5,  # Medium priority
                description=f"Optimization opportunity in {metric_name}: "
                           f"stable performance at {recent_mean:.4f} suggests potential for improvement",
                metrics={
                    'current_performance': recent_mean,
                    'stability': recent_std,
                    'improvement_potential': 1.0 - recent_mean
                },
                suggested_actions=[
                    "Run evolutionary optimization",
                    "Analyze parameter sensitivity",
                    "Consider architectural changes"
                ]
            )
            
        return None
        
    def _infer_source_layer(self, metric_name: str) -> MetaLayer:
        """Infer which layer a metric comes from"""
        name_lower = metric_name.lower()
        
        if 'tensor' in name_lower or 'kernel' in name_lower:
            return MetaLayer.TENSOR_KERNEL
        elif 'attention' in name_lower:
            return MetaLayer.ATTENTION_ALLOCATION
        elif 'grammar' in name_lower or 'symbolic' in name_lower:
            return MetaLayer.COGNITIVE_GRAMMAR
        else:
            return MetaLayer.EXECUTIVE_CONTROL


class PatternRecognizer:
    """Recognizes patterns in system behavior for deeper analysis"""
    
    def __init__(self):
        self.pattern_cache: Dict[str, Any] = {}
        self.correlation_matrix: Dict[Tuple[str, str], float] = {}
        
    def analyze_correlation_patterns(self, 
                                   feedback_signals: List[FeedbackSignal]) -> List[FeedbackSignal]:
        """Analyze correlations between feedback signals"""
        if len(feedback_signals) < 2:
            return []
            
        correlated_signals = []
        
        # Group signals by type and time proximity
        signal_groups = self._group_signals_by_correlation(feedback_signals)
        
        for group in signal_groups:
            if len(group) >= 2:
                # Generate correlation feedback
                correlation_signal = self._create_correlation_signal(group)
                if correlation_signal:
                    correlated_signals.append(correlation_signal)
                    
        return correlated_signals
        
    def _group_signals_by_correlation(self, 
                                    signals: List[FeedbackSignal]) -> List[List[FeedbackSignal]]:
        """Group signals that are likely correlated"""
        groups = []
        time_window = 60.0  # 60 seconds
        
        # Sort signals by timestamp
        sorted_signals = sorted(signals, key=lambda s: s.timestamp)
        
        current_group = []
        for signal in sorted_signals:
            if not current_group:
                current_group = [signal]
            else:
                # Check if signal is within time window of group
                group_start_time = current_group[0].timestamp
                if signal.timestamp - group_start_time <= time_window:
                    current_group.append(signal)
                else:
                    # Start new group
                    if len(current_group) >= 2:
                        groups.append(current_group)
                    current_group = [signal]
                    
        # Add final group
        if len(current_group) >= 2:
            groups.append(current_group)
            
        return groups
        
    def _create_correlation_signal(self, 
                                 signal_group: List[FeedbackSignal]) -> Optional[FeedbackSignal]:
        """Create a signal representing correlated issues"""
        if len(signal_group) < 2:
            return None
            
        # Analyze correlation strength
        layers_involved = set(s.source_layer for s in signal_group)
        feedback_types = set(s.feedback_type for s in signal_group)
        
        # Calculate correlation score
        time_spread = max(s.timestamp for s in signal_group) - min(s.timestamp for s in signal_group)
        correlation_score = 1.0 / (1.0 + time_spread / 10.0)  # Closer in time = higher correlation
        
        return FeedbackSignal(
            signal_id=f"correlation_{int(time.time())}",
            feedback_type=FeedbackType.ERROR_PATTERN,
            source_layer=MetaLayer.EXECUTIVE_CONTROL,
            timestamp=time.time(),
            severity=np.mean([s.severity for s in signal_group]),
            description=f"Correlated issues detected across {len(layers_involved)} layers: "
                       f"{', '.join(ft.value for ft in feedback_types)}",
            metrics={
                'correlation_score': correlation_score,
                'layers_affected': len(layers_involved),
                'signal_count': len(signal_group)
            },
            suggested_actions=[
                "Investigate system-wide dependencies",
                "Check for cascading failures",
                "Consider holistic optimization approach"
            ],
            correlation_signals=[s.signal_id for s in signal_group]
        )


class RecursiveSelfAnalyzer:
    """Implements recursive self-analysis capabilities"""
    
    def __init__(self, max_recursion_depth: int = 3):
        self.max_recursion_depth = max_recursion_depth
        self.analysis_history: List[AnalysisReport] = []
        self.recursion_stack: List[str] = []
        
    def perform_recursive_analysis(self, 
                                 meta_cognitive: MetaCognitive,
                                 analysis_depth: AnalysisDepth = AnalysisDepth.DEEP) -> AnalysisReport:
        """
        Perform recursive self-analysis
        
        Args:
            meta_cognitive: Meta-cognitive system to analyze
            analysis_depth: Depth of analysis to perform
            
        Returns:
            Analysis report
        """
        analysis_id = f"analysis_{int(time.time()*1000)}"
        
        # Prevent infinite recursion
        if len(self.recursion_stack) >= self.max_recursion_depth:
            return self._create_shallow_report(analysis_id, meta_cognitive)
            
        self.recursion_stack.append(analysis_id)
        
        try:
            report = self._perform_analysis_at_depth(
                analysis_id, meta_cognitive, analysis_depth
            )
            
            # Recursive meta-analysis
            if analysis_depth.value >= AnalysisDepth.RECURSIVE.value:
                meta_report = self._analyze_analysis_process(report, meta_cognitive)
                report.improvement_recommendations.extend(meta_report.improvement_recommendations)
                
            self.analysis_history.append(report)
            return report
            
        finally:
            self.recursion_stack.pop()
            
    def _perform_analysis_at_depth(self, 
                                 analysis_id: str,
                                 meta_cognitive: MetaCognitive,
                                 depth: AnalysisDepth) -> AnalysisReport:
        """Perform analysis at specified depth"""
        
        # Get current system state
        current_state = meta_cognitive.get_system_stats()
        health_report = meta_cognitive.diagnose_system_health()
        
        feedback_signals = []
        layers_analyzed = list(meta_cognitive.cognitive_layers.keys())
        
        if depth.value >= AnalysisDepth.SURFACE.value:
            # Surface analysis: basic metrics
            feedback_signals.extend(self._surface_analysis(meta_cognitive))
            
        if depth.value >= AnalysisDepth.INTERMEDIATE.value:
            # Intermediate analysis: pattern recognition
            feedback_signals.extend(self._intermediate_analysis(meta_cognitive, feedback_signals))
            
        if depth.value >= AnalysisDepth.DEEP.value:
            # Deep analysis: causal relationships
            feedback_signals.extend(self._deep_analysis(meta_cognitive, feedback_signals))
            
        # Calculate overall health score
        health_score = self._calculate_health_score(health_report, feedback_signals)
        
        # Generate improvement recommendations
        recommendations = self._generate_recommendations(feedback_signals, health_report)
        
        # Predict outcomes of recommendations
        predictions = self._predict_outcomes(recommendations, meta_cognitive)
        
        # Calculate confidence level
        confidence = self._calculate_confidence(feedback_signals, health_report)
        
        return AnalysisReport(
            report_id=analysis_id,
            analysis_depth=depth,
            timestamp=time.time(),
            layers_analyzed=layers_analyzed,
            feedback_signals=feedback_signals,
            system_health_score=health_score,
            improvement_recommendations=recommendations,
            predicted_outcomes=predictions,
            confidence_level=confidence
        )
        
    def _surface_analysis(self, meta_cognitive: MetaCognitive) -> List[FeedbackSignal]:
        """Perform surface-level analysis"""
        signals = []
        
        # Analyze current metrics
        health_report = meta_cognitive.diagnose_system_health()
        
        if health_report['status'] == 'degraded':
            signals.append(FeedbackSignal(
                signal_id=f"health_degraded_{int(time.time())}",
                feedback_type=FeedbackType.PERFORMANCE_DEGRADATION,
                source_layer=MetaLayer.EXECUTIVE_CONTROL,
                timestamp=time.time(),
                severity=0.7,
                description="System health is degraded",
                metrics={'error_count': len(health_report.get('errors', []))},
                suggested_actions=["Investigate system errors", "Check resource usage"]
            ))
            
        return signals
        
    def _intermediate_analysis(self, 
                             meta_cognitive: MetaCognitive,
                             existing_signals: List[FeedbackSignal]) -> List[FeedbackSignal]:
        """Perform intermediate pattern analysis"""
        pattern_recognizer = PatternRecognizer()
        return pattern_recognizer.analyze_correlation_patterns(existing_signals)
        
    def _deep_analysis(self, 
                      meta_cognitive: MetaCognitive,
                      existing_signals: List[FeedbackSignal]) -> List[FeedbackSignal]:
        """Perform deep causal analysis"""
        signals = []
        
        # Analyze meta-tensor dynamics
        for layer in meta_cognitive.cognitive_layers.keys():
            dynamics = meta_cognitive.get_meta_tensor_dynamics(layer, window_size=20)
            
            if len(dynamics) > 5:
                # Look for instability patterns
                stability = self._analyze_stability(dynamics)
                if stability < 0.5:
                    signals.append(FeedbackSignal(
                        signal_id=f"instability_{layer.value}_{int(time.time())}",
                        feedback_type=FeedbackType.COHERENCE_LOSS,
                        source_layer=layer,
                        timestamp=time.time(),
                        severity=1.0 - stability,
                        description=f"Instability detected in {layer.value} meta-tensor dynamics",
                        metrics={'stability_score': stability},
                        suggested_actions=[
                            "Analyze layer coupling strength",
                            "Check for parameter drift",
                            "Consider stabilization mechanisms"
                        ]
                    ))
                    
        return signals
        
    def _analyze_analysis_process(self, 
                                report: AnalysisReport,
                                meta_cognitive: MetaCognitive) -> AnalysisReport:
        """Meta-analyze the analysis process itself"""
        
        # This is the recursive part - analyzing how well we're analyzing
        meta_signals = []
        
        # Check analysis effectiveness
        if len(report.feedback_signals) == 0:
            meta_signals.append(FeedbackSignal(
                signal_id=f"analysis_ineffective_{int(time.time())}",
                feedback_type=FeedbackType.OPTIMIZATION_OPPORTUNITY,
                source_layer=MetaLayer.EXECUTIVE_CONTROL,
                timestamp=time.time(),
                severity=0.5,
                description="Analysis process generated no feedback signals",
                suggested_actions=["Increase analysis sensitivity", "Check metric collection"]
            ))
            
        # Check recommendation quality
        if len(report.improvement_recommendations) < 3:
            meta_signals.append(FeedbackSignal(
                signal_id=f"few_recommendations_{int(time.time())}",
                feedback_type=FeedbackType.OPTIMIZATION_OPPORTUNITY,
                source_layer=MetaLayer.EXECUTIVE_CONTROL,
                timestamp=time.time(),
                severity=0.3,
                description="Analysis generated few improvement recommendations",
                suggested_actions=["Expand recommendation generation logic"]
            ))
            
        return AnalysisReport(
            report_id=f"meta_{report.report_id}",
            analysis_depth=AnalysisDepth.RECURSIVE,
            timestamp=time.time(),
            layers_analyzed=[MetaLayer.EXECUTIVE_CONTROL],
            feedback_signals=meta_signals,
            system_health_score=report.system_health_score,
            improvement_recommendations=[
                "Improve analysis process effectiveness",
                "Enhance feedback signal generation",
                "Optimize recursive analysis depth"
            ],
            predicted_outcomes={'analysis_improvement': 0.2},
            confidence_level=0.8
        )
        
    def _analyze_stability(self, dynamics: np.ndarray) -> float:
        """Analyze stability of meta-tensor dynamics"""
        if len(dynamics) < 3:
            return 1.0
            
        # Calculate stability based on variance and trend
        if len(dynamics.shape) == 1:
            variance = np.var(dynamics)
            stability = 1.0 / (1.0 + variance)
        else:
            # Multi-dimensional dynamics
            variances = np.var(dynamics, axis=0)
            avg_variance = np.mean(variances)
            stability = 1.0 / (1.0 + avg_variance)
            
        return min(1.0, max(0.0, stability))
        
    def _create_shallow_report(self, analysis_id: str, meta_cognitive: MetaCognitive) -> AnalysisReport:
        """Create a shallow report when recursion limit reached"""
        return AnalysisReport(
            report_id=analysis_id,
            analysis_depth=AnalysisDepth.SURFACE,
            timestamp=time.time(),
            layers_analyzed=list(meta_cognitive.cognitive_layers.keys()),
            feedback_signals=[],
            system_health_score=0.5,
            improvement_recommendations=["Recursion limit reached - consider increasing depth"],
            predicted_outcomes={},
            confidence_level=0.3
        )
        
    def _calculate_health_score(self, 
                              health_report: Dict[str, Any],
                              feedback_signals: List[FeedbackSignal]) -> float:
        """Calculate overall system health score"""
        base_score = 1.0 if health_report.get('status') == 'healthy' else 0.5
        
        # Reduce score based on feedback severity
        for signal in feedback_signals:
            base_score -= signal.severity * 0.1
            
        return max(0.0, min(1.0, base_score))
        
    def _generate_recommendations(self, 
                                feedback_signals: List[FeedbackSignal],
                                health_report: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = set()
        
        # Extract recommendations from feedback signals
        for signal in feedback_signals:
            recommendations.update(signal.suggested_actions)
            
        # Add general recommendations based on health
        if health_report.get('status') == 'degraded':
            recommendations.add("Perform system-wide health check")
            recommendations.add("Review error logs and patterns")
            
        # Add evolutionary optimization recommendations
        if any(signal.feedback_type == FeedbackType.OPTIMIZATION_OPPORTUNITY 
               for signal in feedback_signals):
            recommendations.add("Run evolutionary optimization cycle")
            recommendations.add("Analyze parameter sensitivity")
            
        return list(recommendations)
        
    def _predict_outcomes(self, 
                        recommendations: List[str],
                        meta_cognitive: MetaCognitive) -> Dict[str, float]:
        """Predict outcomes of implementing recommendations"""
        predictions = {}
        
        for rec in recommendations:
            # Simple heuristic-based predictions
            if 'optimization' in rec.lower():
                predictions[rec] = 0.3  # Moderate improvement expected
            elif 'error' in rec.lower() or 'check' in rec.lower():
                predictions[rec] = 0.2  # Small but important improvement
            elif 'evolutionary' in rec.lower():
                predictions[rec] = 0.5  # High potential improvement
            else:
                predictions[rec] = 0.1  # Unknown/low impact
                
        return predictions
        
    def _calculate_confidence(self, 
                            feedback_signals: List[FeedbackSignal],
                            health_report: Dict[str, Any]) -> float:
        """Calculate confidence in analysis results"""
        base_confidence = 0.7
        
        # Higher confidence with more signals
        signal_bonus = min(0.2, len(feedback_signals) * 0.05)
        
        # Lower confidence if system is unhealthy
        health_penalty = 0.0
        if health_report.get('status') == 'degraded':
            health_penalty = 0.1
            
        return max(0.1, min(1.0, base_confidence + signal_bonus - health_penalty))


class FeedbackDrivenSelfAnalysis:
    """Main system for feedback-driven self-analysis"""
    
    def __init__(self, meta_cognitive: MetaCognitive):
        self.meta_cognitive = meta_cognitive
        self.performance_analyzer = PerformanceAnalyzer()
        self.recursive_analyzer = RecursiveSelfAnalyzer()
        self.evolutionary_optimizer = EvolutionaryOptimizer()
        
        self.feedback_queue = queue.Queue()
        self.analysis_active = False
        self.analysis_thread: Optional[threading.Thread] = None
        self.feedback_history: List[FeedbackSignal] = []
        
    def start_continuous_analysis(self, analysis_interval: float = 30.0):
        """Start continuous self-analysis process"""
        self.analysis_active = True
        self.analysis_thread = threading.Thread(
            target=self._continuous_analysis_loop,
            args=(analysis_interval,),
            daemon=True
        )
        self.analysis_thread.start()
        print(f"🔄 Started continuous self-analysis (interval: {analysis_interval}s)")
        
    def stop_continuous_analysis(self):
        """Stop continuous analysis"""
        self.analysis_active = False
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=5.0)
        print("⏹️ Stopped continuous self-analysis")
        
    def _continuous_analysis_loop(self, interval: float):
        """Main loop for continuous analysis"""
        while self.analysis_active:
            try:
                # Update system state
                self.meta_cognitive.update_meta_state()
                
                # Collect current metrics
                system_stats = self.meta_cognitive.get_system_stats()
                health_report = self.meta_cognitive.diagnose_system_health()
                
                # Update performance analyzer
                metrics = {
                    'system_health': health_report.get('stability_score', 0.5),
                    'coherence': health_report.get('coherence_score', 0.5),
                    'layers_active': health_report.get('layers_active', 0)
                }
                self.performance_analyzer.update_metrics(metrics)
                
                # Generate feedback signals
                feedback_signals = self.performance_analyzer.analyze_performance_trends()
                
                # Process feedback signals
                for signal in feedback_signals:
                    self.feedback_queue.put(signal)
                    self.feedback_history.append(signal)
                    
                # Trigger adaptive responses if needed
                self._process_feedback_signals(feedback_signals)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Error in continuous analysis: {e}")
                time.sleep(interval)
                
    def _process_feedback_signals(self, signals: List[FeedbackSignal]):
        """Process feedback signals and trigger appropriate responses"""
        high_severity_signals = [s for s in signals if s.severity > 0.7]
        
        if high_severity_signals:
            print(f"🚨 High severity feedback detected: {len(high_severity_signals)} signals")
            
            # Trigger evolutionary optimization for optimization opportunities
            optimization_signals = [
                s for s in high_severity_signals 
                if s.feedback_type == FeedbackType.OPTIMIZATION_OPPORTUNITY
            ]
            
            if optimization_signals:
                self._trigger_evolutionary_optimization()
                
    def _trigger_evolutionary_optimization(self):
        """Trigger evolutionary optimization in response to feedback"""
        print("🧬 Triggering evolutionary optimization...")
        
        try:
            # Create seed genome from current system configuration
            current_config = self._extract_current_configuration()
            seed_genome = self._config_to_genome(current_config)
            
            # Run optimization
            self.evolutionary_optimizer.initialize_population(
                target_system=self.meta_cognitive,
                seed_genomes=[seed_genome]
            )
            
            best_genome = self.evolutionary_optimizer.evolve(
                target_system=self.meta_cognitive,
                convergence_threshold=0.001
            )
            
            # Apply best configuration
            if best_genome.fitness_score > seed_genome.fitness_score:
                print(f"🎯 Found improved configuration (fitness: {best_genome.fitness_score:.4f})")
                self._apply_genome_configuration(best_genome)
                
                # Generate success feedback
                self.feedback_history.append(FeedbackSignal(
                    signal_id=f"optimization_success_{int(time.time())}",
                    feedback_type=FeedbackType.ADAPTATION_SUCCESS,
                    source_layer=MetaLayer.EXECUTIVE_CONTROL,
                    timestamp=time.time(),
                    severity=0.8,
                    description=f"Evolutionary optimization improved system fitness to {best_genome.fitness_score:.4f}",
                    metrics={'fitness_improvement': best_genome.fitness_score - seed_genome.fitness_score}
                ))
            else:
                print("📊 No improvement found through evolutionary optimization")
                
        except Exception as e:
            print(f"❌ Error in evolutionary optimization: {e}")
            
    def _extract_current_configuration(self) -> Dict[str, Any]:
        """Extract current system configuration"""
        # This would extract actual configuration from the meta-cognitive system
        return {
            'learning_rates': {'primary': 0.01, 'secondary': 0.005},
            'thresholds': {'attention': 0.5, 'coherence': 0.7},
            'weights': {'primary': 1.0, 'secondary': 0.8}
        }
        
    def _config_to_genome(self, config: Dict[str, Any]) -> Genome:
        """Convert configuration to genome"""
        genome = Genome(config_id="current_system_config")
        
        # Flatten configuration to parameters
        for category, params in config.items():
            if isinstance(params, dict):
                for param_name, value in params.items():
                    genome.parameters[f"{category}_{param_name}"] = value
            else:
                genome.parameters[category] = params
                
        return genome
        
    def _apply_genome_configuration(self, genome: Genome):
        """Apply genome configuration to system"""
        # This would apply the configuration to the actual system
        print(f"🔧 Applying configuration from genome {genome.config_id}")
        
    def perform_deep_analysis(self) -> AnalysisReport:
        """Perform one-time deep analysis"""
        return self.recursive_analyzer.perform_recursive_analysis(
            self.meta_cognitive, 
            AnalysisDepth.RECURSIVE
        )
        
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of feedback history"""
        if not self.feedback_history:
            return {'total_signals': 0}
            
        feedback_by_type = defaultdict(int)
        feedback_by_layer = defaultdict(int)
        severity_distribution = []
        
        for signal in self.feedback_history:
            feedback_by_type[signal.feedback_type.value] += 1
            feedback_by_layer[signal.source_layer.value] += 1
            severity_distribution.append(signal.severity)
            
        return {
            'total_signals': len(self.feedback_history),
            'feedback_by_type': dict(feedback_by_type),
            'feedback_by_layer': dict(feedback_by_layer),
            'average_severity': np.mean(severity_distribution),
            'max_severity': max(severity_distribution),
            'recent_signals': len([s for s in self.feedback_history 
                                 if time.time() - s.timestamp < 300])  # Last 5 minutes
        }