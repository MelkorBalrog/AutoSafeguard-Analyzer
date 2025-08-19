import tkinter as tk
from tkinter import ttk

class ToolTip:
    """Simple tooltip for Tkinter widgets.

    By default the tooltip is displayed when the mouse hovers over the
    associated widget.  The ``show`` and ``hide`` methods can also be used to
    control the tooltip manually (e.g. for notebook tabs).
    """

    def __init__(self, widget, text: str, delay: int = 500, *, automatic: bool = True):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        if automatic:
            widget.bind("<Enter>", self._schedule)
            widget.bind("<Leave>", self._hide)

    def _schedule(self, _event=None):
        self._unschedule()
        self.id = self.widget.after(self.delay, self._show)

    def _show(self, _x: int | None = None, _y: int | None = None):
        if self.tipwindow or not self.text:
            return

        # If explicit coordinates aren't provided, fall back to the current
        # pointer location so the tooltip follows the cursor.  Handle x and y
        # independently to avoid "unbound" errors when only one value is given.
        if x is None or y is None:
            px, py = self.widget.winfo_pointerxy()
            if x is None:
                x = px
            if y is None:
                y = py

        # Offset slightly so the cursor stays over the widget, otherwise some
        # widgets (e.g. notebook tabs) immediately receive a <Leave> event when
        # the tooltip window appears on top of the pointer.
        x += 1
        y += 1
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        # Ensure the tooltip stays above other windows
        try:
            tw.wm_attributes("-topmost", True)
            tw.wm_attributes("-alpha", 0.9)
        except tk.TclError:
            pass

        lines = self.text.split("\n")
        max_len = max((len(line) for line in lines), default=1)
        width = min(max_len, 80)
        height = min(len(lines), 20)
        need_h = max_len > width
        need_v = len(lines) > height

        text = tk.Text(
            tw,
            width=width,
            height=height,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            wrap="none",
            # Use a fixed-width font so table-like tooltip content stays aligned
            font=("TkFixedFont", 8),
        )
        vbar = ttk.Scrollbar(tw, orient="vertical", command=text.yview)
        hbar = ttk.Scrollbar(tw, orient="horizontal", command=text.xview)
        if need_v:
            text.configure(yscrollcommand=vbar.set)
            vbar.grid(row=0, column=1, sticky="ns")
        if need_h:
            text.configure(xscrollcommand=hbar.set)
            hbar.grid(row=1, column=0, sticky="ew")
        text.insert("1.0", self.text)
        text.configure(state="disabled")
        text.grid(row=0, column=0, sticky="nsew")
        tw.grid_columnconfigure(0, weight=1)
        tw.grid_rowconfigure(0, weight=1)
        tw.wm_geometry(f"+{x}+{y}")

    def show(self, x: int | None = None, y: int | None = None):
        """Show the tooltip immediately."""
        self._hide()
        self._show()

    def hide(self):
        """Hide the tooltip immediately."""
        self._hide()

    def _hide(self, _event=None):
        self._unschedule()
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

    def _unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
