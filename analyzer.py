"""
Data Analysis and Visualization

This module provides functions for analyzing infection number data,
generating tables, creating plots, and identifying patterns.
"""

from typing import List, Dict
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


def generate_tables(data: List[Dict]) -> None:
    """
    Print formatted tables of infection number data to console.
    
    Tables are grouped by n for easier reading.
    
    Args:
        data: List of data dictionaries from data collection
    """
    if not data:
        print("No data to display")
        return
    
    print("\n" + "=" * 80)
    print("INFECTION NUMBER DATA FOR C_n(3,a)")
    print("=" * 80)
    
    # Group data by n
    data_by_n = defaultdict(list)
    for d in data:
        data_by_n[d['n']].append(d)
    
    # Print table for each n
    for n in sorted(data_by_n.keys()):
        n_data = data_by_n[n]
        
        print(f"\n{'─' * 80}")
        print(f"n = {n} ({len(n_data)} valid values of a)")
        print(f"{'─' * 80}")
        print(f"{'a':>5} │ {'m_2':>5} │ {'Contagious Set':^40} │ {'Time (s)':>10}")
        print(f"{'─' * 5}─┼─{'─' * 5}─┼─{'─' * 40}─┼─{'─' * 10}")
        
        for d in sorted(n_data, key=lambda x: x['a']):
            contagious_str = str(d['contagious_set'])
            if len(contagious_str) > 40:
                contagious_str = contagious_str[:37] + "..."
            
            print(f"{d['a']:5d} │ {d['m2']:5d} │ {contagious_str:40s} │ {d['computation_time']:10.4f}")
    
    print("\n" + "=" * 80)


def export_to_csv(data: List[Dict], filename: str) -> None:
    """
    Export infection number data to a CSV file.
    
    Args:
        data: List of data dictionaries
        filename: Output CSV filename
    """
    if not data:
        print(f"No data to export to {filename}")
        return
    
    # Write CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['n', 'a', 'm2', 'contagious_set', 'computation_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for d in data:
            # Convert contagious_set to string for CSV
            row = d.copy()
            row['contagious_set'] = str(d['contagious_set'])
            writer.writerow(row)
    
    print(f"\nData exported to: {filename}")


def create_plots(data: List[Dict], output_prefix: str = "infection") -> None:
    """
    Create multiple visualization plots of the infection number data.
    
    Creates:
    1. m_2 vs n scatter plot (different colors for different a values)
    2. Heatmap of m_2 values (n vs a)
    3. Distribution of m_2 values (histogram)
    
    Args:
        data: List of data dictionaries
        output_prefix: Prefix for output filenames
    """
    if not data:
        print("No data to plot")
        return
    
    # Extract data for plotting
    n_values = [d['n'] for d in data]
    a_values = [d['a'] for d in data]
    m2_values = [d['m2'] for d in data]
    
    # Set up style
    plt.style.use('default')
    
    # Plot 1: m_2 vs n (scatter plot)
    plt.figure(figsize=(12, 6))
    
    # Group by a value for coloring
    unique_a = sorted(set(a_values))
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_a)))
    
    for idx, a in enumerate(unique_a):
        a_data = [d for d in data if d['a'] == a]
        n_vals = [d['n'] for d in a_data]
        m2_vals = [d['m2'] for d in a_data]
        plt.scatter(n_vals, m2_vals, label=f'a={a}', alpha=0.7, s=100, color=colors[idx])
    
    plt.xlabel('n (number of vertices)', fontsize=12)
    plt.ylabel('m₂(C_n(3,a)) (infection number)', fontsize=12)
    plt.title('Infection Number vs Graph Size', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    filename1 = f"{output_prefix}_vs_n.png"
    plt.savefig(filename1, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {filename1}")
    plt.close()
    
    # Plot 2: Heatmap of m_2 values
    plt.figure(figsize=(14, 8))
    
    # Create matrix for heatmap
    unique_n = sorted(set(n_values))
    unique_a = sorted(set(a_values))
    
    # Create a mapping
    heatmap_data = np.full((len(unique_n), len(unique_a)), np.nan)
    
    for d in data:
        n_idx = unique_n.index(d['n'])
        a_idx = unique_a.index(d['a'])
        heatmap_data[n_idx, a_idx] = d['m2']
    
    # Create heatmap
    im = plt.imshow(heatmap_data, aspect='auto', cmap='YlOrRd', interpolation='nearest')
    
    # Set ticks
    plt.xticks(range(len(unique_a)), unique_a, rotation=45)
    plt.yticks(range(len(unique_n)), unique_n)
    
    plt.xlabel('a (step size parameter)', fontsize=12)
    plt.ylabel('n (number of vertices)', fontsize=12)
    plt.title('Heatmap of Infection Numbers m₂(C_n(3,a))', fontsize=14, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('m₂ (infection number)', fontsize=11)
    
    # Add values to cells
    for i in range(len(unique_n)):
        for j in range(len(unique_a)):
            if not np.isnan(heatmap_data[i, j]):
                text = plt.text(j, i, int(heatmap_data[i, j]),
                               ha="center", va="center", color="black", fontsize=8)
    
    plt.tight_layout()
    
    filename2 = f"{output_prefix}_heatmap.png"
    plt.savefig(filename2, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {filename2}")
    plt.close()
    
    # Plot 3: Distribution of m_2 values
    plt.figure(figsize=(10, 6))
    
    plt.hist(m2_values, bins=range(min(m2_values), max(m2_values) + 2), 
             alpha=0.7, color='steelblue', edgecolor='black')
    
    plt.xlabel('m₂ (infection number)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Infection Numbers', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add mean line
    mean_m2 = np.mean(m2_values)
    plt.axvline(mean_m2, color='red', linestyle='--', linewidth=2, 
                label=f'Mean = {mean_m2:.2f}')
    plt.legend()
    
    plt.tight_layout()
    
    filename3 = f"{output_prefix}_distribution.png"
    plt.savefig(filename3, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {filename3}")
    plt.close()
    
    print(f"\nAll plots created successfully!")


def identify_patterns(data: List[Dict]) -> None:
    """
    Analyze the data to identify patterns and generate observations.
    
    Args:
        data: List of data dictionaries
    """
    if not data:
        print("No data to analyze")
        return
    
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS AND OBSERVATIONS")
    print("=" * 80)
    
    # Group by n
    data_by_n = defaultdict(list)
    for d in data:
        data_by_n[d['n']].append(d)
    
    # Analyze patterns
    print("\n1. INFECTION NUMBER BY n:")
    print("   " + "─" * 60)
    
    n_stats = {}
    for n in sorted(data_by_n.keys()):
        n_data = data_by_n[n]
        m2_values = [d['m2'] for d in n_data]
        
        n_stats[n] = {
            'min': min(m2_values),
            'max': max(m2_values),
            'mean': sum(m2_values) / len(m2_values),
            'count': len(m2_values)
        }
        
        print(f"   n={n:2d}: m₂ ∈ [{n_stats[n]['min']:2d}, {n_stats[n]['max']:2d}], "
              f"avg={n_stats[n]['mean']:.2f}, "
              f"({n_stats[n]['count']} graphs)")
    
    # Check if m_2 grows with n
    print("\n2. GROWTH TREND:")
    print("   " + "─" * 60)
    
    n_list = sorted(n_stats.keys())
    if len(n_list) > 1:
        avg_m2_list = [n_stats[n]['mean'] for n in n_list]
        
        # Check if generally increasing
        increasing = all(avg_m2_list[i] <= avg_m2_list[i+1] for i in range(len(avg_m2_list)-1))
        
        if increasing:
            print(f"   ✓ m₂ appears to INCREASE as n increases")
        else:
            print(f"   • m₂ does not consistently increase with n")
        
        # Calculate growth rate
        if len(n_list) > 2:
            growth_rates = []
            for i in range(len(n_list) - 1):
                rate = (avg_m2_list[i+1] - avg_m2_list[i]) / (n_list[i+1] - n_list[i])
                growth_rates.append(rate)
            
            avg_growth = sum(growth_rates) / len(growth_rates)
            print(f"   • Average growth rate: Δm₂/Δn ≈ {avg_growth:.2f}")
    
    # Check relationship with a
    print("\n3. DEPENDENCY ON PARAMETER a:")
    print("   " + "─" * 60)
    
    # For each n, check if m_2 varies with a
    for n in sorted(data_by_n.keys()):
        n_data = data_by_n[n]
        if len(n_data) > 1:
            m2_values = [d['m2'] for d in n_data]
            if min(m2_values) == max(m2_values):
                print(f"   n={n}: m₂ is CONSTANT (m₂={m2_values[0]}) for all valid a")
            else:
                print(f"   n={n}: m₂ VARIES with a (range: [{min(m2_values)}, {max(m2_values)}])")
    
    # Special cases
    print("\n4. SPECIAL CASES:")
    print("   " + "─" * 60)
    
    # Check for n divisible by 3
    divisible_by_3 = [n for n in n_list if n % 3 == 0]
    not_divisible_by_3 = [n for n in n_list if n % 3 != 0]
    
    if divisible_by_3 and not_divisible_by_3:
        avg_div3 = sum(n_stats[n]['mean'] for n in divisible_by_3) / len(divisible_by_3)
        avg_not_div3 = sum(n_stats[n]['mean'] for n in not_divisible_by_3) / len(not_divisible_by_3)
        
        print(f"   • When 3|n: average m₂ = {avg_div3:.2f}")
        print(f"   • When 3∤n: average m₂ = {avg_not_div3:.2f}")
    
    # Most common m_2 values
    all_m2 = [d['m2'] for d in data]
    m2_counts = defaultdict(int)
    for m2 in all_m2:
        m2_counts[m2] += 1
    
    print("\n5. MOST COMMON INFECTION NUMBERS:")
    print("   " + "─" * 60)
    for m2, count in sorted(m2_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = 100 * count / len(data)
        print(f"   m₂={m2}: {count} graphs ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)


def generate_conjectures(data: List[Dict]) -> None:
    """
    Based on observed patterns, generate mathematical conjectures.
    
    Args:
        data: List of data dictionaries
    """
    print("\n" + "=" * 80)
    print("PROPOSED CONJECTURES")
    print("=" * 80)
    
    # Group by n
    data_by_n = defaultdict(list)
    for d in data:
        data_by_n[d['n']].append(d)
    
    n_list = sorted(data_by_n.keys())
    
    # Analyze m_2 values for each n
    print("\nBased on the computational data, we propose the following conjectures:\n")
    
    # Conjecture 1: Check if m_2 is constant for each n
    print("Conjecture 1:")
    constant_for_all_n = True
    for n in n_list:
        m2_values = [d['m2'] for d in data_by_n[n]]
        if len(set(m2_values)) > 1:
            constant_for_all_n = False
            break
    
    if constant_for_all_n:
        print("   For each fixed n, m₂(C_n(3,a)) is CONSTANT for all valid a.")
        print("   This suggests m₂ depends only on n, not on a.")
    else:
        print("   m₂(C_n(3,a)) may depend on both n and a.")
    
    # Conjecture 2: Formula for m_2
    print("\nConjecture 2:")
    
    # Check different formulas
    formulas = {
        '⌈n/3⌉': lambda n: (n + 2) // 3,
        '⌈n/2⌉': lambda n: (n + 1) // 2,
        '⌊n/3⌋': lambda n: n // 3,
        '⌊n/2⌋': lambda n: n // 2,
        '2': lambda n: 2,
        '3': lambda n: 3,
    }
    
    best_formula = None
    best_match_count = 0
    
    for formula_name, formula_func in formulas.items():
        match_count = 0
        for d in data:
            predicted = formula_func(d['n'])
            if predicted == d['m2']:
                match_count += 1
        
        if match_count > best_match_count:
            best_match_count = match_count
            best_formula = formula_name
    
    if best_match_count == len(data):
        print(f"   m₂(C_n(3,a)) = {best_formula} for all tested cases!")
        print(f"   (Matches {best_match_count}/{len(data)} graphs)")
    elif best_match_count > len(data) * 0.8:
        print(f"   m₂(C_n(3,a)) ≈ {best_formula} in most cases")
        print(f"   (Matches {best_match_count}/{len(data)} graphs, {100*best_match_count/len(data):.1f}%)")
    else:
        print(f"   No simple formula found. Best approximation: {best_formula}")
        print(f"   (Matches {best_match_count}/{len(data)} graphs, {100*best_match_count/len(data):.1f}%)")
    
    # Show actual m_2 values by n
    print("\n   Observed values:")
    for n in n_list:
        m2_values = sorted(set(d['m2'] for d in data_by_n[n]))
        if len(m2_values) == 1:
            print(f"      n={n:2d}: m₂ = {m2_values[0]}")
        else:
            print(f"      n={n:2d}: m₂ ∈ {{{', '.join(map(str, m2_values))}}}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Test with sample data
    print("Testing Analyzer Module")
    print("=" * 60)
    
    # Create some dummy data
    sample_data = [
        {'n': 5, 'a': 1, 'm2': 2, 'contagious_set': [0, 1], 'computation_time': 0.001},
        {'n': 5, 'a': 2, 'm2': 2, 'contagious_set': [0, 2], 'computation_time': 0.001},
        {'n': 6, 'a': 1, 'm2': 2, 'contagious_set': [0, 1], 'computation_time': 0.002},
        {'n': 7, 'a': 1, 'm2': 3, 'contagious_set': [0, 1, 2], 'computation_time': 0.003},
    ]
    
    generate_tables(sample_data)
    identify_patterns(sample_data)
    generate_conjectures(sample_data)


