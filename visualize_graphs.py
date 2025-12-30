"""
Graph Visualization Tool

This module creates visual representations of the Cayley graphs C_n(3,a)
and shows the infection spreading process to validate the infection number.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import List, Tuple, Set
import math
import os

from graph_generator import CayleyGraph, generate_all_valid_graphs
from infection_simulator import get_infection_spread_sequence
from contagious_set_finder import find_minimum_contagious_set


def draw_circulant_graph(graph: CayleyGraph, ax, initial_infected: Set[int] = None, 
                        current_infected: Set[int] = None, title: str = None):
    """
    Draw a circulant graph with vertices arranged in a circle.
    
    Args:
        graph: The CayleyGraph to draw
        ax: Matplotlib axis to draw on
        initial_infected: Initial infection set (shown in red)
        current_infected: Currently infected vertices (shown in orange/red)
        title: Title for the plot
    """
    n = graph.n
    a = graph.a
    
    # Arrange vertices in a circle
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    # Start from top and go clockwise
    angles = angles - np.pi / 2
    
    # Vertex positions
    radius = 1.0
    positions = {}
    for i in range(n):
        x = radius * np.cos(angles[i])
        y = radius * np.sin(angles[i])
        positions[i] = (x, y)
    
    # Draw edges first (so they appear behind vertices)
    # Group edges by type for different colors
    edges_3 = []
    edges_a = []
    
    for v in graph.vertices:
        neighbors = graph.get_neighbors(v)
        for neighbor in neighbors:
            if v < neighbor:  # Draw each edge only once
                # Determine edge type
                if (neighbor - v) % n == 3 or (v - neighbor) % n == 3:
                    edges_3.append((v, neighbor))
                else:
                    edges_a.append((v, neighbor))
    
    # Draw edges of type ±3 in blue
    for v1, v2 in edges_3:
        x1, y1 = positions[v1]
        x2, y2 = positions[v2]
        ax.plot([x1, x2], [y1, y2], 'b-', linewidth=1.5, alpha=0.4, zorder=1)
    
    # Draw edges of type ±a in green
    for v1, v2 in edges_a:
        x1, y1 = positions[v1]
        x2, y2 = positions[v2]
        ax.plot([x1, x2], [y1, y2], 'g-', linewidth=1.5, alpha=0.4, zorder=1)
    
    # Draw vertices
    for v in graph.vertices:
        x, y = positions[v]
        
        # Determine vertex color based on infection status
        if initial_infected and v in initial_infected:
            color = 'red'
            size = 400
            edge_color = 'darkred'
            edge_width = 3
        elif current_infected and v in current_infected:
            color = 'orange'
            size = 350
            edge_color = 'darkorange'
            edge_width = 2
        else:
            color = 'lightblue'
            size = 300
            edge_color = 'navy'
            edge_width = 1.5
        
        ax.scatter(x, y, c=color, s=size, edgecolors=edge_color, 
                  linewidths=edge_width, zorder=3)
        
        # Add vertex label
        ax.text(x, y, str(v), fontsize=10, fontweight='bold',
               ha='center', va='center', zorder=4)
    
    # Set title
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    else:
        ax.set_title(f'C_{n}(3,{a})', fontsize=12, fontweight='bold')
    
    # Set equal aspect ratio and remove axes
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)


def visualize_infection_process(graph: CayleyGraph, initial_infected: Set[int], 
                                output_filename: str = None):
    """
    Visualize the infection spreading process step by step.
    
    Args:
        graph: The CayleyGraph
        initial_infected: Initial infection set
        output_filename: If provided, save the figure to this file
    """
    # Get infection sequence
    sequence = get_infection_spread_sequence(graph, initial_infected)
    
    # Create figure with subplots for each round
    num_rounds = len(sequence)
    cols = min(num_rounds, 4)
    rows = math.ceil(num_rounds / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    if num_rounds == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    # Draw each round
    for round_num, infected in enumerate(sequence):
        ax = axes[round_num]
        
        if round_num == 0:
            title = f'Round 0: Initial ({len(infected)} infected)'
            draw_circulant_graph(graph, ax, initial_infected=infected, 
                               current_infected=infected, title=title)
        else:
            title = f'Round {round_num} ({len(infected)} infected)'
            draw_circulant_graph(graph, ax, initial_infected=initial_infected,
                               current_infected=infected, title=title)
    
    # Hide unused subplots
    for idx in range(num_rounds, len(axes)):
        axes[idx].axis('off')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='red', edgecolor='darkred', label='Initial infection'),
        mpatches.Patch(facecolor='orange', edgecolor='darkorange', label='Newly infected'),
        mpatches.Patch(facecolor='lightblue', edgecolor='navy', label='Healthy'),
        mpatches.Patch(facecolor='none', edgecolor='blue', label='Edges: ±3'),
        mpatches.Patch(facecolor='none', edgecolor='green', label='Edges: ±a')
    ]
    fig.legend(handles=legend_elements, loc='upper center', ncol=5, 
              bbox_to_anchor=(0.5, 0.98), fontsize=10)
    
    plt.suptitle(f'Infection Process for C_{graph.n}(3,{graph.a})\n'
                f'Initial set: {sorted(initial_infected)}, m_2 = {len(initial_infected)}',
                fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    if output_filename:
        plt.savefig(output_filename, dpi=200, bbox_inches='tight')
        print(f"  Saved: {output_filename}")
    
    plt.close()


def visualize_all_graphs(n_min: int = 5, n_max: int = 10, output_dir: str = "graph_visualizations"):
    """
    Create visualizations for all valid graphs in the range.
    
    Args:
        n_min: Minimum n value
        n_max: Maximum n value
        output_dir: Directory to save visualizations
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating visualizations for all graphs with n ∈ [{n_min}, {n_max}]")
    print("=" * 70)
    
    # Generate all valid graphs
    all_graphs = generate_all_valid_graphs(n_min, n_max)
    
    print(f"Found {len(all_graphs)} valid connected graphs")
    print()
    
    # Process each graph
    for idx, (n, a, graph) in enumerate(all_graphs, 1):
        print(f"[{idx}/{len(all_graphs)}] Visualizing C_{n}(3,{a})...", end=" ", flush=True)
        
        # Find minimum contagious set
        m2, contagious_set = find_minimum_contagious_set(graph)
        
        # Create filename
        filename = os.path.join(output_dir, f"C_{n}_3_{a}_infection.png")
        
        # Visualize infection process
        visualize_infection_process(graph, contagious_set, filename)
    
    print()
    print("=" * 70)
    print(f"All visualizations saved to: {output_dir}/")
    print(f"Total files: {len(all_graphs)}")


def create_summary_grid(n_min: int = 5, n_max: int = 10, output_filename: str = "all_graphs_summary.png"):
    """
    Create a summary grid showing all graphs with their initial infection sets.
    
    Args:
        n_min: Minimum n value
        n_max: Maximum n value
        output_filename: Output filename for the summary
    """
    print(f"\nCreating summary grid of all graphs...")
    
    # Generate all valid graphs
    all_graphs = generate_all_valid_graphs(n_min, n_max)
    
    # Calculate grid dimensions
    num_graphs = len(all_graphs)
    cols = 4
    rows = math.ceil(num_graphs / cols)
    
    # Create figure
    fig, axes = plt.subplots(rows, cols, figsize=(16, 4*rows))
    axes = axes.flatten()
    
    # Draw each graph
    for idx, (n, a, graph) in enumerate(all_graphs):
        ax = axes[idx]
        
        # Find minimum contagious set
        m2, contagious_set = find_minimum_contagious_set(graph)
        
        # Draw graph with initial infection
        title = f'C_{n}(3,{a})\nm_2={m2}, set={sorted(contagious_set)}'
        draw_circulant_graph(graph, ax, initial_infected=contagious_set,
                           current_infected=contagious_set, title=title)
    
    # Hide unused subplots
    for idx in range(num_graphs, len(axes)):
        axes[idx].axis('off')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='red', edgecolor='darkred', label='Initial infection (m_2 vertices)'),
        mpatches.Patch(facecolor='lightblue', edgecolor='navy', label='Healthy'),
        mpatches.Patch(facecolor='none', edgecolor='blue', label='Edges: ±3'),
        mpatches.Patch(facecolor='none', edgecolor='green', label='Edges: ±a')
    ]
    
    plt.suptitle(f'All Valid Quartic Circulant Graphs C_n(3,a) for n ∈ [{n_min}, {n_max}]\n'
                f'Total: {num_graphs} graphs, All have m_2 = 2',
                fontsize=16, fontweight='bold')
    
    fig.legend(handles=legend_elements, loc='upper center', ncol=4,
              bbox_to_anchor=(0.5, 0.98), fontsize=11)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_filename, dpi=200, bbox_inches='tight')
    print(f"Summary grid saved: {output_filename}")
    plt.close()


if __name__ == "__main__":
    print("Graph Visualization Tool")
    print("=" * 70)
    
    # Create visualizations for all graphs
    visualize_all_graphs(5, 10)
    
    # Create summary grid
    create_summary_grid(5, 10)
    
    print("\n" + "=" * 70)
    print("Visualization complete!")
    print("\nYou can now:")
    print("  1. Check individual infection processes in: graph_visualizations/")
    print("  2. View the summary of all graphs in: all_graphs_summary.png")
    print("=" * 70 + "\n")

