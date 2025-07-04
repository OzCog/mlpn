"""
Cognitive Architecture Module for ERPNext

This module implements a cognitive architecture framework integrating:
- Tensor Kernel Cohesion Layer (GGML, Kokkos, A0ML)
- Cognitive Grammar Field (AtomSpace, PLN, Memory Systems)
- ECAN Attention Allocation
- Meta-Cognitive Enhancement

The architecture follows the recursive neural-symbolic integration paradigm
for distributed cognition and emergent intelligence.
"""

try:
    from .tensor_kernel import TensorKernel, TensorFormat, initialize_default_shapes
    from .cognitive_grammar import CognitiveGrammar, AtomSpace, PLN, PatternMatcher
    from .attention_allocation import ECANAttention, AttentionBank, ActivationSpreading
    from .meta_cognitive import MetaCognitive, MetaStateMonitor, RecursiveIntrospector, MetaLayer
    
    __all__ = [
        "TensorKernel", "TensorFormat", "initialize_default_shapes",
        "CognitiveGrammar", "AtomSpace", "PLN", "PatternMatcher",
        "ECANAttention", "AttentionBank", "ActivationSpreading",
        "MetaCognitive", "MetaStateMonitor", "RecursiveIntrospector", "MetaLayer"
    ]
    
except ImportError as e:
    # Graceful fallback if numpy or other dependencies are not available
    print(f"Warning: Cognitive architecture requires numpy. Install with: pip install numpy")
    __all__ = []