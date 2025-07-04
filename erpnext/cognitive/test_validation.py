#!/usr/bin/env python3
"""
Basic validation tests for the cognitive architecture
"""

import sys
import os
import numpy as np

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive.tensor_kernel import TensorKernel, TensorFormat, initialize_default_shapes
from cognitive.cognitive_grammar import CognitiveGrammar
from cognitive.attention_allocation import ECANAttention
from cognitive.meta_cognitive import MetaCognitive, MetaLayer


def test_tensor_kernel():
    """Test basic tensor kernel functionality"""
    print("Testing Tensor Kernel...")
    
    kernel = TensorKernel()
    initialize_default_shapes(kernel)
    
    # Test tensor creation
    tensor = kernel.create_tensor([[1, 2], [3, 4]])
    assert tensor.shape == (2, 2), f"Expected shape (2, 2), got {tensor.shape}"
    
    # Test tensor contraction
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    result = kernel.tensor_contraction(a, b)
    expected = np.array([[19, 22], [43, 50]])
    assert np.array_equal(result, expected), "Tensor contraction failed"
    
    # Test canonical shapes
    attention_shape = kernel.get_canonical_shape("attention")
    assert attention_shape is not None, "Attention shape not found"
    assert "batch_size" in attention_shape, "Attention shape missing batch_size"
    
    print("✓ Tensor Kernel tests passed")


def test_cognitive_grammar():
    """Test cognitive grammar functionality"""
    print("Testing Cognitive Grammar...")
    
    grammar = CognitiveGrammar()
    
    # Test entity creation
    entity1 = grammar.create_entity("test_entity")
    assert isinstance(entity1, str), "Entity ID should be a string"
    
    # Test relationship creation
    entity2 = grammar.create_entity("test_entity2")
    relationship = grammar.create_relationship(entity1, entity2)
    assert isinstance(relationship, str), "Relationship ID should be a string"
    
    # Test knowledge stats
    stats = grammar.get_knowledge_stats()
    assert stats["total_atoms"] >= 2, "Should have at least 2 atoms"
    assert stats["total_links"] >= 1, "Should have at least 1 link"
    
    print("✓ Cognitive Grammar tests passed")


def test_attention_allocation():
    """Test attention allocation functionality"""
    print("Testing Attention Allocation...")
    
    attention = ECANAttention()
    
    # Test attention focusing
    attention.focus_attention("test_atom", 2.0)
    
    # Check attention was allocated
    attention_val = attention.attention_bank.attention_values.get("test_atom")
    assert attention_val is not None, "Attention value not found"
    assert attention_val.sti > 0, "STI should be greater than 0"
    
    # Test attention cycle
    attention.run_attention_cycle(["test_atom"])
    
    # Check economic stats
    stats = attention.get_economic_stats()
    assert "total_wages" in stats, "Economic stats missing total_wages"
    assert "total_rents" in stats, "Economic stats missing total_rents"
    
    print("✓ Attention Allocation tests passed")


def test_meta_cognitive():
    """Test meta-cognitive functionality"""
    print("Testing Meta-Cognitive...")
    
    meta = MetaCognitive()
    
    # Create mock components
    tensor_kernel = TensorKernel()
    grammar = CognitiveGrammar()
    attention = ECANAttention()
    
    # Register layers
    meta.register_layer(MetaLayer.TENSOR_KERNEL, tensor_kernel)
    meta.register_layer(MetaLayer.COGNITIVE_GRAMMAR, grammar)
    meta.register_layer(MetaLayer.ATTENTION_ALLOCATION, attention)
    
    # Test state update
    meta.update_meta_state()
    
    # Check meta-tensor history
    assert len(meta.meta_tensor_history) > 0, "Meta-tensor history should not be empty"
    
    # Test system health
    health = meta.diagnose_system_health()
    assert "status" in health, "Health report missing status"
    assert health["status"] in ["healthy", "degraded"], "Invalid health status"
    
    # Test system stats
    stats = meta.get_system_stats()
    assert stats["registered_layers"] == 3, "Should have 3 registered layers"
    
    print("✓ Meta-Cognitive tests passed")


def test_integration():
    """Test full system integration"""
    print("Testing System Integration...")
    
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
    
    # Create knowledge scenario
    entity1 = grammar.create_entity("entity1")
    entity2 = grammar.create_entity("entity2")
    relationship = grammar.create_relationship(entity1, entity2)
    
    # Focus attention
    attention.focus_attention(entity1, 2.0)
    
    # Perform tensor operations
    tensor = tensor_kernel.create_tensor([[1, 0], [0, 1]])
    
    # Update meta-state
    meta_cognitive.update_meta_state()
    
    # Run attention cycle
    attention.run_attention_cycle([entity1])
    
    # Verify integration
    tensor_stats = tensor_kernel.get_operation_stats()
    knowledge_stats = grammar.get_knowledge_stats()
    attention_stats = attention.get_economic_stats()
    meta_stats = meta_cognitive.get_system_stats()
    
    assert tensor_stats["operation_count"] > 0, "No tensor operations recorded"
    assert knowledge_stats["total_atoms"] >= 2, "Insufficient knowledge atoms"
    assert attention_stats["total_wages"] > 0, "No wages allocated"
    assert meta_stats["registered_layers"] == 3, "Wrong number of registered layers"
    
    print("✓ Integration tests passed")


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("COGNITIVE ARCHITECTURE VALIDATION TESTS")
    print("=" * 60)
    
    try:
        test_tensor_kernel()
        test_cognitive_grammar()
        test_attention_allocation()
        test_meta_cognitive()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("The cognitive architecture is functioning correctly.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)