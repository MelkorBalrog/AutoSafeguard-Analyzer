"""Simple canvas window with toolbox for editing GSN diagrams."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from gsn import GSNNode, GSNDiagram


class GSNDiagramWindow(tk.Frame):
    """Display a :class:`GSNDiagram` inside a notebook tab with basic tools."""

    TOOLBOX_BUTTONS = [
        "Goal",
        "Strategy",
        "Solution",
        "Assumption",
        "Justification",
        "Context",
        "Solved By",
        "In Context Of",
    ]

    def __init__(self, master, app, diagram: GSNDiagram):
        super().__init__(master)
        self.app = app
        self.diagram = diagram

        # toolbox with buttons to add nodes and connectors
        self.toolbox = ttk.Frame(self)
        self.toolbox.pack(side=tk.TOP, fill=tk.X)
        btn_cmds = [
            ("Goal", self.add_goal),
            ("Strategy", self.add_strategy),
            ("Solution", self.add_solution),
            ("Assumption", self.add_assumption),
            ("Justification", self.add_justification),
            ("Context", self.add_context),
            ("Solved By", self.connect_solved_by),
            ("In Context Of", self.connect_in_context),
        ]
        for name, cmd in btn_cmds:
            ttk.Button(self.toolbox, text=name, command=cmd).pack(side=tk.LEFT)

        # drawing canvas
        self.canvas = tk.Canvas(self, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.pack(fill=tk.BOTH, expand=True)

        self._pending_parent: Optional[GSNNode] = None
        self.refresh()

    # ------------------------------------------------------------------
    def refresh(self):  # pragma: no cover - requires tkinter
        self.canvas.delete("all")
        self.diagram.draw(self.canvas)

    # The following methods simply extend the diagram with new nodes.
    # Placement is very rudimentary but sufficient for tests.
    def _add_node(self, node_type: str):  # pragma: no cover - requires tkinter
        node = GSNNode(node_type, node_type, x=50, y=50)
        self.diagram.root.add_child(node)
        self.refresh()

    def add_goal(self):  # pragma: no cover - requires tkinter
        self._add_node("Goal")

    def add_strategy(self):  # pragma: no cover - requires tkinter
        self._add_node("Strategy")

    def add_solution(self):  # pragma: no cover - requires tkinter
        self._add_node("Solution")

    def add_assumption(self):  # pragma: no cover - requires tkinter
        self._add_node("Assumption")

    def add_justification(self):  # pragma: no cover - requires tkinter
        self._add_node("Justification")

    def add_context(self):  # pragma: no cover - requires tkinter
        self._add_node("Context")

    def connect_solved_by(self):  # pragma: no cover - GUI interaction stub
        pass

    def connect_in_context(self):  # pragma: no cover - GUI interaction stub
        pass
