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

"""Page diagram rendering and interaction utilities."""


from pathlib import Path
import tkinter as tk
import tkinter.font as tkFont

from config import load_diagram_rules
from gui.utils.drawing_helper import fta_drawing_helper

# Node types treated as gates when rendering and editing
_CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "rules"
    / "diagram_rules.json"
)
_CONFIG = load_diagram_rules(_CONFIG_PATH)
GATE_NODE_TYPES = set(_CONFIG.get("gate_node_types", []))


class PageDiagram:
    def __init__(self, app, page_gate_node, canvas):
        self.app = app
        self.root_node = page_gate_node
        self.canvas = canvas
        self.diagram_mode = getattr(canvas, "diagram_mode", "FTA")
        self.zoom = 1.0
        self.diagram_font = tkFont.Font(family="Arial", size=int(8 * self.zoom))
        self.grid_size = 20
        self.selected_node = None
        self.dragging_node = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.rc_dragged = False
        # Reference project properties for grid and color options
        self.project_properties = app.project_properties

        # Bind events – including right-click release
        self.canvas.bind("<ButtonPress-3>", self.on_right_mouse_press)
        self.canvas.bind("<B3-Motion>", self.on_right_mouse_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_mouse_release)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Double-1>", self.on_canvas_double_click)
        self.canvas.bind("<Control-MouseWheel>", self.on_ctrl_mousewheel)

    def on_right_mouse_press(self, event):
        self.rc_dragged = False
        self.canvas.scan_mark(event.x, event.y)

    def on_right_mouse_drag(self, event):
        self.rc_dragged = True
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_right_mouse_release(self, event):
        # If there was no significant drag, show the context menu. Guard with
        # ``getattr`` so missing attributes (e.g. if the press event was
        # swallowed) do not raise errors, and always reset the flag.
        if not getattr(self, "rc_dragged", False):
            self.show_context_menu(event)
        self.rc_dragged = False

    def find_node_at_position(self, x, y):
        # Adjust the radius (here using 45 as an example)
        radius_sq = (45 * self.zoom) ** 2
        for n in self.get_all_nodes(self.root_node):
            if (x - n.x) ** 2 + (y - n.y) ** 2 < radius_sq:
                return n
        return None

    def on_ctrl_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def get_all_nodes(self, node=None):
        if node is None:
            node = self.root_node
        visited = set()

        def rec(n):
            if n.unique_id in visited:
                return []
            visited.add(n.unique_id)

            # Skip nodes if a parent is page, but that page is NOT our root_node
            if n != self.root_node and any(p.is_page and p != self.root_node for p in n.parents):
                return []

            result = [n]
            for c in n.children:
                result.extend(rec(c))
            return result

        return rec(node)

    def rc_on_press(self, event):
        self.rc_start = (event.x, event.y)
        self.rc_dragged = False
        self.canvas.scan_mark(event.x, event.y)

    def rc_on_motion(self, event):
        self.rc_dragged = True
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def rc_on_release(self, event):
        if not self.rc_dragged:
            self.show_context_menu(event)

    def show_context_menu(self, event):
        x = self.canvas.canvasx(event.x) / self.zoom
        y = self.canvas.canvasy(event.y) / self.zoom
        node = None
        for n in self.get_all_nodes(self.root_node):
            radius = 60 if n.node_type.upper() in GATE_NODE_TYPES else 45
            if (x - n.x) ** 2 + (y - n.y) ** 2 < radius ** 2:
                node = n
                break
        if not node:
            return
        self.selected_node = node
        self.app.selected_node = node
        menu = tk.Menu(self.app.root, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self.context_edit(node))
        menu.add_command(label="Remove Connection", command=lambda: self.context_remove(node))
        menu.add_command(label="Delete Node", command=lambda: self.context_delete(node))
        menu.add_command(label="Copy", command=lambda: self.context_copy(node))
        menu.add_command(label="Cut", command=lambda: self.context_cut(node))
        menu.add_command(label="Paste", command=lambda: self.context_paste(node))
        if node.node_type.upper() not in ["TOP EVENT", "BASIC EVENT"]:
            menu.add_command(label="Edit Page Flag", command=lambda: self.context_edit_page_flag(node))
        menu.add_separator()
        if self.diagram_mode == "PAA":
            menu.add_command(label="Add Confidence", command=lambda: self.context_add("Confidence Level"))
            menu.add_command(label="Add Robustness", command=lambda: self.context_add("Robustness Score"))
        elif self.diagram_mode == "CTA":
            menu.add_command(label="Add Triggering Condition", command=lambda: self.context_add("Triggering Condition"))
            menu.add_command(label="Add Functional Insufficiency", command=lambda: self.context_add("Functional Insufficiency"))
        else:
            menu.add_command(label="Add Gate", command=lambda: self.context_add("GATE"))
            menu.add_command(label="Add Basic Event", command=lambda: self.context_add("Basic Event"))
            menu.add_command(label="Add Gate from Failure Mode", command=lambda: self.context_add_gate_from_failure_mode())
            menu.add_command(label="Add Fault Event", command=lambda: self.context_add_fault_event())
        menu.tk_popup(event.x_root, event.y_root)

    def context_edit(self, node):
        from gui.dialogs.edit_node_dialog import EditNodeDialog

        EditNodeDialog(self.canvas, node, self.app)
        self.redraw_canvas()
        self.app.update_views()

    def context_remove(self, node):
        self.selected_node = node
        self.app.remove_connection(node)
        self.redraw_canvas()
        self.app.update_views()

    def context_delete(self, node):
        self.selected_node = node
        self.app.delete_node_and_subtree(node)
        self.redraw_canvas()
        self.app.update_views()

    def context_copy(self, node):
        self.selected_node = node
        self.app.copy_node()

    def context_cut(self, node):
        self.selected_node = node
        self.app.cut_node()

    def context_paste(self, node):
        self.selected_node = node
        self.app.paste_node()

    def context_edit_page_flag(self, node):
        self.selected_node = node
        self.app.edit_page_flag()
        self.redraw_canvas()

    def context_add(self, event_type):
        self.app.selected_node = self.selected_node
        self.app.add_node_of_type(event_type)
        self.redraw_canvas()
        self.app.update_views()

    def context_add_gate_from_failure_mode(self):
        self.app.selected_node = self.selected_node
        self.app.add_gate_from_failure_mode()
        self.redraw_canvas()
        self.app.update_views()

    def context_add_fault_event(self):
        self.app.selected_node = self.selected_node
        self.app.add_fault_event()
        self.redraw_canvas()
        self.app.update_views()

    def on_canvas_click(self, event):
        x = self.canvas.canvasx(event.x) / self.zoom
        y = self.canvas.canvasy(event.y) / self.zoom
        clicked_node = None
        for n in self.get_all_nodes(self.root_node):
            radius = 60 if n.node_type.upper() in GATE_NODE_TYPES else 45
            if (x - n.x) ** 2 + (y - n.y) ** 2 < radius ** 2:
                clicked_node = n
                break
        self.selected_node = clicked_node
        self.app.selected_node = clicked_node
        if clicked_node and clicked_node is not self.root_node:
            self.app.push_undo_state()
            self.dragging_node = clicked_node
            self.drag_offset_x = x - clicked_node.x
            self.drag_offset_y = y - clicked_node.y
        else:
            self.dragging_node = None
        self.redraw_canvas()

    def on_canvas_double_click(self, event):
        x = self.canvas.canvasx(event.x) / self.zoom
        y = self.canvas.canvasy(event.y) / self.zoom
        clicked_node = self.find_node_at_position(x, y)
        if clicked_node:
            if not clicked_node.is_primary_instance:
                self.app.window_controllers.open_page_diagram(getattr(clicked_node, "original", clicked_node))
            else:
                if clicked_node.is_page:
                    self.app.window_controllers.open_page_diagram(clicked_node)
                else:
                    from gui.dialogs.edit_node_dialog import EditNodeDialog

                    EditNodeDialog(self.app.root, clicked_node, self.app)
            self.app.update_views()

    def on_canvas_drag(self, event):
        if self.dragging_node:
            x = self.canvas.canvasx(event.x) / self.zoom
            y = self.canvas.canvasy(event.y) / self.zoom
            new_x = x - self.drag_offset_x
            new_y = y - self.drag_offset_y
            dx = new_x - self.dragging_node.x
            dy = new_y - self.dragging_node.y
            self.dragging_node.x = new_x
            self.dragging_node.y = new_y
            if self.dragging_node.is_primary_instance:
                self.app.move_subtree(self.dragging_node, dx, dy)
            self.app.sync_nodes_by_id(self.dragging_node)
            self.redraw_canvas()

    def on_canvas_release(self, event):
        if self.dragging_node:
            self.dragging_node.x = round(self.dragging_node.x / self.grid_size) * self.grid_size
            self.dragging_node.y = round(self.dragging_node.y / self.grid_size) * self.grid_size
            self.app.sync_nodes_by_id(self.dragging_node)
            self.app.push_undo_state()
        self.dragging_node = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def zoom_in(self):
        self.zoom *= 1.2
        self.diagram_font.config(size=int(8 * self.zoom))
        self.redraw_canvas()

    def zoom_out(self):
        self.zoom /= 1.2
        self.diagram_font.config(size=int(8 * self.zoom))
        self.redraw_canvas()

    def auto_arrange(self):
        if self.root_node is None:
            return
        horizontal_gap = 150
        vertical_gap = 100
        next_y = [100]

        def layout(node, depth):
            node.x = depth * horizontal_gap + 100
            if not node.children:
                node.y = next_y[0]
                next_y[0] += vertical_gap
            else:
                for child in node.children:
                    layout(child, depth + 1)
                node.y = (node.children[0].y + node.children[-1].y) / 2

        layout(self.root_node, 0)
        # Center layout horizontally within the canvas
        all_nodes = self.get_all_nodes(self.root_node)
        if all_nodes:
            min_x = min(n.x for n in all_nodes)
            max_x = max(n.x for n in all_nodes)
            canvas_width = self.canvas.winfo_width()
            if canvas_width < 10:
                canvas_width = 800
            diagram_width = max_x - min_x
            offset = (canvas_width / self.zoom - diagram_width) / 2 - min_x
            for n in all_nodes:
                n.x += offset
        self.redraw_canvas()

    def redraw_canvas(self):
        # Clear the canvas and draw the grid first.
        if not hasattr(self, "canvas") or self.canvas is None or not self.canvas.winfo_exists():
            return
        self.canvas.delete("all")
        if hasattr(self.app, "fta_drawing_helper"):
            self.app.fta_drawing_helper.clear_cache()

        # Use the page's root node as the sole top-level event.
        drawn_ids = set()
        for top_event in [self.root_node]:
            self.draw_connections(top_event, drawn_ids)

        all_nodes = []
        for top_event in [self.root_node]:
            all_nodes.extend(self.get_all_nodes(top_event))
        for node in all_nodes:
            self.draw_node(node)

        # Update the scroll region.
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def draw_connections(self, node, drawn_ids=set()):
        if id(node) in drawn_ids:
            return
        drawn_ids.add(id(node))
        if node.is_page and node.is_primary_instance and node != self.root_node:
            return
        if node.children:
            region_width = 100 * self.zoom
            parent_bottom = (node.x * self.zoom, node.y * self.zoom + 40 * self.zoom)
            N = len(node.children)
            for i, child in enumerate(node.children):
                parent_conn = (
                    node.x * self.zoom - region_width / 2 + (i + 0.5) * (region_width / N),
                    parent_bottom[1],
                )
                child_top = (child.x * self.zoom, child.y * self.zoom - 45 * self.zoom)
                fta_drawing_helper.draw_90_connection(
                    self.canvas, parent_conn, child_top, outline_color="dimgray", line_width=1
                )
            for child in node.children:
                self.draw_connections(child, drawn_ids)

    def draw_node(self, node):
        """Draw the given node on the canvas."""

        # If the node is a clone, use its original for configuration (non-positional attributes)
        source = node if node.is_primary_instance else node.original

        # For display purposes, show the clone marker on the clone's display_label.
        if node.is_primary_instance:
            display_label = source.display_label
        else:
            display_label = source.display_label + " (clone)"

        # Build a short top_text string from the source's attributes.
        subtype_text = source.input_subtype if source.input_subtype else "N/A"
        top_text = (
            f"Type: {source.node_type}\n"
            f"Subtype: {subtype_text}\n"
            f"{display_label}\n"
            f"Desc: {source.description}\n\n"
            f"Rationale: {source.rationale}"
        )
        bottom_text = source.name

        # Compute the effective position using the clone’s own (positional) values
        eff_x = node.x * self.zoom
        eff_y = node.y * self.zoom

        # Highlight if selected
        outline_color = "red" if node == self.selected_node else "dimgray"
        line_width = 2 if node == self.selected_node else 1

        # Determine the fill color using this diagram's mode to avoid cross-tab color mixing
        fill_color = self.app.get_node_fill_color(node, self.diagram_mode)
        font_obj = self.diagram_font

        # For shape selection, use the source’s node type and gate type.
        node_type_upper = source.node_type.upper()

        if not node.is_primary_instance:
            # For clones, draw them in the shape of the original with a bottom line marker.
            if node_type_upper in GATE_NODE_TYPES:
                if source.gate_type.upper() == "OR":
                    fta_drawing_helper.draw_rotated_or_gate_clone_shape(
                        self.canvas,
                        eff_x,
                        eff_y,
                        scale=40 * self.zoom,
                        top_text=top_text,
                        bottom_text=bottom_text,
                        fill=fill_color,
                        outline_color=outline_color,
                        line_width=line_width,
                        font_obj=font_obj,
                    )
                else:
                    fta_drawing_helper.draw_rotated_and_gate_clone_shape(
                        self.canvas,
                        eff_x,
                        eff_y,
                        scale=40 * self.zoom,
                        top_text=top_text,
                        bottom_text=bottom_text,
                        fill=fill_color,
                        outline_color=outline_color,
                        line_width=line_width,
                        font_obj=font_obj,
                    )
            elif source.is_page and source != self.root_node:
                fta_drawing_helper.draw_triangle_clone_shape(
                    self.canvas,
                    eff_x,
                    eff_y,
                    scale=40 * self.zoom,
                    top_text=top_text,
                    bottom_text=bottom_text,
                    fill=fill_color,
                    outline_color=outline_color,
                    line_width=line_width,
                    font_obj=font_obj,
                )
            else:
                fta_drawing_helper.draw_circle_event_clone_shape(
                    self.canvas,
                    eff_x,
                    eff_y,
                    45 * self.zoom,
                    top_text=top_text,
                    bottom_text=bottom_text,
                    fill=fill_color,
                    outline_color=outline_color,
                    line_width=line_width,
                    font_obj=font_obj,
                )
        else:
            # Primary node: use normal drawing routines.
            if node_type_upper in GATE_NODE_TYPES:
                if source.is_page and source != self.root_node:
                    fta_drawing_helper.draw_triangle_shape(
                        self.canvas,
                        eff_x,
                        eff_y,
                        scale=40 * self.zoom,
                        top_text=top_text,
                        bottom_text=bottom_text,
                        fill=fill_color,
                        outline_color=outline_color,
                        line_width=line_width,
                        font_obj=font_obj,
                    )
                else:
                    if source.gate_type.upper() == "OR":
                        fta_drawing_helper.draw_rotated_or_gate_shape(
                            self.canvas,
                            eff_x,
                            eff_y,
                            scale=40 * self.zoom,
                            top_text=top_text,
                            bottom_text=bottom_text,
                            fill=fill_color,
                            outline_color=outline_color,
                            line_width=line_width,
                            font_obj=font_obj,
                        )
                    else:
                        fta_drawing_helper.draw_rotated_and_gate_shape(
                            self.canvas,
                            eff_x,
                            eff_y,
                            scale=40 * self.zoom,
                            top_text=top_text,
                            bottom_text=bottom_text,
                            fill=fill_color,
                            outline_color=outline_color,
                            line_width=line_width,
                            font_obj=font_obj,
                        )
            elif node_type_upper in ["CONFIDENCE LEVEL", "ROBUSTNESS SCORE"]:
                fta_drawing_helper.draw_circle_event_shape(
                    self.canvas,
                    eff_x,
                    eff_y,
                    45 * self.zoom,
                    top_text=top_text,
                    bottom_text=bottom_text,
                    fill=fill_color,
                    outline_color=outline_color,
                    line_width=line_width,
                    font_obj=font_obj,
                )
            else:
                if hasattr(self.canvas, "create_line"):
                    fta_drawing_helper.draw_circle_event_shape(
                        self.canvas,
                        eff_x,
                        eff_y,
                        45 * self.zoom,
                        top_text=top_text,
                        bottom_text=bottom_text,
                        fill=fill_color,
                        outline_color=outline_color,
                        line_width=line_width,
                        font_obj=font_obj,
                    )

        # Draw any additional text (such as equations) from the source.
        if source.equation:
            self.canvas.create_text(
                eff_x - 80 * self.zoom,
                eff_y - 15 * self.zoom,
                text=source.equation,
                anchor="e",
                fill="gray",
                font=self.diagram_font,
            )
        if source.detailed_equation:
            self.canvas.create_text(
                eff_x - 80 * self.zoom,
                eff_y + 15 * self.zoom,
                text=source.detailed_equation,
                anchor="e",
                fill="gray",
                font=self.diagram_font,
            )

        # Finally, if the node appears multiple times, draw a shared marker.
        if self.app.occurrence_counts.get(node.unique_id, 0) > 1:
            marker_x = eff_x + 30 * self.zoom
            marker_y = eff_y - 30 * self.zoom
            fta_drawing_helper.draw_shared_marker(self.canvas, marker_x, marker_y, self.zoom)


__all__ = ["PageDiagram"]
