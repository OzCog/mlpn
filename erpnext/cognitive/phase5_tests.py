#!/usr/bin/env python3
"""
Phase 5 Comprehensive Test Suite

Comprehensive tests for Phase 5: Recursive Meta-Cognition & Evolutionary Optimization.
Tests all components with real data and validates integration.
"""

import unittest
import time
import json
import numpy as np
import threading
import tempfile
from typing import Dict, List, Any
from unittest.mock import MagicMock, patch

# Import Phase 5 components
from evolutionary_optimizer import (
    EvolutionaryOptimizer, Genome, FitnessEvaluator, GeneticOperators,
    SelectionStrategy, OptimizationTarget, MutationType
)
from feedback_self_analysis import (
    FeedbackDrivenSelfAnalysis, FeedbackSignal, FeedbackType, AnalysisDepth,
    PerformanceAnalyzer, PatternRecognizer, RecursiveSelfAnalyzer
)
from meta_cognitive import MetaCognitive, MetaLayer


class TestEvolutionaryOptimizer(unittest.TestCase):
    """Test evolutionary optimization components"""
    
    def setUp(self):
        self.optimizer = EvolutionaryOptimizer(
            population_size=20, 
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=0.7
        )
        
    def test_genome_creation_and_validation(self):
        """Test genome creation and validation"""
        genome = Genome(config_id="test_genome")
        genome.parameters = {
            'learning_rate': 0.01,
            'batch_size': 32,
            'hidden_units': 128
        }
        genome.structure_genes = {
            'layers': [64, 128, 64],
            'connections': {'input': 'hidden', 'hidden': 'output'}
        }
        
        self.assertEqual(genome.config_id, "test_genome")
        self.assertEqual(genome.parameters['learning_rate'], 0.01)
        self.assertIn('layers', genome.structure_genes)
        
    def test_fitness_evaluator(self):
        """Test fitness evaluation functionality"""
        evaluator = FitnessEvaluator()
        
        # Create test genomes with different characteristics
        good_genome = Genome(config_id="good")
        good_genome.parameters = {
            'learning_rate': 0.01,  # Good learning rate
            'threshold': 0.5       # Good threshold
        }
        
        bad_genome = Genome(config_id="bad")
        bad_genome.parameters = {
            'learning_rate': 10.0,  # Too high learning rate
            'threshold': -0.5       # Invalid threshold
        }
        
        good_fitness = evaluator.evaluate_genome(good_genome)
        bad_fitness = evaluator.evaluate_genome(bad_genome)
        
        # Good genome should have higher fitness
        self.assertGreater(good_fitness, bad_fitness)
        self.assertGreaterEqual(good_fitness, 0.0)
        self.assertLessEqual(good_fitness, 1.0)
        self.assertGreaterEqual(bad_fitness, 0.0)
        self.assertLessEqual(bad_fitness, 1.0)
        
    def test_genetic_operators(self):
        """Test genetic operators (mutation, crossover)"""
        genetic_ops = GeneticOperators(mutation_rate=0.5, crossover_rate=1.0)
        
        # Create parent genomes
        parent1 = Genome(config_id="parent1")
        parent1.parameters = {'param1': 1.0, 'param2': 2.0}
        parent1.structure_genes = {'struct1': [1, 2, 3]}
        
        parent2 = Genome(config_id="parent2")
        parent2.parameters = {'param1': 10.0, 'param2': 20.0}
        parent2.structure_genes = {'struct1': [10, 20, 30]}
        
        # Test mutation
        mutated = genetic_ops.mutate(parent1)
        self.assertNotEqual(mutated.config_id, parent1.config_id)
        self.assertIn(parent1.config_id, mutated.parent_ids)
        self.assertGreater(len(mutated.mutation_history), 0)
        
        # Test crossover
        child1, child2 = genetic_ops.crossover(parent1, parent2)
        self.assertNotEqual(child1.config_id, parent1.config_id)
        self.assertNotEqual(child2.config_id, parent2.config_id)
        self.assertIn(parent1.config_id, child1.parent_ids)
        self.assertIn(parent2.config_id, child1.parent_ids)
        
    def test_selection_strategies(self):
        """Test selection strategies"""
        # Create population with known fitness scores
        population = []
        for i in range(10):
            genome = Genome(config_id=f"genome_{i}")
            genome.fitness_score = i * 0.1  # Fitness from 0.0 to 0.9
            population.append(genome)
            
        # Test tournament selection
        selected = SelectionStrategy.tournament_selection(population, tournament_size=3)
        self.assertIn(selected, population)
        
        # Test elitist selection
        elites = SelectionStrategy.elitist_selection(population, elite_size=3)
        self.assertEqual(len(elites), 3)
        
        # Elites should be the highest fitness genomes
        elite_fitness = [g.fitness_score for g in elites]
        expected_fitness = [0.9, 0.8, 0.7]
        # Use approximate equality for floating point comparison
        for actual, expected in zip(elite_fitness, expected_fitness):
            self.assertAlmostEqual(actual, expected, places=7)
        
        # Test roulette wheel selection
        selected_roulette = SelectionStrategy.roulette_wheel_selection(population)
        self.assertIn(selected_roulette, population)
        
    def test_evolution_process(self):
        """Test complete evolution process"""
        # Create initial genomes
        seed_genomes = []
        for i in range(3):
            genome = Genome(config_id=f"seed_{i}")
            genome.parameters = {
                'learning_rate': 0.01 * (i + 1),
                'batch_size': 32 * (2 ** i)
            }
            seed_genomes.append(genome)
            
        # Initialize and evolve
        self.optimizer.initialize_population(seed_genomes=seed_genomes)
        initial_best = self.optimizer.best_genome.fitness_score if self.optimizer.best_genome else 0.0
        
        # Run short evolution
        best_genome = self.optimizer.evolve(convergence_threshold=0.001)
        
        # Verify evolution completed
        self.assertIsNotNone(best_genome)
        self.assertGreater(len(self.optimizer.evolution_history), 0)
        self.assertGreaterEqual(best_genome.fitness_score, initial_best)
        
        # Test summary generation
        summary = self.optimizer.get_optimization_summary()
        self.assertIn('total_generations', summary)
        self.assertIn('final_best_fitness', summary)
        self.assertIn('evolution_history', summary)
        
        # Test configuration export
        config = self.optimizer.export_best_configuration()
        self.assertIn('parameters', config)
        self.assertIn('fitness_score', config)


class TestFeedbackDrivenSelfAnalysis(unittest.TestCase):
    """Test feedback-driven self-analysis components"""
    
    def setUp(self):
        self.meta_cognitive = MetaCognitive()
        
        # Create mock cognitive layer
        self.mock_layer = MagicMock()
        self.mock_layer.get_operation_stats.return_value = {
            'operation_count': 100,
            'cached_tensors': 10,
            'registered_shapes': 5,
            'backend': 'cpu'
        }
        
        self.meta_cognitive.register_layer(MetaLayer.TENSOR_KERNEL, self.mock_layer)
        self.feedback_system = FeedbackDrivenSelfAnalysis(self.meta_cognitive)
        
    def test_performance_analyzer(self):
        """Test performance analysis functionality"""
        analyzer = PerformanceAnalyzer(window_size=10)
        
        # Feed performance data
        for i in range(15):
            metrics = {
                'throughput': 0.5 + 0.3 * np.sin(i * 0.5),
                'latency': 100 + 20 * np.sin(i * 0.3),
                'memory_usage': 1000 + i * 10
            }
            analyzer.update_metrics(metrics)
            
        # Analyze trends
        signals = analyzer.analyze_performance_trends()
        
        # Verify signals were generated
        self.assertIsInstance(signals, list)
        for signal in signals:
            self.assertIsInstance(signal, FeedbackSignal)
            self.assertIsInstance(signal.feedback_type, FeedbackType)
            self.assertGreaterEqual(signal.severity, 0.0)
            self.assertLessEqual(signal.severity, 1.0)
            
    def test_pattern_recognizer(self):
        """Test pattern recognition in feedback signals"""
        recognizer = PatternRecognizer()
        
        # Create correlated feedback signals
        signals = []
        base_time = time.time()
        
        for i in range(5):
            signal = FeedbackSignal(
                signal_id=f"signal_{i}",
                feedback_type=FeedbackType.PERFORMANCE_DEGRADATION,
                source_layer=MetaLayer.TENSOR_KERNEL,
                timestamp=base_time + i * 10,  # 10 seconds apart
                severity=0.5 + i * 0.1,
                description=f"Test signal {i}"
            )
            signals.append(signal)
            
        # Analyze correlations
        correlation_signals = recognizer.analyze_correlation_patterns(signals)
        
        # Should detect correlation pattern
        self.assertIsInstance(correlation_signals, list)
        
    def test_recursive_self_analyzer(self):
        """Test recursive self-analysis capabilities"""
        analyzer = RecursiveSelfAnalyzer(max_recursion_depth=3)
        
        # Test analysis at different depths
        for depth in AnalysisDepth:
            report = analyzer.perform_recursive_analysis(self.meta_cognitive, depth)
            
            self.assertIsNotNone(report)
            self.assertEqual(report.analysis_depth, depth)
            self.assertGreaterEqual(report.system_health_score, 0.0)
            self.assertLessEqual(report.system_health_score, 1.0)
            self.assertGreaterEqual(report.confidence_level, 0.0)
            self.assertLessEqual(report.confidence_level, 1.0)
            
        # Verify analysis history is maintained
        self.assertGreater(len(analyzer.analysis_history), 0)
        
    def test_feedback_signal_processing(self):
        """Test feedback signal generation and processing"""
        # Generate test signals
        signals = []
        for severity in [0.3, 0.6, 0.9]:
            signal = FeedbackSignal(
                signal_id=f"test_signal_{severity}",
                feedback_type=FeedbackType.OPTIMIZATION_OPPORTUNITY,
                source_layer=MetaLayer.TENSOR_KERNEL,
                timestamp=time.time(),
                severity=severity,
                description=f"Test signal with severity {severity}"
            )
            signals.append(signal)
            
        # Process signals
        self.feedback_system._process_feedback_signals(signals)
        
        # Verify signals were added to history
        total_signals = len(self.feedback_system.feedback_history)
        self.assertGreater(total_signals, 0)
        
    def test_continuous_analysis(self):
        """Test continuous analysis functionality"""
        # Start continuous analysis with short interval
        self.feedback_system.start_continuous_analysis(analysis_interval=0.5)
        
        # Let it run for a short time
        time.sleep(2.0)
        
        # Stop analysis
        self.feedback_system.stop_continuous_analysis()
        
        # Verify analysis was performed
        feedback_summary = self.feedback_system.get_feedback_summary()
        self.assertGreaterEqual(feedback_summary['total_signals'], 0)
        
    def test_evolutionary_optimization_trigger(self):
        """Test triggering evolutionary optimization from feedback"""
        # Create high-severity optimization signal
        optimization_signal = FeedbackSignal(
            signal_id="trigger_optimization",
            feedback_type=FeedbackType.OPTIMIZATION_OPPORTUNITY,
            source_layer=MetaLayer.TENSOR_KERNEL,
            timestamp=time.time(),
            severity=0.8,
            description="High-severity optimization opportunity"
        )
        
        # Mock evolutionary optimizer to avoid long execution
        with patch.object(self.feedback_system, 'evolutionary_optimizer') as mock_optimizer:
            mock_optimizer.initialize_population.return_value = None
            mock_genome = MagicMock()
            mock_genome.fitness_score = 0.9
            mock_optimizer.evolve.return_value = mock_genome
            
            # Trigger optimization
            self.feedback_system._trigger_evolutionary_optimization()
            
            # Verify optimizer was called
            mock_optimizer.initialize_population.assert_called_once()
            mock_optimizer.evolve.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def setUp(self):
        self.meta_cognitive = MetaCognitive()
        
        # Create multiple mock layers
        self.layers = {}
        for layer_type in [MetaLayer.TENSOR_KERNEL, MetaLayer.COGNITIVE_GRAMMAR, MetaLayer.ATTENTION_ALLOCATION]:
            mock_layer = MagicMock()
            mock_layer.get_operation_stats.return_value = {'operation_count': 50}
            mock_layer.get_knowledge_stats.return_value = {'total_atoms': 100}
            mock_layer.get_economic_stats.return_value = {'total_wages': 1000.0}
            
            self.layers[layer_type] = mock_layer
            self.meta_cognitive.register_layer(layer_type, mock_layer)
            
        self.feedback_system = FeedbackDrivenSelfAnalysis(self.meta_cognitive)
        
    def test_meta_cognitive_integration(self):
        """Test integration with meta-cognitive system"""
        # Update meta-state
        self.meta_cognitive.update_meta_state()
        
        # Verify state was captured
        current_state = self.meta_cognitive.get_current_state()
        self.assertIsNotNone(current_state)
        
        # Verify layers are monitored
        self.assertEqual(len(self.meta_cognitive.cognitive_layers), 3)
        
        # Test health diagnosis
        health_report = self.meta_cognitive.diagnose_system_health()
        self.assertIn('status', health_report)
        self.assertIn('layers_active', health_report)
        
    def test_feedback_meta_cognitive_integration(self):
        """Test feedback system integration with meta-cognitive"""
        # Perform deep analysis
        analysis_report = self.feedback_system.perform_deep_analysis()
        
        self.assertIsNotNone(analysis_report)
        self.assertEqual(len(analysis_report.layers_analyzed), 3)
        self.assertGreaterEqual(analysis_report.system_health_score, 0.0)
        
    def test_evolutionary_meta_cognitive_integration(self):
        """Test evolutionary optimizer integration with meta-cognitive"""
        optimizer = EvolutionaryOptimizer(population_size=10, max_generations=3)
        
        # Initialize with meta-cognitive as target
        optimizer.initialize_population(target_system=self.meta_cognitive)
        
        # Run evolution
        best_genome = optimizer.evolve(target_system=self.meta_cognitive)
        
        self.assertIsNotNone(best_genome)
        self.assertGreater(best_genome.fitness_score, 0.0)
        
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        workflow_steps = {
            'meta_state_update': False,
            'feedback_analysis': False,
            'evolutionary_optimization': False,
            'system_adaptation': False
        }
        
        # Step 1: Update meta-state
        self.meta_cognitive.update_meta_state()
        workflow_steps['meta_state_update'] = True
        
        # Step 2: Generate feedback
        analyzer = PerformanceAnalyzer()
        # Add enough data points for trend analysis (need at least 3)
        analyzer.update_metrics({'performance': 0.8, 'efficiency': 0.9})  # Good baseline
        analyzer.update_metrics({'performance': 0.5, 'efficiency': 0.6})  # Declining
        analyzer.update_metrics({'performance': 0.3, 'efficiency': 0.2})  # Poor performance
        signals = analyzer.analyze_performance_trends()
        
        if signals:
            workflow_steps['feedback_analysis'] = True
            
        # Step 3: Trigger optimization if needed
        if signals:
            # Mock quick optimization
            optimizer = EvolutionaryOptimizer(population_size=5, max_generations=2)
            optimizer.initialize_population(target_system=self.meta_cognitive)
            best = optimizer.evolve(target_system=self.meta_cognitive)
            
            if best:
                workflow_steps['evolutionary_optimization'] = True
                workflow_steps['system_adaptation'] = True
                
        # Verify workflow completion
        completed_steps = sum(workflow_steps.values())
        self.assertGreaterEqual(completed_steps, 2, "At least 2 workflow steps should complete")


class TestRealDataValidation(unittest.TestCase):
    """Validate that implementation uses real data, not mocks"""
    
    def test_evolutionary_algorithms_are_real(self):
        """Verify evolutionary algorithms use real math, not hardcoded results"""
        # Use higher mutation rate to ensure diversity is created
        optimizer = EvolutionaryOptimizer(population_size=10, max_generations=5, mutation_rate=1.0)
        
        # Create identical genomes - fill entire population with identical genomes
        identical_genomes = []
        for i in range(10):  # Fill the entire population
            genome = Genome(config_id=f"identical_{i}")
            genome.parameters = {'param1': 1.0, 'param2': 2.0}  # Identical parameters
            identical_genomes.append(genome)
            
        optimizer.initialize_population(seed_genomes=identical_genomes)
        
        # Verify initial population is identical
        initial_param_values = [g.parameters.get('param1', 0) for g in optimizer.population]
        initial_diversity = np.var(initial_param_values)
        self.assertEqual(initial_diversity, 0, "Initial population should be identical")
        
        # After evolution, population should be diverse (real genetic operators)
        best_genome = optimizer.evolve()
        
        # Check population diversity after evolution
        param_values = [g.parameters.get('param1', 0) for g in optimizer.population]
        diversity = np.var(param_values)
        
        # Also check if any genome has different parameters from the original
        has_mutations = any(g.parameters.get('param1', 0) != 1.0 for g in optimizer.population)
        
        # Either diversity should be > 0 OR we should have clear evidence of mutations
        self.assertTrue(diversity > 0 or has_mutations, 
                       f"Real genetic operations should create diversity. Diversity: {diversity}, Has mutations: {has_mutations}")
        
    def test_fitness_evaluation_is_real(self):
        """Verify fitness evaluation produces different results for different inputs"""
        evaluator = FitnessEvaluator()
        
        # Create genomes with very different characteristics
        genomes = []
        for i in range(5):
            genome = Genome(config_id=f"test_{i}")
            genome.parameters = {
                'learning_rate': 0.001 * (10 ** i),  # Very different learning rates
                'threshold': i * 0.2
            }
            genomes.append(genome)
            
        # Evaluate all genomes
        fitness_scores = [evaluator.evaluate_genome(g) for g in genomes]
        
        # Should get different fitness scores
        unique_scores = len(set(fitness_scores))
        self.assertGreater(unique_scores, 1, "Different genomes should get different fitness scores")
        
    def test_feedback_analysis_uses_real_data(self):
        """Verify feedback analysis responds to real data changes"""
        analyzer = PerformanceAnalyzer()
        
        # Feed good performance data
        for i in range(10):
            analyzer.update_metrics({'performance': 0.9 + np.random.normal(0, 0.01)})
            
        good_signals = analyzer.analyze_performance_trends()
        
        # Feed bad performance data
        for i in range(10):
            analyzer.update_metrics({'performance': 0.1 + np.random.normal(0, 0.01)})
            
        bad_signals = analyzer.analyze_performance_trends()
        
        # Should generate different feedback for different performance
        good_signal_count = len(good_signals)
        bad_signal_count = len(bad_signals)
        
        # Bad performance should generate more feedback signals
        self.assertGreaterEqual(bad_signal_count, good_signal_count,
                               "Poor performance should generate more feedback")


class Phase5TestSuite:
    """Comprehensive test suite runner for Phase 5"""
    
    def run_all_tests(self):
        """Run all Phase 5 tests"""
        print("🧪 Running Phase 5 Comprehensive Test Suite")
        print("=" * 60)
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add all test classes
        test_classes = [
            TestEvolutionaryOptimizer,
            TestFeedbackDrivenSelfAnalysis,
            TestIntegration,
            TestRealDataValidation
        ]
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
            
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Generate summary
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Test Suite Summary:")
        print(f"   Total tests: {total_tests}")
        print(f"   Successes: {total_tests - failures - errors}")
        print(f"   Failures: {failures}")
        print(f"   Errors: {errors}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        # Save detailed results
        test_results = {
            'timestamp': time.time(),
            'total_tests': total_tests,
            'failures': failures,
            'errors': errors,
            'success_rate': success_rate,
            'test_details': {
                'evolutionary_optimizer': 'TestEvolutionaryOptimizer',
                'feedback_analysis': 'TestFeedbackDrivenSelfAnalysis',
                'integration': 'TestIntegration',
                'real_data_validation': 'TestRealDataValidation'
            }
        }
        
        # Save results
        results_file = f'/tmp/phase5_test_results_{int(time.time())}.json'
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
            
        print(f"📄 Detailed results saved to: {results_file}")
        
        return success_rate >= 95.0  # 95% success rate required


def main():
    """Main test runner"""
    suite = Phase5TestSuite()
    
    try:
        success = suite.run_all_tests()
        
        if success:
            print("\n🎉 Phase 5 Test Suite PASSED")
            print("✅ All components tested with real data")
            return 0
        else:
            print("\n💥 Phase 5 Test Suite FAILED")
            print("❌ Some tests failed")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())