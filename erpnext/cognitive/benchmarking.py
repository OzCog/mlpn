"""
Benchmarking Suite for Distributed Cognitive Agents

Provides comprehensive benchmarking capabilities for attention allocation,
resource management, and mesh topology performance across distributed agents.
"""

import numpy as np
import time
import json
import threading
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import matplotlib.pyplot as plt
import io
import base64

from .mesh_topology import DynamicMesh, DistributedAgent, AgentRole, MeshTopology
from .resource_kernel import ResourceKernel, DistributedResourceManager, ResourceType
from .attention_allocation import ECANAttention


class BenchmarkType(Enum):
    """Types of benchmarks to run"""
    ATTENTION_ALLOCATION = "attention_allocation"
    RESOURCE_ALLOCATION = "resource_allocation"
    MESH_COMMUNICATION = "mesh_communication"
    STATE_PROPAGATION = "state_propagation"
    LOAD_BALANCING = "load_balancing"
    FULL_SYSTEM = "full_system"


class MetricType(Enum):
    """Types of metrics to collect"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    SUCCESS_RATE = "success_rate"
    RESOURCE_UTILIZATION = "resource_utilization"
    NETWORK_EFFICIENCY = "network_efficiency"
    SCALABILITY = "scalability"


@dataclass
class BenchmarkResult:
    """Result from a benchmark run"""
    benchmark_type: BenchmarkType
    start_time: float
    end_time: float
    duration: float
    iterations: int
    success_count: int
    failure_count: int
    metrics: Dict[str, Any]
    raw_data: List[Any] = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = []
            
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark runs"""
    benchmark_type: BenchmarkType
    iterations: int = 100
    concurrent_requests: int = 10
    timeout: float = 30.0
    warmup_iterations: int = 10
    collect_raw_data: bool = True
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}


class DistributedCognitiveBenchmark:
    """
    Comprehensive benchmarking suite for distributed cognitive agents
    """
    
    def __init__(self):
        self.results_history: List[BenchmarkResult] = []
        self.mesh: Optional[DynamicMesh] = None
        self.resource_manager: Optional[DistributedResourceManager] = None
        self.attention_systems: Dict[str, ECANAttention] = {}
        self.executor = ThreadPoolExecutor(max_workers=16)
        
    def setup_test_environment(self, num_agents: int = 10, 
                             topology: MeshTopology = MeshTopology.ADAPTIVE) -> bool:
        """
        Set up test environment with distributed agents
        
        Args:
            num_agents: Number of agents to create
            topology: Mesh topology type
            
        Returns:
            True if setup was successful
        """
        try:
            # Create mesh
            self.mesh = DynamicMesh(topology_type=topology)
            self.resource_manager = DistributedResourceManager()
            
            # Create distributed agents with different roles
            roles = list(AgentRole)
            
            for i in range(num_agents):
                # Distribute roles
                role = roles[i % len(roles)]
                agent_id = f"agent_{i:03d}"
                
                # Create agent
                agent = DistributedAgent(agent_id=agent_id, role=role)
                
                # Create resource kernel for agent
                resource_kernel = ResourceKernel(agent_id=agent_id)
                
                # Create attention system for agent
                attention_system = ECANAttention()
                
                # Add to mesh and register with resource manager
                self.mesh.add_agent(agent)
                self.resource_manager.register_resource_kernel(agent_id, resource_kernel)
                self.attention_systems[agent_id] = attention_system
                
            return True
            
        except Exception as e:
            print(f"Error setting up test environment: {e}")
            return False
            
    def teardown_test_environment(self):
        """Tear down test environment"""
        if self.mesh:
            for agent_id in list(self.mesh.agents.keys()):
                self.mesh.remove_agent(agent_id)
                
        if self.resource_manager:
            for agent_id in list(self.resource_manager.resource_kernels.keys()):
                self.resource_manager.unregister_resource_kernel(agent_id)
                
        self.attention_systems.clear()
        # Don't shutdown executor here to avoid shutdown issues
        # self.executor.shutdown(wait=False)
        
    def benchmark_attention_allocation(self, config: BenchmarkConfig) -> BenchmarkResult:
        """
        Benchmark attention allocation performance
        
        Args:
            config: Benchmark configuration
            
        Returns:
            Benchmark results
        """
        if not self.mesh or not self.attention_systems:
            raise ValueError("Test environment not set up")
            
        start_time = time.time()
        success_count = 0
        failure_count = 0
        latencies = []
        throughput_data = []
        raw_data = []
        
        # Warmup
        for _ in range(config.warmup_iterations):
            agent_id = np.random.choice(list(self.attention_systems.keys()))
            attention_system = self.attention_systems[agent_id]
            attention_system.focus_attention(f"warmup_concept_{_}", 1.0)
            
        # Main benchmark
        for i in range(config.iterations):
            batch_start = time.time()
            batch_success = 0
            batch_failure = 0
            
            # Submit concurrent attention requests
            futures = []
            for j in range(config.concurrent_requests):
                future = self.executor.submit(self._attention_allocation_task, i * config.concurrent_requests + j)
                futures.append(future)
                
            # Collect results
            for future in as_completed(futures, timeout=config.timeout):
                try:
                    result = future.result()
                    if result["success"]:
                        batch_success += 1
                        latencies.append(result["latency"])
                    else:
                        batch_failure += 1
                        
                    if config.collect_raw_data:
                        raw_data.append(result)
                        
                except Exception as e:
                    batch_failure += 1
                    
            batch_end = time.time()
            batch_duration = batch_end - batch_start
            batch_throughput = batch_success / batch_duration if batch_duration > 0 else 0
            
            throughput_data.append(batch_throughput)
            success_count += batch_success
            failure_count += batch_failure
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate metrics
        metrics = {
            "avg_latency": statistics.mean(latencies) if latencies else 0,
            "median_latency": statistics.median(latencies) if latencies else 0,
            "p95_latency": np.percentile(latencies, 95) if latencies else 0,
            "p99_latency": np.percentile(latencies, 99) if latencies else 0,
            "avg_throughput": statistics.mean(throughput_data) if throughput_data else 0,
            "max_throughput": max(throughput_data) if throughput_data else 0,
            "total_requests": config.iterations * config.concurrent_requests,
            "requests_per_second": (success_count + failure_count) / duration if duration > 0 else 0,
            "attention_agents": len([a for a in self.mesh.agents.values() if a.state.role == AgentRole.ATTENTION]),
            "mesh_efficiency": self._calculate_mesh_efficiency()
        }
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.ATTENTION_ALLOCATION,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            iterations=config.iterations,
            success_count=success_count,
            failure_count=failure_count,
            metrics=metrics,
            raw_data=raw_data if config.collect_raw_data else []
        )
        
    def _attention_allocation_task(self, task_id: int) -> Dict[str, Any]:
        """
        Single attention allocation task for benchmarking
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            Task result
        """
        task_start = time.time()
        
        try:
            # Select random agent and concept
            agent_id = np.random.choice(list(self.attention_systems.keys()))
            attention_system = self.attention_systems[agent_id]
            concept = f"concept_{task_id % 100}"
            focus_strength = np.random.uniform(0.5, 3.0)
            
            # Focus attention
            attention_system.focus_attention(concept, focus_strength)
            
            # Run attention cycle
            attention_system.run_attention_cycle([concept])
            
            task_end = time.time()
            latency = task_end - task_start
            
            return {
                "success": True,
                "latency": latency,
                "agent_id": agent_id,
                "concept": concept,
                "focus_strength": focus_strength,
                "task_id": task_id
            }
            
        except Exception as e:
            task_end = time.time()
            return {
                "success": False,
                "latency": task_end - task_start,
                "error": str(e),
                "task_id": task_id
            }
            
    def benchmark_resource_allocation(self, config: BenchmarkConfig) -> BenchmarkResult:
        """
        Benchmark distributed resource allocation performance
        
        Args:
            config: Benchmark configuration
            
        Returns:
            Benchmark results
        """
        if not self.resource_manager:
            raise ValueError("Resource manager not set up")
            
        start_time = time.time()
        success_count = 0
        failure_count = 0
        allocation_latencies = []
        resource_utilization_history = []
        raw_data = []
        
        # Warmup
        for _ in range(config.warmup_iterations):
            resource_type = np.random.choice(list(ResourceType))
            requester_id = np.random.choice(list(self.resource_manager.resource_kernels.keys()))
            amount = np.random.uniform(1.0, 10.0)
            self.resource_manager.distributed_resource_request(requester_id, resource_type, amount)
            
        # Main benchmark
        for i in range(config.iterations):
            batch_start = time.time()
            batch_success = 0
            batch_failure = 0
            
            # Submit concurrent resource requests
            futures = []
            for j in range(config.concurrent_requests):
                future = self.executor.submit(self._resource_allocation_task, i * config.concurrent_requests + j)
                futures.append(future)
                
            # Collect results
            for future in as_completed(futures, timeout=config.timeout):
                try:
                    result = future.result()
                    if result["success"]:
                        batch_success += 1
                        allocation_latencies.append(result["latency"])
                    else:
                        batch_failure += 1
                        
                    if config.collect_raw_data:
                        raw_data.append(result)
                        
                except Exception as e:
                    batch_failure += 1
                    
            success_count += batch_success
            failure_count += batch_failure
            
            # Record resource utilization
            global_stats = self.resource_manager.get_global_resource_stats()
            resource_utilization_history.append(global_stats)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate metrics
        avg_utilization = self._calculate_average_utilization(resource_utilization_history)
        
        metrics = {
            "avg_allocation_latency": statistics.mean(allocation_latencies) if allocation_latencies else 0,
            "median_allocation_latency": statistics.median(allocation_latencies) if allocation_latencies else 0,
            "p95_allocation_latency": np.percentile(allocation_latencies, 95) if allocation_latencies else 0,
            "total_resource_requests": config.iterations * config.concurrent_requests,
            "allocations_per_second": (success_count + failure_count) / duration if duration > 0 else 0,
            "average_resource_utilization": avg_utilization,
            "resource_efficiency": success_count / (success_count + failure_count) if (success_count + failure_count) > 0 else 0,
            "total_agents": len(self.resource_manager.resource_kernels)
        }
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.RESOURCE_ALLOCATION,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            iterations=config.iterations,
            success_count=success_count,
            failure_count=failure_count,
            metrics=metrics,
            raw_data=raw_data if config.collect_raw_data else []
        )
        
    def _resource_allocation_task(self, task_id: int) -> Dict[str, Any]:
        """
        Single resource allocation task for benchmarking
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            Task result
        """
        task_start = time.time()
        
        try:
            # Generate random resource request
            resource_type = np.random.choice(list(ResourceType))
            requester_id = np.random.choice(list(self.resource_manager.resource_kernels.keys()))
            amount = np.random.uniform(1.0, 50.0)
            priority = np.random.randint(1, 11)
            
            # Request resource allocation
            allocation_id = self.resource_manager.distributed_resource_request(
                requester_id=requester_id,
                resource_type=resource_type,
                amount=amount,
                priority=priority
            )
            
            task_end = time.time()
            latency = task_end - task_start
            
            return {
                "success": allocation_id is not None,
                "latency": latency,
                "allocation_id": allocation_id,
                "resource_type": resource_type.value,
                "amount": amount,
                "priority": priority,
                "task_id": task_id
            }
            
        except Exception as e:
            task_end = time.time()
            return {
                "success": False,
                "latency": task_end - task_start,
                "error": str(e),
                "task_id": task_id
            }
            
    def benchmark_mesh_communication(self, config: BenchmarkConfig) -> BenchmarkResult:
        """
        Benchmark mesh communication performance
        
        Args:
            config: Benchmark configuration
            
        Returns:
            Benchmark results
        """
        if not self.mesh:
            raise ValueError("Mesh not set up")
            
        start_time = time.time()
        success_count = 0
        failure_count = 0
        communication_latencies = []
        message_sizes = []
        raw_data = []
        
        # Main benchmark
        for i in range(config.iterations):
            batch_start = time.time()
            batch_success = 0
            batch_failure = 0
            
            # Submit concurrent communication tasks
            futures = []
            for j in range(config.concurrent_requests):
                future = self.executor.submit(self._mesh_communication_task, i * config.concurrent_requests + j)
                futures.append(future)
                
            # Collect results
            for future in as_completed(futures, timeout=config.timeout):
                try:
                    result = future.result()
                    if result["success"]:
                        batch_success += 1
                        communication_latencies.append(result["latency"])
                        message_sizes.append(result["message_size"])
                    else:
                        batch_failure += 1
                        
                    if config.collect_raw_data:
                        raw_data.append(result)
                        
                except Exception as e:
                    batch_failure += 1
                    
            success_count += batch_success
            failure_count += batch_failure
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate metrics
        topology_stats = self.mesh.get_mesh_topology_stats()
        
        metrics = {
            "avg_communication_latency": statistics.mean(communication_latencies) if communication_latencies else 0,
            "median_communication_latency": statistics.median(communication_latencies) if communication_latencies else 0,
            "p95_communication_latency": np.percentile(communication_latencies, 95) if communication_latencies else 0,
            "avg_message_size": statistics.mean(message_sizes) if message_sizes else 0,
            "total_messages": config.iterations * config.concurrent_requests,
            "messages_per_second": (success_count + failure_count) / duration if duration > 0 else 0,
            "topology_density": topology_stats.get("topology_density", 0),
            "avg_connections_per_agent": topology_stats.get("avg_connections_per_agent", 0),
            "mesh_efficiency": topology_stats.get("mesh_efficiency", 0)
        }
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.MESH_COMMUNICATION,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            iterations=config.iterations,
            success_count=success_count,
            failure_count=failure_count,
            metrics=metrics,
            raw_data=raw_data if config.collect_raw_data else []
        )
        
    def _mesh_communication_task(self, task_id: int) -> Dict[str, Any]:
        """
        Single mesh communication task for benchmarking
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            Task result
        """
        task_start = time.time()
        
        try:
            # Select random source and target agents
            agent_ids = list(self.mesh.agents.keys())
            if len(agent_ids) < 2:
                return {"success": False, "latency": 0, "error": "Not enough agents", "task_id": task_id}
                
            source_id = np.random.choice(agent_ids)
            target_id = np.random.choice([aid for aid in agent_ids if aid != source_id])
            
            # Create test message
            message_data = {
                "task_id": task_id,
                "timestamp": time.time(),
                "data": [np.random.random() for _ in range(100)]  # 100 random numbers
            }
            message_size = len(json.dumps(message_data))
            
            # Send message (simulated)
            source_agent = self.mesh.agents[source_id]
            message_id = source_agent.send_message(
                receiver_id=target_id,
                message_type="benchmark_test",
                payload=message_data
            )
            
            task_end = time.time()
            latency = task_end - task_start
            
            return {
                "success": True,
                "latency": latency,
                "message_id": message_id,
                "message_size": message_size,
                "source_id": source_id,
                "target_id": target_id,
                "task_id": task_id
            }
            
        except Exception as e:
            task_end = time.time()
            return {
                "success": False,
                "latency": task_end - task_start,
                "error": str(e),
                "task_id": task_id
            }
            
    def run_comprehensive_benchmark(self, agent_counts: List[int] = None,
                                  topologies: List[MeshTopology] = None) -> Dict[str, Any]:
        """
        Run comprehensive benchmark across different configurations
        
        Args:
            agent_counts: List of agent counts to test
            topologies: List of topologies to test
            
        Returns:
            Comprehensive benchmark results
        """
        if agent_counts is None:
            agent_counts = [5, 10, 20, 50]
            
        if topologies is None:
            topologies = [MeshTopology.RING, MeshTopology.FULLY_CONNECTED, MeshTopology.ADAPTIVE]
            
        comprehensive_results = {
            "start_time": time.time(),
            "configurations": [],
            "scalability_analysis": {},
            "topology_comparison": {}
        }
        
        config = BenchmarkConfig(
            benchmark_type=BenchmarkType.FULL_SYSTEM,
            iterations=50,
            concurrent_requests=5,
            warmup_iterations=5
        )
        
        for topology in topologies:
            topology_results = []
            
            for agent_count in agent_counts:
                print(f"Testing {topology.value} topology with {agent_count} agents...")
                
                # Create a new benchmark instance for each test to avoid executor issues
                benchmark = DistributedCognitiveBenchmark()
                
                # Setup environment
                if not benchmark.setup_test_environment(num_agents=agent_count, topology=topology):
                    continue
                    
                # Run benchmarks
                attention_result = benchmark.benchmark_attention_allocation(config)
                resource_result = benchmark.benchmark_resource_allocation(config)
                communication_result = benchmark.benchmark_mesh_communication(config)
                
                config_result = {
                    "agent_count": agent_count,
                    "topology": topology.value,
                    "attention_benchmark": asdict(attention_result),
                    "resource_benchmark": asdict(resource_result),
                    "communication_benchmark": asdict(communication_result)
                }
                
                topology_results.append(config_result)
                comprehensive_results["configurations"].append(config_result)
                
                # Clean up benchmark instance
                benchmark.teardown_test_environment()
                
            comprehensive_results["topology_comparison"][topology.value] = topology_results
            
        # Analyze scalability
        comprehensive_results["scalability_analysis"] = self._analyze_scalability(
            comprehensive_results["configurations"]
        )
        
        comprehensive_results["end_time"] = time.time()
        comprehensive_results["duration"] = (
            comprehensive_results["end_time"] - comprehensive_results["start_time"]
        )
        
        return comprehensive_results
        
    def _analyze_scalability(self, configurations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze scalability from benchmark configurations
        
        Args:
            configurations: List of configuration results
            
        Returns:
            Scalability analysis
        """
        scalability_metrics = {
            "attention_throughput_scaling": [],
            "resource_allocation_scaling": [],
            "communication_efficiency_scaling": []
        }
        
        # Group by topology
        by_topology = defaultdict(list)
        for config in configurations:
            by_topology[config["topology"]].append(config)
            
        for topology, configs in by_topology.items():
            # Sort by agent count
            configs.sort(key=lambda x: x["agent_count"])
            
            attention_throughputs = []
            resource_rates = []
            comm_efficiencies = []
            agent_counts = []
            
            for config in configs:
                agent_counts.append(config["agent_count"])
                
                # Extract metrics
                attention_metrics = config["attention_benchmark"]["metrics"]
                resource_metrics = config["resource_benchmark"]["metrics"]
                comm_metrics = config["communication_benchmark"]["metrics"]
                
                attention_throughputs.append(attention_metrics.get("requests_per_second", 0))
                resource_rates.append(resource_metrics.get("allocations_per_second", 0))
                comm_efficiencies.append(comm_metrics.get("messages_per_second", 0))
                
            # Calculate scaling factors
            if len(attention_throughputs) > 1:
                attention_scaling = [
                    attention_throughputs[i] / attention_throughputs[0] if attention_throughputs[0] > 0 else 0
                    for i in range(len(attention_throughputs))
                ]
                resource_scaling = [
                    resource_rates[i] / resource_rates[0] if resource_rates[0] > 0 else 0
                    for i in range(len(resource_rates))
                ]
                comm_scaling = [
                    comm_efficiencies[i] / comm_efficiencies[0] if comm_efficiencies[0] > 0 else 0
                    for i in range(len(comm_efficiencies))
                ]
                
                scalability_metrics[f"{topology}_attention_scaling"] = {
                    "agent_counts": agent_counts,
                    "scaling_factors": attention_scaling,
                    "linear_ideal": [agent_counts[i] / agent_counts[0] for i in range(len(agent_counts))]
                }
                
                scalability_metrics[f"{topology}_resource_scaling"] = {
                    "agent_counts": agent_counts,
                    "scaling_factors": resource_scaling,
                    "linear_ideal": [agent_counts[i] / agent_counts[0] for i in range(len(agent_counts))]
                }
                
                scalability_metrics[f"{topology}_communication_scaling"] = {
                    "agent_counts": agent_counts,
                    "scaling_factors": comm_scaling,
                    "linear_ideal": [agent_counts[i] / agent_counts[0] for i in range(len(agent_counts))]
                }
                
        return scalability_metrics
        
    def _calculate_mesh_efficiency(self) -> float:
        """Calculate mesh efficiency metric"""
        if not self.mesh:
            return 0.0
            
        stats = self.mesh.get_mesh_topology_stats()
        return stats.get("mesh_efficiency", 0.0)
        
    def _calculate_average_utilization(self, utilization_history: List[Dict[str, Any]]) -> float:
        """Calculate average resource utilization across history"""
        if not utilization_history:
            return 0.0
            
        total_utilization = 0.0
        count = 0
        
        for snapshot in utilization_history:
            resource_types = snapshot.get("resource_types", {})
            for resource_data in resource_types.values():
                total_utilization += resource_data.get("global_utilization", 0.0)
                count += 1
                
        return total_utilization / count if count > 0 else 0.0
        
    def generate_benchmark_report(self, results: List[BenchmarkResult]) -> str:
        """
        Generate comprehensive benchmark report
        
        Args:
            results: List of benchmark results
            
        Returns:
            Formatted benchmark report
        """
        report = []
        report.append("=" * 80)
        report.append("DISTRIBUTED COGNITIVE AGENTS BENCHMARK REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        if results:
            total_duration = sum(r.duration for r in results)
            total_iterations = sum(r.iterations for r in results)
            total_success = sum(r.success_count for r in results)
            total_failure = sum(r.failure_count for r in results)
            overall_success_rate = total_success / (total_success + total_failure) if (total_success + total_failure) > 0 else 0
            
            report.append(f"SUMMARY:")
            report.append(f"  Total benchmarks: {len(results)}")
            report.append(f"  Total duration: {total_duration:.2f} seconds")
            report.append(f"  Total iterations: {total_iterations}")
            report.append(f"  Overall success rate: {overall_success_rate:.2%}")
            report.append("")
            
        # Individual benchmark results
        for i, result in enumerate(results):
            report.append(f"BENCHMARK #{i+1}: {result.benchmark_type.value.upper()}")
            report.append("-" * 60)
            report.append(f"  Duration: {result.duration:.2f} seconds")
            report.append(f"  Iterations: {result.iterations}")
            report.append(f"  Success rate: {result.success_rate:.2%}")
            report.append(f"  Successes: {result.success_count}")
            report.append(f"  Failures: {result.failure_count}")
            report.append("")
            
            # Key metrics
            if result.metrics:
                report.append("  Key Metrics:")
                for metric, value in result.metrics.items():
                    if isinstance(value, float):
                        report.append(f"    {metric}: {value:.4f}")
                    else:
                        report.append(f"    {metric}: {value}")
                report.append("")
                
        report.append("=" * 80)
        
        return "\n".join(report)
        
    def scheme_benchmark_spec(self) -> str:
        """
        Generate Scheme specification for benchmarking
        
        Returns:
            Scheme specification string
        """
        spec = """
(define (benchmark-setup num-agents topology)
  (let ((mesh (mesh-topology-create topology))
        (resource-manager (make-resource-manager))
        (attention-systems (make-hash-table)))
    (repeat num-agents
      (let ((agent (create-distributed-agent))
            (kernel (create-resource-kernel))
            (attention (create-attention-system)))
        (mesh-add-agent mesh agent)
        (resource-manager-register resource-manager agent kernel)
        (hash-table-set! attention-systems (agent-id agent) attention)))
    (list mesh resource-manager attention-systems)))

(define (benchmark-attention-allocation systems iterations)
  (let ((start-time (current-time))
        (success-count 0)
        (latencies '()))
    (repeat iterations
      (let ((agent-id (random-agent-id systems))
            (concept (random-concept))
            (task-start (current-time)))
        (attention-focus (hash-table-ref systems agent-id) concept)
        (let ((latency (- (current-time) task-start)))
          (set! latencies (cons latency latencies))
          (set! success-count (+ success-count 1)))))
    (make-benchmark-result 'attention success-count latencies (- (current-time) start-time))))

(define (benchmark-resource-allocation manager iterations)
  (let ((start-time (current-time))
        (success-count 0)
        (allocation-times '()))
    (repeat iterations
      (let ((resource-type (random-resource-type))
            (amount (random-amount))
            (task-start (current-time)))
        (let ((allocation-id (resource-request manager resource-type amount)))
          (let ((allocation-time (- (current-time) task-start)))
            (set! allocation-times (cons allocation-time allocation-times))
            (when allocation-id (set! success-count (+ success-count 1)))))))
    (make-benchmark-result 'resource success-count allocation-times (- (current-time) start-time))))
"""
        return spec.strip()