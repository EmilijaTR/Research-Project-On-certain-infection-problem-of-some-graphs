"""
Visualize the infection process step-by-step in circulant graphs

Shows:
1. Successful infection with 2 vertices (m2=2)
2. Failed infection with 2 vertices, successful with 3 (m2=3)
3. Failed infection that never completes
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from math import gcd
import os

def create_circulant_graph(n, a):
    """Create C_n(3,a) graph"""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    for x in range(n):
        G.add_edge(x, (x + 3) % n)
        G.add_edge(x, (x - 3) % n)
        G.add_edge(x, (x + a) % n)
        G.add_edge(x, (x - a) % n)
    
    return G

def simulate_infection(G, initial_infected):
    """
    Simulate 2-neighbor infection process
    Returns list of infected sets at each round
    """
    n = G.number_of_nodes()
    infected = set(initial_infected)
    history = [infected.copy()]
    
    max_rounds = n + 5  # Safety limit
    for round_num in range(max_rounds):
        new_infected = set()
        
        for v in range(n):
            if v in infected:
                continue
            
            # Count infected neighbors
            neighbors = list(G.neighbors(v))
            infected_neighbors = sum(1 for nb in neighbors if nb in infected)
            
            if infected_neighbors >= 2:
                new_infected.add(v)
        
        if not new_infected:
            # No new infections, process stops
            break
        
        infected.update(new_infected)
        history.append(infected.copy())
    
    return history

def visualize_infection_process(n, a, initial_infected, output_file, title_prefix):
    """Visualize the infection process round by round"""
    G = create_circulant_graph(n, a)
    history = simulate_infection(G, initial_infected)
    
    # Determine if infection succeeded
    final_infected = history[-1]
    success = len(final_infected) == n
    
    # Create figure with subplots for each round
    num_rounds = len(history)
    cols = min(5, num_rounds)
    rows = (num_rounds + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1:
        axes = axes.reshape(1, -1)
    elif cols == 1:
        axes = axes.reshape(-1, 1)
    
    # Circular layout
    pos = {}
    for i in range(n):
        angle = 2 * np.pi * i / n - np.pi/2
        pos[i] = (np.cos(angle), np.sin(angle))
    
    for round_idx, infected_set in enumerate(history):
        row = round_idx // cols
        col = round_idx % cols
        ax = axes[row, col]
        ax.set_aspect('equal')
        
        # Draw edges
        for edge in G.edges():
            u, v = edge
            diff = (v - u) % n
            if diff == a or diff == n - a:
                # ±a edges (thicker)
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                       color='lightblue', linewidth=2, alpha=0.5, zorder=0)
            else:
                # ±3 edges (thinner)
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                       color='lightgray', linewidth=1, alpha=0.5, zorder=0)
        
        # Determine newly infected in this round
        if round_idx == 0:
            newly_infected = infected_set
        else:
            newly_infected = infected_set - history[round_idx - 1]
        
        # Draw nodes
        for node in range(n):
            if node in newly_infected and round_idx > 0:
                # Newly infected (yellow)
                color = 'yellow'
                edgecolor = 'orange'
                linewidth = 3
            elif node in infected_set:
                # Already infected (red)
                color = 'red'
                edgecolor = 'darkred'
                linewidth = 2
            else:
                # Healthy (white)
                color = 'white'
                edgecolor = 'black'
                linewidth = 1
            
            ax.scatter(pos[node][0], pos[node][1], 
                      c=color, s=300, edgecolors=edgecolor, 
                      linewidths=linewidth, zorder=2)
            ax.text(pos[node][0], pos[node][1], str(node), 
                   ha='center', va='center', fontsize=9, fontweight='bold', zorder=3)
        
        # Title for this round
        if round_idx == 0:
            ax.set_title(f'Initial\n{len(infected_set)} infected', 
                        fontsize=11, fontweight='bold')
        else:
            ax.set_title(f'Round {round_idx}\n+{len(newly_infected)} new', 
                        fontsize=11, fontweight='bold')
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.axis('off')
    
    # Hide unused subplots
    for idx in range(num_rounds, rows * cols):
        row = idx // cols
        col = idx % cols
        axes[row, col].axis('off')
    
    # Overall title
    status = "SUCCESS" if success else "FAILED"
    status_color = "green" if success else "red"
    
    fig.suptitle(f'{title_prefix}\nC_{n}(3,{a}) - Initial set: {{{", ".join(map(str, sorted(initial_infected)))}}}\n' +
                 f'Status: {status} - {len(final_infected)}/{n} vertices infected',
                 fontsize=16, fontweight='bold', color=status_color, y=0.98)
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                  markersize=12, markeredgecolor='darkred', markeredgewidth=2,
                  label='Already infected'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', 
                  markersize=12, markeredgecolor='orange', markeredgewidth=3,
                  label='Newly infected'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='white', 
                  markersize=12, markeredgecolor='black', markeredgewidth=1,
                  label='Healthy')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, 
              fontsize=11, frameon=True, bbox_to_anchor=(0.5, -0.02))
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    print(f"  Status: {status} - {len(final_infected)}/{n} infected after {len(history)-1} rounds")
    plt.close()

# Create output directory
output_dir = "infection_process_visualizations"
os.makedirs(output_dir, exist_ok=True)

print("=" * 70)
print("VISUALIZING INFECTION PROCESSES")
print("=" * 70)
print()

# Case 1: Successful with 2 vertices (m2=2)
print("Case 1: C_12(3,1) - Successful infection with 2 vertices")
print("  Initial set: {0, 2}")
print("  Expected: m2 = 2 (should succeed)")
visualize_infection_process(
    n=12, a=1, 
    initial_infected=[0, 2],
    output_file=f"{output_dir}/success_2_vertices_C12_3_1.png",
    title_prefix="Case 1: Successful Infection (m₂=2)"
)
print()

# Case 2a: Failed with 2 vertices (m2=3)
print("Case 2a: C_12(3,2) - Failed infection with 2 vertices")
print("  Initial set: {0, 1}")
print("  Expected: m2 = 3 (should fail)")
visualize_infection_process(
    n=12, a=2, 
    initial_infected=[0, 1],
    output_file=f"{output_dir}/failed_2_vertices_C12_3_2.png",
    title_prefix="Case 2a: Failed Infection - 2 vertices insufficient (m₂=3)"
)
print()

# Case 2b: Successful with 3 vertices (m2=3)
print("Case 2b: C_12(3,2) - Successful infection with 3 vertices")
print("  Initial set: {0, 1, 2}")
print("  Expected: m2 = 3 (should succeed)")
visualize_infection_process(
    n=12, a=2, 
    initial_infected=[0, 1, 2],
    output_file=f"{output_dir}/success_3_vertices_C12_3_2.png",
    title_prefix="Case 2b: Successful Infection (m₂=3)"
)
print()

# Case 3: Failed infection (deliberately bad initial set)
print("Case 3: C_12(3,2) - Failed infection with poorly chosen 2 vertices")
print("  Initial set: {0, 6} (opposite sides)")
print("  Expected: Should fail (too far apart)")
visualize_infection_process(
    n=12, a=2, 
    initial_infected=[0, 6],
    output_file=f"{output_dir}/failed_opposite_vertices_C12_3_2.png",
    title_prefix="Case 3: Failed Infection - Poor initial placement"
)
print()

print("=" * 70)
print("VISUALIZATION COMPLETE")
print("=" * 70)
print(f"\nAll visualizations saved to: {output_dir}/")
print("\nFiles created:")
print("  1. success_2_vertices_C12_3_1.png - Shows m2=2 success")
print("  2. failed_2_vertices_C12_3_2.png - Shows 2 vertices failing")
print("  3. success_3_vertices_C12_3_2.png - Shows 3 vertices succeeding")
print("  4. failed_opposite_vertices_C12_3_2.png - Shows complete failure")




