"""
Data Collector for Infection Number Analysis

This module collects infection number data for multiple graphs and organizes
the results for analysis and visualization.
"""

from typing import List, Dict, Tuple
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from graph_generator import generate_all_valid_graphs, CayleyGraph
from contagious_set_finder import find_minimum_contagious_set


def _process_single_graph(args: Tuple[int, int, int, CayleyGraph]) -> Dict:
    """
    Process a single graph (helper function for parallel processing).
    
    Args:
        args: Tuple of (idx, n, a, graph)
        
    Returns:
        Dictionary with results for this graph
    """
    idx, n, a, graph = args
    
    # Measure computation time
    start_time = time.time()
    m2, contagious_set = find_minimum_contagious_set(graph)
    computation_time = time.time() - start_time
    
    # Return results including index for ordering
    return {
        'idx': idx,
        'n': n,
        'a': a,
        'm2': m2,
        'contagious_set': sorted(list(contagious_set)),
        'computation_time': computation_time
    }


def collect_infection_data(n_min: int, n_max: int, verbose: bool = True, parallel: bool = True, max_workers: int = None) -> List[Dict]:
    """
    Collect infection number data for all valid C_n(3,a) graphs in the given range.
    
    For each valid (n, a) pair:
    - Generate the graph C_n(3,a)
    - Compute the infection number m_2
    - Find one minimum contagious set
    - Record all results
    
    Args:
        n_min: Minimum value of n (inclusive)
        n_max: Maximum value of n (inclusive)
        verbose: If True, print progress information
        parallel: If True, use parallel processing (default: True)
        max_workers: Maximum number of parallel workers (default: CPU count)
        
    Returns:
        List of dictionaries, each containing:
        - 'n': number of vertices
        - 'a': step size parameter
        - 'm2': infection number
        - 'contagious_set': one minimum contagious set (as sorted list)
        - 'computation_time': time taken to find m_2 (in seconds)
    """
    if verbose:
        print(f"Collecting infection number data for n ∈ [{n_min}, {n_max}]")
        print("=" * 60)
    
    # Generate all valid graphs
    all_graphs = generate_all_valid_graphs(n_min, n_max)
    
    if verbose:
        print(f"Found {len(all_graphs)} valid connected graphs")
        if parallel:
            print(f"Using parallel processing with {max_workers or 'default'} workers")
        print()
    
    # Prepare arguments for processing
    graph_args = [(idx, n, a, graph) for idx, (n, a, graph) in enumerate(all_graphs, 1)]
    
    if parallel:
        # Parallel processing
        data_dict = {}
        completed = 0
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_args = {executor.submit(_process_single_graph, args): args for args in graph_args}
            
            # Process results as they complete
            for future in as_completed(future_to_args):
                args = future_to_args[future]
                idx, n, a, _ = args
                
                try:
                    result = future.result()
                    data_dict[result['idx']] = result
                    completed += 1
                    
                    if verbose:
                        print(f"[{completed}/{len(all_graphs)}] Completed C_{n}(3,{a}): "
                              f"m_2 = {result['m2']}, set = {result['contagious_set']}, "
                              f"time = {result['computation_time']:.3f}s", flush=True)
                except Exception as e:
                    print(f"Error processing C_{n}(3,{a}): {e}")
        
        # Sort by index and remove index field
        data = []
        for idx in sorted(data_dict.keys()):
            result = data_dict[idx]
            del result['idx']
            data.append(result)
    
    else:
        # Sequential processing (original behavior)
        data = []
        for idx, (n, a, graph) in enumerate(all_graphs, 1):
            if verbose:
                print(f"[{idx}/{len(all_graphs)}] Processing C_{n}(3,{a})...", end=" ", flush=True)
            
            start_time = time.time()
            m2, contagious_set = find_minimum_contagious_set(graph)
            computation_time = time.time() - start_time
            
            result = {
                'n': n,
                'a': a,
                'm2': m2,
                'contagious_set': sorted(list(contagious_set)),
                'computation_time': computation_time
            }
            data.append(result)
            
            if verbose:
                print(f"m_2 = {m2}, set = {result['contagious_set']}, "
                      f"time = {computation_time:.3f}s", flush=True)
    
    if verbose:
        print()
        print("=" * 60)
        print(f"Data collection complete: {len(data)} graphs analyzed")
    
    return data


def summarize_data(data: List[Dict]) -> Dict:
    """
    Generate summary statistics from collected data.
    
    Args:
        data: List of data dictionaries from collect_infection_data
        
    Returns:
        Dictionary of summary statistics
    """
    if not data:
        return {}
    
    m2_values = [d['m2'] for d in data]
    n_values = [d['n'] for d in data]
    times = [d['computation_time'] for d in data]
    
    summary = {
        'total_graphs': len(data),
        'n_range': (min(n_values), max(n_values)),
        'm2_range': (min(m2_values), max(m2_values)),
        'm2_mean': sum(m2_values) / len(m2_values),
        'total_time': sum(times),
        'avg_time_per_graph': sum(times) / len(times),
        'graphs_by_n': {}
    }
    
    # Count graphs by n
    for d in data:
        n = d['n']
        if n not in summary['graphs_by_n']:
            summary['graphs_by_n'][n] = 0
        summary['graphs_by_n'][n] += 1
    
    return summary


def get_data_by_n(data: List[Dict], n: int) -> List[Dict]:
    """
    Filter data to only include graphs with a specific n value.
    
    Args:
        data: List of data dictionaries
        n: Value of n to filter by
        
    Returns:
        Filtered list of data dictionaries
    """
    return [d for d in data if d['n'] == n]


def get_unique_n_values(data: List[Dict]) -> List[int]:
    """
    Get sorted list of unique n values in the data.
    
    Args:
        data: List of data dictionaries
        
    Returns:
        Sorted list of unique n values
    """
    return sorted(list(set(d['n'] for d in data)))


def get_unique_a_values(data: List[Dict]) -> List[int]:
    """
    Get sorted list of unique a values in the data.
    
    Args:
        data: List of data dictionaries
        
    Returns:
        Sorted list of unique a values
    """
    return sorted(list(set(d['a'] for d in data)))


if __name__ == "__main__":
    # Test data collection on a small range
    print("Testing Data Collector")
    print("=" * 60)
    
    # Collect data for n in [5, 7]
    data = collect_infection_data(5, 7, verbose=True)
    
    # Show summary
    print("\nSummary Statistics:")
    summary = summarize_data(data)
    print(f"  Total graphs analyzed: {summary['total_graphs']}")
    print(f"  n range: {summary['n_range']}")
    print(f"  m_2 range: {summary['m2_range']}")
    print(f"  Average m_2: {summary['m2_mean']:.2f}")
    print(f"  Total computation time: {summary['total_time']:.2f}s")
    print(f"  Graphs by n: {summary['graphs_by_n']}")
    
    # Show data for each n
    print("\nData by n:")
    for n in get_unique_n_values(data):
        n_data = get_data_by_n(data, n)
        print(f"  n={n}: {len(n_data)} graphs")
        for d in n_data:
            print(f"    C_{d['n']}(3,{d['a']}): m_2 = {d['m2']}")

