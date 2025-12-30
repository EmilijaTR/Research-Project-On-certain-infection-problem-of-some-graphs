import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np
import math
import random

# --- Backend Logic (Graph & Infection) ---

class CayleyGraph:
    """Represents a quartic circulant graph C_n(3,a)."""
    def __init__(self, n: int, a: int):
        self.n = n
        self.a = a % n
        self.vertices = list(range(n))
        
        # Validation
        if self.n < 4:
            raise ValueError("n must be at least 4")
        
        # Check connectivity: gcd(3, a, n) must be 1
        g = math.gcd(3, self.a)
        g = math.gcd(g, self.n)
        if g != 1:
             raise ValueError(f"Graph is not connected! gcd(3, {self.a}, {self.n}) = {g} != 1")

        # Check for 4-regularity conditions
        if self.a == 0:
            raise ValueError("a cannot be 0")
        if self.a == 3 or self.a == (self.n - 3) % self.n:
            raise ValueError(f"a cannot be ±3 (mod {self.n})")
        if (2 * self.a) % self.n == 0:
            raise ValueError(f"a cannot be n/2 (results in degree 3)")
        if (2 * 3) % self.n == 0: # n=6 case where 3 == -3
            raise ValueError(f"n=6 is invalid for step 3 (results in degree 3)")

        self.adjacency = self._build_adjacency_list()

    def _build_adjacency_list(self):
        adj = {i: set() for i in self.vertices}
        for i in self.vertices:
            neighbors = {
                (i + 3) % self.n,
                (i - 3) % self.n,
                (i + self.a) % self.n,
                (i - self.a) % self.n
            }
            # Remove self-loops if any (though unlikely with valid parameters)
            if i in neighbors:
                neighbors.remove(i)
            adj[i] = neighbors
        return adj

    def get_neighbors(self, u):
        return self.adjacency[u]

class InfectionModel:
    """Manages the state of the infection simulation."""
    def __init__(self, graph: CayleyGraph):
        self.graph = graph
        self.infected = set()
        self.round_history = []
        self.round = 0
        self.is_complete = False

    def reset(self):
        self.infected = set()
        self.round_history = []
        self.round = 0
        self.is_complete = False

    def set_initial_infected(self, nodes):
        self.infected = set(nodes)
        self.round_history = [self.infected.copy()]
        self.round = 0
        self.is_complete = False

    def step(self):
        if self.is_complete:
            return False

        new_infected = set()
        healthy_nodes = [v for v in self.graph.vertices if v not in self.infected]
        
        for v in healthy_nodes:
            neighbors = self.graph.get_neighbors(v)
            infected_neighbors = sum(1 for nb in neighbors if nb in self.infected)
            if infected_neighbors >= 2:
                new_infected.add(v)
        
        if not new_infected:
            self.is_complete = True
            return False
        
        self.infected.update(new_infected)
        self.round_history.append(self.infected.copy())
        self.round += 1
        
        # Check if all nodes are infected
        if len(self.infected) == self.graph.n:
            self.is_complete = True
            
        return True

# --- Frontend (GUI) ---

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cayley Graph Infection Simulator")
        self.root.geometry("1200x800")

        self.graph_model = None
        self.infection_model = None
        self.pos = None # Node positions for layout
        self.is_playing = False
        self.animation_job = None

        # -- UI Layout --
        
        # Left Panel: Controls
        self.control_panel = ttk.Frame(self.root, padding="10")
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y)

        # Graph Generation Section
        ttk.Label(self.control_panel, text="Graph Parameters", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        input_frame = ttk.Frame(self.control_panel)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="n (Vertices):").grid(row=0, column=0, sticky=tk.W)
        self.entry_n = ttk.Entry(input_frame, width=10)
        self.entry_n.insert(0, "20")
        self.entry_n.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="a (Step):").grid(row=1, column=0, sticky=tk.W)
        self.entry_a = ttk.Entry(input_frame, width=10)
        self.entry_a.insert(0, "4")
        self.entry_a.grid(row=1, column=1, padx=5)
        
        self.btn_generate = ttk.Button(self.control_panel, text="Generate Graph", command=self.generate_graph)
        self.btn_generate.pack(fill=tk.X, pady=10)

        # Infection Setup Section
        ttk.Separator(self.control_panel, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(self.control_panel, text="Infection Setup", font=("Arial", 12, "bold")).pack(pady=(0, 5))

        self.selection_mode = tk.StringVar(value="manual")
        
        ttk.Radiobutton(self.control_panel, text="Manual Selection (Click Nodes)", 
                        variable=self.selection_mode, value="manual").pack(anchor=tk.W)
        
        ttk.Radiobutton(self.control_panel, text="Random Set", 
                        variable=self.selection_mode, value="random").pack(anchor=tk.W)
        
        rand_frame = ttk.Frame(self.control_panel)
        rand_frame.pack(fill=tk.X, padx=20)
        ttk.Label(rand_frame, text="Count:").pack(side=tk.LEFT)
        self.entry_k = ttk.Entry(rand_frame, width=5)
        self.entry_k.insert(0, "2")
        self.entry_k.pack(side=tk.LEFT, padx=5)
        self.btn_randomize = ttk.Button(rand_frame, text="Apply", command=self.apply_random)
        self.btn_randomize.pack(side=tk.LEFT)

        self.btn_clear_selection = ttk.Button(self.control_panel, text="Clear Selection", command=self.clear_selection)
        self.btn_clear_selection.pack(fill=tk.X, pady=5)

        # Simulation Controls
        ttk.Separator(self.control_panel, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(self.control_panel, text="Simulation", font=("Arial", 12, "bold")).pack(pady=(0, 5))

        self.btn_start = ttk.Button(self.control_panel, text="Start / Reset", command=self.toggle_simulation_mode)
        self.btn_start.pack(fill=tk.X, pady=5)

        self.sim_controls_frame = ttk.Frame(self.control_panel)
        self.sim_controls_frame.pack(fill=tk.X)
        
        self.btn_step = ttk.Button(self.sim_controls_frame, text="Step >", command=self.step_simulation, state=tk.DISABLED)
        self.btn_step.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.btn_play = ttk.Button(self.sim_controls_frame, text="Play >>", command=self.play_simulation, state=tk.DISABLED)
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.btn_pause = ttk.Button(self.sim_controls_frame, text="Pause ||", command=self.pause_simulation, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Stats
        self.lbl_status = ttk.Label(self.control_panel, text="Status: Ready", wraplength=180)
        self.lbl_status.pack(pady=20)
        
        self.lbl_stats = ttk.Label(self.control_panel, text="Round: 0\nInfected: 0/0")
        self.lbl_stats.pack(pady=5)

        # Right Panel: Plot
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Connect click event
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Initial State
        self.currently_selected = set()
        self.simulation_active = False # True if simulation has started (locked editing)
        
        # Generate initial default graph
        self.generate_graph()

    def generate_graph(self):
        try:
            n = int(self.entry_n.get())
            a = int(self.entry_a.get())
            
            self.graph_model = CayleyGraph(n, a)
            self.infection_model = InfectionModel(self.graph_model)
            
            # Setup visualization layout (Circular)
            self.pos = {}
            for i in range(n):
                angle = 2 * math.pi * i / n + math.pi/2 # Start from top
                self.pos[i] = (math.cos(angle), math.sin(angle))
            
            self.reset_ui_state()
            self.draw_graph()
            self.update_status(f"Generated C_{n}(3, {a})")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def reset_ui_state(self):
        self.pause_simulation()
        self.currently_selected = set()
        self.simulation_active = False
        self.infection_model.reset()
        
        self.btn_start.config(text="Start Simulation")
        self.btn_step.config(state=tk.DISABLED)
        self.btn_play.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_randomize.config(state=tk.NORMAL)
        self.btn_clear_selection.config(state=tk.NORMAL)
        self.update_stats()

    def draw_graph(self):
        self.ax.clear()
        if not self.graph_model:
            return

        n = self.graph_model.n
        a = self.graph_model.a
        
        # Draw edges
        # We draw edges manually to control style
        for u in range(n):
            neighbors = self.graph_model.get_neighbors(u)
            for v in neighbors:
                if u > v: continue # Draw each edge once
                
                # Check edge type
                diff = abs(u - v)
                is_step_3 = (diff == 3) or (diff == n - 3)
                is_step_a = (diff == a) or (diff == n - a)
                
                if is_step_3:
                    self.ax.plot([self.pos[u][0], self.pos[v][0]], 
                                 [self.pos[u][1], self.pos[v][1]], 
                                 'k-', alpha=0.3, linewidth=1)
                elif is_step_a:
                    self.ax.plot([self.pos[u][0], self.pos[v][0]], 
                                 [self.pos[u][1], self.pos[v][1]], 
                                 'b-', alpha=0.3, linewidth=1.5)

        # Draw nodes
        node_colors = []
        node_sizes = []
        
        # Determine colors
        # If simulation active, use model state. If not, use manual selection.
        if self.simulation_active:
            infected_set = self.infection_model.infected
            # Identify newly infected in last round
            last_round_new = set()
            if self.infection_model.round > 0 and self.infection_model.round_history:
                last_round_new = self.infection_model.round_history[-1] - self.infection_model.round_history[-2] if len(self.infection_model.round_history) > 1 else self.infection_model.round_history[0]
            elif self.infection_model.round == 0 and self.infection_model.round_history:
                 last_round_new = self.infection_model.round_history[0]

            for i in range(n):
                if i in last_round_new:
                    node_colors.append('yellow') # Newly infected
                elif i in infected_set:
                    node_colors.append('red') # Infected
                else:
                    node_colors.append('white') # Healthy
        else:
            # Editing mode
            for i in range(n):
                if i in self.currently_selected:
                    node_colors.append('red')
                else:
                    node_colors.append('white')
        
        # Draw scatter
        x_vals = [self.pos[i][0] for i in range(n)]
        y_vals = [self.pos[i][1] for i in range(n)]
        
        self.ax.scatter(x_vals, y_vals, c=node_colors, s=300, edgecolors='black', zorder=5)
        
        # Labels
        for i in range(n):
            self.ax.text(self.pos[i][0], self.pos[i][1], str(i), 
                         ha='center', va='center', fontweight='bold', fontsize=8, zorder=6)

        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.canvas.draw()

    def on_click(self, event):
        if self.simulation_active:
            return # No editing during simulation
            
        if event.inaxes != self.ax:
            return
            
        # Find closest node
        min_dist = float('inf')
        closest_node = None
        
        for i, (x, y) in self.pos.items():
            dist = (x - event.xdata)**2 + (y - event.ydata)**2
            if dist < min_dist:
                min_dist = dist
                closest_node = i
        
        # Threshold for clicking (0.1 squared)
        if min_dist < 0.04:
            if closest_node in self.currently_selected:
                self.currently_selected.remove(closest_node)
            else:
                self.currently_selected.add(closest_node)
            self.draw_graph()
            self.update_stats()

    def apply_random(self):
        if self.simulation_active: return
        try:
            k = int(self.entry_k.get())
            if k > self.graph_model.n:
                k = self.graph_model.n
            self.currently_selected = set(random.sample(range(self.graph_model.n), k))
            self.draw_graph()
            self.update_stats()
        except ValueError:
            pass

    def clear_selection(self):
        if self.simulation_active: return
        self.currently_selected = set()
        self.draw_graph()
        self.update_stats()

    def toggle_simulation_mode(self):
        if not self.simulation_active:
            # Start Simulation
            if not self.currently_selected:
                messagebox.showwarning("Warning", "Select at least one initial node.")
                return
                
            self.simulation_active = True
            self.infection_model.set_initial_infected(self.currently_selected)
            
            self.btn_start.config(text="Reset Simulation")
            self.btn_step.config(state=tk.NORMAL)
            self.btn_play.config(state=tk.NORMAL)
            self.btn_randomize.config(state=tk.DISABLED)
            self.btn_clear_selection.config(state=tk.DISABLED)
            
            self.update_status("Simulation Started. Press Step or Play.")
            self.draw_graph()
            self.update_stats()
        else:
            # Reset Simulation
            self.reset_ui_state()
            self.draw_graph()
            self.update_status("Simulation Reset. Modify selection or generate new graph.")

    def step_simulation(self):
        if not self.simulation_active: return
        
        changed = self.infection_model.step()
        self.draw_graph()
        self.update_stats()
        
        if not changed:
            self.pause_simulation()
            if self.infection_model.is_complete:
                if len(self.infection_model.infected) == self.graph_model.n:
                    self.update_status("Simulation Finished: All infected!")
                else:
                    self.update_status("Simulation Finished: Stalled.")
            else:
                self.update_status("Simulation Finished.")

    def play_simulation(self):
        if not self.simulation_active: return
        self.is_playing = True
        self.btn_play.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL)
        self.btn_step.config(state=tk.DISABLED)
        self.animate_step()

    def pause_simulation(self):
        self.is_playing = False
        if self.simulation_active:
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.DISABLED)
            self.btn_step.config(state=tk.NORMAL)
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def animate_step(self):
        if self.is_playing:
            changed = self.infection_model.step()
            self.draw_graph()
            self.update_stats()
            
            if changed:
                self.animation_job = self.root.after(800, self.animate_step) # 800ms delay
            else:
                self.pause_simulation()
                if len(self.infection_model.infected) == self.graph_model.n:
                    self.update_status("Simulation Finished: All infected!")
                else:
                    self.update_status("Simulation Finished: Stalled.")

    def update_stats(self):
        total = self.graph_model.n if self.graph_model else 0
        if self.simulation_active:
            count = len(self.infection_model.infected)
            round_num = self.infection_model.round
        else:
            count = len(self.currently_selected)
            round_num = 0
            
        self.lbl_stats.config(text=f"Round: {round_num}\nInfected: {count}/{total}")

    def update_status(self, msg):
        self.lbl_status.config(text=f"Status: {msg}")

if __name__ == "__main__":
    root = tk.Tk()
    # Set icon if available, otherwise ignore
    # root.iconbitmap('icon.ico') 
    app = GraphApp(root)
    root.mainloop()

