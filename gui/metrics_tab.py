import tkinter as tk
from collections import Counter


class MetricsTab(tk.Frame):
    """Tab displaying simple project metrics graphs without Matplotlib."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.canvases = [tk.Canvas(self, width=300, height=200, bg="white") for _ in range(3)]
        for c in self.canvases:
            c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.update_plots()
        
    def _draw_line_chart(self, canvas: tk.Canvas, data):
        canvas.delete("all")
        h = int(canvas["height"])
        w = int(canvas["width"])
        max_val = max(data) if data else 1
        step = w / max(1, len(data) - 1)
        points = []
        for i, val in enumerate(data):
            x = i * step
            y = h - (val / max_val) * h
            points.extend([x, y])
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

        statuses = Counter(getattr(r, "status", "unknown") for r in getattr(self.app, "requirements", []))
        self._draw_bar_chart(self.canvases[1], statuses)
        self.canvases[1].create_text(5, 5, anchor="nw", text="Status")

        user_metrics = getattr(self.app, "user_metrics", {})
        self._draw_bar_chart(self.canvases[2], user_metrics)
        self.canvases[2].create_text(5, 5, anchor="nw", text="User Effort")
