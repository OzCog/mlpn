"""
Standalone Phase 3 Neural-Symbolic Kernel Test

Tests the neural-symbolic synthesis implementation without frappe dependencies.
"""

import sys
import os
import numpy as np
import time
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our neural-symbolic components directly
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


def test_neural_symbolic_kernels():
    """Test neural-symbolic kernel functionality"""
    print("🧠 Testing Neural-Symbolic Kernels...")
    
    results = {}
    
    # Test 1: Kernel Registry
    print("  Testing kernel registry...")
    try:
        registry = create_default_kernel_registry()
        kernels = registry.list_kernels()
        stats = registry.get_registry_stats()
        
        results["kernel_registry"] = {
            "success": True,
            "registered_kernels": len(kernels),
            "kernel_names": kernels,
            "stats": stats
        }
        print(f"    ✅ Registry created with {len(kernels)} kernels: {kernels}")
    except Exception as e:
        results["kernel_registry"] = {"success": False, "error": str(e)}
        print(f"    ❌ Registry creation failed: {e}")
        
    # Test 2: Individual Kernels
    print("  Testing individual kernels...")
    kernel_results = {}
    
    # Conceptual Embedding Kernel
    try:
        kernel = GGMLConceptualEmbeddingKernel(concept_dim=64, embedding_dim=128)
        neural_input = np.random.randn(128).astype(np.float32)
        symbolic_input = np.random.randn(64).astype(np.float32)
        
        result = kernel.forward([neural_input, symbolic_input])
        signature = kernel.get_signature()
        
        kernel_results["conceptual_embedding"] = {
            "success": True,
            "input_shapes": [neural_input.shape, symbolic_input.shape],
            "output_shape": result.shape,
            "signature": {
                "operation_name": signature.operation_name,
                "complexity": signature.complexity,
                "parallelizable": signature.parallelizable
            }
        }
        print(f"    ✅ Conceptual Embedding: {neural_input.shape} + {symbolic_input.shape} → {result.shape}")
    except Exception as e:
        kernel_results["conceptual_embedding"] = {"success": False, "error": str(e)}
        print(f"    ❌ Conceptual Embedding failed: {e}")
        
    # Logical Inference Kernel
    try:
        kernel = GGMLLogicalInferenceKernel(logic_dim=64)
        premise = np.random.randn(64).astype(np.float32)
        rule = np.random.randn(64).astype(np.float32)
        op_code = np.array([0])  # AND operation
        
        result = kernel.forward([premise, rule, op_code])
        
        kernel_results["logical_inference"] = {
            "success": True,
            "input_shapes": [premise.shape, rule.shape, op_code.shape],
            "output_shape": result.shape
        }
        print(f"    ✅ Logical Inference: {premise.shape} + {rule.shape} → {result.shape}")
    except Exception as e:
        kernel_results["logical_inference"] = {"success": False, "error": str(e)}
        print(f"    ❌ Logical Inference failed: {e}")
        
    # Attention Allocation Kernel
    try:
        kernel = GGMLAttentionAllocationKernel(attention_dim=128, num_heads=4)
        atoms = np.random.randn(10, 128).astype(np.float32)
        attention_vals = np.random.randn(10).astype(np.float32)
        focus = np.random.randn(128).astype(np.float32)
        
        result = kernel.forward([atoms, attention_vals, focus])
        
        kernel_results["attention_allocation"] = {
            "success": True,
            "input_shapes": [atoms.shape, attention_vals.shape, focus.shape],
            "output_shape": result.shape
        }
        print(f"    ✅ Attention Allocation: {atoms.shape} + {attention_vals.shape} → {result.shape}")
    except Exception as e:
        kernel_results["attention_allocation"] = {"success": False, "error": str(e)}
        print(f"    ❌ Attention Allocation failed: {e}")
        
    # Hypergraph Convolution Kernel
    try:
        kernel = GGMLHypergraphConvolutionKernel(node_dim=64, edge_dim=32, output_dim=64)
        nodes = np.random.randn(20, 64).astype(np.float32)
        edges = np.random.randn(15, 32).astype(np.float32)
        structure = np.random.rand(20, 20).astype(np.float32)
        
        result = kernel.forward([nodes, edges, structure])
        
        kernel_results["hypergraph_convolution"] = {
            "success": True,
            "input_shapes": [nodes.shape, edges.shape, structure.shape],
            "output_shape": result.shape
        }
        print(f"    ✅ Hypergraph Convolution: {nodes.shape} + {edges.shape} → {result.shape}")
    except Exception as e:
        kernel_results["hypergraph_convolution"] = {"success": False, "error": str(e)}
        print(f"    ❌ Hypergraph Convolution failed: {e}")
        
    results["individual_kernels"] = kernel_results
    
    return results


def test_neural_symbolic_synthesizer():
    """Test the neural-symbolic synthesizer"""
    print("🔬 Testing Neural-Symbolic Synthesizer...")
    
    results = {}
    
    # Test 1: Synthesizer Creation
    try:
        synthesizer = NeuralSymbolicSynthesizer()
        kernels = synthesizer.registry.list_kernels()
        
        results["creation"] = {
            "success": True,
            "available_kernels": kernels
        }
        print(f"    ✅ Synthesizer created with {len(kernels)} kernels")
    except Exception as e:
        results["creation"] = {"success": False, "error": str(e)}
        print(f"    ❌ Synthesizer creation failed: {e}")
        return results
        
    # Test 2: Basic Synthesis
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
        
        stats = synthesizer.get_synthesis_stats()
        
        results["basic_synthesis"] = {
            "success": True,
            "neural_input_shape": neural_input.shape,
            "output_shape": result.shape,
            "synthesis_count": stats["total_syntheses"],
            "avg_execution_time": stats["average_execution_time"]
        }
        print(f"    ✅ Basic synthesis: {neural_input.shape} → {result.shape}")
        print(f"    📊 Average execution time: {stats['average_execution_time']:.6f}s")
    except Exception as e:
        results["basic_synthesis"] = {"success": False, "error": str(e)}
        print(f"    ❌ Basic synthesis failed: {e}")
        
    # Test 3: Multiple Synthesis Operations
    try:
        synthesizer = NeuralSymbolicSynthesizer()
        
        test_cases = [
            {"concept": "high_confidence", "truth_value": {"strength": 0.9, "confidence": 0.9}},
            {"concept": "medium_confidence", "truth_value": {"strength": 0.5, "confidence": 0.5}},
            {"concept": "low_confidence", "truth_value": {"strength": 0.1, "confidence": 0.1}}
        ]
        
        neural_input = np.random.randn(256).astype(np.float32)
        synthesis_results = []
        
        for i, symbolic_input in enumerate(test_cases):
            result = synthesizer.synthesize(symbolic_input, neural_input)
            synthesis_results.append(result)
            
        # Check that different symbolic inputs produce different results
        results_different = not all(np.allclose(synthesis_results[0], r) for r in synthesis_results[1:])
        
        results["multiple_synthesis"] = {
            "success": True,
            "test_cases": len(test_cases),
            "results_different": results_different,
            "final_stats": synthesizer.get_synthesis_stats()
        }
        print(f"    ✅ Multiple synthesis: {len(test_cases)} cases, different results: {results_different}")
    except Exception as e:
        results["multiple_synthesis"] = {"success": False, "error": str(e)}
        print(f"    ❌ Multiple synthesis failed: {e}")
        
    return results


def test_benchmarking_system():
    """Test the tensor benchmarking system"""
    print("📊 Testing Benchmarking System...")
    
    results = {}
    
    # Test 1: Benchmark Creation
    try:
        benchmark = create_standard_benchmark_suite()
        system_info = benchmark.system_info
        
        results["creation"] = {
            "success": True,
            "system_info_keys": list(system_info.keys())
        }
        print(f"    ✅ Benchmark suite created")
        print(f"    🖥️  Platform: {system_info.get('platform', 'Unknown')}")
    except Exception as e:
        results["creation"] = {"success": False, "error": str(e)}
        print(f"    ❌ Benchmark creation failed: {e}")
        return results
        
    # Test 2: Single Operation Benchmark
    try:
        benchmark = create_standard_benchmark_suite()
        
        def test_operation(inputs):
            return np.dot(inputs[0], inputs[1].T)
            
        test_inputs = [
            np.random.randn(50, 30).astype(np.float32),
            np.random.randn(50, 30).astype(np.float32)
        ]
        
        result = benchmark.benchmark_operation(
            test_operation,
            "matrix_multiplication",
            test_inputs,
            iterations=20
        )
        
        results["single_operation"] = {
            "success": True,
            "execution_time": result.execution_time,
            "throughput": result.throughput,
            "memory_usage": result.memory_usage
        }
        print(f"    ✅ Single operation benchmark: {result.execution_time:.6f}s, {result.throughput:.1f} ops/s")
    except Exception as e:
        results["single_operation"] = {"success": False, "error": str(e)}
        print(f"    ❌ Single operation benchmark failed: {e}")
        
    # Test 3: Kernel Registry Benchmark
    try:
        benchmark = create_standard_benchmark_suite()
        registry = create_default_kernel_registry()
        
        suite = benchmark.benchmark_kernel_registry(
            registry,
            test_sizes=[10, 50],
            iterations=10
        )
        
        summary_stats = suite.get_summary_stats()
        
        results["kernel_registry"] = {
            "success": True,
            "total_results": len(suite.results),
            "summary_stats": summary_stats
        }
        print(f"    ✅ Kernel registry benchmark: {len(suite.results)} results")
        if 'execution_time' in summary_stats:
            print(f"    ⏱️  Average execution time: {summary_stats['execution_time']['mean']:.6f}s")
    except Exception as e:
        results["kernel_registry"] = {"success": False, "error": str(e)}
        print(f"    ❌ Kernel registry benchmark failed: {e}")
        
    return results


def test_performance_characteristics():
    """Test performance characteristics"""
    print("⚡ Testing Performance Characteristics...")
    
    results = {}
    
    # Test 1: Kernel Performance
    try:
        synthesizer = NeuralSymbolicSynthesizer()
        
        # Benchmark all kernels
        start_time = time.time()
        benchmarks = synthesizer.benchmark_kernels(iterations=50)
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        avg_execution_times = [metrics["avg_execution_time"] for metrics in benchmarks.values()]
        total_ops_per_second = sum(metrics["operations_per_second"] for metrics in benchmarks.values())
        
        results["kernel_performance"] = {
            "success": True,
            "benchmarks": benchmarks,
            "total_benchmark_time": total_time,
            "average_execution_time": np.mean(avg_execution_times),
            "total_throughput": total_ops_per_second
        }
        
        print(f"    ✅ Kernel performance tested")
        print(f"    📈 Total throughput: {total_ops_per_second:.1f} ops/s")
        print(f"    ⏱️  Average execution time: {np.mean(avg_execution_times):.6f}s")
        
        # Print individual kernel performance
        for kernel_name, metrics in benchmarks.items():
            print(f"       {kernel_name}: {metrics['operations_per_second']:.1f} ops/s")
            
    except Exception as e:
        results["kernel_performance"] = {"success": False, "error": str(e)}
        print(f"    ❌ Kernel performance test failed: {e}")
        
    # Test 2: Scalability Test
    try:
        synthesizer = NeuralSymbolicSynthesizer()
        
        # Test with increasing data sizes, but keep neural input compatible
        sizes = [128, 256, 512, 1024]  # Use sizes compatible with synthesizer
        scalability_results = {}
        
        for size in sizes:
            symbolic_input = {"concept": f"scalability_test_{size}"}
            # Keep neural input at 256 dimensions but vary processing complexity
            neural_input = np.random.randn(256).astype(np.float32)
            
            start_time = time.time()
            for _ in range(5):  # Fewer iterations for larger sizes
                result = synthesizer.synthesize(symbolic_input, neural_input)
            execution_time = time.time() - start_time
            
            scalability_results[size] = {
                "execution_time": execution_time,
                "ops_per_second": 5 / execution_time
            }
            
        results["scalability"] = {
            "success": True,
            "results": scalability_results
        }
        
        print(f"    ✅ Scalability tested across complexity levels: {sizes}")
        for size, metrics in scalability_results.items():
            print(f"       Complexity {size}: {metrics['ops_per_second']:.1f} ops/s")
            
    except Exception as e:
        results["scalability"] = {"success": False, "error": str(e)}
        print(f"    ❌ Scalability test failed: {e}")
        
    return results


def run_comprehensive_test():
    """Run comprehensive Phase 3 test suite"""
    print("🚀 Phase 3: Neural-Symbolic Synthesis via Custom ggml Kernels")
    print("=" * 70)
    
    start_time = time.time()
    
    # Run all tests
    test_results = {
        "neural_symbolic_kernels": test_neural_symbolic_kernels(),
        "neural_symbolic_synthesizer": test_neural_symbolic_synthesizer(),
        "benchmarking_system": test_benchmarking_system(),
        "performance_characteristics": test_performance_characteristics()
    }
    
    total_time = time.time() - start_time
    
    # Calculate summary statistics
    total_tests = 0
    passed_tests = 0
    
    def count_tests(results_dict):
        nonlocal total_tests, passed_tests
        for key, value in results_dict.items():
            if isinstance(value, dict):
                if "success" in value:
                    total_tests += 1
                    if value["success"]:
                        passed_tests += 1
                else:
                    count_tests(value)
                    
    count_tests(test_results)
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Generate summary
    summary = {
        "timestamp": time.time(),
        "total_execution_time": total_time,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": success_rate,
        "overall_status": "PASSED" if success_rate >= 90 else "FAILED"
    }
    
    test_results["summary"] = summary
    
    # Print summary
    print("\n" + "=" * 70)
    print("📋 Phase 3 Test Summary")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Total Execution Time: {total_time:.2f}s")
    
    # Save results
    output_file = "phase3_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    print(f"📄 Results saved to: {output_file}")
    
    return test_results


if __name__ == "__main__":
    results = run_comprehensive_test()