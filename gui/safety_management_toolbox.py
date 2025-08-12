"""GUI for interacting with the Safety Management toolbox."""

import tkinter as tk
from tkinter import ttk, simpledialog

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

        # Canvas used to render a lightweight BPMN diagram without matplotlib
        self.canvas = tk.Canvas(self, width=500, height=400, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Start with a diagram built from current work products
        self.toolbox.build_default_diagram()
        self._refresh()

    def _refresh(self) -> None:
        """Redraw the BPMN diagram on the canvas."""
        self.canvas.delete("all")
        g = self.toolbox.business_diagram.graph
        nodes = list(g.nodes())
        if not nodes:
            return

        # Simple horizontal layout
        pos = {n: (50 + i * 100, 100) for i, n in enumerate(nodes)}

        # Draw flows
        for u, v in g.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)

        # Draw tasks
        radius = 20
        for name, (x, y) in pos.items():
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="lightgray",
            )
            self.canvas.create_text(x, y, text=name)

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
