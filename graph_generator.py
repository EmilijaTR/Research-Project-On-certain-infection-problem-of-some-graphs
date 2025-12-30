"""
Graph Generator for Quartic Circulant Graphs C_n(3,a)

This module implements the generation of Cayley graphs on the cyclic group Z_n
with connection set {±3, ±a}, resulting in 4-regular circulant graphs.
"""

import math
from typing import List, Tuple, Set


class CayleyGraph:
    """
    Represents a quartic circulant graph C_n(3,a) = Cay(Z_n, {±3, ±a}).
    
    Attributes:
        n: Number of vertices (order of cyclic group Z_n)
        a: Step size parameter (must satisfy constraints)
        vertices: List of vertex labels [0, 1, ..., n-1]
        adjacency: Dictionary mapping each vertex to its set of neighbors
    """
    
    def __init__(self, n: int, a: int):
        """
        Initialize a quartic circulant graph C_n(3,a).
        
        Args:
            n: Number of vertices
            a: Step size (must be valid: gcd(3,a,n)=1, a ≠ 0, ±3 mod n)
        
        Raises:
            ValueError: If parameters don't satisfy connectivity constraints
        """
        if not is_connected_circulant(n, a):
            raise ValueError(f"Graph C_{n}(3,{a}) is not connected: gcd(3,{a},{n}) ≠ 1")
        
        # Normalize a to be in range [0, n-1]
        a = a % n
        
        # Check that a is not 0 or ±3 (mod n)
        if a == 0 or a == 3 or a == (n - 3) % n:
            raise ValueError(f"Invalid parameter a={a} for n={n}: a must not be 0 or ±3 (mod n)")
        
        # Check that a ≠ n/2 (i.e., 2a ≠ 0 mod n) to ensure +a and -a are distinct
        # This ensures we get 4 distinct neighbors, not 3
        if (2 * a) % n == 0:
            raise ValueError(f"Invalid parameter a={a} for n={n}: a = n/2, so +a ≡ -a (mod n), vertices would have only 3 neighbors")
        
        # Check that 3 ≠ n/2 (i.e., 2*3 ≠ 0 mod n) to ensure +3 and -3 are distinct
        if (2 * 3) % n == 0:
            raise ValueError(f"Invalid parameter n={n}: n=6, so +3 ≡ -3 (mod n), vertices would have only 3 neighbors")
        
        self.n = n
        self.a = a
        self.vertices = list(range(n))
        self.adjacency = self._build_adjacency_list()
    
    def _build_adjacency_list(self) -> dict:
        """
        Build the adjacency list representation of the graph.
        
        Returns:
            Dictionary mapping each vertex to a set of its 4 neighbors
        """
        adjacency = {}
        for v in self.vertices:
            neighbors = self.get_neighbors(v)
            # Validate that we actually have 4 distinct neighbors
            if len(neighbors) != 4:
                raise ValueError(f"Vertex {v} has {len(neighbors)} neighbors instead of 4. "
                               f"Parameters n={self.n}, a={self.a} are invalid.")
            adjacency[v] = neighbors
        return adjacency
    
    def get_neighbors(self, vertex: int) -> Set[int]:
        """
        Get the 4 neighbors of a vertex in C_n(3,a).
        
        Each vertex x has neighbors: x+3, x-3, x+a, x-a (all mod n).
        Note: Python's % operator handles negative numbers correctly for our use.
        
        Args:
            vertex: The vertex whose neighbors to find
            
        Returns:
            Set of 4 neighbor vertices
        """
        neighbors = {
            (vertex + 3) % self.n,
            (vertex - 3) % self.n,
            (vertex + self.a) % self.n,
            (vertex - self.a) % self.n
        }
        return neighbors
    
    def __repr__(self):
        return f"CayleyGraph(C_{self.n}(3,{self.a}))"
    
    def __str__(self):
        return f"C_{self.n}(3,{self.a}) with {self.n} vertices"


def is_connected_circulant(n: int, a: int) -> bool:
    """
    Check if C_n(3,a) is connected.
    
    The graph is connected if and only if gcd(3, a, n) = 1.
    
    Args:
        n: Number of vertices
        a: Step size parameter
        
    Returns:
        True if the graph is connected, False otherwise
    """
    # Compute gcd(3, a, n)
    g = math.gcd(3, a)
    g = math.gcd(g, n)
    return g == 1


def get_valid_a_values(n: int) -> List[int]:
    """
    Get all valid values of 'a' for a given n.
    
    Valid means:
    - gcd(3, a, n) = 1 (graph is connected)
    - a ≠ 0, ±3 (mod n) (ensures distinct from step 3)
    - 2a ≢ 0 (mod n) (ensures a ≢ -a, i.e., 4 distinct neighbors not 3)
    - 2*3 ≢ 0 (mod n) (ensures 3 ≢ -3, checked for n)
    - We only need a in range [1, n-1] due to symmetry
    
    Args:
        n: Number of vertices
        
    Returns:
        List of valid 'a' values
    """
    # Check if n=6 (since 2*3 = 6 ≡ 0 mod 6)
    if (2 * 3) % n == 0:
        return []  # No valid graphs for this n with step 3
    
    valid_values = []
    for a in range(1, n):
        # Skip if a ≡ ±3 (mod n)
        if a == 3 or a == (n - 3):
            continue
        
        # Skip if 2a ≡ 0 (mod n), i.e., a = n/2
        if (2 * a) % n == 0:
            continue
        
        # Check connectivity
        if is_connected_circulant(n, a):
            valid_values.append(a)
    
    return valid_values


def generate_all_valid_graphs(n_min: int, n_max: int) -> List[Tuple[int, int, CayleyGraph]]:
    """
    Generate all valid connected C_n(3,a) graphs for n in [n_min, n_max].
    
    Args:
        n_min: Minimum value of n (inclusive)
        n_max: Maximum value of n (inclusive)
        
    Returns:
        List of tuples (n, a, graph) for all valid combinations
    """
    graphs = []
    
    for n in range(n_min, n_max + 1):
        valid_a_values = get_valid_a_values(n)
        
        for a in valid_a_values:
            try:
                graph = CayleyGraph(n, a)
                graphs.append((n, a, graph))
            except ValueError:
                # Skip invalid combinations
                continue
    
    return graphs


if __name__ == "__main__":
    # Test the graph generator
    print("Testing Graph Generator for C_n(3,a)")
    print("=" * 50)
    
    # Test for n=5
    print("\nFor n=5:")
    valid_a = get_valid_a_values(5)
    print(f"Valid a values: {valid_a}")
    
    for a in valid_a:
        graph = CayleyGraph(5, a)
        print(f"\n{graph}")
        print(f"Vertex 0 neighbors: {graph.get_neighbors(0)}")
        print(f"Vertex 1 neighbors: {graph.get_neighbors(1)}")
    
    # Test for n=6
    print("\nFor n=6:")
    valid_a = get_valid_a_values(6)
    print(f"Valid a values: {valid_a}")
    
    # Generate all graphs for n in [5, 8]
    print("\n" + "=" * 50)
    print("All valid graphs for n ∈ [5, 8]:")
    all_graphs = generate_all_valid_graphs(5, 8)
    for n, a, graph in all_graphs:
        print(f"  C_{n}(3,{a})")

