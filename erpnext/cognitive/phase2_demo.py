"""
Phase 2 Integration Demo: ECAN Attention Allocation & Resource Kernel Construction

Demonstrates the complete Phase 2 implementation with real-world scenarios,
showing dynamic mesh integration, resource management, and enhanced attention allocation.
"""

import time
import numpy as np
from typing import Dict, List, Any
import json

# Import all Phase 2 components
from resource_kernel import ResourceKernel, AttentionScheduler, ResourceType, ResourcePriority
from attention_allocation import ECANAttention, AttentionType
from cognitive_grammar import CognitiveGrammar


class Phase2IntegratedDemo:
    """Complete demonstration of Phase 2 integrated functionality"""
    
    def __init__(self):
        self.demo_results = {}
        
    def setup_cognitive_infrastructure(self) -> Dict[str, Any]:
        """Setup complete cognitive infrastructure for demo"""
        print("🔧 Setting up Phase 2 Cognitive Infrastructure...")
        
        # Initialize core components
        self.grammar = CognitiveGrammar()
        self.resource_kernel = ResourceKernel("demo_primary_node")
        self.scheduler = AttentionScheduler(self.resource_kernel)
        
        # Create knowledge base scenario
        self.entities = self._create_business_scenario()
        
        # Setup connections for attention spreading
        connections = self._create_attention_network()
        
        # Initialize enhanced ECAN with resource kernel
        self.ecan = ECANAttention(
            atomspace_connections=connections,
            node_id="demo_ecan_primary",
            resource_kernel=self.resource_kernel
        )
        
        # Setup distributed mesh
        self._setup_cognitive_mesh()
        
        infrastructure_stats = {
            "entities_created": len(self.entities),
            "connections_established": len(connections),
            "mesh_nodes_registered": len(self.ecan.mesh_nodes),
            "resource_types_available": len(self.resource_kernel.quotas)
        }
        
        print(f"✅ Infrastructure ready: {infrastructure_stats}")
        return infrastructure_stats
    
    def _create_business_scenario(self) -> Dict[str, str]:
        """Create realistic business scenario entities"""
        scenarios = [
            ("enterprise_customer", "concept"),
            ("premium_product", "concept"), 
            ("large_order", "concept"),
            ("urgent_delivery", "concept"),
            ("payment_processing", "concept"),
            ("inventory_check", "concept"),
            ("quality_assurance", "concept"),
            ("customer_service", "concept"),
            ("supply_chain", "concept"),
            ("financial_reporting", "concept")
        ]
        
        entities = {}
        for name, entity_type in scenarios:
            entity_id = self.grammar.create_entity(name, entity_type)
            entities[name] = entity_id
            
        # Create relationships between entities
        relationships = [
            ("enterprise_customer", "large_order", "places_order"),
            ("large_order", "premium_product", "contains_product"), 
            ("large_order", "urgent_delivery", "requires_delivery"),
            ("large_order", "payment_processing", "needs_payment"),
            ("premium_product", "inventory_check", "requires_inventory"),
            ("premium_product", "quality_assurance", "needs_qa"),
            ("urgent_delivery", "supply_chain", "uses_supply_chain"),
            ("payment_processing", "financial_reporting", "updates_reports")
        ]
        
        for entity1, entity2, relation_type in relationships:
            if entity1 in entities and entity2 in entities:
                self.grammar.create_relationship(
                    entities[entity1], entities[entity2], relation_type
                )
        
        return entities
    
    def _create_attention_network(self) -> Dict[str, List[str]]:
        """Create attention spreading network"""
        connections = {}
        entity_ids = list(self.entities.values())
        
        # Create realistic business process connections
        business_flows = {
            self.entities["enterprise_customer"]: [
                self.entities["large_order"], 
                self.entities["customer_service"]
            ],
            self.entities["large_order"]: [
                self.entities["premium_product"],
                self.entities["payment_processing"],
                self.entities["urgent_delivery"]
            ],
            self.entities["premium_product"]: [
                self.entities["inventory_check"],
                self.entities["quality_assurance"],
                self.entities["supply_chain"]
            ],
            self.entities["urgent_delivery"]: [
                self.entities["supply_chain"],
                self.entities["customer_service"]
            ],
            self.entities["payment_processing"]: [
                self.entities["financial_reporting"]
            ]
        }
        
        return business_flows
    
    def _setup_cognitive_mesh(self):
        """Setup distributed cognitive mesh nodes"""
        mesh_configurations = [
            {
                "node_id": "order_processing_node",
                "config": {
                    "attention_capacity": 200.0,
                    "node_type": "business_process_handler",
                    "specialization": ["order_management", "payment_processing"],
                    "performance_tier": "high"
                }
            },
            {
                "node_id": "inventory_management_node", 
                "config": {
                    "attention_capacity": 150.0,
                    "node_type": "resource_manager",
                    "specialization": ["inventory_tracking", "supply_chain"],
                    "performance_tier": "medium"
                }
            },
            {
                "node_id": "customer_service_node",
                "config": {
                    "attention_capacity": 180.0,
                    "node_type": "interaction_handler",
                    "specialization": ["customer_communication", "issue_resolution"],
                    "performance_tier": "high"
                }
            },
            {
                "node_id": "analytics_node",
                "config": {
                    "attention_capacity": 250.0,
                    "node_type": "data_processor",
                    "specialization": ["financial_analysis", "reporting"],
                    "performance_tier": "premium"
                }
            }
        ]
        
        for mesh_config in mesh_configurations:
            self.ecan.register_mesh_node(
                mesh_config["node_id"], 
                mesh_config["config"]
            )
    
    def demonstrate_resource_allocation(self) -> Dict[str, Any]:
        """Demonstrate dynamic resource allocation"""
        print("\n💼 Demonstrating Dynamic Resource Allocation...")
        
        allocation_results = {
            "requests_made": 0,
            "successful_allocations": 0,
            "resource_utilization": {},
            "processing_time": 0.0
        }
        
        start_time = time.time()
        
        # Simulate various resource requests
        resource_requests = [
            ("order_processor", ResourceType.ATTENTION, 75.0, ResourcePriority.HIGH, 45.0),
            ("inventory_manager", ResourceType.MEMORY, 200.0, ResourcePriority.NORMAL, 60.0),
            ("analytics_engine", ResourceType.COMPUTATION, 150.0, ResourcePriority.HIGH, 90.0),
            ("customer_service", ResourceType.ATTENTION, 50.0, ResourcePriority.CRITICAL, 30.0),
            ("payment_system", ResourceType.BANDWIDTH, 80.0, ResourcePriority.HIGH, 40.0)
        ]
        
        request_ids = []
        for requester, resource_type, amount, priority, duration in resource_requests:
            request_id = self.resource_kernel.request_resource(
                requester_id=requester,
                resource_type=resource_type,
                amount=amount,
                priority=priority,
                duration=duration
            )
            request_ids.append(request_id)
            allocation_results["requests_made"] += 1
        
        # Process resource requests
        allocated_requests = self.resource_kernel.process_resource_requests()
        allocation_results["successful_allocations"] = len(allocated_requests)
        
        # Get resource utilization
        allocation_results["resource_utilization"] = self.resource_kernel.get_resource_utilization()
        allocation_results["processing_time"] = time.time() - start_time
        
        print(f"✅ Resource Allocation: {allocation_results['successful_allocations']}/{allocation_results['requests_made']} successful")
        print(f"⏱️  Processing time: {allocation_results['processing_time']:.4f}s")
        
        return allocation_results
    
    def demonstrate_attention_scheduling(self) -> Dict[str, Any]:
        """Demonstrate intelligent attention scheduling"""
        print("\n🧠 Demonstrating Intelligent Attention Scheduling...")
        
        scheduling_results = {
            "cycles_scheduled": 0,
            "cycles_executed": 0,
            "cycles_completed": 0,
            "total_atoms_processed": 0,
            "scheduling_efficiency": 0.0
        }
        
        # Schedule different attention cycles with varying priorities
        attention_cycles = [
            {
                "cycle_id": "critical_order_processing",
                "atoms": [self.entities["large_order"], self.entities["payment_processing"]],
                "focus_strength": 3.0,
                "priority": ResourcePriority.CRITICAL,
                "duration": 30.0
            },
            {
                "cycle_id": "customer_service_cycle", 
                "atoms": [self.entities["enterprise_customer"], self.entities["customer_service"]],
                "focus_strength": 2.5,
                "priority": ResourcePriority.HIGH,
                "duration": 45.0
            },
            {
                "cycle_id": "inventory_management",
                "atoms": [self.entities["premium_product"], self.entities["inventory_check"]],
                "focus_strength": 2.0,
                "priority": ResourcePriority.NORMAL,
                "duration": 60.0
            },
            {
                "cycle_id": "quality_assurance_cycle",
                "atoms": [self.entities["quality_assurance"], self.entities["premium_product"]],
                "focus_strength": 1.8,
                "priority": ResourcePriority.HIGH,
                "duration": 40.0
            }
        ]
        
        # Schedule all cycles
        for cycle_config in attention_cycles:
            success = self.scheduler.schedule_attention_cycle(**cycle_config)
            if success:
                scheduling_results["cycles_scheduled"] += 1
                scheduling_results["total_atoms_processed"] += len(cycle_config["atoms"])
        
        # Process attention queue
        executed_cycles = self.scheduler.process_attention_queue()
        scheduling_results["cycles_executed"] = len(executed_cycles)
        
        # Complete executed cycles
        for cycle_id in executed_cycles:
            completion_success = self.scheduler.complete_attention_cycle(cycle_id)
            if completion_success:
                scheduling_results["cycles_completed"] += 1
        
        # Calculate efficiency
        if scheduling_results["cycles_scheduled"] > 0:
            scheduling_results["scheduling_efficiency"] = (
                scheduling_results["cycles_completed"] / scheduling_results["cycles_scheduled"]
            )
        
        print(f"✅ Attention Scheduling: {scheduling_results['cycles_completed']}/{scheduling_results['cycles_scheduled']} cycles completed")
        print(f"📊 Efficiency: {scheduling_results['scheduling_efficiency']:.2%}")
        
        return scheduling_results
    
    def demonstrate_mesh_integration(self) -> Dict[str, Any]:
        """Demonstrate distributed cognitive mesh integration"""
        print("\n🌐 Demonstrating Distributed Mesh Integration...")
        
        mesh_results = {
            "mesh_nodes_active": 0,
            "attention_distributed": 0.0,
            "sync_operations": 0,
            "economic_exchanges": 0.0
        }
        
        # Focus attention on key business entities
        key_entities = [
            ("enterprise_customer", 3.5),
            ("large_order", 3.0),
            ("urgent_delivery", 2.8),
            ("payment_processing", 2.5)
        ]
        
        total_distributed_attention = 0.0
        
        for entity_name, focus_strength in key_entities:
            if entity_name in self.entities:
                entity_id = self.entities[entity_name]
                self.ecan.focus_attention(entity_id, focus_strength)
                total_distributed_attention += focus_strength
        
        # Run enhanced attention cycle with mesh integration
        cycle_results = self.ecan.run_enhanced_attention_cycle(
            focus_atoms=[self.entities[name] for name, _ in key_entities],
            enable_mesh_sync=True
        )
        
        # Get mesh statistics
        mesh_stats = self.ecan.get_mesh_statistics()
        mesh_results["mesh_nodes_active"] = mesh_stats["active_mesh_nodes"]
        mesh_results["attention_distributed"] = mesh_stats["total_distributed_attention"]
        
        # Perform additional sync operations
        for _ in range(3):
            sync_result = self.ecan.sync_mesh_attention()
            if sync_result["status"] == "completed":
                mesh_results["sync_operations"] += 1
                mesh_results["economic_exchanges"] += sync_result.get("attention_exchanged", 0.0)
        
        print(f"✅ Mesh Integration: {mesh_results['mesh_nodes_active']} active nodes")
        print(f"💰 Economic Exchanges: {mesh_results['economic_exchanges']:.2f} attention units")
        print(f"🔄 Sync Operations: {mesh_results['sync_operations']} completed")
        
        return mesh_results
    
    def demonstrate_economic_attention_model(self) -> Dict[str, Any]:
        """Demonstrate economic attention allocation model"""
        print("\n💰 Demonstrating Economic Attention Model...")
        
        economic_results = {
            "total_wages_allocated": 0.0,
            "total_rents_allocated": 0.0,
            "attention_economy_health": 0.0,
            "top_valued_entities": []
        }
        
        # Run multiple attention cycles to build economic history
        for i in range(5):
            # Vary attention focus to simulate dynamic business priorities
            cycle_entities = list(self.entities.values())[i*2:(i+1)*2]
            if cycle_entities:
                self.ecan.run_enhanced_attention_cycle(
                    focus_atoms=cycle_entities,
                    enable_mesh_sync=True
                )
        
        # Get economic statistics
        economic_stats = self.ecan.get_economic_stats()
        economic_results["total_wages_allocated"] = economic_stats["total_wages"]
        economic_results["total_rents_allocated"] = economic_stats["total_rents"]
        
        # Calculate attention economy health
        total_funds_available = (
            economic_stats["wage_fund"] + economic_stats["rent_fund"]
        )
        total_funds_allocated = (
            economic_stats["total_wages"] + economic_stats["total_rents"]
        )
        
        if total_funds_available > 0:
            economic_results["attention_economy_health"] = (
                total_funds_allocated / total_funds_available
            )
        
        # Get top valued entities by attention
        attention_focus = self.ecan.get_attention_focus(5)
        economic_results["top_valued_entities"] = [
            {"entity_id": entity_id, "attention_value": attention_val}
            for entity_id, attention_val in attention_focus
        ]
        
        print(f"✅ Economic Model: {economic_results['attention_economy_health']:.2%} economy utilization")
        print(f"💼 Wages Allocated: {economic_results['total_wages_allocated']:.2f}")
        print(f"🏠 Rents Allocated: {economic_results['total_rents_allocated']:.2f}")
        
        return economic_results
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        print("\n🏆 Running Performance Benchmark...")
        
        benchmark_results = {
            "entities_processed_per_second": 0.0,
            "attention_cycles_per_second": 0.0,
            "resource_allocation_time": 0.0,
            "mesh_sync_time": 0.0,
            "total_benchmark_time": 0.0
        }
        
        start_time = time.time()
        
        # Benchmark resource allocation
        resource_start = time.time()
        for i in range(50):
            self.resource_kernel.request_resource(
                requester_id=f"benchmark_requester_{i}",
                resource_type=ResourceType.ATTENTION,
                amount=10.0,
                priority=ResourcePriority.NORMAL,
                duration=20.0
            )
        self.resource_kernel.process_resource_requests()
        benchmark_results["resource_allocation_time"] = time.time() - resource_start
        
        # Benchmark attention cycles
        cycles_start = time.time()
        entity_list = list(self.entities.values())
        cycle_count = 0
        
        for i in range(0, len(entity_list), 2):
            cycle_entities = entity_list[i:i+2]
            if cycle_entities:
                self.ecan.run_enhanced_attention_cycle(
                    focus_atoms=cycle_entities,
                    enable_mesh_sync=False  # Disable for pure cycle benchmark
                )
                cycle_count += 1
        
        cycles_time = time.time() - cycles_start
        if cycles_time > 0:
            benchmark_results["attention_cycles_per_second"] = cycle_count / cycles_time
        
        # Benchmark mesh synchronization
        mesh_start = time.time()
        for _ in range(10):
            self.ecan.sync_mesh_attention()
        benchmark_results["mesh_sync_time"] = time.time() - mesh_start
        
        # Calculate overall performance
        total_time = time.time() - start_time
        benchmark_results["total_benchmark_time"] = total_time
        
        if total_time > 0:
            benchmark_results["entities_processed_per_second"] = (
                len(self.entities) * cycle_count / total_time
            )
        
        print(f"✅ Performance: {benchmark_results['entities_processed_per_second']:.0f} entities/sec")
        print(f"⚡ Attention Cycles: {benchmark_results['attention_cycles_per_second']:.1f} cycles/sec")
        print(f"🔄 Resource Allocation: {benchmark_results['resource_allocation_time']:.4f}s")
        
        return benchmark_results
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive Phase 2 demonstration report"""
        print("\n📊 Generating Comprehensive Phase 2 Report...")
        
        # Collect final statistics from all components
        final_stats = {
            "resource_kernel_stats": self.resource_kernel.get_kernel_stats(),
            "scheduler_stats": self.scheduler.get_scheduler_stats(),
            "ecan_economic_stats": self.ecan.get_economic_stats(),
            "mesh_statistics": self.ecan.get_mesh_statistics(),
            "knowledge_base_stats": self.grammar.get_knowledge_stats(),
            "demo_results": self.demo_results
        }
        
        # Calculate overall system health
        system_health = {
            "resource_utilization_avg": np.mean(list(
                final_stats["resource_kernel_stats"]["resource_utilization"].values()
            )),
            "attention_economy_efficiency": (
                final_stats["ecan_economic_stats"]["total_wages"] / 
                final_stats["ecan_economic_stats"]["wage_fund"]
            ),
            "mesh_integration_success": (
                final_stats["mesh_statistics"]["active_mesh_nodes"] / 
                final_stats["mesh_statistics"]["total_mesh_nodes"]
            ),
            "knowledge_density": final_stats["knowledge_base_stats"]["hypergraph_density"]
        }
        
        print("=" * 70)
        print("📋 PHASE 2 COMPREHENSIVE DEMONSTRATION REPORT")
        print("=" * 70)
        print(f"🔧 Resource Kernel Health: {system_health['resource_utilization_avg']:.2%}")
        print(f"💰 Economic Efficiency: {system_health['attention_economy_efficiency']:.2%}")
        print(f"🌐 Mesh Integration: {system_health['mesh_integration_success']:.2%}")
        print(f"🧠 Knowledge Density: {system_health['knowledge_density']:.3f}")
        
        return {
            "system_statistics": final_stats,
            "system_health": system_health,
            "overall_success": all(metric > 0.8 for metric in system_health.values())
        }
    
    def run_complete_demonstration(self) -> Dict[str, Any]:
        """Run complete Phase 2 integrated demonstration"""
        print("🚀 PHASE 2 INTEGRATED DEMONSTRATION")
        print("ECAN Attention Allocation & Resource Kernel Construction")
        print("=" * 70)
        
        demonstration_start = time.time()
        
        # Run all demonstration components
        self.demo_results["infrastructure"] = self.setup_cognitive_infrastructure()
        self.demo_results["resource_allocation"] = self.demonstrate_resource_allocation()
        self.demo_results["attention_scheduling"] = self.demonstrate_attention_scheduling()
        self.demo_results["mesh_integration"] = self.demonstrate_mesh_integration()
        self.demo_results["economic_model"] = self.demonstrate_economic_attention_model()
        self.demo_results["performance_benchmark"] = self.run_performance_benchmark()
        
        # Generate final report
        final_report = self.generate_comprehensive_report()
        self.demo_results["final_report"] = final_report
        
        total_demo_time = time.time() - demonstration_start
        
        print(f"\n⏱️  Total Demonstration Time: {total_demo_time:.3f}s")
        
        if final_report["overall_success"]:
            print("✅ PHASE 2 DEMONSTRATION: COMPLETE SUCCESS")
            print("All ECAN & Resource Kernel components operational and integrated")
        else:
            print("⚠️  PHASE 2 DEMONSTRATION: Partial success - review metrics")
        
        return self.demo_results


def main():
    """Run the complete Phase 2 integrated demonstration"""
    demo = Phase2IntegratedDemo()
    results = demo.run_complete_demonstration()
    return results


if __name__ == "__main__":
    demonstration_results = main()