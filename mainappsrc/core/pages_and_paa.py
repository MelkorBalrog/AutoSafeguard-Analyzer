# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

"""Helpers for page diagrams and Prototype Assurance activities."""


import tkinter as tk
from gui.styles.style_manager import StyleManager
from gui.utils.drawing_helper import fta_drawing_helper, draw_90_connection

from .page_diagram import PageDiagram, GATE_NODE_TYPES


class Pages_and_PAA:
    """Encapsulate page-diagram rendering and PAA helpers.

    The class delegates attribute access to the main application so existing
    code can continue to call these helpers via the app instance.
    """

    def __init__(self, app) -> None:
        self.app = app

    def __getattr__(self, name):  # pragma: no cover - delegation helper
        return getattr(self.app, name)

    # ------------------------------------------------------------------
    # PAA helpers
    # ------------------------------------------------------------------
    def enable_paa_actions(self, enabled: bool) -> None:
        """Enable or disable PAA-related menu actions."""
        if hasattr(self, "paa_menu"):
            state = tk.NORMAL if enabled else tk.DISABLED
            for key in ("add_confidence", "add_robustness"):
                self.paa_menu.entryconfig(self._paa_menu_indices[key], state=state)

    def _create_paa_tab(self) -> None:
        """Delegate PAA tab creation to the manager."""
        self.paa_manager._create_paa_tab()

    def create_paa_diagram(self) -> None:
        """Delegate PAA diagram setup to the manager."""
        self.paa_manager.create_paa_diagram()

    # ------------------------------------------------------------------
    # Page diagram helpers
    # ------------------------------------------------------------------
    def draw_page_subtree(self, page_root):
        self.page_canvas.delete("all")
        self.draw_page_grid()
        visited_ids = set()
        self.draw_page_connections_subtree(page_root, visited_ids)
        self.draw_page_nodes_subtree(page_root)
        bbox = self.page_canvas.bbox("all")
        if bbox:
            self.page_canvas.config(scrollregion=bbox)

    def draw_page_grid(self):
        spacing = 20
        width = self.page_canvas.winfo_width() or 800
        height = self.page_canvas.winfo_height() or 600
        for x in range(0, width, spacing):
            self.page_canvas.create_line(x, 0, x, height, fill="#ddd", tags="grid")
        for y in range(0, height, spacing):
            self.page_canvas.create_line(0, y, width, y, fill="#ddd", tags="grid")

    def draw_page_connections_subtree(self, node, visited_ids):
        if id(node) in visited_ids:
            return
        visited_ids.add(id(node))
        region_width = 100
        parent_bottom = (node.x, node.y + 40)
        N = len(node.children)
        for i, child in enumerate(node.children):
            parent_conn = (
                node.x - region_width / 2 + (i + 0.5) * (region_width / N),
                parent_bottom[1],
            )
            child_top = (child.x, child.y - 45)
            draw_90_connection(
                self.page_canvas,
                parent_conn,
                child_top,
                outline_color="dimgray",
                line_width=1,
            )
        for child in node.children:
            self.draw_page_connections_subtree(child, visited_ids)

    def draw_page_nodes_subtree(self, node):
        self.draw_node_on_page_canvas(node)
        for child in node.children:
            self.draw_page_nodes_subtree(child)

    def draw_node_on_page_canvas(self, node):
        canvas = self.page_canvas
        fill_color = self.get_node_fill_color(node, getattr(canvas, "diagram_mode", None))
        eff_x, eff_y = node.x, node.y
        top_text = f"Type: {node.node_type}"
        if node.input_subtype:
            top_text += f" ({node.input_subtype})"
        if node.description:
            top_text += f"\nDesc: {node.description}"
        if node.rationale:
            top_text += f"\nRationale: {node.rationale}"
        bottom_text = node.name

        outline_color = "dimgray"
        line_width = 1
        if node.unique_id in getattr(self.app, "diff_nodes", []):
            outline_color = "blue"
            line_width = 2
        elif not node.is_primary_instance:
            outline_color = "red"

        if node.is_page:
            fta_drawing_helper.draw_triangle_shape(
                canvas,
                eff_x,
                eff_y,
                scale=40,
                top_text=top_text,
                bottom_text=bottom_text,
                fill=fill_color,
                outline_color=outline_color,
                line_width=line_width,
                font_obj=self.diagram_font,
                obj_id=node.unique_id,
            )
        else:
            self._draw_non_page_node(
                canvas,
                node,
                eff_x,
                eff_y,
                top_text,
                bottom_text,
                fill_color,
                outline_color,
                line_width,
            )

        if self.review_data:
            self._draw_review_marker(canvas, eff_x, eff_y, node)

    def _draw_non_page_node(
        self,
        canvas,
        node,
        eff_x,
        eff_y,
        top_text,
        bottom_text,
        fill_color,
        outline_color,
        line_width,
    ):
        node_type_upper = node.node_type.upper()
        if node_type_upper in GATE_NODE_TYPES:
            drawer = (
                fta_drawing_helper.draw_rotated_or_gate_shape
                if node.gate_type and node.gate_type.upper() == "OR"
                else fta_drawing_helper.draw_rotated_and_gate_shape
            )
            drawer(
                canvas,
                eff_x,
                eff_y,
                scale=40,
                top_text=top_text,
                bottom_text=bottom_text,
                fill=fill_color,
                outline_color=outline_color,
                line_width=line_width,
                obj_id=node.unique_id,
            )
        else:
            fta_drawing_helper.draw_circle_event_shape(
                canvas,
                eff_x,
                eff_y,
                45,
                top_text=top_text,
                bottom_text=bottom_text,
                fill=fill_color,
                outline_color=outline_color,
                line_width=line_width,
                obj_id=node.unique_id,
            )

    def _draw_review_marker(self, canvas, eff_x, eff_y, node):
        unresolved = any(
            c.node_id == node.unique_id and not c.resolved for c in self.review_data.comments
        )
        if unresolved:
            canvas.create_oval(
                eff_x + 35,
                eff_y + 35,
                eff_x + 45,
                eff_y + 45,
                fill="yellow",
                outline=StyleManager.get_instance().outline_color,
            )

    def capture_page_diagram(self, page_node):
        """Return a PIL Image of the given page diagram."""
        from io import BytesIO
        from PIL import Image

        temp = tk.Toplevel(self.root)
        temp.withdraw()
        canvas = tk.Canvas(
            temp, bg=StyleManager.get_instance().canvas_bg, width=2000, height=2000
        )
        canvas.pack()

        pd = PageDiagram(self, page_node, canvas)
        pd.redraw_canvas()

        canvas.delete("grid")
        canvas.update()
        bbox = canvas.bbox("all")
        if not bbox:
            temp.destroy()
            return None

        x, y, x2, y2 = bbox
        width, height = x2 - x, y2 - y

        ps = canvas.postscript(colormode="color", x=x, y=y, width=width, height=height)
        ps_bytes = BytesIO(ps.encode("utf-8"))

        try:
            img = Image.open(ps_bytes)
            img.load(scale=3)
        except Exception:
            img = None
        temp.destroy()
        return img.convert("RGB") if img else None
