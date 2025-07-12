"""
Tensor Fragment Architecture

Implements distributed tensor fragment system for Phase 1 cognitive primitives.
Provides tensor composition/decomposition, fragment synchronization, and 
distributed parallel processing capabilities.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import uuid
import threading
import time

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tensor_kernel import TensorKernel, TensorFormat


class FragmentType(Enum):
    """Types of tensor fragments"""
    COGNITIVE = "cognitive"
    ATTENTION = "attention"
    GRAMMAR = "grammar"
    META = "meta"
    HYBRID = "hybrid"


class SyncState(Enum):
    """Fragment synchronization states"""
    SYNCHRONIZED = "synchronized"
    PENDING = "pending"
    DIRTY = "dirty"
    CONFLICT = "conflict"


@dataclass
class FragmentMetadata:
    """Metadata for tensor fragments"""
    fragment_id: str
    fragment_type: FragmentType
    shape: Tuple[int, ...]
    dtype: str
    created_at: float
    last_modified: float
    sync_state: SyncState
    parent_fragments: List[str]
    child_fragments: List[str]
    dependencies: List[str]


@dataclass
class TensorFragment:
    """Individual tensor fragment with metadata"""
    metadata: FragmentMetadata
    data: np.ndarray
    version: int
    checksum: str
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._compute_checksum()
    
    def _compute_checksum(self) -> str:
        """Compute checksum for fragment data"""
        return str(hash(self.data.tobytes()))
    
    def is_stale(self, other_checksum: str) -> bool:
        """Check if fragment is stale compared to another version"""
        return self.checksum != other_checksum
    
    def update_data(self, new_data: np.ndarray):
        """Update fragment data and metadata"""
        self.data = new_data
        self.version += 1
        self.checksum = self._compute_checksum()
        self.metadata.last_modified = time.time()
        self.metadata.sync_state = SyncState.DIRTY


class FragmentRegistry:
    """Registry for managing tensor fragments"""
    
    def __init__(self):
        self.fragments: Dict[str, TensorFragment] = {}
        self.type_index: Dict[FragmentType, List[str]] = {
            ft: [] for ft in FragmentType
        }
        self.dependency_graph: Dict[str, List[str]] = {}
        self._lock = threading.Lock()
    
    def register_fragment(self, fragment: TensorFragment) -> str:
        """Register a new tensor fragment"""
        with self._lock:
            fragment_id = fragment.metadata.fragment_id
            self.fragments[fragment_id] = fragment
            self.type_index[fragment.metadata.fragment_type].append(fragment_id)
            self.dependency_graph[fragment_id] = fragment.metadata.dependencies.copy()
            return fragment_id
    
    def get_fragment(self, fragment_id: str) -> Optional[TensorFragment]:
        """Get fragment by ID"""
        return self.fragments.get(fragment_id)
    
    def get_fragments_by_type(self, fragment_type: FragmentType) -> List[TensorFragment]:
        """Get all fragments of a specific type"""
        fragment_ids = self.type_index.get(fragment_type, [])
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def get_dependent_fragments(self, fragment_id: str) -> List[TensorFragment]:
        """Get fragments that depend on the given fragment"""
        dependents = []
        for fid, deps in self.dependency_graph.items():
            if fragment_id in deps:
                fragment = self.fragments.get(fid)
                if fragment:
                    dependents.append(fragment)
        return dependents
    
    def mark_dirty_cascade(self, fragment_id: str):
        """Mark fragment and all dependents as dirty"""
        with self._lock:
            fragment = self.fragments.get(fragment_id)
            if fragment:
                fragment.metadata.sync_state = SyncState.DIRTY
                
                # Cascade to dependents
                for dependent in self.get_dependent_fragments(fragment_id):
                    dependent.metadata.sync_state = SyncState.DIRTY


class TensorFragmentArchitecture:
    """
    Main tensor fragment architecture system
    
    Provides distributed tensor operations with fragment management,
    composition/decomposition, and synchronization capabilities.
    """
    
    def __init__(self, tensor_kernel: TensorKernel = None):
        self.tensor_kernel = tensor_kernel or TensorKernel()
        self.registry = FragmentRegistry()
        self.composition_cache: Dict[str, TensorFragment] = {}
        self.sync_threads: Dict[str, threading.Thread] = {}
        self._operation_count = 0
    
    def create_fragment(self, 
                       data: np.ndarray,
                       fragment_type: FragmentType,
                       dependencies: List[str] = None) -> str:
        """
        Create a new tensor fragment
        
        Args:
            data: Tensor data for the fragment
            fragment_type: Type of the fragment
            dependencies: List of fragment IDs this depends on
            
        Returns:
            Fragment ID
        """
        fragment_id = str(uuid.uuid4())
        
        metadata = FragmentMetadata(
            fragment_id=fragment_id,
            fragment_type=fragment_type,
            shape=data.shape,
            dtype=str(data.dtype),
            created_at=time.time(),
            last_modified=time.time(),
            sync_state=SyncState.SYNCHRONIZED,
            parent_fragments=[],
            child_fragments=[],
            dependencies=dependencies or []
        )
        
        fragment = TensorFragment(
            metadata=metadata,
            data=data.copy(),
            version=1,
            checksum=""
        )
        
        return self.registry.register_fragment(fragment)
    
    def decompose_tensor(self, 
                        tensor: np.ndarray,
                        fragment_scheme: Dict[str, Any]) -> List[str]:
        """
        Decompose tensor into multiple fragments
        
        Args:
            tensor: Tensor to decompose
            fragment_scheme: Scheme defining how to fragment
            
        Returns:
            List of fragment IDs
        """
        fragments = []
        scheme_type = fragment_scheme.get("type", "grid")
        
        if scheme_type == "grid":
            # Grid-based decomposition
            grid_shape = fragment_scheme.get("grid_shape", (2, 2))
            fragment_tensors = self._grid_decompose(tensor, grid_shape)
            
            for i, fragment_tensor in enumerate(fragment_tensors):
                fragment_id = self.create_fragment(
                    fragment_tensor,
                    FragmentType.COGNITIVE,
                    dependencies=[]
                )
                fragments.append(fragment_id)
                
        elif scheme_type == "hierarchical":
            # Hierarchical decomposition
            levels = fragment_scheme.get("levels", 2)
            fragment_tensors = self._hierarchical_decompose(tensor, levels)
            
            # Create fragments with dependency relationships
            for level_fragments in fragment_tensors:
                level_ids = []
                for fragment_tensor in level_fragments:
                    fragment_id = self.create_fragment(
                        fragment_tensor,
                        FragmentType.COGNITIVE,
                        dependencies=fragments[-len(level_ids):] if fragments else []
                    )
                    level_ids.append(fragment_id)
                fragments.extend(level_ids)
        
        return fragments
    
    def compose_fragments(self, fragment_ids: List[str]) -> np.ndarray:
        """
        Compose multiple fragments into a single tensor
        
        Args:
            fragment_ids: List of fragment IDs to compose
            
        Returns:
            Composed tensor
        """
        # Check cache first
        cache_key = "|".join(sorted(fragment_ids))
        if cache_key in self.composition_cache:
            cached_fragment = self.composition_cache[cache_key]
            return cached_fragment.data.copy()
        
        fragments = [self.registry.get_fragment(fid) for fid in fragment_ids]
        fragments = [f for f in fragments if f is not None]
        
        if not fragments:
            raise ValueError("No valid fragments found")
        
        # Determine composition strategy based on fragment metadata
        composed_tensor = self._compose_by_shape_compatibility(fragments)
        
        # Cache the result
        cache_fragment = TensorFragment(
            metadata=FragmentMetadata(
                fragment_id=cache_key,
                fragment_type=FragmentType.HYBRID,
                shape=composed_tensor.shape,
                dtype=str(composed_tensor.dtype),
                created_at=time.time(),
                last_modified=time.time(),
                sync_state=SyncState.SYNCHRONIZED,
                parent_fragments=fragment_ids,
                child_fragments=[],
                dependencies=fragment_ids
            ),
            data=composed_tensor,
            version=1,
            checksum=""
        )
        
        self.composition_cache[cache_key] = cache_fragment
        return composed_tensor
    
    def fragment_contraction(self, 
                           fragment_id1: str, 
                           fragment_id2: str,
                           axes: Optional[List[int]] = None) -> str:
        """
        Perform tensor contraction between fragments
        
        Args:
            fragment_id1: First fragment ID
            fragment_id2: Second fragment ID
            axes: Contraction axes
            
        Returns:
            Result fragment ID
        """
        fragment1 = self.registry.get_fragment(fragment_id1)
        fragment2 = self.registry.get_fragment(fragment_id2)
        
        if not fragment1 or not fragment2:
            raise ValueError("Invalid fragment IDs")
        
        # Perform contraction using tensor kernel
        result_tensor = self.tensor_kernel.tensor_contraction(
            fragment1.data, fragment2.data, axes
        )
        
        # Create result fragment
        result_id = self.create_fragment(
            result_tensor,
            FragmentType.HYBRID,
            dependencies=[fragment_id1, fragment_id2]
        )
        
        self._operation_count += 1
        return result_id
    
    def parallel_fragment_operation(self, 
                                  operation: str,
                                  fragment_ids: List[str],
                                  **kwargs) -> str:
        """
        Execute parallel operation across multiple fragments
        
        Args:
            operation: Operation name
            fragment_ids: List of fragment IDs
            **kwargs: Additional operation parameters
            
        Returns:
            Result fragment ID
        """
        fragments = [self.registry.get_fragment(fid) for fid in fragment_ids]
        fragments = [f for f in fragments if f is not None]
        
        if not fragments:
            raise ValueError("No valid fragments found")
        
        # Extract tensor data
        tensors = [f.data for f in fragments]
        
        # Perform parallel operation
        result_tensor = self.tensor_kernel.parallel_operation(
            operation, tensors, **kwargs
        )
        
        # Create result fragment
        result_id = self.create_fragment(
            result_tensor,
            FragmentType.HYBRID,
            dependencies=fragment_ids
        )
        
        self._operation_count += 1
        return result_id
    
    def synchronize_fragments(self, fragment_ids: List[str] = None):
        """
        Synchronize fragments across distributed system
        
        Args:
            fragment_ids: Specific fragments to sync, or None for all
        """
        if fragment_ids is None:
            fragment_ids = list(self.registry.fragments.keys())
        
        for fragment_id in fragment_ids:
            self._synchronize_single_fragment(fragment_id)
    
    def _synchronize_single_fragment(self, fragment_id: str):
        """Synchronize a single fragment"""
        fragment = self.registry.get_fragment(fragment_id)
        if not fragment:
            return
        
        # Mark as pending sync
        fragment.metadata.sync_state = SyncState.PENDING
        
        # In a real distributed system, this would sync with remote nodes
        # For now, we just mark as synchronized
        time.sleep(0.001)  # Simulate sync delay
        fragment.metadata.sync_state = SyncState.SYNCHRONIZED
    
    def _grid_decompose(self, tensor: np.ndarray, grid_shape: Tuple[int, int]) -> List[np.ndarray]:
        """Decompose tensor using grid scheme"""
        rows, cols = grid_shape
        h, w = tensor.shape[0] // rows, tensor.shape[1] // cols
        
        fragments = []
        for i in range(rows):
            for j in range(cols):
                fragment = tensor[i*h:(i+1)*h, j*w:(j+1)*w]
                fragments.append(fragment)
        
        return fragments
    
    def _hierarchical_decompose(self, tensor: np.ndarray, levels: int) -> List[List[np.ndarray]]:
        """Decompose tensor hierarchically"""
        result = []
        current_tensors = [tensor]
        
        for level in range(levels):
            next_level = []
            for t in current_tensors:
                if t.size > 4:  # Only decompose if large enough
                    mid_h, mid_w = t.shape[0] // 2, t.shape[1] // 2
                    if mid_h > 0 and mid_w > 0:
                        fragments = [
                            t[:mid_h, :mid_w],
                            t[:mid_h, mid_w:],
                            t[mid_h:, :mid_w],
                            t[mid_h:, mid_w:]
                        ]
                        next_level.extend(fragments)
                    else:
                        next_level.append(t)
                else:
                    next_level.append(t)
            
            result.append(next_level)
            current_tensors = next_level
        
        return result
    
    def _compose_by_shape_compatibility(self, fragments: List[TensorFragment]) -> np.ndarray:
        """Compose fragments based on shape compatibility"""
        if len(fragments) == 1:
            return fragments[0].data
        
        # Sort by creation time for consistent composition
        fragments.sort(key=lambda f: f.metadata.created_at)
        
        # Try different composition strategies
        try:
            # Stack strategy
            return np.stack([f.data for f in fragments])
        except ValueError:
            try:
                # Concatenate strategy
                return np.concatenate([f.data for f in fragments])
            except ValueError:
                # Sum strategy as fallback
                base_shape = fragments[0].data.shape
                result = np.zeros(base_shape)
                for fragment in fragments:
                    if fragment.data.shape == base_shape:
                        result += fragment.data
                return result
    
    def get_fragment_stats(self) -> Dict[str, Any]:
        """Get fragment architecture statistics"""
        return {
            "total_fragments": len(self.registry.fragments),
            "fragments_by_type": {
                ft.value: len(self.registry.type_index[ft])
                for ft in FragmentType
            },
            "total_operations": self._operation_count,
            "cache_size": len(self.composition_cache),
            "sync_states": self._get_sync_state_counts()
        }
    
    def _get_sync_state_counts(self) -> Dict[str, int]:
        """Get count of fragments by sync state"""
        counts = {state.value: 0 for state in SyncState}
        for fragment in self.registry.fragments.values():
            counts[fragment.metadata.sync_state.value] += 1
        return counts
    
    def generate_scheme_fragment_spec(self, fragment_id: str) -> str:
        """
        Generate Scheme specification for fragment operations
        
        Args:
            fragment_id: Fragment ID
            
        Returns:
            Scheme specification string
        """
        fragment = self.registry.get_fragment(fragment_id)
        if not fragment:
            return f"(define (fragment-spec {fragment_id}) 'not-found)"
        
        scheme_spec = f"""(define (fragment-spec {fragment_id})
  '((id "{fragment.metadata.fragment_id}")
    (type {fragment.metadata.fragment_type.value})
    (shape {list(fragment.metadata.shape)})
    (version {fragment.version})
    (sync-state {fragment.metadata.sync_state.value})
    (dependencies {fragment.metadata.dependencies})))

(define (fragment-compose {fragment_id} other-fragments)
  (let ((fragment (get-fragment {fragment_id}))
        (others (map get-fragment other-fragments)))
    (compose-tensors (cons fragment others))))

(define (fragment-contract {fragment_id} other-id axes)
  (tensor-contract 
    (get-fragment {fragment_id}) 
    (get-fragment other-id) 
    axes))"""
        
        return scheme_spec