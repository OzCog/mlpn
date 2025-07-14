#!/usr/bin/env python3
"""
Phase 6: Recursive Documentation Generator
Auto-generates architectural flowcharts and maintains living documentation

This module implements automatic generation of architectural diagrams for every
module in the cognitive architecture, maintaining living documentation that
tracks code, tensors, tests, and evolution.

Author: Cognitive Architecture Team
Date: 2024-07-14
Phase: 6 - Recursive Documentation & Auto-Generation
"""

import os
import sys
import ast
import json
import inspect
import importlib
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ModuleInfo:
    """Information about a module for documentation generation"""
    name: str
    path: str
    classes: List[str]
    functions: List[str]
    dependencies: List[str]
    docstring: Optional[str]
    complexity_score: float
    test_coverage: float
    last_modified: datetime


@dataclass
class ArchitecturalDiagram:
    """Represents an architectural diagram for a module"""
    module_name: str
    diagram_type: str  # 'flowchart', 'class_diagram', 'dependency_graph'
    mermaid_content: str
    dependencies: List[str]
    components: List[str]
    timestamp: datetime


class DocumentationGenerator:
    """Auto-generates architectural flowcharts and living documentation"""
    
    def __init__(self, cognitive_root: str = None):
        self.cognitive_root = cognitive_root or os.path.dirname(os.path.abspath(__file__))
        self.modules_info = {}
        self.diagrams = {}
        self.living_docs = {
            'code_evolution': [],
            'tensor_signatures': {},
            'test_coverage': {},
            'architecture_changes': []
        }
        
    def scan_cognitive_modules(self) -> Dict[str, ModuleInfo]:
        """Scan all cognitive modules and extract information"""
        logger.info("🔍 Scanning cognitive modules for documentation generation...")
        
        modules_info = {}
        
        # Scan Python files in cognitive directory
        for root, dirs, files in os.walk(self.cognitive_root):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    module_name = file[:-3]  # Remove .py extension
                    
                    try:
                        module_info = self._analyze_module(file_path, module_name)
                        modules_info[module_name] = module_info
                        logger.info(f"✅ Analyzed module: {module_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to analyze {module_name}: {e}")
                        
        self.modules_info = modules_info
        logger.info(f"✅ Scanned {len(modules_info)} cognitive modules")
        return modules_info
        
    def _analyze_module(self, file_path: str, module_name: str) -> ModuleInfo:
        """Analyze a single module and extract information"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse AST to extract classes and functions
        tree = ast.parse(content)
        
        classes = []
        functions = []
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module)
                    
        # Extract module docstring
        docstring = ast.get_docstring(tree)
        
        # Calculate complexity score (simple heuristic)
        complexity_score = len(classes) * 2 + len(functions) + len(dependencies) * 0.5
        
        # Get file modification time
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        return ModuleInfo(
            name=module_name,
            path=file_path,
            classes=classes,
            functions=functions,
            dependencies=list(dependencies),
            docstring=docstring,
            complexity_score=complexity_score,
            test_coverage=self._calculate_test_coverage(module_name),
            last_modified=last_modified
        )
        
    def _calculate_test_coverage(self, module_name: str) -> float:
        """Calculate test coverage for a module"""
        # Simple heuristic: check if test file exists
        test_files = [
            f"{module_name}_test.py",
            f"test_{module_name}.py",
            f"{module_name}_tests.py"
        ]
        
        for test_file in test_files:
            test_path = os.path.join(self.cognitive_root, test_file)
            if os.path.exists(test_path):
                return 0.8  # Assume 80% coverage if test file exists
                
        return 0.0  # No test coverage
        
    def generate_flowchart_for_module(self, module_name: str) -> ArchitecturalDiagram:
        """Generate a flowchart diagram for a specific module"""
        if module_name not in self.modules_info:
            raise ValueError(f"Module {module_name} not found in scanned modules")
            
        module_info = self.modules_info[module_name]
        
        # Generate Mermaid flowchart
        mermaid_content = self._create_module_flowchart(module_info)
        
        diagram = ArchitecturalDiagram(
            module_name=module_name,
            diagram_type='flowchart',
            mermaid_content=mermaid_content,
            dependencies=module_info.dependencies,
            components=module_info.classes + module_info.functions,
            timestamp=datetime.now()
        )
        
        self.diagrams[module_name] = diagram
        logger.info(f"✅ Generated flowchart for module: {module_name}")
        return diagram
        
    def _create_module_flowchart(self, module_info: ModuleInfo) -> str:
        """Create Mermaid flowchart content for a module"""
        lines = [
            f"# {module_info.name} - Architectural Flowchart",
            "",
            "```mermaid",
            "graph TD",
            f"    M[{module_info.name}]",
            ""
        ]
        
        # Add classes
        if module_info.classes:
            lines.append("    subgraph \"Classes\"")
            for i, cls in enumerate(module_info.classes):
                lines.append(f"        C{i}[{cls}]")
            lines.append("    end")
            lines.append("")
            
            # Connect module to classes
            for i, cls in enumerate(module_info.classes):
                lines.append(f"    M --> C{i}")
        
        # Add functions
        if module_info.functions:
            lines.append("    subgraph \"Functions\"")
            for i, func in enumerate(module_info.functions):
                if not func.startswith('_'):  # Only public functions
                    lines.append(f"        F{i}[{func}]")
            lines.append("    end")
            lines.append("")
            
            # Connect module to functions
            for i, func in enumerate(module_info.functions):
                if not func.startswith('_'):
                    lines.append(f"    M --> F{i}")
        
        # Add dependencies
        if module_info.dependencies:
            lines.append("    subgraph \"Dependencies\"")
            for i, dep in enumerate(module_info.dependencies[:5]):  # Limit to top 5
                clean_dep = dep.split('.')[-1]  # Get last part of module name
                lines.append(f"        D{i}[{clean_dep}]")
            lines.append("    end")
            lines.append("")
            
            # Connect dependencies to module
            for i, dep in enumerate(module_info.dependencies[:5]):
                lines.append(f"    D{i} --> M")
        
        lines.extend(["```", ""])
        
        return "\n".join(lines)
        
    def generate_dependency_graph(self) -> ArchitecturalDiagram:
        """Generate a dependency graph for all cognitive modules"""
        logger.info("🕸️ Generating cognitive architecture dependency graph...")
        
        mermaid_content = self._create_dependency_graph()
        
        all_modules = list(self.modules_info.keys())
        all_dependencies = set()
        for module_info in self.modules_info.values():
            all_dependencies.update(module_info.dependencies)
        
        diagram = ArchitecturalDiagram(
            module_name='cognitive_architecture',
            diagram_type='dependency_graph',
            mermaid_content=mermaid_content,
            dependencies=list(all_dependencies),
            components=all_modules,
            timestamp=datetime.now()
        )
        
        self.diagrams['cognitive_architecture'] = diagram
        logger.info("✅ Generated cognitive architecture dependency graph")
        return diagram
        
    def _create_dependency_graph(self) -> str:
        """Create dependency graph content"""
        lines = [
            "# Cognitive Architecture - Dependency Graph",
            "",
            "```mermaid",
            "graph TB",
            ""
        ]
        
        # Core cognitive modules
        core_modules = [
            'tensor_kernel', 'cognitive_grammar', 'attention_allocation',
            'meta_cognitive', 'evolutionary_optimizer', 'feedback_self_analysis'
        ]
        
        # Add core modules
        lines.append("    subgraph \"Core Cognitive Architecture\"")
        for module in core_modules:
            if module in self.modules_info:
                lines.append(f"        {module.upper()}[{module}]")
        lines.append("    end")
        lines.append("")
        
        # Add testing modules
        test_modules = [name for name in self.modules_info.keys() if 'test' in name or 'phase' in name]
        if test_modules:
            lines.append("    subgraph \"Testing & Validation\"")
            for module in test_modules[:5]:  # Limit to top 5
                lines.append(f"        {module.upper().replace('-', '_')}[{module}]")
            lines.append("    end")
            lines.append("")
        
        # Add dependencies between core modules
        dependencies = [
            ('TENSOR_KERNEL', 'COGNITIVE_GRAMMAR'),
            ('COGNITIVE_GRAMMAR', 'ATTENTION_ALLOCATION'),
            ('ATTENTION_ALLOCATION', 'META_COGNITIVE'),
            ('META_COGNITIVE', 'EVOLUTIONARY_OPTIMIZER'),
            ('EVOLUTIONARY_OPTIMIZER', 'FEEDBACK_SELF_ANALYSIS'),
            ('FEEDBACK_SELF_ANALYSIS', 'TENSOR_KERNEL')  # Feedback loop
        ]
        
        for src, dst in dependencies:
            if src in [m.upper() for m in core_modules] and dst in [m.upper() for m in core_modules]:
                lines.append(f"    {src} --> {dst}")
        
        lines.extend(["```", ""])
        
        return "\n".join(lines)
        
    def generate_class_diagram_for_module(self, module_name: str) -> ArchitecturalDiagram:
        """Generate a class diagram for a specific module"""
        if module_name not in self.modules_info:
            raise ValueError(f"Module {module_name} not found")
            
        module_info = self.modules_info[module_name]
        
        # Generate Mermaid class diagram
        mermaid_content = self._create_class_diagram(module_info)
        
        diagram = ArchitecturalDiagram(
            module_name=module_name,
            diagram_type='class_diagram',
            mermaid_content=mermaid_content,
            dependencies=module_info.dependencies,
            components=module_info.classes,
            timestamp=datetime.now()
        )
        
        self.diagrams[f"{module_name}_classes"] = diagram
        logger.info(f"✅ Generated class diagram for module: {module_name}")
        return diagram
        
    def _create_class_diagram(self, module_info: ModuleInfo) -> str:
        """Create class diagram content"""
        lines = [
            f"# {module_info.name} - Class Diagram",
            "",
            "```mermaid",
            "classDiagram",
            ""
        ]
        
        if not module_info.classes:
            lines.extend([
                f"    class {module_info.name} {{",
                "        +functions()",
                "    }",
                "```",
                ""
            ])
            return "\n".join(lines)
        
        # Add classes
        for cls in module_info.classes:
            lines.extend([
                f"    class {cls} {{",
                "        +methods()",
                "        +attributes",
                "    }",
                ""
            ])
        
        # Add relationships (simple inheritance detection)
        for i, cls in enumerate(module_info.classes):
            if i > 0:  # Simple heuristic: assume some inheritance
                lines.append(f"    {module_info.classes[0]} <|-- {cls}")
        
        lines.extend(["```", ""])
        
        return "\n".join(lines)
        
    def update_living_documentation(self) -> Dict[str, Any]:
        """Update living documentation with current state"""
        logger.info("📚 Updating living documentation...")
        
        # Update code evolution tracking
        self.living_docs['code_evolution'].append({
            'timestamp': datetime.now().isoformat(),
            'modules_count': len(self.modules_info),
            'total_classes': sum(len(info.classes) for info in self.modules_info.values()),
            'total_functions': sum(len(info.functions) for info in self.modules_info.values()),
            'average_complexity': sum(info.complexity_score for info in self.modules_info.values()) / len(self.modules_info) if self.modules_info else 0
        })
        
        # Update tensor signatures tracking
        self._update_tensor_signatures()
        
        # Update test coverage tracking
        self._update_test_coverage()
        
        # Update architecture changes
        self._track_architecture_changes()
        
        logger.info("✅ Living documentation updated")
        return self.living_docs
        
    def _update_tensor_signatures(self):
        """Update tensor signatures documentation"""
        # Track tensor-related modules
        tensor_modules = [name for name in self.modules_info.keys() if 'tensor' in name.lower()]
        
        for module_name in tensor_modules:
            module_info = self.modules_info[module_name]
            self.living_docs['tensor_signatures'][module_name] = {
                'classes': module_info.classes,
                'functions': [f for f in module_info.functions if 'tensor' in f.lower()],
                'last_modified': module_info.last_modified.isoformat()
            }
            
    def _update_test_coverage(self):
        """Update test coverage tracking"""
        for module_name, module_info in self.modules_info.items():
            self.living_docs['test_coverage'][module_name] = {
                'coverage': module_info.test_coverage,
                'has_tests': module_info.test_coverage > 0,
                'last_updated': datetime.now().isoformat()
            }
            
    def _track_architecture_changes(self):
        """Track architecture changes over time"""
        # Simple change tracking based on modification times
        recent_changes = []
        
        for module_name, module_info in self.modules_info.items():
            # Consider changes in last 24 hours as recent
            if (datetime.now() - module_info.last_modified).days == 0:
                recent_changes.append({
                    'module': module_name,
                    'last_modified': module_info.last_modified.isoformat(),
                    'complexity_score': module_info.complexity_score
                })
        
        if recent_changes:
            self.living_docs['architecture_changes'].append({
                'timestamp': datetime.now().isoformat(),
                'changes': recent_changes
            })
            
    def generate_all_documentation(self) -> Dict[str, Any]:
        """Generate all documentation artifacts"""
        logger.info("🚀 Generating all documentation artifacts...")
        
        # Scan modules
        self.scan_cognitive_modules()
        
        # Generate diagrams for all modules
        for module_name in self.modules_info.keys():
            try:
                self.generate_flowchart_for_module(module_name)
                if self.modules_info[module_name].classes:
                    self.generate_class_diagram_for_module(module_name)
            except Exception as e:
                logger.warning(f"⚠️ Failed to generate diagrams for {module_name}: {e}")
        
        # Generate dependency graph
        self.generate_dependency_graph()
        
        # Update living documentation
        self.update_living_documentation()
        
        # Save all documentation
        docs_report = self._create_documentation_report()
        
        logger.info("✅ All documentation artifacts generated")
        return docs_report
        
    def _create_documentation_report(self) -> Dict[str, Any]:
        """Create comprehensive documentation report"""
        return {
            'generation_timestamp': datetime.now().isoformat(),
            'modules_analyzed': len(self.modules_info),
            'diagrams_generated': len(self.diagrams),
            'modules_info': {name: asdict(info) for name, info in self.modules_info.items()},
            'architectural_diagrams': {name: asdict(diagram) for name, diagram in self.diagrams.items()},
            'living_documentation': self.living_docs,
            'documentation_completeness': self._calculate_documentation_completeness()
        }
        
    def _calculate_documentation_completeness(self) -> Dict[str, float]:
        """Calculate documentation completeness metrics"""
        total_modules = len(self.modules_info)
        
        if total_modules == 0:
            return {'overall': 0.0}
        
        # Calculate various completeness metrics
        modules_with_docstrings = sum(1 for info in self.modules_info.values() if info.docstring)
        modules_with_tests = sum(1 for info in self.modules_info.values() if info.test_coverage > 0)
        modules_with_diagrams = len(self.diagrams)
        
        return {
            'overall': (modules_with_docstrings + modules_with_tests + modules_with_diagrams) / (total_modules * 3),
            'docstring_coverage': modules_with_docstrings / total_modules,
            'test_coverage': modules_with_tests / total_modules,
            'diagram_coverage': modules_with_diagrams / total_modules
        }
        
    def save_documentation_to_files(self, output_dir: str = None):
        """Save generated documentation to files"""
        if not output_dir:
            output_dir = os.path.join(self.cognitive_root, '..', '..', 'docs', 'generated')
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual module diagrams
        for diagram_name, diagram in self.diagrams.items():
            filename = f"{diagram_name}_{diagram.diagram_type}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(diagram.mermaid_content)
                
        # Save comprehensive report
        report = self._create_documentation_report()
        report_path = os.path.join(output_dir, 'documentation_report.json')
        
        # Convert datetime objects to strings for JSON serialization
        def datetime_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=datetime_converter)
            
        logger.info(f"✅ Documentation saved to {output_dir}")


def main():
    """Main function for running documentation generation"""
    generator = DocumentationGenerator()
    
    # Generate all documentation
    report = generator.generate_all_documentation()
    
    # Save to files
    generator.save_documentation_to_files()
    
    # Print summary
    print(f"\n🎉 Documentation Generation Complete!")
    print(f"📊 Modules analyzed: {report['modules_analyzed']}")
    print(f"📈 Diagrams generated: {report['diagrams_generated']}")
    print(f"📋 Documentation completeness: {report['documentation_completeness']['overall']:.1%}")
    
    return report


if __name__ == "__main__":
    main()