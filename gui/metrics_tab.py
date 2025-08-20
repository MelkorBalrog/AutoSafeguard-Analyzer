import tkinter as tk
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class MetricsTab(tk.Frame):
    """Tab displaying simple project metrics graphs."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.fig = plt.Figure(figsize=(9, 3))
        self.axes = [self.fig.add_subplot(131),
                     self.fig.add_subplot(132),
                     self.fig.add_subplot(133)]
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas = canvas
        self.update_plots()

    def update_plots(self):
        req_history = getattr(self.app, "requirement_history", [])
        if not req_history:
            req_history = [len(getattr(self.app, "requirements", []))]
        ax = self.axes[0]
        ax.clear()
        ax.plot(req_history)
        ax.set_title("Requirements")

        statuses = Counter(getattr(r, "status", "unknown") for r in getattr(self.app, "requirements", []))
        ax = self.axes[1]
        ax.clear()
        ax.bar(list(statuses.keys()), list(statuses.values()))
        ax.set_title("Status")

        user_metrics = getattr(self.app, "user_metrics", {})
        ax = self.axes[2]
        ax.clear()
        if user_metrics:
            ax.bar(list(user_metrics.keys()), list(user_metrics.values()))
        ax.set_title("User Effort")
        self.fig.tight_layout()
        self.canvas.draw_idle()
