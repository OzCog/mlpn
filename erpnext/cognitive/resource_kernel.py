"""
Resource Kernel for Dynamic ECAN Attention Allocation

Implements resource management, allocation scheduling, and distributed
cognitive mesh integration for Phase 2 of the cognitive architecture.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
from collections import defaultdict, deque
import json


class ResourceType(Enum):
    """Types of cognitive resources"""
    ATTENTION = "attention"
    MEMORY = "memory"
    COMPUTATION = "computation"
    BANDWIDTH = "bandwidth"
    INFERENCE = "inference"


class ResourcePriority(Enum):
    """Resource allocation priorities"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ResourceQuota:
    """Resource quota specification"""
    resource_type: ResourceType
    max_allocation: float
    current_usage: float = 0.0
    reserved: float = 0.0
    
    @property
    def available(self) -> float:
        """Get available resource amount"""
        return max(0.0, self.max_allocation - self.current_usage - self.reserved)


@dataclass
class ResourceRequest:
    """Resource allocation request"""
    request_id: str
    requester_id: str
    resource_type: ResourceType
    amount: float
    priority: ResourcePriority
    duration_estimate: float
    timestamp: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if request has expired"""
        if self.deadline is None:
            return False
        return time.time() > self.deadline


@dataclass
class ResourceAllocation:
    """Active resource allocation"""
    allocation_id: str
    request: ResourceRequest
    allocated_amount: float
    start_time: float
    estimated_end_time: float
    actual_usage: float = 0.0
    
    @property
    def is_expired(self) -> bool:
        """Check if allocation has expired"""
        return time.time() > self.estimated_end_time


class ResourceKernel:
    """
    Dynamic resource allocation kernel for cognitive mesh
    """
    
    def __init__(self, node_id: str = "local_node"):
        self.node_id = node_id
        self.quotas: Dict[ResourceType, ResourceQuota] = {}
        self.pending_requests: deque = deque()
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: List[ResourceAllocation] = []
        self.mesh_nodes: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_allocations": 0,
            "failed_allocations": 0,
            "average_response_time": 0.0,
            "resource_utilization": defaultdict(float)
        }
        
        # Initialize default quotas
        self._initialize_default_quotas()
        
    def _initialize_default_quotas(self):
        """Initialize default resource quotas"""
        default_quotas = {
            ResourceType.ATTENTION: 100.0,
            ResourceType.MEMORY: 1000.0,
            ResourceType.COMPUTATION: 500.0,
            ResourceType.BANDWIDTH: 200.0,
            ResourceType.INFERENCE: 150.0
        }
        
        for resource_type, max_alloc in default_quotas.items():
            self.quotas[resource_type] = ResourceQuota(
                resource_type=resource_type,
                max_allocation=max_alloc
            )
    
    def request_resource(self, requester_id: str, resource_type: ResourceType,
                        amount: float, priority: ResourcePriority = ResourcePriority.NORMAL,
                        duration: float = 60.0, deadline: Optional[float] = None) -> str:
        """
        Request resource allocation
        
        Args:
            requester_id: ID of the requesting entity
            resource_type: Type of resource needed
            amount: Amount of resource requested
            priority: Priority of the request
            duration: Estimated duration of usage
            deadline: Optional deadline for the request
            
        Returns:
            Request ID
        """
        request_id = f"{requester_id}_{resource_type.value}_{int(time.time() * 1000)}"
        
        request = ResourceRequest(
            request_id=request_id,
            requester_id=requester_id,
            resource_type=resource_type,
            amount=amount,
            priority=priority,
            duration_estimate=duration,
            deadline=deadline
        )
        
        with self.lock:
            self.pending_requests.append(request)
            self.metrics["total_requests"] += 1
            
        return request_id
    
    def process_resource_requests(self) -> List[str]:
        """
        Process pending resource requests and allocate resources
        
        Returns:
            List of allocated request IDs
        """
        allocated_requests = []
        
        with self.lock:
            # Clean up expired requests
            self.pending_requests = deque([req for req in self.pending_requests 
                                         if not req.is_expired()])
            
            # Sort requests by priority and timestamp
            sorted_requests = sorted(self.pending_requests, 
                                   key=lambda r: (r.priority.value, r.timestamp))
            
            requests_to_remove = []
            
            for request in sorted_requests:
                if self._can_allocate(request):
                    allocation_id = self._allocate_resource(request)
                    if allocation_id:
                        allocated_requests.append(request.request_id)
                        requests_to_remove.append(request)
                        self.metrics["successful_allocations"] += 1
                    else:
                        self.metrics["failed_allocations"] += 1
            
            # Remove processed requests
            for request in requests_to_remove:
                if request in self.pending_requests:
                    self.pending_requests.remove(request)
        
        return allocated_requests
    
    def _can_allocate(self, request: ResourceRequest) -> bool:
        """Check if resource can be allocated"""
        quota = self.quotas.get(request.resource_type)
        if not quota:
            return False
        
        return quota.available >= request.amount
    
    def _allocate_resource(self, request: ResourceRequest) -> Optional[str]:
        """Allocate resource for a request"""
        quota = self.quotas.get(request.resource_type)
        if not quota or quota.available < request.amount:
            return None
        
        allocation_id = f"alloc_{request.request_id}"
        current_time = time.time()
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            request=request,
            allocated_amount=request.amount,
            start_time=current_time,
            estimated_end_time=current_time + request.duration_estimate
        )
        
        # Update quota usage
        quota.current_usage += request.amount
        
        # Store allocation
        self.active_allocations[allocation_id] = allocation
        
        return allocation_id
    
    def release_resource(self, allocation_id: str) -> bool:
        """
        Release allocated resource
        
        Args:
            allocation_id: ID of the allocation to release
            
        Returns:
            True if successfully released
        """
        with self.lock:
            allocation = self.active_allocations.get(allocation_id)
            if not allocation:
                return False
            
            # Update quota
            quota = self.quotas.get(allocation.request.resource_type)
            if quota:
                quota.current_usage -= allocation.allocated_amount
                quota.current_usage = max(0.0, quota.current_usage)
            
            # Move to history
            self.allocation_history.append(allocation)
            del self.active_allocations[allocation_id]
            
            return True
    
    def cleanup_expired_allocations(self) -> List[str]:
        """
        Clean up expired allocations
        
        Returns:
            List of cleaned up allocation IDs
        """
        cleaned_allocations = []
        
        with self.lock:
            expired_allocations = [alloc_id for alloc_id, alloc 
                                 in self.active_allocations.items() 
                                 if alloc.is_expired]
            
            for alloc_id in expired_allocations:
                if self.release_resource(alloc_id):
                    cleaned_allocations.append(alloc_id)
        
        return cleaned_allocations
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Get current resource utilization"""
        utilization = {}
        
        for resource_type, quota in self.quotas.items():
            if quota.max_allocation > 0:
                utilization[resource_type.value] = quota.current_usage / quota.max_allocation
            else:
                utilization[resource_type.value] = 0.0
        
        return utilization
    
    def register_mesh_node(self, node_id: str, node_info: Dict[str, Any]) -> None:
        """
        Register a mesh node for distributed resource allocation
        
        Args:
            node_id: ID of the mesh node
            node_info: Information about the node (capabilities, quotas, etc.)
        """
        self.mesh_nodes[node_id] = {
            **node_info,
            "last_seen": time.time(),
            "status": "active"
        }
    
    def request_mesh_resources(self, resource_type: ResourceType, 
                              amount: float) -> Optional[str]:
        """
        Request resources from mesh nodes
        
        Args:
            resource_type: Type of resource needed
            amount: Amount of resource requested
            
        Returns:
            Mesh node ID that can provide the resource, or None
        """
        available_nodes = []
        
        for node_id, node_info in self.mesh_nodes.items():
            if node_info.get("status") == "active":
                node_quotas = node_info.get("quotas", {})
                node_quota = node_quotas.get(resource_type.value, {})
                available = node_quota.get("available", 0.0)
                
                if available >= amount:
                    available_nodes.append((node_id, available))
        
        # Sort by available resources (descending)
        available_nodes.sort(key=lambda x: x[1], reverse=True)
        
        return available_nodes[0][0] if available_nodes else None
    
    def update_resource_metrics(self) -> None:
        """Update resource utilization metrics"""
        utilization = self.get_resource_utilization()
        
        for resource_type, util in utilization.items():
            self.metrics["resource_utilization"][resource_type] = util
        
        # Calculate average response time
        if self.allocation_history:
            response_times = []
            for allocation in self.allocation_history[-100:]:  # Last 100 allocations
                response_time = allocation.start_time - allocation.request.timestamp
                response_times.append(response_time)
            
            self.metrics["average_response_time"] = np.mean(response_times)
    
    def get_kernel_stats(self) -> Dict[str, Any]:
        """Get comprehensive kernel statistics"""
        self.update_resource_metrics()
        
        return {
            "node_id": self.node_id,
            "metrics": dict(self.metrics),
            "resource_utilization": self.get_resource_utilization(),
            "active_allocations": len(self.active_allocations),
            "pending_requests": len(self.pending_requests),
            "mesh_nodes": len(self.mesh_nodes),
            "quotas": {rt.value: {"max": q.max_allocation, "current": q.current_usage, 
                                "available": q.available} 
                      for rt, q in self.quotas.items()}
        }
    
    def scheme_resource_spec(self) -> str:
        """
        Generate Scheme specification for resource allocation
        
        Returns:
            Scheme specification string
        """
        spec = f"""
;; Resource Kernel Specification for {self.node_id}
(define (resource-request requester resource-type amount priority)
  (let ((request-id (generate-request-id requester resource-type)))
    (add-pending-request request-id requester resource-type amount priority)
    request-id))

(define (process-resource-requests)
  (map (lambda (request)
         (if (can-allocate? request)
             (allocate-resource request)
             (queue-request request)))
       (sort-requests-by-priority (get-pending-requests))))

(define (resource-utilization resource-type)
  (/ (current-usage resource-type) (max-allocation resource-type)))

(define (mesh-resource-request resource-type amount)
  (find-available-node 
    (filter (lambda (node) 
              (>= (node-available-resource node resource-type) amount))
            mesh-nodes)))
"""
        return spec.strip()


class AttentionScheduler:
    """
    Scheduler for optimized attention allocation cycles
    """
    
    def __init__(self, resource_kernel: ResourceKernel):
        self.resource_kernel = resource_kernel
        self.attention_queue: deque = deque()
        self.active_cycles: Dict[str, Dict[str, Any]] = {}
        self.cycle_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
    def schedule_attention_cycle(self, cycle_id: str, atoms: List[str],
                               focus_strength: float = 1.0,
                               priority: ResourcePriority = ResourcePriority.NORMAL,
                               duration: float = 30.0) -> bool:
        """
        Schedule an attention allocation cycle
        
        Args:
            cycle_id: Unique identifier for the cycle
            atoms: List of atom IDs to focus on
            focus_strength: Strength of attention focus
            priority: Priority of the cycle
            duration: Estimated duration of the cycle
            
        Returns:
            True if successfully scheduled
        """
        # Calculate resource requirements
        attention_needed = len(atoms) * focus_strength * 10.0  # Heuristic
        computation_needed = len(atoms) * focus_strength * 5.0
        
        # Request resources
        attention_request = self.resource_kernel.request_resource(
            requester_id=cycle_id,
            resource_type=ResourceType.ATTENTION,
            amount=attention_needed,
            priority=priority,
            duration=duration
        )
        
        computation_request = self.resource_kernel.request_resource(
            requester_id=cycle_id,
            resource_type=ResourceType.COMPUTATION,
            amount=computation_needed,
            priority=priority,
            duration=duration
        )
        
        cycle_spec = {
            "cycle_id": cycle_id,
            "atoms": atoms,
            "focus_strength": focus_strength,
            "priority": priority,
            "duration": duration,
            "attention_request": attention_request,
            "computation_request": computation_request,
            "timestamp": time.time(),
            "status": "scheduled"
        }
        
        with self.lock:
            self.attention_queue.append(cycle_spec)
        
        return True
    
    def process_attention_queue(self) -> List[str]:
        """
        Process scheduled attention cycles
        
        Returns:
            List of executed cycle IDs
        """
        executed_cycles = []
        
        # Process resource requests first
        allocated_requests = self.resource_kernel.process_resource_requests()
        
        with self.lock:
            cycles_to_execute = []
            cycles_to_remove = []
            
            for cycle_spec in list(self.attention_queue):
                attention_req = cycle_spec["attention_request"]
                computation_req = cycle_spec["computation_request"]
                
                # Check if both resources are allocated
                if (attention_req in allocated_requests and 
                    computation_req in allocated_requests):
                    cycles_to_execute.append(cycle_spec)
                    cycles_to_remove.append(cycle_spec)
            
            # Remove cycles to be executed
            for cycle_spec in cycles_to_remove:
                if cycle_spec in self.attention_queue:
                    self.attention_queue.remove(cycle_spec)
            
            # Execute cycles
            for cycle_spec in cycles_to_execute:
                cycle_id = cycle_spec["cycle_id"]
                cycle_spec["status"] = "executing"
                cycle_spec["execution_start"] = time.time()
                
                self.active_cycles[cycle_id] = cycle_spec
                executed_cycles.append(cycle_id)
        
        return executed_cycles
    
    def complete_attention_cycle(self, cycle_id: str) -> bool:
        """
        Mark attention cycle as complete and release resources
        
        Args:
            cycle_id: ID of the cycle to complete
            
        Returns:
            True if successfully completed
        """
        with self.lock:
            cycle_spec = self.active_cycles.get(cycle_id)
            if not cycle_spec:
                return False
            
            # Release resources
            attention_alloc = f"alloc_{cycle_spec['attention_request']}"
            computation_alloc = f"alloc_{cycle_spec['computation_request']}"
            
            self.resource_kernel.release_resource(attention_alloc)
            self.resource_kernel.release_resource(computation_alloc)
            
            # Mark as completed
            cycle_spec["status"] = "completed"
            cycle_spec["completion_time"] = time.time()
            
            # Move to history
            self.cycle_history.append(cycle_spec)
            del self.active_cycles[cycle_id]
            
            return True
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            "queued_cycles": len(self.attention_queue),
            "active_cycles": len(self.active_cycles),
            "completed_cycles": len(self.cycle_history),
            "average_cycle_duration": self._calculate_average_duration(),
            "resource_efficiency": self._calculate_resource_efficiency()
        }
    
    def _calculate_average_duration(self) -> float:
        """Calculate average cycle duration"""
        if not self.cycle_history:
            return 0.0
        
        durations = []
        for cycle in self.cycle_history[-50:]:  # Last 50 cycles
            if "execution_start" in cycle and "completion_time" in cycle:
                duration = cycle["completion_time"] - cycle["execution_start"]
                durations.append(duration)
        
        return np.mean(durations) if durations else 0.0
    
    def _calculate_resource_efficiency(self) -> float:
        """Calculate resource allocation efficiency"""
        if not self.cycle_history:
            return 0.0
        
        total_requested = 0.0
        total_used = 0.0
        
        for cycle in self.cycle_history[-20:]:  # Last 20 cycles
            estimated_duration = cycle.get("duration", 0.0)
            if "execution_start" in cycle and "completion_time" in cycle:
                actual_duration = cycle["completion_time"] - cycle["execution_start"]
                total_requested += estimated_duration
                total_used += actual_duration
        
        if total_requested > 0:
            return min(total_used / total_requested, 1.0)
        return 0.0