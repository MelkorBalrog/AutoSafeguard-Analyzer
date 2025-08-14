import tkinter as tk
from tkinter import ttk, simpledialog

from analysis import SafetyManagementToolbox
from gui.architecture import GovernanceDiagramWindow
from gui import messagebox


class SafetyManagementWindow(tk.Frame):
    """Editor and browser for Safety & Security Management diagrams.

    Users can create, rename, and delete Governance Diagrams that model the
    project's safety governance. Only diagrams registered in the provided
    :class:`SafetyManagementToolbox` are listed.
    """

    def __init__(self, master, app, toolbox: SafetyManagementToolbox | None = None):
        super().__init__(master)
        self.app = app
        self.toolbox = toolbox or SafetyManagementToolbox()

        phase_bar = ttk.Frame(self)
        phase_bar.pack(fill=tk.X)
        ttk.Label(phase_bar, text="Lifecycle:").pack(side=tk.LEFT)
        self.phase_var = tk.StringVar()
        self.phase_cb = ttk.Combobox(phase_bar, textvariable=self.phase_var, state="readonly")
        self.phase_cb.pack(side=tk.LEFT, padx=2)
        self.phase_cb.bind("<<ComboboxSelected>>", self.select_phase)

        top = ttk.Frame(self)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Diagram:").pack(side=tk.LEFT)
        self.diag_var = tk.StringVar()
        self.diag_cb = ttk.Combobox(top, textvariable=self.diag_var, state="readonly")
        self.diag_cb.pack(side=tk.LEFT, padx=2)
        self.diag_cb.bind("<<ComboboxSelected>>", self.select_diagram)

        ttk.Button(top, text="New", command=self.new_diagram).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_diagram).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_diagram).pack(side=tk.LEFT)

        self.diagram_frame = ttk.Frame(self)
        self.diagram_frame.pack(fill=tk.BOTH, expand=True)
        self.current_window = None

        self.refresh_phases()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Diagram operations
    # ------------------------------------------------------------------
    def refresh_diagrams(self):
        if self.toolbox.active_module:
            names = sorted(self.toolbox.diagrams_for_module(self.toolbox.active_module))
        else:
            names = self.toolbox.list_diagrams()
        self.diag_cb.configure(values=names)
        if names:
            current = self.diag_var.get()
            if current not in names:
                self.diag_var.set(names[0])
            self.open_diagram(self.diag_var.get())
        else:
            self.diag_var.set("")
            self.open_diagram(None)

    def refresh_phases(self):
        phases = ["All"] + sorted(self.toolbox.list_modules())
        self.phase_cb.configure(values=phases)
        current = self.phase_var.get()
        if current not in phases:
            self.phase_var.set("All")
        self.select_phase()

    def select_phase(self, *_):
        phase = self.phase_var.get()
        if phase == "All" or not phase:
            self.toolbox.set_active_module(None)
            phase_name = ""
        else:
            self.toolbox.set_active_module(phase)
            phase_name = phase

        app = getattr(self, "app", None)
        if app:
            if hasattr(app, "lifecycle_var"):
                try:
                    app.lifecycle_var.set(phase_name)
                except Exception:
                    pass
            if hasattr(app, "on_lifecycle_selected"):
                try:
                    app.on_lifecycle_selected()
                except Exception:
                    pass
            if hasattr(app, "refresh_tool_enablement"):
                try:
                    app.refresh_tool_enablement()
                except Exception:
                    pass

        self.refresh_diagrams()

    def new_diagram(self):
        messagebox.showerror(
            "New Diagram",
            "Governance diagrams must be created inside a folder in the Explorer",
        )

    def delete_diagram(self):
        name = self.diag_var.get()
        if not name:
            return
        self.toolbox.delete_diagram(name)
        self.refresh_diagrams()

    def rename_diagram(self):
        old = self.diag_var.get()
        if not old:
            return
        new = simpledialog.askstring("Rename Diagram", "Name:", initialvalue=old, parent=self)
        if not new or new == old:
            return
        actual = self.toolbox.rename_diagram(old, new)
        self.refresh_diagrams()
        self.diag_var.set(actual)
        self.open_diagram(actual)

    def select_diagram(self, *_):
        name = self.diag_var.get()
        self.open_diagram(name)

    def open_diagram(self, name: str | None):
        for child in self.diagram_frame.winfo_children():
            child.destroy()
        self.current_window = None
        if not name:
            return
        diag_id = self.toolbox.diagrams.get(name)
        if diag_id is None:
            return
        self.current_window = GovernanceDiagramWindow(self.diagram_frame, self.app, diagram_id=diag_id)
        self.current_window.pack(fill=tk.BOTH, expand=True)
