"""
Cognitive Grammar Field

Implements AtomSpace for hypergraph knowledge representation, PLN for probabilistic logic,
and template-based pattern recognition. Integrates memory systems for symbolic and
sub-symbolic storage.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from collections import defaultdict


class AtomType(Enum):
    """Types of atoms in the hypergraph"""
    CONCEPT = "concept"
    PREDICATE = "predicate"
    LINK = "link"
    VARIABLE = "variable"
    SCHEMA = "schema"


class LinkType(Enum):
    """Types of links in the hypergraph"""
    INHERITANCE = "inheritance"
    SIMILARITY = "similarity"
    MEMBER = "member"
    SUBSET = "subset"
    IMPLICATION = "implication"
    EQUIVALENCE = "equivalence"
    EVALUATION = "evaluation"


@dataclass
class TruthValue:
    """Probabilistic truth value for PLN"""
    strength: float  # Probability/confidence
    confidence: float  # Certainty of the estimate
    
    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class Atom:
    """Base atom in the hypergraph"""
    id: str
    name: str
    atom_type: AtomType
    truth_value: TruthValue
    prime_index: int = 0  # Prime-factorized index for density
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class Link:
    """Link between atoms in the hypergraph"""
    id: str
    link_type: LinkType
    atoms: List[str]  # List of atom IDs
    truth_value: TruthValue
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class AtomSpace:
    """
    Hypergraph knowledge representation system
    Implements ERP entity representation with prime-factorized indexing
    """
    
    def __init__(self):
        self.atoms: Dict[str, Atom] = {}
        self.links: Dict[str, Link] = {}
        self.prime_indices: Dict[int, str] = {}  # Prime -> atom_id mapping
        self.next_prime = 2
        self._atom_type_index: Dict[AtomType, Set[str]] = defaultdict(set)
        self._link_type_index: Dict[LinkType, Set[str]] = defaultdict(set)
        
    def add_atom(self, name: str, atom_type: AtomType, 
                 truth_value: TruthValue = None) -> str:
        """
        Add atom to the hypergraph
        
        Args:
            name: Atom name
            atom_type: Type of atom
            truth_value: Truth value for PLN
            
        Returns:
            Atom ID
        """
        if truth_value is None:
            truth_value = TruthValue(strength=0.5, confidence=0.5)
            
        atom = Atom(
            id="",
            name=name,
            atom_type=atom_type,
            truth_value=truth_value,
            prime_index=self._get_next_prime()
        )
        
        self.atoms[atom.id] = atom
        self.prime_indices[atom.prime_index] = atom.id
        self._atom_type_index[atom_type].add(atom.id)
        
        return atom.id
        
    def add_link(self, link_type: LinkType, atom_ids: List[str],
                 truth_value: TruthValue = None) -> str:
        """
        Add link between atoms
        
        Args:
            link_type: Type of link
            atom_ids: List of atom IDs to link
            truth_value: Truth value for PLN
            
        Returns:
            Link ID
        """
        if truth_value is None:
            truth_value = TruthValue(strength=0.5, confidence=0.5)
            
        link = Link(
            id="",
            link_type=link_type,
            atoms=atom_ids,
            truth_value=truth_value
        )
        
        self.links[link.id] = link
        self._link_type_index[link_type].add(link.id)
        
        return link.id
        
    def get_atom(self, atom_id: str) -> Optional[Atom]:
        """Get atom by ID"""
        return self.atoms.get(atom_id)
        
    def get_link(self, link_id: str) -> Optional[Link]:
        """Get link by ID"""
        return self.links.get(link_id)
        
    def find_atoms_by_type(self, atom_type: AtomType) -> List[Atom]:
        """Find all atoms of a specific type"""
        atom_ids = self._atom_type_index[atom_type]
        return [self.atoms[aid] for aid in atom_ids]
        
    def find_links_by_type(self, link_type: LinkType) -> List[Link]:
        """Find all links of a specific type"""
        link_ids = self._link_type_index[link_type]
        return [self.links[lid] for lid in link_ids]
        
    def get_connected_atoms(self, atom_id: str) -> List[Tuple[str, LinkType]]:
        """Get atoms connected to the given atom"""
        connected = []
        for link in self.links.values():
            if atom_id in link.atoms:
                for other_atom_id in link.atoms:
                    if other_atom_id != atom_id:
                        connected.append((other_atom_id, link.link_type))
        return connected
        
    def _get_next_prime(self) -> int:
        """Get next prime number for indexing"""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
            
        while not is_prime(self.next_prime):
            self.next_prime += 1
            
        prime = self.next_prime
        self.next_prime += 1
        return prime
        
    def get_hypergraph_density(self) -> float:
        """Calculate hypergraph density using prime factorization"""
        if not self.atoms:
            return 0.0
            
        # Calculate density based on prime indices
        prime_product = 1
        for prime in self.prime_indices.keys():
            prime_product *= prime
            
        # Normalize by number of atoms
        if len(self.atoms) == 0:
            return 0.0
        
        # Handle large prime products to avoid overflow
        try:
            if prime_product > 1e10:  # Too large for safe float conversion
                # Use log properties: log(a*b) = log(a) + log(b)
                log_sum = 0.0
                for prime in self.prime_indices.keys():
                    log_sum += np.log(float(prime))
                density = log_sum / len(self.atoms)
            else:
                density = np.log(float(prime_product)) / len(self.atoms)
            return density
        except (OverflowError, ValueError):
            # Fallback for very large numbers
            return np.log(len(self.prime_indices)) if len(self.prime_indices) > 0 else 0.0


class PLN:
    """
    Probabilistic Logic Networks for deduction, induction, and abduction
    """
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        
    def deduction(self, premise1_id: str, premise2_id: str) -> TruthValue:
        """
        Deductive inference: A->B, B->C => A->C
        
        Args:
            premise1_id: First premise link ID
            premise2_id: Second premise link ID
            
        Returns:
            Truth value of conclusion
        """
        link1 = self.atomspace.get_link(premise1_id)
        link2 = self.atomspace.get_link(premise2_id)
        
        if not link1 or not link2:
            return TruthValue(0.0, 0.0)
            
        # Simple deduction rule
        s1, c1 = link1.truth_value.strength, link1.truth_value.confidence
        s2, c2 = link2.truth_value.strength, link2.truth_value.confidence
        
        # Deduction formula
        strength = s1 * s2
        confidence = c1 * c2 * 0.9  # Slight confidence reduction
        
        return TruthValue(strength, confidence)
        
    def induction(self, evidence_links: List[str]) -> TruthValue:
        """
        Inductive inference from evidence
        
        Args:
            evidence_links: List of evidence link IDs
            
        Returns:
            Truth value of induced pattern
        """
        if not evidence_links:
            return TruthValue(0.0, 0.0)
            
        strengths = []
        confidences = []
        
        for link_id in evidence_links:
            link = self.atomspace.get_link(link_id)
            if link:
                strengths.append(link.truth_value.strength)
                confidences.append(link.truth_value.confidence)
                
        if not strengths:
            return TruthValue(0.0, 0.0)
            
        # Induction formula
        strength = np.mean(strengths)
        confidence = np.mean(confidences) * np.sqrt(len(strengths)) / 10
        
        return TruthValue(strength, min(confidence, 1.0))
        
    def abduction(self, observation_id: str, rule_id: str) -> TruthValue:
        """
        Abductive inference: Given observation and rule, infer cause
        
        Args:
            observation_id: Observation atom ID
            rule_id: Rule link ID
            
        Returns:
            Truth value of abduced cause
        """
        observation = self.atomspace.get_atom(observation_id)
        rule = self.atomspace.get_link(rule_id)
        
        if not observation or not rule:
            return TruthValue(0.0, 0.0)
            
        # Simple abduction
        obs_strength = observation.truth_value.strength
        rule_strength = rule.truth_value.strength
        
        # Abduction formula
        strength = obs_strength / (rule_strength + 0.01)  # Avoid division by zero
        confidence = min(observation.truth_value.confidence, 
                        rule.truth_value.confidence) * 0.8
        
        return TruthValue(min(strength, 1.0), confidence)


class PatternMatcher:
    """
    Template-based pattern recognition system
    """
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.patterns: Dict[str, Dict[str, Any]] = {}
        
    def define_pattern(self, pattern_name: str, template: Dict[str, Any]) -> None:
        """
        Define a pattern template
        
        Args:
            pattern_name: Name of the pattern
            template: Pattern template specification
        """
        self.patterns[pattern_name] = template
        
    def match_pattern(self, pattern_name: str, 
                     target_atoms: List[str]) -> List[Dict[str, str]]:
        """
        Match pattern against target atoms
        
        Args:
            pattern_name: Name of pattern to match
            target_atoms: List of atom IDs to match against
            
        Returns:
            List of matching bindings
        """
        if pattern_name not in self.patterns:
            return []
            
        pattern = self.patterns[pattern_name]
        matches = []
        
        # Simple pattern matching implementation
        for atom_id in target_atoms:
            atom = self.atomspace.get_atom(atom_id)
            if atom and self._matches_template(atom, pattern):
                matches.append({"atom_id": atom_id, "pattern": pattern_name})
                
        return matches
        
    def _matches_template(self, atom: Atom, template: Dict[str, Any]) -> bool:
        """Check if atom matches template"""
        if "type" in template and atom.atom_type.value != template["type"]:
            return False
            
        if "truth_strength_min" in template:
            if atom.truth_value.strength < template["truth_strength_min"]:
                return False
                
        if "truth_confidence_min" in template:
            if atom.truth_value.confidence < template["truth_confidence_min"]:
                return False
                
        return True
        
    def scheme_pattern_match(self, pattern_name: str) -> str:
        """
        Generate Scheme specification for pattern matching
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Scheme specification string
        """
        if pattern_name not in self.patterns:
            return f"(define (pattern-match atomspace {pattern_name}) '())"
            
        pattern = self.patterns[pattern_name]
        scheme_spec = f"(define (pattern-match atomspace {pattern_name})\n"
        scheme_spec += f"  (filter (lambda (atom)\n"
        scheme_spec += f"    (and\n"
        
        for key, value in pattern.items():
            scheme_spec += f"      ({key} atom {value})\n"
            
        scheme_spec += f"    ))\n"
        scheme_spec += f"  (atomspace-atoms)))"
        
        return scheme_spec


class CognitiveGrammar:
    """
    Main cognitive grammar system integrating AtomSpace, PLN, and pattern matching
    """
    
    def __init__(self):
        self.atomspace = AtomSpace()
        self.pln = PLN(self.atomspace)
        self.pattern_matcher = PatternMatcher(self.atomspace)
        
        # Initialize default patterns
        self._initialize_default_patterns()
        
    def _initialize_default_patterns(self) -> None:
        """Initialize default pattern templates"""
        
        # Entity recognition pattern
        self.pattern_matcher.define_pattern("entity", {
            "type": "concept",
            "truth_strength_min": 0.7,
            "truth_confidence_min": 0.5
        })
        
        # Relationship pattern
        self.pattern_matcher.define_pattern("relationship", {
            "type": "predicate",
            "truth_strength_min": 0.6,
            "truth_confidence_min": 0.4
        })
        
        # High-confidence pattern
        self.pattern_matcher.define_pattern("high_confidence", {
            "truth_strength_min": 0.8,
            "truth_confidence_min": 0.8
        })
        
    def create_entity(self, name: str, entity_type: str = "concept") -> str:
        """Create an entity in the knowledge base"""
        atom_type = AtomType.CONCEPT if entity_type == "concept" else AtomType.PREDICATE
        return self.atomspace.add_atom(name, atom_type)
        
    def create_relationship(self, entity1_id: str, entity2_id: str, 
                          relation_type: str = "similarity") -> str:
        """Create a relationship between entities"""
        link_type = LinkType.SIMILARITY if relation_type == "similarity" else LinkType.INHERITANCE
        return self.atomspace.add_link(link_type, [entity1_id, entity2_id])
        
    def infer_knowledge(self, inference_type: str = "deduction", 
                       **kwargs) -> TruthValue:
        """Perform knowledge inference"""
        if inference_type == "deduction":
            return self.pln.deduction(kwargs["premise1"], kwargs["premise2"])
        elif inference_type == "induction":
            return self.pln.induction(kwargs["evidence_links"])
        elif inference_type == "abduction":
            return self.pln.abduction(kwargs["observation"], kwargs["rule"])
        else:
            return TruthValue(0.0, 0.0)
            
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            "total_atoms": len(self.atomspace.atoms),
            "total_links": len(self.atomspace.links),
            "hypergraph_density": self.atomspace.get_hypergraph_density(),
            "pattern_count": len(self.pattern_matcher.patterns)
        }