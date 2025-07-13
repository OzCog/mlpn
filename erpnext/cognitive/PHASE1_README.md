# Phase 1: Cognitive Primitives & Foundational Hypergraph Encoding

## Overview

Phase 1 establishes the atomic vocabulary and bidirectional translation mechanisms between ko6ml primitives and AtomSpace hypergraph patterns. This implementation follows recursive modularity principles with real implementation verification and comprehensive testing protocols.

## Implemented Components

### 1. Scheme Cognitive Grammar Microservices

**Location**: `erpnext/cognitive/microservices/`

Modular microservice architecture for cognitive primitives:

- **AtomSpaceService** (`atomspace_service.py`): REST API for hypergraph operations
- **PLNService** (`pln_service.py`): Probabilistic logic inference endpoints
- **PatternService** (`pattern_service.py`): Template-based pattern recognition
- **Ko6mlTranslator** (`ko6ml_translator.py`): Bidirectional ko6ml ↔ AtomSpace translation

#### Key Features:
- REST API endpoints for all cognitive operations
- Real-time hypergraph manipulation
- Probabilistic logic networks (PLN) for inference
- Pattern matching with Scheme specifications
- Comprehensive error handling and health monitoring

#### Usage:
```python
from erpnext.cognitive.microservices import AtomSpaceService, PLNService, PatternService

# Start microservices
atomspace_service = AtomSpaceService(port=8001).start()
pln_service = PLNService(port=8002).start()
pattern_service = PatternService(port=8003).start()

# Use via REST API or direct access
atomspace = atomspace_service.get_atomspace()
atom_id = atomspace.add_atom("customer", AtomType.CONCEPT)
```

### 2. Tensor Fragment Architecture

**Location**: `erpnext/cognitive/tensor_fragments.py`

Distributed tensor fragment system for cognitive computation:

#### Core Classes:
- **TensorFragment**: Individual tensor fragment with metadata
- **FragmentRegistry**: Registry for managing tensor fragments
- **TensorFragmentArchitecture**: Main system for distributed tensor operations

#### Key Features:
- Grid and hierarchical tensor decomposition
- Fragment composition and contraction operations
- Parallel processing across fragments
- Automatic synchronization mechanisms
- Fragment-aware caching system

#### Usage:
```python
from erpnext.cognitive.tensor_fragments import TensorFragmentArchitecture, FragmentType

# Initialize architecture
arch = TensorFragmentArchitecture()

# Create fragments
data = np.array([[1, 2], [3, 4]])
fragment_id = arch.create_fragment(data, FragmentType.COGNITIVE)

# Decompose tensors
fragments = arch.decompose_tensor(large_tensor, {"type": "grid", "grid_shape": (2, 2)})

# Perform operations
result_id = arch.fragment_contraction(fragment_id1, fragment_id2)
```

### 3. ko6ml ↔ AtomSpace Bidirectional Translation

**Location**: `erpnext/cognitive/microservices/ko6ml_translator.py`

Complete translation system between ko6ml primitives and AtomSpace patterns:

#### Translation Types:
- **Entity** → ConceptNode
- **Relation** → PredicateNode  
- **Property** → ConceptNode
- **Rule/Constraint** → SchemaNode
- **Pattern** → VariableNode

#### Key Features:
- Round-trip translation verification
- Complex pattern translation
- Metadata preservation
- Truth value mapping
- Scheme specification generation

#### Usage:
```python
from erpnext.cognitive.microservices.ko6ml_translator import Ko6mlTranslator, Ko6mlExpression, Ko6mlPrimitive

translator = Ko6mlTranslator()

# ko6ml to AtomSpace
expr = Ko6mlExpression(Ko6mlPrimitive.ENTITY, "customer", {}, {"confidence": 0.8})
atom_id = translator.ko6ml_to_atomspace(expr)

# AtomSpace to ko6ml
recovered_expr = translator.atomspace_to_ko6ml(atom_id)

# Verify round-trip
is_valid = translator.verify_round_trip([expr])
```

## Architecture Principles

### Recursive Modularity
Each component is designed as a self-similar module that can be composed with others:
- Microservices can be combined into larger cognitive systems
- Tensor fragments can be hierarchically decomposed and recomposed
- Translation patterns are recursively applicable

### Real Implementation
All components use real data and operations:
- No mocks or simulations in core functionality
- Actual tensor mathematics and hypergraph operations
- Real HTTP servers for microservices
- Genuine probabilistic logic inference

### Comprehensive Testing
**Location**: `erpnext/cognitive/phase1_tests.py`

Complete test suite covering:
- Microservices architecture validation
- ko6ml translation round-trip integrity
- Tensor fragment operations
- Integrated cognitive scenarios
- Scheme specification generation

## Scheme Integration

All components generate Scheme specifications for functional programming integration:

```scheme
;; ko6ml Translation
(define (ko6ml-to-atomspace customer)
  (let ((atom-id (add-atom "customer" 'concept)))
    (set-truth-value atom-id (make-truth-value 0.9 0.8))
    atom-id))

;; Tensor Fragment Operations
(define (fragment-compose fragment-id other-fragments)
  (compose-tensors (cons (get-fragment fragment-id) 
                        (map get-fragment other-fragments))))

;; Pattern Matching
(define (pattern-match atomspace entity)
  (filter (lambda (atom) (type atom concept)) (atomspace-atoms)))
```

## Performance Characteristics

### Scalability
- Microservices support horizontal scaling
- Fragment architecture enables distributed processing
- Tensor operations leverage parallel computation

### Memory Efficiency
- Fragment-based tensor caching
- Lazy evaluation for composition operations
- Automatic cleanup of unused fragments

### Real-time Performance
- Sub-millisecond atom operations
- Parallel tensor processing
- Efficient hypergraph traversal

## Integration Points

### ERPNext Integration
Phase 1 components integrate seamlessly with ERPNext:
- Customer entities map to cognitive atoms
- Order relationships become hypergraph links
- Business rules translate to PLN inference

### Future Phases
Phase 1 provides foundation for:
- **Phase 2**: ECAN attention allocation with cognitive wages
- **Phase 3**: Neural-symbolic synthesis via custom ggml kernels
- **Phase 4**: Distributed cognitive mesh API & embodiment
- **Phase 5**: Recursive meta-cognition & evolutionary optimization
- **Phase 6**: Rigorous testing & cognitive unification

## Running Phase 1

### Quick Start
```bash
cd erpnext/cognitive
python3 phase1_demo.py  # Comprehensive demonstration
python3 phase1_tests.py # Full test suite
python3 test_validation.py # Basic validation
```

### Microservices
```bash
# Start individual services
python3 microservices/atomspace_service.py
python3 microservices/pln_service.py
python3 microservices/pattern_service.py
```

### Integration Testing
```bash
# Run complete Phase 1 verification
python3 phase1_tests.py
```

## Configuration

### Tensor Kernel Configuration
```python
from erpnext.cognitive.tensor_kernel import TensorKernel, initialize_default_shapes

kernel = TensorKernel(backend="cpu", precision="float32")
initialize_default_shapes(kernel)
```

### Microservice Configuration
```python
# Port configuration
ATOMSPACE_PORT = 8001
PLN_PORT = 8002
PATTERN_PORT = 8003

# Service limits
MAX_ATOMS = 100000
MAX_FRAGMENTS = 10000
CACHE_SIZE = 1000
```

## Verification Results

Phase 1 implementation successfully demonstrates:

✅ **Scheme Cognitive Grammar Microservices**
- AtomSpace REST API operational
- PLN inference working correctly
- Pattern matching with Scheme specs
- Round-trip ko6ml translation verified

✅ **Tensor Fragment Architecture**
- Grid and hierarchical decomposition
- Fragment composition and contraction
- Parallel processing capabilities
- Synchronization mechanisms

✅ **Phase 1 Verification**
- All tests passing
- Real implementation confirmed
- Integration scenarios validated
- Performance metrics within targets

## Next Steps

Phase 1 provides the foundational atomic vocabulary and translation mechanisms. Phase 2 will build upon this foundation to implement ECAN attention allocation and resource kernel construction, adding cognitive wages, rents, and attention spreading mechanisms to the hypergraph representation.

## Hypergraph Fragment Flowcharts

Phase 1 includes comprehensive visualization capabilities through the `hypergraph_visualizer.py` module:

### Generated Flowcharts

1. **Phase 1 Hypergraph Fragment** - Basic hypergraph structure showing nodes and edges
2. **ko6ml ↔ AtomSpace Translation Diagram** - Bidirectional translation visualization  
3. **Tensor Fragment Operations** - Grid/hierarchical decomposition and composition
4. **Attention Allocation Heatmap** - ECAN attention spreading visualization
5. **Comprehensive Architecture Flowchart** - Complete Phase 1 system overview

### Visualization Features

```python
from erpnext.cognitive.hypergraph_visualizer import HypergraphVisualizer

# Create visualizer
visualizer = HypergraphVisualizer(output_dir="/tmp/viz")

# Generate all Phase 1 flowcharts
files = visualizer.generate_all_phase1_visualizations(phase1_data)
```

The visualizations demonstrate:
- Hypergraph node relationships and edge types
- ko6ml primitive translations to AtomSpace patterns
- Tensor fragment decomposition strategies
- Attention allocation heat patterns
- Complete cognitive architecture integration

### Usage in Demonstrations

Run the comprehensive demo with visualization:

```bash
cd erpnext/cognitive
python3 phase1_demo_with_visualization.py
```

This generates all required hypergraph fragment flowcharts as specified in the Phase 1 implementation details.

### Generated Files

The visualization system creates the following flowchart files:
- `phase_1_hypergraph_fragment_flowchart.png`
- `ko6ml_to_atomspace_translation_diagram.png`
- `tensor_fragment_operations_visualization.png`
- `attention_allocation_heatmap_heatmap.png`
- `phase_1_comprehensive_architecture_flowchart.png`