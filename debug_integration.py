#!/usr/bin/env python3
"""Debug integration testing scores"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erpnext', 'cognitive'))

from tensor_kernel import TensorKernel
from cognitive_grammar import CognitiveGrammar
from attention_allocation import ECANAttention
from meta_cognitive import MetaCognitive
from phase6_integration_test import CognitiveUnificationEngine

def debug_integration():
    # Initialize components
    tensor_kernel = TensorKernel()
    grammar = CognitiveGrammar()
    attention = ECANAttention()
    meta_cognitive = MetaCognitive()
    
    components = {
        'tensor_kernel': tensor_kernel,
        'grammar': grammar,
        'attention': attention,
        'meta_cognitive': meta_cognitive
    }
    
    unification_engine = CognitiveUnificationEngine(components)
    
    print("=== Debug Integration Testing ===")
    
    # Test 1: Unification validation
    print("\n1. Testing unification validation...")
    try:
        unified_validation = unification_engine.validate_unified_cognitive_architecture()
        unification_score = unified_validation.get('overall_unification_score', 0)
        print(f"   Unification score: {unification_score}")
        print(f"   Unification achieved: {unification_score > 0.7}")
    except Exception as e:
        print(f"   Error: {e}")
        
    # Test 2: End-to-end workflow
    print("\n2. Testing end-to-end workflow...")
    try:
        import numpy as np
        
        # Phase 1: Tensor operations
        test_tensor = tensor_kernel.create_tensor([[1, 2], [3, 4]], 'numpy')
        print(f"   Tensor created: {test_tensor is not None}")
        
        # Phase 2: Knowledge representation
        entity = grammar.create_entity("integration_test_entity")
        print(f"   Entity created: {entity is not None}")
        
        # Phase 3: Attention allocation
        attention.focus_attention(entity, 2.0)
        print(f"   Attention focused: {entity in attention.attention_bank.attention_values}")
        
        # Phase 4: Meta-cognitive monitoring
        try:
            print(f"   About to call update_meta_state...")
            print(f"   Registered layers: {list(meta_cognitive.cognitive_layers.keys())}")
            meta_cognitive.update_meta_state()
            print(f"   Meta state updated: {len(meta_cognitive.meta_tensor_history) > 0}")
            workflow_success = True
        except Exception as e:
            print(f"   Meta state update error: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            workflow_success = False
        
        workflow_complete = all([
            test_tensor is not None,
            entity is not None,
            len(meta_cognitive.meta_tensor_history) > 0,
            workflow_success if 'workflow_success' in locals() else True
        ])
        print(f"   Workflow complete: {workflow_complete}")
        
    except Exception as e:
        print(f"   Error: {e}")
        
    # Test 3: System health
    print("\n3. Testing system health...")
    try:
        health = meta_cognitive.diagnose_system_health()
        coherence_score = health.get('coherence_score', 0)
        stability_score = health.get('stability_score', 0)
        
        print(f"   Coherence score: {coherence_score}")
        print(f"   Stability score: {stability_score}")
        print(f"   Coherence > 0.5: {coherence_score > 0.5}")
        print(f"   Stability > 0.5: {stability_score > 0.5}")
        print(f"   Health status: {health.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"   Error: {e}")
        
    # Test 4: Data flow integration
    print("\n4. Testing data flow integration...")
    try:
        entity1 = grammar.create_entity("flow_test_1")
        entity2 = grammar.create_entity("flow_test_2")
        relationship = grammar.create_relationship(entity1, entity2)
        
        attention.focus_attention(entity1, 2.0)
        attention.focus_attention(entity2, 1.5)
        
        initial_length = len(meta_cognitive.meta_tensor_history)
        meta_cognitive.update_meta_state()
        final_length = len(meta_cognitive.meta_tensor_history)
        
        data_flow_integration = (
            relationship is not None and
            final_length > initial_length
        )
        
        print(f"   Relationship created: {relationship is not None}")
        print(f"   Meta history grew: {final_length > initial_length} ({initial_length} -> {final_length})")
        print(f"   Data flow integration: {data_flow_integration}")
        
    except Exception as e:
        print(f"   Error: {e}")
        
    # Summary
    print("\n=== Summary ===")
    integration_checks = [
        unification_score > 0.7 if 'unification_score' in locals() else False,
        workflow_complete if 'workflow_complete' in locals() else False,
        data_flow_integration if 'data_flow_integration' in locals() else False,
        coherence_score > 0.5 if 'coherence_score' in locals() else False,
        stability_score > 0.5 if 'stability_score' in locals() else False,
    ]
    
    print(f"Integration checks: {integration_checks}")
    print(f"Passed checks: {sum(integration_checks)}/5")
    print(f"Confidence: {sum(integration_checks) / 5:.3f}")

if __name__ == "__main__":
    debug_integration()