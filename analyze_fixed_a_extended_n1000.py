"""
Extended analysis of infection number stability for fixed small values of a.
Analyzes a=4,5,7,8,9,10,12,15,18,21 up to n=1000.
"""

import numpy as np
import matplotlib.pyplot as plt
from graph_generator import CayleyGraph, get_valid_a_values
from contagious_set_finder import find_minimum_contagious_set
import pandas as pd
from tqdm import tqdm
import sys

def analyze_fixed_a(a_value, max_n=1000, min_n=5):
    """
    Analyze infection number for fixed a across increasing n.
    
    Args:
        a_value: Fixed step size to analyze
        max_n: Maximum value of n to test
        min_n: Minimum value of n to test
    
    Returns:
        DataFrame with columns: n, a, m2, is_valid, contagious_set
    """
    results = []
    
    print(f"\nAnalyzing a={a_value} for n in [{min_n}, {max_n}]...")
    
    for n in tqdm(range(min_n, max_n + 1), desc=f"a={a_value}"):
        # Check if this (n, a) combination is valid
        valid_a_list = get_valid_a_values(n)
        
        if a_value in valid_a_list:
            try:
                graph = CayleyGraph(n, a_value)
                m2, contagious_set = find_minimum_contagious_set(graph, max_size=min(20, n))
                
                results.append({
                    'n': n,
                    'a': a_value,
                    'm2': m2,
                    'is_valid': True,
                    'contagious_set': str(sorted(contagious_set))
                })
            except Exception as e:
                print(f"\n  Error at n={n}, a={a_value}: {e}")
                results.append({
                    'n': n,
                    'a': a_value,
                    'm2': None,
                    'is_valid': True,
                    'contagious_set': None
                })
        else:
            results.append({
                'n': n,
                'a': a_value,
                'm2': None,
                'is_valid': False,
                'contagious_set': None
            })
    
    return pd.DataFrame(results)

def analyze_stability(df):
    """
    Analyze when m_2 stabilizes for a given a value.
    
    Args:
        df: DataFrame with results for one value of a
    
    Returns:
        Dictionary with stability analysis
    """
    # Filter to valid graphs only
    valid_df = df[df['is_valid']].copy()
    
    if len(valid_df) == 0:
        return {'stable': False, 'message': 'No valid graphs found', 'stable_value': None, 'stable_from_n': None}
    
    # Get m2 values
    m2_values = valid_df['m2'].dropna().values
    n_values = valid_df[valid_df['m2'].notna()]['n'].values
    
    if len(m2_values) == 0:
        return {'stable': False, 'message': 'No m2 values computed', 'stable_value': None, 'stable_from_n': None}
    
    # Check for exact stability (150+ consecutive same values)
    if len(m2_values) >= 150:
        # Check all possible stable values in the last portion
        unique_vals = set(m2_values[-150:])
        for val in unique_vals:
            # Find longest consecutive run of this value from the end
            consecutive = 0
            first_n = None
            for i in range(len(m2_values) - 1, -1, -1):
                if m2_values[i] == val:
                    consecutive += 1
                    first_n = n_values[i]
                else:
                    break
            
            if consecutive >= 150:
                return {
                    'stable': True,
                    'stable_value': int(val),
                    'stable_from_n': int(first_n),
                    'message': f'Stabilizes to m_2={int(val)} from n>={first_n}'
                }
    
    # Check for approximate stability (within ±1 for last 100)
    if len(m2_values) >= 100:
        last_100 = m2_values[-100:]
        if max(last_100) - min(last_100) <= 1:
            mean_value = np.mean(last_100)
            return {
                'stable': 'approximate',
                'stable_value': round(mean_value, 1),
                'stable_from_n': int(n_values[-100]),
                'message': f'Approximately stable around m_2~{mean_value:.1f}'
            }
    
    return {
        'stable': False,
        'stable_value': None,
        'stable_from_n': None,
        'message': 'No clear stabilization detected'
    }

def plot_single_a(a_value, df, save_path):
    """
    Create a single plot for one value of a.
    
    Args:
        a_value: The value of a
        df: DataFrame with results
        save_path: Path to save the plot
    """
    # Filter to valid graphs with m2 computed
    valid_df = df[df['m2'].notna()].copy()
    
    if len(valid_df) == 0:
        print(f"No valid data for a={a_value}")
        return
    
    # Create single plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    # Plot data
    ax.plot(valid_df['n'], valid_df['m2'], 'o-', markersize=3, linewidth=1, alpha=0.7, color='steelblue')
    
    # Analyze stability
    stability_info = analyze_stability(df)
    
    # Set title and labels based on stability
    if stability_info['stable'] == True:
        title = f'$a = {a_value}$: Stabilizes to $m_2={stability_info["stable_value"]}$ from $n \\geq {stability_info["stable_from_n"]}$'
        ax.axhline(y=stability_info['stable_value'], color='red', linestyle='--', linewidth=2, 
                  label=f'$m_2 = {stability_info["stable_value"]}$ (stable from n$\\geq${stability_info["stable_from_n"]})', alpha=0.8)
        ax.axvline(x=stability_info['stable_from_n'], color='green', linestyle=':', linewidth=1.5, alpha=0.5)
        ax.legend(fontsize=11, loc='best')
    else:
        # Check for approximate stability or oscillation
        max_m2 = int(np.max(valid_df['m2'].values))
        if len(valid_df) >= 100:
            last_100 = valid_df['m2'].values[-100:]
            avg_m2 = np.mean(last_100)
            title = f'$a = {a_value}$: Approximately stable around $m_2 \\approx {avg_m2:.1f}$ (max: {max_m2})'
        else:
            title = f'$a = {a_value}$: No clear stability (max $m_2 = {max_m2}$)'
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Number of vertices ($n$)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Infection number ($m_2$)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0, max(valid_df['n']) + 20)
    
    # Set y-axis limits with some padding
    y_min = max(0, min(valid_df['m2']) - 1)
    y_max = max(valid_df['m2']) + 1
    ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Plot saved to {save_path}")
    plt.close()

def main():
    """Main analysis function."""
    
    # Ensure UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Values of a to analyze
    a_values_to_test = [4, 5, 7, 8, 9, 10, 12, 15, 18, 21]
    max_n = 1000
    
    print("="*70)
    print("EXTENDED FIXED STEP SIZE STABILITY ANALYSIS (n up to 1000)")
    print("="*70)
    print(f"Testing a = {a_values_to_test}")
    print(f"For n up to {max_n}")
    print("="*70)
    
    # Collect results
    all_results = {}
    summary_data = []
    
    for a in a_values_to_test:
        df = analyze_fixed_a(a, max_n=max_n)
        all_results[a] = df
        
        # Save individual CSV
        csv_path = f'analysis_results/fixed_a{a}_n1000_results.csv'
        df.to_csv(csv_path, index=False)
        print(f"  Saved CSV to {csv_path}")
        
        # Analyze stability
        stability = analyze_stability(df)
        print(f"  {stability['message']}")
        
        # Create individual plot
        plot_path = f'analysis_results/fixed_a{a}_stability_n1000.png'
        plot_single_a(a, df, plot_path)
        
        # Add to summary
        summary_data.append({
            'a': a,
            'divisible_by_3': (a % 3 == 0),
            'stable': stability['stable'],
            'stable_value': stability['stable_value'],
            'stable_from_n': stability['stable_from_n'],
            'valid_graphs': df['is_valid'].sum(),
            'computed': df['m2'].notna().sum()
        })
    
    # Save summary
    summary_df = pd.DataFrame(summary_data)
    summary_csv_path = 'analysis_results/comprehensive_stability_summary_n1000.csv'
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"\nSummary saved to {summary_csv_path}")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nSummary:")
    print(summary_df.to_string(index=False))
    
    return all_results, summary_df

if __name__ == "__main__":
    results, summary = main()

