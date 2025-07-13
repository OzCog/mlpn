"""
Tensor Signature Benchmarking System

Comprehensive performance measurement framework for neural-symbolic tensor operations.
Provides benchmarking, profiling, and performance optimization for custom GGML kernels.
"""

import numpy as np
import time
import json
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path


class BenchmarkMetric(Enum):
    """Available benchmarking metrics"""
    EXECUTION_TIME = "execution_time"
    THROUGHPUT = "throughput" 
    MEMORY_USAGE = "memory_usage"
    CACHE_EFFICIENCY = "cache_efficiency"
    PARALLELIZATION_FACTOR = "parallelization_factor"
    ACCURACY = "accuracy"


@dataclass
class BenchmarkResult:
    """Individual benchmark result"""
    operation_name: str
    input_shapes: List[Tuple[int, ...]]
    output_shape: Tuple[int, ...]
    execution_time: float
    memory_usage: int
    throughput: float
    accuracy: Optional[float] = None
    additional_metrics: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results for analysis"""
    suite_name: str
    results: List[BenchmarkResult]
    timestamp: float
    system_info: Dict[str, Any]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics for the benchmark suite"""
        if not self.results:
            return {}
            
        execution_times = [r.execution_time for r in self.results]
        throughputs = [r.throughput for r in self.results]
        memory_usages = [r.memory_usage for r in self.results]
        
        return {
            "total_operations": len(self.results),
            "execution_time": {
                "mean": statistics.mean(execution_times),
                "median": statistics.median(execution_times),
                "std": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                "min": min(execution_times),
                "max": max(execution_times)
            },
            "throughput": {
                "mean": statistics.mean(throughputs),
                "median": statistics.median(throughputs),
                "total": sum(throughputs)
            },
            "memory_usage": {
                "mean": statistics.mean(memory_usages),
                "total": sum(memory_usages),
                "max": max(memory_usages)
            }
        }


class TensorSignatureBenchmark:
    """
    Main benchmarking system for tensor signature performance measurement
    """
    
    def __init__(self, output_dir: str = "./benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.benchmark_history = []
        self.system_info = self._collect_system_info()
        
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for benchmark context"""
        import platform
        import psutil
        
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available
        }
        
    def benchmark_operation(self, 
                           operation_func: Callable,
                           operation_name: str,
                           inputs: List[np.ndarray],
                           iterations: int = 100,
                           warmup_iterations: int = 10) -> BenchmarkResult:
        """
        Benchmark a single tensor operation
        
        Args:
            operation_func: Function to benchmark
            operation_name: Name of the operation
            inputs: Input tensors
            iterations: Number of benchmark iterations
            warmup_iterations: Number of warmup iterations
            
        Returns:
            Benchmark result
        """
        # Warmup runs
        for _ in range(warmup_iterations):
            operation_func(inputs)
            
        # Benchmark runs
        execution_times = []
        memory_usages = []
        results = []
        
        for _ in range(iterations):
            # Memory usage before operation
            memory_before = sum(inp.nbytes for inp in inputs)
            
            # Time the operation
            start_time = time.perf_counter()
            result = operation_func(inputs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # Memory usage after operation
            memory_after = memory_before + result.nbytes
            memory_usages.append(memory_after)
            results.append(result)
            
        # Calculate metrics
        avg_execution_time = statistics.mean(execution_times)
        total_operations = iterations
        throughput = total_operations / sum(execution_times)
        avg_memory_usage = statistics.mean(memory_usages)
        
        # Calculate accuracy if ground truth is available
        accuracy = self._calculate_accuracy(results) if len(results) > 1 else None
        
        input_shapes = [inp.shape for inp in inputs]
        output_shape = results[0].shape if results else ()
        
        return BenchmarkResult(
            operation_name=operation_name,
            input_shapes=input_shapes,
            output_shape=output_shape,
            execution_time=avg_execution_time,
            memory_usage=int(avg_memory_usage),
            throughput=throughput,
            accuracy=accuracy,
            additional_metrics={
                "execution_time_std": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                "iterations": iterations,
                "warmup_iterations": warmup_iterations
            }
        )
        
    def _calculate_accuracy(self, results: List[np.ndarray]) -> float:
        """Calculate accuracy metric for repeated operations"""
        if len(results) < 2:
            return 1.0
            
        # Check consistency across runs (for deterministic operations)
        reference = results[0]
        accuracies = []
        
        for result in results[1:]:
            if result.shape == reference.shape:
                # Calculate relative error
                diff = np.abs(result - reference)
                rel_error = np.mean(diff) / (np.mean(np.abs(reference)) + 1e-8)
                accuracy = max(0.0, 1.0 - rel_error)
                accuracies.append(accuracy)
                
        return statistics.mean(accuracies) if accuracies else 1.0
        
    def benchmark_kernel_registry(self, 
                                kernel_registry,
                                test_sizes: List[int] = [100, 1000, 10000],
                                iterations: int = 50) -> BenchmarkSuite:
        """
        Benchmark all kernels in a registry across different input sizes
        
        Args:
            kernel_registry: Neural-symbolic kernel registry
            test_sizes: Different input sizes to test
            iterations: Number of iterations per test
            
        Returns:
            Complete benchmark suite
        """
        suite_name = f"kernel_registry_benchmark_{int(time.time())}"
        results = []
        
        for kernel_name in kernel_registry.list_kernels():
            signature = kernel_registry.get_kernel_signature(kernel_name)
            
            for size in test_sizes:
                # Generate test inputs based on signature and size
                test_inputs = self._generate_test_inputs(signature, size)
                
                # Create benchmark function
                def benchmark_func(inputs):
                    return kernel_registry.execute_kernel(kernel_name, inputs)
                    
                # Run benchmark
                result = self.benchmark_operation(
                    benchmark_func,
                    f"{kernel_name}_size_{size}",
                    test_inputs,
                    iterations
                )
                
                results.append(result)
                
        suite = BenchmarkSuite(
            suite_name=suite_name,
            results=results,
            timestamp=time.time(),
            system_info=self.system_info
        )
        
        self.benchmark_history.append(suite)
        return suite
        
    def _generate_test_inputs(self, signature, size: int) -> List[np.ndarray]:
        """Generate test inputs based on tensor signature"""
        test_inputs = []
        
        for input_shape in signature.input_shapes:
            # Handle dynamic shapes
            actual_shape = []
            for dim in input_shape:
                if dim == -1:
                    actual_shape.append(size)
                else:
                    actual_shape.append(dim)
                    
            # Generate random test data
            test_input = np.random.randn(*actual_shape).astype(np.float32)
            test_inputs.append(test_input)
            
        return test_inputs
        
    def benchmark_distributed_mesh(self, 
                                 mesh_nodes: List[Any],
                                 operation_name: str,
                                 test_data: List[np.ndarray],
                                 iterations: int = 20) -> BenchmarkResult:
        """
        Benchmark distributed mesh operations
        
        Args:
            mesh_nodes: List of mesh nodes to benchmark
            operation_name: Name of the distributed operation
            test_data: Test data for the operation
            iterations: Number of iterations
            
        Returns:
            Distributed benchmark result
        """
        execution_times = []
        memory_usages = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            # Simulate distributed operation
            # In real implementation, this would distribute work across mesh nodes
            distributed_results = []
            for node_id, node in enumerate(mesh_nodes):
                # Distribute data to node
                node_data = test_data[node_id % len(test_data)]
                # Simulate processing (placeholder)
                node_result = node_data * 2  # Simple operation
                distributed_results.append(node_result)
                
            # Aggregate results
            final_result = np.concatenate(distributed_results) if distributed_results else np.array([])
            
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
            
            # Calculate memory usage
            memory_usage = sum(data.nbytes for data in test_data) + final_result.nbytes
            memory_usages.append(memory_usage)
            
        avg_execution_time = statistics.mean(execution_times)
        throughput = iterations / sum(execution_times)
        avg_memory_usage = statistics.mean(memory_usages)
        
        return BenchmarkResult(
            operation_name=f"distributed_{operation_name}",
            input_shapes=[data.shape for data in test_data],
            output_shape=final_result.shape if 'final_result' in locals() else (),
            execution_time=avg_execution_time,
            memory_usage=int(avg_memory_usage),
            throughput=throughput,
            additional_metrics={
                "mesh_nodes": len(mesh_nodes),
                "distribution_overhead": avg_execution_time / len(mesh_nodes),
                "parallelization_factor": len(mesh_nodes)
            }
        )
        
    def profile_memory_usage(self, 
                           operation_func: Callable,
                           inputs: List[np.ndarray],
                           iterations: int = 10) -> Dict[str, Any]:
        """
        Profile memory usage of an operation
        
        Args:
            operation_func: Function to profile
            inputs: Input tensors
            iterations: Number of iterations
            
        Returns:
            Memory usage profile
        """
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_snapshots = []
        
        # Baseline memory
        baseline_memory = process.memory_info().rss
        
        for i in range(iterations):
            memory_before = process.memory_info().rss
            result = operation_func(inputs)
            memory_after = process.memory_info().rss
            
            memory_snapshots.append({
                "iteration": i,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_delta": memory_after - memory_before,
                "result_size": result.nbytes
            })
            
        return {
            "baseline_memory": baseline_memory,
            "snapshots": memory_snapshots,
            "peak_memory": max(snap["memory_after"] for snap in memory_snapshots),
            "total_allocated": sum(snap["result_size"] for snap in memory_snapshots),
            "memory_efficiency": sum(snap["result_size"] for snap in memory_snapshots) / max(snap["memory_delta"] for snap in memory_snapshots) if memory_snapshots else 0
        }
        
    def generate_performance_report(self, 
                                  suite: BenchmarkSuite,
                                  output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive performance report
        
        Args:
            suite: Benchmark suite to analyze
            output_file: Optional output file path
            
        Returns:
            Performance report as string
        """
        report_lines = []
        report_lines.append(f"# Tensor Signature Benchmark Report")
        report_lines.append(f"Suite: {suite.suite_name}")
        report_lines.append(f"Timestamp: {time.ctime(suite.timestamp)}")
        report_lines.append("")
        
        # System information
        report_lines.append("## System Information")
        for key, value in suite.system_info.items():
            report_lines.append(f"- {key}: {value}")
        report_lines.append("")
        
        # Summary statistics
        summary = suite.get_summary_stats()
        report_lines.append("## Summary Statistics")
        report_lines.append(f"- Total Operations: {summary.get('total_operations', 0)}")
        
        if 'execution_time' in summary:
            exec_stats = summary['execution_time']
            report_lines.append(f"- Average Execution Time: {exec_stats['mean']:.6f}s")
            report_lines.append(f"- Median Execution Time: {exec_stats['median']:.6f}s")
            report_lines.append(f"- Execution Time Range: {exec_stats['min']:.6f}s - {exec_stats['max']:.6f}s")
            
        if 'throughput' in summary:
            throughput_stats = summary['throughput']
            report_lines.append(f"- Average Throughput: {throughput_stats['mean']:.2f} ops/s")
            report_lines.append(f"- Total Throughput: {throughput_stats['total']:.2f} ops/s")
            
        report_lines.append("")
        
        # Detailed results
        report_lines.append("## Detailed Results")
        for result in suite.results:
            report_lines.append(f"### {result.operation_name}")
            report_lines.append(f"- Input Shapes: {result.input_shapes}")
            report_lines.append(f"- Output Shape: {result.output_shape}")
            report_lines.append(f"- Execution Time: {result.execution_time:.6f}s")
            report_lines.append(f"- Memory Usage: {result.memory_usage:,} bytes")
            report_lines.append(f"- Throughput: {result.throughput:.2f} ops/s")
            if result.accuracy is not None:
                report_lines.append(f"- Accuracy: {result.accuracy:.4f}")
            report_lines.append("")
            
        report_content = "\n".join(report_lines)
        
        if output_file:
            output_path = self.output_dir / output_file
            with open(output_path, 'w') as f:
                f.write(report_content)
                
        return report_content
        
    def save_benchmark_data(self, suite: BenchmarkSuite, filename: Optional[str] = None):
        """Save benchmark data to JSON file"""
        if filename is None:
            filename = f"{suite.suite_name}.json"
            
        output_path = self.output_dir / filename
        
        # Convert to serializable format
        suite_data = {
            "suite_name": suite.suite_name,
            "timestamp": suite.timestamp,
            "system_info": suite.system_info,
            "results": [result.to_dict() for result in suite.results],
            "summary_stats": suite.get_summary_stats()
        }
        
        with open(output_path, 'w') as f:
            json.dump(suite_data, f, indent=2)
            
    def compare_benchmarks(self, 
                         suite1: BenchmarkSuite, 
                         suite2: BenchmarkSuite) -> Dict[str, Any]:
        """
        Compare two benchmark suites
        
        Args:
            suite1: First benchmark suite
            suite2: Second benchmark suite
            
        Returns:
            Comparison analysis
        """
        summary1 = suite1.get_summary_stats()
        summary2 = suite2.get_summary_stats()
        
        comparison = {
            "suites": {
                "suite1": suite1.suite_name,
                "suite2": suite2.suite_name
            },
            "performance_delta": {}
        }
        
        if 'execution_time' in summary1 and 'execution_time' in summary2:
            time1 = summary1['execution_time']['mean']
            time2 = summary2['execution_time']['mean']
            improvement = (time1 - time2) / time1 * 100 if time1 > 0 else 0
            comparison["performance_delta"]["execution_time_improvement"] = improvement
            
        if 'throughput' in summary1 and 'throughput' in summary2:
            throughput1 = summary1['throughput']['mean']
            throughput2 = summary2['throughput']['mean']
            improvement = (throughput2 - throughput1) / throughput1 * 100 if throughput1 > 0 else 0
            comparison["performance_delta"]["throughput_improvement"] = improvement
            
        # Operation-level comparison
        operations_comparison = {}
        for result1 in suite1.results:
            for result2 in suite2.results:
                if result1.operation_name == result2.operation_name:
                    time_improvement = (result1.execution_time - result2.execution_time) / result1.execution_time * 100
                    operations_comparison[result1.operation_name] = {
                        "execution_time_improvement": time_improvement,
                        "memory_usage_delta": result2.memory_usage - result1.memory_usage
                    }
                    
        comparison["operations"] = operations_comparison
        return comparison


def create_standard_benchmark_suite() -> TensorSignatureBenchmark:
    """Create standard benchmarking suite for neural-symbolic operations"""
    benchmark = TensorSignatureBenchmark()
    return benchmark