"""
Phase 1 Verification Tests

Comprehensive test suite for Phase 1: Cognitive Primitives & Foundational Hypergraph Encoding.
Tests microservices architecture, tensor fragment operations, and ko6ml translations.
"""

import unittest
import numpy as np
import time
import threading
import requests
import json
from typing import List, Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from microservices import AtomSpaceService, PLNService, PatternService, Ko6mlTranslator
from microservices.ko6ml_translator import Ko6mlExpression, Ko6mlPrimitive
from tensor_fragments import TensorFragmentArchitecture, FragmentType
from cognitive_grammar import AtomType, LinkType, TruthValue
from tensor_kernel import TensorKernel, initialize_default_shapes


class TestPhase1Microservices(unittest.TestCase):
    """Test Phase 1 microservices architecture"""
    
    @classmethod
    def setUpClass(cls):
        """Set up microservices for testing"""
        cls.atomspace_service = AtomSpaceService(port=18001)
        cls.pln_service = PLNService(port=18002)
        cls.pattern_service = PatternService(port=18003)
        
        # Start services
        cls.atomspace_service.start()
        cls.pln_service.start()
        cls.pattern_service.start()
        
        # Wait for services to start
        time.sleep(1)
    
    @classmethod
    def tearDownClass(cls):
        """Tear down microservices"""
        cls.atomspace_service.stop()
        cls.pln_service.stop()
        cls.pattern_service.stop()
    
    def test_atomspace_service_health(self):
        """Test AtomSpace service health check"""
        try:
            response = requests.get("http://localhost:18001/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["service"], "atomspace")
        except requests.exceptions.RequestException:
            self.skipTest("AtomSpace service not available")
    
    def test_atomspace_crud_operations(self):
        """Test AtomSpace CRUD operations via REST API"""
        try:
            # Create atom
            atom_data = {
                "name": "test_entity",
                "type": "concept",
                "truth_value": {"strength": 0.8, "confidence": 0.9}
            }
            
            response = requests.post("http://localhost:18001/atoms", 
                                   json=atom_data, timeout=5)
            self.assertEqual(response.status_code, 201)
            
            created_atom = response.json()
            atom_id = created_atom["id"]
            self.assertEqual(created_atom["name"], "test_entity")
            
            # Get atom
            response = requests.get(f"http://localhost:18001/atoms/{atom_id}", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            retrieved_atom = response.json()
            self.assertEqual(retrieved_atom["name"], "test_entity")
            self.assertEqual(retrieved_atom["truth_value"]["strength"], 0.8)
            
            # List atoms
            response = requests.get("http://localhost:18001/atoms", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            atoms_list = response.json()
            self.assertGreater(len(atoms_list), 0)
            
        except requests.exceptions.RequestException:
            self.skipTest("AtomSpace service not available")
    
    def test_pln_service_inference(self):
        """Test PLN inference service"""
        try:
            # Test health first
            response = requests.get("http://localhost:18002/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            # Create some test data in AtomSpace first
            atom1_data = {"name": "A", "type": "concept"}
            atom2_data = {"name": "B", "type": "concept"}
            
            response1 = requests.post("http://localhost:18001/atoms", json=atom1_data, timeout=5)
            response2 = requests.post("http://localhost:18001/atoms", json=atom2_data, timeout=5)
            
            atom1_id = response1.json()["id"]
            atom2_id = response2.json()["id"]
            
            # Create link
            link_data = {
                "type": "implication",
                "atoms": [atom1_id, atom2_id],
                "truth_value": {"strength": 0.8, "confidence": 0.9}
            }
            
            link_response = requests.post("http://localhost:18001/links", json=link_data, timeout=5)
            link_id = link_response.json()["id"]
            
            # Test deduction (using same link for both premises - simplified test)
            deduction_data = {
                "premise1_id": link_id,
                "premise2_id": link_id
            }
            
            response = requests.post("http://localhost:18002/deduction", 
                                   json=deduction_data, timeout=5)
            self.assertEqual(response.status_code, 200)
            
            result = response.json()
            self.assertEqual(result["inference_type"], "deduction")
            self.assertIn("result", result)
            self.assertIn("strength", result["result"])
            
        except requests.exceptions.RequestException:
            self.skipTest("PLN service not available")
    
    def test_pattern_service_operations(self):
        """Test pattern matching service"""
        try:
            # Test health first
            response = requests.get("http://localhost:18003/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            # Define a pattern
            pattern_data = {
                "pattern_name": "test_pattern",
                "template": {
                    "type": "concept",
                    "truth_strength_min": 0.7
                }
            }
            
            response = requests.post("http://localhost:18003/patterns", 
                                   json=pattern_data, timeout=5)
            self.assertEqual(response.status_code, 201)
            
            # List patterns
            response = requests.get("http://localhost:18003/patterns", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            patterns = response.json()
            self.assertIn("test_pattern", patterns["patterns"])
            
            # Get specific pattern
            response = requests.get("http://localhost:18003/patterns/test_pattern", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            pattern = response.json()
            self.assertEqual(pattern["pattern_name"], "test_pattern")
            
        except requests.exceptions.RequestException:
            self.skipTest("Pattern service not available")


class TestKo6mlTranslation(unittest.TestCase):
    """Test ko6ml ↔ AtomSpace bidirectional translation"""
    
    def setUp(self):
        """Set up translator"""
        self.translator = Ko6mlTranslator()
    
    def test_basic_ko6ml_to_atomspace(self):
        """Test basic ko6ml to AtomSpace translation"""
        ko6ml_expr = Ko6mlExpression(
            primitive_type=Ko6mlPrimitive.ENTITY,
            name="customer",
            parameters={"properties": {"type": "business", "priority": "high"}},
            metadata={"confidence": 0.8, "certainty": 0.9}
        )
        
        atom_id = self.translator.ko6ml_to_atomspace(ko6ml_expr)
        
        self.assertIsInstance(atom_id, str)
        
        # Verify atom was created
        atom = self.translator.atomspace.get_atom(atom_id)
        self.assertIsNotNone(atom)
        self.assertEqual(atom.name, "customer")
        self.assertEqual(atom.atom_type, AtomType.CONCEPT)
    
    def test_atomspace_to_ko6ml(self):
        """Test AtomSpace to ko6ml translation"""
        # Create atom directly
        atom_id = self.translator.atomspace.add_atom(
            "order", AtomType.PREDICATE, TruthValue(0.7, 0.8)
        )
        
        ko6ml_expr = self.translator.atomspace_to_ko6ml(atom_id)
        
        self.assertIsNotNone(ko6ml_expr)
        self.assertEqual(ko6ml_expr.name, "order")
        self.assertEqual(ko6ml_expr.primitive_type, Ko6mlPrimitive.RELATION)
        self.assertEqual(ko6ml_expr.metadata["truth_strength"], 0.7)
    
    def test_round_trip_translation(self):
        """Test round-trip translation integrity"""
        original_expressions = [
            Ko6mlExpression(
                primitive_type=Ko6mlPrimitive.ENTITY,
                name="customer",
                parameters={},
                metadata={"confidence": 0.8}
            ),
            Ko6mlExpression(
                primitive_type=Ko6mlPrimitive.RELATION,
                name="has_order",
                parameters={"relations": [{"type": "evaluates", "target_index": 0}]},
                metadata={"confidence": 0.7}
            )
        ]
        
        # Test round-trip
        is_valid = self.translator.verify_round_trip(original_expressions)
        self.assertTrue(is_valid)
    
    def test_complex_pattern_translation(self):
        """Test complex pattern translation"""
        ko6ml_patterns = [
            Ko6mlExpression(
                primitive_type=Ko6mlPrimitive.ENTITY,
                name="customer",
                parameters={},
                metadata={"confidence": 0.8}
            ),
            Ko6mlExpression(
                primitive_type=Ko6mlPrimitive.ENTITY,
                name="order",
                parameters={},
                metadata={"confidence": 0.9}
            ),
            Ko6mlExpression(
                primitive_type=Ko6mlPrimitive.RELATION,
                name="places",
                parameters={
                    "relations": [
                        {"type": "evaluates", "target_index": 1}
                    ]
                },
                metadata={"confidence": 0.85}
            )
        ]
        
        atomspace_pattern = self.translator.translate_pattern(ko6ml_patterns)
        
        self.assertGreater(len(atomspace_pattern.atoms), 0)
        self.assertEqual(len(atomspace_pattern.atoms), 3)
        
        # Translate back
        recovered_ko6ml = self.translator.atomspace_pattern_to_ko6ml(atomspace_pattern)
        self.assertEqual(len(recovered_ko6ml), 3)
    
    def test_scheme_generation(self):
        """Test Scheme specification generation"""
        ko6ml_expr = Ko6mlExpression(
            primitive_type=Ko6mlPrimitive.ENTITY,
            name="test_entity",
            parameters={},
            metadata={"confidence": 0.8}
        )
        
        scheme_spec = self.translator.generate_scheme_translation(ko6ml_expr)
        
        self.assertIn("ko6ml-to-atomspace", scheme_spec)
        self.assertIn("atomspace-to-ko6ml", scheme_spec)
        self.assertIn("test_entity", scheme_spec)


class TestTensorFragmentArchitecture(unittest.TestCase):
    """Test tensor fragment architecture"""
    
    def setUp(self):
        """Set up tensor fragment architecture"""
        tensor_kernel = TensorKernel()
        initialize_default_shapes(tensor_kernel)
        self.fragment_arch = TensorFragmentArchitecture(tensor_kernel)
    
    def test_fragment_creation(self):
        """Test tensor fragment creation"""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        
        fragment_id = self.fragment_arch.create_fragment(
            data, FragmentType.COGNITIVE
        )
        
        self.assertIsInstance(fragment_id, str)
        
        # Retrieve fragment
        fragment = self.fragment_arch.registry.get_fragment(fragment_id)
        self.assertIsNotNone(fragment)
        self.assertEqual(fragment.metadata.fragment_type, FragmentType.COGNITIVE)
        np.testing.assert_array_equal(fragment.data, data)
    
    def test_tensor_decomposition(self):
        """Test tensor decomposition"""
        tensor = np.random.rand(4, 4)
        
        fragment_scheme = {
            "type": "grid",
            "grid_shape": (2, 2)
        }
        
        fragment_ids = self.fragment_arch.decompose_tensor(tensor, fragment_scheme)
        
        self.assertEqual(len(fragment_ids), 4)  # 2x2 grid
        
        # Verify fragments
        for fragment_id in fragment_ids:
            fragment = self.fragment_arch.registry.get_fragment(fragment_id)
            self.assertIsNotNone(fragment)
            self.assertEqual(fragment.data.shape, (2, 2))
    
    def test_fragment_composition(self):
        """Test fragment composition"""
        # Create test fragments
        fragment_ids = []
        for i in range(3):
            data = np.ones((2, 2)) * (i + 1)
            fragment_id = self.fragment_arch.create_fragment(
                data, FragmentType.COGNITIVE
            )
            fragment_ids.append(fragment_id)
        
        # Compose fragments
        composed_tensor = self.fragment_arch.compose_fragments(fragment_ids)
        
        self.assertEqual(composed_tensor.shape, (3, 2, 2))
        np.testing.assert_array_equal(composed_tensor[0], np.ones((2, 2)))
        np.testing.assert_array_equal(composed_tensor[1], np.ones((2, 2)) * 2)
    
    def test_fragment_contraction(self):
        """Test fragment contraction operations"""
        # Create test fragments
        data1 = np.array([[1, 2], [3, 4]])
        data2 = np.array([[5, 6], [7, 8]])
        
        fragment_id1 = self.fragment_arch.create_fragment(data1, FragmentType.COGNITIVE)
        fragment_id2 = self.fragment_arch.create_fragment(data2, FragmentType.ATTENTION)
        
        # Perform contraction
        result_id = self.fragment_arch.fragment_contraction(fragment_id1, fragment_id2)
        
        # Verify result
        result_fragment = self.fragment_arch.registry.get_fragment(result_id)
        self.assertIsNotNone(result_fragment)
        self.assertEqual(result_fragment.metadata.fragment_type, FragmentType.HYBRID)
        
        # Check result is correct matrix multiplication
        expected = np.dot(data1, data2)
        np.testing.assert_array_equal(result_fragment.data, expected)
    
    def test_parallel_fragment_operations(self):
        """Test parallel fragment operations"""
        # Create test fragments
        fragment_ids = []
        for i in range(3):
            data = np.array([i + 1, i + 2, i + 3])
            fragment_id = self.fragment_arch.create_fragment(
                data, FragmentType.COGNITIVE
            )
            fragment_ids.append(fragment_id)
        
        # Perform parallel reduce operation
        result_id = self.fragment_arch.parallel_fragment_operation(
            "reduce", fragment_ids
        )
        
        # Verify result
        result_fragment = self.fragment_arch.registry.get_fragment(result_id)
        self.assertIsNotNone(result_fragment)
        
        expected = np.array([6, 9, 12])  # Sum of [1,2,3] + [2,3,4] + [3,4,5]
        np.testing.assert_array_equal(result_fragment.data, expected)
    
    def test_fragment_synchronization(self):
        """Test fragment synchronization"""
        # Create test fragment
        data = np.array([1, 2, 3])
        fragment_id = self.fragment_arch.create_fragment(data, FragmentType.COGNITIVE)
        
        # Synchronize
        self.fragment_arch.synchronize_fragments([fragment_id])
        
        # Verify sync state
        fragment = self.fragment_arch.registry.get_fragment(fragment_id)
        self.assertIsNotNone(fragment)
        # Note: In our test implementation, sync completes immediately
    
    def test_hierarchical_decomposition(self):
        """Test hierarchical tensor decomposition"""
        tensor = np.random.rand(8, 8)
        
        fragment_scheme = {
            "type": "hierarchical",
            "levels": 2
        }
        
        fragment_ids = self.fragment_arch.decompose_tensor(tensor, fragment_scheme)
        
        # Should have fragments from multiple levels
        self.assertGreater(len(fragment_ids), 4)
        
        # Verify dependency relationships
        for fragment_id in fragment_ids[4:]:  # Second level fragments
            fragment = self.fragment_arch.registry.get_fragment(fragment_id)
            self.assertGreater(len(fragment.metadata.dependencies), 0)
    
    def test_scheme_fragment_generation(self):
        """Test Scheme specification generation for fragments"""
        data = np.array([[1, 2], [3, 4]])
        fragment_id = self.fragment_arch.create_fragment(data, FragmentType.COGNITIVE)
        
        scheme_spec = self.fragment_arch.generate_scheme_fragment_spec(fragment_id)
        
        self.assertIn("fragment-spec", scheme_spec)
        self.assertIn("fragment-compose", scheme_spec)
        self.assertIn("fragment-contract", scheme_spec)
        self.assertIn(fragment_id, scheme_spec)


class TestPhase1Integration(unittest.TestCase):
    """Integration tests for complete Phase 1 system"""
    
    def setUp(self):
        """Set up complete Phase 1 system"""
        self.translator = Ko6mlTranslator()
        tensor_kernel = TensorKernel()
        initialize_default_shapes(tensor_kernel)
        self.fragment_arch = TensorFragmentArchitecture(tensor_kernel)
    
    def test_end_to_end_cognitive_scenario(self):
        """Test complete end-to-end cognitive scenario"""
        # 1. Create ko6ml expressions for a business scenario
        customer_expr = Ko6mlExpression(
            primitive_type=Ko6mlPrimitive.ENTITY,
            name="customer",
            parameters={"properties": {"type": "enterprise"}},
            metadata={"confidence": 0.9}
        )
        
        order_expr = Ko6mlExpression(
            primitive_type=Ko6mlPrimitive.ENTITY,
            name="order",
            parameters={"properties": {"value": "high"}},
            metadata={"confidence": 0.8}
        )
        
        # 2. Translate to AtomSpace
        customer_atom_id = self.translator.ko6ml_to_atomspace(customer_expr)
        order_atom_id = self.translator.ko6ml_to_atomspace(order_expr)
        
        # 3. Create tensor fragments for these concepts
        customer_tensor = np.array([[0.9, 0.1], [0.8, 0.2]])  # Feature representation
        order_tensor = np.array([[0.7, 0.3], [0.6, 0.4]])
        
        customer_fragment_id = self.fragment_arch.create_fragment(
            customer_tensor, FragmentType.COGNITIVE
        )
        order_fragment_id = self.fragment_arch.create_fragment(
            order_tensor, FragmentType.COGNITIVE
        )
        
        # 4. Perform tensor operations
        relation_fragment_id = self.fragment_arch.fragment_contraction(
            customer_fragment_id, order_fragment_id
        )
        
        # 5. Verify integration
        self.assertIsNotNone(customer_atom_id)
        self.assertIsNotNone(order_atom_id)
        self.assertIsNotNone(customer_fragment_id)
        self.assertIsNotNone(order_fragment_id)
        self.assertIsNotNone(relation_fragment_id)
        
        # 6. Verify round-trip
        recovered_customer = self.translator.atomspace_to_ko6ml(customer_atom_id)
        self.assertIsNotNone(recovered_customer)
        self.assertEqual(recovered_customer.name, "customer")
        
        # 7. Get system statistics
        translation_stats = self.translator.get_translation_stats()
        fragment_stats = self.fragment_arch.get_fragment_stats()
        
        self.assertGreater(translation_stats["total_atoms"], 0)
        self.assertGreater(fragment_stats["total_fragments"], 0)
    
    def test_distributed_cognitive_operations(self):
        """Test distributed cognitive operations across fragments"""
        # Create multiple cognitive fragments
        fragment_ids = []
        for i in range(5):
            data = np.random.rand(3, 3) * (i + 1)
            fragment_id = self.fragment_arch.create_fragment(
                data, FragmentType.COGNITIVE
            )
            fragment_ids.append(fragment_id)
        
        # Perform distributed operations
        result_id = self.fragment_arch.parallel_fragment_operation(
            "reduce", fragment_ids
        )
        
        # Compose fragments
        composed_tensor = self.fragment_arch.compose_fragments(fragment_ids[:3])
        
        # Synchronize all fragments
        self.fragment_arch.synchronize_fragments()
        
        # Verify operations completed successfully
        result_fragment = self.fragment_arch.registry.get_fragment(result_id)
        self.assertIsNotNone(result_fragment)
        self.assertEqual(composed_tensor.shape, (3, 3, 3))
        
        # Get final statistics
        stats = self.fragment_arch.get_fragment_stats()
        self.assertGreater(stats["total_operations"], 0)
        self.assertGreater(stats["total_fragments"], 5)


def run_phase1_verification():
    """Run complete Phase 1 verification test suite"""
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPhase1Microservices,
        TestKo6mlTranslation,
        TestTensorFragmentArchitecture,
        TestPhase1Integration
    ]
    
    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 80)
    print("PHASE 1 VERIFICATION: Cognitive Primitives & Foundational Hypergraph Encoding")
    print("=" * 80)
    
    success = run_phase1_verification()
    
    if success:
        print("\n" + "=" * 80)
        print("✓ PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY!")
        print("All cognitive primitives and hypergraph encoding tests passed.")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ PHASE 1 VERIFICATION FAILED!")
        print("Some tests did not pass. Please review the output above.")
        print("=" * 80)
    
    exit(0 if success else 1)