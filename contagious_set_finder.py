"""
Minimum Contagious Set Finder

This module implements algorithms to find the minimum contagious set (infection number)
for quartic circulant graphs using heuristic search strategies.
"""

from typing import Set, Tuple, List
from itertools import combinations
import random
from graph_generator import CayleyGraph
from infection_simulator import simulate_infection


def find_minimum_contagious_set(graph: CayleyGraph, max_size: int = None) -> Tuple[int, Set[int]]:
    """
    Find the infection number m_2(G) and a minimum contagious set.
    
    Uses a hybrid approach:
    1. For small sizes (≤ 4), use exhaustive search
    2. For larger sizes, use heuristic search
    3. Return the first contagious set found and its size
    
    Args:
        graph: The CayleyGraph to analyze
        max_size: Maximum set size to try (defaults to n)
        
    Returns:
        Tuple of (m_2, contagious_set) where m_2 is the infection number
        and contagious_set is one minimum size contagious set
    """
    n = graph.n
    if max_size is None:
        max_size = n
    
    # Try increasing sizes starting from 2
    for size in range(2, max_size + 1):
        # For small sizes with small n, use exhaustive search
        if size <= 4 and n <= 12:
            # Exhaustive search with limit
            max_combinations = min(5000, combinations_count(n, size))
            count = 0
            for candidate in combinations(graph.vertices, size):
                if simulate_infection(graph, set(candidate)):
                    return (size, set(candidate))
                count += 1
                if count >= max_combinations:
                    break
        
        # Heuristic search for larger sizes or if exhaustive didn't work
        candidate_sets = generate_strategic_candidates(graph, size)
        
        for candidate in candidate_sets:
            if simulate_infection(graph, candidate):
                return (size, candidate)
    
    # If nothing worked, the entire vertex set is contagious
    return (n, set(graph.vertices))


def combinations_count(n: int, k: int) -> int:
    """Calculate C(n,k) = n!/(k!(n-k)!)"""
    if k > n or k < 0:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def generate_strategic_candidates(graph: CayleyGraph, size: int, max_random: int = 50) -> List[Set[int]]:
    """
    Generate strategic candidate sets of a given size.
    
    Strategies:
    1. Evenly spaced vertices (good for circulant structure)
    2. Consecutive vertices
    3. Vertices with specific patterns related to step sizes
    4. Random samples (with early termination limit)
    
    Args:
        graph: The CayleyGraph
        size: Size of sets to generate
        max_random: Maximum number of random candidates to try
        
    Returns:
        List of candidate sets to test
    """
    n = graph.n
    candidates = []
    
    # Strategy 1: Evenly spaced vertices
    if size <= n:
        spacing = n // size
        for offset in range(min(spacing, 3)):  # Try a few offsets
            candidate = {(offset + i * spacing) % n for i in range(size)}
            if len(candidate) == size:  # Ensure no duplicates
                candidates.append(candidate)
    
    # Strategy 2: Consecutive vertices starting from different positions
    for start in range(min(n, 5)):  # Try a few starting positions
        candidate = {(start + i) % n for i in range(size)}
        candidates.append(candidate)
    
    # Strategy 3: Pattern based on step sizes (3 and a)
    # Try sets that include vertices connected by the step sizes
    if size >= 2:
        for start in range(min(n, 3)):
            candidate = {start}
            current = start
            for i in range(size - 1):
                # Alternate between +3 and +a steps
                if i % 2 == 0:
                    current = (current + 3) % n
                else:
                    current = (current + graph.a) % n
                candidate.add(current)
            if len(candidate) == size:
                candidates.append(candidate)
    
    # Strategy 4: Vertices at specific distances
    if size >= 2:
        for start in range(min(n, 2)):
            candidate = {start}
            for dist in [graph.a, 3, graph.a + 3]:
                if len(candidate) < size:
                    candidate.add((start + dist) % n)
            if len(candidate) >= size:
                candidates.append(set(list(candidate)[:size]))
    
    # Strategy 5: Random samples (limited to avoid excessive computation)
    random.seed(42)  # For reproducibility
    random_count = 0
    vertices = list(graph.vertices)
    
    # Limit total candidates to avoid excessive testing
    max_total_candidates = min(max_random + 20, 100)
    
    while random_count < max_random and len(candidates) < max_total_candidates:
        candidate = set(random.sample(vertices, size))
        if candidate not in candidates:
            candidates.append(candidate)
            random_count += 1
    
    return candidates[:max_total_candidates]


def find_all_minimum_contagious_sets(graph: CayleyGraph, m2: int, max_search: int = 1000) -> List[Set[int]]:
    """
    Find multiple minimum contagious sets of size m_2.
    
    Useful for understanding the structure of optimal solutions.
    
    Args:
        graph: The CayleyGraph
        m2: The known infection number
        max_search: Maximum number of sets to find
        
    Returns:
        List of contagious sets of size m_2
    """
    n = graph.n
    contagious_sets = []
    
    # Try all combinations of size m2 (limited by max_search)
    count = 0
    for candidate in combinations(graph.vertices, m2):
        candidate_set = set(candidate)
        if simulate_infection(graph, candidate_set):
            contagious_sets.append(candidate_set)
            count += 1
            if count >= max_search:
                break
    
    return contagious_sets


def verify_infection_number(graph: CayleyGraph, claimed_m2: int) -> bool:
    """
    Verify that a claimed infection number is correct.
    
    Checks:
    1. There exists at least one contagious set of size claimed_m2
    2. No contagious set of size claimed_m2 - 1 exists (exhaustive for small sizes)
    
    Args:
        graph: The CayleyGraph
        claimed_m2: The claimed infection number
        
    Returns:
        True if verified, False otherwise
    """
    n = graph.n
    
    # Check if there's a contagious set of the claimed size
    found_m2 = False
    candidates = generate_strategic_candidates(graph, claimed_m2, max_random=200)
    for candidate in candidates:
        if simulate_infection(graph, candidate):
            found_m2 = True
            break
    
    if not found_m2:
        return False
    
    # For small sizes, exhaustively verify no smaller set works
    if claimed_m2 > 1 and claimed_m2 <= 5:
        for candidate in combinations(graph.vertices, claimed_m2 - 1):
            if simulate_infection(graph, set(candidate)):
                return False  # Found a smaller contagious set
    
    return True


if __name__ == "__main__":
    # Test the contagious set finder
    from graph_generator import CayleyGraph
    
    print("Testing Minimum Contagious Set Finder")
    print("=" * 50)
    
    # Test on small graphs
    test_cases = [
        (5, 1),
        (5, 2),
        (6, 1),
        (7, 1),
        (7, 2),
    ]
    
    for n, a in test_cases:
        try:
            graph = CayleyGraph(n, a)
            m2, contagious_set = find_minimum_contagious_set(graph)
            
            print(f"\n{graph}")
            print(f"  m_2 = {m2}")
            print(f"  Example contagious set: {sorted(contagious_set)}")
            
            # Verify the result
            verified = verify_infection_number(graph, m2)
            print(f"  Verified: {verified}")
            
        except ValueError as e:
            print(f"\nC_{n}(3,{a}): {e}")

