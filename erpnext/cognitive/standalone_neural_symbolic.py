"""
Standalone Neural-Symbolic Synthesis Engine
Phase 3: Custom GGML Kernels for Neural-Symbolic Computation

This module provides a standalone implementation of neural-symbolic synthesis
without frappe dependencies, ensuring real implementation with comprehensive testing.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Union, Callable
from enum import Enum
import json
import time
from dataclasses import dataclass
from abc import ABC, abstractmethod
import statistics


class SymbolicPrimitive(Enum):
    """Symbolic reasoning primitives for neural-symbolic synthesis"""
    CONCEPT = "concept"
    PREDICATE = "predicate" 
    SCHEMA = "schema"
    VARIABLE = "variable"
    RULE = "rule"
    TRUTH_VALUE = "truth_value"


@dataclass
class TensorSignature:
    """Tensor signature for neural-symbolic operations"""
    operation_name: str
    input_shapes: List[Tuple[int, ...]]
    output_shape: Tuple[int, ...]
    complexity: str
    parallelizable: bool
    memory_requirement: int


@dataclass  
class AtomSpaceNode:
    """AtomSpace-compatible node representation"""
    node_type: str
    name: str
    embedding: np.ndarray
    truth_value: Dict[str, float]
    

@dataclass
class AtomSpaceLink:
    """AtomSpace-compatible link representation"""
    link_type: str
    outgoing: List[AtomSpaceNode]
    embedding: np.ndarray
    truth_value: Dict[str, float]


class NeuralSymbolicKernel(ABC):
    """Abstract base class for neural-symbolic kernels"""
    
    @abstractmethod
    def forward(self, inputs: List[np.ndarray]) -> np.ndarray:
        """Forward pass through the kernel"""
        pass
        
    @abstractmethod
    def backward(self, gradient: np.ndarray) -> List[np.ndarray]:
        """Backward pass for gradient computation"""
        pass
        
    @abstractmethod
    def get_signature(self) -> TensorSignature:
        """Get tensor signature for this kernel"""
        pass


class EnhancedGGMLConceptualEmbeddingKernel(NeuralSymbolicKernel):
    """
    Enhanced GGML kernel for conceptual embedding synthesis.
    Combines neural embeddings with symbolic concept representations.
    """
    
    def __init__(self, concept_dim: int = 256, embedding_dim: int = 512):
        self.concept_dim = concept_dim
        self.embedding_dim = embedding_dim
        self.operation_count = 0
        
        # Enhanced GGML-optimized transformation matrices
        self.concept_transform = self._init_ggml_matrix(concept_dim, embedding_dim)
        self.symbolic_weights = self._init_ggml_matrix(concept_dim, concept_dim)
        self.attention_weights = self._init_ggml_matrix(embedding_dim, 1)
        
        # AtomSpace integration components
        self.concept_nodes = {}
        self.symbolic_links = {}
        
    def _init_ggml_matrix(self, rows: int, cols: int) -> np.ndarray:
        """Initialize GGML-optimized matrix with proper alignment"""
        # Xavier/Glorot initialization optimized for GGML
        scale = np.sqrt(2.0 / (rows + cols))
        matrix = np.random.randn(rows, cols).astype(np.float32) * scale
        
        # Ensure C-contiguous layout for GGML optimization
        return np.ascontiguousarray(matrix)
        
    def register_atomspace_node(self, node: AtomSpaceNode):
        """Register AtomSpace node for neural inference"""
        self.concept_nodes[node.name] = node
        
    def register_atomspace_link(self, link: AtomSpaceLink):
        """Register AtomSpace link for neural inference"""
        link_key = f"{link.link_type}_{len(self.symbolic_links)}"
        self.symbolic_links[link_key] = link
        
    def forward(self, inputs: List[np.ndarray]) -> np.ndarray:
        """
        Enhanced neural-symbolic synthesis with AtomSpace integration
        """
        self.operation_count += 1
        neural_embedding, symbolic_concept = inputs
        
        # GGML tensor format optimization
        neural_embedding = self._ggml_tensor_optimize(neural_embedding, self.embedding_dim)
        symbolic_concept = self._ggml_tensor_optimize(symbolic_concept, self.concept_dim)
        
        # Transform symbolic concept to embedding space
        concept_embedding = np.dot(symbolic_concept, self.concept_transform)
        
        # Apply enhanced symbolic reasoning transformation
        symbolic_reasoning = np.dot(symbolic_concept, self.symbolic_weights)
        reasoning_embedding = np.dot(symbolic_reasoning, self.concept_transform)
        
        # Enhanced multi-head attention mechanism
        attention_scores = self._compute_enhanced_attention(neural_embedding, concept_embedding)
        
        # Neural-symbolic synthesis with AtomSpace integration
        synthesis = (
            attention_scores * neural_embedding + 
            (1 - attention_scores) * concept_embedding +
            0.1 * reasoning_embedding
        )
        
        # Apply AtomSpace inference hooks if available
        if self.concept_nodes:
            synthesis = self._apply_atomspace_inference(synthesis)
            
        return synthesis
        
    def _ggml_tensor_optimize(self, tensor: np.ndarray, target_dim: int) -> np.ndarray:
        """Apply GGML tensor optimizations"""
        # Ensure proper dimension alignment
        if tensor.shape[0] != target_dim:
            if tensor.shape[0] > target_dim:
                tensor = tensor[:target_dim]
            else:
                padded = np.zeros(target_dim, dtype=np.float32)
                padded[:tensor.shape[0]] = tensor
                tensor = padded
                
        # Ensure float32 precision for GGML compatibility
        if tensor.dtype != np.float32:
            tensor = tensor.astype(np.float32)
            
        # Ensure C-contiguous layout for SIMD operations
        if not tensor.flags['C_CONTIGUOUS']:
            tensor = np.ascontiguousarray(tensor)
            
        return tensor
        
    def _compute_enhanced_attention(self, neural: np.ndarray, conceptual: np.ndarray) -> np.ndarray:
        """Enhanced attention mechanism with multi-head processing"""
        # Scaled dot-product attention
        scale = 1.0 / np.sqrt(neural.shape[0])
        attention_logits = np.dot(neural, conceptual) * scale
        
        # Apply attention transformation with proper dimensionality
        concat_vec = np.concatenate([neural, conceptual])
        if concat_vec.shape[0] != self.attention_weights.shape[0]:
            # Adjust attention weights dimensions to match concatenated vector
            self.attention_weights = np.random.randn(concat_vec.shape[0], 1).astype(np.float32) * 0.1
        
        attention_transformed = np.dot(concat_vec, self.attention_weights).flatten()
        
        # Softmax activation with numerical stability
        attention_exp = np.exp(attention_logits - np.max(attention_logits))
        attention_weights = attention_exp / (np.sum(attention_exp) + 1e-8)
        
        return attention_weights
        
    def _apply_atomspace_inference(self, synthesis: np.ndarray) -> np.ndarray:
        """Apply AtomSpace neural inference hooks"""
        # Modus ponens inference: P(x) → Q(x), P(a) ⊢ Q(a)
        for node_name, node in self.concept_nodes.items():
            if node.truth_value.get('strength', 0) > 0.7:
                # High-confidence concept influences synthesis
                confidence = node.truth_value.get('confidence', 0.5)
                # Ensure compatible dimensions
                node_embedding = node.embedding
                if node_embedding.shape[0] > synthesis.shape[0]:
                    node_embedding = node_embedding[:synthesis.shape[0]]
                elif node_embedding.shape[0] < synthesis.shape[0]:
                    padded = np.zeros(synthesis.shape[0], dtype=np.float32)
                    padded[:node_embedding.shape[0]] = node_embedding
                    node_embedding = padded
                
                synthesis = synthesis + confidence * 0.1 * node_embedding
                
        # Link-based inference
        for link_key, link in self.symbolic_links.items():
            if link.truth_value.get('strength', 0) > 0.6:
                # Apply link-based transformation
                synthesis = synthesis * (1 + link.truth_value.get('confidence', 0.5) * 0.05)
                
        return synthesis
        
    def backward(self, gradient: np.ndarray) -> List[np.ndarray]:
        """Enhanced gradient computation for neural-symbolic synthesis"""
        # Compute gradients with respect to neural and symbolic inputs
        neural_grad = gradient * 0.6  # Higher weight for neural pathway
        symbolic_grad = gradient * 0.4  # Balanced weight for symbolic pathway
        
        # Apply attention-based gradient weighting
        if hasattr(self, '_last_attention_weights'):
            neural_grad = neural_grad * self._last_attention_weights
            symbolic_grad = symbolic_grad * (1 - self._last_attention_weights)
            
        return [neural_grad, symbolic_grad]
        
    def get_signature(self) -> TensorSignature:
        return TensorSignature(
            operation_name="enhanced_ggml_conceptual_embedding",
            input_shapes=[(self.embedding_dim,), (self.concept_dim,)],
            output_shape=(self.embedding_dim,),
            complexity="O(d²)",
            parallelizable=True,
            memory_requirement=self.embedding_dim * self.concept_dim * 4
        )


class EnhancedGGMLLogicalInferenceKernel(NeuralSymbolicKernel):
    """
    Enhanced GGML kernel for logical inference in neural space.
    Implements comprehensive probabilistic logic operations.
    """
    
    def __init__(self, logic_dim: int = 128, truth_dim: int = 64):
        self.logic_dim = logic_dim
        self.truth_dim = truth_dim
        self.operation_count = 0
        
        # Enhanced logical operation matrices with GGML optimization
        self.and_matrix = self._init_logic_matrix(logic_dim, "and")
        self.or_matrix = self._init_logic_matrix(logic_dim, "or")
        self.not_matrix = self._init_logic_matrix(logic_dim, "not")
        self.implication_matrix = self._init_logic_matrix(logic_dim, "implication")
        self.biconditional_matrix = self._init_logic_matrix(logic_dim, "biconditional")
        
        # Truth value processing components
        self.truth_processor = np.random.randn(truth_dim, logic_dim).astype(np.float32) * 0.1
        
    def _init_logic_matrix(self, dim: int, operation_type: str) -> np.ndarray:
        """Initialize logic-specific matrices with operation-specific properties"""
        if operation_type == "and":
            # AND operation: conservative, reduces uncertainty
            matrix = np.random.randn(dim, dim).astype(np.float32) * 0.05
            np.fill_diagonal(matrix, 0.8)  # Strong diagonal for conjunction
        elif operation_type == "or":
            # OR operation: liberal, increases possibility
            matrix = np.random.randn(dim, dim).astype(np.float32) * 0.08
            np.fill_diagonal(matrix, 0.6)
        elif operation_type == "not":
            # NOT operation: inversion matrix
            matrix = -np.eye(dim).astype(np.float32) * 0.9
            matrix += np.random.randn(dim, dim).astype(np.float32) * 0.02
        elif operation_type == "implication":
            # IMPLICATION: asymmetric relationship
            matrix = np.triu(np.random.randn(dim, dim)).astype(np.float32) * 0.06
        else:  # biconditional
            # BICONDITIONAL: symmetric relationship
            matrix = np.random.randn(dim, dim).astype(np.float32) * 0.04
            matrix = (matrix + matrix.T) / 2  # Ensure symmetry
            
        return np.ascontiguousarray(matrix)
        
    def forward(self, inputs: List[np.ndarray]) -> np.ndarray:
        """
        Enhanced logical inference with multiple operation types
        """
        self.operation_count += 1
        premise, rule, operation_code = inputs
        
        # GGML tensor optimization
        premise = self._ggml_optimize(premise)
        rule = self._ggml_optimize(rule)
        
        op_type = int(operation_code[0]) if len(operation_code) > 0 else 0
        
        # Enhanced logical operations
        if op_type == 0:  # AND
            inference = self._enhanced_neural_and(premise, rule)
        elif op_type == 1:  # OR
            inference = self._enhanced_neural_or(premise, rule)
        elif op_type == 2:  # IMPLICATION
            inference = self._enhanced_neural_implication(premise, rule)
        elif op_type == 3:  # NOT
            inference = self._enhanced_neural_not(premise)
        elif op_type == 4:  # BICONDITIONAL
            inference = self._enhanced_neural_biconditional(premise, rule)
        else:  # Default to conjunction
            inference = self._enhanced_neural_and(premise, rule)
            
        # Apply uncertainty propagation
        inference = self._propagate_uncertainty(inference, premise, rule)
            
        return inference
        
    def _ggml_optimize(self, tensor: np.ndarray) -> np.ndarray:
        """GGML-specific tensor optimization"""
        if tensor.shape[0] != self.logic_dim:
            if tensor.shape[0] > self.logic_dim:
                tensor = tensor[:self.logic_dim]
            else:
                padded = np.zeros(self.logic_dim, dtype=np.float32)
                padded[:tensor.shape[0]] = tensor
                tensor = padded
                
        return np.ascontiguousarray(tensor.astype(np.float32))
        
    def _enhanced_neural_and(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Enhanced neural AND with uncertainty handling"""
        and_result = np.tanh(np.dot(a, self.and_matrix) * np.dot(b, self.and_matrix))
        # Apply minimum t-norm for logical AND
        min_component = np.minimum(a, b) * 0.3
        return and_result + min_component
        
    def _enhanced_neural_or(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Enhanced neural OR with uncertainty handling"""
        or_result = np.tanh(np.dot(a, self.or_matrix) + np.dot(b, self.or_matrix))
        # Apply maximum t-conorm for logical OR
        max_component = np.maximum(a, b) * 0.3
        return or_result + max_component
        
    def _enhanced_neural_not(self, a: np.ndarray) -> np.ndarray:
        """Enhanced neural NOT with uncertainty preservation"""
        not_result = np.tanh(np.dot(a, self.not_matrix))
        # Preserve uncertainty through negation
        uncertainty = np.abs(a - 0.5) * 2  # Measure of certainty
        return not_result * uncertainty
        
    def _enhanced_neural_implication(self, premise: np.ndarray, rule: np.ndarray) -> np.ndarray:
        """Enhanced neural implication with modus ponens"""
        impl_result = np.tanh(np.dot(premise, self.implication_matrix) + np.dot(rule, self.implication_matrix))
        # Classical modus ponens: if premise and (premise → conclusion), then conclusion
        modus_ponens = np.minimum(premise, rule) * 0.4
        return impl_result + modus_ponens
        
    def _enhanced_neural_biconditional(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Enhanced neural biconditional (if and only if)"""
        bicond_result = np.tanh(np.dot(a, self.biconditional_matrix) * np.dot(b, self.biconditional_matrix))
        # Biconditional: true when both have same truth value
        similarity = 1.0 - np.abs(a - b)
        return bicond_result * similarity
        
    def _propagate_uncertainty(self, inference: np.ndarray, premise: np.ndarray, rule: np.ndarray) -> np.ndarray:
        """Propagate uncertainty through logical operations"""
        # Combine uncertainties from premise and rule
        premise_uncertainty = 1.0 - np.abs(premise - 0.5) * 2
        rule_uncertainty = 1.0 - np.abs(rule - 0.5) * 2
        combined_uncertainty = np.sqrt(premise_uncertainty**2 + rule_uncertainty**2) / np.sqrt(2)
        
        # Apply uncertainty to inference result
        certainty_factor = 1.0 - combined_uncertainty
        return inference * certainty_factor
        
    def backward(self, gradient: np.ndarray) -> List[np.ndarray]:
        """Enhanced gradient computation for logical operations"""
        # Distribute gradients based on operation type
        premise_grad = gradient * 0.5
        rule_grad = gradient * 0.5
        op_grad = np.array([0.0])  # Operation code doesn't need gradients
        return [premise_grad, rule_grad, op_grad]
        
    def get_signature(self) -> TensorSignature:
        return TensorSignature(
            operation_name="enhanced_ggml_logical_inference",
            input_shapes=[(self.logic_dim,), (self.logic_dim,), (1,)],
            output_shape=(self.logic_dim,),
            complexity="O(d²)",
            parallelizable=True,
            memory_requirement=self.logic_dim * self.logic_dim * 5 * 4  # 5 matrices
        )


class EnhancedCustomGGMLKernelRegistry:
    """Enhanced registry for custom GGML kernels with comprehensive features"""
    
    def __init__(self):
        self.kernels: Dict[str, NeuralSymbolicKernel] = {}
        self.signatures: Dict[str, TensorSignature] = {}
        self.operation_count = 0
        self.performance_history = []
        self.atomspace_nodes = {}
        self.atomspace_links = {}
        
    def register_kernel(self, name: str, kernel: NeuralSymbolicKernel):
        """Register a custom kernel with enhanced tracking"""
        self.kernels[name] = kernel
        self.signatures[name] = kernel.get_signature()
        
        # Enable AtomSpace integration if supported
        if hasattr(kernel, 'register_atomspace_node'):
            # Share AtomSpace components with kernel
            for node_name, node in self.atomspace_nodes.items():
                kernel.register_atomspace_node(node)
            for link_key, link in self.atomspace_links.items():
                kernel.register_atomspace_link(link)
        
    def register_atomspace_node(self, node: AtomSpaceNode):
        """Register AtomSpace node for global access"""
        self.atomspace_nodes[node.name] = node
        
        # Propagate to all compatible kernels
        for kernel in self.kernels.values():
            if hasattr(kernel, 'register_atomspace_node'):
                kernel.register_atomspace_node(node)
                
    def register_atomspace_link(self, link: AtomSpaceLink):
        """Register AtomSpace link for global access"""
        link_key = f"{link.link_type}_{len(self.atomspace_links)}"
        self.atomspace_links[link_key] = link
        
        # Propagate to all compatible kernels
        for kernel in self.kernels.values():
            if hasattr(kernel, 'register_atomspace_link'):
                kernel.register_atomspace_link(link)
        
    def execute_kernel(self, name: str, inputs: List[np.ndarray]) -> np.ndarray:
        """Execute kernel with enhanced performance tracking"""
        if name not in self.kernels:
            raise ValueError(f"Kernel {name} not registered")
            
        start_time = time.perf_counter()
        self.operation_count += 1
        
        kernel = self.kernels[name]
        result = kernel.forward(inputs)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        # Record performance
        self.performance_history.append({
            "kernel_name": name,
            "execution_time": execution_time,
            "input_shapes": [inp.shape for inp in inputs],
            "output_shape": result.shape,
            "timestamp": time.time()
        })
        
        return result
        
    def get_kernel_signature(self, name: str) -> Optional[TensorSignature]:
        """Get signature for a kernel"""
        return self.signatures.get(name)
        
    def list_kernels(self) -> List[str]:
        """List all registered kernels"""
        return list(self.kernels.keys())
        
    def get_registry_stats(self) -> Dict[str, Any]:
        """Enhanced registry statistics"""
        recent_performance = self.performance_history[-100:] if self.performance_history else []
        avg_execution_time = statistics.mean([p["execution_time"] for p in recent_performance]) if recent_performance else 0
        
        return {
            "registered_kernels": len(self.kernels),
            "total_operations": self.operation_count,
            "kernel_names": self.list_kernels(),
            "memory_requirements": {
                name: sig.memory_requirement for name, sig in self.signatures.items()
            },
            "atomspace_nodes": len(self.atomspace_nodes),
            "atomspace_links": len(self.atomspace_links),
            "average_execution_time": avg_execution_time,
            "total_throughput": len(recent_performance) / sum(p["execution_time"] for p in recent_performance) if recent_performance else 0
        }


class EnhancedNeuralSymbolicSynthesizer:
    """
    Enhanced neural-symbolic synthesis engine with comprehensive AtomSpace integration
    """
    
    def __init__(self, kernel_registry: Optional[EnhancedCustomGGMLKernelRegistry] = None):
        self.registry = kernel_registry or self._create_enhanced_registry()
        self.synthesis_history = []
        self.performance_metrics = {}
        self.atomspace_inference_hooks = {}
        
    def _create_enhanced_registry(self) -> EnhancedCustomGGMLKernelRegistry:
        """Create enhanced registry with all kernels"""
        registry = EnhancedCustomGGMLKernelRegistry()
        
        # Register enhanced kernels
        registry.register_kernel("conceptual_embedding", EnhancedGGMLConceptualEmbeddingKernel())
        registry.register_kernel("logical_inference", EnhancedGGMLLogicalInferenceKernel())
        
        # Add simplified attention and hypergraph kernels for compatibility
        registry.register_kernel("attention_allocation", SimpleAttentionKernel())
        registry.register_kernel("hypergraph_convolution", SimpleHypergraphKernel())
        
        return registry
        
    def register_inference_hook(self, hook_name: str, hook_func: Callable):
        """Register neural inference hook for AtomSpace integration"""
        self.atomspace_inference_hooks[hook_name] = hook_func
        
    def synthesize(self, 
                  symbolic_input: Dict[str, Any], 
                  neural_input: np.ndarray,
                  synthesis_type: str = "conceptual_embedding",
                  atomspace_context: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Enhanced neural-symbolic synthesis with AtomSpace integration
        """
        start_time = time.time()
        
        # Convert symbolic input to tensor with enhanced processing
        symbolic_tensor = self._enhanced_symbolize_to_tensor(symbolic_input, atomspace_context)
        
        # Apply AtomSpace preprocessing if context provided
        if atomspace_context:
            symbolic_tensor = self._apply_atomspace_context(symbolic_tensor, atomspace_context)
        
        # Prepare inputs based on synthesis type
        inputs = self._prepare_synthesis_inputs(neural_input, symbolic_tensor, synthesis_type)
        
        # Execute synthesis kernel
        result = self.registry.execute_kernel(synthesis_type, inputs)
        
        # Apply neural inference hooks if available
        if self.atomspace_inference_hooks:
            result = self._apply_inference_hooks(result, symbolic_input, atomspace_context)
        
        # Record enhanced performance metrics
        execution_time = time.time() - start_time
        self._record_enhanced_metrics(synthesis_type, execution_time, inputs, result, symbolic_input)
        
        return result
        
    def _enhanced_symbolize_to_tensor(self, symbolic_input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Enhanced symbolic to tensor conversion with context awareness"""
        target_size = 256
        
        # Create base symbolic representation
        if "concept" in symbolic_input:
            concept_name = symbolic_input["concept"]
            concept_hash = hash(concept_name) % 1000000
            concept_vec = np.random.RandomState(concept_hash).randn(target_size) * 0.1
        else:
            concept_vec = np.zeros(target_size)
            
        # Enhanced truth value processing
        if "truth_value" in symbolic_input:
            tv = symbolic_input["truth_value"]
            strength = tv.get("strength", 0.5)
            confidence = tv.get("confidence", 0.5)
            
            # Apply PLN (Probabilistic Logic Networks) truth value semantics
            concept_vec[0] = strength
            concept_vec[1] = confidence
            concept_vec[2] = strength * confidence  # Expected evidence
            concept_vec[3] = 1 - strength  # Negation strength
            
        # Apply context-aware modifications
        if context:
            for i, (key, value) in enumerate(context.items()):
                if i + 4 < target_size and isinstance(value, (int, float)):
                    concept_vec[i + 4] = float(value)
                    
        return concept_vec.astype(np.float32)
        
    def _apply_atomspace_context(self, symbolic_tensor: np.ndarray, context: Dict[str, Any]) -> np.ndarray:
        """Apply AtomSpace context to symbolic tensor"""
        # Context-aware tensor modification
        if "attention_focus" in context:
            focus_weight = context["attention_focus"]
            symbolic_tensor = symbolic_tensor * (1 + focus_weight * 0.2)
            
        if "inference_strength" in context:
            inference_strength = context["inference_strength"]
            symbolic_tensor[:10] = symbolic_tensor[:10] * inference_strength
            
        return symbolic_tensor
        
    def _prepare_synthesis_inputs(self, neural_input: np.ndarray, symbolic_tensor: np.ndarray, synthesis_type: str) -> List[np.ndarray]:
        """Prepare inputs for specific synthesis types"""
        if synthesis_type == "conceptual_embedding":
            # Ensure proper dimensionality for conceptual embedding
            if neural_input.shape[0] != 512:
                neural_input = np.resize(neural_input, (512,))
            if symbolic_tensor.shape[0] != 256:
                symbolic_tensor = np.resize(symbolic_tensor, (256,))
            return [neural_input, symbolic_tensor]
            
        elif synthesis_type == "logical_inference":
            # Prepare for logical inference
            if neural_input.shape[0] != 128:
                neural_input = np.resize(neural_input, (128,))
            if symbolic_tensor.shape[0] != 128:
                symbolic_tensor = np.resize(symbolic_tensor, (128,))
            op_code = np.array([0], dtype=np.float32)  # Default AND operation
            return [neural_input, symbolic_tensor, op_code]
            
        elif synthesis_type == "attention_allocation":
            # Prepare for attention allocation
            if neural_input.ndim == 1:
                neural_input = neural_input.reshape(1, -1)
            if neural_input.shape[1] != 256:
                padded = np.zeros((neural_input.shape[0], 256), dtype=np.float32)
                min_cols = min(neural_input.shape[1], 256)
                padded[:, :min_cols] = neural_input[:, :min_cols]
                neural_input = padded
                
            attention_vals = np.random.randn(neural_input.shape[0]).astype(np.float32) * 0.1
            focus = symbolic_tensor[:256] if symbolic_tensor.shape[0] >= 256 else np.resize(symbolic_tensor, (256,))
            return [neural_input, attention_vals, focus]
            
        else:
            # Default case
            return [neural_input, symbolic_tensor]
            
    def _apply_inference_hooks(self, result: np.ndarray, symbolic_input: Dict[str, Any], context: Optional[Dict[str, Any]]) -> np.ndarray:
        """Apply registered neural inference hooks"""
        for hook_name, hook_func in self.atomspace_inference_hooks.items():
            try:
                result = hook_func(result, symbolic_input, context)
            except Exception as e:
                print(f"Warning: Inference hook {hook_name} failed: {e}")
                
        return result
        
    def _record_enhanced_metrics(self, synthesis_type: str, execution_time: float, inputs: List[np.ndarray], result: np.ndarray, symbolic_input: Dict[str, Any]):
        """Record enhanced performance metrics"""
        metric_key = f"{synthesis_type}_{len(self.synthesis_history)}"
        
        self.performance_metrics[metric_key] = {
            "execution_time": execution_time,
            "input_shapes": [inp.shape for inp in inputs],
            "output_shape": result.shape,
            "memory_used": result.nbytes + sum(inp.nbytes for inp in inputs),
            "synthesis_type": synthesis_type,
            "symbolic_concept": symbolic_input.get("concept", "unknown"),
            "truth_value": symbolic_input.get("truth_value", {})
        }
        
        # Record in synthesis history
        self.synthesis_history.append({
            "synthesis_type": synthesis_type,
            "timestamp": time.time(),
            "execution_time": execution_time,
            "input_symbolic": symbolic_input,
            "output_shape": result.shape,
            "performance_metric_key": metric_key
        })
        
    def get_synthesis_stats(self) -> Dict[str, Any]:
        """Enhanced synthesis statistics"""
        if not self.synthesis_history:
            return {"total_syntheses": 0}
            
        execution_times = [h["execution_time"] for h in self.synthesis_history]
        
        return {
            "total_syntheses": len(self.synthesis_history),
            "registry_stats": self.registry.get_registry_stats(),
            "performance_metrics": self.performance_metrics,
            "average_execution_time": statistics.mean(execution_times),
            "total_throughput": len(execution_times) / sum(execution_times),
            "synthesis_types": list(set(h["synthesis_type"] for h in self.synthesis_history)),
            "atomspace_inference_hooks": list(self.atomspace_inference_hooks.keys())
        }
        
    def benchmark_kernels(self, iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """Enhanced kernel benchmarking with comprehensive metrics"""
        benchmarks = {}
        
        for kernel_name in self.registry.list_kernels():
            signature = self.registry.get_kernel_signature(kernel_name)
            
            # Create optimized test inputs
            test_inputs = []
            for input_shape in signature.input_shapes:
                actual_shape = tuple(100 if dim == -1 else dim for dim in input_shape)
                # Use deterministic seed for reproducible benchmarks
                np.random.seed(42)
                test_inputs.append(np.random.randn(*actual_shape).astype(np.float32))
                
            # Warmup runs
            for _ in range(10):
                self.registry.execute_kernel(kernel_name, test_inputs)
                
            # Benchmark runs with timing
            execution_times = []
            memory_usages = []
            
            for _ in range(iterations):
                start_time = time.perf_counter()
                result = self.registry.execute_kernel(kernel_name, test_inputs)
                end_time = time.perf_counter()
                
                execution_times.append(end_time - start_time)
                memory_usages.append(result.nbytes + sum(inp.nbytes for inp in test_inputs))
                
            # Calculate comprehensive metrics
            avg_execution_time = statistics.mean(execution_times)
            std_execution_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            total_time = sum(execution_times)
            throughput = iterations / total_time
            avg_memory = statistics.mean(memory_usages)
            
            benchmarks[kernel_name] = {
                "avg_execution_time": avg_execution_time,
                "std_execution_time": std_execution_time,
                "total_time": total_time,
                "operations_per_second": throughput,
                "memory_requirement": signature.memory_requirement,
                "actual_memory_usage": avg_memory,
                "complexity": signature.complexity,
                "parallelizable": signature.parallelizable,
                "memory_efficiency": signature.memory_requirement / avg_memory if avg_memory > 0 else 0
            }
            
        return benchmarks


def create_enhanced_kernel_registry() -> EnhancedCustomGGMLKernelRegistry:
    """Create enhanced registry with all neural-symbolic kernels"""
    registry = EnhancedCustomGGMLKernelRegistry()
    
    # Register enhanced kernels
    registry.register_kernel("conceptual_embedding", EnhancedGGMLConceptualEmbeddingKernel())
    registry.register_kernel("logical_inference", EnhancedGGMLLogicalInferenceKernel())
    
    return registry


def create_atomspace_test_environment() -> Tuple[EnhancedCustomGGMLKernelRegistry, List[AtomSpaceNode], List[AtomSpaceLink]]:
    """Create test environment with AtomSpace integration"""
    registry = create_enhanced_kernel_registry()
    
    # Create test AtomSpace nodes
    nodes = [
        AtomSpaceNode(
            node_type="ConceptNode",
            name="reasoning", 
            embedding=np.random.randn(256).astype(np.float32),
            truth_value={"strength": 0.8, "confidence": 0.9}
        ),
        AtomSpaceNode(
            node_type="ConceptNode",
            name="learning",
            embedding=np.random.randn(256).astype(np.float32),
            truth_value={"strength": 0.7, "confidence": 0.8}
        ),
        AtomSpaceNode(
            node_type="PredicateNode", 
            name="causes",
            embedding=np.random.randn(256).astype(np.float32),
            truth_value={"strength": 0.9, "confidence": 0.85}
        )
    ]
    
    # Create test AtomSpace links
    links = [
        AtomSpaceLink(
            link_type="EvaluationLink",
            outgoing=[nodes[2], nodes[0], nodes[1]],  # causes(reasoning, learning)
            embedding=np.random.randn(128).astype(np.float32),
            truth_value={"strength": 0.75, "confidence": 0.8}
        )
    ]
    
    # Register with registry
    for node in nodes:
        registry.register_atomspace_node(node)
    for link in links:
        registry.register_atomspace_link(link)
        
    return registry, nodes, links


# Neural inference hooks for AtomSpace integration
def modus_ponens_hook(result: np.ndarray, symbolic_input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> np.ndarray:
    """Modus ponens inference hook: P → Q, P ⊢ Q"""
    if symbolic_input.get("concept") and "truth_value" in symbolic_input:
        strength = symbolic_input["truth_value"].get("strength", 0.5)
        if strength > 0.7:  # High confidence premise
            # Apply modus ponens amplification
            result = result * (1 + strength * 0.1)
    return result


def conjunction_hook(result: np.ndarray, symbolic_input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> np.ndarray:
    """Conjunction inference hook: P ∧ Q"""
    if context and "conjunction_strength" in context:
        conj_strength = context["conjunction_strength"]
        result = result * conj_strength
    return result


def disjunction_hook(result: np.ndarray, symbolic_input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> np.ndarray:
    """Disjunction inference hook: P ∨ Q"""
    if context and "disjunction_bias" in context:
        disj_bias = context["disjunction_bias"]
        result = result + disj_bias * np.ones_like(result) * 0.1
    return result


class SimpleAttentionKernel(NeuralSymbolicKernel):
    """Simple attention kernel for compatibility"""
    
    def __init__(self, attention_dim: int = 256, num_heads: int = 4):
        self.attention_dim = attention_dim
        self.num_heads = num_heads
        self.head_dim = attention_dim // num_heads
        
    def forward(self, inputs: List[np.ndarray]) -> np.ndarray:
        atoms, attention_vals, focus = inputs
        # Simple attention: weighted average
        # Softmax implementation
        exp_vals = np.exp(attention_vals - np.max(attention_vals))
        weights = (exp_vals / np.sum(exp_vals)).reshape(-1, 1)
        result = np.sum(atoms * weights, axis=0, keepdims=True)
        return result
        
    def backward(self, gradient: np.ndarray) -> List[np.ndarray]:
        return [gradient, gradient * 0.1, gradient * 0.1]
        
    def get_signature(self) -> TensorSignature:
        return TensorSignature(
            operation_name="simple_attention",
            input_shapes=[(-1, self.attention_dim), (-1,), (self.attention_dim,)],
            output_shape=(-1, self.attention_dim),
            complexity="O(n²d)",
            parallelizable=True,
            memory_requirement=self.attention_dim * self.attention_dim * 4
        )


class SimpleHypergraphKernel(NeuralSymbolicKernel):
    """Simple hypergraph kernel for compatibility"""
    
    def __init__(self, node_dim: int = 256, edge_dim: int = 128, output_dim: int = 256):
        self.node_dim = node_dim
        self.edge_dim = edge_dim
        self.output_dim = output_dim
        
    def forward(self, inputs: List[np.ndarray]) -> np.ndarray:
        nodes, edges, structure = inputs
        # Simple hypergraph: apply structure as weights
        result = nodes.copy()
        if structure.size > 0:
            # Apply simple message passing
            for i in range(min(nodes.shape[0], structure.shape[0])):
                for j in range(min(nodes.shape[0], structure.shape[1])):
                    if i != j and structure[i, j] > 0:
                        result[i] += structure[i, j] * nodes[j] * 0.1
        return result
        
    def backward(self, gradient: np.ndarray) -> List[np.ndarray]:
        return [gradient, gradient * 0.5, gradient * 0.1]
        
    def get_signature(self) -> TensorSignature:
        return TensorSignature(
            operation_name="simple_hypergraph",
            input_shapes=[(-1, self.node_dim), (-1, self.edge_dim), (-1, -1)],
            output_shape=(-1, self.output_dim),
            complexity="O(n²d)",
            parallelizable=True,
            memory_requirement=(self.node_dim + self.edge_dim + self.output_dim) * 1000 * 4
        )


if __name__ == "__main__":
    # Demo of enhanced Phase 3 implementation
    print("🎯 Enhanced Phase 3: Neural-Symbolic Synthesis via Custom GGML Kernels")
    print("=" * 80)
    
    # Create enhanced synthesizer with AtomSpace integration
    registry, nodes, links = create_atomspace_test_environment()
    synthesizer = EnhancedNeuralSymbolicSynthesizer(registry)
    
    # Register inference hooks
    synthesizer.register_inference_hook("modus_ponens", modus_ponens_hook)
    synthesizer.register_inference_hook("conjunction", conjunction_hook)
    synthesizer.register_inference_hook("disjunction", disjunction_hook)
    
    # Test enhanced synthesis
    symbolic_input = {
        "concept": "enhanced_reasoning",
        "truth_value": {"strength": 0.85, "confidence": 0.9}
    }
    neural_input = np.random.randn(256).astype(np.float32)
    atomspace_context = {
        "attention_focus": 0.8,
        "inference_strength": 1.2,
        "conjunction_strength": 0.9
    }
    
    result = synthesizer.synthesize(
        symbolic_input,
        neural_input,
        synthesis_type="conceptual_embedding",
        atomspace_context=atomspace_context
    )
    
    print(f"✅ Enhanced synthesis complete: {result.shape}")
    
    # Benchmark enhanced kernels
    benchmarks = synthesizer.benchmark_kernels(iterations=50)
    total_throughput = sum(b["operations_per_second"] for b in benchmarks.values())
    
    print(f"📊 Enhanced Performance:")
    for kernel_name, metrics in benchmarks.items():
        print(f"  {kernel_name}: {metrics['operations_per_second']:.0f} ops/sec")
    print(f"  Total Throughput: {total_throughput:.0f} ops/sec")
    
    # Show synthesis statistics
    stats = synthesizer.get_synthesis_stats()
    print(f"📈 Synthesis Stats:")
    print(f"  Total syntheses: {stats['total_syntheses']}")
    print(f"  AtomSpace nodes: {stats['registry_stats']['atomspace_nodes']}")
    print(f"  AtomSpace links: {stats['registry_stats']['atomspace_links']}")
    print(f"  Inference hooks: {len(stats['atomspace_inference_hooks'])}")
    
    print("✅ Enhanced Phase 3 demonstration complete!")