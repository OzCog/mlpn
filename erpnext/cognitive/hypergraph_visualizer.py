"""
Hypergraph Fragment Flowchart Visualizer

Provides comprehensive visualization for Phase 1 hypergraph fragments,
ko6ml translations, and cognitive primitive operations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import os

@dataclass
class HypergraphNode:
    """Represents a node in the hypergraph"""
    id: str
    label: str
    node_type: str  # 'concept', 'predicate', 'schema', 'variable'
    position: Tuple[float, float]
    metadata: Dict[str, Any]

@dataclass
class HypergraphEdge:
    """Represents a hyperedge connecting multiple nodes"""
    id: str
    nodes: List[str]  # List of node IDs
    edge_type: str  # 'inheritance', 'similarity', 'evaluation', etc.
    weight: float
    metadata: Dict[str, Any]

@dataclass
class FragmentLayout:
    """Layout configuration for fragment visualization"""
    width: float
    height: float
    node_size: float
    edge_width: float
    colors: Dict[str, str]

class HypergraphVisualizer:
    """
    Main visualizer for hypergraph fragments and cognitive primitives
    """
    
    def __init__(self, output_dir: str = "/tmp/hypergraph_viz"):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save visualization outputs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Default color scheme for different node types
        self.default_colors = {
            'concept': '#FF6B6B',      # Red for concepts
            'predicate': '#4ECDC4',    # Teal for predicates  
            'schema': '#45B7D1',       # Blue for schemas
            'variable': '#96CEB4',     # Green for variables
            'fragment': '#FECA57',     # Yellow for fragments
            'edge': '#74B9FF'          # Light blue for edges
        }
        
        # Default layout settings
        self.default_layout = FragmentLayout(
            width=12.0,
            height=8.0,
            node_size=1000,
            edge_width=2.0,
            colors=self.default_colors
        )
    
    def create_hypergraph_flowchart(self, 
                                  nodes: List[HypergraphNode],
                                  edges: List[HypergraphEdge],
                                  title: str = "Hypergraph Fragment",
                                  layout: Optional[FragmentLayout] = None) -> str:
        """
        Create a flowchart visualization of hypergraph fragments
        
        Args:
            nodes: List of hypergraph nodes
            edges: List of hypergraph edges
            title: Chart title
            layout: Layout configuration
            
        Returns:
            Path to saved visualization file
        """
        if layout is None:
            layout = self.default_layout
            
        fig, ax = plt.subplots(figsize=(layout.width, layout.height))
        
        # Create node positions lookup
        node_positions = {node.id: node.position for node in nodes}
        
        # Draw edges first (so they appear behind nodes)
        for edge in edges:
            self._draw_hyperedge(ax, edge, node_positions, layout)
        
        # Draw nodes
        for node in nodes:
            self._draw_node(ax, node, layout)
            
        # Add title and formatting
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-0.5, 6.5)
        ax.axis('off')
        
        # Add legend
        self._add_legend(ax, layout)
        
        # Save the figure
        filename = f"{title.lower().replace(' ', '_')}_flowchart.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_ko6ml_translation_diagram(self,
                                       ko6ml_expressions: List[Dict[str, Any]],
                                       atomspace_atoms: List[Dict[str, Any]],
                                       title: str = "ko6ml ↔ AtomSpace Translation") -> str:
        """
        Create diagram showing ko6ml to AtomSpace translation
        
        Args:
            ko6ml_expressions: List of ko6ml expression dictionaries
            atomspace_atoms: List of corresponding AtomSpace atoms
            title: Diagram title
            
        Returns:
            Path to saved diagram file
        """
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 8))
        
        # ko6ml side
        ax1.set_title("ko6ml Primitives", fontsize=14, fontweight='bold')
        self._draw_ko6ml_primitives(ax1, ko6ml_expressions)
        
        # Translation arrows
        ax2.set_title("Translation", fontsize=14, fontweight='bold')
        self._draw_translation_arrows(ax2)
        
        # AtomSpace side
        ax3.set_title("AtomSpace Hypergraph", fontsize=14, fontweight='bold')
        self._draw_atomspace_atoms(ax3, atomspace_atoms)
        
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        for ax in [ax1, ax2, ax3]:
            ax.set_xlim(-0.5, 5.5)
            ax.set_ylim(-0.5, 8.5)
            ax.axis('off')
        
        # Save the figure
        filename = f"{title.lower().replace(' ', '_').replace('↔', 'to')}_diagram.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_tensor_fragment_visualization(self,
                                           fragments: List[Dict[str, Any]],
                                           operations: List[str],
                                           title: str = "Tensor Fragment Operations") -> str:
        """
        Create visualization of tensor fragment operations
        
        Args:
            fragments: List of tensor fragment metadata
            operations: List of operation descriptions
            title: Visualization title
            
        Returns:
            Path to saved visualization file
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Fragment grid decomposition
        ax1.set_title("Grid Decomposition", fontsize=12, fontweight='bold')
        self._draw_tensor_grid(ax1, fragments[:4] if len(fragments) >= 4 else fragments)
        
        # Hierarchical decomposition
        ax2.set_title("Hierarchical Decomposition", fontsize=12, fontweight='bold')
        self._draw_tensor_hierarchy(ax2, fragments)
        
        # Fragment composition
        ax3.set_title("Fragment Composition", fontsize=12, fontweight='bold')
        self._draw_fragment_composition(ax3, fragments, operations)
        
        # Operations flowchart
        ax4.set_title("Operations Pipeline", fontsize=12, fontweight='bold')
        self._draw_operations_pipeline(ax4, operations)
        
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_xlim(-0.5, 5.5)
            ax.set_ylim(-0.5, 5.5)
            ax.axis('off')
        
        # Save the figure
        filename = f"{title.lower().replace(' ', '_')}_visualization.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_attention_heatmap(self,
                               attention_matrix: np.ndarray,
                               labels: List[str],
                               title: str = "Attention Allocation Heatmap") -> str:
        """
        Create heatmap visualization of attention allocation
        
        Args:
            attention_matrix: Matrix of attention values
            labels: Labels for atoms/concepts
            title: Heatmap title
            
        Returns:
            Path to saved heatmap file
        """
        plt.figure(figsize=(10, 8))
        
        # Create heatmap with seaborn
        sns.heatmap(attention_matrix, 
                   xticklabels=labels[:attention_matrix.shape[1]] if labels else False,
                   yticklabels=labels[:attention_matrix.shape[0]] if labels else False,
                   annot=True, 
                   fmt='.3f',
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Attention Value'})
        
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.xlabel("Time Steps / Dimensions", fontsize=12)
        plt.ylabel("Concepts / Atoms", fontsize=12)
        plt.tight_layout()
        
        # Save the figure
        filename = f"{title.lower().replace(' ', '_')}_heatmap.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_comprehensive_flowchart(self,
                                     phase1_data: Dict[str, Any],
                                     title: str = "Phase 1 Comprehensive Architecture") -> str:
        """
        Create comprehensive flowchart showing all Phase 1 components
        
        Args:
            phase1_data: Dictionary containing all Phase 1 component data
            title: Flowchart title
            
        Returns:
            Path to saved flowchart file
        """
        fig, ax = plt.subplots(figsize=(20, 14))
        
        # Define component areas
        areas = {
            'microservices': {'x': 1, 'y': 8, 'w': 5, 'h': 4},
            'translation': {'x': 8, 'y': 8, 'w': 5, 'h': 4},
            'fragments': {'x': 15, 'y': 8, 'w': 4, 'h': 4},
            'hypergraph': {'x': 1, 'y': 2, 'w': 8, 'h': 4},
            'attention': {'x': 11, 'y': 2, 'w': 8, 'h': 4}
        }
        
        # Draw component areas
        for area_name, area in areas.items():
            self._draw_component_area(ax, area, area_name, phase1_data.get(area_name, {}))
        
        # Draw connections between components
        self._draw_component_connections(ax, areas)
        
        ax.set_title(title, fontsize=18, fontweight='bold', pad=30)
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 13)
        ax.axis('off')
        
        # Add overall legend
        self._add_comprehensive_legend(ax)
        
        # Save the figure
        filename = f"{title.lower().replace(' ', '_')}_flowchart.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _draw_node(self, ax, node: HypergraphNode, layout: FragmentLayout):
        """Draw a single hypergraph node"""
        x, y = node.position
        color = layout.colors.get(node.node_type, layout.colors['concept'])
        
        # Draw node circle
        circle = patches.Circle((x, y), 0.3, facecolor=color, 
                              edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        # Add label
        ax.text(x, y, node.label, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        
        # Add type indicator
        ax.text(x, y-0.5, f"({node.node_type})", ha='center', va='center', 
               fontsize=8, style='italic')
    
    def _draw_hyperedge(self, ax, edge: HypergraphEdge, 
                       node_positions: Dict[str, Tuple[float, float]], 
                       layout: FragmentLayout):
        """Draw a hyperedge connecting multiple nodes"""
        positions = [node_positions[node_id] for node_id in edge.nodes if node_id in node_positions]
        
        if len(positions) < 2:
            return
            
        # For simplicity, draw lines between consecutive nodes
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            
            ax.plot([x1, x2], [y1, y2], 
                   color=layout.colors['edge'], 
                   linewidth=layout.edge_width,
                   alpha=0.7)
            
            # Add edge label at midpoint
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y + 0.1, edge.edge_type, 
                   ha='center', va='bottom', fontsize=8,
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    def _draw_ko6ml_primitives(self, ax, expressions: List[Dict[str, Any]]):
        """Draw ko6ml primitive expressions"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        
        for i, expr in enumerate(expressions[:5]):  # Limit to 5 for clarity
            y = 7 - i * 1.5
            color = colors[i % len(colors)]
            
            # Draw expression box
            rect = patches.Rectangle((1, y-0.4), 3, 0.8, 
                                   facecolor=color, alpha=0.7,
                                   edgecolor='black', linewidth=1)
            ax.add_patch(rect)
            
            # Add expression text
            expr_text = f"{expr.get('primitive', 'unknown')}: {expr.get('value', '')}"
            ax.text(2.5, y, expr_text, ha='center', va='center', 
                   fontsize=10, fontweight='bold')
    
    def _draw_translation_arrows(self, ax):
        """Draw bidirectional translation arrows"""
        # Forward arrow
        ax.arrow(1, 4, 3, 0, head_width=0.3, head_length=0.3, 
                fc='green', ec='green', linewidth=3)
        ax.text(2.5, 4.5, "ko6ml → AtomSpace", ha='center', va='center', 
               fontsize=10, fontweight='bold')
        
        # Backward arrow  
        ax.arrow(4, 3, -3, 0, head_width=0.3, head_length=0.3,
                fc='blue', ec='blue', linewidth=3)
        ax.text(2.5, 2.5, "AtomSpace → ko6ml", ha='center', va='center',
               fontsize=10, fontweight='bold')
    
    def _draw_atomspace_atoms(self, ax, atoms: List[Dict[str, Any]]):
        """Draw AtomSpace atoms representation"""
        positions = [(2, 7), (4, 6), (2, 5), (4, 4), (3, 3)]
        
        for i, atom in enumerate(atoms[:5]):  # Limit to 5 for clarity
            if i >= len(positions):
                break
                
            x, y = positions[i]
            atom_type = atom.get('type', 'unknown')
            color = self.default_colors.get(atom_type, '#DDD')
            
            # Draw atom node
            circle = patches.Circle((x, y), 0.3, facecolor=color,
                                  edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            
            # Add atom label
            label = atom.get('name', f"atom_{i}")
            ax.text(x, y, label, ha='center', va='center',
                   fontsize=9, fontweight='bold')
    
    def _draw_tensor_grid(self, ax, fragments: List[Dict[str, Any]]):
        """Draw tensor grid decomposition"""
        grid_positions = [(1, 4), (3, 4), (1, 2), (3, 2)]
        
        for i, fragment in enumerate(fragments[:4]):
            if i >= len(grid_positions):
                break
                
            x, y = grid_positions[i]
            
            # Draw fragment square
            rect = patches.Rectangle((x-0.4, y-0.4), 0.8, 0.8,
                                   facecolor=self.default_colors['fragment'],
                                   edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Add fragment label
            ax.text(x, y, f"F{i+1}", ha='center', va='center',
                   fontsize=12, fontweight='bold')
    
    def _draw_tensor_hierarchy(self, ax, fragments: List[Dict[str, Any]]):
        """Draw hierarchical tensor decomposition"""
        # Root fragment
        ax.add_patch(patches.Rectangle((2, 4), 1, 1, 
                                     facecolor=self.default_colors['fragment'],
                                     edgecolor='black', linewidth=2))
        ax.text(2.5, 4.5, "Root", ha='center', va='center', fontweight='bold')
        
        # Child fragments
        child_positions = [(1, 2.5), (2.5, 2.5), (4, 2.5)]
        for i, pos in enumerate(child_positions):
            x, y = pos
            ax.add_patch(patches.Rectangle((x-0.3, y-0.3), 0.6, 0.6,
                                         facecolor=self.default_colors['fragment'],
                                         alpha=0.7, edgecolor='black'))
            ax.text(x, y, f"C{i+1}", ha='center', va='center', fontweight='bold')
            
            # Draw connection to root
            ax.plot([2.5, x], [4, y+0.3], 'k-', linewidth=2)
    
    def _draw_fragment_composition(self, ax, fragments: List[Dict[str, Any]], 
                                 operations: List[str]):
        """Draw fragment composition operations"""
        # Input fragments
        ax.add_patch(patches.Circle((1, 3), 0.3, facecolor='lightblue'))
        ax.add_patch(patches.Circle((1, 1), 0.3, facecolor='lightblue'))
        ax.text(1, 3, "F1", ha='center', va='center', fontweight='bold')
        ax.text(1, 1, "F2", ha='center', va='center', fontweight='bold')
        
        # Composition operation
        ax.add_patch(patches.Rectangle((2.5, 1.5), 1, 1,
                                     facecolor='lightgreen',
                                     edgecolor='black', linewidth=2))
        ax.text(3, 2, "⊗", ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Output fragment
        ax.add_patch(patches.Circle((5, 2), 0.4, facecolor='orange'))
        ax.text(5, 2, "F3", ha='center', va='center', fontweight='bold')
        
        # Draw arrows
        ax.arrow(1.3, 3, 1, -0.5, head_width=0.1, head_length=0.1, fc='k', ec='k')
        ax.arrow(1.3, 1, 1, 0.5, head_width=0.1, head_length=0.1, fc='k', ec='k')
        ax.arrow(3.5, 2, 1.2, 0, head_width=0.1, head_length=0.1, fc='k', ec='k')
    
    def _draw_operations_pipeline(self, ax, operations: List[str]):
        """Draw operations pipeline flowchart"""
        y_positions = [4, 3, 2, 1]
        
        for i, op in enumerate(operations[:4]):
            y = y_positions[i]
            
            # Draw operation box
            rect = patches.Rectangle((1, y-0.3), 3, 0.6,
                                   facecolor='lightcyan',
                                   edgecolor='black', linewidth=1)
            ax.add_patch(rect)
            
            # Add operation text
            ax.text(2.5, y, op, ha='center', va='center',
                   fontsize=10, fontweight='bold')
            
            # Draw arrow to next operation
            if i < len(operations) - 1 and i < 3:
                ax.arrow(2.5, y-0.3, 0, -0.4, head_width=0.1, head_length=0.1,
                        fc='black', ec='black')
    
    def _draw_component_area(self, ax, area: Dict[str, float], 
                           area_name: str, data: Dict[str, Any]):
        """Draw a component area in the comprehensive flowchart"""
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        
        # Color scheme for different areas
        area_colors = {
            'microservices': '#FFE5E5',
            'translation': '#E5F3FF', 
            'fragments': '#E5FFE5',
            'hypergraph': '#FFF5E5',
            'attention': '#F5E5FF'
        }
        
        # Draw area background
        rect = patches.Rectangle((x, y), w, h, 
                               facecolor=area_colors.get(area_name, '#F0F0F0'),
                               edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Add area title
        ax.text(x + w/2, y + h - 0.5, area_name.title(), 
               ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Add area-specific content
        if area_name == 'microservices':
            services = ['AtomSpace', 'PLN', 'Pattern']
            for i, service in enumerate(services):
                ax.text(x + 1 + i*1.5, y + h/2, service,
                       ha='center', va='center', fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white'))
        
        elif area_name == 'translation':
            ax.text(x + w/2, y + h/2, "ko6ml ↔ AtomSpace\nBidirectional\nTranslation",
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        elif area_name == 'fragments':
            ax.text(x + w/2, y + h/2, "Tensor\nFragments\nDistributed\nOps",
                   ha='center', va='center', fontsize=10, fontweight='bold')
    
    def _draw_component_connections(self, ax, areas: Dict[str, Dict[str, float]]):
        """Draw connections between component areas"""
        # Connection specifications: (from_area, to_area, style)
        connections = [
            ('microservices', 'translation', 'solid'),
            ('translation', 'fragments', 'solid'),
            ('microservices', 'hypergraph', 'dashed'),
            ('translation', 'hypergraph', 'solid'),
            ('fragments', 'attention', 'solid'),
            ('hypergraph', 'attention', 'dashed')
        ]
        
        for from_area, to_area, style in connections:
            if from_area in areas and to_area in areas:
                from_pos = areas[from_area]
                to_pos = areas[to_area]
                
                # Calculate connection points
                from_x = from_pos['x'] + from_pos['w']
                from_y = from_pos['y'] + from_pos['h']/2
                to_x = to_pos['x'] 
                to_y = to_pos['y'] + to_pos['h']/2
                
                # Draw connection
                linestyle = '--' if style == 'dashed' else '-'
                ax.plot([from_x, to_x], [from_y, to_y], 
                       linestyle=linestyle, linewidth=2, color='blue', alpha=0.6)
    
    def _add_legend(self, ax, layout: FragmentLayout):
        """Add legend to hypergraph visualization"""
        legend_elements = []
        for node_type, color in layout.colors.items():
            if node_type != 'edge':
                legend_elements.append(patches.Patch(color=color, label=node_type.title()))
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    def _add_comprehensive_legend(self, ax):
        """Add legend to comprehensive flowchart"""
        legend_text = [
            "—— Data Flow",
            "- - - Control Flow", 
            "Areas: Microservices, Translation, Fragments, Hypergraph, Attention"
        ]
        
        ax.text(1, 0.5, '\n'.join(legend_text), fontsize=10,
               bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    def generate_all_phase1_visualizations(self, 
                                         phase1_data: Dict[str, Any]) -> List[str]:
        """
        Generate all Phase 1 visualizations
        
        Args:
            phase1_data: Complete Phase 1 data for visualization
            
        Returns:
            List of paths to generated visualization files
        """
        generated_files = []
        
        # 1. Basic hypergraph fragment
        if 'hypergraph' in phase1_data:
            hg_data = phase1_data['hypergraph']
            nodes = [
                HypergraphNode('n1', 'customer', 'concept', (2, 4), {}),
                HypergraphNode('n2', 'order', 'concept', (6, 4), {}),
                HypergraphNode('n3', 'places', 'predicate', (4, 2), {}),
                HypergraphNode('n4', 'person', 'concept', (2, 6), {})
            ]
            edges = [
                HypergraphEdge('e1', ['n1', 'n3', 'n2'], 'evaluation', 0.8, {}),
                HypergraphEdge('e2', ['n1', 'n4'], 'inheritance', 0.9, {})
            ]
            filepath = self.create_hypergraph_flowchart(nodes, edges, 
                                                       "Phase 1 Hypergraph Fragment")
            generated_files.append(filepath)
        
        # 2. ko6ml translation diagram
        if 'translation' in phase1_data:
            ko6ml_exprs = [
                {'primitive': 'ENTITY', 'value': 'customer', 'confidence': 0.9},
                {'primitive': 'RELATION', 'value': 'places_order', 'confidence': 0.8},
                {'primitive': 'PROPERTY', 'value': 'urgent', 'confidence': 0.7}
            ]
            atomspace_atoms = [
                {'type': 'concept', 'name': 'customer'},
                {'type': 'predicate', 'name': 'places_order'},
                {'type': 'concept', 'name': 'urgent'}
            ]
            filepath = self.create_ko6ml_translation_diagram(ko6ml_exprs, atomspace_atoms)
            generated_files.append(filepath)
        
        # 3. Tensor fragment operations
        if 'fragments' in phase1_data:
            fragments = [
                {'id': 'f1', 'shape': (2, 2), 'type': 'cognitive'},
                {'id': 'f2', 'shape': (2, 2), 'type': 'attention'},
                {'id': 'f3', 'shape': (4, 4), 'type': 'composed'},
                {'id': 'f4', 'shape': (1, 4), 'type': 'reduced'}
            ]
            operations = ['Decompose', 'Process', 'Compose', 'Synchronize']
            filepath = self.create_tensor_fragment_visualization(fragments, operations)
            generated_files.append(filepath)
        
        # 4. Attention heatmap
        if 'attention' in phase1_data:
            attention_matrix = np.random.rand(5, 8) * 5  # Example attention data
            labels = ['customer', 'order', 'product', 'invoice', 'payment']
            filepath = self.create_attention_heatmap(attention_matrix, labels)
            generated_files.append(filepath)
        
        # 5. Comprehensive architecture flowchart
        filepath = self.create_comprehensive_flowchart(phase1_data)
        generated_files.append(filepath)
        
        return generated_files

def main():
    """
    Main function to demonstrate hypergraph visualization capabilities
    """
    visualizer = HypergraphVisualizer()
    
    # Example Phase 1 data
    phase1_data = {
        'hypergraph': {'nodes': 4, 'edges': 3, 'density': 1.33},
        'translation': {'ko6ml_expressions': 5, 'success_rate': 0.95},
        'fragments': {'total_fragments': 12, 'composition_ops': 8},
        'attention': {'atoms_tracked': 15, 'cycles': 10},
        'microservices': {'services': 3, 'uptime': 0.99}
    }
    
    # Generate all visualizations
    files = visualizer.generate_all_phase1_visualizations(phase1_data)
    
    print("Generated Phase 1 Hypergraph Fragment Flowcharts:")
    for filepath in files:
        print(f"  ✓ {filepath}")
    
    return files

if __name__ == "__main__":
    main()