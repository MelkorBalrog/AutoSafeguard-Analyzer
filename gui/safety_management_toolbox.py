import tkinter as tk
from tkinter import ttk, simpledialog

from analysis import SafetyManagementToolbox
from gui.architecture import BPMNDiagramWindow


class SafetyManagementWindow(tk.Frame):
    """Editor and browser for Safety Management diagrams.

    Users can create, rename, and delete BPMN Diagrams that model the
    project's safety governance. Only diagrams registered in the provided
    :class:`SafetyManagementToolbox` are listed.
    """

    def __init__(self, master, app, toolbox: SafetyManagementToolbox | None = None):
        super().__init__(master)
        self.app = app
        self.toolbox = toolbox or SafetyManagementToolbox()

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

        self.refresh_diagrams()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Diagram operations
    # ------------------------------------------------------------------
    def refresh_diagrams(self):
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

    def new_diagram(self):
        name = simpledialog.askstring("New Diagram", "Name:", parent=self)
        if not name:
            return
        self.toolbox.create_diagram(name)
        self.refresh_diagrams()
        self.diag_var.set(name)
        self.open_diagram(name)

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
        self.toolbox.rename_diagram(old, new)
        self.refresh_diagrams()
        self.diag_var.set(new)
        self.open_diagram(new)

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
        self.current_window = BPMNDiagramWindow(self.diagram_frame, self.app, diagram_id=diag_id)
        self.current_window.pack(fill=tk.BOTH, expand=True)
