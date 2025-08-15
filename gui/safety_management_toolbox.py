import tkinter as tk
from tkinter import ttk, simpledialog

from analysis import SafetyManagementToolbox
from analysis.governance import GovernanceDiagram
from gui.architecture import GovernanceDiagramWindow
from gui import messagebox
from sysml.sysml_repository import SysMLRepository


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
        try:
            self.app.safety_mgmt_window = self
        except Exception:
            pass

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
        ttk.Button(top, text="Requirements", command=self.generate_requirements).pack(
            side=tk.LEFT
        )
        self.phase_menu_btn = tk.Menubutton(top, text="Phase Requirements")
        self.phase_menu = tk.Menu(self.phase_menu_btn, tearoff=False)
        self.phase_menu_btn.configure(menu=self.phase_menu)
        self.phase_menu_btn.pack(side=tk.LEFT)

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
        self._refresh_phase_menu()

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

    def generate_requirements(self) -> None:
        """Generate requirements for the selected governance diagram."""
        name = self.diag_var.get()
        if not name:
            return
        diag_id = self.toolbox.diagrams.get(name)
        if not diag_id:
            return
        repo = SysMLRepository.get_instance()
        gov = GovernanceDiagram.from_repository(repo, diag_id)
        reqs = gov.generate_requirements()
        if not reqs:
            messagebox.showinfo("Requirements", "No requirements were generated.")
            return
        frame = self.app._new_tab(f"{name} Requirements")
        txt = tk.Text(frame, wrap="word")
        txt.insert("1.0", "\n".join(reqs))
        txt.configure(state="disabled")
        txt.pack(fill=tk.BOTH, expand=True)

    def _refresh_phase_menu(self) -> None:
        self.phase_menu.delete(0, tk.END)
        for phase in sorted(self.toolbox.list_modules()):
            self.phase_menu.add_command(
                label=phase,
                command=lambda p=phase: self.generate_phase_requirements(p),
            )

    def generate_phase_requirements(self, phase: str) -> None:
        diag_names = sorted(self.toolbox.diagrams_for_module(phase))
        if not diag_names:
            messagebox.showinfo("Requirements", f"No governance diagrams for phase '{phase}'.")
            return
        repo = SysMLRepository.get_instance()
        lines: list[str] = []
        for name in diag_names:
            diag_id = self.toolbox.diagrams.get(name)
            if not diag_id:
                continue
            gov = GovernanceDiagram.from_repository(repo, diag_id)
            reqs = gov.generate_requirements()
            if reqs:
                lines.append(f"{name}:")
                lines.extend(reqs)
                lines.append("")
        if not lines:
            messagebox.showinfo(
                "Requirements",
                f"No requirements were generated for phase '{phase}'.",
            )
            return
        frame = self.app._new_tab(f"{phase} Requirements")
        txt = tk.Text(frame, wrap="word")
        txt.insert("1.0", "\n".join(lines).strip())
        txt.configure(state="disabled")
        txt.pack(fill=tk.BOTH, expand=True)
