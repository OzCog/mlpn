"""
ECAN Attention Allocation System

Implements economic attention allocation with cognitive 'wages' and 'rents',
activation spreading, and attention tensor visualization.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import json
from collections import defaultdict


class AttentionType(Enum):
    """Types of attention allocation"""
    STI = "short_term_importance"  # Short-term importance
    LTI = "long_term_importance"   # Long-term importance
    VLTI = "very_long_term_importance"  # Very long-term importance


@dataclass
class AttentionValue:
    """Attention value for an atom"""
    sti: float = 0.0  # Short-term importance
    lti: float = 0.0  # Long-term importance
    vlti: float = 0.0  # Very long-term importance
    
    def total_attention(self) -> float:
        """Calculate total attention value"""
        return self.sti + self.lti + self.vlti


@dataclass
class EconomicParams:
    """Economic parameters for attention allocation"""
    wage_fund: float = 100.0  # Total wages available
    rent_fund: float = 50.0   # Total rents available
    min_wage: float = 1.0     # Minimum wage
    max_wage: float = 10.0    # Maximum wage
    decay_rate: float = 0.95  # Attention decay rate
    spreading_factor: float = 0.1  # Activation spreading factor


class AttentionBank:
    """
    Manages attention allocation and economic resources
    """
    
    def __init__(self, params: EconomicParams = None):
        self.params = params or EconomicParams()
        self.attention_values: Dict[str, AttentionValue] = {}
        self.last_activation: Dict[str, float] = {}
        self.wages: Dict[str, float] = {}
        self.rents: Dict[str, float] = {}
        self.activation_history: Dict[str, List[float]] = defaultdict(list)
        
    def allocate_attention(self, atom_id: str, 
                          attention_type: AttentionType, 
                          value: float) -> None:
        """
        Allocate attention to an atom
        
        Args:
            atom_id: ID of the atom
            attention_type: Type of attention
            value: Attention value to allocate
        """
        if atom_id not in self.attention_values:
            self.attention_values[atom_id] = AttentionValue()
            
        current_time = time.time()
        self.last_activation[atom_id] = current_time
        
        # Update attention value
        attention_val = self.attention_values[atom_id]
        if attention_type == AttentionType.STI:
            attention_val.sti += value
        elif attention_type == AttentionType.LTI:
            attention_val.lti += value
        elif attention_type == AttentionType.VLTI:
            attention_val.vlti += value
            
        # Record activation
        self.activation_history[atom_id].append(current_time)
        
    def calculate_utility(self, atom_id: str) -> float:
        """
        Calculate utility of an atom for wage calculation
        
        Args:
            atom_id: ID of the atom
            
        Returns:
            Utility value
        """
        if atom_id not in self.attention_values:
            return 0.0
            
        attention = self.attention_values[atom_id]
        
        # Utility based on attention and recency
        base_utility = attention.total_attention()
        
        # Recency factor
        if atom_id in self.last_activation:
            time_since_activation = time.time() - self.last_activation[atom_id]
            recency_factor = np.exp(-time_since_activation / 3600)  # Decay over 1 hour
            base_utility *= recency_factor
            
        return base_utility
        
    def calculate_novelty(self, atom_id: str) -> float:
        """
        Calculate novelty of an atom
        
        Args:
            atom_id: ID of the atom
            
        Returns:
            Novelty value
        """
        if atom_id not in self.activation_history:
            return 1.0  # New atoms are highly novel
            
        history = self.activation_history[atom_id]
        if len(history) < 2:
            return 1.0
            
        # Calculate novelty based on activation frequency
        recent_activations = len([t for t in history if time.time() - t < 3600])
        novelty = 1.0 / (1.0 + recent_activations)
        
        return novelty
        
    def allocate_wages(self) -> None:
        """Allocate wages to atoms based on utility"""
        if not self.attention_values:
            return
            
        # Calculate utilities for all atoms
        utilities = {}
        for atom_id in self.attention_values.keys():
            utilities[atom_id] = self.calculate_utility(atom_id)
            
        # Total utility
        total_utility = sum(utilities.values())
        if total_utility == 0:
            return
            
        # Allocate wages proportionally
        for atom_id, utility in utilities.items():
            wage_proportion = utility / total_utility
            wage = (self.params.wage_fund * wage_proportion)
            wage = max(self.params.min_wage, min(self.params.max_wage, wage))
            self.wages[atom_id] = wage
            
    def allocate_rents(self) -> None:
        """Allocate rents to atoms based on novelty"""
        if not self.attention_values:
            return
            
        # Calculate novelties for all atoms
        novelties = {}
        for atom_id in self.attention_values.keys():
            novelties[atom_id] = self.calculate_novelty(atom_id)
            
        # Total novelty
        total_novelty = sum(novelties.values())
        if total_novelty == 0:
            return
            
        # Allocate rents proportionally
        for atom_id, novelty in novelties.items():
            rent_proportion = novelty / total_novelty
            rent = self.params.rent_fund * rent_proportion
            self.rents[atom_id] = rent
            
    def get_attention_tensor(self, atom_ids: List[str]) -> np.ndarray:
        """
        Get attention tensor for visualization
        
        Args:
            atom_ids: List of atom IDs
            
        Returns:
            Attention tensor
        """
        if not atom_ids:
            return np.array([])
            
        tensor = np.zeros((len(atom_ids), 3))  # STI, LTI, VLTI
        
        for i, atom_id in enumerate(atom_ids):
            if atom_id in self.attention_values:
                attention = self.attention_values[atom_id]
                tensor[i] = [attention.sti, attention.lti, attention.vlti]
                
        return tensor
        
    def decay_attention(self) -> None:
        """Apply decay to attention values"""
        for atom_id in self.attention_values:
            attention = self.attention_values[atom_id]
            attention.sti *= self.params.decay_rate
            attention.lti *= self.params.decay_rate
            attention.vlti *= self.params.decay_rate


class ActivationSpreading:
    """
    Implements activation spreading mechanism similar to PageRank
    """
    
    def __init__(self, atomspace_connections: Dict[str, List[str]]):
        self.connections = atomspace_connections
        self.activation_levels: Dict[str, float] = {}
        self.damping_factor = 0.85  # Similar to PageRank damping
        
    def initialize_activation(self, atom_ids: List[str], 
                            initial_activation: float = 1.0) -> None:
        """
        Initialize activation levels for atoms
        
        Args:
            atom_ids: List of atom IDs
            initial_activation: Initial activation level
        """
        for atom_id in atom_ids:
            self.activation_levels[atom_id] = initial_activation
            
    def spread_activation(self, iterations: int = 10) -> None:
        """
        Spread activation across the network
        
        Args:
            iterations: Number of spreading iterations
        """
        for _ in range(iterations):
            new_activations = {}
            
            for atom_id in self.activation_levels:
                # Base activation (like PageRank's random jump)
                base_activation = (1 - self.damping_factor) / len(self.activation_levels)
                
                # Spread activation from connected atoms
                spread_activation = 0.0
                for connected_atom in self.connections.get(atom_id, []):
                    if connected_atom in self.activation_levels:
                        # Normalize by number of outgoing connections
                        num_connections = len(self.connections.get(connected_atom, []))
                        if num_connections > 0:
                            spread_activation += (self.activation_levels[connected_atom] / 
                                                num_connections)
                            
                new_activations[atom_id] = (base_activation + 
                                          self.damping_factor * spread_activation)
                
            self.activation_levels = new_activations
            
    def get_top_activated(self, n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top N activated atoms
        
        Args:
            n: Number of top atoms to return
            
        Returns:
            List of (atom_id, activation_level) tuples
        """
        sorted_atoms = sorted(self.activation_levels.items(), 
                            key=lambda x: x[1], reverse=True)
        return sorted_atoms[:n]


class AttentionVisualizer:
    """
    Visualizes attention allocation and spreads
    """
    
    def __init__(self):
        self.attention_history: List[Dict[str, float]] = []
        
    def record_attention_state(self, attention_bank: AttentionBank) -> None:
        """
        Record current attention state for visualization
        
        Args:
            attention_bank: Attention bank to record from
        """
        state = {}
        for atom_id, attention in attention_bank.attention_values.items():
            state[atom_id] = attention.total_attention()
            
        self.attention_history.append(state)
        
    def get_attention_dynamics(self) -> Dict[str, List[float]]:
        """
        Get attention dynamics over time
        
        Returns:
            Dictionary mapping atom IDs to attention time series
        """
        dynamics = defaultdict(list)
        
        for state in self.attention_history:
            for atom_id, attention in state.items():
                dynamics[atom_id].append(attention)
                
        return dict(dynamics)
        
    def generate_attention_summary(self) -> Dict[str, Any]:
        """
        Generate summary of attention allocation
        
        Returns:
            Attention summary statistics
        """
        if not self.attention_history:
            return {}
            
        # Get latest state
        latest_state = self.attention_history[-1]
        
        # Calculate statistics
        attentions = list(latest_state.values())
        
        return {
            "total_atoms": len(latest_state),
            "total_attention": sum(attentions),
            "mean_attention": np.mean(attentions),
            "std_attention": np.std(attentions),
            "max_attention": max(attentions) if attentions else 0,
            "min_attention": min(attentions) if attentions else 0,
            "history_length": len(self.attention_history)
        }


class ECANAttention:
    """
    Main ECAN attention allocation system
    """
    
    def __init__(self, atomspace_connections: Dict[str, List[str]] = None):
        self.attention_bank = AttentionBank()
        self.connections = atomspace_connections or {}
        self.activation_spreader = ActivationSpreading(self.connections)
        self.visualizer = AttentionVisualizer()
        
    def focus_attention(self, atom_id: str, focus_strength: float = 1.0) -> None:
        """
        Focus attention on a specific atom
        
        Args:
            atom_id: ID of the atom to focus on
            focus_strength: Strength of focus
        """
        # Allocate immediate attention
        self.attention_bank.allocate_attention(
            atom_id, AttentionType.STI, focus_strength
        )
        
        # Spread activation to connected atoms
        if atom_id in self.connections:
            for connected_atom in self.connections[atom_id]:
                spread_strength = focus_strength * self.attention_bank.params.spreading_factor
                self.attention_bank.allocate_attention(
                    connected_atom, AttentionType.STI, spread_strength
                )
                
    def update_attention_economy(self) -> None:
        """Update the attention economy by allocating wages and rents"""
        self.attention_bank.allocate_wages()
        self.attention_bank.allocate_rents()
        self.attention_bank.decay_attention()
        
        # Record state for visualization
        self.visualizer.record_attention_state(self.attention_bank)
        
    def get_attention_focus(self, n: int = 10) -> List[Tuple[str, float]]:
        """
        Get current attention focus
        
        Args:
            n: Number of top focused atoms to return
            
        Returns:
            List of (atom_id, attention_value) tuples
        """
        focus_list = []
        for atom_id, attention in self.attention_bank.attention_values.items():
            focus_list.append((atom_id, attention.total_attention()))
            
        return sorted(focus_list, key=lambda x: x[1], reverse=True)[:n]
        
    def visualize_attention_tensor(self, atom_ids: List[str]) -> np.ndarray:
        """
        Create attention tensor for visualization
        
        Args:
            atom_ids: List of atom IDs
            
        Returns:
            Attention tensor
        """
        return self.attention_bank.get_attention_tensor(atom_ids)
        
    def get_economic_stats(self) -> Dict[str, Any]:
        """Get economic statistics"""
        return {
            "total_wages": sum(self.attention_bank.wages.values()),
            "total_rents": sum(self.attention_bank.rents.values()),
            "wage_fund": self.attention_bank.params.wage_fund,
            "rent_fund": self.attention_bank.params.rent_fund,
            "attention_summary": self.visualizer.generate_attention_summary()
        }
        
    def run_attention_cycle(self, focus_atoms: List[str] = None) -> None:
        """
        Run a complete attention allocation cycle
        
        Args:
            focus_atoms: List of atoms to focus on
        """
        # Focus on specified atoms
        if focus_atoms:
            for atom_id in focus_atoms:
                self.focus_attention(atom_id)
                
        # Run activation spreading
        if self.activation_spreader.activation_levels:
            self.activation_spreader.spread_activation()
            
        # Update attention economy
        self.update_attention_economy()
        
    def scheme_attention_spec(self) -> str:
        """
        Generate Scheme specification for attention allocation
        
        Returns:
            Scheme specification string
        """
        spec = """
(define (attention-allocate atom-id type value)
  (let ((current-attention (get-attention atom-id)))
    (set-attention atom-id 
      (+ current-attention (* value (attention-weight type))))))

(define (attention-spread atom-id connections)
  (map (lambda (connected-atom)
         (attention-allocate connected-atom 'sti 
           (* (get-attention atom-id) spreading-factor)))
       connections))

(define (attention-focus atoms)
  (map (lambda (atom-id)
         (attention-allocate atom-id 'sti focus-strength))
       atoms))
"""
        return spec.strip()