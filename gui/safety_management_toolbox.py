"""GUI for interacting with the Safety Management toolbox."""

import tkinter as tk
from tkinter import ttk, simpledialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from gui import messagebox
from analysis.safety_management import SafetyManagementToolbox as SMT


class SafetyManagementToolbox(ttk.Frame):
    """Tab widget exposing safety governance data and BPMN editing."""

    def __init__(self, master, toolbox: SMT | None = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.toolbox = toolbox or SMT()

        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(controls, text="Add Task", command=self._add_task).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(controls, text="Add Flow", command=self._add_flow).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(controls, text="Rebuild Default", command=self._rebuild).pack(
            side=tk.LEFT, padx=2
        )

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Start with a diagram built from current work products
        self.toolbox.build_default_diagram()
        self._refresh()

    def _refresh(self) -> None:
        self.ax.clear()
        g = self.toolbox.business_diagram.graph
        nodes = g.nodes()
        if nodes:
            pos = {n: (i, 0) for i, n in enumerate(nodes)}
            # Draw edges
            for u, v in g.edges():
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                self.ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                                 arrowprops=dict(arrowstyle="->"))
            # Draw nodes
            xs = [pos[n][0] for n in nodes]
            ys = [pos[n][1] for n in nodes]
            self.ax.scatter(xs, ys, s=300)
            for n, (x, y) in pos.items():
                self.ax.text(x, y, n, ha="center", va="center")
        self.ax.axis("off")
        self.canvas.draw()

    def _add_task(self) -> None:
        name = simpledialog.askstring("Task", "Task name:", parent=self)
        if name:
            self.toolbox.add_business_task(name)
            self._refresh()

    def _add_flow(self) -> None:
        src = simpledialog.askstring("Flow", "Source task:", parent=self)
        dst = simpledialog.askstring("Flow", "Destination task:", parent=self)
        if src and dst:
            try:
                self.toolbox.add_business_flow(src, dst)
            except ValueError as exc:
                messagebox.showerror("Flow", str(exc))
            self._refresh()

    def _rebuild(self) -> None:
        self.toolbox.build_default_diagram()
        self._refresh()
