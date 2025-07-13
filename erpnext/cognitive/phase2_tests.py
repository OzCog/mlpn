#!/usr/bin/env python3
"""
Phase 2 Tests: ECAN Attention Allocation & Dynamic Mesh Integration

Comprehensive test suite for Phase 2 implementation including:
- Dynamic mesh topology management
- Distributed resource allocation
- Attention allocation benchmarking
- Mesh communication performance
- Integration validation
"""

import sys
import os
import time
import numpy as np
from typing import Dict, List, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive.mesh_topology import DynamicMesh, DistributedAgent, AgentRole, MeshTopology
from cognitive.resource_kernel import ResourceKernel, DistributedResourceManager, ResourceType
from cognitive.attention_allocation import ECANAttention
from cognitive.benchmarking import DistributedCognitiveBenchmark, BenchmarkConfig, BenchmarkType


class Phase2Tests:
    """Comprehensive test suite for Phase 2 implementation"""
    
    def __init__(self):
        self.test_results = {}
        
    def test_dynamic_mesh_creation(self) -> bool:
        """Test dynamic mesh creation and agent management"""
        print("Testing Dynamic Mesh Creation...")
        
        try:
            # Test different mesh topologies
            topologies = [MeshTopology.RING, MeshTopology.FULLY_CONNECTED, MeshTopology.ADAPTIVE]
            
            for topology in topologies:
                mesh = DynamicMesh(topology_type=topology)
                
                # Create agents with different roles
                agents = []
                roles = list(AgentRole)
                
                for i in range(6):  # Create 6 agents
                    role = roles[i % len(roles)]
                    agent = DistributedAgent(agent_id=f"test_agent_{i}", role=role)
                    agents.append(agent)
                    
                    # Add agent to mesh
                    success = mesh.add_agent(agent)
                    assert success, f"Failed to add agent {agent.state.agent_id}"
                    
                # Verify topology was built
                stats = mesh.get_mesh_topology_stats()
                assert stats["total_agents"] == 6, f"Expected 6 agents, got {stats['total_agents']}"
                assert stats["total_connections"] > 0, "No connections in mesh"
                
                # Test state propagation
                test_state = {"test_data": "propagation_test", "timestamp": time.time()}
                propagated_count = mesh.propagate_state(agents[0].state.agent_id, test_state)
                assert propagated_count >= 0, "State propagation failed"
                
                # Test agent removal
                remove_success = mesh.remove_agent(agents[0].state.agent_id)
                assert remove_success, "Failed to remove agent"
                
                updated_stats = mesh.get_mesh_topology_stats()
                assert updated_stats["total_agents"] == 5, "Agent removal failed"
                
            print("✓ Dynamic Mesh Creation tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Dynamic Mesh Creation tests failed: {str(e)}")
            return False
            
    def test_resource_kernel_allocation(self) -> bool:
        """Test resource kernel allocation and management"""
        print("Testing Resource Kernel Allocation...")
        
        try:
            # Create resource kernel
            kernel = ResourceKernel(agent_id="test_agent", strategy="load_balanced")
            
            # Test resource requests
            resource_types = list(ResourceType)
            request_ids = []
            
            for resource_type in resource_types:
                request_id = kernel.request_resource(
                    resource_type=resource_type,
                    amount=10.0,
                    priority=5,
                    requester_id="test_requester"
                )
                assert request_id, f"Failed to create request for {resource_type.value}"
                request_ids.append(request_id)
                
            # Test resource processing
            processed_count = kernel.process_pending_requests()
            assert processed_count >= 0, "Failed to process requests"
            
            # Test resource utilization
            utilization = kernel.get_resource_utilization()
            assert len(utilization) == len(resource_types), "Utilization data incomplete"
            
            for resource_type_str, stats in utilization.items():
                assert "total_capacity" in stats, f"Missing capacity for {resource_type_str}"
                assert "utilization_rate" in stats, f"Missing utilization for {resource_type_str}"
                assert stats["utilization_rate"] >= 0, f"Invalid utilization for {resource_type_str}"
                
            # Test performance metrics
            metrics = kernel.get_performance_metrics()
            assert "active_allocations" in metrics, "Missing active allocations metric"
            assert "allocation_success_rate" in metrics, "Missing success rate metric"
            
            # Test cleanup
            cleanup_count = kernel.cleanup_expired_allocations()
            assert cleanup_count >= 0, "Cleanup failed"
            
            print("✓ Resource Kernel Allocation tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Resource Kernel Allocation tests failed: {str(e)}")
            return False
            
    def test_distributed_resource_management(self) -> bool:
        """Test distributed resource management across multiple agents"""
        print("Testing Distributed Resource Management...")
        
        try:
            # Create distributed resource manager
            resource_manager = DistributedResourceManager()
            
            # Create multiple resource kernels
            num_agents = 5
            kernels = {}
            
            for i in range(num_agents):
                agent_id = f"agent_{i}"
                kernel = ResourceKernel(agent_id=agent_id)
                kernels[agent_id] = kernel
                resource_manager.register_resource_kernel(agent_id, kernel)
                
            # Test global resource view
            global_stats = resource_manager.get_global_resource_stats()
            assert global_stats["total_agents"] == num_agents, "Incorrect agent count"
            assert "resource_types" in global_stats, "Missing resource types"
            
            # Test distributed resource requests
            successful_requests = 0
            total_requests = 20
            
            for i in range(total_requests):
                resource_type = np.random.choice(list(ResourceType))
                requester_id = f"agent_{i % num_agents}"
                amount = np.random.uniform(1.0, 20.0)
                
                allocation_id = resource_manager.distributed_resource_request(
                    requester_id=requester_id,
                    resource_type=resource_type,
                    amount=amount,
                    priority=np.random.randint(1, 6)
                )
                
                if allocation_id:
                    successful_requests += 1
                    
            success_rate = successful_requests / total_requests
            assert success_rate > 0, "No successful resource allocations"
            print(f"  Resource allocation success rate: {success_rate:.2%}")
            
            # Test resource rebalancing
            rebalance_results = resource_manager.rebalance_resources()
            assert "moves" in rebalance_results, "Missing rebalance moves"
            assert "efficiency_improvement" in rebalance_results, "Missing efficiency metric"
            
            # Test best provider finding
            for resource_type in ResourceType:
                provider = resource_manager.find_best_provider(resource_type, 5.0)
                # Provider may be None if no capacity available, which is valid
                
            print("✓ Distributed Resource Management tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Distributed Resource Management tests failed: {str(e)}")
            return False
            
    def test_attention_allocation_benchmarking(self) -> bool:
        """Test attention allocation benchmarking functionality"""
        print("Testing Attention Allocation Benchmarking...")
        
        try:
            # Setup benchmark environment
            benchmark = DistributedCognitiveBenchmark()
            success = benchmark.setup_test_environment(num_agents=8, topology=MeshTopology.ADAPTIVE)
            assert success, "Failed to setup benchmark environment"
            
            # Test attention allocation benchmark
            config = BenchmarkConfig(
                benchmark_type=BenchmarkType.ATTENTION_ALLOCATION,
                iterations=10,
                concurrent_requests=3,
                warmup_iterations=2
            )
            
            result = benchmark.benchmark_attention_allocation(config)
            
            assert result.benchmark_type == BenchmarkType.ATTENTION_ALLOCATION, "Wrong benchmark type"
            assert result.iterations == config.iterations, "Iteration mismatch"
            assert result.duration > 0, "Invalid duration"
            assert "avg_latency" in result.metrics, "Missing latency metric"
            assert "requests_per_second" in result.metrics, "Missing throughput metric"
            assert "attention_agents" in result.metrics, "Missing agent count"
            
            # Validate performance metrics
            assert result.metrics["avg_latency"] >= 0, "Invalid latency"
            assert result.metrics["requests_per_second"] >= 0, "Invalid throughput"
            
            # Test mesh-specific benchmark
            mesh_benchmark_results = benchmark.mesh.benchmark_attention_allocation(50)
            assert "total_time" in mesh_benchmark_results, "Missing total time"
            assert "successful_allocations" in mesh_benchmark_results, "Missing success count"
            assert "messages_per_second" in mesh_benchmark_results, "Missing message rate"
            
            benchmark.teardown_test_environment()
            
            print("✓ Attention Allocation Benchmarking tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Attention Allocation Benchmarking tests failed: {str(e)}")
            return False
            
    def test_mesh_communication_performance(self) -> bool:
        """Test mesh communication performance"""
        print("Testing Mesh Communication Performance...")
        
        try:
            # Setup benchmark environment
            benchmark = DistributedCognitiveBenchmark()
            success = benchmark.setup_test_environment(num_agents=6, topology=MeshTopology.FULLY_CONNECTED)
            assert success, "Failed to setup benchmark environment"
            
            # Test communication benchmark
            config = BenchmarkConfig(
                benchmark_type=BenchmarkType.MESH_COMMUNICATION,
                iterations=8,
                concurrent_requests=2,
                warmup_iterations=1
            )
            
            result = benchmark.benchmark_mesh_communication(config)
            
            assert result.benchmark_type == BenchmarkType.MESH_COMMUNICATION, "Wrong benchmark type"
            assert result.duration > 0, "Invalid duration"
            assert "avg_communication_latency" in result.metrics, "Missing communication latency"
            assert "messages_per_second" in result.metrics, "Missing message throughput"
            assert "topology_density" in result.metrics, "Missing topology density"
            
            # Validate mesh topology stats
            topology_stats = benchmark.mesh.get_mesh_topology_stats()
            assert topology_stats["total_agents"] == 6, "Incorrect agent count"
            assert topology_stats["topology_type"] == MeshTopology.FULLY_CONNECTED.value, "Wrong topology"
            
            # Test topology visualization
            viz_data = benchmark.mesh.visualize_topology()
            assert "nodes" in viz_data, "Missing visualization nodes"
            assert "edges" in viz_data, "Missing visualization edges"
            assert len(viz_data["nodes"]) == 6, "Incorrect node count"
            
            benchmark.teardown_test_environment()
            
            print("✓ Mesh Communication Performance tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Mesh Communication Performance tests failed: {str(e)}")
            return False
            
    def test_comprehensive_benchmarking(self) -> bool:
        """Test comprehensive benchmarking across multiple configurations"""
        print("Testing Comprehensive Benchmarking...")
        
        try:
            benchmark = DistributedCognitiveBenchmark()
            
            # Run smaller scale comprehensive benchmark for testing
            results = benchmark.run_comprehensive_benchmark(
                agent_counts=[4, 6],
                topologies=[MeshTopology.RING, MeshTopology.ADAPTIVE]
            )
            
            assert "start_time" in results, "Missing start time"
            assert "end_time" in results, "Missing end time"
            assert "configurations" in results, "Missing configurations"
            assert "scalability_analysis" in results, "Missing scalability analysis"
            assert "topology_comparison" in results, "Missing topology comparison"
            
            # Validate configurations
            configurations = results["configurations"]
            assert len(configurations) == 4, "Expected 4 configurations (2 counts × 2 topologies)"
            
            for config in configurations:
                assert "agent_count" in config, "Missing agent count"
                assert "topology" in config, "Missing topology"
                assert "attention_benchmark" in config, "Missing attention benchmark"
                assert "resource_benchmark" in config, "Missing resource benchmark"
                assert "communication_benchmark" in config, "Missing communication benchmark"
                
            # Validate scalability analysis
            scalability = results["scalability_analysis"]
            assert isinstance(scalability, dict), "Invalid scalability analysis format"
            
            print("✓ Comprehensive Benchmarking tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Comprehensive Benchmarking tests failed: {str(e)}")
            return False
            
    def test_integration_scenarios(self) -> bool:
        """Test full integration scenarios"""
        print("Testing Integration Scenarios...")
        
        try:
            # Create integrated system
            mesh = DynamicMesh(topology_type=MeshTopology.ADAPTIVE)
            resource_manager = DistributedResourceManager()
            attention_systems = {}
            
            # Create agents with integrated components
            num_agents = 5
            agent_roles = [AgentRole.COORDINATOR, AgentRole.ATTENTION, AgentRole.PROCESSOR, 
                          AgentRole.MEMORY, AgentRole.INFERENCE]
            
            for i in range(num_agents):
                role = agent_roles[i]
                agent_id = f"integrated_agent_{i}"
                
                # Create agent
                agent = DistributedAgent(agent_id=agent_id, role=role)
                
                # Create resource kernel
                resource_kernel = ResourceKernel(agent_id=agent_id)
                
                # Create attention system
                attention_system = ECANAttention()
                
                # Add to systems
                mesh.add_agent(agent)
                resource_manager.register_resource_kernel(agent_id, resource_kernel)
                attention_systems[agent_id] = attention_system
                
            # Test integrated workflow
            print("  Testing integrated attention-resource workflow...")
            
            # 1. Focus attention on concepts
            concepts = ["customer", "order", "product", "payment", "delivery"]
            for i, concept in enumerate(concepts):
                agent_id = f"integrated_agent_{i % num_agents}"
                attention_system = attention_systems[agent_id]
                attention_system.focus_attention(concept, 2.0)
                
            # 2. Allocate resources for processing
            for i in range(10):
                resource_type = np.random.choice(list(ResourceType))
                requester_id = f"integrated_agent_{i % num_agents}"
                amount = np.random.uniform(5.0, 25.0)
                
                allocation_id = resource_manager.distributed_resource_request(
                    requester_id=requester_id,
                    resource_type=resource_type,
                    amount=amount,
                    priority=np.random.randint(1, 8)
                )
                
            # 3. Propagate state across mesh
            test_state = {
                "attention_focus": concepts,
                "processing_load": 0.6,
                "timestamp": time.time()
            }
            
            propagated_count = mesh.propagate_state(
                f"integrated_agent_0", 
                test_state
            )
            assert propagated_count >= 0, "State propagation failed"
            
            # 4. Verify system health
            mesh_stats = mesh.get_mesh_topology_stats()
            resource_stats = resource_manager.get_global_resource_stats()
            
            assert mesh_stats["total_agents"] == num_agents, "Agent count mismatch"
            assert mesh_stats["mesh_efficiency"] >= 0, "Invalid mesh efficiency"
            assert resource_stats["total_agents"] == num_agents, "Resource agent count mismatch"
            
            # 5. Test attention coordination
            coordinator_id = f"integrated_agent_0"  # First agent is coordinator
            coordinator_agent = mesh.agents[coordinator_id]
            
            # Send coordination messages
            for target_id in list(mesh.agents.keys())[1:]:  # All except coordinator
                message_sent = coordinator_agent.send_message(
                    receiver_id=target_id,
                    message_type="attention_coordination",
                    payload={"focus_concepts": concepts, "priority": "high"}
                )
                assert message_sent, f"Failed to send message to {target_id}"
                
            print("✓ Integration Scenarios tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Integration Scenarios tests failed: {str(e)}")
            return False
            
    def test_scheme_specifications(self) -> bool:
        """Test Scheme specification generation"""
        print("Testing Scheme Specifications...")
        
        try:
            # Test mesh Scheme specification
            mesh = DynamicMesh()
            mesh_spec = mesh.scheme_mesh_spec()
            assert isinstance(mesh_spec, str), "Mesh spec should be string"
            assert "mesh-topology-create" in mesh_spec, "Missing mesh creation function"
            assert "mesh-propagate-state" in mesh_spec, "Missing state propagation function"
            assert "mesh-benchmark-attention" in mesh_spec, "Missing benchmark function"
            
            # Test resource kernel Scheme specification
            kernel = ResourceKernel("test_agent")
            resource_spec = kernel.scheme_resource_spec()
            assert isinstance(resource_spec, str), "Resource spec should be string"
            assert "resource-request" in resource_spec, "Missing resource request function"
            assert "resource-allocate" in resource_spec, "Missing allocation function"
            
            # Test distributed resource manager Scheme specification
            manager = DistributedResourceManager()
            manager_spec = manager.scheme_resource_spec()
            assert isinstance(manager_spec, str), "Manager spec should be string"
            assert "distributed-resource-find-provider" in manager_spec, "Missing provider function"
            
            # Test benchmarking Scheme specification
            benchmark = DistributedCognitiveBenchmark()
            benchmark_spec = benchmark.scheme_benchmark_spec()
            assert isinstance(benchmark_spec, str), "Benchmark spec should be string"
            assert "benchmark-setup" in benchmark_spec, "Missing setup function"
            assert "benchmark-attention-allocation" in benchmark_spec, "Missing attention benchmark"
            assert "benchmark-resource-allocation" in benchmark_spec, "Missing resource benchmark"
            
            print("✓ Scheme Specifications tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Scheme Specifications tests failed: {str(e)}")
            return False
            
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all Phase 2 tests"""
        print("=" * 80)
        print("PHASE 2: ECAN ATTENTION ALLOCATION & DYNAMIC MESH INTEGRATION TESTS")
        print("=" * 80)
        
        tests = [
            ("Dynamic Mesh Creation", self.test_dynamic_mesh_creation),
            ("Resource Kernel Allocation", self.test_resource_kernel_allocation),
            ("Distributed Resource Management", self.test_distributed_resource_management),
            ("Attention Allocation Benchmarking", self.test_attention_allocation_benchmarking),
            ("Mesh Communication Performance", self.test_mesh_communication_performance),
            ("Comprehensive Benchmarking", self.test_comprehensive_benchmarking),
            ("Integration Scenarios", self.test_integration_scenarios),
            ("Scheme Specifications", self.test_scheme_specifications)
        ]
        
        results = {}
        passed_count = 0
        
        for test_name, test_func in tests:
            print(f"\nRunning {test_name}...")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed_count += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                results[test_name] = False
                
        print("\n" + "=" * 80)
        print(f"PHASE 2 TEST RESULTS: {passed_count}/{len(tests)} tests passed")
        print("=" * 80)
        
        for test_name, result in results.items():
            status = "✓ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            
        if passed_count == len(tests):
            print("\n🎉 ALL PHASE 2 TESTS PASSED SUCCESSFULLY!")
            print("Phase 2: ECAN Attention Allocation & Dynamic Mesh Integration is complete.")
        else:
            print(f"\n⚠️  {len(tests) - passed_count} tests failed. Review implementation.")
            
        print("=" * 80)
        
        self.test_results = results
        return results


def main():
    """Run Phase 2 tests"""
    phase2_tests = Phase2Tests()
    results = phase2_tests.run_all_tests()
    
    # Return exit code based on test results
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())