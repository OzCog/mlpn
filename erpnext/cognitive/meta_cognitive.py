"""
Meta-Cognitive Enhancement System

Implements meta-tensor state tracking, recursive introspection capabilities,
and operational state monitoring for each cognitive layer.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import inspect
from collections import defaultdict


class MetaLayer(Enum):
    """Types of meta-cognitive layers"""
    TENSOR_KERNEL = "tensor_kernel"
    COGNITIVE_GRAMMAR = "cognitive_grammar"
    ATTENTION_ALLOCATION = "attention_allocation"
    EXECUTIVE_CONTROL = "executive_control"


class IntrospectionLevel(Enum):
    """Levels of introspection depth"""
    SHALLOW = 1
    MEDIUM = 2
    DEEP = 3
    RECURSIVE = 4


@dataclass
class MetaTensor:
    """Meta-tensor representing operational state"""
    layer: MetaLayer
    timestamp: float
    state_vector: np.ndarray
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    error_states: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


@dataclass
class CognitiveState:
    """Complete cognitive system state"""
    meta_tensors: Dict[MetaLayer, MetaTensor] = field(default_factory=dict)
    global_performance: float = 0.0
    coherence_measure: float = 0.0
    attention_focus: List[str] = field(default_factory=list)
    active_processes: List[str] = field(default_factory=list)


class MetaStateMonitor:
    """
    Monitors and tracks meta-cognitive states across layers
    """
    
    def __init__(self):
        self.state_history: List[CognitiveState] = []
        self.layer_monitors: Dict[MetaLayer, Callable] = {}
        self.introspection_cache: Dict[str, Any] = {}
        self.monitoring_active = False
        
    def register_layer_monitor(self, layer: MetaLayer, monitor_func: Callable) -> None:
        """
        Register a monitoring function for a specific layer
        
        Args:
            layer: Meta-cognitive layer
            monitor_func: Function to monitor layer state
        """
        self.layer_monitors[layer] = monitor_func
        
    def capture_layer_state(self, layer: MetaLayer, layer_instance: Any) -> MetaTensor:
        """
        Capture state of a specific cognitive layer
        
        Args:
            layer: Meta-cognitive layer type
            layer_instance: Instance of the layer to monitor
            
        Returns:
            MetaTensor representing layer state
        """
        # Get state vector based on layer type
        if layer == MetaLayer.TENSOR_KERNEL:
            state_vector = self._capture_tensor_kernel_state(layer_instance)
        elif layer == MetaLayer.COGNITIVE_GRAMMAR:
            state_vector = self._capture_grammar_state(layer_instance)
        elif layer == MetaLayer.ATTENTION_ALLOCATION:
            state_vector = self._capture_attention_state(layer_instance)
        else:
            state_vector = np.array([0.0])
            
        # Calculate performance metrics
        performance = self._calculate_performance_metrics(layer, layer_instance)
        
        # Monitor resource usage
        resources = self._monitor_resources(layer_instance)
        
        # Check for error states
        errors = self._check_error_states(layer_instance)
        
        return MetaTensor(
            layer=layer,
            timestamp=time.time(),
            state_vector=state_vector,
            performance_metrics=performance,
            resource_usage=resources,
            error_states=errors
        )
        
    def _capture_tensor_kernel_state(self, tensor_kernel) -> np.ndarray:
        """Capture tensor kernel state"""
        try:
            stats = tensor_kernel.get_operation_stats()
            return np.array([
                stats.get("operation_count", 0),
                stats.get("cached_tensors", 0),
                stats.get("registered_shapes", 0),
                1.0 if stats.get("backend") == "gpu" else 0.0
            ])
        except:
            return np.array([0.0, 0.0, 0.0, 0.0])
            
    def _capture_grammar_state(self, grammar) -> np.ndarray:
        """Capture cognitive grammar state"""
        try:
            stats = grammar.get_knowledge_stats()
            return np.array([
                stats.get("total_atoms", 0),
                stats.get("total_links", 0),
                stats.get("hypergraph_density", 0.0),
                stats.get("pattern_count", 0)
            ])
        except:
            return np.array([0.0, 0.0, 0.0, 0.0])
            
    def _capture_attention_state(self, attention) -> np.ndarray:
        """Capture attention allocation state"""
        try:
            stats = attention.get_economic_stats()
            return np.array([
                stats.get("total_wages", 0.0),
                stats.get("total_rents", 0.0),
                stats.get("wage_fund", 0.0),
                stats.get("rent_fund", 0.0)
            ])
        except:
            return np.array([0.0, 0.0, 0.0, 0.0])
            
    def _calculate_performance_metrics(self, layer: MetaLayer, instance: Any) -> Dict[str, float]:
        """Calculate performance metrics for a layer"""
        metrics = {
            "throughput": 0.0,
            "latency": 0.0,
            "accuracy": 0.0,
            "efficiency": 0.0
        }
        
        # Layer-specific performance calculation
        if layer == MetaLayer.TENSOR_KERNEL:
            # Measure tensor operation performance
            if hasattr(instance, 'get_operation_stats'):
                stats = instance.get_operation_stats()
                metrics["throughput"] = stats.get("operation_count", 0) / 60.0  # ops/minute
                
        elif layer == MetaLayer.COGNITIVE_GRAMMAR:
            # Measure knowledge processing performance
            if hasattr(instance, 'get_knowledge_stats'):
                stats = instance.get_knowledge_stats()
                metrics["throughput"] = stats.get("total_atoms", 0) + stats.get("total_links", 0)
                
        return metrics
        
    def _monitor_resources(self, instance: Any) -> Dict[str, float]:
        """Monitor resource usage"""
        resources = {
            "memory_mb": 0.0,
            "cpu_percent": 0.0,
            "gpu_percent": 0.0,
            "io_operations": 0.0
        }
        
        # Basic resource monitoring (would integrate with actual monitoring tools)
        try:
            import psutil
            process = psutil.Process()
            resources["memory_mb"] = process.memory_info().rss / 1024 / 1024
            resources["cpu_percent"] = process.cpu_percent()
        except:
            pass
            
        return resources
        
    def _check_error_states(self, instance: Any) -> List[str]:
        """Check for error states in the layer"""
        errors = []
        
        # Check for common error conditions
        if hasattr(instance, 'get_operation_stats'):
            stats = instance.get_operation_stats()
            if stats.get("operation_count", 0) == 0:
                errors.append("no_operations")
                
        if hasattr(instance, 'get_knowledge_stats'):
            stats = instance.get_knowledge_stats()
            if stats.get("total_atoms", 0) == 0:
                errors.append("empty_knowledge_base")
                
        return errors
        
    def start_monitoring(self) -> None:
        """Start continuous monitoring"""
        self.monitoring_active = True
        
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.monitoring_active = False
        
    def get_current_state(self) -> CognitiveState:
        """Get current cognitive state"""
        if not self.state_history:
            return CognitiveState()
        return self.state_history[-1]
        
    def get_state_trajectory(self, window_size: int = 10) -> List[CognitiveState]:
        """Get recent state trajectory"""
        return self.state_history[-window_size:]


class RecursiveIntrospector:
    """
    Implements recursive introspection capabilities
    """
    
    def __init__(self, max_depth: int = 4):
        self.max_depth = max_depth
        self.introspection_results: Dict[str, Any] = {}
        self.call_stack: List[str] = []
        
    def introspect_layer(self, layer: MetaLayer, instance: Any, 
                        depth: int = 1) -> Dict[str, Any]:
        """
        Perform recursive introspection on a layer
        
        Args:
            layer: Layer to introspect
            instance: Layer instance
            depth: Current introspection depth
            
        Returns:
            Introspection results
        """
        if depth > self.max_depth:
            return {"error": "max_depth_exceeded"}
            
        # Prevent infinite recursion
        call_id = f"{layer.value}_{depth}"
        if call_id in self.call_stack:
            return {"error": "recursive_loop_detected"}
            
        self.call_stack.append(call_id)
        
        try:
            result = self._perform_introspection(layer, instance, depth)
            
            # Recursive introspection if depth allows
            if depth < self.max_depth:
                result["meta_introspection"] = self.introspect_layer(
                    layer, instance, depth + 1
                )
                
            return result
            
        finally:
            self.call_stack.remove(call_id)
            
    def _perform_introspection(self, layer: MetaLayer, instance: Any, 
                             depth: int) -> Dict[str, Any]:
        """Perform actual introspection"""
        result = {
            "layer": layer.value,
            "depth": depth,
            "timestamp": time.time(),
            "structure": self._analyze_structure(instance),
            "behavior": self._analyze_behavior(instance),
            "state": self._analyze_state(instance)
        }
        
        return result
        
    def _analyze_structure(self, instance: Any) -> Dict[str, Any]:
        """Analyze structural properties"""
        return {
            "class_name": instance.__class__.__name__,
            "module": instance.__class__.__module__,
            "methods": [m for m in dir(instance) if not m.startswith('_')],
            "attributes": [a for a in vars(instance).keys() if not a.startswith('_')]
        }
        
    def _analyze_behavior(self, instance: Any) -> Dict[str, Any]:
        """Analyze behavioral patterns"""
        behavior = {
            "callable_methods": [],
            "method_signatures": {},
            "recent_calls": []
        }
        
        # Analyze methods
        for method_name in dir(instance):
            if not method_name.startswith('_'):
                method = getattr(instance, method_name)
                if callable(method):
                    behavior["callable_methods"].append(method_name)
                    try:
                        sig = inspect.signature(method)
                        behavior["method_signatures"][method_name] = str(sig)
                    except:
                        pass
                        
        return behavior
        
    def _analyze_state(self, instance: Any) -> Dict[str, Any]:
        """Analyze current state"""
        state = {
            "attributes": {},
            "collections": {},
            "numeric_values": {}
        }
        
        for attr_name in vars(instance):
            if not attr_name.startswith('_'):
                attr_value = getattr(instance, attr_name)
                
                if isinstance(attr_value, (list, dict, set)):
                    state["collections"][attr_name] = len(attr_value)
                elif isinstance(attr_value, (int, float)):
                    state["numeric_values"][attr_name] = attr_value
                else:
                    state["attributes"][attr_name] = str(type(attr_value))
                    
        return state
        
    def scheme_introspection(self, layer: MetaLayer) -> str:
        """
        Generate Scheme specification for introspection
        
        Args:
            layer: Layer to generate spec for
            
        Returns:
            Scheme specification string
        """
        spec = f"""
(define (introspect-layer {layer.value})
  (let ((structure (analyze-structure {layer.value}))
        (behavior (analyze-behavior {layer.value}))
        (state (analyze-state {layer.value})))
    (display "Layer: ") (display "{layer.value}") (newline)
    (display "Structure: ") (display structure) (newline)
    (display "Behavior: ") (display behavior) (newline)
    (display "State: ") (display state) (newline)
    (list structure behavior state)))
"""
        return spec.strip()


class MetaCognitive:
    """
    Main meta-cognitive system integrating monitoring and introspection
    """
    
    def __init__(self):
        self.state_monitor = MetaStateMonitor()
        self.introspector = RecursiveIntrospector()
        self.cognitive_layers: Dict[Union[MetaLayer, str], Any] = {}
        self.meta_tensor_history: List[Dict[MetaLayer, MetaTensor]] = []
        
    def register_layer(self, layer: Union[MetaLayer, str], instance: Any) -> None:
        """
        Register a cognitive layer for monitoring
        
        Args:
            layer: Layer type (MetaLayer enum or string)
            instance: Layer instance
        """
        # Convert string to MetaLayer if needed
        if isinstance(layer, str):
            # Try to find matching MetaLayer
            for meta_layer in MetaLayer:
                if meta_layer.value == layer:
                    layer = meta_layer
                    break
            else:
                # If no match found, use the string directly as key
                # This allows for dynamic layer registration
                self.cognitive_layers[layer] = instance
                return
        
        self.cognitive_layers[layer] = instance
        
    def update_meta_state(self) -> None:
        """Update meta-cognitive state for all layers"""
        current_meta_tensors = {}
        
        for layer, instance in self.cognitive_layers.items():
            meta_tensor = self.state_monitor.capture_layer_state(layer, instance)
            current_meta_tensors[layer] = meta_tensor
            
        self.meta_tensor_history.append(current_meta_tensors)
        
        # Update cognitive state
        cognitive_state = self._compute_cognitive_state(current_meta_tensors)
        self.state_monitor.state_history.append(cognitive_state)
        
    def _compute_cognitive_state(self, meta_tensors: Dict[MetaLayer, MetaTensor]) -> CognitiveState:
        """Compute overall cognitive state"""
        # Calculate global performance
        performances = []
        for tensor in meta_tensors.values():
            if tensor.performance_metrics:
                performances.extend(tensor.performance_metrics.values())
                
        global_performance = np.mean(performances) if performances else 0.0
        
        # Calculate coherence measure
        coherence = self._calculate_coherence(meta_tensors)
        
        # Extract attention focus
        attention_focus = []
        if MetaLayer.ATTENTION_ALLOCATION in meta_tensors:
            # Would extract from attention layer
            pass
            
        # Extract active processes
        active_processes = []
        for layer, tensor in meta_tensors.items():
            if tensor.resource_usage.get("cpu_percent", 0) > 10:
                active_processes.append(layer.value)
                
        return CognitiveState(
            meta_tensors=meta_tensors,
            global_performance=global_performance,
            coherence_measure=coherence,
            attention_focus=attention_focus,
            active_processes=active_processes
        )
        
    def _calculate_coherence(self, meta_tensors: Dict[MetaLayer, MetaTensor]) -> float:
        """Calculate coherence between layers"""
        if len(meta_tensors) < 2:
            return 1.0
            
        # Calculate correlation between layer states
        vectors = []
        for tensor in meta_tensors.values():
            if len(tensor.state_vector) > 0:
                vectors.append(tensor.state_vector)
                
        if len(vectors) < 2:
            return 1.0
            
        # Compute pairwise correlations
        correlations = []
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                try:
                    corr = np.corrcoef(vectors[i], vectors[j])[0, 1]
                    if not np.isnan(corr):
                        correlations.append(abs(corr))
                except:
                    pass
                    
        return np.mean(correlations) if correlations else 0.75  # Default to good coherence when no conflicts detected
        
    def perform_deep_introspection(self, layer: MetaLayer = None) -> Dict[str, Any]:
        """
        Perform deep introspection on specified layer or all layers
        
        Args:
            layer: Specific layer to introspect, or None for all
            
        Returns:
            Introspection results
        """
        if layer is not None:
            if layer in self.cognitive_layers:
                return self.introspector.introspect_layer(
                    layer, self.cognitive_layers[layer], depth=1
                )
            else:
                return {"error": "layer_not_registered"}
        else:
            # Introspect all layers
            results = {}
            for layer, instance in self.cognitive_layers.items():
                results[layer.value] = self.introspector.introspect_layer(
                    layer, instance, depth=1
                )
            return results
            
    def get_meta_tensor_dynamics(self, layer: MetaLayer, 
                                window_size: int = 10) -> np.ndarray:
        """
        Get meta-tensor dynamics over time
        
        Args:
            layer: Layer to analyze
            window_size: Size of time window
            
        Returns:
            Tensor dynamics array
        """
        if not self.meta_tensor_history:
            return np.array([])
            
        # Extract tensor history for the layer
        history = []
        for meta_tensors in self.meta_tensor_history[-window_size:]:
            if layer in meta_tensors:
                history.append(meta_tensors[layer].state_vector)
                
        if not history:
            return np.array([])
            
        return np.array(history)
        
    def diagnose_system_health(self) -> Dict[str, Any]:
        """
        Diagnose overall system health
        
        Returns:
            System health report
        """
        if not self.meta_tensor_history:
            return {"status": "no_data"}
            
        latest_tensors = self.meta_tensor_history[-1]
        
        # Check for errors
        errors = []
        for layer, tensor in latest_tensors.items():
            errors.extend(tensor.error_states)
            
        # Check resource usage
        high_resource_layers = []
        for layer, tensor in latest_tensors.items():
            if tensor.resource_usage.get("memory_mb", 0) > 1000:  # >1GB
                high_resource_layers.append(layer.value)
                
        # Calculate system stability
        stability = self._calculate_stability()
        
        return {
            "status": "healthy" if not errors else "degraded",
            "errors": errors,
            "high_resource_layers": high_resource_layers,
            "stability_score": stability,
            "coherence_score": self.state_monitor.get_current_state().coherence_measure,
            "layers_active": len(self.cognitive_layers)
        }
        
    def _calculate_stability(self) -> float:
        """Calculate system stability over time"""
        if len(self.meta_tensor_history) < 2:
            return 1.0
            
        # Compare recent states
        recent_states = self.meta_tensor_history[-5:]
        
        # Calculate variance in performance metrics
        variances = []
        for layer in self.cognitive_layers:
            layer_performances = []
            for state in recent_states:
                if layer in state:
                    tensor = state[layer]
                    if tensor.performance_metrics:
                        layer_performances.extend(tensor.performance_metrics.values())
                        
            if layer_performances:
                variances.append(np.var(layer_performances))
                
        # Lower variance = higher stability
        if variances:
            avg_variance = np.mean(variances)
            stability = 1.0 / (1.0 + avg_variance)
        else:
            # No variance data means system is stable (no fluctuations detected)
            stability = 0.85
            
        return stability
        
    def get_current_state(self) -> CognitiveState:
        """Get current cognitive state"""
        return self.state_monitor.get_current_state()
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            "registered_layers": len(self.cognitive_layers),
            "meta_tensor_history_length": len(self.meta_tensor_history),
            "current_state": self.state_monitor.get_current_state(),
            "system_health": self.diagnose_system_health(),
            "monitoring_active": self.state_monitor.monitoring_active
        }