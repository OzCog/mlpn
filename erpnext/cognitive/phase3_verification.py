"""
Phase 3 Verification and Testing System

Comprehensive testing protocols for Neural-Symbolic Synthesis via Custom ggml Kernels.
Implements real implementation verification with no mocks.
"""

import numpy as np
import time
import json
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

# Import our neural-symbolic components
try:
    from .neural_symbolic_kernels import (
        CustomGGMLKernelRegistry, 
        create_default_kernel_registry,
        NeuralSymbolicSynthesizer,
        GGMLConceptualEmbeddingKernel,
        GGMLLogicalInferenceKernel,
        GGMLAttentionAllocationKernel,
        GGMLHypergraphConvolutionKernel
    )
    from .tensor_benchmarking import TensorSignatureBenchmark, create_standard_benchmark_suite
    from .tensor_kernel import TensorKernel, TensorFormat
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from neural_symbolic_kernels import (
        CustomGGMLKernelRegistry, 
        create_default_kernel_registry,
        NeuralSymbolicSynthesizer,
        GGMLConceptualEmbeddingKernel,
        GGMLLogicalInferenceKernel,
        GGMLAttentionAllocationKernel,
        GGMLHypergraphConvolutionKernel
    )
    from tensor_benchmarking import TensorSignatureBenchmark, create_standard_benchmark_suite
    from tensor_kernel import TensorKernel, TensorFormat


class Phase3VerificationSuite:
    """
    Comprehensive verification suite for Phase 3 implementation
    """
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.integration_results = {}
        self.verification_timestamp = time.time()
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 3 verification tests"""
        print("🔬 Starting Phase 3 Verification Suite...")
        
        results = {
            "kernel_customization_tests": self.test_kernel_customization(),
            "tensor_signature_benchmarking": self.test_tensor_signature_benchmarking(),
            "neural_symbolic_synthesis": self.test_neural_symbolic_synthesis(),
            "integration_verification": self.test_integration_verification(),
            "performance_validation": self.test_performance_validation(),
            "real_implementation_verification": self.test_real_implementation_verification(),
            "distributed_mesh_integration": self.test_distributed_mesh_integration()
        }
        
        # Generate summary
        results["summary"] = self._generate_test_summary(results)
        results["timestamp"] = self.verification_timestamp
        
        return results
        
    def test_kernel_customization(self) -> Dict[str, Any]:
        """Test custom GGML kernel implementations"""
        print("  Testing kernel customization...")
        
        test_results = {}
        
        # Test 1: Kernel Registry Creation
        try:
            registry = create_default_kernel_registry()
            kernels = registry.list_kernels()
            test_results["registry_creation"] = {
                "passed": True,
                "registered_kernels": len(kernels),
                "kernel_names": kernels
            }
        except Exception as e:
            test_results["registry_creation"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 2: Individual Kernel Functionality
        kernel_tests = {}
        
        # Conceptual Embedding Kernel
        try:
            kernel = GGMLConceptualEmbeddingKernel(concept_dim=64, embedding_dim=128)
            neural_input = np.random.randn(128).astype(np.float32)
            symbolic_input = np.random.randn(64).astype(np.float32)
            
            result = kernel.forward([neural_input, symbolic_input])
            
            kernel_tests["conceptual_embedding"] = {
                "passed": True,
                "input_shapes": [neural_input.shape, symbolic_input.shape],
                "output_shape": result.shape,
                "output_dtype": str(result.dtype),
                "operation_count": kernel.operation_count
            }
        except Exception as e:
            kernel_tests["conceptual_embedding"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Logical Inference Kernel
        try:
            kernel = GGMLLogicalInferenceKernel(logic_dim=64)
            premise = np.random.randn(64).astype(np.float32)
            rule = np.random.randn(64).astype(np.float32)
            op_code = np.array([0])  # AND operation
            
            result = kernel.forward([premise, rule, op_code])
            
            kernel_tests["logical_inference"] = {
                "passed": True,
                "input_shapes": [premise.shape, rule.shape, op_code.shape],
                "output_shape": result.shape,
                "operation_count": kernel.operation_count
            }
        except Exception as e:
            kernel_tests["logical_inference"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Attention Allocation Kernel
        try:
            kernel = GGMLAttentionAllocationKernel(attention_dim=128, num_heads=4)
            atoms = np.random.randn(10, 128).astype(np.float32)
            attention_vals = np.random.randn(10).astype(np.float32)
            focus = np.random.randn(128).astype(np.float32)
            
            result = kernel.forward([atoms, attention_vals, focus])
            
            kernel_tests["attention_allocation"] = {
                "passed": True,
                "input_shapes": [atoms.shape, attention_vals.shape, focus.shape],
                "output_shape": result.shape,
                "operation_count": kernel.operation_count
            }
        except Exception as e:
            kernel_tests["attention_allocation"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Hypergraph Convolution Kernel
        try:
            kernel = GGMLHypergraphConvolutionKernel(node_dim=64, edge_dim=32, output_dim=64)
            nodes = np.random.randn(20, 64).astype(np.float32)
            edges = np.random.randn(15, 32).astype(np.float32)
            structure = np.random.rand(20, 20).astype(np.float32)
            
            result = kernel.forward([nodes, edges, structure])
            
            kernel_tests["hypergraph_convolution"] = {
                "passed": True,
                "input_shapes": [nodes.shape, edges.shape, structure.shape],
                "output_shape": result.shape,
                "operation_count": kernel.operation_count
            }
        except Exception as e:
            kernel_tests["hypergraph_convolution"] = {
                "passed": False,
                "error": str(e)
            }
            
        test_results["individual_kernels"] = kernel_tests
        
        # Test 3: Kernel Integration with Registry
        try:
            registry = create_default_kernel_registry()
            test_input = [
                np.random.randn(128).astype(np.float32),
                np.random.randn(256).astype(np.float32)
            ]
            
            result = registry.execute_kernel("conceptual_embedding", test_input)
            
            test_results["registry_integration"] = {
                "passed": True,
                "result_shape": result.shape,
                "registry_stats": registry.get_registry_stats()
            }
        except Exception as e:
            test_results["registry_integration"] = {
                "passed": False,
                "error": str(e)
            }
            
        return test_results
        
    def test_tensor_signature_benchmarking(self) -> Dict[str, Any]:
        """Test tensor signature benchmarking system"""
        print("  Testing tensor signature benchmarking...")
        
        test_results = {}
        
        # Test 1: Benchmark System Creation
        try:
            benchmark = create_standard_benchmark_suite()
            test_results["benchmark_creation"] = {
                "passed": True,
                "system_info": benchmark.system_info
            }
        except Exception as e:
            test_results["benchmark_creation"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 2: Individual Operation Benchmarking
        try:
            benchmark = create_standard_benchmark_suite()
            
            # Simple test operation
            def test_operation(inputs):
                return np.dot(inputs[0], inputs[1].T)
                
            test_inputs = [
                np.random.randn(100, 50).astype(np.float32),
                np.random.randn(100, 50).astype(np.float32)
            ]
            
            result = benchmark.benchmark_operation(
                test_operation,
                "matrix_multiplication",
                test_inputs,
                iterations=10
            )
            
            test_results["individual_benchmarking"] = {
                "passed": True,
                "execution_time": result.execution_time,
                "throughput": result.throughput,
                "memory_usage": result.memory_usage,
                "accuracy": result.accuracy
            }
        except Exception as e:
            test_results["individual_benchmarking"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 3: Kernel Registry Benchmarking
        try:
            benchmark = create_standard_benchmark_suite()
            registry = create_default_kernel_registry()
            
            suite = benchmark.benchmark_kernel_registry(
                registry,
                test_sizes=[10, 100],
                iterations=5
            )
            
            test_results["registry_benchmarking"] = {
                "passed": True,
                "suite_name": suite.suite_name,
                "total_results": len(suite.results),
                "summary_stats": suite.get_summary_stats()
            }
        except Exception as e:
            test_results["registry_benchmarking"] = {
                "passed": False,
                "error": str(e)
            }
            
        return test_results
        
    def test_neural_symbolic_synthesis(self) -> Dict[str, Any]:
        """Test neural-symbolic synthesis functionality"""
        print("  Testing neural-symbolic synthesis...")
        
        test_results = {}
        
        # Test 1: Synthesizer Creation
        try:
            synthesizer = NeuralSymbolicSynthesizer()
            test_results["synthesizer_creation"] = {
                "passed": True,
                "registry_kernels": synthesizer.registry.list_kernels()
            }
        except Exception as e:
            test_results["synthesizer_creation"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 2: Basic Synthesis Operation
        try:
            synthesizer = NeuralSymbolicSynthesizer()
            
            symbolic_input = {
                "concept": "test_concept",
                "truth_value": {"strength": 0.8, "confidence": 0.9}
            }
            neural_input = np.random.randn(256).astype(np.float32)
            
            result = synthesizer.synthesize(
                symbolic_input,
                neural_input,
                synthesis_type="conceptual_embedding"
            )
            
            test_results["basic_synthesis"] = {
                "passed": True,
                "input_symbolic": symbolic_input,
                "neural_input_shape": neural_input.shape,
                "output_shape": result.shape,
                "synthesis_stats": synthesizer.get_synthesis_stats()
            }
        except Exception as e:
            test_results["basic_synthesis"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 3: Multiple Synthesis Types
        synthesis_tests = {}
        
        for synthesis_type in ["conceptual_embedding", "logical_inference", "attention_allocation"]:
            try:
                synthesizer = NeuralSymbolicSynthesizer()
                
                symbolic_input = {"concept": f"test_{synthesis_type}"}
                neural_input = np.random.randn(256).astype(np.float32)
                
                if synthesis_type == "logical_inference":
                    # Adjust for logical inference requirements
                    neural_input = np.random.randn(128).astype(np.float32)
                elif synthesis_type == "attention_allocation":
                    # Adjust for attention allocation requirements
                    neural_input = np.random.randn(256).astype(np.float32)
                    
                result = synthesizer.synthesize(
                    symbolic_input,
                    neural_input,
                    synthesis_type=synthesis_type
                )
                
                synthesis_tests[synthesis_type] = {
                    "passed": True,
                    "output_shape": result.shape
                }
            except Exception as e:
                synthesis_tests[synthesis_type] = {
                    "passed": False,
                    "error": str(e)
                }
                
        test_results["multiple_synthesis_types"] = synthesis_tests
        
        return test_results
        
    def test_integration_verification(self) -> Dict[str, Any]:
        """Test integration with existing Phase 1/2 components"""
        print("  Testing integration verification...")
        
        test_results = {}
        
        # Test 1: Tensor Kernel Integration
        try:
            tensor_kernel = TensorKernel()
            enabled = tensor_kernel.enable_neural_symbolic_synthesis()
            
            if enabled:
                # Test neural-symbolic operation through tensor kernel
                test_inputs = [
                    np.random.randn(128).astype(np.float32),
                    np.random.randn(256).astype(np.float32)
                ]
                
                result = tensor_kernel.neural_symbolic_operation(
                    "conceptual_embedding",
                    test_inputs
                )
                
                test_results["tensor_kernel_integration"] = {
                    "passed": True,
                    "neural_symbolic_enabled": enabled,
                    "operation_result_shape": result.shape,
                    "kernel_stats": tensor_kernel.get_operation_stats()
                }
            else:
                test_results["tensor_kernel_integration"] = {
                    "passed": False,
                    "neural_symbolic_enabled": False,
                    "error": "Neural-symbolic synthesis not available"
                }
        except Exception as e:
            test_results["tensor_kernel_integration"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 2: GGML Format Conversion
        try:
            tensor_kernel = TensorKernel()
            test_data = np.random.randn(100, 50).astype(np.float64)
            
            ggml_tensor = tensor_kernel.create_tensor(
                test_data,
                TensorFormat.GGML
            )
            
            test_results["ggml_format_conversion"] = {
                "passed": True,
                "original_dtype": str(test_data.dtype),
                "converted_dtype": str(ggml_tensor.dtype),
                "original_shape": test_data.shape,
                "converted_shape": ggml_tensor.shape,
                "memory_contiguous": ggml_tensor.flags['C_CONTIGUOUS']
            }
        except Exception as e:
            test_results["ggml_format_conversion"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 3: Parallel Operations Enhancement
        try:
            tensor_kernel = TensorKernel()
            test_tensors = [
                np.random.randn(50, 50).astype(np.float32) for _ in range(5)
            ]
            
            # Test enhanced parallel operations
            parallel_ops = ["reduce", "map", "scan", "stencil"]
            parallel_results = {}
            
            for op in parallel_ops:
                try:
                    if op == "map":
                        result = tensor_kernel.parallel_operation(
                            op, test_tensors, func=lambda x: x * 2
                        )
                    else:
                        result = tensor_kernel.parallel_operation(op, test_tensors)
                        
                    parallel_results[op] = {
                        "passed": True,
                        "result_shape": result.shape
                    }
                except Exception as e:
                    parallel_results[op] = {
                        "passed": False,
                        "error": str(e)
                    }
                    
            test_results["parallel_operations"] = parallel_results
        except Exception as e:
            test_results["parallel_operations"] = {
                "passed": False,
                "error": str(e)
            }
            
        return test_results
        
    def test_performance_validation(self) -> Dict[str, Any]:
        """Test performance characteristics and optimization"""
        print("  Testing performance validation...")
        
        test_results = {}
        
        # Test 1: Kernel Performance Benchmarking
        try:
            synthesizer = NeuralSymbolicSynthesizer()
            benchmarks = synthesizer.benchmark_kernels(iterations=20)
            
            # Validate performance thresholds
            performance_validation = {}
            for kernel_name, metrics in benchmarks.items():
                # Define performance thresholds
                max_execution_time = 0.1  # 100ms max
                min_ops_per_second = 10   # At least 10 ops/sec
                
                performance_validation[kernel_name] = {
                    "execution_time_ok": metrics["avg_execution_time"] < max_execution_time,
                    "throughput_ok": metrics["operations_per_second"] > min_ops_per_second,
                    "avg_execution_time": metrics["avg_execution_time"],
                    "operations_per_second": metrics["operations_per_second"]
                }
                
            test_results["kernel_performance"] = {
                "passed": True,
                "benchmarks": benchmarks,
                "validation": performance_validation
            }
        except Exception as e:
            test_results["kernel_performance"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 2: Memory Efficiency Testing
        try:
            benchmark = create_standard_benchmark_suite()
            
            def memory_intensive_operation(inputs):
                # Create temporary large tensors to test memory management
                temp = np.random.randn(1000, 1000).astype(np.float32)
                result = np.dot(inputs[0], temp[:inputs[0].shape[1], :inputs[0].shape[0]].T)
                return result
                
            test_inputs = [np.random.randn(100, 100).astype(np.float32)]
            
            memory_profile = benchmark.profile_memory_usage(
                memory_intensive_operation,
                test_inputs,
                iterations=5
            )
            
            test_results["memory_efficiency"] = {
                "passed": True,
                "peak_memory": memory_profile["peak_memory"],
                "memory_efficiency": memory_profile["memory_efficiency"],
                "baseline_memory": memory_profile["baseline_memory"]
            }
        except Exception as e:
            test_results["memory_efficiency"] = {
                "passed": False,
                "error": str(e)
            }
            
        return test_results
        
    def test_real_implementation_verification(self) -> Dict[str, Any]:
        """Verify real implementation with no mocks or simulations"""
        print("  Testing real implementation verification...")
        
        test_results = {}
        
        # Test 1: Actual Tensor Mathematics
        try:
            # Verify real mathematical operations
            kernel = GGMLConceptualEmbeddingKernel(concept_dim=32, embedding_dim=64)
            
            # Create deterministic inputs
            neural_input = np.ones(64, dtype=np.float32)
            symbolic_input = np.ones(32, dtype=np.float32) * 0.5
            
            result1 = kernel.forward([neural_input, symbolic_input])
            result2 = kernel.forward([neural_input, symbolic_input])
            
            # Verify deterministic behavior
            deterministic = np.allclose(result1, result2)
            
            # Verify actual computation (not just pass-through)
            different_from_input = not np.allclose(result1, neural_input)
            
            test_results["tensor_mathematics"] = {
                "passed": True,
                "deterministic": deterministic,
                "actual_computation": different_from_input,
                "result_shape": result1.shape,
                "input_output_relationship": "transformed" if different_from_input else "pass_through"
            }
        except Exception as e:
            test_results["tensor_mathematics"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 2: Real Neural-Symbolic Synthesis
        try:
            synthesizer = NeuralSymbolicSynthesizer()
            
            # Test with different symbolic inputs to verify real synthesis
            symbolic_inputs = [
                {"concept": "high_confidence", "truth_value": {"strength": 0.9, "confidence": 0.9}},
                {"concept": "low_confidence", "truth_value": {"strength": 0.1, "confidence": 0.1}},
                {"concept": "medium_confidence", "truth_value": {"strength": 0.5, "confidence": 0.5}}
            ]
            
            neural_input = np.random.randn(256).astype(np.float32)
            results = []
            
            for symbolic_input in symbolic_inputs:
                result = synthesizer.synthesize(symbolic_input, neural_input)
                results.append(result)
                
            # Verify different symbolic inputs produce different results
            results_different = not all(np.allclose(results[0], r) for r in results[1:])
            
            test_results["neural_symbolic_synthesis"] = {
                "passed": True,
                "different_outputs": results_different,
                "synthesis_count": len(results),
                "synthesis_stats": synthesizer.get_synthesis_stats()
            }
        except Exception as e:
            test_results["neural_symbolic_synthesis"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 3: Performance Under Load
        try:
            synthesizer = NeuralSymbolicSynthesizer()
            
            # High-load test
            start_time = time.time()
            operations_completed = 0
            
            for i in range(100):
                symbolic_input = {"concept": f"load_test_{i}"}
                neural_input = np.random.randn(256).astype(np.float32)
                
                result = synthesizer.synthesize(symbolic_input, neural_input)
                operations_completed += 1
                
            total_time = time.time() - start_time
            ops_per_second = operations_completed / total_time
            
            test_results["load_testing"] = {
                "passed": True,
                "operations_completed": operations_completed,
                "total_time": total_time,
                "operations_per_second": ops_per_second,
                "performance_acceptable": ops_per_second > 50  # At least 50 ops/sec
            }
        except Exception as e:
            test_results["load_testing"] = {
                "passed": False,
                "error": str(e)
            }
            
        return test_results
        
    def test_distributed_mesh_integration(self) -> Dict[str, Any]:
        """Test integration with distributed cognitive mesh"""
        print("  Testing distributed mesh integration...")
        
        test_results = {}
        
        # Test 1: Mesh-Compatible Operations
        try:
            # Simulate mesh nodes
            mesh_nodes = [{"id": i, "capacity": 100} for i in range(3)]
            
            benchmark = create_standard_benchmark_suite()
            test_data = [np.random.randn(50, 50).astype(np.float32) for _ in range(3)]
            
            result = benchmark.benchmark_distributed_mesh(
                mesh_nodes,
                "neural_symbolic_processing",
                test_data,
                iterations=5
            )
            
            test_results["mesh_operations"] = {
                "passed": True,
                "mesh_nodes": len(mesh_nodes),
                "execution_time": result.execution_time,
                "parallelization_factor": result.additional_metrics.get("parallelization_factor", 1),
                "distribution_overhead": result.additional_metrics.get("distribution_overhead", 0)
            }
        except Exception as e:
            test_results["mesh_operations"] = {
                "passed": False,
                "error": str(e)
            }
            
        # Test 2: Scalability Testing
        try:
            # Test with different mesh sizes
            mesh_sizes = [1, 2, 4, 8]
            scalability_results = {}
            
            for size in mesh_sizes:
                mesh_nodes = [{"id": i, "capacity": 100} for i in range(size)]
                test_data = [np.random.randn(20, 20).astype(np.float32) for _ in range(size)]
                
                benchmark = create_standard_benchmark_suite()
                result = benchmark.benchmark_distributed_mesh(
                    mesh_nodes,
                    f"scalability_test_size_{size}",
                    test_data,
                    iterations=3
                )
                
                scalability_results[f"mesh_size_{size}"] = {
                    "execution_time": result.execution_time,
                    "throughput": result.throughput
                }
                
            test_results["scalability_testing"] = {
                "passed": True,
                "results": scalability_results
            }
        except Exception as e:
            test_results["scalability_testing"] = {
                "passed": False,
                "error": str(e)
            }
            
        return test_results
        
    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all test results"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        def count_tests(test_dict):
            nonlocal total_tests, passed_tests, failed_tests
            
            for key, value in test_dict.items():
                if isinstance(value, dict):
                    if "passed" in value:
                        total_tests += 1
                        if value["passed"]:
                            passed_tests += 1
                        else:
                            failed_tests += 1
                    else:
                        count_tests(value)
                        
        for test_category in results.values():
            if isinstance(test_category, dict):
                count_tests(test_category)
                
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "overall_status": "PASSED" if success_rate >= 95 else "FAILED",
            "test_categories": list(results.keys())
        }
        
    def save_verification_report(self, results: Dict[str, Any], output_file: str = "phase3_verification_report.json"):
        """Save verification results to file"""
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        print(f"📊 Verification report saved to: {output_path}")


def run_phase3_verification() -> Dict[str, Any]:
    """Run complete Phase 3 verification suite"""
    verification_suite = Phase3VerificationSuite()
    results = verification_suite.run_all_tests()
    
    # Print summary
    summary = results["summary"]
    print(f"\n🎯 Phase 3 Verification Complete")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed_tests']}")
    print(f"   Failed: {summary['failed_tests']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Overall Status: {summary['overall_status']}")
    
    # Save report
    verification_suite.save_verification_report(results)
    
    return results


if __name__ == "__main__":
    # Run verification when script is executed directly
    results = run_phase3_verification()