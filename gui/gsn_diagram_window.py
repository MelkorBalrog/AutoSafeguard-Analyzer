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
        "Zoom In",
        "Zoom Out",
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
            ("Zoom In", self.zoom_in),
            ("Zoom Out", self.zoom_out),
        ]
        for name, cmd in btn_cmds:
            ttk.Button(self.toolbox, text=name, command=cmd).pack(side=tk.LEFT)

        # drawing canvas
        self.canvas = tk.Canvas(self, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.pack(fill=tk.BOTH, expand=True)

        self.id_to_node = {}
        self.selected_node: Optional[GSNNode] = None
        self._drag_node: Optional[GSNNode] = None
        self._drag_offset = (0, 0)
        self._connect_mode: Optional[str] = None
        self._connect_parent: Optional[GSNNode] = None
        self.zoom = 1.0
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.refresh()

    # ------------------------------------------------------------------
    def refresh(self):  # pragma: no cover - requires tkinter
        self.canvas.delete("all")
        self.id_to_node = {n.unique_id: n for n in self.diagram._traverse()}
        self.diagram.draw(self.canvas, zoom=self.zoom)
        if self.selected_node:
            bbox = self.canvas.bbox(self.selected_node.unique_id)
            if bbox:
                self.canvas.create_rectangle(*bbox, outline="red", width=2)

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
        self._connect_mode = "solved"
        self._connect_parent = None

    def connect_in_context(self):  # pragma: no cover - GUI interaction stub
        self._connect_mode = "context"
        self._connect_parent = None

    def _on_click(self, event):  # pragma: no cover - requires tkinter
        node = self._node_at(event.x, event.y)
        if not node:
            self.selected_node = None
            self.refresh()
            return
        if self._connect_mode:
            if self._connect_parent is None:
                self._connect_parent = node
            else:
                self._connect_parent.add_child(node)
                self._connect_mode = None
                self._connect_parent = None
            self.refresh()
            return
        self.selected_node = node
        self._drag_node = node
        sx, sy = node.x * self.zoom, node.y * self.zoom
        self._drag_offset = (event.x - sx, event.y - sy)
        self.refresh()

    def _on_drag(self, event):  # pragma: no cover - requires tkinter
        if not self._drag_node:
            return
        nx = (event.x - self._drag_offset[0]) / self.zoom
        ny = (event.y - self._drag_offset[1]) / self.zoom
        self._drag_node.x = nx
        self._drag_node.y = ny
        self.refresh()

    def _on_release(self, _event):  # pragma: no cover - requires tkinter
        self._drag_node = None

    def _node_at(self, x: float, y: float) -> Optional[GSNNode]:
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in items:
            for tag in self.canvas.gettags(item):
                node = self.id_to_node.get(tag)
                if node:
                    return node
        return None

    def zoom_in(self):  # pragma: no cover - GUI interaction stub
        self.zoom *= 1.2
        self.refresh()

    def zoom_out(self):  # pragma: no cover - GUI interaction stub
        self.zoom /= 1.2
        self.refresh()