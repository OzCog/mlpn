"""
ko6ml ↔ AtomSpace Bidirectional Translator

Implements bidirectional translation mechanisms between ko6ml primitives 
and AtomSpace hypergraph patterns for Phase 1 cognitive integration.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive_grammar import AtomSpace, AtomType, LinkType, TruthValue


class Ko6mlPrimitive(Enum):
    """ko6ml primitive types"""
    ENTITY = "entity"
    RELATION = "relation"
    PROPERTY = "property"
    RULE = "rule"
    CONSTRAINT = "constraint"
    PATTERN = "pattern"


@dataclass
class Ko6mlExpression:
    """ko6ml expression structure"""
    primitive_type: Ko6mlPrimitive
    name: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class AtomSpacePattern:
    """AtomSpace hypergraph pattern"""
    atoms: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    truth_values: Dict[str, TruthValue]


class Ko6mlTranslator:
    """
    Bidirectional translator between ko6ml primitives and AtomSpace patterns
    
    Provides round-trip translation capabilities for cognitive architecture integration.
    """
    
    def __init__(self):
        self.atomspace = AtomSpace()
        self.ko6ml_to_atom_mapping = {}
        self.atom_to_ko6ml_mapping = {}
        
        # Initialize primitive translation rules
        self._initialize_translation_rules()
    
    def _initialize_translation_rules(self):
        """Initialize translation rules between ko6ml and AtomSpace"""
        self.primitive_mappings = {
            Ko6mlPrimitive.ENTITY: AtomType.CONCEPT,
            Ko6mlPrimitive.RELATION: AtomType.PREDICATE,
            Ko6mlPrimitive.PROPERTY: AtomType.CONCEPT,
            Ko6mlPrimitive.RULE: AtomType.SCHEMA,
            Ko6mlPrimitive.CONSTRAINT: AtomType.SCHEMA,
            Ko6mlPrimitive.PATTERN: AtomType.VARIABLE
        }
        
        self.relation_mappings = {
            "is_a": LinkType.INHERITANCE,
            "similar_to": LinkType.SIMILARITY,
            "member_of": LinkType.MEMBER,
            "subset_of": LinkType.SUBSET,
            "implies": LinkType.IMPLICATION,
            "equivalent_to": LinkType.EQUIVALENCE,
            "evaluates": LinkType.EVALUATION
        }
    
    def ko6ml_to_atomspace(self, ko6ml_expr: Ko6mlExpression) -> str:
        """
        Translate ko6ml expression to AtomSpace pattern
        
        Args:
            ko6ml_expr: ko6ml expression to translate
            
        Returns:
            Atom ID in AtomSpace
        """
        # Map ko6ml primitive to AtomSpace type
        atom_type = self.primitive_mappings.get(
            ko6ml_expr.primitive_type, 
            AtomType.CONCEPT
        )
        
        # Extract truth value from metadata
        truth_value = self._extract_truth_value(ko6ml_expr.metadata)
        
        # Create atom in AtomSpace
        atom_id = self.atomspace.add_atom(
            ko6ml_expr.name, 
            atom_type, 
            truth_value
        )
        
        # Store bidirectional mapping with original type preserved
        self.ko6ml_to_atom_mapping[id(ko6ml_expr)] = atom_id
        
        # Store the original ko6ml type as metadata for round-trip fidelity
        enhanced_ko6ml = Ko6mlExpression(
            primitive_type=ko6ml_expr.primitive_type,
            name=ko6ml_expr.name,
            parameters=ko6ml_expr.parameters.copy(),
            metadata=ko6ml_expr.metadata.copy()
        )
        self.atom_to_ko6ml_mapping[atom_id] = enhanced_ko6ml
        
        # Handle parameters as additional atoms/links
        self._process_parameters(atom_id, ko6ml_expr.parameters)
        
        return atom_id
    
    def atomspace_to_ko6ml(self, atom_id: str) -> Optional[Ko6mlExpression]:
        """
        Translate AtomSpace atom to ko6ml expression
        
        Args:
            atom_id: AtomSpace atom ID
            
        Returns:
            ko6ml expression or None if not found
        """
        # Check if we have a stored mapping first (for round-trip fidelity)
        if atom_id in self.atom_to_ko6ml_mapping:
            return self.atom_to_ko6ml_mapping[atom_id]
        
        atom = self.atomspace.get_atom(atom_id)
        if not atom:
            return None
        
        # Map AtomSpace type to ko6ml primitive
        primitive_type = self._atom_type_to_ko6ml(atom.atom_type)
        
        # Extract metadata
        metadata = {
            "atom_id": atom_id,
            "truth_strength": atom.truth_value.strength,
            "truth_confidence": atom.truth_value.confidence,
            "prime_index": atom.prime_index
        }
        
        # Extract parameters from connected atoms
        parameters = self._extract_parameters(atom_id)
        
        ko6ml_expr = Ko6mlExpression(
            primitive_type=primitive_type,
            name=atom.name,
            parameters=parameters,
            metadata=metadata
        )
        
        return ko6ml_expr
    
    def translate_pattern(self, ko6ml_patterns: List[Ko6mlExpression]) -> AtomSpacePattern:
        """
        Translate complex ko6ml pattern to AtomSpace hypergraph
        
        Args:
            ko6ml_patterns: List of ko6ml expressions forming a pattern
            
        Returns:
            AtomSpace hypergraph pattern
        """
        atoms = []
        links = []
        truth_values = {}
        
        # Create atoms for each ko6ml expression
        atom_ids = []
        for expr in ko6ml_patterns:
            atom_id = self.ko6ml_to_atomspace(expr)
            atom_ids.append(atom_id)
            
            atom = self.atomspace.get_atom(atom_id)
            atoms.append({
                "id": atom_id,
                "name": atom.name,
                "type": atom.atom_type.value
            })
            truth_values[atom_id] = atom.truth_value
        
        # Create links based on relationships
        for i, expr in enumerate(ko6ml_patterns):
            relations = expr.parameters.get("relations", [])
            for relation in relations:
                target_idx = relation.get("target_index")
                if target_idx is not None and target_idx < len(atom_ids):
                    link_type = self.relation_mappings.get(
                        relation.get("type", "similarity"),
                        LinkType.SIMILARITY
                    )
                    
                    link_id = self.atomspace.add_link(
                        link_type,
                        [atom_ids[i], atom_ids[target_idx]]
                    )
                    
                    link = self.atomspace.get_link(link_id)
                    links.append({
                        "id": link_id,
                        "type": link.link_type.value,
                        "atoms": link.atoms
                    })
                    truth_values[link_id] = link.truth_value
        
        return AtomSpacePattern(
            atoms=atoms,
            links=links,
            truth_values=truth_values
        )
    
    def atomspace_pattern_to_ko6ml(self, pattern: AtomSpacePattern) -> List[Ko6mlExpression]:
        """
        Translate AtomSpace pattern back to ko6ml expressions
        
        Args:
            pattern: AtomSpace hypergraph pattern
            
        Returns:
            List of ko6ml expressions
        """
        ko6ml_expressions = []
        
        for atom_data in pattern.atoms:
            atom_id = atom_data["id"]
            ko6ml_expr = self.atomspace_to_ko6ml(atom_id)
            if ko6ml_expr:
                # Add relationship information from links
                relations = []
                for link_data in pattern.links:
                    if atom_id in link_data["atoms"]:
                        # Find the other atom in the link
                        other_atoms = [aid for aid in link_data["atoms"] if aid != atom_id]
                        if other_atoms:
                            relation = {
                                "type": self._link_type_to_relation(link_data["type"]),
                                "target_atom": other_atoms[0],
                                "link_id": link_data["id"]
                            }
                            relations.append(relation)
                
                if relations:
                    ko6ml_expr.parameters["relations"] = relations
                
                ko6ml_expressions.append(ko6ml_expr)
        
        return ko6ml_expressions
    
    def verify_round_trip(self, original_ko6ml: List[Ko6mlExpression]) -> bool:
        """
        Verify round-trip translation integrity
        
        Args:
            original_ko6ml: Original ko6ml expressions
            
        Returns:
            True if round-trip translation preserves semantics
        """
        # Translate to AtomSpace
        atomspace_pattern = self.translate_pattern(original_ko6ml)
        
        # Translate back to ko6ml
        recovered_ko6ml = self.atomspace_pattern_to_ko6ml(atomspace_pattern)
        
        # Compare structures (simplified semantic comparison)
        if len(original_ko6ml) != len(recovered_ko6ml):
            return False
        
        for orig, recovered in zip(original_ko6ml, recovered_ko6ml):
            if orig.primitive_type != recovered.primitive_type:
                return False
            if orig.name != recovered.name:
                return False
        
        return True
    
    def _extract_truth_value(self, metadata: Dict[str, Any]) -> TruthValue:
        """Extract truth value from ko6ml metadata"""
        strength = metadata.get("confidence", 0.5)
        confidence = metadata.get("certainty", 0.5)
        return TruthValue(strength, confidence)
    
    def _atom_type_to_ko6ml(self, atom_type: AtomType) -> Ko6mlPrimitive:
        """Map AtomSpace type to ko6ml primitive"""
        # Handle ambiguous mappings by preferring the most common usage
        if atom_type == AtomType.CONCEPT:
            # Default to ENTITY for concepts (most common usage)
            return Ko6mlPrimitive.ENTITY
        elif atom_type == AtomType.PREDICATE:
            return Ko6mlPrimitive.RELATION
        elif atom_type == AtomType.SCHEMA:
            return Ko6mlPrimitive.RULE
        elif atom_type == AtomType.VARIABLE:
            return Ko6mlPrimitive.PATTERN
        else:
            return Ko6mlPrimitive.ENTITY
    
    def _link_type_to_relation(self, link_type: str) -> str:
        """Map AtomSpace link type to ko6ml relation"""
        reverse_mapping = {v.value: k for k, v in self.relation_mappings.items()}
        return reverse_mapping.get(link_type, "related_to")
    
    def _process_parameters(self, atom_id: str, parameters: Dict[str, Any]):
        """Process ko6ml parameters and create additional atoms/links"""
        for key, value in parameters.items():
            if key == "properties":
                for prop_name, prop_value in value.items():
                    prop_atom_id = self.atomspace.add_atom(
                        f"{prop_name}:{prop_value}",
                        AtomType.CONCEPT
                    )
                    self.atomspace.add_link(
                        LinkType.EVALUATION,
                        [atom_id, prop_atom_id]
                    )
    
    def _extract_parameters(self, atom_id: str) -> Dict[str, Any]:
        """Extract parameters from connected atoms"""
        parameters = {"properties": {}, "relations": []}
        
        connected = self.atomspace.get_connected_atoms(atom_id)
        for connected_id, link_type in connected:
            connected_atom = self.atomspace.get_atom(connected_id)
            if connected_atom and ":" in connected_atom.name:
                # Property atom
                prop_name, prop_value = connected_atom.name.split(":", 1)
                parameters["properties"][prop_name] = prop_value
        
        return parameters
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """Get translation statistics"""
        return {
            "ko6ml_to_atom_mappings": len(self.ko6ml_to_atom_mapping),
            "atom_to_ko6ml_mappings": len(self.atom_to_ko6ml_mapping),
            "total_atoms": len(self.atomspace.atoms),
            "total_links": len(self.atomspace.links),
            "supported_primitives": len(self.primitive_mappings),
            "supported_relations": len(self.relation_mappings)
        }
    
    def generate_scheme_translation(self, ko6ml_expr: Ko6mlExpression) -> str:
        """
        Generate Scheme specification for ko6ml translation
        
        Args:
            ko6ml_expr: ko6ml expression
            
        Returns:
            Scheme specification string
        """
        atom_id = self.ko6ml_to_atomspace(ko6ml_expr)
        atom = self.atomspace.get_atom(atom_id)
        
        scheme_spec = f"""(define (ko6ml-to-atomspace {ko6ml_expr.name})
  (let ((atom-id (add-atom "{ko6ml_expr.name}" '{atom.atom_type.value})))
    (set-truth-value atom-id 
      (make-truth-value {atom.truth_value.strength} {atom.truth_value.confidence}))
    atom-id))

(define (atomspace-to-ko6ml {atom_id})
  (make-ko6ml-expression
    '{ko6ml_expr.primitive_type.value}
    "{ko6ml_expr.name}"
    '{ko6ml_expr.parameters}
    '{ko6ml_expr.metadata}))"""
        
        return scheme_spec