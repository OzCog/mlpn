#!/usr/bin/env python3
"""
Cognitive Architecture Demo

This script demonstrates the complete cognitive architecture system
integrating tensor computation, knowledge representation, attention allocation,
and meta-cognitive monitoring.
"""

import sys
import os
import numpy as np
from typing import Dict, List, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive.tensor_kernel import TensorKernel, TensorFormat, initialize_default_shapes
from cognitive.cognitive_grammar import CognitiveGrammar, TruthValue
from cognitive.attention_allocation import ECANAttention, EconomicParams
from cognitive.meta_cognitive import MetaCognitive, MetaLayer


def demonstrate_tensor_operations():
    """Demonstrate tensor kernel operations"""
    print("=" * 60)
    print("TENSOR KERNEL COHESION LAYER DEMONSTRATION")
    print("=" * 60)
    
    # Initialize tensor kernel
    kernel = TensorKernel(backend="cpu", precision="float32")
    initialize_default_shapes(kernel)
    
    print("1. Creating tensors with different formats:")
    
    # Create various tensors
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    numpy_tensor = kernel.create_tensor(data, TensorFormat.NUMPY)
    print(f"   NumPy tensor shape: {numpy_tensor.shape}")
    
    ggml_tensor = kernel.create_tensor(data, TensorFormat.GGML)
    print(f"   GGML tensor shape: {ggml_tensor.shape}")
    
    print("\n2. Canonical tensor shapes:")
    for shape_name in ["attention", "grammar", "meta"]:
        shape = kernel.get_canonical_shape(shape_name)
        print(f"   {shape_name}: {shape}")
        
    print("\n3. Tensor operations:")
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    
    contraction = kernel.tensor_contraction(a, b)
    print(f"   Tensor contraction result:\n{contraction}")
    
    # Parallel operations
    tensors = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])]
    parallel_sum = kernel.parallel_operation("reduce", tensors)
    print(f"   Parallel reduction result: {parallel_sum}")
    
    # Meta-learning update
    params = np.array([1.0, 2.0, 3.0])
    gradients = np.array([0.1, 0.2, 0.3])
    updated_params = kernel.meta_learning_update(0.01, gradients, params)
    print(f"   Meta-learning update: {params} -> {updated_params}")
    
    # Show statistics
    stats = kernel.get_operation_stats()
    print(f"\n4. Operation statistics: {stats}")
    
    # Generate Scheme specification
    scheme_spec = kernel.scheme_tensor_shape("attention")
    print(f"\n5. Scheme specification for attention tensor:")
    print(f"   {scheme_spec}")
    
    return kernel


def demonstrate_cognitive_grammar():
    """Demonstrate cognitive grammar system"""
    print("\n" + "=" * 60)
    print("COGNITIVE GRAMMAR FIELD DEMONSTRATION")
    print("=" * 60)
    
    # Initialize cognitive grammar
    grammar = CognitiveGrammar()
    
    print("1. Creating entities and relationships:")
    
    # Create entities
    person = grammar.create_entity("person", "concept")
    john = grammar.create_entity("john", "concept")
    mary = grammar.create_entity("mary", "concept")
    loves = grammar.create_entity("loves", "predicate")
    
    print(f"   Created entities: person, john, mary, loves")
    
    # Create relationships
    john_person = grammar.create_relationship(john, person, "inheritance")
    mary_person = grammar.create_relationship(mary, person, "inheritance")
    john_loves_mary = grammar.create_relationship(john, mary, "similarity")
    
    print(f"   Created relationships: john-person, mary-person, john-mary")
    
    print("\n2. Knowledge inference:")
    
    # Perform inference
    deduction_result = grammar.infer_knowledge(
        "deduction", 
        premise1=john_person, 
        premise2=mary_person
    )
    print(f"   Deduction result: strength={deduction_result.strength:.3f}, confidence={deduction_result.confidence:.3f}")
    
    induction_result = grammar.infer_knowledge(
        "induction",
        evidence_links=[john_person, mary_person, john_loves_mary]
    )
    print(f"   Induction result: strength={induction_result.strength:.3f}, confidence={induction_result.confidence:.3f}")
    
    print("\n3. Pattern matching:")
    
    # Test pattern matching
    high_conf_entities = grammar.pattern_matcher.match_pattern(
        "high_confidence", 
        [john, mary, person]
    )
    print(f"   High confidence entities: {len(high_conf_entities)}")
    
    print("\n4. Knowledge statistics:")
    stats = grammar.get_knowledge_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
    print("\n5. Hypergraph density:")
    density = grammar.atomspace.get_hypergraph_density()
    print(f"   Hypergraph density: {density:.3f}")
    
    return grammar


def demonstrate_attention_allocation():
    """Demonstrate ECAN attention allocation"""
    print("\n" + "=" * 60)
    print("ECAN ATTENTION ALLOCATION DEMONSTRATION")
    print("=" * 60)
    
    # Initialize attention system
    connections = {
        "concept1": ["concept2", "concept3"],
        "concept2": ["concept3", "concept4"],
        "concept3": ["concept4"],
        "concept4": []
    }
    
    attention = ECANAttention(connections)
    
    print("1. Initial attention focusing:")
    
    # Focus attention on different concepts
    attention.focus_attention("concept1", 3.0)
    attention.focus_attention("concept2", 2.0)
    attention.focus_attention("concept3", 1.0)
    
    print("   Focused attention on concept1 (3.0), concept2 (2.0), concept3 (1.0)")
    
    print("\n2. Attention spreading and economic allocation:")
    
    # Run attention cycle
    attention.run_attention_cycle(["concept1"])
    
    # Show attention focus
    focus = attention.get_attention_focus(5)
    print("   Current attention focus:")
    for atom_id, attention_val in focus:
        print(f"     {atom_id}: {attention_val:.3f}")
        
    print("\n3. Economic statistics:")
    economic_stats = attention.get_economic_stats()
    for key, value in economic_stats.items():
        if key != "attention_summary":
            print(f"   {key}: {value}")
            
    print("\n4. Attention tensor visualization:")
    atom_ids = ["concept1", "concept2", "concept3", "concept4"]
    attention_tensor = attention.visualize_attention_tensor(atom_ids)
    print(f"   Attention tensor shape: {attention_tensor.shape}")
    print(f"   Attention values:\n{attention_tensor}")
    
    print("\n5. Scheme specification:")
    scheme = attention.scheme_attention_spec()
    print("   Generated Scheme specification for attention allocation")
    
    return attention


def demonstrate_meta_cognitive():
    """Demonstrate meta-cognitive system"""
    print("\n" + "=" * 60)
    print("META-COGNITIVE ENHANCEMENT DEMONSTRATION")
    print("=" * 60)
    
    # Initialize meta-cognitive system
    meta = MetaCognitive()
    
    # Create mock components for demonstration
    tensor_kernel = TensorKernel()
    initialize_default_shapes(tensor_kernel)
    
    grammar = CognitiveGrammar()
    attention = ECANAttention()
    
    print("1. Registering cognitive layers:")
    
    # Register layers
    meta.register_layer(MetaLayer.TENSOR_KERNEL, tensor_kernel)
    meta.register_layer(MetaLayer.COGNITIVE_GRAMMAR, grammar)
    meta.register_layer(MetaLayer.ATTENTION_ALLOCATION, attention)
    
    print("   Registered tensor kernel, cognitive grammar, and attention allocation")
    
    print("\n2. Performing some operations to generate state:")
    
    # Perform operations to generate state
    tensor_kernel.create_tensor([[1, 2], [3, 4]])
    tensor_kernel.tensor_contraction(np.array([1, 2]), np.array([3, 4]))
    
    grammar.create_entity("test_entity")
    grammar.create_entity("another_entity")
    
    attention.focus_attention("test_atom", 2.0)
    
    print("   Executed tensor operations, created entities, focused attention")
    
    print("\n3. Updating meta-cognitive state:")
    
    # Update meta-state
    meta.update_meta_state()
    
    print("   Meta-state updated")
    
    print("\n4. System health diagnosis:")
    
    # Diagnose system health
    health = meta.diagnose_system_health()
    print("   System health report:")
    for key, value in health.items():
        print(f"     {key}: {value}")
        
    print("\n5. Deep introspection:")
    
    # Perform introspection
    introspection = meta.perform_deep_introspection(MetaLayer.TENSOR_KERNEL)
    print("   Introspection of tensor kernel:")
    print(f"     Layer: {introspection.get('layer', 'unknown')}")
    print(f"     Depth: {introspection.get('depth', 0)}")
    print(f"     Structure: {len(introspection.get('structure', {}))} components")
    
    print("\n6. System statistics:")
    
    stats = meta.get_system_stats()
    print("   System statistics:")
    for key, value in stats.items():
        if key != "current_state":
            print(f"     {key}: {value}")
            
    return meta


def demonstrate_full_integration():
    """Demonstrate full system integration"""
    print("\n" + "=" * 60)
    print("FULL COGNITIVE ARCHITECTURE INTEGRATION")
    print("=" * 60)
    
    # Initialize all components
    tensor_kernel = TensorKernel()
    initialize_default_shapes(tensor_kernel)
    
    grammar = CognitiveGrammar()
    attention = ECANAttention()
    meta_cognitive = MetaCognitive()
    
    # Register with meta-cognitive system
    meta_cognitive.register_layer(MetaLayer.TENSOR_KERNEL, tensor_kernel)
    meta_cognitive.register_layer(MetaLayer.COGNITIVE_GRAMMAR, grammar)
    meta_cognitive.register_layer(MetaLayer.ATTENTION_ALLOCATION, attention)
    
    print("1. Creating integrated knowledge scenario:")
    
    # Create a knowledge scenario
    person = grammar.create_entity("person")
    alice = grammar.create_entity("alice")
    bob = grammar.create_entity("bob")
    
    # Create relationships
    alice_person = grammar.create_relationship(alice, person, "inheritance")
    bob_person = grammar.create_relationship(bob, person, "inheritance")
    
    # Focus attention on key entities
    attention.focus_attention(alice, 3.0)
    attention.focus_attention(bob, 2.0)
    
    # Perform tensor operations for knowledge representation
    knowledge_tensor = tensor_kernel.create_tensor([
        [1, 0, 0],  # alice
        [0, 1, 0],  # bob
        [0, 0, 1]   # person
    ])
    
    print("   Created knowledge scenario with alice, bob, and person")
    
    print("\n2. Running integrated cognitive cycle:")
    
    # Update meta-state
    meta_cognitive.update_meta_state()
    
    # Run attention cycle
    attention.run_attention_cycle([alice, bob])
    
    # Perform knowledge inference
    inference_result = grammar.infer_knowledge("induction", evidence_links=[alice_person, bob_person])
    
    print(f"   Inference result: strength={inference_result.strength:.3f}")
    
    print("\n3. System-wide statistics:")
    
    # Collect statistics from all components
    tensor_stats = tensor_kernel.get_operation_stats()
    knowledge_stats = grammar.get_knowledge_stats()
    attention_stats = attention.get_economic_stats()
    meta_stats = meta_cognitive.get_system_stats()
    
    print("   Tensor operations:", tensor_stats["operation_count"])
    print("   Knowledge atoms:", knowledge_stats["total_atoms"])
    print("   Attention wages:", attention_stats["total_wages"])
    print("   Meta-cognitive layers:", meta_stats["registered_layers"])
    
    print("\n4. Scheme specifications:")
    
    # Generate comprehensive Scheme specifications
    tensor_scheme = tensor_kernel.scheme_tensor_shape("grammar")
    pattern_scheme = grammar.pattern_matcher.scheme_pattern_match("entity")
    attention_scheme = attention.scheme_attention_spec()
    
    print("   Generated Scheme specifications for all components")
    
    print("\n5. Final system health check:")
    
    health = meta_cognitive.diagnose_system_health()
    print(f"   System status: {health['status']}")
    print(f"   Stability score: {health['stability_score']:.3f}")
    print(f"   Coherence score: {health['coherence_score']:.3f}")
    
    print("\n" + "=" * 60)
    print("COGNITIVE ARCHITECTURE DEMONSTRATION COMPLETE")
    print("=" * 60)
    
    return {
        "tensor_kernel": tensor_kernel,
        "grammar": grammar,
        "attention": attention,
        "meta_cognitive": meta_cognitive
    }


def main():
    """Main demonstration function"""
    print("COGNITIVE ARCHITECTURE ENGINEERING DEMONSTRATION")
    print("Implementing tensor computation, knowledge representation,")
    print("attention allocation, and meta-cognitive monitoring")
    
    try:
        # Run individual component demonstrations
        tensor_kernel = demonstrate_tensor_operations()
        grammar = demonstrate_cognitive_grammar()
        attention = demonstrate_attention_allocation()
        meta_cognitive = demonstrate_meta_cognitive()
        
        # Run full integration demonstration
        integrated_system = demonstrate_full_integration()
        
        print("\n✓ All demonstrations completed successfully!")
        print("\nThe cognitive architecture system is now ready for:")
        print("- Real-time tensor computation with GGML/Kokkos/A0ML")
        print("- Hypergraph knowledge representation with AtomSpace")
        print("- Economic attention allocation with ECAN")
        print("- Meta-cognitive monitoring and introspection")
        print("- Recursive neural-symbolic integration")
        
        return integrated_system
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()