"""
Infection Simulator for the 2-Neighbor Threshold Model

This module implements the deterministic infection spreading process:
- A healthy vertex becomes infected if at least 2 of its neighbors are infected
- Once infected, a vertex remains infected permanently
"""

from typing import Set, List
from graph_generator import CayleyGraph


def simulate_infection(graph: CayleyGraph, initial_infected: Set[int]) -> bool:
    """
    Simulate the 2-neighbor threshold infection process.
    
    The infection spreads in discrete rounds:
    - In each round, a healthy vertex becomes infected if ≥2 neighbors are infected
    - Process continues until no new infections occur
    - Returns True if all vertices eventually become infected
    
    Args:
        graph: The CayleyGraph to simulate on
        initial_infected: Set of initially infected vertices
        
    Returns:
        True if all vertices become infected, False otherwise
    """
    # Initialize infected set
    infected = set(initial_infected)
    n = graph.n
    
    # Keep spreading until no new infections occur
    changed = True
    while changed:
        changed = False
        new_infected = set()
        
        # Check each healthy vertex
        for vertex in graph.vertices:
            if vertex not in infected:
                # Count infected neighbors
                neighbors = graph.get_neighbors(vertex)
                infected_neighbor_count = sum(1 for neighbor in neighbors if neighbor in infected)
                
                # Infect if threshold reached (≥2 infected neighbors)
                if infected_neighbor_count >= 2:
                    new_infected.add(vertex)
                    changed = True
        
        # Add newly infected vertices
        infected.update(new_infected)
    
    # Check if all vertices are infected
    return len(infected) == n


def get_infection_spread_sequence(graph: CayleyGraph, initial_infected: Set[int]) -> List[Set[int]]:
    """
    Get the sequence of infected sets at each round of the infection process.
    
    Useful for visualizing and understanding how the infection spreads.
    
    Args:
        graph: The CayleyGraph to simulate on
        initial_infected: Set of initially infected vertices
        
    Returns:
        List of sets, where each set contains the infected vertices at that round
    """
    infected = set(initial_infected)
    sequence = [infected.copy()]
    
    changed = True
    while changed:
        changed = False
        new_infected = set()
        
        for vertex in graph.vertices:
            if vertex not in infected:
                neighbors = graph.get_neighbors(vertex)
                infected_neighbor_count = sum(1 for neighbor in neighbors if neighbor in infected)
                
                if infected_neighbor_count >= 2:
                    new_infected.add(vertex)
                    changed = True
        
        infected.update(new_infected)
        if changed:
            sequence.append(infected.copy())
    
    return sequence


def is_contagious_set(graph: CayleyGraph, candidate_set: Set[int]) -> bool:
    """
    Check if a given set is contagious (i.e., infects the entire graph).
    
    Args:
        graph: The CayleyGraph to test on
        candidate_set: Set of vertices to test as initial infection
        
    Returns:
        True if the set is contagious, False otherwise
    """
    return simulate_infection(graph, candidate_set)


if __name__ == "__main__":
    # Test the infection simulator
    from graph_generator import CayleyGraph
    
    print("Testing Infection Simulator")
    print("=" * 50)
    
    # Test on C_5(3,1)
    print("\nTest 1: C_5(3,1)")
    graph = CayleyGraph(5, 1)
    print(f"Graph: {graph}")
    
    # Test with initial set {0, 1}
    initial = {0, 1}
    print(f"Initial infected: {initial}")
    result = simulate_infection(graph, initial)
    print(f"Infects all vertices: {result}")
    
    # Show the infection sequence
    sequence = get_infection_spread_sequence(graph, initial)
    print(f"Infection sequence:")
    for round_num, infected_set in enumerate(sequence):
        print(f"  Round {round_num}: {sorted(infected_set)}")
    
    # Test with a non-contagious set
    print("\nTest 2: Single vertex")
    initial = {0}
    print(f"Initial infected: {initial}")
    result = simulate_infection(graph, initial)
    print(f"Infects all vertices: {result}")
    
    sequence = get_infection_spread_sequence(graph, initial)
    print(f"Infection sequence:")
    for round_num, infected_set in enumerate(sequence):
        print(f"  Round {round_num}: {sorted(infected_set)}")
    
    # Test on C_6(3,1)
    print("\nTest 3: C_6(3,1)")
    graph = CayleyGraph(6, 1)
    print(f"Graph: {graph}")
    
    initial = {0, 1}
    print(f"Initial infected: {initial}")
    result = simulate_infection(graph, initial)
    print(f"Infects all vertices: {result}")
    
    sequence = get_infection_spread_sequence(graph, initial)
    print(f"Infection sequence:")
    for round_num, infected_set in enumerate(sequence):
        print(f"  Round {round_num}: {sorted(infected_set)}")


