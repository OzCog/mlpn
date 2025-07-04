# Cognitive Architecture for ERPNext

## Overview

This cognitive architecture implementation provides a comprehensive framework for artificial intelligence within the ERPNext system, featuring:

- **Tensor Kernel Cohesion Layer**: Backend-abstracted tensor computation with GGML, Kokkos, and A0ML integration
- **Cognitive Grammar Field**: Hypergraph knowledge representation using AtomSpace and PLN
- **ECAN Attention Allocation**: Economic attention allocation with cognitive wages and rents
- **Meta-Cognitive Enhancement**: Recursive introspection and system monitoring

## Architecture Components

### 1. Tensor Kernel (`tensor_kernel.py`)

The tensor kernel provides unified tensor computation across different backends:

```python
from erpnext.cognitive.tensor_kernel import TensorKernel, initialize_default_shapes

# Initialize tensor kernel
kernel = TensorKernel(backend="cpu", precision="float32")
initialize_default_shapes(kernel)

# Create tensors
tensor = kernel.create_tensor([[1, 2, 3], [4, 5, 6]])

# Perform operations
result = kernel.tensor_contraction(tensor_a, tensor_b)
```

**Key Features:**
- Multiple tensor format support (GGML, Kokkos, A0ML, NumPy)
- Canonical tensor shape specifications
- Parallel operations for distributed computation
- Meta-learning parameter updates
- Scheme-based configuration

### 2. Cognitive Grammar (`cognitive_grammar.py`)

Implements knowledge representation using hypergraphs and probabilistic logic:

```python
from erpnext.cognitive.cognitive_grammar import CognitiveGrammar

# Initialize grammar system
grammar = CognitiveGrammar()

# Create entities
person = grammar.create_entity("person")
john = grammar.create_entity("john")

# Create relationships
john_is_person = grammar.create_relationship(john, person, "inheritance")

# Perform inference
result = grammar.infer_knowledge("deduction", premise1=link1, premise2=link2)
```

**Key Features:**
- AtomSpace hypergraph representation
- PLN (Probabilistic Logic Networks) inference
- Prime-factorized indexing for maximum density
- Template-based pattern recognition
- Truth value propagation

### 3. Attention Allocation (`attention_allocation.py`)

Economic attention allocation system with activation spreading:

```python
from erpnext.cognitive.attention_allocation import ECANAttention

# Initialize attention system
attention = ECANAttention(atomspace_connections)

# Focus attention
attention.focus_attention("important_concept", 3.0)

# Run attention cycle
attention.run_attention_cycle(["concept1", "concept2"])

# Get attention focus
top_focused = attention.get_attention_focus(10)
```

**Key Features:**
- Short/Long/Very-Long-term importance tracking
- Economic wage and rent allocation
- Activation spreading (PageRank-style)
- Attention tensor visualization
- Utility and novelty calculation

### 4. Meta-Cognitive System (`meta_cognitive.py`)

Recursive introspection and system monitoring:

```python
from erpnext.cognitive.meta_cognitive import MetaCognitive, MetaLayer

# Initialize meta-cognitive system
meta = MetaCognitive()

# Register cognitive layers
meta.register_layer(MetaLayer.TENSOR_KERNEL, tensor_kernel)
meta.register_layer(MetaLayer.COGNITIVE_GRAMMAR, grammar)

# Update meta-state
meta.update_meta_state()

# Perform introspection
introspection = meta.perform_deep_introspection(MetaLayer.TENSOR_KERNEL)

# Diagnose system health
health = meta.diagnose_system_health()
```

**Key Features:**
- Meta-tensor state tracking
- Recursive introspection capabilities
- System health monitoring
- Performance metrics collection
- Coherence measurement between layers

## Scheme Configuration

The system includes comprehensive Scheme specifications in `cognitive_config.scm`:

```scheme
;; Tensor shape definitions
(define (tensor-shape attention) 
  '((batch_size 1) (sequence_length 512) (hidden_dim 256)))

;; Pattern matching
(define (pattern-match atomspace entity)
  (filter (lambda (atom) (type atom concept)) (atomspace-atoms)))

;; Attention allocation
(define (attention-allocate atom-id type value)
  (set-attention atom-id (+ (get-attention atom-id) value)))
```

## Integration Example

Complete system integration:

```python
from erpnext.cognitive import *

# Initialize all components
tensor_kernel = TensorKernel()
grammar = CognitiveGrammar()
attention = ECANAttention()
meta_cognitive = MetaCognitive()

# Register with meta-cognitive system
meta_cognitive.register_layer(MetaLayer.TENSOR_KERNEL, tensor_kernel)
meta_cognitive.register_layer(MetaLayer.COGNITIVE_GRAMMAR, grammar)
meta_cognitive.register_layer(MetaLayer.ATTENTION_ALLOCATION, attention)

# Create knowledge scenario
entity1 = grammar.create_entity("customer")
entity2 = grammar.create_entity("order")
relationship = grammar.create_relationship(entity1, entity2)

# Focus attention on important entities
attention.focus_attention(entity1, 3.0)

# Perform tensor operations
knowledge_tensor = tensor_kernel.create_tensor([[1, 0], [0, 1]])

# Update meta-cognitive state
meta_cognitive.update_meta_state()

# Run complete cognitive cycle
attention.run_attention_cycle([entity1, entity2])

# Get system statistics
health = meta_cognitive.diagnose_system_health()
```

## Running Tests

Run the validation tests to ensure proper functionality:

```bash
cd erpnext/cognitive
python test_validation.py
```

## Running Demo

Execute the comprehensive demonstration:

```bash
cd erpnext/cognitive
python demo.py
```

## Key Benefits

1. **Unified Tensor Computation**: Seamless integration with GGML, Kokkos, and A0ML for distributed cognition
2. **Knowledge Representation**: Hypergraph-based knowledge with probabilistic inference
3. **Attention Management**: Economic allocation of cognitive resources
4. **Self-Monitoring**: Recursive introspection and system health tracking
5. **Scheme Integration**: Functional programming specifications for cognitive operations

## Recursive Neural-Symbolic Integration

The architecture implements recursive neural-symbolic integration through:

- **Tensor-Symbolic Bridging**: Conversion between tensor representations and symbolic knowledge
- **Multi-layer Coherence**: Ensuring consistency across cognitive layers
- **Emergent Behavior**: System-level intelligence emerging from component interactions
- **Distributed Cognition**: Parallel processing across multiple cognitive kernels

## Future Extensions

The architecture is designed for extension with:

- **Advanced GGML Integration**: Custom tensor operations for cognitive workloads
- **Distributed Memory Systems**: Integration with Mem0 and Node9 memory architectures
- **Real-time Learning**: Online adaptation and knowledge acquisition
- **Multi-modal Processing**: Vision, language, and reasoning integration
- **Quantum Cognitive Operations**: Quantum-enhanced tensor computation

## Performance Considerations

- **Memory Management**: Efficient tensor caching and garbage collection
- **Parallel Processing**: Multi-threaded attention spreading and inference
- **Scalability**: Designed for large-scale knowledge bases and attention networks
- **Real-time Operation**: Low-latency tensor operations for interactive systems

This cognitive architecture provides a solid foundation for building intelligent ERP systems with human-like reasoning, attention, and learning capabilities.