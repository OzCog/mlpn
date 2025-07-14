#!/usr/bin/env python3
"""
Phase 6: Living Documentation System
Maintains dynamic documentation that tracks code, tensors, tests, and evolution

This module implements a living documentation system that automatically tracks
changes, updates documentation, and maintains real-time awareness of the
cognitive architecture evolution.

Author: Cognitive Architecture Team
Date: 2024-07-14
Phase: 6 - Living Documentation & Real-time Tracking
"""

import os
import sys
import json
import hashlib
import time
import threading
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging
import watchdog.observers
import watchdog.events

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from documentation_generator import DocumentationGenerator, ModuleInfo, ArchitecturalDiagram

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CodeChangeEvent:
    """Represents a code change event"""
    file_path: str
    change_type: str  # 'modified', 'created', 'deleted'
    timestamp: datetime
    content_hash: str
    size_bytes: int
    
    
@dataclass
class TensorSignatureChange:
    """Represents a change in tensor signatures"""
    module_name: str
    function_name: str
    old_signature: Optional[str]
    new_signature: str
    timestamp: datetime
    impact_score: float


@dataclass
class TestCoverageEvent:
    """Represents a test coverage change"""
    module_name: str
    test_file: str
    coverage_delta: float
    test_count_delta: int
    timestamp: datetime


@dataclass
class EvolutionEvent:
    """Represents an evolutionary change in the architecture"""
    event_type: str  # 'module_added', 'module_removed', 'interface_changed', 'dependency_changed'
    description: str
    affected_modules: List[str]
    impact_level: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime
    metadata: Dict[str, Any]


class FileWatcher(watchdog.events.FileSystemEventHandler):
    """Watches for file system changes in the cognitive directory"""
    
    def __init__(self, living_docs: 'LivingDocumentationSystem'):
        self.living_docs = living_docs
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            self.living_docs.handle_file_change(event.src_path, 'modified')
            
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            self.living_docs.handle_file_change(event.src_path, 'created')
            
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            self.living_docs.handle_file_change(event.src_path, 'deleted')


class LivingDocumentationSystem:
    """Maintains living documentation with real-time tracking"""
    
    def __init__(self, cognitive_root: str = None, update_interval: int = 60):
        self.cognitive_root = cognitive_root or os.path.dirname(os.path.abspath(__file__))
        self.update_interval = update_interval
        
        # Initialize documentation generator
        self.doc_generator = DocumentationGenerator(self.cognitive_root)
        
        # Initialize tracking data
        self.code_changes = []
        self.tensor_changes = []
        self.test_coverage_changes = []
        self.evolution_events = []
        
        # File hashes for change detection
        self.file_hashes = {}
        
        # State tracking
        self.is_monitoring = False
        self.monitoring_thread = None
        self.file_observer = None
        
        # Callbacks for different events
        self.change_callbacks = {
            'code_change': [],
            'tensor_change': [],
            'test_change': [],
            'evolution_event': []
        }
        
    def start_monitoring(self):
        """Start real-time monitoring of the cognitive architecture"""
        logger.info("🔍 Starting living documentation monitoring...")
        
        if self.is_monitoring:
            logger.warning("⚠️ Monitoring already active")
            return
            
        self.is_monitoring = True
        
        # Initialize file system watcher
        self.file_observer = watchdog.observers.Observer()
        event_handler = FileWatcher(self)
        self.file_observer.schedule(event_handler, self.cognitive_root, recursive=True)
        self.file_observer.start()
        
        # Start periodic update thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        # Initial scan
        self._initial_scan()
        
        logger.info("✅ Living documentation monitoring started")
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        logger.info("🛑 Stopping living documentation monitoring...")
        
        self.is_monitoring = False
        
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            
        if self.monitoring_thread:
            self.monitoring_thread.join()
            
        logger.info("✅ Living documentation monitoring stopped")
        
    def _initial_scan(self):
        """Perform initial scan of all files"""
        logger.info("📊 Performing initial cognitive architecture scan...")
        
        # Scan all Python files and create initial hashes
        for root, dirs, files in os.walk(self.cognitive_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._update_file_hash(file_path)
                    
        # Generate initial documentation
        self.doc_generator.generate_all_documentation()
        
        # Track initial tensor signatures
        self._scan_tensor_signatures()
        
        # Track initial test coverage
        self._scan_test_coverage()
        
        logger.info("✅ Initial scan complete")
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Periodic update
                self._periodic_update()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(5)  # Brief pause before retry
                
    def _periodic_update(self):
        """Perform periodic updates"""
        logger.info("🔄 Performing periodic documentation update...")
        
        # Check for tensor signature changes
        self._scan_tensor_signatures()
        
        # Check for test coverage changes
        self._scan_test_coverage()
        
        # Update documentation
        self.doc_generator.generate_all_documentation()
        
        # Generate evolution summary
        self._generate_evolution_summary()
        
        logger.info("✅ Periodic update complete")
        
    def handle_file_change(self, file_path: str, change_type: str):
        """Handle a file change event"""
        logger.info(f"📝 File change detected: {change_type} - {os.path.basename(file_path)}")
        
        # Create change event
        if change_type != 'deleted':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content_hash = hashlib.md5(content.encode()).hexdigest()
                size_bytes = len(content.encode())
            except Exception as e:
                logger.error(f"❌ Error reading file {file_path}: {e}")
                return
        else:
            content_hash = "deleted"
            size_bytes = 0
            
        change_event = CodeChangeEvent(
            file_path=file_path,
            change_type=change_type,
            timestamp=datetime.now(),
            content_hash=content_hash,
            size_bytes=size_bytes
        )
        
        self.code_changes.append(change_event)
        
        # Update file hash
        if change_type != 'deleted':
            self._update_file_hash(file_path)
        elif file_path in self.file_hashes:
            del self.file_hashes[file_path]
            
        # Trigger callbacks
        self._trigger_callbacks('code_change', change_event)
        
        # Check for architectural impacts
        self._analyze_architectural_impact(change_event)
        
    def _update_file_hash(self, file_path: str):
        """Update hash for a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.file_hashes[file_path] = hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"⚠️ Could not hash file {file_path}: {e}")
            
    def _scan_tensor_signatures(self):
        """Scan for changes in tensor signatures"""
        tensor_modules = ['tensor_kernel', 'neural_symbolic_kernels', 'tensor_fragments']
        
        for module_name in tensor_modules:
            if module_name not in self.doc_generator.modules_info:
                continue
                
            module_info = self.doc_generator.modules_info[module_name]
            
            # Check functions for tensor-related signatures
            for func_name in module_info.functions:
                if 'tensor' in func_name.lower():
                    # Simple signature tracking (could be enhanced with AST analysis)
                    signature = f"{module_name}.{func_name}"
                    
                    # For now, just track that signature exists
                    # In a full implementation, would parse actual function signatures
                    change = TensorSignatureChange(
                        module_name=module_name,
                        function_name=func_name,
                        old_signature=None,
                        new_signature=signature,
                        timestamp=datetime.now(),
                        impact_score=0.5
                    )
                    
                    self.tensor_changes.append(change)
                    
    def _scan_test_coverage(self):
        """Scan for changes in test coverage"""
        for module_name, module_info in self.doc_generator.modules_info.items():
            if 'test' in module_name:
                # Track test file changes
                coverage_event = TestCoverageEvent(
                    module_name=module_name,
                    test_file=module_info.path,
                    coverage_delta=0.0,  # Would calculate actual delta
                    test_count_delta=len(module_info.functions),
                    timestamp=datetime.now()
                )
                
                self.test_coverage_changes.append(coverage_event)
                
    def _analyze_architectural_impact(self, change_event: CodeChangeEvent):
        """Analyze the architectural impact of a change"""
        file_name = os.path.basename(change_event.file_path)
        module_name = file_name[:-3] if file_name.endswith('.py') else file_name
        
        # Determine impact level
        impact_level = 'low'
        if 'test' in module_name:
            impact_level = 'low'
        elif module_name in ['tensor_kernel', 'cognitive_grammar', 'attention_allocation']:
            impact_level = 'high'
        elif 'phase' in module_name:
            impact_level = 'medium'
            
        # Create evolution event
        evolution_event = EvolutionEvent(
            event_type='module_modified',
            description=f"Module {module_name} was {change_event.change_type}",
            affected_modules=[module_name],
            impact_level=impact_level,
            timestamp=change_event.timestamp,
            metadata={
                'file_path': change_event.file_path,
                'content_hash': change_event.content_hash,
                'size_bytes': change_event.size_bytes
            }
        )
        
        self.evolution_events.append(evolution_event)
        self._trigger_callbacks('evolution_event', evolution_event)
        
    def _generate_evolution_summary(self):
        """Generate a summary of evolution events"""
        recent_events = [
            event for event in self.evolution_events
            if (datetime.now() - event.timestamp) < timedelta(hours=1)
        ]
        
        if recent_events:
            logger.info(f"📈 Recent evolution: {len(recent_events)} events in the last hour")
            for event in recent_events[-3:]:  # Last 3 events
                logger.info(f"  - {event.description} (impact: {event.impact_level})")
                
    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for specific event types"""
        if event_type in self.change_callbacks:
            self.change_callbacks[event_type].append(callback)
            logger.info(f"✅ Registered callback for {event_type}")
        else:
            logger.warning(f"⚠️ Unknown event type: {event_type}")
            
    def _trigger_callbacks(self, event_type: str, event_data: Any):
        """Trigger callbacks for an event type"""
        for callback in self.change_callbacks.get(event_type, []):
            try:
                callback(event_data)
            except Exception as e:
                logger.error(f"❌ Callback error for {event_type}: {e}")
                
    def get_living_documentation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive living documentation report"""
        return {
            'generation_timestamp': datetime.now().isoformat(),
            'monitoring_status': self.is_monitoring,
            'tracked_files': len(self.file_hashes),
            
            # Change statistics
            'code_changes': {
                'total_changes': len(self.code_changes),
                'recent_changes': len([
                    c for c in self.code_changes 
                    if (datetime.now() - c.timestamp) < timedelta(hours=24)
                ]),
                'change_types': {
                    'modified': len([c for c in self.code_changes if c.change_type == 'modified']),
                    'created': len([c for c in self.code_changes if c.change_type == 'created']),
                    'deleted': len([c for c in self.code_changes if c.change_type == 'deleted'])
                }
            },
            
            # Tensor evolution
            'tensor_evolution': {
                'signature_changes': len(self.tensor_changes),
                'modules_with_tensors': len(set(c.module_name for c in self.tensor_changes)),
                'recent_tensor_changes': len([
                    c for c in self.tensor_changes
                    if (datetime.now() - c.timestamp) < timedelta(hours=24)
                ])
            },
            
            # Test evolution
            'test_evolution': {
                'coverage_events': len(self.test_coverage_changes),
                'test_modules': len(set(c.module_name for c in self.test_coverage_changes)),
                'recent_test_changes': len([
                    c for c in self.test_coverage_changes
                    if (datetime.now() - c.timestamp) < timedelta(hours=24)
                ])
            },
            
            # Architecture evolution
            'architecture_evolution': {
                'total_events': len(self.evolution_events),
                'recent_events': len([
                    e for e in self.evolution_events
                    if (datetime.now() - e.timestamp) < timedelta(hours=24)
                ]),
                'impact_distribution': {
                    'low': len([e for e in self.evolution_events if e.impact_level == 'low']),
                    'medium': len([e for e in self.evolution_events if e.impact_level == 'medium']),
                    'high': len([e for e in self.evolution_events if e.impact_level == 'high']),
                    'critical': len([e for e in self.evolution_events if e.impact_level == 'critical'])
                }
            },
            
            # Current documentation state
            'documentation_state': self.doc_generator._create_documentation_report(),
            
            # Recent events (last 10)
            'recent_events': [
                {
                    'type': 'code_change',
                    'timestamp': event.timestamp.isoformat(),
                    'description': f"{event.change_type}: {os.path.basename(event.file_path)}"
                }
                for event in self.code_changes[-10:]
            ] + [
                {
                    'type': 'evolution_event',
                    'timestamp': event.timestamp.isoformat(),
                    'description': event.description,
                    'impact': event.impact_level
                }
                for event in self.evolution_events[-10:]
            ]
        }
        
    def save_living_documentation(self, output_path: str = None):
        """Save living documentation to file"""
        if not output_path:
            output_path = os.path.join(self.cognitive_root, 'living_documentation_report.json')
            
        report = self.get_living_documentation_report()
        
        # Convert datetime objects for JSON serialization
        def datetime_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=datetime_converter)
            
        logger.info(f"💾 Living documentation saved to {output_path}")
        
    def generate_markdown_report(self) -> str:
        """Generate a markdown report of the living documentation"""
        report = self.get_living_documentation_report()
        
        markdown = [
            "# Living Documentation Report",
            "",
            f"Generated: {report['generation_timestamp']}",
            f"Monitoring Status: {'🟢 Active' if report['monitoring_status'] else '🔴 Inactive'}",
            "",
            "## Summary",
            "",
            f"- **Tracked Files**: {report['tracked_files']}",
            f"- **Total Code Changes**: {report['code_changes']['total_changes']}",
            f"- **Recent Changes (24h)**: {report['code_changes']['recent_changes']}",
            f"- **Tensor Evolution Events**: {report['tensor_evolution']['signature_changes']}",
            f"- **Test Evolution Events**: {report['test_evolution']['coverage_events']}",
            f"- **Architecture Events**: {report['architecture_evolution']['total_events']}",
            "",
            "## Code Evolution",
            "",
            f"- Modified: {report['code_changes']['change_types']['modified']}",
            f"- Created: {report['code_changes']['change_types']['created']}",
            f"- Deleted: {report['code_changes']['change_types']['deleted']}",
            "",
            "## Architecture Impact Distribution",
            "",
            f"- Low Impact: {report['architecture_evolution']['impact_distribution']['low']}",
            f"- Medium Impact: {report['architecture_evolution']['impact_distribution']['medium']}",
            f"- High Impact: {report['architecture_evolution']['impact_distribution']['high']}",
            f"- Critical Impact: {report['architecture_evolution']['impact_distribution']['critical']}",
            "",
            "## Recent Activity",
            ""
        ]
        
        for event in report['recent_events'][-10:]:
            timestamp = event['timestamp'][:19]  # Remove microseconds
            if event['type'] == 'evolution_event':
                markdown.append(f"- **{timestamp}**: {event['description']} (Impact: {event['impact']})")
            else:
                markdown.append(f"- **{timestamp}**: {event['description']}")
                
        return "\n".join(markdown)


def main():
    """Main function for running living documentation system"""
    living_docs = LivingDocumentationSystem()
    
    # Start monitoring
    living_docs.start_monitoring()
    
    try:
        # Run for a short demo period
        logger.info("🚀 Living documentation system running...")
        time.sleep(10)  # Run for 10 seconds
        
        # Generate report
        report = living_docs.get_living_documentation_report()
        living_docs.save_living_documentation()
        
        # Generate markdown report
        markdown_report = living_docs.generate_markdown_report()
        markdown_path = os.path.join(living_docs.cognitive_root, 'living_documentation.md')
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
            
        print(f"\n📊 Living Documentation System Report")
        print(f"🔍 Monitoring Status: {'Active' if report['monitoring_status'] else 'Inactive'}")
        print(f"📁 Tracked Files: {report['tracked_files']}")
        print(f"📝 Code Changes: {report['code_changes']['total_changes']}")
        print(f"🧮 Tensor Evolution: {report['tensor_evolution']['signature_changes']}")
        print(f"🧪 Test Evolution: {report['test_evolution']['coverage_events']}")
        print(f"🏗️ Architecture Events: {report['architecture_evolution']['total_events']}")
        print(f"📄 Markdown Report: {markdown_path}")
        
    finally:
        # Stop monitoring
        living_docs.stop_monitoring()
        
    return living_docs


if __name__ == "__main__":
    main()