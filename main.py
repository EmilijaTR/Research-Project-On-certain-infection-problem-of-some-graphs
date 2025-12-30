"""
Main Program for Infection Number Analysis

This is the main entry point for the computational exploration of infection
numbers in quartic circulant graphs C_n(3,a).

Usage:
    python main.py

This will:
1. Generate all valid C_n(3,a) graphs for n ∈ [5, 10]
2. Compute infection numbers m_2 for each graph
3. Generate console tables, CSV export, and visualization plots
4. Analyze patterns and propose conjectures
"""

import sys
import time
from datetime import datetime

from data_collector import collect_infection_data, summarize_data
from analyzer import (generate_tables, export_to_csv, create_plots, 
                     identify_patterns, generate_conjectures)


def main():
    """
    Main function to orchestrate the computational exploration.
    """
    print("\n" + "=" * 80)
    print(" COMPUTATIONAL EXPLORATION OF INFECTION NUMBERS IN C_n(3,a)")
    print("=" * 80)
    print(f"\n Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n This program will:")
    print("   1. Generate all valid connected C_n(3,a) graphs for n ∈ [5, 10]")
    print("   2. Compute the infection number m_2 for each graph")
    print("   3. Find one minimum contagious set for each graph")
    print("   4. Export results to CSV")
    print("   5. Create visualization plots")
    print("   6. Analyze patterns and generate conjectures")
    print("\n" + "=" * 80)
    
    # Configuration
    N_MIN = 5
    N_MAX = 10
    CSV_FILENAME = f"infection_data_n{N_MIN}_to_{N_MAX}.csv"
    PLOT_PREFIX = "infection"
    
    # Step 1: Collect data
    print("\n" + "─" * 80)
    print("STEP 1: DATA COLLECTION")
    print("─" * 80)
    
    start_time = time.time()
    data = collect_infection_data(N_MIN, N_MAX, verbose=True)
    collection_time = time.time() - start_time
    
    if not data:
        print("\n ERROR: No data collected. Exiting.")
        sys.exit(1)
    
    # Show summary
    summary = summarize_data(data)
    print(f"\n Summary:")
    print(f"   • Total graphs analyzed: {summary['total_graphs']}")
    print(f"   • n range: {summary['n_range']}")
    print(f"   • m₂ range: {summary['m2_range']}")
    print(f"   • Average m₂: {summary['m2_mean']:.2f}")
    print(f"   • Total computation time: {summary['total_time']:.2f}s")
    
    # Step 2: Generate tables
    print("\n" + "─" * 80)
    print("STEP 2: GENERATING TABLES")
    print("─" * 80)
    
    generate_tables(data)
    
    # Step 3: Export to CSV
    print("\n" + "─" * 80)
    print("STEP 3: EXPORTING TO CSV")
    print("─" * 80)
    
    export_to_csv(data, CSV_FILENAME)
    
    # Step 4: Create plots
    print("\n" + "─" * 80)
    print("STEP 4: CREATING VISUALIZATION PLOTS")
    print("─" * 80)
    
    try:
        create_plots(data, PLOT_PREFIX)
    except Exception as e:
        print(f"\n Warning: Could not create plots: {e}")
        print(" (This may happen if matplotlib is not properly configured)")
    
    # Step 5: Analyze patterns
    print("\n" + "─" * 80)
    print("STEP 5: PATTERN ANALYSIS")
    print("─" * 80)
    
    identify_patterns(data)
    
    # Step 6: Generate conjectures
    print("\n" + "─" * 80)
    print("STEP 6: GENERATING CONJECTURES")
    print("─" * 80)
    
    generate_conjectures(data)
    
    # Final summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(" COMPUTATIONAL EXPLORATION COMPLETE")
    print("=" * 80)
    print(f"\n Total execution time: {total_time:.2f}s")
    print(f" Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n Output files:")
    print(f"   • Data: {CSV_FILENAME}")
    print(f"   • Plots: {PLOT_PREFIX}_vs_n.png")
    print(f"            {PLOT_PREFIX}_heatmap.png")
    print(f"            {PLOT_PREFIX}_distribution.png")
    print("\n" + "=" * 80)
    print("\n Next steps:")
    print("   1. Review the patterns and conjectures above")
    print("   2. Examine the plots for visual insights")
    print("   3. Use the CSV data for further analysis")
    print("   4. Attempt to prove the proposed conjectures")
    print("   5. Test conjectures on larger values of n if needed")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Program interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n ERROR: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


