import tkinter as tk

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

    def _show(self, x: int | None = None, y: int | None = None):
        if self.tipwindow or not self.text:
            return
        if x is None:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        # Ensure the tooltip stays above other windows
        try:
            tw.wm_attributes("-topmost", True)
        except tk.TclError:
            pass
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            justify="left",
            wraplength=300,
        )
        label.pack(ipadx=1)

    def show(self, x: int | None = None, y: int | None = None):
        """Show the tooltip immediately."""
        self._hide()
        self._show(x, y)

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
