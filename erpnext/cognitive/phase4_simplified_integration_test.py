#!/usr/bin/env python3
"""
Phase 4: Simplified Full-Stack Integration Test

Focused test demonstrating core embodiment interface recursion functionality
with stable synthesis operations.
"""

import time
import json
import numpy as np
import unittest
from typing import Dict, List, Any
import logging

# Import Phase 4 components
from phase4_api_server import CognitiveAPIServer, CognitiveTask, EmbodimentBinding
from unity3d_adapter import Unity3DIntegrationAdapter, Unity3DCognitiveAgent
from ros_adapter import ROSIntegrationAdapter, ROSCognitiveAgent
from web_agent_adapter import WebAgentIntegrationAdapter, WebAgent

logger = logging.getLogger(__name__)


class Phase4SimplifiedIntegrationTest(unittest.TestCase):
    """Simplified integration test focusing on core functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test infrastructure"""
        cls.api_server = CognitiveAPIServer(host="127.0.0.1", port=15020, debug=False)
        cls.unity_adapter = Unity3DIntegrationAdapter(port=17790)
        cls.ros_adapter = ROSIntegrationAdapter(port=18900)
        cls.web_adapter = WebAgentIntegrationAdapter(host="127.0.0.1", port=16680)
        
        logger.info("Phase 4 Simplified Integration Test infrastructure initialized")
    
    def test_embodiment_recursion_level_1(self):
        """Test Level 1: Direct embodiment recursion"""
        print("\n🔄 Testing Level 1: Direct Embodiment Recursion")
        
        # Unity3D direct cognitive processing
        unity_input = {
            'symbolic_input': {
                'concept': 'unity_spatial_navigation',
                'truth_value': {'strength': 0.9, 'confidence': 0.85}
            },
            'neural_input': np.random.randn(256),
        }
        
        unity_result = self.api_server.neural_symbolic.synthesize(
            unity_input['symbolic_input'],
            unity_input['neural_input'],
            'conceptual_embedding'
        )
        
        self.assertIsInstance(unity_result, np.ndarray)
        self.assertGreater(len(unity_result), 0)
        print(f"  ✓ Unity3D Level 1: {unity_result.shape}")
        
        # ROS direct cognitive processing
        ros_input = {
            'symbolic_input': {
                'concept': 'ros_sensor_processing',
                'truth_value': {'strength': 0.88, 'confidence': 0.92}
            },
            'neural_input': np.random.randn(360),  # Laser scan
        }
        
        ros_result = self.api_server.neural_symbolic.synthesize(
            ros_input['symbolic_input'],
            ros_input['neural_input'],
            'attention_allocation'
        )
        
        self.assertIsInstance(ros_result, np.ndarray)
        self.assertGreater(len(ros_result), 0)
        print(f"  ✓ ROS Level 1: {ros_result.shape}")
        
        # Web direct cognitive processing
        web_input = {
            'symbolic_input': {
                'concept': 'web_user_interaction',
                'truth_value': {'strength': 0.95, 'confidence': 0.90}
            },
            'neural_input': np.random.randn(128),
        }
        
        web_result = self.api_server.neural_symbolic.synthesize(
            web_input['symbolic_input'],
            web_input['neural_input'],
            'logical_inference'
        )
        
        self.assertIsInstance(web_result, np.ndarray)
        self.assertGreater(len(web_result), 0)
        print(f"  ✓ Web Level 1: {web_result.shape}")
        
        print("✅ Level 1 Direct Embodiment Recursion: All platforms successful")
    
    def test_embodiment_recursion_level_2(self):
        """Test Level 2: Cross-platform embodiment recursion"""
        print("\n🔄 Testing Level 2: Cross-Platform Embodiment Recursion")
        
        # Step 1: Unity3D processes environment
        unity_input = {
            'symbolic_input': {
                'concept': 'environment_simulation',
                'truth_value': {'strength': 0.92, 'confidence': 0.88}
            },
            'neural_input': np.random.randn(512),
        }
        
        unity_result = self.api_server.neural_symbolic.synthesize(
            unity_input['symbolic_input'],
            unity_input['neural_input'],
            'conceptual_embedding'
        )
        
        # Step 2: ROS uses Unity data for navigation planning
        ros_input = {
            'symbolic_input': {
                'concept': 'navigation_planning',
                'truth_value': {'strength': 0.85, 'confidence': 0.93},
                'context': 'unity_environment_data'
            },
            'neural_input': unity_result,  # Use Unity result as input
        }
        
        ros_result = self.api_server.neural_symbolic.synthesize(
            ros_input['symbolic_input'],
            ros_input['neural_input'],
            'attention_allocation'
        )
        
        # Step 3: Web agent visualizes combined results
        web_input = {
            'symbolic_input': {
                'concept': 'visualization_synthesis',
                'truth_value': {'strength': 0.90, 'confidence': 0.91},
                'context': 'unity_ros_combined_data'
            },
            'neural_input': ros_result,  # Use ROS result as input
        }
        
        web_result = self.api_server.neural_symbolic.synthesize(
            web_input['symbolic_input'],
            web_input['neural_input'],
            'logical_inference'
        )
        
        # Validate recursive data flow
        self.assertIsInstance(unity_result, np.ndarray)
        self.assertIsInstance(ros_result, np.ndarray)
        self.assertIsInstance(web_result, np.ndarray)
        
        print(f"  ✓ Unity→ROS→Web chain: {unity_result.shape} → {ros_result.shape} → {web_result.shape}")
        print("✅ Level 2 Cross-Platform Recursion: Data flow successful")
    
    def test_embodiment_recursion_level_3(self):
        """Test Level 3: Meta-cognitive embodiment recursion"""
        print("\n🔄 Testing Level 3: Meta-Cognitive Embodiment Recursion")
        
        # Collect results from all platforms
        platform_results = []
        
        # Unity3D meta-analysis
        unity_meta_input = {
            'symbolic_input': {
                'concept': 'unity_performance_analysis',
                'truth_value': {'strength': 0.94, 'confidence': 0.89}
            },
            'neural_input': np.random.randn(256),
        }
        
        unity_meta_result = self.api_server.neural_symbolic.synthesize(
            unity_meta_input['symbolic_input'],
            unity_meta_input['neural_input'],
            'conceptual_embedding'
        )
        platform_results.append(unity_meta_result)
        
        # ROS meta-analysis
        ros_meta_input = {
            'symbolic_input': {
                'concept': 'ros_system_optimization',
                'truth_value': {'strength': 0.91, 'confidence': 0.87}
            },
            'neural_input': np.random.randn(256),
        }
        
        ros_meta_result = self.api_server.neural_symbolic.synthesize(
            ros_meta_input['symbolic_input'],
            ros_meta_input['neural_input'],
            'attention_allocation'
        )
        platform_results.append(ros_meta_result)
        
        # Web meta-analysis
        web_meta_input = {
            'symbolic_input': {
                'concept': 'web_interaction_optimization',
                'truth_value': {'strength': 0.96, 'confidence': 0.92}
            },
            'neural_input': np.random.randn(128),
        }
        
        web_meta_result = self.api_server.neural_symbolic.synthesize(
            web_meta_input['symbolic_input'],
            web_meta_input['neural_input'],
            'logical_inference'
        )
        platform_results.append(web_meta_result)
        
        # Meta-cognitive synthesis combining all platforms
        # Normalize all results to 1D for concatenation
        normalized_results = []
        for result in platform_results:
            if len(result.shape) > 1:
                # Flatten multi-dimensional results
                normalized_results.append(result.flatten())
            else:
                normalized_results.append(result)
        
        # Ensure all results have same length for concatenation
        min_length = min(len(result) for result in normalized_results)
        combined_input = np.concatenate([result[:min_length] for result in normalized_results])
        
        meta_cognitive_input = {
            'symbolic_input': {
                'concept': 'meta_cognitive_synthesis',
                'truth_value': {'strength': 0.98, 'confidence': 0.95},
                'context': 'all_platforms_analysis'
            },
            'neural_input': combined_input,
        }
        
        meta_result = self.api_server.neural_symbolic.synthesize(
            meta_cognitive_input['symbolic_input'],
            meta_cognitive_input['neural_input'],
            'conceptual_embedding'
        )
        
        # Validate meta-cognitive results
        self.assertEqual(len(platform_results), 3)
        for result in platform_results:
            self.assertIsInstance(result, np.ndarray)
            self.assertGreater(len(result), 0)
        
        self.assertIsInstance(meta_result, np.ndarray)
        self.assertGreater(len(meta_result), 0)
        
        print(f"  ✓ Platform results: Unity({unity_meta_result.shape}), ROS({ros_meta_result.shape}), Web({web_meta_result.shape})")
        print(f"  ✓ Meta-cognitive synthesis: {meta_result.shape}")
        print("✅ Level 3 Meta-Cognitive Recursion: All platforms integrated successfully")
    
    def test_distributed_task_orchestration(self):
        """Test distributed task orchestration across embodiment platforms"""
        print("\n🎼 Testing Distributed Task Orchestration")
        
        # Create distributed cognitive tasks
        tasks = []
        
        # Task 1: Multi-platform navigation task
        nav_task = CognitiveTask(
            task_id="distributed_navigation_001",
            task_type="multi_platform_navigation",
            input_data={
                'environment_data': {'obstacles': [[1, 2], [3, 4]], 'target': [5, 6]},
                'robot_state': {'position': [0, 0], 'orientation': 0.0},
                'user_preferences': {'speed': 'moderate', 'safety': 'high'}
            },
            metadata={'priority': 'high', 'platforms': ['unity3d', 'ros', 'web']}
        )
        tasks.append(nav_task)
        
        # Task 2: Sensor fusion task
        fusion_task = CognitiveTask(
            task_id="sensor_fusion_002",
            task_type="multi_modal_fusion",
            input_data={
                'visual_data': np.random.randn(224, 224, 3).tolist(),
                'audio_data': np.random.randn(1000).tolist(),
                'lidar_data': np.random.randn(360).tolist()
            },
            metadata={'priority': 'medium', 'platforms': ['unity3d', 'ros']}
        )
        tasks.append(fusion_task)
        
        # Execute tasks through API server
        execution_results = []
        
        for task in tasks:
            # Simulate task execution
            result = self.api_server._execute_synthesis_task(task)
            execution_results.append(result)
        
        # Validate task execution
        self.assertEqual(len(execution_results), 2)
        
        for result in execution_results:
            self.assertIn('synthesis_result', result)
            self.assertIn('execution_time', result)
            self.assertIsInstance(result['synthesis_result'], list)
            self.assertGreater(len(result['synthesis_result']), 0)
            self.assertLess(result['execution_time'], 2.0)
        
        print(f"  ✓ Executed {len(tasks)} distributed tasks successfully")
        print(f"  ✓ Average execution time: {sum(r['execution_time'] for r in execution_results) / len(execution_results):.3f}s")
        print("✅ Distributed Task Orchestration: All tasks completed successfully")
    
    def test_real_time_state_propagation(self):
        """Test real-time state propagation across embodiment interfaces"""
        print("\n⚡ Testing Real-Time State Propagation")
        
        # Simulate state updates from different embodiment sources
        state_updates = [
            {
                'source': 'unity3d',
                'update': {
                    'global_attention': {
                        'focus_target': 'moving_obstacle',
                        'intensity': 0.95,
                        'timestamp': time.time()
                    }
                }
            },
            {
                'source': 'ros',
                'update': {
                    'distributed_memory': {
                        'sensor_reading': 'proximity_alert',
                        'confidence': 0.88,
                        'location': [2.5, 1.8]
                    }
                }
            },
            {
                'source': 'web',
                'update': {
                    'active_computations': {
                        'user_command': 'emergency_stop',
                        'priority': 'critical',
                        'timestamp': time.time()
                    }
                }
            }
        ]
        
        propagation_results = []
        
        for update in state_updates:
            start_time = time.time()
            
            # Propagate state update through API server
            result = self.api_server._propagate_cognitive_state(
                update['update'],
                ['platform_1', 'platform_2', 'platform_3']
            )
            
            propagation_time = time.time() - start_time
            
            propagation_results.append({
                'source': update['source'],
                'propagation_time': propagation_time,
                'target_count': len(result),
                'success_rate': sum(1 for r in result.values() if r['status'] == 'success') / len(result)
            })
        
        # Validate propagation performance
        self.assertEqual(len(propagation_results), 3)
        
        for result in propagation_results:
            self.assertGreater(result['target_count'], 0)
            self.assertGreaterEqual(result['success_rate'], 1.0)  # All should succeed
            self.assertLess(result['propagation_time'], 0.1)     # Should be fast
        
        avg_propagation_time = sum(r['propagation_time'] for r in propagation_results) / len(propagation_results)
        
        print(f"  ✓ Propagated {len(state_updates)} state updates")
        print(f"  ✓ Average propagation time: {avg_propagation_time:.4f}s")
        print(f"  ✓ Total targets reached: {sum(r['target_count'] for r in propagation_results)}")
        print("✅ Real-Time State Propagation: All updates propagated successfully")
    
    def test_end_to_end_embodiment_scenario(self):
        """Test complete end-to-end embodiment scenario"""
        print("\n🎯 Testing End-to-End Embodiment Scenario")
        print("Scenario: Collaborative Robot Task with Multi-Platform Coordination")
        
        scenario_start = time.time()
        
        # Phase 1: Web Agent - Task Planning
        print("  Phase 1: Web Agent - Task Planning")
        web_planning = {
            'symbolic_input': {
                'concept': 'collaborative_task_planning',
                'truth_value': {'strength': 0.95, 'confidence': 0.92}
            },
            'neural_input': np.random.randn(256),
        }
        
        plan_result = self.api_server.neural_symbolic.synthesize(
            web_planning['symbolic_input'],
            web_planning['neural_input'],
            'logical_inference'
        )
        
        # Phase 2: Unity3D Agent - Environment Simulation
        print("  Phase 2: Unity3D Agent - Environment Simulation")
        unity_simulation = {
            'symbolic_input': {
                'concept': 'environment_simulation',
                'truth_value': {'strength': 0.90, 'confidence': 0.88},
                'context': 'task_planning_data'
            },
            'neural_input': plan_result,  # Use planning result
        }
        
        sim_result = self.api_server.neural_symbolic.synthesize(
            unity_simulation['symbolic_input'],
            unity_simulation['neural_input'],
            'conceptual_embedding'
        )
        
        # Phase 3: ROS Agent - Robot Execution
        print("  Phase 3: ROS Agent - Robot Execution")
        ros_execution = {
            'symbolic_input': {
                'concept': 'robot_task_execution',
                'truth_value': {'strength': 0.88, 'confidence': 0.94},
                'context': 'simulation_data'
            },
            'neural_input': sim_result,  # Use simulation result
        }
        
        exec_result = self.api_server.neural_symbolic.synthesize(
            ros_execution['symbolic_input'],
            ros_execution['neural_input'],
            'attention_allocation'
        )
        
        # Phase 4: Web Agent - Monitoring and Feedback
        print("  Phase 4: Web Agent - Monitoring and Feedback")
        web_monitoring = {
            'symbolic_input': {
                'concept': 'task_monitoring_feedback',
                'truth_value': {'strength': 0.92, 'confidence': 0.89},
                'context': 'execution_data'
            },
            'neural_input': exec_result,  # Use execution result
        }
        
        monitor_result = self.api_server.neural_symbolic.synthesize(
            web_monitoring['symbolic_input'],
            web_monitoring['neural_input'],
            'logical_inference'
        )
        
        scenario_end = time.time()
        total_time = scenario_end - scenario_start
        
        # Validate end-to-end scenario
        results = [plan_result, sim_result, exec_result, monitor_result]
        
        for i, result in enumerate(results, 1):
            self.assertIsInstance(result, np.ndarray)
            self.assertGreater(len(result), 0)
            print(f"    ✓ Phase {i} result: {result.shape}")
        
        self.assertLess(total_time, 5.0)  # Should complete in reasonable time
        
        print(f"  ✓ End-to-end scenario completed in {total_time:.3f}s")
        print(f"  ✓ Data flow: Web→Unity3D→ROS→Web (4 phases)")
        print("✅ End-to-End Embodiment Scenario: Successfully completed")


def run_phase4_simplified_integration_test():
    """Run the simplified Phase 4 integration test"""
    print("🧠 Phase 4: Distributed Cognitive Mesh API & Embodiment Layer")
    print("🔬 Simplified Full-Stack Integration Test")
    print("=" * 80)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run the test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(Phase4SimplifiedIntegrationTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate test report
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 80)
    print("📋 PHASE 4 SIMPLIFIED INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    test_report = {
        "test_type": "simplified_integration",
        "phase": "4",
        "timestamp": time.time(),
        "test_results": {
            "total_tests": total_tests,
            "passed": total_tests - failures - errors,
            "failed": failures,
            "errors": errors,
            "success_rate": success_rate
        },
        "test_categories": [
            "embodiment_recursion_level_1",
            "embodiment_recursion_level_2", 
            "embodiment_recursion_level_3",
            "distributed_task_orchestration",
            "real_time_state_propagation",
            "end_to_end_embodiment_scenario"
        ],
        "key_validations": {
            "recursive_embodiment_interface": "3-level recursion tested",
            "cross_platform_coordination": "Unity3D + ROS + Web integration",
            "distributed_processing": "Task orchestration validated",
            "real_time_performance": "Sub-100ms state propagation",
            "end_to_end_flow": "Complete scenario workflow"
        }
    }
    
    print("Test Results Summary:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {total_tests - failures - errors}")
    print(f"  Failed: {failures}")
    print(f"  Errors: {errors}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100.0:
        print(f"\n🎉 ALL SIMPLIFIED INTEGRATION TESTS PASSED!")
        print("Phase 4 embodiment interface recursion core functionality verified")
    else:
        print(f"\n⚠️  Some tests failed or had errors")
        
    # Save test report
    with open('phase4_simplified_integration_report.json', 'w') as f:
        json.dump(test_report, f, indent=2)
    
    print(f"\n📄 Simplified integration test report saved to: phase4_simplified_integration_report.json")
    
    return success_rate == 100.0


if __name__ == "__main__":
    success = run_phase4_simplified_integration_test()
    exit(0 if success else 1)