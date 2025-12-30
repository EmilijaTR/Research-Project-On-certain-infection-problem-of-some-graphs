import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
output_dir = "analysis_results"

print("Loading data...")
df = pd.read_csv("timed_exploration_10min_extended.csv")

# --- Define Regimes based on Conjecture ---

def classify_graph(row):
    n = row['n']
    a = row['a']
    
    # Check for Hard Regime: n approx 3a
    # We use a small tolerance
    ratio = n / a if a != 0 else 0
    if 2.9 <= ratio <= 3.1:
        return "Hard Regime (n ≈ 3a)"
    
    # Check for Modulo 3 behavior
    if a % 3 == 0:
        return "Modulo 3 Case (a % 3 == 0)"
    
    return "Standard Case (a % 3 != 0)"

df['Regime'] = df.apply(classify_graph, axis=1)

# --- Plot 1: The Hard Regime (Linear Scaling) ---
print("Generating Plot 1: Hard Regime Scaling...")
plt.figure(figsize=(10, 6))
hard_regime = df[df['Regime'] == "Hard Regime (n ≈ 3a)"]

# Plot points
plt.scatter(hard_regime['n'], hard_regime['m2'], color='#d62728', alpha=0.6, label='Data Points')

# Add trend line
if not hard_regime.empty:
    z = np.polyfit(hard_regime['n'], hard_regime['m2'], 1)
    p = np.poly1d(z)
    plt.plot(hard_regime['n'], p(hard_regime['n']), "k--", alpha=0.8, 
             label=f'Trend: $m_2 \\approx {z[0]:.2f}n {z[1]:+.2f}$')

plt.xlabel('Number of Vertices ($n$)')
plt.ylabel('Infection Number ($m_2$)')
plt.title('Evidence for Linear Scaling in the "Hard" Regime ($n \\approx 3a$)')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "conjecture_hard_regime_linear.png"), dpi=300)


# --- Plot 2: Modulo 3 Effect (Boxplot) ---
print("Generating Plot 2: Modulo 3 Effect...")
plt.figure(figsize=(10, 6))

# Filter out the hard regime to focus on the constant behavior difference
easy_regimes = df[df['Regime'] != "Hard Regime (n ≈ 3a)"]

sns.boxplot(data=easy_regimes, x='Regime', y='m2', palette=['#1f77b4', '#2ca02c'])
plt.title('Impact of Step Size Divisibility by 3 on Infection Number')
plt.ylabel('Infection Number ($m_2$)')
plt.xlabel('Graph Class')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "conjecture_modulo_3_effect.png"), dpi=300)


# --- Plot 3: The Big Picture (Classified Scatter) ---
print("Generating Plot 3: Classified Scatter...")
plt.figure(figsize=(12, 8))

# Define colors
colors = {
    "Standard Case (a % 3 != 0)": '#1f77b4', # Blue
    "Modulo 3 Case (a % 3 == 0)": '#2ca02c', # Green
    "Hard Regime (n ≈ 3a)": '#d62728'        # Red
}

for regime, color in colors.items():
    subset = df[df['Regime'] == regime]
    plt.scatter(subset['n'], subset['m2'], c=color, label=regime, alpha=0.6, s=15)

plt.xlabel('Number of Vertices ($n$)')
plt.ylabel('Infection Number ($m_2$)')
plt.title('Global Classification of Infection Behavior')
plt.legend(title='Conjectured Regime')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "conjecture_global_classification.png"), dpi=300)

print("Plots generated successfully.")



