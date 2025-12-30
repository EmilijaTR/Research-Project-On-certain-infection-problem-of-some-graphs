# Research Outputs: Infection Numbers in Quartic Circulant Graphs C_n(3,a)

This folder contains all computational results and visualizations from the infection number analysis.

## Folder Structure

### 01_data/
CSV data files with computed infection numbers for all tested graphs.
- `infection_data_n5_to_10.csv` - Complete results for n ∈ [5, 10]

### 02_summary_plots/
High-level analysis and summary visualizations.
- `all_graphs_summary.png` - Overview of all 22 graphs with n ≤ 10
- `infection_vs_n.png` - Scatter plot of m_2 vs n
- `infection_heatmap.png` - Heatmap of infection numbers
- `infection_distribution.png` - Distribution histogram

### 03_individual_graphs/
Detailed infection process for each graph with n ∈ [5, 10] (22 files).
Each shows the step-by-step spreading from the initial infection set.
- All these graphs have m_2 = 2

### 04_m2_equals_3_examples/
Examples of graphs requiring 3 initial vertices (n ≥ 12).
Shows infection processes for graphs where m_2 = 3.
- Demonstrates the transition point at n = 12

### 05_failed_infections/
Critical evidence: Failed infection attempts with only 2 vertices.
- `failed_infection_*.png` - Side-by-side comparison of success vs failure
- `detailed_failure_*.png` - Step-by-step process showing why 2 vertices fail

### 06_comparison/
Direct comparisons between different graph types.
- `comparison_m2_2_vs_3.png` - Visual comparison of graphs with m_2 = 2 vs m_2 = 3

## Key Findings

1. **n ≤ 11**: All graphs have m_2 = 2
2. **n = 12**: First appearance of m_2 = 3
3. **n ≥ 12**: Mix of m_2 = 2 and m_2 = 3
4. For graphs with m_2 = 3, **all** 2-vertex pairs fail (100% failure rate)

## Generated
December 11, 2025
