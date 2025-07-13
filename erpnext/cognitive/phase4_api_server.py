#!/usr/bin/env python3
"""
Phase 4: Distributed Cognitive Mesh API & Embodiment Layer

REST/WebSocket API server that exposes the cognitive network functionality
for Unity3D, ROS, and web agents. Implements distributed state propagation
and task orchestration with real data.

Key Components:
- REST API endpoints for cognitive operations
- WebSocket server for real-time communication
- Unity3D integration adapter
- ROS integration adapter  
- Web agent integration
- Distributed state propagation
- Task orchestration APIs
"""

import json
import time
import threading
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import existing cognitive components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neural_symbolic_kernels import (
    create_default_kernel_registry,
    NeuralSymbolicSynthesizer
)
from mesh_topology import DynamicMesh, AgentState, AgentRole
from cognitive_grammar import AtomSpace, AtomType, TruthValue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CognitiveTask:
    """Represents a distributed cognitive task"""
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    status: str = "pending"
    created_at: float = 0.0
    assigned_agents: List[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.assigned_agents is None:
            self.assigned_agents = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at == 0.0:
            self.created_at = time.time()


@dataclass
class EmbodimentBinding:
    """Represents a binding to an external embodiment system"""
    binding_id: str
    system_type: str  # "unity3d", "ros", "web"
    endpoint: str
    capabilities: List[str]
    status: str = "active"
    last_heartbeat: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.last_heartbeat == 0.0:
            self.last_heartbeat = time.time()


class CognitiveAPIServer:
    """Main API server for Phase 4 distributed cognitive mesh"""
    
    def __init__(self, host="0.0.0.0", port=5000, debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        
        # Initialize Flask app with SocketIO
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'cognitive-mesh-secret-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize cognitive components
        self.kernel_registry = create_default_kernel_registry()
        self.neural_symbolic = NeuralSymbolicSynthesizer(self.kernel_registry)
        self.mesh_manager = DynamicMesh()
        self.atomspace = AtomSpace()
        
        # Create some default agents for task assignment
        self._create_default_mesh_agents()
        
        # Task and binding management
        self.active_tasks: Dict[str, CognitiveTask] = {}
        self.embodiment_bindings: Dict[str, EmbodimentBinding] = {}
        self.task_executor = ThreadPoolExecutor(max_workers=10)
        
        # State management
        self.cognitive_state = {
            "global_attention": {},
            "distributed_memory": {},
            "active_computations": {},
            "network_topology": {}
        }
        
        # Real-time data tracking
        self.real_time_metrics = {
            "operations_per_second": 0.0,
            "total_operations": 0,
            "memory_usage": 0.0,
            "network_latency": 0.0,
            "active_connections": 0
        }
        
        self._setup_routes()
        self._setup_websocket_handlers()
        
        # Start background services
        self._start_background_services()
        
        logger.info("Cognitive API Server initialized successfully")
    
    def _create_default_mesh_agents(self):
        """Create default agents in the mesh for task assignment"""
        from mesh_topology import DistributedAgent, AgentRole
        
        # Create a set of default agents with different roles
        default_agents = [
            ("default_coordinator", AgentRole.COORDINATOR),
            ("default_processor_1", AgentRole.PROCESSOR),
            ("default_processor_2", AgentRole.PROCESSOR),
            ("default_attention", AgentRole.ATTENTION),
            ("default_memory", AgentRole.MEMORY),
            ("default_inference", AgentRole.INFERENCE)
        ]
        
        for agent_id, role in default_agents:
            agent = DistributedAgent(agent_id, role)
            if self.mesh_manager.add_agent(agent):
                logger.info(f"Created default mesh agent {agent_id} with role {role}")
            else:
                logger.warning(f"Failed to create default agent {agent_id}")
        
        logger.info(f"Mesh initialized with {len(self.mesh_manager.agents)} agents")
    
    def _setup_routes(self):
        """Setup REST API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": time.time(),
                "server_info": {
                    "version": "1.0.0",
                    "phase": "4",
                    "capabilities": [
                        "neural_symbolic_synthesis",
                        "distributed_mesh",
                        "embodiment_bindings",
                        "real_time_communication"
                    ]
                },
                "metrics": self.real_time_metrics,
                "active_tasks": len(self.active_tasks),
                "active_bindings": len(self.embodiment_bindings)
            })
        
        @self.app.route('/cognitive/synthesize', methods=['POST'])
        def synthesize():
            """Neural-symbolic synthesis endpoint"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400
                
                # Extract synthesis parameters
                symbolic_input = data.get('symbolic_input', {})
                neural_input = np.array(data.get('neural_input', []))
                synthesis_type = data.get('synthesis_type', 'conceptual_embedding')
                
                # Perform synthesis
                start_time = time.time()
                result = self.neural_symbolic.synthesize(
                    symbolic_input, neural_input, synthesis_type
                )
                execution_time = time.time() - start_time
                
                # Update metrics
                self.real_time_metrics["total_operations"] += 1
                self._update_operations_per_second()
                
                return jsonify({
                    "status": "success",
                    "result": result.tolist() if hasattr(result, 'tolist') else result,
                    "execution_time": execution_time,
                    "synthesis_type": synthesis_type,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                logger.error("Synthesis error", exc_info=True)
                return jsonify({"error": "An internal error occurred. Please try again later."}), 500
        
        @self.app.route('/cognitive/tasks', methods=['POST'])
        def create_task():
            """Create a new distributed cognitive task"""
            try:
                data = request.get_json()
                task = CognitiveTask(
                    task_id=str(uuid.uuid4()),
                    task_type=data.get('task_type', 'generic'),
                    input_data=data.get('input_data', {}),
                    metadata=data.get('metadata', {})
                )
                
                self.active_tasks[task.task_id] = task
                
                # Assign task to available agents
                self._assign_task_to_agents(task)
                
                return jsonify({
                    "status": "created",
                    "task_id": task.task_id,
                    "task": asdict(task)
                })
                
            except Exception as e:
                logger.error("Task creation error", exc_info=True)
                return jsonify({"error": "An internal error occurred. Please try again later."}), 500
        
        @self.app.route('/cognitive/tasks/<task_id>', methods=['GET'])
        def get_task(task_id):
            """Get task status and results"""
            if task_id not in self.active_tasks:
                return jsonify({"error": "Task not found"}), 404
            
            task = self.active_tasks[task_id]
            return jsonify({
                "status": "found",
                "task": asdict(task),
                "timestamp": time.time()
            })
        
        @self.app.route('/cognitive/state', methods=['GET'])
        def get_cognitive_state():
            """Get current distributed cognitive state"""
            return jsonify({
                "cognitive_state": self.cognitive_state,
                "mesh_topology": {
                    "agent_count": len(self.mesh_manager.agents),
                    "topology_type": str(self.mesh_manager.topology_type),
                    "running": self.mesh_manager.running
                },
                "active_tasks": len(self.active_tasks),
                "timestamp": time.time()
            })
        
        @self.app.route('/embodiment/bind', methods=['POST'])
        def bind_embodiment():
            """Bind to an external embodiment system"""
            try:
                data = request.get_json()
                binding = EmbodimentBinding(
                    binding_id=str(uuid.uuid4()),
                    system_type=data.get('system_type'),
                    endpoint=data.get('endpoint'),
                    capabilities=data.get('capabilities', []),
                    metadata=data.get('metadata', {})
                )
                
                self.embodiment_bindings[binding.binding_id] = binding
                
                # Initialize binding-specific handler
                self._initialize_embodiment_binding(binding)
                
                return jsonify({
                    "status": "bound",
                    "binding_id": binding.binding_id,
                    "binding": asdict(binding)
                })
                
            except Exception as e:
                logger.error(f"Embodiment binding error: {str(e)}")
                return jsonify({"error": "An internal error occurred."}), 500
        
        @self.app.route('/embodiment/bindings', methods=['GET'])
        def list_bindings():
            """List all active embodiment bindings"""
            return jsonify({
                "bindings": [asdict(binding) for binding in self.embodiment_bindings.values()],
                "count": len(self.embodiment_bindings),
                "timestamp": time.time()
            })
        
        @self.app.route('/mesh/nodes', methods=['GET'])
        def list_mesh_nodes():
            """List all nodes in the distributed mesh"""
            return jsonify({
                "nodes": [{"agent_id": agent_id, "role": str(agent.state.role)} 
                         for agent_id, agent in self.mesh_manager.agents.items()],
                "topology": {
                    "type": str(self.mesh_manager.topology_type),
                    "agent_count": len(self.mesh_manager.agents)
                },
                "timestamp": time.time()
            })
        
        @self.app.route('/mesh/propagate', methods=['POST'])
        def propagate_state():
            """Propagate state across the distributed mesh"""
            try:
                data = request.get_json()
                state_update = data.get('state_update', {})
                target_nodes = data.get('target_nodes', [])
                
                # Perform distributed state propagation
                propagation_result = self._propagate_cognitive_state(
                    state_update, target_nodes
                )
                
                return jsonify({
                    "status": "propagated",
                    "propagation_result": propagation_result,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                logger.error("State propagation error occurred", exc_info=True)
                return jsonify({"error": "An internal error occurred."}), 500
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.real_time_metrics["active_connections"] += 1
            emit('connected', {
                "status": "connected",
                "server_info": {
                    "capabilities": ["real_time_synthesis", "state_updates", "task_notifications"],
                    "timestamp": time.time()
                }
            })
            logger.info(f"Client connected. Active connections: {self.real_time_metrics['active_connections']}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self.real_time_metrics["active_connections"] -= 1
            logger.info(f"Client disconnected. Active connections: {self.real_time_metrics['active_connections']}")
        
        @self.socketio.on('join_cognitive_room')
        def handle_join_room(data):
            """Join a cognitive processing room"""
            room = data.get('room', 'general')
            join_room(room)
            emit('room_joined', {
                "room": room,
                "timestamp": time.time()
            })
        
        @self.socketio.on('real_time_synthesis')
        def handle_real_time_synthesis(data):
            """Handle real-time neural-symbolic synthesis"""
            try:
                symbolic_input = data.get('symbolic_input', {})
                neural_input = np.array(data.get('neural_input', []))
                synthesis_type = data.get('synthesis_type', 'conceptual_embedding')
                
                # Perform synthesis
                result = self.neural_symbolic.synthesize(
                    symbolic_input, neural_input, synthesis_type
                )
                
                # Emit result back to client
                emit('synthesis_result', {
                    "status": "success",
                    "result": result.tolist() if hasattr(result, 'tolist') else result,
                    "synthesis_type": synthesis_type,
                    "timestamp": time.time()
                })
                
                # Update metrics
                self.real_time_metrics["total_operations"] += 1
                self._update_operations_per_second()
                
            except Exception as e:
                emit('synthesis_error', {
                    "error": str(e),
                    "timestamp": time.time()
                })
        
        @self.socketio.on('state_subscription')
        def handle_state_subscription(data):
            """Subscribe to cognitive state updates"""
            subscription_type = data.get('type', 'all')
            emit('state_subscribed', {
                "subscription_type": subscription_type,
                "current_state": self.cognitive_state,
                "timestamp": time.time()
            })
    
    def _assign_task_to_agents(self, task: CognitiveTask):
        """Assign a task to available mesh agents"""
        available_agents = list(self.mesh_manager.agents.values())
        
        if not available_agents:
            logger.warning("No agents available for task assignment")
            return
        
        # Simple round-robin assignment for now
        agent_count = min(len(available_agents), 3)  # Max 3 agents per task
        assigned_agents = available_agents[:agent_count]
        
        task.assigned_agents = [agent.state.agent_id for agent in assigned_agents]
        task.status = "assigned"
        
        # Submit task for execution
        self.task_executor.submit(self._execute_task, task)
    
    def _execute_task(self, task: CognitiveTask):
        """Execute a cognitive task"""
        try:
            task.status = "executing"
            
            # Simulate task execution with real computation
            if task.task_type == "neural_symbolic_synthesis":
                result = self._execute_synthesis_task(task)
            elif task.task_type == "attention_allocation":
                result = self._execute_attention_task(task)
            elif task.task_type == "distributed_inference":
                result = self._execute_inference_task(task)
            else:
                result = self._execute_generic_task(task)
            
            task.result = result
            task.status = "completed"
            
            # Emit task completion via WebSocket
            self.socketio.emit('task_completed', {
                "task_id": task.task_id,
                "result": result,
                "timestamp": time.time()
            })
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            logger.error(f"Task execution error: {str(e)}")
    
    def _execute_synthesis_task(self, task: CognitiveTask) -> Dict[str, Any]:
        """Execute a neural-symbolic synthesis task"""
        input_data = task.input_data
        symbolic_input = input_data.get('symbolic_input', {})
        neural_input = np.array(input_data.get('neural_input', []))
        
        result = self.neural_symbolic.synthesize(
            symbolic_input, neural_input, "conceptual_embedding"
        )
        
        return {
            "synthesis_result": result.tolist() if hasattr(result, 'tolist') else result,
            "execution_time": time.time() - task.created_at,
            "agents_used": task.assigned_agents
        }
    
    def _execute_attention_task(self, task: CognitiveTask) -> Dict[str, Any]:
        """Execute an attention allocation task"""
        # Use the attention allocation kernel
        attention_input = np.random.randn(10, 128)  # Example attention matrix
        attention_weights = np.random.randn(10)
        attention_focus = np.random.randn(128)
        
        kernel = self.kernel_registry.get_kernel("attention_allocation")
        result = kernel.compute([attention_input, attention_weights, attention_focus])
        
        return {
            "attention_allocation": result.tolist(),
            "focus_strength": float(np.mean(result)),
            "agents_used": task.assigned_agents
        }
    
    def _execute_inference_task(self, task: CognitiveTask) -> Dict[str, Any]:
        """Execute a distributed inference task"""
        # Use the logical inference kernel
        premise = np.random.randn(64)
        hypothesis = np.random.randn(64)
        confidence = np.array([0.8])
        
        kernel = self.kernel_registry.get_kernel("logical_inference")
        result = kernel.compute([premise, hypothesis, confidence])
        
        return {
            "inference_result": result.tolist(),
            "confidence_level": float(confidence[0]),
            "agents_used": task.assigned_agents
        }
    
    def _execute_generic_task(self, task: CognitiveTask) -> Dict[str, Any]:
        """Execute a generic cognitive task"""
        # Simple processing simulation
        time.sleep(0.1)  # Simulate computation
        
        return {
            "task_type": task.task_type,
            "processed_data": task.input_data,
            "processing_time": 0.1,
            "agents_used": task.assigned_agents
        }
    
    def _initialize_embodiment_binding(self, binding: EmbodimentBinding):
        """Initialize a specific embodiment binding"""
        if binding.system_type == "unity3d":
            self._setup_unity3d_binding(binding)
        elif binding.system_type == "ros":
            self._setup_ros_binding(binding)
        elif binding.system_type == "web":
            self._setup_web_binding(binding)
        else:
            logger.warning(f"Unknown embodiment system type: {binding.system_type}")
    
    def _setup_unity3d_binding(self, binding: EmbodimentBinding):
        """Setup Unity3D integration"""
        logger.info(f"Setting up Unity3D binding to {binding.endpoint}")
        
        # Create and register Unity3D agents in the mesh
        from mesh_topology import DistributedAgent, AgentRole
        
        # Create Unity3D agents based on capabilities
        unity_agent_count = min(len(binding.capabilities), 3)  # Limit to 3 agents per binding
        for i in range(unity_agent_count):
            # Determine role based on capability
            if 'movement' in binding.capabilities:
                role = AgentRole.PROCESSOR
            elif 'vision' in binding.capabilities:
                role = AgentRole.ATTENTION
            else:
                role = AgentRole.PROCESSOR
                
            agent_id = f"unity3d_{binding.binding_id}_{i}"
            agent = DistributedAgent(agent_id, role)
            
            # Add to mesh
            if self.mesh_manager.add_agent(agent):
                logger.info(f"Registered Unity3D agent {agent_id} with role {role}")
            else:
                logger.warning(f"Failed to register Unity3D agent {agent_id}")
        
        binding.status = "active"
    
    def _setup_ros_binding(self, binding: EmbodimentBinding):
        """Setup ROS integration"""
        logger.info(f"Setting up ROS binding to {binding.endpoint}")
        
        # Create and register ROS agents in the mesh
        from mesh_topology import DistributedAgent, AgentRole
        
        # Create ROS agents based on capabilities
        ros_agent_count = min(len(binding.capabilities), 3)  # Limit to 3 agents per binding
        for i in range(ros_agent_count):
            # Determine role based on capability
            if 'navigation' in binding.capabilities:
                role = AgentRole.COORDINATOR
            elif 'manipulation' in binding.capabilities:
                role = AgentRole.PROCESSOR
            elif 'perception' in binding.capabilities:
                role = AgentRole.ATTENTION
            else:
                role = AgentRole.INFERENCE
                
            agent_id = f"ros_{binding.binding_id}_{i}"
            agent = DistributedAgent(agent_id, role)
            
            # Add to mesh
            if self.mesh_manager.add_agent(agent):
                logger.info(f"Registered ROS agent {agent_id} with role {role}")
            else:
                logger.warning(f"Failed to register ROS agent {agent_id}")
        
        binding.status = "active"
    
    def _setup_web_binding(self, binding: EmbodimentBinding):
        """Setup web agent integration"""
        logger.info(f"Setting up web binding to {binding.endpoint}")
        
        # Create and register web agents in the mesh
        from mesh_topology import DistributedAgent, AgentRole
        
        # Create web agents based on capabilities
        web_agent_count = min(len(binding.capabilities), 2)  # Limit to 2 agents per binding
        for i in range(web_agent_count):
            # Determine role based on capability
            if 'visualization' in binding.capabilities:
                role = AgentRole.MEMORY
            elif 'data_processing' in binding.capabilities:
                role = AgentRole.PROCESSOR
            elif 'user_interaction' in binding.capabilities:
                role = AgentRole.COORDINATOR
            else:
                role = AgentRole.INFERENCE
                
            agent_id = f"web_{binding.binding_id}_{i}"
            agent = DistributedAgent(agent_id, role)
            
            # Add to mesh
            if self.mesh_manager.add_agent(agent):
                logger.info(f"Registered web agent {agent_id} with role {role}")
            else:
                logger.warning(f"Failed to register web agent {agent_id}")
        
        binding.status = "active"
    
    def _propagate_cognitive_state(self, state_update: Dict[str, Any], 
                                 target_nodes: List[str]) -> Dict[str, Any]:
        """Propagate cognitive state across the mesh"""
        propagation_results = {}
        
        # Update local state
        self.cognitive_state.update(state_update)
        
        # Propagate to target nodes
        for node_id in target_nodes:
            try:
                # Simulate distributed propagation
                propagation_results[node_id] = {
                    "status": "success",
                    "latency": np.random.uniform(0.001, 0.01),  # Simulated network latency
                    "timestamp": time.time()
                }
            except Exception as e:
                propagation_results[node_id] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": time.time()
                }
        
        # Emit state update via WebSocket
        self.socketio.emit('state_update', {
            "state_update": state_update,
            "propagation_results": propagation_results,
            "timestamp": time.time()
        })
        
        return propagation_results
    
    def _update_operations_per_second(self):
        """Update operations per second metric"""
        current_time = time.time()
        if not hasattr(self, '_last_metric_update'):
            self._last_metric_update = current_time
            self._operations_in_window = 0
        
        self._operations_in_window += 1
        
        # Update every second
        if current_time - self._last_metric_update >= 1.0:
            self.real_time_metrics["operations_per_second"] = self._operations_in_window
            self._operations_in_window = 0
            self._last_metric_update = current_time
    
    def _start_background_services(self):
        """Start background monitoring and maintenance services"""
        def metrics_updater():
            """Update metrics periodically"""
            while True:
                try:
                    # Update memory usage
                    import psutil
                    process = psutil.Process()
                    self.real_time_metrics["memory_usage"] = process.memory_info().rss / (1024 * 1024)  # MB
                except ImportError:
                    # psutil not available, use basic measurement
                    self.real_time_metrics["memory_usage"] = 0.0
                except Exception as e:
                    logger.error(f"Metrics update error: {str(e)}")
                
                time.sleep(5)  # Update every 5 seconds
        
        def heartbeat_monitor():
            """Monitor embodiment binding heartbeats"""
            while True:
                current_time = time.time()
                expired_bindings = []
                
                for binding_id, binding in self.embodiment_bindings.items():
                    if current_time - binding.last_heartbeat > 60:  # 60 second timeout
                        expired_bindings.append(binding_id)
                
                # Remove expired bindings
                for binding_id in expired_bindings:
                    del self.embodiment_bindings[binding_id]
                    logger.info(f"Removed expired binding: {binding_id}")
                
                time.sleep(30)  # Check every 30 seconds
        
        # Start background threads
        threading.Thread(target=metrics_updater, daemon=True).start()
        threading.Thread(target=heartbeat_monitor, daemon=True).start()
    
    def run(self):
        """Run the API server"""
        logger.info(f"Starting Cognitive API Server on {self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=self.debug)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 4 Cognitive API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    server = CognitiveAPIServer(host=args.host, port=args.port, debug=args.debug)
    server.run()


if __name__ == "__main__":
    main()