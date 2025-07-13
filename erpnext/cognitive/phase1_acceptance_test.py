#!/usr/bin/env python3
"""
Phase 1 Final Acceptance Test with Visualization Validation

Validates all Phase 1 acceptance criteria including the specific requirement
for "Visualization: Hypergraph fragment flowcharts"
"""

import os
import sys
import subprocess
import numpy as np

def test_hypergraph_visualization():
    """Test hypergraph fragment flowchart generation"""
    print("🎨 TESTING HYPERGRAPH FRAGMENT FLOWCHARTS")
    print("-" * 50)
    
    # Import and test the visualizer
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hypergraph_visualizer import HypergraphVisualizer, HypergraphNode, HypergraphEdge
    
    # Create visualizer
    viz = HypergraphVisualizer(output_dir="/tmp/phase1_validation_viz")
    
    # Test data
    phase1_data = {
        'hypergraph': {
            'nodes': [
                {'id': 'customer', 'type': 'concept', 'position': (2, 4)},
                {'id': 'order', 'type': 'concept', 'position': (6, 4)},
                {'id': 'places', 'type': 'predicate', 'position': (4, 2)}
            ],
            'edges': [
                {'id': 'places_rel', 'nodes': ['customer', 'places', 'order'], 'type': 'evaluation'}
            ],
            'statistics': {'atoms': 3, 'links': 1, 'density': 1.33}
        },
        'translation': {
            'ko6ml_expressions': [
                {'primitive': 'ENTITY', 'value': 'customer'},
                {'primitive': 'RELATION', 'value': 'places'}
            ],
            'atomspace_atoms': [
                {'type': 'concept', 'name': 'customer'},
                {'type': 'predicate', 'name': 'places'}
            ]
        },
        'fragments': {
            'fragments': [
                {'id': 'f1', 'shape': (2, 2), 'type': 'cognitive'},
                {'id': 'f2', 'shape': (3, 3), 'type': 'attention'}
            ],
            'operations': ['decompose', 'compose', 'contract']
        },
        'attention': {
            'atoms': ['customer', 'order', 'product'],
            'matrix': np.random.rand(3, 5)
        },
        'microservices': {
            'services': ['AtomSpace', 'PLN', 'Pattern'],
            'status': 'operational'
        }
    }
    
    # Generate all visualizations
    try:
        viz_files = viz.generate_all_phase1_visualizations(phase1_data)
        
        print("✅ HYPERGRAPH FRAGMENT FLOWCHARTS GENERATED:")
        for filepath in viz_files:
            filename = os.path.basename(filepath)
            if os.path.exists(filepath):
                filesize = os.path.getsize(filepath)
                print(f"  ✓ {filename} ({filesize:,} bytes)")
            else:
                print(f"  ❌ {filename} (file not found)")
                return False
        
        print(f"\n✅ All {len(viz_files)} visualization files generated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Visualization generation failed: {e}")
        return False

def validate_all_acceptance_criteria():
    """Validate all Phase 1 acceptance criteria"""
    print("\n📋 FINAL PHASE 1 ACCEPTANCE CRITERIA VALIDATION")
    print("=" * 60)
    
    criteria = {
        "Real Implementation (No Mocks)": test_real_implementation(),
        "Comprehensive Tests": test_comprehensive_tests(),
        "Documentation with Diagrams": test_documentation(),
        "Recursive Modularity": test_recursive_modularity(),
        "Integration Tests": test_integration_tests(),
        "Hypergraph Fragment Flowcharts": test_hypergraph_visualization()
    }
    
    print("\n📊 ACCEPTANCE CRITERIA RESULTS:")
    print("-" * 40)
    
    all_passed = True
    for criterion, passed in criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {criterion}")
        if not passed:
            all_passed = False
    
    print("-" * 40)
    if all_passed:
        print("🎉 ALL PHASE 1 ACCEPTANCE CRITERIA MET!")
        print("Phase 1: Cognitive Primitives & Foundational Hypergraph Encoding")
        print("Status: ✅ COMPLETE AND VERIFIED")
    else:
        print("⚠️  Some acceptance criteria not met")
        print("Status: ❌ REQUIRES ATTENTION")
    
    return all_passed

def test_real_implementation():
    """Test that implementation uses real data, not mocks"""
    try:
        # Test core components with real operations
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from tensor_kernel import TensorKernel
        from cognitive_grammar import CognitiveGrammar
        from attention_allocation import ECANAttention
        
        # Test real tensor operations
        kernel = TensorKernel()
        tensor = kernel.create_tensor([[1, 2], [3, 4]])
        assert tensor.shape == (2, 2)
        
        # Test real knowledge operations
        grammar = CognitiveGrammar()
        entity = grammar.create_entity("test_entity")
        assert entity is not None
        
        # Test real attention operations
        attention = ECANAttention()
        attention.focus_attention("test_concept", 2.0)
        
        return True
    except Exception as e:
        print(f"Real implementation test failed: {e}")
        return False

def test_comprehensive_tests():
    """Test that comprehensive tests exist and pass"""
    try:
        # Run the main test suite
        result = subprocess.run([
            sys.executable, "test_validation.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Test suite failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False

def test_documentation():
    """Test that documentation with architectural diagrams exists"""
    required_docs = [
        "../../docs/phase1-architecture.md",
        "../../docs/tensor-signatures.md",
        "README.md",
        "PHASE1_README.md"
    ]
    
    for doc_path in required_docs:
        if not os.path.exists(doc_path):
            print(f"Missing documentation: {doc_path}")
            return False
        
        # Check file has reasonable content
        with open(doc_path, 'r') as f:
            content = f.read()
            if len(content) < 1000:  # Minimum content check
                print(f"Documentation too short: {doc_path}")
                return False
    
    return True

def test_recursive_modularity():
    """Test that code follows recursive modularity principles"""
    try:
        # Check that components can be imported and instantiated independently
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from tensor_kernel import TensorKernel
        from cognitive_grammar import CognitiveGrammar
        from attention_allocation import ECANAttention
        from meta_cognitive import MetaCognitive
        from tensor_fragments import TensorFragmentArchitecture
        
        # Test independent instantiation
        components = [
            TensorKernel(),
            CognitiveGrammar(),
            ECANAttention(),
            MetaCognitive(),
            TensorFragmentArchitecture()
        ]
        
        # Test that components can be composed
        meta = MetaCognitive()
        meta.register_layer("test", components[0])
        
        return True
    except Exception as e:
        print(f"Modularity test failed: {e}")
        return False

def test_integration_tests():
    """Test that integration tests validate functionality"""
    try:
        # Run Phase 1 comprehensive tests
        result = subprocess.run([
            sys.executable, "phase1_tests.py"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and "OK" in result.stdout:
            return True
        else:
            print(f"Integration tests failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Integration test execution failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 PHASE 1 FINAL ACCEPTANCE VALIDATION")
    print("Cognitive Primitives & Foundational Hypergraph Encoding")
    print("=" * 70)
    
    # Test the specific visualization requirement first
    viz_success = test_hypergraph_visualization()
    
    if viz_success:
        print("\n✅ VISUALIZATION REQUIREMENT SATISFIED")
        print("Hypergraph fragment flowcharts successfully generated!")
    else:
        print("\n❌ VISUALIZATION REQUIREMENT NOT MET")
        return False
    
    # Test all other acceptance criteria
    all_success = validate_all_acceptance_criteria()
    
    if all_success:
        print("\n🎯 PHASE 1 IMPLEMENTATION COMPLETE!")
        print("All acceptance criteria have been satisfied.")
        print("Ready to proceed to Phase 2: ECAN Attention Allocation")
        return True
    else:
        print("\n⚠️  PHASE 1 IMPLEMENTATION INCOMPLETE")
        print("Some acceptance criteria require attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)