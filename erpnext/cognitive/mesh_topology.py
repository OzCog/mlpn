"""
Dynamic Mesh Topology for Distributed Cognitive Agents

Implements distributed agent mesh with dynamic topology management,
state propagation, and real-time agent communication.
"""

import numpy as np
import json
import time
import threading
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import socket
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib


class AgentRole(Enum):
    """Roles for distributed cognitive agents"""
    COORDINATOR = "coordinator"
    PROCESSOR = "processor"
    MEMORY = "memory"
    ATTENTION = "attention"
    INFERENCE = "inference"


class MeshTopology(Enum):
    """Mesh topology types"""
    FULLY_CONNECTED = "fully_connected"
    RING = "ring"
    TREE = "tree"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


@dataclass
class AgentState:
    """State of a distributed cognitive agent"""
    agent_id: str
    role: AgentRole
    load: float = 0.0
    last_heartbeat: float = 0.0
    attention_focus: Dict[str, float] = None
    memory_usage: float = 0.0
    processing_capacity: float = 1.0
    connections: Set[str] = None
    
    def __post_init__(self):
        if self.attention_focus is None:
            self.attention_focus = {}
        if self.connections is None:
            self.connections = set()
        if self.last_heartbeat == 0.0:
            self.last_heartbeat = time.time()


@dataclass
class MeshMessage:
    """Message for inter-agent communication"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float = 0.0
    priority: int = 0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.message_id:
            self.message_id = str(uuid.uuid4())


class DistributedAgent:
    """
    Individual agent in the distributed cognitive mesh
    """
    
    def __init__(self, agent_id: str, role: AgentRole, port: int = None):
        self.state = AgentState(agent_id=agent_id, role=role)
        self.port = port or self._find_free_port()
        self.message_queue: List[MeshMessage] = []
        self.message_handlers: Dict[str, callable] = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize role-specific capabilities
        self._initialize_role_capabilities()
        
    def _find_free_port(self) -> int:
        """Find a free port for the agent"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
        
    def _initialize_role_capabilities(self):
        """Initialize capabilities based on agent role"""
        if self.state.role == AgentRole.COORDINATOR:
            self.state.processing_capacity = 2.0
            self.message_handlers.update({
                "mesh_coordination": self._handle_coordination,
                "state_sync": self._handle_state_sync,
                "topology_update": self._handle_topology_update
            })
        elif self.state.role == AgentRole.ATTENTION:
            self.state.processing_capacity = 1.5
            self.message_handlers.update({
                "attention_focus": self._handle_attention_focus,
                "attention_spread": self._handle_attention_spread,
                "state_sync": self._handle_state_sync
            })
        elif self.state.role == AgentRole.MEMORY:
            self.state.processing_capacity = 1.0
            self.message_handlers.update({
                "memory_store": self._handle_memory_store,
                "memory_retrieve": self._handle_memory_retrieve,
                "state_sync": self._handle_state_sync
            })
        elif self.state.role == AgentRole.PROCESSOR:
            self.state.processing_capacity = 1.8
            self.message_handlers.update({
                "process_task": self._handle_process_task,
                "compute_tensor": self._handle_compute_tensor,
                "state_sync": self._handle_state_sync
            })
        elif self.state.role == AgentRole.INFERENCE:
            self.state.processing_capacity = 1.3
            self.message_handlers.update({
                "run_inference": self._handle_run_inference,
                "update_beliefs": self._handle_update_beliefs,
                "state_sync": self._handle_state_sync
            })
            
    def start(self):
        """Start the agent"""
        self.running = True
        self.state.last_heartbeat = time.time()
        
    def stop(self):
        """Stop the agent"""
        self.running = False
        self.executor.shutdown(wait=True)
        
    def send_message(self, receiver_id: str, message_type: str, 
                    payload: Dict[str, Any], priority: int = 0) -> str:
        """
        Send message to another agent
        
        Args:
            receiver_id: Target agent ID
            message_type: Type of message
            payload: Message payload
            priority: Message priority (higher = more urgent)
            
        Returns:
            Message ID
        """
        message = MeshMessage(
            message_id="",  # Will be auto-generated
            sender_id=self.state.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        
        # In a real implementation, this would use network protocols
        # For now, we'll simulate message passing
        return message.message_id
        
    def receive_message(self, message: MeshMessage) -> bool:
        """
        Receive and process a message
        
        Args:
            message: Message to process
            
        Returns:
            True if message was handled successfully
        """
        if message.message_type in self.message_handlers:
            try:
                handler = self.message_handlers[message.message_type]
                handler(message)
                return True
            except Exception as e:
                print(f"Error handling message {message.message_id}: {e}")
                return False
        else:
            print(f"No handler for message type: {message.message_type}")
            return False
            
    def update_load(self, new_load: float):
        """Update agent processing load"""
        self.state.load = max(0.0, min(1.0, new_load))
        self.state.last_heartbeat = time.time()
        
    def get_capacity(self) -> float:
        """Get available processing capacity"""
        return max(0.0, self.state.processing_capacity - self.state.load)
        
    # Message handlers
    def _handle_coordination(self, message: MeshMessage):
        """Handle coordination messages"""
        payload = message.payload
        if "action" in payload:
            if payload["action"] == "heartbeat_request":
                # Respond with current state
                response_payload = {
                    "action": "heartbeat_response",
                    "state": asdict(self.state)
                }
                self.send_message(message.sender_id, "mesh_coordination", response_payload)
                
    def _handle_state_sync(self, message: MeshMessage):
        """Handle state synchronization"""
        # Update connections based on sync message
        if "connections" in message.payload:
            self.state.connections.update(message.payload["connections"])
            
    def _handle_topology_update(self, message: MeshMessage):
        """Handle topology updates"""
        # Update mesh topology connections
        if "topology" in message.payload:
            topology_data = message.payload["topology"]
            self.state.connections = set(topology_data.get("connections", []))
            
    def _handle_attention_focus(self, message: MeshMessage):
        """Handle attention focus messages"""
        if "focus_targets" in message.payload:
            for target, strength in message.payload["focus_targets"].items():
                self.state.attention_focus[target] = strength
                
    def _handle_attention_spread(self, message: MeshMessage):
        """Handle attention spreading"""
        # Simulate attention spreading to connected agents
        if "attention_values" in message.payload:
            attention_values = message.payload["attention_values"]
            # Propagate attention with decay
            for connected_agent in self.state.connections:
                spread_payload = {
                    "attention_values": {k: v * 0.8 for k, v in attention_values.items()}
                }
                self.send_message(connected_agent, "attention_spread", spread_payload)
                
    def _handle_memory_store(self, message: MeshMessage):
        """Handle memory storage requests"""
        # Simulate memory storage
        self.state.memory_usage += 0.1
        
    def _handle_memory_retrieve(self, message: MeshMessage):
        """Handle memory retrieval requests"""
        # Simulate memory retrieval
        pass
        
    def _handle_process_task(self, message: MeshMessage):
        """Handle processing tasks"""
        # Simulate task processing
        self.state.load += 0.2
        
    def _handle_compute_tensor(self, message: MeshMessage):
        """Handle tensor computation"""
        # Simulate tensor computation
        self.state.load += 0.3
        
    def _handle_run_inference(self, message: MeshMessage):
        """Handle inference requests"""
        # Simulate inference
        self.state.load += 0.25
        
    def _handle_update_beliefs(self, message: MeshMessage):
        """Handle belief updates"""
        # Simulate belief updating
        pass


class DynamicMesh:
    """
    Dynamic mesh topology manager for distributed cognitive agents
    """
    
    def __init__(self, topology_type: MeshTopology = MeshTopology.ADAPTIVE):
        self.topology_type = topology_type
        self.agents: Dict[str, DistributedAgent] = {}
        self.topology_matrix: np.ndarray = np.array([])
        self.message_routing: Dict[str, List[str]] = defaultdict(list)
        self.performance_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.state_history: List[Dict[str, Any]] = []
        self.running = False
        
    def add_agent(self, agent: DistributedAgent) -> bool:
        """
        Add agent to the mesh
        
        Args:
            agent: Agent to add
            
        Returns:
            True if agent was added successfully
        """
        if agent.state.agent_id in self.agents:
            return False
            
        self.agents[agent.state.agent_id] = agent
        self._rebuild_topology()
        agent.start()
        return True
        
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove agent from the mesh
        
        Args:
            agent_id: ID of agent to remove
            
        Returns:
            True if agent was removed successfully
        """
        if agent_id not in self.agents:
            return False
            
        agent = self.agents[agent_id]
        agent.stop()
        del self.agents[agent_id]
        self._rebuild_topology()
        return True
        
    def _rebuild_topology(self):
        """Rebuild mesh topology based on current agents"""
        num_agents = len(self.agents)
        if num_agents == 0:
            self.topology_matrix = np.array([])
            return
            
        # Create adjacency matrix
        self.topology_matrix = np.zeros((num_agents, num_agents))
        agent_ids = list(self.agents.keys())
        
        if self.topology_type == MeshTopology.FULLY_CONNECTED:
            # Connect all agents to all other agents
            self.topology_matrix = np.ones((num_agents, num_agents)) - np.eye(num_agents)
            
        elif self.topology_type == MeshTopology.RING:
            # Connect each agent to next agent in ring
            for i in range(num_agents):
                next_i = (i + 1) % num_agents
                self.topology_matrix[i][next_i] = 1
                self.topology_matrix[next_i][i] = 1
                
        elif self.topology_type == MeshTopology.TREE:
            # Create tree topology (each agent connected to 2-3 others)
            for i in range(1, num_agents):
                parent = (i - 1) // 2
                self.topology_matrix[i][parent] = 1
                self.topology_matrix[parent][i] = 1
                
        elif self.topology_type == MeshTopology.ADAPTIVE:
            # Adaptive topology based on agent roles and performance
            self._build_adaptive_topology(agent_ids)
            
        # Update agent connections
        self._update_agent_connections(agent_ids)
        
    def _build_adaptive_topology(self, agent_ids: List[str]):
        """Build adaptive topology based on agent characteristics"""
        coordinators = []
        processors = []
        others = []
        
        for i, agent_id in enumerate(agent_ids):
            agent = self.agents[agent_id]
            if agent.state.role == AgentRole.COORDINATOR:
                coordinators.append(i)
            elif agent.state.role == AgentRole.PROCESSOR:
                processors.append(i)
            else:
                others.append(i)
                
        # Connect coordinators to all other agents
        for coord_i in coordinators:
            for i in range(len(agent_ids)):
                if i != coord_i:
                    self.topology_matrix[coord_i][i] = 1
                    self.topology_matrix[i][coord_i] = 1
                    
        # Connect processors in a ring
        for i, proc_i in enumerate(processors):
            if len(processors) > 1:
                next_proc = processors[(i + 1) % len(processors)]
                self.topology_matrix[proc_i][next_proc] = 1
                self.topology_matrix[next_proc][proc_i] = 1
                
        # Connect other agents to nearest coordinator or processor
        for other_i in others:
            if coordinators:
                coord_i = coordinators[0]  # Connect to first coordinator
                self.topology_matrix[other_i][coord_i] = 1
                self.topology_matrix[coord_i][other_i] = 1
            elif processors:
                proc_i = processors[0]  # Connect to first processor
                self.topology_matrix[other_i][proc_i] = 1
                self.topology_matrix[proc_i][other_i] = 1
                
    def _update_agent_connections(self, agent_ids: List[str]):
        """Update agent connection sets based on topology matrix"""
        for i, agent_id in enumerate(agent_ids):
            agent = self.agents[agent_id]
            connections = set()
            
            for j, other_agent_id in enumerate(agent_ids):
                if i != j and self.topology_matrix[i][j] == 1:
                    connections.add(other_agent_id)
                    
            agent.state.connections = connections
            
    def propagate_state(self, source_agent_id: str, state_data: Dict[str, Any]) -> int:
        """
        Propagate state across the mesh
        
        Args:
            source_agent_id: Source agent for state propagation
            state_data: State data to propagate
            
        Returns:
            Number of agents that received the state
        """
        if source_agent_id not in self.agents:
            return 0
            
        propagated_count = 0
        visited = set()
        queue = [source_agent_id]
        
        while queue:
            current_agent_id = queue.pop(0)
            if current_agent_id in visited:
                continue
                
            visited.add(current_agent_id)
            current_agent = self.agents[current_agent_id]
            
            # Send state to connected agents
            for connected_agent_id in current_agent.state.connections:
                if connected_agent_id not in visited:
                    message = MeshMessage(
                        message_id="",
                        sender_id=current_agent_id,
                        receiver_id=connected_agent_id,
                        message_type="state_sync",
                        payload={"state_data": state_data}
                    )
                    
                    connected_agent = self.agents[connected_agent_id]
                    connected_agent.receive_message(message)
                    
                    queue.append(connected_agent_id)
                    propagated_count += 1
                    
        return propagated_count
        
    def benchmark_attention_allocation(self, iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark attention allocation across distributed agents
        
        Args:
            iterations: Number of benchmark iterations
            
        Returns:
            Benchmark results
        """
        if not self.agents:
            return {"error": "No agents available for benchmarking"}
            
        start_time = time.time()
        attention_agents = [agent for agent in self.agents.values() 
                          if agent.state.role == AgentRole.ATTENTION]
        
        if not attention_agents:
            return {"error": "No attention agents available"}
            
        # Benchmark metrics
        total_messages = 0
        total_propagation_time = 0.0
        successful_allocations = 0
        
        for i in range(iterations):
            # Choose random attention agent and target
            agent = np.random.choice(attention_agents)
            target = f"concept_{i % 10}"
            
            # Measure attention allocation time
            alloc_start = time.time()
            
            # Focus attention
            focus_payload = {
                "focus_targets": {target: np.random.uniform(0.5, 2.0)}
            }
            
            # Propagate to connected agents
            for connected_id in agent.state.connections:
                message = MeshMessage(
                    message_id="",
                    sender_id=agent.state.agent_id,
                    receiver_id=connected_id,
                    message_type="attention_focus",
                    payload=focus_payload
                )
                
                if connected_id in self.agents:
                    self.agents[connected_id].receive_message(message)
                    total_messages += 1
                    
            alloc_end = time.time()
            total_propagation_time += (alloc_end - alloc_start)
            successful_allocations += 1
            
        end_time = time.time()
        
        # Calculate performance metrics
        total_time = end_time - start_time
        avg_propagation_time = total_propagation_time / iterations if iterations > 0 else 0
        messages_per_second = total_messages / total_time if total_time > 0 else 0
        
        return {
            "total_time": total_time,
            "iterations": iterations,
            "total_messages": total_messages,
            "successful_allocations": successful_allocations,
            "avg_propagation_time": avg_propagation_time,
            "messages_per_second": messages_per_second,
            "attention_agents": len(attention_agents),
            "total_agents": len(self.agents),
            "topology_type": self.topology_type.value
        }
        
    def get_mesh_topology_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive mesh topology statistics
        
        Returns:
            Topology statistics
        """
        if not self.agents:
            return {"error": "No agents in mesh"}
            
        agent_roles = defaultdict(int)
        total_connections = 0
        avg_load = 0.0
        total_capacity = 0.0
        
        for agent in self.agents.values():
            agent_roles[agent.state.role.value] += 1
            total_connections += len(agent.state.connections)
            avg_load += agent.state.load
            total_capacity += agent.state.processing_capacity
            
        num_agents = len(self.agents)
        avg_load = avg_load / num_agents if num_agents > 0 else 0
        avg_connections = total_connections / num_agents if num_agents > 0 else 0
        
        # Calculate topology density
        max_connections = num_agents * (num_agents - 1)
        density = total_connections / max_connections if max_connections > 0 else 0
        
        return {
            "total_agents": num_agents,
            "agent_roles": dict(agent_roles),
            "topology_type": self.topology_type.value,
            "total_connections": total_connections,
            "avg_connections_per_agent": avg_connections,
            "topology_density": density,
            "avg_agent_load": avg_load,
            "total_processing_capacity": total_capacity,
            "mesh_efficiency": (total_capacity - avg_load * num_agents) / total_capacity if total_capacity > 0 else 0
        }
        
    def visualize_topology(self) -> Dict[str, Any]:
        """
        Generate topology visualization data
        
        Returns:
            Visualization data for mesh topology
        """
        if not self.agents:
            return {"error": "No agents to visualize"}
            
        nodes = []
        edges = []
        
        agent_ids = list(self.agents.keys())
        id_to_index = {agent_id: i for i, agent_id in enumerate(agent_ids)}
        
        # Create nodes
        for agent_id, agent in self.agents.items():
            nodes.append({
                "id": agent_id,
                "label": f"{agent.state.role.value}_{agent_id[:8]}",
                "role": agent.state.role.value,
                "load": agent.state.load,
                "capacity": agent.state.processing_capacity,
                "connections": len(agent.state.connections)
            })
            
        # Create edges
        for i, agent_id in enumerate(agent_ids):
            agent = self.agents[agent_id]
            for connected_id in agent.state.connections:
                if connected_id in id_to_index:
                    j = id_to_index[connected_id]
                    if i < j:  # Avoid duplicate edges
                        edges.append({
                            "source": agent_id,
                            "target": connected_id,
                            "weight": 1.0
                        })
                        
        return {
            "nodes": nodes,
            "edges": edges,
            "topology_type": self.topology_type.value,
            "stats": self.get_mesh_topology_stats()
        }
        
    def scheme_mesh_spec(self) -> str:
        """
        Generate Scheme specification for mesh topology
        
        Returns:
            Scheme specification string
        """
        spec = """
(define (mesh-topology-create type agents)
  (let ((mesh (make-mesh type)))
    (map (lambda (agent) (mesh-add-agent mesh agent)) agents)
    mesh))

(define (mesh-propagate-state mesh source-id state)
  (let ((visited (make-set))
        (queue (list source-id)))
    (while (not (null? queue))
      (let ((current (car queue)))
        (set-add! visited current)
        (map (lambda (neighbor)
               (unless (set-member? visited neighbor)
                 (set! queue (append queue (list neighbor)))
                 (agent-receive-state neighbor state)))
             (mesh-get-connections mesh current))
        (set! queue (cdr queue))))))

(define (mesh-benchmark-attention mesh iterations)
  (let ((start-time (current-time))
        (total-messages 0))
    (repeat iterations
      (let ((agent (mesh-random-attention-agent mesh))
            (target (random-concept)))
        (set! total-messages 
              (+ total-messages 
                 (mesh-propagate-attention mesh agent target)))))
    (list (- (current-time) start-time) total-messages)))
"""
        return spec.strip()