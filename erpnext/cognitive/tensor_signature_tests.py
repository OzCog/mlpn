#!/usr/bin/env python3
"""
Tensor Signature and Prime Factorization Validation Tests

Tests specifically for the enhanced documentation and implementation
of tensor signatures and prime factorization mapping.
"""

import sys
import os
import unittest
import numpy as np
from typing import Dict, Any

# Add the cognitive module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tensor_kernel import TensorKernel, initialize_default_shapes, TensorFormat
from cognitive_grammar import CognitiveGrammar, AtomType
from tensor_fragments import TensorFragmentArchitecture, FragmentType


class TestTensorSignatures(unittest.TestCase):
    """Test tensor signature specifications"""
    
    def setUp(self):
        self.kernel = TensorKernel()
        initialize_default_shapes(self.kernel)
    
    def test_attention_tensor_signature(self):
        """Test attention tensor signature specification"""
        attention_shape = self.kernel.get_canonical_shape("attention")
        
        # Verify attention tensor signature: T_attention ∈ ℝ^(1×512×256×8×3)
        expected_signature = {
            'batch_size': 1,
            'sequence_length': 512,
            'hidden_dim': 256,
            'num_heads': 8,
            'recursion_depth': 3
        }
        
        self.assertEqual(attention_shape, expected_signature)
        
        # Test tensor creation with attention signature
        tensor_data = np.random.rand(1, 512, 256, 8, 3).astype(np.float32)
        tensor = self.kernel.create_tensor(tensor_data, TensorFormat.NUMPY)
        
        self.assertEqual(tensor.shape, (1, 512, 256, 8, 3))
        self.assertEqual(tensor.dtype, np.float32)
    
    def test_grammar_tensor_signature(self):
        """Test grammar tensor signature specification"""
        grammar_shape = self.kernel.get_canonical_shape("grammar")
        
        # Verify grammar tensor signature: T_grammar ∈ ℝ^(10000×512×1024×6×1000)
        expected_signature = {
            'vocab_size': 10000,
            'embedding_dim': 512,
            'hidden_dim': 1024,
            'num_layers': 6,
            'hypergraph_nodes': 1000
        }
        
        self.assertEqual(grammar_shape, expected_signature)
        
        # Test smaller tensor for memory efficiency in testing
        test_tensor = np.random.rand(100, 32, 64, 2, 50)  # Scaled down version
        tensor = self.kernel.create_tensor(test_tensor, TensorFormat.NUMPY)
        
        self.assertEqual(len(tensor.shape), 5)  # Verify 5-dimensional tensor
    
    def test_meta_cognitive_tensor_signature(self):
        """Test meta-cognitive tensor signature specification"""
        meta_shape = self.kernel.get_canonical_shape("meta")
        
        # Verify meta tensor signature: T_meta ∈ ℝ^(128×4×3×16)
        expected_signature = {
            'state_dim': 128,
            'introspection_depth': 4,
            'meta_tensor_rank': 3,
            'monitoring_channels': 16
        }
        
        self.assertEqual(meta_shape, expected_signature)
        
        # Test meta tensor creation
        tensor_data = np.random.rand(128, 4, 3, 16)
        tensor = self.kernel.create_tensor(tensor_data, TensorFormat.NUMPY)
        
        self.assertEqual(tensor.shape, (128, 4, 3, 16))
    
    def test_scheme_tensor_generation(self):
        """Test Scheme specification generation for tensor shapes"""
        # Test attention tensor Scheme generation
        attention_scheme = self.kernel.scheme_tensor_shape("attention")
        
        expected_scheme = "(define (tensor-shape attention) '((batch_size 1) (sequence_length 512) (hidden_dim 256) (num_heads 8) (recursion_depth 3)))"
        self.assertEqual(attention_scheme, expected_scheme)
        
        # Test grammar tensor Scheme generation
        grammar_scheme = self.kernel.scheme_tensor_shape("grammar")
        self.assertIn("tensor-shape grammar", grammar_scheme)
        self.assertIn("vocab_size 10000", grammar_scheme)
        
        # Test meta tensor Scheme generation
        meta_scheme = self.kernel.scheme_tensor_shape("meta")
        self.assertIn("tensor-shape meta", meta_scheme)
        self.assertIn("state_dim 128", meta_scheme)


class TestPrimeFactorizationMapping(unittest.TestCase):
    """Test prime factorization mapping implementation"""
    
    def setUp(self):
        self.grammar = CognitiveGrammar()
    
    def test_prime_index_assignment(self):
        """Test unique prime index assignment for atoms"""
        # Create several atoms
        customer_id = self.grammar.create_entity("customer")
        order_id = self.grammar.create_entity("order")
        product_id = self.grammar.create_entity("product")
        
        # Get atom objects
        customer = self.grammar.atomspace.atoms[customer_id]
        order = self.grammar.atomspace.atoms[order_id]
        product = self.grammar.atomspace.atoms[product_id]
        
        # Verify prime indices are unique
        prime_indices = [customer.prime_index, order.prime_index, product.prime_index]
        self.assertEqual(len(prime_indices), len(set(prime_indices)))  # All unique
        
        # Verify indices are actually prime numbers
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        for prime_idx in prime_indices:
            self.assertTrue(is_prime(prime_idx), f"{prime_idx} is not prime")
    
    def test_prime_sequence_generation(self):
        """Test prime number sequence generation"""
        # Test first few primes
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
        atom_ids = []
        for i in range(10):
            atom_id = self.grammar.create_entity(f"entity_{i}")
            atom_ids.append(atom_id)
        
        # Get atom objects and extract prime indices
        atoms = [self.grammar.atomspace.atoms[atom_id] for atom_id in atom_ids]
        generated_primes = [atom.prime_index for atom in atoms]
        self.assertEqual(generated_primes, expected_primes)
    
    def test_hypergraph_density_calculation(self):
        """Test hypergraph density calculation using prime factorization"""
        # Create atoms with known prime indices
        customer_id = self.grammar.create_entity("customer")  # Prime: 2
        order_id = self.grammar.create_entity("order")        # Prime: 3
        product_id = self.grammar.create_entity("product")    # Prime: 5
        
        # Calculate density
        density = self.grammar.atomspace.get_hypergraph_density()
        
        # Expected: log(2*3*5) / 3 = log(30) / 3 ≈ 1.131
        expected_density = np.log(2 * 3 * 5) / 3
        
        self.assertAlmostEqual(density, expected_density, places=3)
    
    def test_prime_index_collision_prevention(self):
        """Test that prime indexing prevents collisions"""
        # Create many atoms to test collision prevention
        atom_ids = []
        for i in range(50):
            atom_id = self.grammar.create_entity(f"test_entity_{i}")
            atom_ids.append(atom_id)
        
        # Get atom objects
        atoms = [self.grammar.atomspace.atoms[atom_id] for atom_id in atom_ids]
        
        # Verify all prime indices are unique
        prime_indices = [atom.prime_index for atom in atoms]
        self.assertEqual(len(prime_indices), len(set(prime_indices)))
        
        # Verify prime mapping integrity
        for atom in atoms:
            mapped_id = self.grammar.atomspace.prime_indices.get(atom.prime_index)
            self.assertEqual(mapped_id, atom.id)
    
    def test_density_scaling_properties(self):
        """Test density scaling with hypergraph growth"""
        initial_density = self.grammar.atomspace.get_hypergraph_density()
        
        # Add more atoms and observe density change
        for i in range(10):
            self.grammar.create_entity(f"scaling_test_{i}")
        
        final_density = self.grammar.atomspace.get_hypergraph_density()
        
        # Density should increase with more atoms (due to prime product growth)
        self.assertGreater(final_density, initial_density)
        
        # Verify density is a valid number
        self.assertGreaterEqual(final_density, 0.0)
        self.assertIsInstance(final_density, (int, float))


class TestFragmentSignatureValidation(unittest.TestCase):
    """Test tensor fragment signatures and operations"""
    
    def setUp(self):
        self.architecture = TensorFragmentArchitecture()
    
    def test_fragment_metadata_signature(self):
        """Test fragment metadata signature validation"""
        # Create a fragment
        data = np.random.rand(4, 6)
        fragment_id = self.architecture.create_fragment(data, FragmentType.COGNITIVE)
        
        fragment = self.architecture.registry.get_fragment(fragment_id)
        
        # Verify metadata signature
        self.assertIsInstance(fragment.metadata.fragment_id, str)
        self.assertEqual(fragment.metadata.fragment_type, FragmentType.COGNITIVE)
        self.assertEqual(fragment.metadata.shape, (4, 6))
        self.assertEqual(fragment.metadata.dtype, "float64")
        self.assertIsInstance(fragment.metadata.created_at, float)
        self.assertIsInstance(fragment.metadata.last_modified, float)
    
    def test_fragment_operation_signatures(self):
        """Test fragment operation method signatures"""
        # Test composition signature: [Fragment_ID] → Tensor (not Fragment_ID)
        data1 = np.random.rand(2, 3)
        data2 = np.random.rand(2, 3)
        
        frag1_id = self.architecture.create_fragment(data1, FragmentType.COGNITIVE)
        frag2_id = self.architecture.create_fragment(data2, FragmentType.COGNITIVE)
        
        # Composition operation returns composed tensor, not new fragment ID
        composed_tensor = self.architecture.compose_fragments([frag1_id, frag2_id])
        self.assertIsInstance(composed_tensor, np.ndarray)
        
        # Verify composed tensor has expected shape
        self.assertEqual(len(composed_tensor.shape), 3)  # Should be 3D tensor
    
    def test_decomposition_signature(self):
        """Test tensor decomposition signature: Tensor × Strategy → [Fragment_ID]"""
        # Create test tensor
        tensor = np.random.rand(8, 8)
        strategy = {"type": "grid", "grid_shape": (2, 2)}
        
        # Decompose tensor
        fragment_ids = self.architecture.decompose_tensor(tensor, strategy)
        
        # Verify return signature: list of fragment IDs
        self.assertIsInstance(fragment_ids, list)
        self.assertEqual(len(fragment_ids), 4)  # 2x2 grid = 4 fragments
        
        for frag_id in fragment_ids:
            self.assertIsInstance(frag_id, str)
            fragment = self.architecture.registry.get_fragment(frag_id)
            self.assertIsNotNone(fragment)
    
    def test_scheme_fragment_specification(self):
        """Test Scheme specification generation for fragments"""
        # Create a fragment
        data = np.random.rand(3, 4)
        fragment_id = self.architecture.create_fragment(data, FragmentType.COGNITIVE)
        
        # Generate Scheme specification
        scheme_spec = self.architecture.generate_scheme_fragment_spec(fragment_id)
        
        # Verify Scheme format
        self.assertIn(f"fragment-spec {fragment_id}", scheme_spec)
        self.assertIn("cognitive", scheme_spec)
        self.assertIn("[3, 4]", scheme_spec)
        self.assertIn("fragment-compose", scheme_spec)
        self.assertIn("fragment-contract", scheme_spec)


if __name__ == "__main__":
    print("=" * 80)
    print("TENSOR SIGNATURE AND PRIME FACTORIZATION VALIDATION TESTS")
    print("=" * 80)
    
    # Run test suites
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestTensorSignatures))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPrimeFactorizationMapping))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestFragmentSignatureValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("✓ ALL TENSOR SIGNATURE AND PRIME FACTORIZATION TESTS PASSED!")
        print("Tensor signatures and prime factorization mapping verified successfully.")
    else:
        print("✗ SOME TESTS FAILED!")
        print(f"Failures: {len(result.failures)}, Errors: {len(result.errors)}")
    print("=" * 80)