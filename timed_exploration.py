"""
Timed Exploration: Calculate infection numbers for 10 minutes

This script will compute infection numbers for as many graphs as possible
within a 10-minute time limit, then generate plots and CSV outputs.
"""

import time
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

from graph_generator import generate_all_valid_graphs, get_valid_a_values
from contagious_set_finder import find_minimum_contagious_set


def timed_exploration(duration_minutes=10, start_n=5, max_n=None):
    """
    Explore infection numbers for graphs within a time limit.
    
    Args:
        duration_minutes: How long to run (in minutes)
        start_n: Starting value of n
        max_n: Maximum value of n to try (None = no limit, only time constraint)
        
    Returns:
        List of result dictionaries
    """
    duration_seconds = duration_minutes * 60
    start_time = time.time()
    end_time = start_time + duration_seconds
    
    print("=" * 70)
    print(f"TIMED EXPLORATION: {duration_minutes} MINUTES")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"End time: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}")
    print(f"Testing graphs starting from n={start_n}")
    if max_n:
        print(f"Maximum n: {max_n}")
    else:
        print(f"No n limit (time-constrained only)")
    print()
    
    results = []
    n = start_n
    total_graphs = 0
    
    while time.time() < end_time and (max_n is None or n <= max_n):
        # Check if we have time for this n
        elapsed = time.time() - start_time
        remaining = duration_seconds - elapsed
        
        if remaining < 5:  # Need at least 5 seconds
            print(f"\nLess than 5 seconds remaining, stopping...")
            break
        
        # Get valid a values for this n
        valid_a = get_valid_a_values(n)
        
        if not valid_a:
            n += 1
            continue
        
        print(f"\n{'-' * 70}")
        print(f"n = {n} ({len(valid_a)} graphs)")
        print(f"Elapsed: {elapsed:.1f}s / {duration_seconds}s "
              f"({100*elapsed/duration_seconds:.1f}%)")
        print(f"{'-' * 70}")
        
        # Process each graph for this n
        for idx, a in enumerate(valid_a, 1):
            if time.time() >= end_time:
                print(f"\n  Time limit reached at graph {idx}/{len(valid_a)}")
                break
            
            try:
                # Generate graph
                from graph_generator import CayleyGraph
                graph = CayleyGraph(n, a)
                
                # Find infection number
                compute_start = time.time()
                m2, contagious_set = find_minimum_contagious_set(graph)
                compute_time = time.time() - compute_start
                
                # Store result
                result = {
                    'n': n,
                    'a': a,
                    'm2': m2,
                    'contagious_set': sorted(list(contagious_set)),
                    'computation_time': compute_time,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
                total_graphs += 1
                
                # Print progress
                print(f"  [{idx}/{len(valid_a)}] C_{n}(3,{a}): "
                      f"m_2 = {m2}, time = {compute_time:.3f}s", flush=True)
                
            except Exception as e:
                print(f"  [{idx}/{len(valid_a)}] C_{n}(3,{a}): ERROR - {e}")
        
        n += 1
    
    elapsed_total = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)
    print(f"Total time: {elapsed_total:.1f}s ({elapsed_total/60:.2f} minutes)")
    print(f"Graphs computed: {total_graphs}")
    print(f"n range tested: [{start_n}, {n-1}]")
    
    if results:
        print(f"Average time per graph: {elapsed_total/total_graphs:.3f}s")
        print(f"Rate: {total_graphs/(elapsed_total/60):.1f} graphs/minute")
    
    return results


def save_results_to_csv(results, filename):
    """
    Save results to CSV file.
    
    Args:
        results: List of result dictionaries
        filename: Output CSV filename
    """
    if not results:
        print("No results to save")
        return
    
    print(f"\nSaving results to {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['n', 'a', 'm2', 'contagious_set', 'computation_time', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            row = result.copy()
            row['contagious_set'] = str(result['contagious_set'])
            writer.writerow(row)
    
    print(f"Saved {len(results)} results to {filename}")


def generate_analysis_plots(results, output_prefix="timed_exploration"):
    """
    Generate analysis plots from the results.
    
    Args:
        results: List of result dictionaries
        output_prefix: Prefix for output filenames
    """
    if not results:
        print("No results to plot")
        return
    
    print("\nGenerating plots...")
    
    # Extract data
    n_values = [r['n'] for r in results]
    m2_values = [r['m2'] for r in results]
    
    # Group by n
    data_by_n = defaultdict(list)
    for r in results:
        data_by_n[r['n']].append(r['m2'])
    
    unique_n = sorted(data_by_n.keys())
    
    # Plot 1: m_2 vs n (all points)
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Color by m_2 value
    colors = {2: 'blue', 3: 'orange', 4: 'red', 5: 'purple', 6: 'brown'}
    for m2_val in sorted(set(m2_values)):
        mask = [m2 == m2_val for m2 in m2_values]
        n_filtered = [n for n, m in zip(n_values, mask) if m]
        m2_filtered = [m2 for m2, m in zip(m2_values, mask) if m]
        
        color = colors.get(m2_val, 'gray')
        ax.scatter(n_filtered, m2_filtered, label=f'm_2={m2_val}', 
                  alpha=0.6, s=50, color=color)
    
    ax.set_xlabel('n (number of vertices)', fontsize=12)
    ax.set_ylabel('m₂ (infection number)', fontsize=12)
    ax.set_title(f'Infection Numbers: {len(results)} Graphs Tested', 
                fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    filename1 = f"{output_prefix}_scatter.png"
    plt.tight_layout()
    plt.savefig(filename1, dpi=200, bbox_inches='tight')
    print(f"Saved: {filename1}")
    plt.close()
    
    # Plot 2: Distribution by n (box plot or bar chart)
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Calculate statistics for each n
    n_labels = []
    m2_min = []
    m2_max = []
    m2_avg = []
    counts = []
    
    for n in unique_n:
        values = data_by_n[n]
        n_labels.append(str(n))
        m2_min.append(min(values))
        m2_max.append(max(values))
        m2_avg.append(sum(values) / len(values))
        counts.append(len(values))
    
    x_pos = np.arange(len(n_labels))
    width = 0.6
    
    # Plot bars showing range
    for i, n in enumerate(unique_n):
        values = data_by_n[n]
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        
        # Bar from min to max
        ax.bar(i, max_val - min_val, width, bottom=min_val, 
              alpha=0.3, color='steelblue', edgecolor='navy')
        # Average marker
        ax.scatter(i, avg_val, color='red', s=100, zorder=5, marker='_', linewidths=3)
    
    ax.set_xlabel('n (number of vertices)', fontsize=12)
    ax.set_ylabel('m₂ (infection number)', fontsize=12)
    ax.set_title('Infection Number Distribution by n\n(bars show range, red line shows average)',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(n_labels)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add count labels
    for i, count in enumerate(counts):
        ax.text(i, ax.get_ylim()[1] * 0.95, f'n={count}', 
               ha='center', va='top', fontsize=9, color='gray')
    
    filename2 = f"{output_prefix}_distribution.png"
    plt.tight_layout()
    plt.savefig(filename2, dpi=200, bbox_inches='tight')
    print(f"Saved: {filename2}")
    plt.close()
    
    # Plot 3: Cumulative progress
    fig, ax = plt.subplots(figsize=(12, 6))
    
    cumulative_counts = []
    count = 0
    for n in unique_n:
        count += len(data_by_n[n])
        cumulative_counts.append(count)
    
    ax.plot(unique_n, cumulative_counts, marker='o', linewidth=2, markersize=6)
    ax.fill_between(unique_n, cumulative_counts, alpha=0.3)
    
    ax.set_xlabel('n (number of vertices)', fontsize=12)
    ax.set_ylabel('Cumulative graphs tested', fontsize=12)
    ax.set_title('Exploration Progress', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add final count annotation
    ax.annotate(f'Total: {count} graphs', 
               xy=(unique_n[-1], cumulative_counts[-1]),
               xytext=(10, -20), textcoords='offset points',
               fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
               arrowprops=dict(arrowstyle='->', lw=2))
    
    filename3 = f"{output_prefix}_progress.png"
    plt.tight_layout()
    plt.savefig(filename3, dpi=200, bbox_inches='tight')
    print(f"Saved: {filename3}")
    plt.close()


def print_summary_statistics(results):
    """
    Print summary statistics from the results.
    
    Args:
        results: List of result dictionaries
    """
    if not results:
        return
    
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    
    # Group by n
    data_by_n = defaultdict(list)
    for r in results:
        data_by_n[r['n']].append(r['m2'])
    
    # Overall statistics
    all_m2 = [r['m2'] for r in results]
    print(f"\nOverall:")
    print(f"  Graphs tested: {len(results)}")
    print(f"  n range: [{min(r['n'] for r in results)}, {max(r['n'] for r in results)}]")
    print(f"  m_2 range: [{min(all_m2)}, {max(all_m2)}]")
    print(f"  Average m_2: {sum(all_m2)/len(all_m2):.2f}")
    
    # Distribution by m_2
    m2_counts = defaultdict(int)
    for m2 in all_m2:
        m2_counts[m2] += 1
    
    print(f"\nDistribution by infection number:")
    for m2 in sorted(m2_counts.keys()):
        count = m2_counts[m2]
        pct = 100 * count / len(results)
        print(f"  m_2 = {m2}: {count} graphs ({pct:.1f}%)")
    
    # By n
    print(f"\nBy n value:")
    for n in sorted(data_by_n.keys()):
        values = data_by_n[n]
        print(f"  n={n:3d}: {len(values):3d} graphs, "
              f"m_2 ∈ [{min(values)}, {max(values)}], "
              f"avg = {sum(values)/len(values):.2f}")
    
    print("=" * 70)


if __name__ == "__main__":
    # Configuration
    DURATION_MINUTES = 10
    START_N = 5
    OUTPUT_PREFIX = "timed_exploration_10min_extended"
    
    print("Starting timed exploration...")
    print(f"Duration: {DURATION_MINUTES} minutes")
    print("No n limit - exploring as far as time allows!")
    print()
    
    # Run exploration (no max_n limit)
    results = timed_exploration(
        duration_minutes=DURATION_MINUTES,
        start_n=START_N,
        max_n=None  # No limit! Will run until time expires
    )
    
    if results:
        # Save CSV
        csv_filename = f"{OUTPUT_PREFIX}.csv"
        save_results_to_csv(results, csv_filename)
        
        # Generate plots
        generate_analysis_plots(results, OUTPUT_PREFIX)
        
        # Print statistics
        print_summary_statistics(results)
        
        print("\n" + "=" * 70)
        print("ALL OUTPUTS GENERATED")
        print("=" * 70)
        print(f"  • CSV data: {csv_filename}")
        print(f"  • Scatter plot: {OUTPUT_PREFIX}_scatter.png")
        print(f"  • Distribution: {OUTPUT_PREFIX}_distribution.png")
        print(f"  • Progress: {OUTPUT_PREFIX}_progress.png")
        print("=" * 70)
    else:
        print("\nNo results collected (time limit too short or error occurred)")


