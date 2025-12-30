# Interactive Infection Simulation for Quartic Circulant Graphs

This application allows you to explore the infection process on $C_n(3, a)$ graphs interactively.

## Features
- **Graph Generation**: Create $C_n(3, a)$ graphs by specifying $n$ and $a$.
- **Interactive Selection**: Click on nodes to toggle their initial infection status, or select a random set of $k$ nodes.
- **Simulation**: Watch the infection spread step-by-step or play it as an animation.
- **Visualization**: Clear color coding (White: Healthy, Red: Infected, Yellow: Newly Infected in the current round).

## Requirements
- Python 3.x
- `tkinter` (usually included with Python)
- `matplotlib`
- `networkx`
- `numpy`

## How to Run
Run the script directly from the terminal:
```bash
python interactive_graph_app.py
```

## Usage
1. **Generate Graph**: Enter values for $n$ (vertices) and $a$ (step size) and click "Generate Graph". Note that $a$ must satisfy $\gcd(3, a, n) = 1$.
2. **Select Initial Nodes**:
   - **Manual**: Click on nodes in the graph to select/deselect them.
   - **Random**: Enter a number $k$ and click "Apply" to select $k$ random nodes.
3. **Run Simulation**:
   - Click "Start Simulation" to lock the selection and enable controls.
   - Use "Step >" to advance one round at a time.
   - Use "Play >>" to animate the process.
   - Use "Pause ||" to stop the animation.
4. **Reset**: Click "Reset Simulation" to clear the progress and modify the initial set or graph parameters.



