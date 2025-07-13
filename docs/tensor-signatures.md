# Tensor Signatures and Prime Factorization Mapping

## Overview

This document provides comprehensive documentation for tensor signatures and prime factorization mapping within the Phase 1 Cognitive Primitives & Foundational Hypergraph Encoding architecture.

## Tensor Signatures

### Core Tensor Formats

The system supports multiple tensor formats for seamless backend integration:

```
TensorFormat:
├── GGML      - GPU-optimized machine learning tensors
├── KOKKOS    - Parallel computing tensor operations
├── A0ML      - Meta-learning orchestration tensors
└── NUMPY     - Standard numerical computing tensors
```

### Canonical Tensor Shapes

#### Attention Tensor Signature
```scheme
(define (tensor-shape attention) 
  '((batch_size 1) 
    (sequence_length 512) 
    (hidden_dim 256) 
    (num_heads 8) 
    (recursion_depth 3)))
```

**Mathematical Representation:**
```
T_attention ∈ ℝ^(1×512×256×8×3)
```

**Usage Context:**
- Economic Cognitive Attention Networks (ECAN)
- Attention allocation and spreading mechanisms
- Focus and priority management in hypergraph processing

#### Grammar Tensor Signature
```scheme
(define (tensor-shape grammar) 
  '((vocab_size 10000) 
    (embedding_dim 512) 
    (hidden_dim 1024) 
    (num_layers 6) 
    (hypergraph_nodes 1000)))
```

**Mathematical Representation:**
```
T_grammar ∈ ℝ^(10000×512×1024×6×1000)
```

**Usage Context:**
- Hypergraph knowledge representation
- Probabilistic Logic Networks (PLN) inference
- ko6ml primitive encoding and translation

#### Meta-Cognitive Tensor Signature
```scheme
(define (tensor-shape meta) 
  '((state_dim 128) 
    (introspection_depth 4) 
    (meta_tensor_rank 3) 
    (monitoring_channels 16)))
```

**Mathematical Representation:**
```
T_meta ∈ ℝ^(128×4×3×16)
```

**Usage Context:**
- Recursive introspection and system monitoring
- Meta-cognitive state tracking
- Performance metrics collection

### Fragment Tensor Signatures

#### Cognitive Fragment Signature
```
TensorFragment:
  fragment_id: UUID
  fragment_type: FragmentType.COGNITIVE
  shape: Tuple[int, ...]
  dtype: "float32" | "float64"
  data: np.ndarray
  metadata: FragmentMetadata
```

**Core Operations:**
```python
# Fragment creation
fragment = TensorFragment(
    fragment_id=uuid4(),
    fragment_type=FragmentType.COGNITIVE,
    shape=(4, 6),
    data=np.random.rand(4, 6)
)

# Fragment decomposition
fragments = architecture.decompose_tensor(
    tensor=large_tensor,
    strategy={"type": "grid", "grid_shape": (2, 2)}
)

# Fragment composition
composed = architecture.compose_fragments(fragment_ids)
```

## Prime Factorization Mapping

### Hypergraph Density Calculation

The system uses prime factorization for maximum hypergraph density and efficient indexing:

```python
class HypergraphAtom:
    id: str
    name: str
    atom_type: AtomType
    truth_value: TruthValue
    prime_index: int  # Prime-factorized index for density
```

### Prime Index Assignment

```python
def _get_next_prime(self) -> int:
    """Get next prime number for indexing"""
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    while not is_prime(self.next_prime):
        self.next_prime += 1
    prime = self.next_prime
    self.next_prime += 1
    return prime
```

### Density Calculation Algorithm

```python
def calculate_hypergraph_density(self) -> float:
    """Calculate hypergraph density using prime factorization"""
    if not self.atoms:
        return 0.0
    
    # Calculate density based on prime indices
    prime_product = 1
    for prime in self.prime_indices.keys():
        prime_product *= prime
    
    # Density formula: log(prime_product) / number_of_atoms
    density = np.log(prime_product) / len(self.atoms)
    return min(density / 10.0, 1.0)  # Normalize to [0,1]
```

### Prime Factorization Benefits

1. **Maximum Density**: Each atom gets a unique prime index, ensuring optimal hypergraph connectivity
2. **Efficient Indexing**: Prime numbers provide collision-free indexing
3. **Mathematical Properties**: Leverages fundamental theorem of arithmetic
4. **Scalability**: Unlimited prime sequence supports infinite hypergraph growth

## Tensor Fragment Architecture Signatures

### Fragment Registry Signature

```python
@dataclass
class FragmentMetadata:
    fragment_id: str
    fragment_type: FragmentType
    shape: Tuple[int, ...]
    dtype: str
    created_at: float
    last_modified: float
    sync_state: SyncState
    dependencies: List[str] = field(default_factory=list)
```

### Synchronization States

```python
class SyncState(Enum):
    SYNCHRONIZED = "synchronized"  # Fragment is up-to-date
    PENDING = "pending"           # Update in progress
    DIRTY = "dirty"              # Needs synchronization
    CONFLICT = "conflict"        # Merge conflict detected
```

### Fragment Operations Signatures

#### Composition Operation
```python
def fragment_composition(self, 
                        fragment_ids: List[str],
                        composition_type: str = "concatenate") -> str:
    """
    Signature: [Fragment_ID] → Fragment_ID
    
    Compose multiple fragments into a single tensor
    Returns new fragment identifier
    """
```

#### Contraction Operation
```python
def fragment_contraction(self,
                        fragment_a_id: str,
                        fragment_b_id: str,
                        axes: Optional[List[int]] = None) -> str:
    """
    Signature: Fragment_ID × Fragment_ID × [Axis] → Fragment_ID
    
    Contract two fragments along specified axes
    Returns new fragment identifier
    """
```

#### Decomposition Operation
```python
def decompose_tensor(self,
                    tensor: np.ndarray,
                    strategy: Dict[str, Any]) -> List[str]:
    """
    Signature: Tensor × Strategy → [Fragment_ID]
    
    Decompose tensor into fragments using specified strategy
    Returns list of fragment identifiers
    """
```

## ko6ml Translation Signatures

### ko6ml → AtomSpace Signature

```python
def ko6ml_to_atomspace(self, expr: Ko6mlExpression) -> str:
    """
    Signature: Ko6mlExpression → AtomSpace_ID
    
    Translation mapping:
    - Ko6mlPrimitive.ENTITY → ConceptNode
    - Ko6mlPrimitive.RELATION → PredicateNode
    - Ko6mlPrimitive.PROPERTY → ConceptNode
    - Ko6mlPrimitive.RULE → SchemaNode
    - Ko6mlPrimitive.CONSTRAINT → SchemaNode
    - Ko6mlPrimitive.PATTERN → VariableNode
    """
```

### AtomSpace → ko6ml Signature

```python
def atomspace_to_ko6ml(self, atom_id: str) -> Ko6mlExpression:
    """
    Signature: AtomSpace_ID → Ko6mlExpression
    
    Reverse translation with metadata preservation:
    - ConceptNode → Ko6mlPrimitive.ENTITY
    - PredicateNode → Ko6mlPrimitive.RELATION
    - SchemaNode → Ko6mlPrimitive.RULE
    - VariableNode → Ko6mlPrimitive.PATTERN
    """
```

## Scheme Integration Specifications

### Pattern Matching Signatures

```scheme
;; Entity pattern matching
(define (pattern-match atomspace entity)
  (filter (lambda (atom)
    (and
      (type atom concept)
      (truth_strength_min atom 0.7)
      (truth_confidence_min atom 0.5)))
  (atomspace-atoms)))

;; Relationship pattern matching
(define (pattern-match atomspace relationship)
  (filter (lambda (atom)
    (and
      (type atom predicate)
      (truth_strength_min atom 0.6)
      (truth_confidence_min atom 0.4)))
  (atomspace-atoms)))
```

### Fragment Operation Schemes

```scheme
;; Fragment composition
(define (fragment-compose fragment-id other-fragments)
  (let ((fragment (get-fragment fragment-id))
        (others (map get-fragment other-fragments)))
    (compose-tensors (cons fragment others))))

;; Fragment contraction
(define (fragment-contract fragment-id other-id axes)
  (let ((frag-a (get-fragment fragment-id))
        (frag-b (get-fragment other-id)))
    (tensor-contract frag-a frag-b axes)))
```

## Performance Characteristics

### Tensor Operation Complexity

| Operation | Time Complexity | Space Complexity | Parallelizable |
|-----------|----------------|------------------|----------------|
| Fragment Creation | O(n) | O(n) | Yes |
| Fragment Composition | O(n×m) | O(n+m) | Yes |
| Fragment Contraction | O(n×m×k) | O(n×m) | Yes |
| Prime Index Assignment | O(√n) | O(1) | No |
| Hypergraph Density | O(n) | O(1) | Yes |

### Memory Efficiency Patterns

```python
# Fragment caching with automatic cleanup
cache_hit_ratio = len(self.composition_cache) / self._operation_count

# Lazy evaluation for composition operations
def lazy_compose(fragment_ids):
    return lambda: actual_composition(fragment_ids)

# Automatic fragment synchronization
def auto_sync(fragment_id):
    if fragment.metadata.sync_state == SyncState.DIRTY:
        synchronize_fragment(fragment_id)
```

## Integration Verification

### Round-trip Translation Integrity

```python
def verify_round_trip(self, expressions: List[Ko6mlExpression]) -> bool:
    """
    Verification signature: [Ko6mlExpression] → Boolean
    
    For each expression e:
    1. ko6ml_to_atomspace(e) → atom_id
    2. atomspace_to_ko6ml(atom_id) → e'
    3. verify e ≡ e' (semantic equivalence)
    """
```

### Fragment Synchronization Verification

```python
def verify_fragment_sync(self, fragment_ids: List[str]) -> bool:
    """
    Synchronization signature: [Fragment_ID] → Boolean
    
    Verify all fragments maintain consistent state
    across distributed operations
    """
```

This comprehensive tensor signature documentation provides the mathematical foundations and operational specifications for the Phase 1 Cognitive Primitives & Foundational Hypergraph Encoding architecture.