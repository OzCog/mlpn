#!/usr/bin/env python3
"""
Phase 2 Demo: ECAN Attention Allocation & Dynamic Mesh Integration

Comprehensive demonstration of Phase 2 capabilities including:
- Dynamic mesh topology with distributed agents
- ECAN-style attention allocation across the mesh
- Resource kernel construction and allocation
- Real-time benchmarking and performance monitoring
- Mesh topology visualization and state propagation
"""

import sys
import os
import time
import numpy as np
import json
from typing import Dict, List, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive.mesh_topology import DynamicMesh, DistributedAgent, AgentRole, MeshTopology
from cognitive.resource_kernel import ResourceKernel, DistributedResourceManager, ResourceType, AllocationStrategy
from cognitive.attention_allocation import ECANAttention, AttentionType
from cognitive.benchmarking import DistributedCognitiveBenchmark, BenchmarkConfig, BenchmarkType


class Phase2Demo:
    """Comprehensive Phase 2 demonstration"""
    
    def __init__(self):
        self.mesh = None
        self.resource_manager = None
        self.attention_systems = {}
        self.benchmark = None
        
    def print_section_header(self, title: str):
        """Print formatted section header"""
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)
        
    def print_subsection(self, title: str):
        """Print formatted subsection"""
        print(f"\n--- {title} ---")
        
    def demo_dynamic_mesh_creation(self):
        """Demonstrate dynamic mesh creation with different topologies"""
        self.print_section_header("DYNAMIC MESH TOPOLOGY CREATION")
        
        print("Creating distributed cognitive agents with various roles...")
        
        # Test different topologies
        topologies = [
            (MeshTopology.RING, "Ring Topology"),
            (MeshTopology.FULLY_CONNECTED, "Fully Connected Topology"),
            (MeshTopology.ADAPTIVE, "Adaptive Topology")
        ]
        
        for topology_type, topology_name in topologies:
            self.print_subsection(f"Creating {topology_name}")
            
            mesh = DynamicMesh(topology_type=topology_type)
            
            # Create agents with different roles
            agent_configs = [
                (AgentRole.COORDINATOR, "Central coordination and mesh management"),
                (AgentRole.ATTENTION, "Attention allocation and focus management"),
                (AgentRole.PROCESSOR, "Cognitive processing and computation"),
                (AgentRole.MEMORY, "Distributed memory and knowledge storage"),
                (AgentRole.INFERENCE, "Probabilistic logic and reasoning"),
                (AgentRole.PROCESSOR, "Additional processing capacity")
            ]
            
            created_agents = []
            
            for i, (role, description) in enumerate(agent_configs):
                agent_id = f"{topology_type.value}_agent_{i:02d}"
                agent = DistributedAgent(agent_id=agent_id, role=role)
                
                success = mesh.add_agent(agent)
                if success:
                    created_agents.append(agent)
                    print(f"  ✓ Created {role.value} agent: {agent_id}")
                    print(f"    Description: {description}")
                    print(f"    Processing capacity: {agent.state.processing_capacity}")
                else:
                    print(f"  ❌ Failed to create agent: {agent_id}")
                    
            # Display mesh statistics
            stats = mesh.get_mesh_topology_stats()
            print(f"\nMesh Statistics for {topology_name}:")
            print(f"  Total agents: {stats['total_agents']}")
            print(f"  Total connections: {stats['total_connections']}")
            print(f"  Average connections per agent: {stats['avg_connections_per_agent']:.2f}")
            print(f"  Topology density: {stats['topology_density']:.3f}")
            print(f"  Mesh efficiency: {stats['mesh_efficiency']:.3f}")
            
            # Demonstrate state propagation
            print(f"\nTesting state propagation in {topology_name}...")
            test_state = {
                "message": f"State propagation test from {topology_name}",
                "timestamp": time.time(),
                "data": {
                    "attention_focus": ["concept_a", "concept_b", "concept_c"],
                    "processing_load": np.random.uniform(0.3, 0.8),
                    "priority": "high"
                }
            }
            
            if created_agents:
                source_agent = created_agents[0]
                propagated_count = mesh.propagate_state(source_agent.state.agent_id, test_state)
                print(f"  ✓ State propagated to {propagated_count} agents")
                
                # Display topology visualization data
                viz_data = mesh.visualize_topology()
                print(f"  Topology visualization: {len(viz_data['nodes'])} nodes, {len(viz_data['edges'])} edges")
                
        # Set up the adaptive mesh for the rest of the demo
        self.mesh = DynamicMesh(topology_type=MeshTopology.ADAPTIVE)
        
        # Create the final agent configuration for remaining demos
        print("\nSetting up main demonstration mesh (Adaptive Topology)...")
        
        main_agents = [
            ("coord_01", AgentRole.COORDINATOR),
            ("attn_01", AgentRole.ATTENTION),
            ("attn_02", AgentRole.ATTENTION),
            ("proc_01", AgentRole.PROCESSOR),
            ("proc_02", AgentRole.PROCESSOR),
            ("mem_01", AgentRole.MEMORY),
            ("inf_01", AgentRole.INFERENCE)
        ]
        
        for agent_id, role in main_agents:
            agent = DistributedAgent(agent_id=agent_id, role=role)
            self.mesh.add_agent(agent)
            print(f"  ✓ Added {role.value} agent: {agent_id}")
            
        final_stats = self.mesh.get_mesh_topology_stats()
        print(f"\nFinal mesh: {final_stats['total_agents']} agents, {final_stats['total_connections']} connections")
        
    def demo_resource_kernel_construction(self):
        """Demonstrate resource kernel construction and allocation"""
        self.print_section_header("RESOURCE KERNEL CONSTRUCTION & ALLOCATION")
        
        if not self.mesh:
            print("❌ Mesh not initialized. Run mesh creation demo first.")
            return
            
        print("Creating distributed resource management system...")
        
        # Create distributed resource manager
        self.resource_manager = DistributedResourceManager()
        
        # Create resource kernels for each agent
        strategies = list(AllocationStrategy)
        
        for i, (agent_id, agent) in enumerate(self.mesh.agents.items()):
            # Vary allocation strategies across agents
            strategy = strategies[i % len(strategies)]
            
            # Create resource kernel with role-specific capacity
            kernel = ResourceKernel(agent_id=agent_id, strategy=strategy)
            
            # Adjust resource pools based on agent role
            if agent.state.role == AgentRole.PROCESSOR:
                # Processors have more compute resources
                kernel.resource_pools[ResourceType.COMPUTE].total_capacity = 200.0
                kernel.resource_pools[ResourceType.COMPUTE].available_capacity = 200.0
            elif agent.state.role == AgentRole.MEMORY:
                # Memory agents have more memory and storage
                kernel.resource_pools[ResourceType.MEMORY].total_capacity = 2000.0
                kernel.resource_pools[ResourceType.MEMORY].available_capacity = 2000.0
                kernel.resource_pools[ResourceType.STORAGE].total_capacity = 10000.0
                kernel.resource_pools[ResourceType.STORAGE].available_capacity = 10000.0
            elif agent.state.role == AgentRole.ATTENTION:
                # Attention agents have more attention resources
                kernel.resource_pools[ResourceType.ATTENTION].total_capacity = 20.0
                kernel.resource_pools[ResourceType.ATTENTION].available_capacity = 20.0
                
            # Register with resource manager
            self.resource_manager.register_resource_kernel(agent_id, kernel)
            
            print(f"  ✓ Created {strategy.value} resource kernel for {agent.state.role.value} agent: {agent_id}")
            
        # Display global resource statistics
        global_stats = self.resource_manager.get_global_resource_stats()
        print(f"\nGlobal Resource Pool Summary:")
        print(f"  Total agents: {global_stats['total_agents']}")
        
        for resource_type, stats in global_stats['resource_types'].items():
            print(f"  {resource_type.upper()}:")
            print(f"    Total capacity: {stats['total_capacity']:.1f}")
            print(f"    Available: {stats['total_available']:.1f}")
            print(f"    Global utilization: {stats['global_utilization']:.1%}")
            
        # Demonstrate distributed resource requests
        self.print_subsection("Distributed Resource Allocation")
        
        print("Submitting distributed resource requests...")
        
        # Generate realistic resource requests
        request_scenarios = [
            (ResourceType.COMPUTE, 50.0, 8, "High-priority cognitive processing"),
            (ResourceType.MEMORY, 200.0, 6, "Knowledge graph storage"),
            (ResourceType.ATTENTION, 5.0, 9, "Critical attention focus"),
            (ResourceType.STORAGE, 1000.0, 4, "Long-term memory persistence"),
            (ResourceType.BANDWIDTH, 25.0, 7, "Mesh communication"),
            (ResourceType.COMPUTE, 75.0, 5, "Background inference"),
            (ResourceType.MEMORY, 150.0, 3, "Working memory"),
            (ResourceType.ATTENTION, 3.0, 8, "Selective attention")
        ]
        
        successful_allocations = 0
        total_requests = len(request_scenarios)
        
        for i, (resource_type, amount, priority, description) in enumerate(request_scenarios):
            # Select random requester
            requester_id = np.random.choice(list(self.mesh.agents.keys()))
            
            print(f"\nRequest {i+1}: {description}")
            print(f"  Resource: {resource_type.value}")
            print(f"  Amount: {amount}")
            print(f"  Priority: {priority}/10")
            print(f"  Requester: {requester_id}")
            
            # Find best provider
            provider_id = self.resource_manager.find_best_provider(resource_type, amount)
            
            if provider_id:
                print(f"  Best provider: {provider_id}")
                
                # Make the request
                allocation_id = self.resource_manager.distributed_resource_request(
                    requester_id=requester_id,
                    resource_type=resource_type,
                    amount=amount,
                    priority=priority
                )
                
                if allocation_id:
                    successful_allocations += 1
                    print(f"  ✓ Successfully allocated: {allocation_id}")
                else:
                    print(f"  ❌ Allocation failed")
            else:
                print(f"  ❌ No suitable provider found")
                
        success_rate = successful_allocations / total_requests
        print(f"\nAllocation Summary:")
        print(f"  Successful allocations: {successful_allocations}/{total_requests}")
        print(f"  Success rate: {success_rate:.1%}")
        
        # Demonstrate resource rebalancing
        self.print_subsection("Resource Rebalancing")
        
        print("Performing resource rebalancing across the mesh...")
        
        rebalance_results = self.resource_manager.rebalance_resources()
        print(f"Rebalancing completed:")
        print(f"  Resource moves: {rebalance_results['moves']}")
        print(f"  Total amount moved: {rebalance_results['total_amount_moved']:.2f}")
        print(f"  Duration: {rebalance_results['duration']:.3f} seconds")
        print(f"  Efficiency improvement: {rebalance_results['efficiency_improvement']:.3f}")
        
    def demo_attention_allocation_across_mesh(self):
        """Demonstrate ECAN attention allocation across distributed agents"""
        self.print_section_header("ECAN ATTENTION ALLOCATION ACROSS MESH")
        
        if not self.mesh:
            print("❌ Mesh not initialized. Run mesh creation demo first.")
            return
            
        print("Setting up ECAN attention systems for distributed agents...")
        
        # Create attention systems for each agent
        self.attention_systems = {}
        
        for agent_id, agent in self.mesh.agents.items():
            # Create connections for attention spreading
            connections = {connected_id: list(agent.state.connections) 
                         for connected_id in agent.state.connections}
            
            attention_system = ECANAttention(atomspace_connections=connections)
            self.attention_systems[agent_id] = attention_system
            
            print(f"  ✓ Created ECAN attention system for {agent.state.role.value} agent: {agent_id}")
            print(f"    Connected to: {list(agent.state.connections)}")
            
        # Demonstrate attention allocation scenarios
        self.print_subsection("Cognitive Attention Scenarios")
        
        # Scenario 1: Customer Order Processing
        print("\nScenario 1: Customer Order Processing")
        print("Simulating attention allocation for customer order workflow...")
        
        customer_concepts = ["customer_profile", "order_validation", "inventory_check", 
                           "payment_processing", "shipping_coordination"]
        
        for i, concept in enumerate(customer_concepts):
            # Use attention agents for primary focus
            attention_agents = [agent_id for agent_id, agent in self.mesh.agents.items() 
                              if agent.state.role == AgentRole.ATTENTION]
            
            if attention_agents:
                agent_id = attention_agents[i % len(attention_agents)]
                attention_system = self.attention_systems[agent_id]
                
                # Focus attention with economic allocation
                focus_strength = np.random.uniform(1.5, 3.0)
                attention_system.focus_attention(concept, focus_strength)
                
                print(f"  {agent_id} focusing on '{concept}' (strength: {focus_strength:.2f})")
                
                # Run attention cycle to propagate
                attention_system.run_attention_cycle([concept])
                
        # Scenario 2: Problem Solving Task
        print("\nScenario 2: Complex Problem Solving")
        print("Simulating attention allocation for complex reasoning task...")
        
        problem_concepts = ["problem_analysis", "solution_generation", "constraint_checking",
                          "resource_optimization", "validation_testing"]
        
        # Use different attention allocation strategies
        for concept in problem_concepts:
            # Select random attention agent
            attention_agents = [aid for aid, a in self.mesh.agents.items() 
                              if a.state.role == AgentRole.ATTENTION]
            
            if attention_agents:
                agent_id = np.random.choice(attention_agents)
                attention_system = self.attention_systems[agent_id]
                
                # Allocate different types of attention
                attention_types = [AttentionType.STI, AttentionType.LTI, AttentionType.VLTI]
                attention_type = np.random.choice(attention_types)
                value = np.random.uniform(0.8, 2.5)
                
                attention_system.attention_bank.allocate_attention(concept, attention_type, value)
                print(f"  {agent_id} allocated {attention_type.value} to '{concept}' (value: {value:.2f})")
                
        # Display attention allocation statistics
        self.print_subsection("Attention Allocation Statistics")
        
        for agent_id, attention_system in self.attention_systems.items():
            agent_role = self.mesh.agents[agent_id].state.role.value
            
            # Get attention focus
            focus_list = attention_system.get_attention_focus(5)
            
            # Get economic stats
            economic_stats = attention_system.get_economic_stats()
            
            print(f"\n{agent_role.upper()} Agent {agent_id}:")
            print(f"  Top attention focuses:")
            for concept, attention_value in focus_list:
                print(f"    {concept}: {attention_value:.3f}")
                
            print(f"  Economic allocation:")
            print(f"    Total wages: {economic_stats['total_wages']:.2f}")
            print(f"    Total rents: {economic_stats['total_rents']:.2f}")
            print(f"    Wage fund: {economic_stats['wage_fund']:.2f}")
            print(f"    Rent fund: {economic_stats['rent_fund']:.2f}")
            
        # Demonstrate mesh-wide attention benchmarking
        self.print_subsection("Mesh-Wide Attention Benchmarking")
        
        print("Running attention allocation benchmark across the mesh...")
        
        benchmark_results = self.mesh.benchmark_attention_allocation(iterations=50)
        
        print(f"Benchmark Results:")
        print(f"  Total time: {benchmark_results['total_time']:.3f} seconds")
        print(f"  Iterations: {benchmark_results['iterations']}")
        print(f"  Total messages: {benchmark_results['total_messages']}")
        print(f"  Successful allocations: {benchmark_results['successful_allocations']}")
        print(f"  Average propagation time: {benchmark_results['avg_propagation_time']:.4f} seconds")
        print(f"  Messages per second: {benchmark_results['messages_per_second']:.2f}")
        print(f"  Attention agents: {benchmark_results['attention_agents']}")
        print(f"  Topology type: {benchmark_results['topology_type']}")
        
    def demo_comprehensive_benchmarking(self):
        """Demonstrate comprehensive benchmarking across the distributed mesh"""
        self.print_section_header("COMPREHENSIVE PERFORMANCE BENCHMARKING")
        
        if not self.mesh or not self.resource_manager or not self.attention_systems:
            print("❌ System not fully initialized. Run previous demos first.")
            return
            
        print("Setting up comprehensive benchmarking suite...")
        
        # Create benchmark system
        self.benchmark = DistributedCognitiveBenchmark()
        
        # Setup with existing systems (simulating the environment)
        self.benchmark.mesh = self.mesh
        self.benchmark.resource_manager = self.resource_manager
        self.benchmark.attention_systems = self.attention_systems
        
        # Attention Allocation Benchmark
        self.print_subsection("Attention Allocation Performance")
        
        attention_config = BenchmarkConfig(
            benchmark_type=BenchmarkType.ATTENTION_ALLOCATION,
            iterations=20,
            concurrent_requests=5,
            warmup_iterations=3
        )
        
        print("Running attention allocation benchmark...")
        attention_result = self.benchmark.benchmark_attention_allocation(attention_config)
        
        print(f"Attention Benchmark Results:")
        print(f"  Duration: {attention_result.duration:.3f} seconds")
        print(f"  Success rate: {attention_result.success_rate:.1%}")
        print(f"  Average latency: {attention_result.metrics['avg_latency']:.4f} seconds")
        print(f"  Median latency: {attention_result.metrics['median_latency']:.4f} seconds")
        print(f"  95th percentile latency: {attention_result.metrics['p95_latency']:.4f} seconds")
        print(f"  Average throughput: {attention_result.metrics['avg_throughput']:.2f} requests/second")
        print(f"  Requests per second: {attention_result.metrics['requests_per_second']:.2f}")
        print(f"  Mesh efficiency: {attention_result.metrics['mesh_efficiency']:.3f}")
        
        # Resource Allocation Benchmark
        self.print_subsection("Resource Allocation Performance")
        
        resource_config = BenchmarkConfig(
            benchmark_type=BenchmarkType.RESOURCE_ALLOCATION,
            iterations=15,
            concurrent_requests=4,
            warmup_iterations=2
        )
        
        print("Running resource allocation benchmark...")
        resource_result = self.benchmark.benchmark_resource_allocation(resource_config)
        
        print(f"Resource Benchmark Results:")
        print(f"  Duration: {resource_result.duration:.3f} seconds")
        print(f"  Success rate: {resource_result.success_rate:.1%}")
        print(f"  Average allocation latency: {resource_result.metrics['avg_allocation_latency']:.4f} seconds")
        print(f"  95th percentile latency: {resource_result.metrics['p95_allocation_latency']:.4f} seconds")
        print(f"  Allocations per second: {resource_result.metrics['allocations_per_second']:.2f}")
        print(f"  Resource efficiency: {resource_result.metrics['resource_efficiency']:.3f}")
        print(f"  Average utilization: {resource_result.metrics['average_resource_utilization']:.3f}")
        
        # Mesh Communication Benchmark
        self.print_subsection("Mesh Communication Performance")
        
        comm_config = BenchmarkConfig(
            benchmark_type=BenchmarkType.MESH_COMMUNICATION,
            iterations=12,
            concurrent_requests=3,
            warmup_iterations=2
        )
        
        print("Running mesh communication benchmark...")
        comm_result = self.benchmark.benchmark_mesh_communication(comm_config)
        
        print(f"Communication Benchmark Results:")
        print(f"  Duration: {comm_result.duration:.3f} seconds")
        print(f"  Success rate: {comm_result.success_rate:.1%}")
        print(f"  Average communication latency: {comm_result.metrics['avg_communication_latency']:.4f} seconds")
        print(f"  95th percentile latency: {comm_result.metrics['p95_communication_latency']:.4f} seconds")
        print(f"  Messages per second: {comm_result.metrics['messages_per_second']:.2f}")
        print(f"  Average message size: {comm_result.metrics['avg_message_size']:.1f} bytes")
        print(f"  Topology density: {comm_result.metrics['topology_density']:.3f}")
        
        # Generate comprehensive report
        self.print_subsection("Benchmark Summary Report")
        
        all_results = [attention_result, resource_result, comm_result]
        report = self.benchmark.generate_benchmark_report(all_results)
        
        print("\nGenerated comprehensive benchmark report:")
        print(report)
        
    def demo_mesh_topology_documentation(self):
        """Demonstrate mesh topology documentation and state propagation"""
        self.print_section_header("MESH TOPOLOGY DOCUMENTATION & STATE PROPAGATION")
        
        if not self.mesh:
            print("❌ Mesh not initialized. Run mesh creation demo first.")
            return
            
        print("Documenting mesh topology and dynamic state propagation...")
        
        # Generate topology visualization data
        self.print_subsection("Topology Visualization")
        
        viz_data = self.mesh.visualize_topology()
        
        print(f"Mesh Topology Structure:")
        print(f"  Topology type: {viz_data['topology_type']}")
        print(f"  Total nodes: {len(viz_data['nodes'])}")
        print(f"  Total edges: {len(viz_data['edges'])}")
        
        print(f"\nNode Details:")
        for node in viz_data['nodes']:
            print(f"  {node['id']} ({node['role']}):")
            print(f"    Label: {node['label']}")
            print(f"    Load: {node['load']:.2f}")
            print(f"    Capacity: {node['capacity']:.2f}")
            print(f"    Connections: {node['connections']}")
            
        print(f"\nEdge Details:")
        for edge in viz_data['edges']:
            print(f"  {edge['source']} ↔ {edge['target']} (weight: {edge['weight']})")
            
        # Comprehensive topology statistics
        self.print_subsection("Detailed Topology Statistics")
        
        detailed_stats = self.mesh.get_mesh_topology_stats()
        
        print(f"Comprehensive Mesh Statistics:")
        print(f"  Agent Configuration:")
        for role, count in detailed_stats['agent_roles'].items():
            print(f"    {role}: {count} agents")
            
        print(f"  Connectivity Metrics:")
        print(f"    Total connections: {detailed_stats['total_connections']}")
        print(f"    Average connections per agent: {detailed_stats['avg_connections_per_agent']:.2f}")
        print(f"    Topology density: {detailed_stats['topology_density']:.3f}")
        
        print(f"  Performance Metrics:")
        print(f"    Average agent load: {detailed_stats['avg_agent_load']:.3f}")
        print(f"    Total processing capacity: {detailed_stats['total_processing_capacity']:.2f}")
        print(f"    Mesh efficiency: {detailed_stats['mesh_efficiency']:.3f}")
        
        # Demonstrate dynamic state propagation
        self.print_subsection("Dynamic State Propagation")
        
        print("Testing various state propagation scenarios...")
        
        # Scenario 1: Configuration update
        config_state = {
            "type": "configuration_update",
            "changes": {
                "attention_threshold": 0.75,
                "resource_rebalance_interval": 300,
                "mesh_optimization": True
            },
            "timestamp": time.time(),
            "priority": "medium"
        }
        
        coordinator_id = None
        for agent_id, agent in self.mesh.agents.items():
            if agent.state.role == AgentRole.COORDINATOR:
                coordinator_id = agent_id
                break
                
        if coordinator_id:
            print(f"\nPropagating configuration update from coordinator {coordinator_id}...")
            propagated = self.mesh.propagate_state(coordinator_id, config_state)
            print(f"  ✓ Configuration propagated to {propagated} agents")
            
        # Scenario 2: Alert propagation
        alert_state = {
            "type": "system_alert",
            "alert": {
                "level": "high",
                "message": "Resource utilization exceeding 85%",
                "affected_resources": ["compute", "memory"],
                "recommended_action": "initiate_load_balancing"
            },
            "timestamp": time.time(),
            "priority": "high"
        }
        
        # Propagate from random agent
        source_agent_id = np.random.choice(list(self.mesh.agents.keys()))
        print(f"\nPropagating system alert from {source_agent_id}...")
        propagated = self.mesh.propagate_state(source_agent_id, alert_state)
        print(f"  ✓ Alert propagated to {propagated} agents")
        
        # Scenario 3: Knowledge update
        knowledge_state = {
            "type": "knowledge_update",
            "knowledge": {
                "domain": "customer_service",
                "facts": [
                    "Customer satisfaction correlates with response time",
                    "Automated routing improves efficiency by 23%",
                    "Peak hours are 10am-2pm and 7pm-9pm"
                ],
                "confidence": 0.87,
                "source": "learning_module"
            },
            "timestamp": time.time(),
            "priority": "low"
        }
        
        memory_agents = [aid for aid, a in self.mesh.agents.items() 
                        if a.state.role == AgentRole.MEMORY]
        
        if memory_agents:
            memory_agent_id = memory_agents[0]
            print(f"\nPropagating knowledge update from memory agent {memory_agent_id}...")
            propagated = self.mesh.propagate_state(memory_agent_id, knowledge_state)
            print(f"  ✓ Knowledge propagated to {propagated} agents")
            
        # Generate Scheme specifications
        self.print_subsection("Scheme Specifications")
        
        print("Generating Scheme specifications for mesh topology...")
        
        mesh_scheme = self.mesh.scheme_mesh_spec()
        print(f"\nMesh Topology Scheme Specification:")
        print(mesh_scheme)
        
    def run_complete_demo(self):
        """Run the complete Phase 2 demonstration"""
        self.print_section_header("PHASE 2: ECAN ATTENTION ALLOCATION & DYNAMIC MESH INTEGRATION")
        
        print("This demonstration showcases the complete Phase 2 implementation including:")
        print("• Dynamic mesh topology with distributed cognitive agents")
        print("• ECAN-style attention allocation across the mesh")
        print("• Resource kernel construction and distributed allocation")
        print("• Real-time performance benchmarking")
        print("• Mesh topology documentation and state propagation")
        print("• Integration with Phase 1 cognitive primitives")
        
        print("\nStarting comprehensive Phase 2 demonstration...")
        
        start_time = time.time()
        
        try:
            # Run all demonstration modules
            self.demo_dynamic_mesh_creation()
            self.demo_resource_kernel_construction()
            self.demo_attention_allocation_across_mesh()
            self.demo_comprehensive_benchmarking()
            self.demo_mesh_topology_documentation()
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            self.print_section_header("PHASE 2 DEMONSTRATION COMPLETED")
            
            print(f"✓ All Phase 2 components successfully demonstrated!")
            print(f"✓ Total demonstration time: {total_duration:.2f} seconds")
            print(f"✓ Dynamic mesh integration: OPERATIONAL")
            print(f"✓ ECAN attention allocation: OPERATIONAL")
            print(f"✓ Resource kernel construction: OPERATIONAL")
            print(f"✓ Distributed benchmarking: OPERATIONAL")
            print(f"✓ State propagation: OPERATIONAL")
            
            # Final system summary
            if self.mesh and self.resource_manager and self.attention_systems:
                print(f"\nFinal System Configuration:")
                print(f"  Mesh agents: {len(self.mesh.agents)}")
                print(f"  Resource kernels: {len(self.resource_manager.resource_kernels)}")
                print(f"  Attention systems: {len(self.attention_systems)}")
                
                mesh_stats = self.mesh.get_mesh_topology_stats()
                resource_stats = self.resource_manager.get_global_resource_stats()
                
                print(f"  Mesh efficiency: {mesh_stats['mesh_efficiency']:.3f}")
                print(f"  Total processing capacity: {mesh_stats['total_processing_capacity']:.2f}")
                print(f"  Resource agents: {resource_stats['total_agents']}")
                
            print(f"\n🎉 Phase 2: ECAN Attention Allocation & Dynamic Mesh Integration is complete!")
            print(f"Ready for Phase 3: Neural-Symbolic Synthesis via Custom ggml Kernels")
            
        except Exception as e:
            print(f"\n❌ Demonstration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Cleanup
            if self.benchmark:
                self.benchmark.teardown_test_environment()


def main():
    """Run the Phase 2 demonstration"""
    demo = Phase2Demo()
    demo.run_complete_demo()


if __name__ == "__main__":
    main()