"""
Resource Kernel for Dynamic ECAN Attention Allocation & Distributed Cognitive Mesh

Implements resource management, allocation scheduling, and distributed
cognitive mesh integration for Phase 2 of the cognitive architecture.
This includes both local resource kernels and distributed resource management.
"""

import numpy as np
import time
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import json


class ResourceType(Enum):
    """Types of cognitive resources"""
    COMPUTE = "compute"
    MEMORY = "memory"
    ATTENTION = "attention"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"
    INFERENCE = "inference"


class ResourcePriority(Enum):
    """Resource allocation priorities"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class AllocationStrategy(Enum):
    """Resource allocation strategies"""
    FAIR_SHARE = "fair_share"
    PRIORITY_BASED = "priority_based"
    LOAD_BALANCED = "load_balanced"
    PREDICTIVE = "predictive"
    MARKET_BASED = "market_based"


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
    """Request for resource allocation"""
    request_id: str
    requester_id: str
    resource_type: ResourceType
    amount: float
    priority: int
    deadline: float  # Unix timestamp
    duration_estimate: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_expired(self) -> bool:
        """Check if request has expired"""
        return time.time() > self.deadline


@dataclass
class ResourceAllocation:
    """Allocated resource record"""
    allocation_id: str
    request_id: str
    resource_type: ResourceType
    amount: float
    allocated_at: float
    expires_at: float
    provider_id: str
    consumer_id: str
    cost: float = 0.0
    actual_usage: float = 0.0
    
    @property
    def is_expired(self) -> bool:
        """Check if allocation has expired"""
        return time.time() > self.expires_at


@dataclass
class ResourcePool:
    """Pool of available resources"""
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    allocated_amount: float
    reservations: Dict[str, float] = None
    quality_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.reservations is None:
            self.reservations = {}
        if self.quality_metrics is None:
            self.quality_metrics = {
                "latency": 0.0,
                "throughput": 1.0,
                "reliability": 1.0
            }


class ResourceKernel:
    """
    Core resource management kernel for distributed cognitive agents
    """
    
    def __init__(self, agent_id: str = "local_node", strategy: AllocationStrategy = AllocationStrategy.LOAD_BALANCED):
        self.agent_id = agent_id
        self.node_id = agent_id  # Alias for backwards compatibility
        self.strategy = strategy
        self.resource_pools: Dict[ResourceType, ResourcePool] = {}
        self.quotas: Dict[ResourceType, ResourceQuota] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.pending_requests: List[ResourceRequest] = []
        self.allocation_history: List[ResourceAllocation] = []
        self.performance_metrics: Dict[str, float] = defaultdict(float)
        self.mesh_nodes: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
        # Performance metrics
        self.metrics = {
            "requests_processed": 0,
            "allocations_made": 0,
            "total_resource_time": 0.0,
            "average_response_time": 0.0
        }
        
        # Initialize default resource pools and quotas
        self._initialize_resource_pools()
        self._initialize_quotas()
        
    def _initialize_resource_pools(self):
        """Initialize default resource pools"""
        default_pools = {
            ResourceType.COMPUTE: ResourcePool(
                resource_type=ResourceType.COMPUTE,
                total_capacity=100.0,
                available_capacity=100.0,
                allocated_amount=0.0
            ),
            ResourceType.MEMORY: ResourcePool(
                resource_type=ResourceType.MEMORY,
                total_capacity=1000.0,  # MB
                available_capacity=1000.0,
                allocated_amount=0.0
            ),
            ResourceType.ATTENTION: ResourcePool(
                resource_type=ResourceType.ATTENTION,
                total_capacity=10.0,
                available_capacity=10.0,
                allocated_amount=0.0
            ),
            ResourceType.BANDWIDTH: ResourcePool(
                resource_type=ResourceType.BANDWIDTH,
                total_capacity=100.0,  # Mbps
                available_capacity=100.0,
                allocated_amount=0.0
            ),
            ResourceType.STORAGE: ResourcePool(
                resource_type=ResourceType.STORAGE,
                total_capacity=5000.0,  # MB
                available_capacity=5000.0,
                allocated_amount=0.0
            ),
            ResourceType.INFERENCE: ResourcePool(
                resource_type=ResourceType.INFERENCE,
                total_capacity=50.0,
                available_capacity=50.0,
                allocated_amount=0.0
            )
        }
        
        self.resource_pools.update(default_pools)
    
    def _initialize_quotas(self):
        """Initialize resource quotas"""
        for resource_type, pool in self.resource_pools.items():
            self.quotas[resource_type] = ResourceQuota(
                resource_type=resource_type,
                max_allocation=pool.total_capacity,
                current_usage=0.0,
                reserved=0.0
            )
        
    def request_resource(self, resource_type: ResourceType, amount: float, 
                        priority: int = 1, deadline: float = None,
                        requester_id: str = None, duration_estimate: float = 0.0) -> str:
        """
        Request resource allocation
        
        Args:
            resource_type: Type of resource to request
            amount: Amount of resource needed
            priority: Request priority (1-10, higher = more urgent)
            deadline: Request deadline (Unix timestamp)
            requester_id: ID of the requesting agent
            duration_estimate: Estimated duration of resource usage
            
        Returns:
            Request ID
        """
        if deadline is None:
            deadline = time.time() + 3600  # Default 1 hour deadline
            
        if requester_id is None:
            requester_id = self.agent_id
            
        request_id = f"req_{int(time.time() * 1000000)}"
        
        request = ResourceRequest(
            request_id=request_id,
            requester_id=requester_id,
            resource_type=resource_type,
            amount=amount,
            priority=priority,
            deadline=deadline,
            duration_estimate=duration_estimate
        )
        
        with self.lock:
            self.pending_requests.append(request)
            self.metrics["requests_processed"] += 1
            
        # Try immediate allocation
        allocation_id = self._try_allocate_request(request)
        
        return request_id
        
    def _try_allocate_request(self, request: ResourceRequest) -> Optional[str]:
        """
        Try to allocate resources for a request
        
        Args:
            request: Resource request to allocate
            
        Returns:
            Allocation ID if successful, None otherwise
        """
        with self.lock:
            resource_pool = self.resource_pools.get(request.resource_type)
            quota = self.quotas.get(request.resource_type)
            
            if not resource_pool or not quota:
                return None
                
            # Check if enough resources are available
            if (resource_pool.available_capacity >= request.amount and
                quota.available >= request.amount):
                
                # Create allocation
                allocation_id = f"alloc_{int(time.time() * 1000000)}"
                
                # Calculate expiration time
                expires_at = request.deadline
                if request.duration_estimate > 0:
                    expires_at = min(expires_at, time.time() + request.duration_estimate)
                
                allocation = ResourceAllocation(
                    allocation_id=allocation_id,
                    request_id=request.request_id,
                    resource_type=request.resource_type,
                    amount=request.amount,
                    allocated_at=time.time(),
                    expires_at=expires_at,
                    provider_id=self.agent_id,
                    consumer_id=request.requester_id,
                    cost=self._calculate_resource_cost(request)
                )
                
                # Update resource pool and quota
                resource_pool.available_capacity -= request.amount
                resource_pool.allocated_amount += request.amount
                quota.current_usage += request.amount
                
                # Record allocation
                self.active_allocations[allocation_id] = allocation
                self.allocation_history.append(allocation)
                
                # Remove from pending requests
                self.pending_requests = [r for r in self.pending_requests 
                                       if r.request_id != request.request_id]
                
                # Update performance metrics
                self.performance_metrics["successful_allocations"] += 1
                self.metrics["allocations_made"] += 1
                
                return allocation_id
                
        return None
        
    def _calculate_resource_cost(self, request: ResourceRequest) -> float:
        """
        Calculate cost for resource allocation
        
        Args:
            request: Resource request
            
        Returns:
            Cost of the allocation
        """
        base_cost = request.amount * 0.1  # Base cost per unit
        
        # Priority multiplier
        priority_multiplier = 1.0 + (request.priority - 1) * 0.1
        
        # Urgency multiplier (closer to deadline = higher cost)
        time_remaining = max(0, request.deadline - time.time())
        urgency_multiplier = 1.0 + max(0, (3600 - time_remaining) / 3600)
        
        # Scarcity multiplier (less available = higher cost)
        resource_pool = self.resource_pools.get(request.resource_type)
        if resource_pool:
            scarcity = 1.0 - (resource_pool.available_capacity / resource_pool.total_capacity)
            scarcity_multiplier = 1.0 + scarcity
        else:
            scarcity_multiplier = 1.0
            
        total_cost = base_cost * priority_multiplier * urgency_multiplier * scarcity_multiplier
        return total_cost
        
    def release_resource(self, allocation_id: str) -> bool:
        """
        Release allocated resource
        
        Args:
            allocation_id: ID of allocation to release
            
        Returns:
            True if resource was released successfully
        """
        with self.lock:
            if allocation_id not in self.active_allocations:
                return False
                
            allocation = self.active_allocations[allocation_id]
            resource_pool = self.resource_pools.get(allocation.resource_type)
            quota = self.quotas.get(allocation.resource_type)
            
            if resource_pool and quota:
                # Return resources to pool
                resource_pool.available_capacity += allocation.amount
                resource_pool.allocated_amount -= allocation.amount
                quota.current_usage -= allocation.amount
                
                # Remove allocation
                del self.active_allocations[allocation_id]
                
                # Update performance metrics
                self.performance_metrics["releases"] += 1
                
                return True
                
        return False
        
    def process_pending_requests(self) -> int:
        """
        Process pending resource requests
        
        Returns:
            Number of requests processed
        """
        processed_count = 0
        
        with self.lock:
            # Sort requests by priority and deadline
            if self.strategy == AllocationStrategy.PRIORITY_BASED:
                self.pending_requests.sort(key=lambda r: (-r.priority, r.deadline))
            elif self.strategy == AllocationStrategy.FAIR_SHARE:
                # Simple round-robin for fair share
                pass
            elif self.strategy == AllocationStrategy.LOAD_BALANCED:
                # Sort by amount to balance load
                self.pending_requests.sort(key=lambda r: r.amount)
                
            # Try to allocate each pending request
            requests_to_process = list(self.pending_requests)
            
        for request in requests_to_process:
            # Check if deadline has passed
            if request.is_expired():
                with self.lock:
                    self.pending_requests = [r for r in self.pending_requests 
                                           if r.request_id != request.request_id]
                self.performance_metrics["expired_requests"] += 1
                continue
                
            # Try to allocate
            allocation_id = self._try_allocate_request(request)
            if allocation_id:
                processed_count += 1
                
        return processed_count
        
    def cleanup_expired_allocations(self) -> int:
        """
        Clean up expired resource allocations
        
        Returns:
            Number of allocations cleaned up
        """
        current_time = time.time()
        expired_allocations = []
        
        with self.lock:
            for allocation_id, allocation in self.active_allocations.items():
                if allocation.is_expired:
                    expired_allocations.append(allocation_id)
                    
        cleanup_count = 0
        for allocation_id in expired_allocations:
            if self.release_resource(allocation_id):
                cleanup_count += 1
                
        return cleanup_count
        
    def get_resource_utilization(self) -> Dict[str, Dict[str, float]]:
        """
        Get resource utilization statistics
        
        Returns:
            Resource utilization data
        """
        utilization = {}
        
        with self.lock:
            for resource_type, pool in self.resource_pools.items():
                utilization[resource_type.value] = {
                    "total_capacity": pool.total_capacity,
                    "available_capacity": pool.available_capacity,
                    "allocated_amount": pool.allocated_amount,
                    "utilization_rate": pool.allocated_amount / pool.total_capacity,
                    "availability_rate": pool.available_capacity / pool.total_capacity
                }
                
        return utilization
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the resource kernel
        
        Returns:
            Performance metrics
        """
        with self.lock:
            metrics = dict(self.performance_metrics)
            metrics.update(self.metrics)
            metrics.update({
                "active_allocations": len(self.active_allocations),
                "pending_requests": len(self.pending_requests),
                "total_allocations": len(self.allocation_history),
                "allocation_success_rate": (
                    metrics.get("successful_allocations", 0) / 
                    max(1, metrics.get("successful_allocations", 0) + metrics.get("expired_requests", 0))
                )
            })
            
        return metrics

    def register_mesh_node(self, node_id: str, node_info: Dict[str, Any]):
        """Register a mesh node for distributed operations"""
        with self.lock:
            self.mesh_nodes[node_id] = node_info
            
    def get_mesh_status(self) -> Dict[str, Any]:
        """Get status of the mesh network"""
        with self.lock:
            return {
                "local_node": self.node_id,
                "connected_nodes": len(self.mesh_nodes),
                "mesh_nodes": dict(self.mesh_nodes)
            }
        
    def optimize_allocations(self) -> Dict[str, Any]:
        """
        Optimize current resource allocations
        
        Returns:
            Optimization results
        """
        optimization_results = {
            "reallocated": 0,
            "freed_resources": 0.0,
            "efficiency_gain": 0.0
        }
        
        with self.lock:
            # Find underutilized allocations
            current_time = time.time()
            candidates_for_reallocation = []
            
            for allocation_id, allocation in self.active_allocations.items():
                # Check if allocation is near expiry or low priority
                time_remaining = allocation.expires_at - current_time
                if time_remaining < 300:  # Less than 5 minutes remaining
                    candidates_for_reallocation.append(allocation_id)
                    
            # Attempt to defragment allocations
            for allocation_id in candidates_for_reallocation:
                allocation = self.active_allocations.get(allocation_id)
                if allocation:
                    # Check if there are higher priority pending requests
                    high_priority_requests = [r for r in self.pending_requests 
                                            if r.priority > 7 and r.resource_type == allocation.resource_type]
                    
                    if high_priority_requests:
                        # Release this allocation to make room
                        if self.release_resource(allocation_id):
                            optimization_results["reallocated"] += 1
                            optimization_results["freed_resources"] += allocation.amount
                            
        return optimization_results
        
    def scheme_resource_spec(self) -> str:
        """
        Generate Scheme specification for resource management
        
        Returns:
            Scheme specification string
        """
        spec = """
(define (resource-request kernel type amount priority)
  (let ((request-id (generate-request-id)))
    (kernel-add-request kernel 
      (make-request request-id type amount priority (current-time)))
    request-id))

(define (resource-allocate kernel request)
  (let ((pool (kernel-get-pool kernel (request-type request))))
    (if (>= (pool-available pool) (request-amount request))
        (let ((allocation-id (generate-allocation-id)))
          (pool-allocate! pool (request-amount request))
          (kernel-add-allocation kernel allocation-id request)
          allocation-id)
        #f)))

(define (process-resource-requests kernel)
  (let ((allocated-count 0))
    (map (lambda (request)
           (when (resource-allocate kernel request)
             (set! allocated-count (+ allocated-count 1))))
         (kernel-pending-requests kernel))
    allocated-count))

(define (resource-optimize kernel)
  (let ((reallocated 0)
        (freed-resources 0.0))
    (map (lambda (allocation)
           (when (allocation-underutilized? allocation)
             (set! freed-resources (+ freed-resources (allocation-amount allocation)))
             (resource-release kernel (allocation-id allocation))
             (set! reallocated (+ reallocated 1))))
         (kernel-get-allocations kernel))
    (list reallocated freed-resources)))
"""
        return spec.strip()


class AttentionScheduler:
    """
    Attention scheduling system integrated with resource kernel
    """
    
    def __init__(self, resource_kernel: ResourceKernel):
        self.resource_kernel = resource_kernel
        self.attention_requests: deque = deque()
        self.active_attention_tasks: Dict[str, Dict[str, Any]] = {}
        self.attention_queue: List[Dict[str, Any]] = []  # For compatibility
        self.lock = threading.Lock()
        
    def schedule_attention(self, task_id: str, attention_amount: float,
                          priority: ResourcePriority = ResourcePriority.NORMAL,
                          duration: float = 60.0) -> bool:
        """
        Schedule attention allocation for a cognitive task
        
        Args:
            task_id: Unique identifier for the task
            attention_amount: Amount of attention required
            priority: Priority level for the task
            duration: Expected duration in seconds
            
        Returns:
            True if attention was successfully scheduled
        """
        request_id = self.resource_kernel.request_resource(
            resource_type=ResourceType.ATTENTION,
            amount=attention_amount,
            priority=priority.value,
            deadline=time.time() + duration,
            duration_estimate=duration
        )
        
        if request_id:
            with self.lock:
                self.attention_requests.append({
                    "task_id": task_id,
                    "request_id": request_id,
                    "amount": attention_amount,
                    "priority": priority,
                    "scheduled_at": time.time()
                })
            return True
            
        return False
    
    def schedule_attention_cycle(self, cycle_id: str, atoms: List[str], 
                               focus_strength: float = 1.0,
                               priority: ResourcePriority = ResourcePriority.NORMAL,
                               duration: float = 60.0) -> bool:
        """
        Schedule an attention cycle for multiple atoms (compatibility method)
        
        Args:
            cycle_id: Unique identifier for the cycle
            atoms: List of atoms to focus attention on
            focus_strength: Strength of attention focus
            priority: Priority level for the cycle
            duration: Expected duration in seconds
            
        Returns:
            True if cycle was scheduled successfully
        """
        total_attention = len(atoms) * focus_strength * 10.0
        
        # Schedule the resource request
        request_id = self.resource_kernel.request_resource(
            resource_type=ResourceType.ATTENTION,
            amount=total_attention,
            priority=priority.value,
            deadline=time.time() + duration,
            duration_estimate=duration
        )
        
        if request_id:
            with self.lock:
                cycle_info = {
                    "cycle_id": cycle_id,
                    "atoms": atoms,
                    "focus_strength": focus_strength,
                    "priority": priority,
                    "duration": duration,
                    "request_id": request_id,
                    "scheduled_at": time.time(),
                    "status": "queued"
                }
                self.attention_queue.append(cycle_info)
            return True
            
        return False
    
    def process_attention_queue(self) -> List[str]:
        """
        Process queued attention cycles (compatibility method)
        
        Returns:
            List of executed cycle IDs
        """
        executed_cycles = []
        
        with self.lock:
            for cycle in self.attention_queue:
                if cycle["status"] == "queued":
                    cycle["status"] = "executed"
                    cycle["executed_at"] = time.time()
                    executed_cycles.append(cycle["cycle_id"])
                    
        return executed_cycles
    
    def complete_attention_cycle(self, cycle_id: str) -> bool:
        """
        Mark an attention cycle as completed (compatibility method)
        
        Args:
            cycle_id: ID of the cycle to complete
            
        Returns:
            True if cycle was found and completed
        """
        with self.lock:
            for cycle in self.attention_queue:
                if cycle["cycle_id"] == cycle_id:
                    cycle["status"] = "completed"
                    cycle["completed_at"] = time.time()
                    return True
        return False
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """
        Get scheduler statistics (compatibility method)
        
        Returns:
            Scheduler statistics
        """
        with self.lock:
            queued_count = len([c for c in self.attention_queue if c["status"] == "queued"])
            active_count = len([c for c in self.attention_queue if c["status"] == "executed"])
            
            return {
                "queued_cycles": queued_count,
                "active_cycles": active_count,
                "total_cycles": len(self.attention_queue),
                "attention_requests": len(self.attention_requests)
            }
    
    def get_attention_status(self) -> Dict[str, Any]:
        """Get current attention allocation status"""
        with self.lock:
            return {
                "pending_requests": len(self.attention_requests),
                "active_tasks": len(self.active_attention_tasks),
                "total_attention_allocated": sum(
                    alloc.amount for alloc in self.resource_kernel.active_allocations.values()
                    if alloc.resource_type == ResourceType.ATTENTION
                )
            }


class DistributedResourceManager:
    """
    Manages resources across multiple distributed cognitive agents
    """
    
    def __init__(self):
        self.resource_kernels: Dict[str, ResourceKernel] = {}
        self.global_resource_view: Dict[ResourceType, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.resource_policies: Dict[str, Any] = {}
        self.rebalancing_history: List[Dict[str, Any]] = []
        self.executor = ThreadPoolExecutor(max_workers=8)
        
    def register_resource_kernel(self, agent_id: str, kernel: ResourceKernel):
        """
        Register a resource kernel from an agent
        
        Args:
            agent_id: ID of the agent
            kernel: Resource kernel to register
        """
        self.resource_kernels[agent_id] = kernel
        self._update_global_view()
        
    def unregister_resource_kernel(self, agent_id: str):
        """
        Unregister a resource kernel
        
        Args:
            agent_id: ID of the agent to unregister
        """
        if agent_id in self.resource_kernels:
            del self.resource_kernels[agent_id]
            self._update_global_view()
            
    def _update_global_view(self):
        """Update global view of resource availability"""
        # Reset global view
        self.global_resource_view.clear()
        
        # Aggregate resources from all kernels
        for agent_id, kernel in self.resource_kernels.items():
            utilization = kernel.get_resource_utilization()
            
            for resource_type_str, stats in utilization.items():
                resource_type = ResourceType(resource_type_str)
                self.global_resource_view[resource_type]["total"] += stats["total_capacity"]
                self.global_resource_view[resource_type]["available"] += stats["available_capacity"]
                self.global_resource_view[resource_type]["allocated"] += stats["allocated_amount"]
                
    def find_best_provider(self, resource_type: ResourceType, amount: float) -> Optional[str]:
        """
        Find the best provider for a resource request
        
        Args:
            resource_type: Type of resource needed
            amount: Amount of resource needed
            
        Returns:
            Agent ID of best provider, or None if no suitable provider
        """
        best_provider = None
        best_score = float('-inf')
        
        for agent_id, kernel in self.resource_kernels.items():
            utilization = kernel.get_resource_utilization()
            resource_stats = utilization.get(resource_type.value)
            
            if resource_stats and resource_stats["available_capacity"] >= amount:
                # Calculate provider score (higher is better)
                availability_ratio = resource_stats["availability_rate"]
                capacity_ratio = resource_stats["available_capacity"] / amount
                
                # Prefer providers with good availability and excess capacity
                score = availability_ratio * 0.6 + min(capacity_ratio, 2.0) * 0.4
                
                if score > best_score:
                    best_score = score
                    best_provider = agent_id
                    
        return best_provider
        
    def distributed_resource_request(self, requester_id: str, resource_type: ResourceType, 
                                   amount: float, priority: int = 1) -> Optional[str]:
        """
        Handle distributed resource request
        
        Args:
            requester_id: ID of requesting agent
            resource_type: Type of resource needed
            amount: Amount of resource needed
            priority: Request priority
            
        Returns:
            Allocation ID if successful, None otherwise
        """
        # Find best provider
        provider_id = self.find_best_provider(resource_type, amount)
        
        if provider_id and provider_id in self.resource_kernels:
            # Make request to provider
            provider_kernel = self.resource_kernels[provider_id]
            request_id = provider_kernel.request_resource(
                resource_type=resource_type,
                amount=amount,
                priority=priority,
                requester_id=requester_id
            )
            
            # Update global view
            self._update_global_view()
            
            return request_id
            
        return None
        
    def rebalance_resources(self) -> Dict[str, Any]:
        """
        Rebalance resources across the distributed mesh
        
        Returns:
            Rebalancing results
        """
        rebalancing_results = {
            "moves": 0,
            "total_amount_moved": 0.0,
            "efficiency_improvement": 0.0,
            "start_time": time.time()
        }
        
        # Update global view
        self._update_global_view()
        
        # Find imbalanced resources
        for resource_type, global_stats in self.global_resource_view.items():
            if global_stats["total"] == 0:
                continue
                
            global_utilization = global_stats["allocated"] / global_stats["total"]
            num_agents = len(self.resource_kernels)
            
            if num_agents < 2:
                continue
                
            # Find agents with significantly different utilization
            overloaded_agents = []
            underloaded_agents = []
            
            for agent_id, kernel in self.resource_kernels.items():
                utilization = kernel.get_resource_utilization()
                resource_stats = utilization.get(resource_type.value)
                
                if resource_stats:
                    agent_utilization = resource_stats["utilization_rate"]
                    
                    if agent_utilization > global_utilization + 0.2:  # 20% above average
                        overloaded_agents.append((agent_id, agent_utilization, resource_stats))
                    elif agent_utilization < global_utilization - 0.2:  # 20% below average
                        underloaded_agents.append((agent_id, agent_utilization, resource_stats))
                        
            # Attempt to move resources from overloaded to underloaded agents
            for overloaded_id, overload_util, overload_stats in overloaded_agents:
                for underloaded_id, underload_util, underload_stats in underloaded_agents:
                    # Calculate optimal move amount
                    excess_capacity = overload_stats["allocated_amount"] - (
                        overload_stats["total_capacity"] * global_utilization
                    )
                    available_capacity = underload_stats["available_capacity"]
                    
                    move_amount = min(excess_capacity * 0.5, available_capacity * 0.8)
                    
                    if move_amount > 0:
                        # Simulate resource move (in real implementation, this would involve
                        # complex negotiation and migration protocols)
                        rebalancing_results["moves"] += 1
                        rebalancing_results["total_amount_moved"] += move_amount
                        
        rebalancing_results["end_time"] = time.time()
        rebalancing_results["duration"] = rebalancing_results["end_time"] - rebalancing_results["start_time"]
        
        # Record rebalancing event
        self.rebalancing_history.append(rebalancing_results)
        
        return rebalancing_results
        
    def get_global_resource_stats(self) -> Dict[str, Any]:
        """
        Get global resource statistics
        
        Returns:
            Global resource statistics
        """
        self._update_global_view()
        
        stats = {
            "total_agents": len(self.resource_kernels),
            "resource_types": {}
        }
        
        for resource_type, global_stats in self.global_resource_view.items():
            if global_stats["total"] > 0:
                stats["resource_types"][resource_type.value] = {
                    "total_capacity": global_stats["total"],
                    "total_available": global_stats["available"],
                    "total_allocated": global_stats["allocated"],
                    "global_utilization": global_stats["allocated"] / global_stats["total"],
                    "global_availability": global_stats["available"] / global_stats["total"]
                }
                
        return stats
        
    def benchmark_resource_allocation(self, iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark distributed resource allocation performance
        
        Args:
            iterations: Number of benchmark iterations
            
        Returns:
            Benchmark results
        """
        if not self.resource_kernels:
            return {"error": "No resource kernels available"}
            
        start_time = time.time()
        
        successful_requests = 0
        failed_requests = 0
        total_allocation_time = 0.0
        
        # Prepare random test data
        resource_types = list(ResourceType)
        agent_ids = list(self.resource_kernels.keys())
        
        for i in range(iterations):
            # Random resource request
            resource_type = np.random.choice(resource_types)
            requester_id = np.random.choice(agent_ids)
            amount = np.random.uniform(1.0, 50.0)
            priority = np.random.randint(1, 11)
            
            # Measure allocation time
            alloc_start = time.time()
            
            allocation_id = self.distributed_resource_request(
                requester_id=requester_id,
                resource_type=resource_type,
                amount=amount,
                priority=priority
            )
            
            alloc_end = time.time()
            total_allocation_time += (alloc_end - alloc_start)
            
            if allocation_id:
                successful_requests += 1
            else:
                failed_requests += 1
                
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        avg_allocation_time = total_allocation_time / iterations if iterations > 0 else 0
        success_rate = successful_requests / iterations if iterations > 0 else 0
        requests_per_second = iterations / total_time if total_time > 0 else 0
        
        return {
            "total_time": total_time,
            "iterations": iterations,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "avg_allocation_time": avg_allocation_time,
            "requests_per_second": requests_per_second,
            "total_agents": len(self.resource_kernels),
            "global_stats": self.get_global_resource_stats()
        }
        
    def scheme_distributed_spec(self) -> str:
        """
        Generate Scheme specification for distributed resource management
        
        Returns:
            Scheme specification string
        """
        spec = """
(define (distributed-resource-find-provider managers type amount)
  (let ((best-provider #f)
        (best-score 0))
    (map (lambda (manager)
           (let ((score (manager-provider-score manager type amount)))
             (when (> score best-score)
               (set! best-score score)
               (set! best-provider manager))))
         managers)
    best-provider))

(define (resource-rebalance managers)
  (let ((moves 0))
    (map (lambda (type)
           (let ((overloaded (filter-overloaded managers type))
                 (underloaded (filter-underloaded managers type)))
             (set! moves (+ moves (rebalance-between overloaded underloaded)))))
         (list 'compute 'memory 'attention 'bandwidth 'storage))
    moves))
"""
        return spec.strip()
        
    def scheme_resource_spec(self) -> str:
        """
        Generate Scheme specification for distributed resource management
        (Alias for scheme_distributed_spec for compatibility)
        
        Returns:
            Scheme specification string
        """
        return self.scheme_distributed_spec()