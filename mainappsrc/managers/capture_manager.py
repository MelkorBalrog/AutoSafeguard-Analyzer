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

"""Helpers for capturing various diagram types into images.

This manager centralises logic that was previously scattered in
``automl_core`` to reduce its complexity and improve modularity.
"""

import tkinter as tk
from gui.styles.style_manager import StyleManager


class CaptureManager:
    """Capture diagrams and return PIL images."""

    def __init__(self, app):
        self.app = app

    def capture_page_diagram(self, page_node):
        return self.app.pages_and_paa.capture_page_diagram(page_node)

    def capture_gsn_diagram(self, diagram):
        """Return a PIL Image of the given GSN diagram."""
        from io import BytesIO
        from PIL import Image

        temp = tk.Toplevel(self.app.root)
        temp.withdraw()
        canvas = tk.Canvas(
            temp,
            bg=StyleManager.get_instance().canvas_bg,
            width=2000,
            height=2000,
        )
        canvas.pack()

        try:
            diagram.draw(canvas)
        except Exception:
            temp.destroy()
            return None

        canvas.update()
        bbox = canvas.bbox("all")
        if not bbox:
            temp.destroy()
            return None
        x, y, x2, y2 = bbox
        width, height = x2 - x, y2 - y
        ps = canvas.postscript(
            colormode="color", x=x, y=y, width=width, height=height
        )
        ps_bytes = BytesIO(ps.encode("utf-8"))
        try:
            img = Image.open(ps_bytes)
            img.load(scale=3)
        except Exception:
            img = None
        temp.destroy()
        return img.convert("RGB") if img else None

    def capture_sysml_diagram(self, diagram):
        """Return a PIL Image of the given SysML diagram."""
        from io import BytesIO
        from PIL import Image
        from gui.windows.architecture import (
            UseCaseDiagramWindow,
            ActivityDiagramWindow,
            BlockDiagramWindow,
            InternalBlockDiagramWindow,
            ControlFlowDiagramWindow,
            GovernanceDiagramWindow,
        )

        temp = tk.Toplevel(self.app.root)
        temp.withdraw()
        if diagram.diag_type == "Use Case Diagram":
            win = UseCaseDiagramWindow(temp, self.app, diagram_id=diagram.diag_id)
        elif diagram.diag_type == "Activity Diagram":
            win = ActivityDiagramWindow(temp, self.app, diagram_id=diagram.diag_id)
        elif diagram.diag_type == "Block Diagram":
            win = BlockDiagramWindow(temp, self.app, diagram_id=diagram.diag_id)
        elif diagram.diag_type == "Internal Block Diagram":
            win = InternalBlockDiagramWindow(temp, self.app, diagram_id=diagram.diag_id)
        elif diagram.diag_type == "Control Flow Diagram":
            win = ControlFlowDiagramWindow(temp, self.app, diagram_id=diagram.diag_id)
        elif diagram.diag_type == "Governance Diagram":
            win = GovernanceDiagramWindow(temp, self.app, diagram_id=diagram.diag_id)
        else:
            temp.destroy()
            return None

        win.redraw()
        win.canvas.update()
        bbox = win.canvas.bbox("all")
        if not bbox:
            temp.destroy()
            return None

        x, y, x2, y2 = bbox
        width, height = x2 - x, y2 - y
        ps = win.canvas.postscript(
            colormode="color", x=x, y=y, width=width, height=height
        )
        ps_bytes = BytesIO(ps.encode("utf-8"))
        try:
            img = Image.open(ps_bytes)
            img.load(scale=3)
        except Exception:
            img = None
        temp.destroy()
        return img.convert("RGB") if img else None

    def capture_cbn_diagram(self, doc):
        """Return a PIL Image of the given Causal Bayesian Network diagram."""
        from io import BytesIO
        from PIL import Image
        from gui.causal_bayesian_network_window import (
            CausalBayesianNetworkWindow,
        )

        temp = tk.Toplevel(self.app.root)
        temp.withdraw()
        try:
            win = CausalBayesianNetworkWindow(temp, self.app)
            win.doc_var.set(doc.name)
            win.select_doc()
            win.canvas.update()
            bbox = win.canvas.bbox("all")
            if not bbox:
                temp.destroy()
                return None
            x, y, x2, y2 = bbox
            width, height = x2 - x, y2 - y
            ps = win.canvas.postscript(
                colormode="color", x=x, y=y, width=width, height=height
            )
            ps_bytes = BytesIO(ps.encode("utf-8"))
            try:
                img = Image.open(ps_bytes)
                img.load(scale=3)
            except Exception:
                img = None
        finally:
            temp.destroy()
        return img.convert("RGB") if img else None

    def capture_diff_diagram(self, top_event):
        return self.app.review_manager.capture_diff_diagram(top_event)
