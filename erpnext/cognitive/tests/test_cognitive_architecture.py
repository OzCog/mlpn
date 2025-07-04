"""
Comprehensive tests for the cognitive architecture system
"""

import unittest
import numpy as np
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tensor_kernel import TensorKernel, TensorFormat, initialize_default_shapes
from cognitive_grammar import (
    CognitiveGrammar, AtomSpace, PLN, PatternMatcher, 
    AtomType, LinkType, TruthValue
)
from attention_allocation import (
    ECANAttention, AttentionBank, ActivationSpreading, 
    AttentionType, EconomicParams
)
from meta_cognitive import (
    MetaCognitive, MetaStateMonitor, RecursiveIntrospector,
    MetaLayer, MetaTensor
)


class TestTensorKernel(unittest.TestCase):
    """Test cases for TensorKernel"""
    
    def setUp(self):
        self.kernel = TensorKernel()
        initialize_default_shapes(self.kernel)
        
    def test_tensor_creation(self):
        """Test tensor creation with different formats"""
        data = [[1, 2, 3], [4, 5, 6]]
        tensor = self.kernel.create_tensor(data, TensorFormat.NUMPY)
        
        self.assertIsInstance(tensor, np.ndarray)
        self.assertEqual(tensor.shape, (2, 3))
        
    def test_canonical_shapes(self):
        """Test canonical shape definition and retrieval"""
        # Test predefined shapes
        attention_shape = self.kernel.get_canonical_shape("attention")
        self.assertIsNotNone(attention_shape)
        self.assertIn("batch_size", attention_shape)
        
        # Test custom shape
        self.kernel.define_canonical_shape("test", {"dim1": 10, "dim2": 20})
        test_shape = self.kernel.get_canonical_shape("test")
        self.assertEqual(test_shape["dim1"], 10)
        self.assertEqual(test_shape["dim2"], 20)
        
    def test_tensor_contraction(self):
        """Test tensor contraction operations"""
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        
        result = self.kernel.tensor_contraction(a, b)
        expected = np.dot(a, b)
        
        np.testing.assert_array_equal(result, expected)
        
    def test_parallel_operations(self):
        """Test parallel tensor operations"""
        tensors = [np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])]
        
        # Test reduce operation
        result = self.kernel.parallel_operation("reduce", tensors)
        expected = np.sum(tensors, axis=0)
        np.testing.assert_array_equal(result, expected)
        
        # Test map operation
        result = self.kernel.parallel_operation("map", tensors, func=lambda x: x * 2)
        expected = [t * 2 for t in tensors]
        for i, r in enumerate(result):
            np.testing.assert_array_equal(r, expected[i])
            
    def test_meta_learning_update(self):
        """Test A0ML meta-learning updates"""
        params = np.array([1.0, 2.0, 3.0])
        gradients = np.array([0.1, 0.2, 0.3])
        learning_rate = 0.01
        
        updated = self.kernel.meta_learning_update(learning_rate, gradients, params)
        expected = params - learning_rate * gradients
        
        np.testing.assert_array_equal(updated, expected)
        
    def test_operation_stats(self):
        """Test operation statistics tracking"""
        # Perform some operations
        self.kernel.create_tensor([1, 2, 3])
        self.kernel.tensor_contraction(np.array([1, 2]), np.array([3, 4]))
        
        stats = self.kernel.get_operation_stats()
        
        self.assertIn("operation_count", stats)
        self.assertIn("cached_tensors", stats)
        self.assertIn("registered_shapes", stats)
        self.assertGreater(stats["operation_count"], 0)
        
    def test_scheme_tensor_shape(self):
        """Test Scheme specification generation"""
        scheme_spec = self.kernel.scheme_tensor_shape("attention")
        
        self.assertIn("define", scheme_spec)
        self.assertIn("tensor-shape", scheme_spec)
        self.assertIn("attention", scheme_spec)


class TestCognitiveGrammar(unittest.TestCase):
    """Test cases for CognitiveGrammar"""
    
    def setUp(self):
        self.grammar = CognitiveGrammar()
        
    def test_entity_creation(self):
        """Test entity creation in knowledge base"""
        entity_id = self.grammar.create_entity("test_entity")
        
        self.assertIsInstance(entity_id, str)
        atom = self.grammar.atomspace.get_atom(entity_id)
        self.assertIsNotNone(atom)
        self.assertEqual(atom.name, "test_entity")
        
    def test_relationship_creation(self):
        """Test relationship creation between entities"""
        entity1 = self.grammar.create_entity("entity1")
        entity2 = self.grammar.create_entity("entity2")
        
        relationship = self.grammar.create_relationship(entity1, entity2)
        
        self.assertIsInstance(relationship, str)
        link = self.grammar.atomspace.get_link(relationship)
        self.assertIsNotNone(link)
        self.assertIn(entity1, link.atoms)
        self.assertIn(entity2, link.atoms)
        
    def test_atom_space_operations(self):
        """Test AtomSpace operations"""
        atomspace = AtomSpace()
        
        # Test atom creation
        atom_id = atomspace.add_atom("test", AtomType.CONCEPT)
        atom = atomspace.get_atom(atom_id)
        self.assertEqual(atom.name, "test")
        self.assertEqual(atom.atom_type, AtomType.CONCEPT)
        
        # Test link creation
        atom2_id = atomspace.add_atom("test2", AtomType.CONCEPT)
        link_id = atomspace.add_link(LinkType.SIMILARITY, [atom_id, atom2_id])
        link = atomspace.get_link(link_id)
        self.assertEqual(link.link_type, LinkType.SIMILARITY)
        
    def test_pln_inference(self):
        """Test PLN inference operations"""
        atomspace = AtomSpace()
        pln = PLN(atomspace)
        
        # Create test atoms and links
        atom1 = atomspace.add_atom("A", AtomType.CONCEPT)
        atom2 = atomspace.add_atom("B", AtomType.CONCEPT)
        atom3 = atomspace.add_atom("C", AtomType.CONCEPT)
        
        link1 = atomspace.add_link(LinkType.IMPLICATION, [atom1, atom2],
                                  TruthValue(0.8, 0.9))
        link2 = atomspace.add_link(LinkType.IMPLICATION, [atom2, atom3],
                                  TruthValue(0.7, 0.8))
        
        # Test deduction
        result = pln.deduction(link1, link2)
        self.assertIsInstance(result, TruthValue)
        self.assertGreater(result.strength, 0)
        self.assertGreater(result.confidence, 0)
        
    def test_pattern_matching(self):
        """Test pattern matching functionality"""
        atomspace = AtomSpace()
        matcher = PatternMatcher(atomspace)
        
        # Create test atoms
        atom1 = atomspace.add_atom("high_conf", AtomType.CONCEPT, 
                                  TruthValue(0.9, 0.9))
        atom2 = atomspace.add_atom("low_conf", AtomType.CONCEPT, 
                                  TruthValue(0.3, 0.3))
        
        # Test pattern matching
        matches = matcher.match_pattern("high_confidence", [atom1, atom2])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["atom_id"], atom1)
        
    def test_knowledge_stats(self):
        """Test knowledge statistics"""
        # Create some entities and relationships
        entity1 = self.grammar.create_entity("entity1")
        entity2 = self.grammar.create_entity("entity2")
        self.grammar.create_relationship(entity1, entity2)
        
        stats = self.grammar.get_knowledge_stats()
        
        self.assertIn("total_atoms", stats)
        self.assertIn("total_links", stats)
        self.assertIn("hypergraph_density", stats)
        self.assertGreater(stats["total_atoms"], 0)
        self.assertGreater(stats["total_links"], 0)


class TestAttentionAllocation(unittest.TestCase):
    """Test cases for ECAN attention allocation"""
    
    def setUp(self):
        self.attention = ECANAttention()
        
    def test_attention_focus(self):
        """Test attention focusing mechanism"""
        self.attention.focus_attention("test_atom", 1.0)
        
        attention_val = self.attention.attention_bank.attention_values.get("test_atom")
        self.assertIsNotNone(attention_val)
        self.assertGreater(attention_val.sti, 0)
        
    def test_attention_spreading(self):
        """Test attention spreading to connected atoms"""
        # Set up connections
        self.attention.connections = {
            "atom1": ["atom2", "atom3"],
            "atom2": ["atom4"]
        }
        
        # Focus on atom1
        self.attention.focus_attention("atom1", 2.0)
        
        # Check that attention spread to connected atoms
        atom2_attention = self.attention.attention_bank.attention_values.get("atom2")
        self.assertIsNotNone(atom2_attention)
        self.assertGreater(atom2_attention.sti, 0)
        
    def test_economic_allocation(self):
        """Test economic wage and rent allocation"""
        # Create some atoms with different attention values
        self.attention.focus_attention("atom1", 3.0)
        self.attention.focus_attention("atom2", 1.0)
        
        # Update economy
        self.attention.update_attention_economy()
        
        # Check wages and rents were allocated
        self.assertGreater(len(self.attention.attention_bank.wages), 0)
        self.assertGreater(len(self.attention.attention_bank.rents), 0)
        
    def test_attention_visualization(self):
        """Test attention tensor visualization"""
        # Create attention values
        self.attention.focus_attention("atom1", 2.0)
        self.attention.focus_attention("atom2", 1.5)
        
        # Get visualization tensor
        tensor = self.attention.visualize_attention_tensor(["atom1", "atom2"])
        
        self.assertEqual(tensor.shape, (2, 3))  # 2 atoms, 3 attention types
        self.assertGreater(tensor[0, 0], 0)  # atom1 STI
        
    def test_attention_cycle(self):
        """Test complete attention cycle"""
        # Set up connections
        self.attention.connections = {"atom1": ["atom2"]}
        
        # Run attention cycle
        self.attention.run_attention_cycle(["atom1"])
        
        # Check that attention was allocated and economy updated
        stats = self.attention.get_economic_stats()
        self.assertIn("total_wages", stats)
        self.assertIn("total_rents", stats)
        
    def test_activation_spreading(self):
        """Test activation spreading mechanism"""
        connections = {
            "atom1": ["atom2", "atom3"],
            "atom2": ["atom3"],
            "atom3": []
        }
        
        spreader = ActivationSpreading(connections)
        spreader.initialize_activation(["atom1", "atom2", "atom3"])
        spreader.spread_activation(iterations=5)
        
        # Check that activation was spread
        top_activated = spreader.get_top_activated(3)
        self.assertEqual(len(top_activated), 3)
        
    def test_scheme_attention_spec(self):
        """Test Scheme specification generation"""
        scheme_spec = self.attention.scheme_attention_spec()
        
        self.assertIn("attention-allocate", scheme_spec)
        self.assertIn("attention-spread", scheme_spec)
        self.assertIn("attention-focus", scheme_spec)


class TestMetaCognitive(unittest.TestCase):
    """Test cases for meta-cognitive system"""
    
    def setUp(self):
        self.meta = MetaCognitive()
        
        # Create mock cognitive layers
        self.mock_tensor_kernel = MagicMock()
        self.mock_tensor_kernel.get_operation_stats.return_value = {
            "operation_count": 10,
            "cached_tensors": 5,
            "registered_shapes": 3,
            "backend": "cpu"
        }
        
        self.mock_grammar = MagicMock()
        self.mock_grammar.get_knowledge_stats.return_value = {
            "total_atoms": 100,
            "total_links": 50,
            "hypergraph_density": 0.5,
            "pattern_count": 10
        }
        
        self.mock_attention = MagicMock()
        self.mock_attention.get_economic_stats.return_value = {
            "total_wages": 80.0,
            "total_rents": 40.0,
            "wage_fund": 100.0,
            "rent_fund": 50.0
        }
        
    def test_layer_registration(self):
        """Test cognitive layer registration"""
        self.meta.register_layer(MetaLayer.TENSOR_KERNEL, self.mock_tensor_kernel)
        
        self.assertIn(MetaLayer.TENSOR_KERNEL, self.meta.cognitive_layers)
        self.assertEqual(self.meta.cognitive_layers[MetaLayer.TENSOR_KERNEL], 
                        self.mock_tensor_kernel)
        
    def test_meta_state_update(self):
        """Test meta-state update process"""
        # Register layers
        self.meta.register_layer(MetaLayer.TENSOR_KERNEL, self.mock_tensor_kernel)
        self.meta.register_layer(MetaLayer.COGNITIVE_GRAMMAR, self.mock_grammar)
        
        # Update meta-state
        self.meta.update_meta_state()
        
        # Check that meta-tensors were created
        self.assertGreater(len(self.meta.meta_tensor_history), 0)
        latest_tensors = self.meta.meta_tensor_history[-1]
        self.assertIn(MetaLayer.TENSOR_KERNEL, latest_tensors)
        self.assertIn(MetaLayer.COGNITIVE_GRAMMAR, latest_tensors)
        
    def test_introspection(self):
        """Test recursive introspection"""
        self.meta.register_layer(MetaLayer.TENSOR_KERNEL, self.mock_tensor_kernel)
        
        # Perform introspection
        result = self.meta.perform_deep_introspection(MetaLayer.TENSOR_KERNEL)
        
        self.assertIn("layer", result)
        self.assertIn("structure", result)
        self.assertIn("behavior", result)
        self.assertIn("state", result)
        
    def test_system_health_diagnosis(self):
        """Test system health diagnosis"""
        # Register layers and update state
        self.meta.register_layer(MetaLayer.TENSOR_KERNEL, self.mock_tensor_kernel)
        self.meta.update_meta_state()
        
        # Diagnose health
        health = self.meta.diagnose_system_health()
        
        self.assertIn("status", health)
        self.assertIn("errors", health)
        self.assertIn("stability_score", health)
        self.assertIn("coherence_score", health)
        
    def test_meta_tensor_dynamics(self):
        """Test meta-tensor dynamics analysis"""
        # Register layer and create some history
        self.meta.register_layer(MetaLayer.TENSOR_KERNEL, self.mock_tensor_kernel)
        
        # Create multiple state updates
        for _ in range(5):
            self.meta.update_meta_state()
            
        # Get dynamics
        dynamics = self.meta.get_meta_tensor_dynamics(MetaLayer.TENSOR_KERNEL)
        
        self.assertGreater(len(dynamics), 0)
        
    def test_system_stats(self):
        """Test comprehensive system statistics"""
        # Register layers
        self.meta.register_layer(MetaLayer.TENSOR_KERNEL, self.mock_tensor_kernel)
        self.meta.register_layer(MetaLayer.COGNITIVE_GRAMMAR, self.mock_grammar)
        
        # Update state
        self.meta.update_meta_state()
        
        # Get stats
        stats = self.meta.get_system_stats()
        
        self.assertIn("registered_layers", stats)
        self.assertIn("meta_tensor_history_length", stats)
        self.assertIn("system_health", stats)
        self.assertEqual(stats["registered_layers"], 2)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete cognitive architecture"""
    
    def test_full_integration(self):
        """Test full integration of all components"""
        # Create all components
        tensor_kernel = TensorKernel()
        initialize_default_shapes(tensor_kernel)
        
        grammar = CognitiveGrammar()
        attention = ECANAttention()
        meta_cognitive = MetaCognitive()
        
        # Register layers with meta-cognitive system
        meta_cognitive.register_layer(MetaLayer.TENSOR_KERNEL, tensor_kernel)
        meta_cognitive.register_layer(MetaLayer.COGNITIVE_GRAMMAR, grammar)
        meta_cognitive.register_layer(MetaLayer.ATTENTION_ALLOCATION, attention)
        
        # Create some knowledge
        entity1 = grammar.create_entity("knowledge_entity")
        entity2 = grammar.create_entity("related_entity")
        grammar.create_relationship(entity1, entity2)
        
        # Focus attention
        attention.focus_attention("knowledge_entity", 2.0)
        
        # Perform tensor operations
        tensor_kernel.create_tensor([[1, 2], [3, 4]])
        
        # Update meta-cognitive state
        meta_cognitive.update_meta_state()
        
        # Run attention cycle
        attention.run_attention_cycle([entity1])
        
        # Check integration
        stats = meta_cognitive.get_system_stats()
        self.assertEqual(stats["registered_layers"], 3)
        
        # Check knowledge was created
        knowledge_stats = grammar.get_knowledge_stats()
        self.assertGreater(knowledge_stats["total_atoms"], 0)
        
        # Check attention was allocated
        attention_stats = attention.get_economic_stats()
        self.assertGreater(attention_stats["total_wages"], 0)
        
        # Check tensor operations
        tensor_stats = tensor_kernel.get_operation_stats()
        self.assertGreater(tensor_stats["operation_count"], 0)
        
    def test_scheme_integration(self):
        """Test Scheme specification integration"""
        tensor_kernel = TensorKernel()
        initialize_default_shapes(tensor_kernel)
        
        grammar = CognitiveGrammar()
        attention = ECANAttention()
        
        # Generate Scheme specifications
        tensor_scheme = tensor_kernel.scheme_tensor_shape("attention")
        pattern_scheme = grammar.pattern_matcher.scheme_pattern_match("entity")
        attention_scheme = attention.scheme_attention_spec()
        
        # Check that all specifications are valid Scheme
        self.assertIn("define", tensor_scheme)
        self.assertIn("define", pattern_scheme)
        self.assertIn("define", attention_scheme)
        
        # Check specific elements
        self.assertIn("tensor-shape", tensor_scheme)
        self.assertIn("pattern-match", pattern_scheme)
        self.assertIn("attention-allocate", attention_scheme)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)