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

import tkinter as tk
from collections import Counter


class MetricsTab(tk.Frame):
    """Tab displaying simple project metrics graphs without Matplotlib."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.canvases = [
            tk.Canvas(self, width=300, height=200, bg="white") for _ in range(3)
        ]
        for c in self.canvases:
            c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.update_plots()

    # Four experimental implementations of the same line chart function.
    # Each delegates to ``_line_chart_core`` which performs the actual work.
    def _draw_line_chart(self, canvas: tk.Canvas, data):
        self._line_chart_core(canvas, data)

    @staticmethod
    def _draw_line_chart_v1(_self, canvas: tk.Canvas, data):
        MetricsTab._line_chart_core(canvas, data)

    @staticmethod
    def _draw_line_chart_v2(_self, canvas: tk.Canvas, data):
        MetricsTab._line_chart_core(canvas, data)

    @staticmethod
    def _draw_line_chart_v3(_self, canvas: tk.Canvas, data):
        MetricsTab._line_chart_core(canvas, data)

    @staticmethod
    def _draw_line_chart_v4(_self, canvas: tk.Canvas, data):
        MetricsTab._line_chart_core(canvas, data)

    @staticmethod
    def _line_chart_core(canvas: tk.Canvas, data):
        canvas.delete("all")
        h = int(canvas["height"])
        w = int(canvas["width"])
        max_val = max(data or [0]) or 1
        step = w / max(1, len(data) - 1)
        points = [
            coord
            for i, val in enumerate(data)
            for coord in (i * step, h - (val / max_val) * h)
        ]
        if len(points) > 3:
            canvas.create_line(*points, fill="blue")
        canvas.create_text(5, 5, anchor="nw", text="Requirements")

    def _draw_bar_chart(self, canvas: tk.Canvas, data):
        canvas.delete("all")
        h = int(canvas["height"])
        w = int(canvas["width"])
        keys = list(data.keys())
        vals = list(data.values())
        n = len(keys)
        bar_w = w / max(1, n)
        max_val = max(vals) if vals else 1
        for i, (k, v) in enumerate(data.items()):
            x0 = i * bar_w + 10
            x1 = (i + 1) * bar_w - 10
            y1 = h - (v / max_val) * h
            canvas.create_rectangle(x0, y1, x1, h, fill="green")
            canvas.create_text((x0 + x1) / 2, h - 5, anchor="s", text=str(k))

    def update_plots(self):
        req_history = getattr(self.app, "requirement_history", [])
        if not req_history:
            req_history = [len(getattr(self.app, "requirements", []))]
        self._draw_line_chart(self.canvases[0], req_history)

        statuses = Counter(
            getattr(r, "status", "unknown")
            for r in getattr(self.app, "requirements", [])
        )
        self._draw_bar_chart(self.canvases[1], statuses)
        self.canvases[1].create_text(5, 5, anchor="nw", text="Status")

        user_metrics = getattr(self.app, "user_metrics", {})
        self._draw_bar_chart(self.canvases[2], user_metrics)
        self.canvases[2].create_text(5, 5, anchor="nw", text="User Effort")
