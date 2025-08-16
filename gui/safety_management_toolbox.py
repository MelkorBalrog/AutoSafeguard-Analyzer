import tkinter as tk
from tkinter import ttk, simpledialog

from functools import partial

from analysis import SafetyManagementToolbox
from analysis.governance import GovernanceDiagram
from analysis.models import (
    REQUIREMENT_TYPE_OPTIONS,
    ensure_requirement_defaults,
    global_requirements,
)
from gui.architecture import GovernanceDiagramWindow
from gui import messagebox
from sysml.sysml_repository import SysMLRepository


class SafetyManagementWindow(tk.Frame):
    """Editor and browser for Safety & Security Management diagrams.

    Users can create, rename, and delete Governance Diagrams that model the
    project's safety governance. Only diagrams registered in the provided
    :class:`SafetyManagementToolbox` are listed.
    """

    def __init__(
        self,
        master,
        app,
        toolbox: SafetyManagementToolbox | None = None,
        show_diagrams: bool = True,
    ):
        super().__init__(master)
        self.app = app
        self.toolbox = toolbox or SafetyManagementToolbox()
        self._auto_show_diagram = show_diagrams
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
        self.phase_menu_btn = ttk.Menubutton(top, text="Phase Requirements")
        self.phase_menu = tk.Menu(self.phase_menu_btn, tearoff=False)
        self.phase_menu_btn.configure(menu=self.phase_menu)
        self.phase_menu_btn.pack(side=tk.LEFT)
        ttk.Button(
            top,
            text="Lifecycle Requirements",
            command=self.generate_lifecycle_requirements,
        ).pack(side=tk.LEFT)
        ttk.Button(
            top,
            text="Delete Obsolete",
            command=self.delete_obsolete_requirements,
        ).pack(side=tk.LEFT)

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
                # Setting the variable programmatically fires the
                # ``<<ComboboxSelected>>`` event which in turn calls
                # ``open_diagram``.  Calling ``open_diagram`` here as well would
                # result in the widget being destroyed while the first call is
                # still rendering, leading to ``invalid command name`` errors.
                # Therefore only set the variable and let the event handler
                # perform the actual opening.
                self.diag_var.set(names[0])
            elif self._auto_show_diagram:
                self.open_diagram(current)
        elif self._auto_show_diagram:
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
        if app and hasattr(app, "refresh_all"):
            try:
                app.refresh_all()
            except Exception:
                pass

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

    # ------------------------------------------------------------------
    def _add_requirement(
        self,
        text: str,
        req_type: str = "organizational",
        phase: str | None = None,
        diagram: str | None = None,
        variables: list[str] | None = None,
    ) -> str:
        """Create a new requirement with a unique identifier.

        ``phase`` indicates the lifecycle phase the requirement originates from.
        ``None`` means it is a lifecycle requirement visible in all phases.
        ``diagram`` records the source diagram so updates can be tracked per
        diagram.
        """
        idx = 1
        while f"R{idx}" in global_requirements:
            idx += 1
        rid = f"R{idx}"
        app = getattr(self, "app", None)
        if app and hasattr(app, "add_new_requirement"):
            req = app.add_new_requirement(rid, req_type, text)
            req["phase"] = phase
            req["diagram"] = diagram
            req["variables"] = variables or []
            global_requirements[rid] = req
        else:
            req = {
                "id": rid,
                "custom_id": rid,
                "req_type": req_type,
                "text": text,
                "status": "draft",
                "parent_id": "",
                "phase": phase,
                "diagram": diagram,
                "variables": variables or [],
            }
            ensure_requirement_defaults(req)
            global_requirements[rid] = req
        return rid

    # ------------------------------------------------------------------
    def _display_requirements(self, title: str, ids: list[str]) -> None:
        frame = self.app._new_tab(title)
        for child in frame.winfo_children():
            child.destroy()
        columns = ("ID", "Type", "Text", "Phase", "Status")
        tree_frame = ttk.Frame(frame)
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for c in columns:
            tree.heading(c, text=c)
        for rid in ids:
            req = global_requirements.get(rid, {})
            tree.insert(
                "",
                "end",
                values=(
                    rid,
                    req.get("req_type", ""),
                    req.get("text", ""),
                    req.get("phase") or "",
                    req.get("status", ""),
                ),
            )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def _current_requirement_pairs(
        phase: str | None, diagram: str | None = None
    ) -> list[tuple[str, str, tuple[str, ...]]]:
        """Return existing requirement (text, type, variables) tuples.

        Only non-obsolete requirements are considered.  When ``diagram`` is
        provided, only requirements originating from that diagram are returned.
        """
        return sorted(
            (
                req.get("text", "").strip(),
                req.get("req_type", "organizational"),
                tuple(req.get("variables", [])),
            )
            for req in global_requirements.values()
            if req.get("phase") == phase
            and req.get("status") != "obsolete"
            and (diagram is None or req.get("diagram") == diagram)
        )

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
        try:
            raw_reqs = gov.generate_requirements()
        except Exception as exc:  # pragma: no cover - defensive
            messagebox.showerror(
                "Requirements", f"Failed to generate requirements: {exc}"
            )
            return
        reqs: list[tuple[str, str, list[str]]] = []
        for r in raw_reqs:
            if isinstance(r, tuple):
                text, rtype = r
                vars_: list[str] = []
            elif hasattr(r, "text"):
                text, rtype = r.text, getattr(r, "req_type", "organizational")
                vars_ = getattr(r, "variables", [])
            else:
                text, rtype = str(r), "organizational"
                vars_ = []
            text = text.strip()
            if text:
                reqs.append((text, rtype, tuple(vars_)))
        if not reqs:
            messagebox.showinfo("Requirements", "No requirements were generated.")
            return
        phase = self.toolbox.module_for_diagram(name)
        existing = self._current_requirement_pairs(phase, name)
        if sorted(reqs) == existing:
            ids = [
                rid
                for rid, req in global_requirements.items()
                if (req.get("diagram") == name and req.get("phase") == phase)
                or req.get("phase") is None
            ]
            self._display_requirements(f"{name} Requirements", ids)
            return
        # Mark existing requirements from this diagram as obsolete before
        # creating new ones to reflect the updated governance model.
        for req in global_requirements.values():
            if req.get("phase") == phase and req.get("diagram") == name:
                req["status"] = "obsolete"
        ids: list[str] = []
        for text, rtype, vars_ in reqs:
            ids.append(
                self._add_requirement(
                    text, rtype, phase=phase, diagram=name, variables=vars_
                )
            )
        ids = [
            rid
            for rid, req in global_requirements.items()
            if (req.get("diagram") == name and req.get("phase") == phase)
            or req.get("phase") is None
        ]
        self._display_requirements(f"{name} Requirements", ids)

    def _refresh_phase_menu(self) -> None:
        self.phase_menu.delete(0, tk.END)
        phases = sorted(self.toolbox.list_modules())
        for phase in phases:
            # Use ``functools.partial`` to bind the current ``phase`` to the
            # callback.  Using ``lambda`` without binding would result in all
            # menu entries invoking the handler with the last value from the
            # loop.  ``partial`` creates a function with ``phase`` fixed to the
            # desired value so selecting a phase generates the correct
            # requirements.
            self.phase_menu.add_command(
                label=phase,
                command=partial(self.generate_phase_requirements, phase),
            )
        if phases:
            self.phase_menu.add_separator()
        self.phase_menu.add_command(
            label="Lifecycle",
            command=self.generate_lifecycle_requirements,
        )

    def generate_phase_requirements(self, phase: str) -> None:
        diag_names = sorted(self.toolbox.diagrams_for_module(phase))
        if not diag_names:
            messagebox.showinfo("Requirements", f"No governance diagrams for phase '{phase}'.")
            return
        repo = SysMLRepository.get_instance()
        diag_pairs: dict[str, list[tuple[str, str, list[str]]]] = {}
        for name in diag_names:
            diag_id = self.toolbox.diagrams.get(name)
            if not diag_id:
                continue
            gov = GovernanceDiagram.from_repository(repo, diag_id)
            try:
                raw_reqs = gov.generate_requirements()
            except Exception as exc:  # pragma: no cover - defensive
                messagebox.showerror(
                    "Requirements",
                    f"Failed to generate requirements for '{name}': {exc}",
                )
                continue
            pairs: list[tuple[str, str, list[str]]] = []
            invalid = False
            for r in raw_reqs:
                if isinstance(r, tuple):
                    if len(r) != 2:
                        invalid = True
                        break
                    text, rtype = r
                    vars_: list[str] = []
                elif hasattr(r, "text"):
                    text, rtype = r.text, getattr(r, "req_type", "organizational")
                    vars_ = getattr(r, "variables", [])
                elif isinstance(r, str):
                    text, rtype = r, "organizational"
                    vars_ = []
                else:
                    invalid = True
                    break
                text = text.strip()
                if text:
                    pairs.append((text, rtype, tuple(vars_)))
            if invalid:
                messagebox.showerror(
                    "Requirements",
                    "Requirement entries must be strings or (text, type) pairs.",
                )
                continue
            diag_pairs[name] = pairs
        pairs_all = [pair for pairs in diag_pairs.values() for pair in pairs]
        existing = self._current_requirement_pairs(phase)
        if not pairs_all and not existing:
            messagebox.showinfo(
                "Requirements",
                f"No requirements were generated for phase '{phase}'.",
            )
            return
        if sorted(pairs_all) == existing:
            ids = [
                rid
                for rid, req in global_requirements.items()
                if req.get("phase") in (phase, None)
            ]
            self._display_requirements(f"{phase} Requirements", ids)
            return
        # Mark existing requirements for this phase as obsolete before
        # generating updated ones.
        for req in global_requirements.values():
            if req.get("phase") == phase:
                req["status"] = "obsolete"
        ids: list[str] = []
        for name, pairs in diag_pairs.items():
            for text, rtype, vars_ in pairs:
                ids.append(
                    self._add_requirement(
                        text, rtype, phase=phase, diagram=name, variables=vars_
                    )
                )
        ids = [
            rid
            for rid, req in global_requirements.items()
            if req.get("phase") in (phase, None)
        ]
        self._display_requirements(f"{phase} Requirements", ids)

    def generate_lifecycle_requirements(self) -> None:
        """Generate requirements for diagrams outside of any phase."""
        all_diags = set(self.toolbox.list_diagrams())
        for phase in self.toolbox.list_modules():
            all_diags -= self.toolbox.diagrams_for_module(phase)
        diag_names = sorted(all_diags)
        if not diag_names:
            messagebox.showinfo(
                "Requirements", "No lifecycle governance diagrams.")
            return
        repo = SysMLRepository.get_instance()
        diag_pairs: dict[str, list[tuple[str, str, list[str]]]] = {}
        for name in diag_names:
            diag_id = self.toolbox.diagrams.get(name)
            if not diag_id:
                continue
            gov = GovernanceDiagram.from_repository(repo, diag_id)
            try:
                raw_reqs = gov.generate_requirements()
            except Exception as exc:  # pragma: no cover - defensive
                messagebox.showerror(
                    "Requirements",
                    f"Failed to generate requirements for '{name}': {exc}",
                )
                continue
            pairs: list[tuple[str, str, list[str]]] = []
            invalid = False
            for r in raw_reqs:
                if isinstance(r, tuple):
                    if len(r) != 2:
                        invalid = True
                        break
                    text, rtype = r
                    vars_: list[str] = []
                elif hasattr(r, "text"):
                    text, rtype = r.text, getattr(r, "req_type", "organizational")
                    vars_ = getattr(r, "variables", [])
                elif isinstance(r, str):
                    text, rtype = r, "organizational"
                    vars_ = []
                else:
                    invalid = True
                    break
                text = text.strip()
                if text:
                    pairs.append((text, rtype, tuple(vars_)))
            if invalid:
                messagebox.showerror(
                    "Requirements",
                    "Requirement entries must be strings or (text, type) pairs.",
                )
                continue
            diag_pairs[name] = pairs
        pairs_all = [pair for pairs in diag_pairs.values() for pair in pairs]
        existing = self._current_requirement_pairs(None)
        if not pairs_all and not existing:
            messagebox.showinfo(
                "Requirements",
                "No requirements were generated for lifecycle diagrams.",
            )
            return
        if sorted(pairs_all) == existing:
            ids = [
                rid
                for rid, req in global_requirements.items()
                if req.get("phase") is None
            ]
            self._display_requirements("Lifecycle Requirements", ids)
            return
        # Mark existing lifecycle requirements as obsolete before generating
        # new ones so the table reflects the latest governance models.
        for req in global_requirements.values():
            if req.get("phase") is None:
                req["status"] = "obsolete"
        ids: list[str] = []
        for name, pairs in diag_pairs.items():
            for text, rtype, vars_ in pairs:
                ids.append(
                    self._add_requirement(text, rtype, diagram=name, variables=vars_)
                )
        ids = [rid for rid, req in global_requirements.items() if req.get("phase") is None]
        self._display_requirements("Lifecycle Requirements", ids)

    def delete_obsolete_requirements(self) -> None:
        """Remove all requirements marked as obsolete."""
        obsolete = [rid for rid, req in global_requirements.items() if req.get("status") == "obsolete"]
        if not obsolete:
            messagebox.showinfo("Requirements", "No obsolete requirements to delete.")
            return
        for rid in obsolete:
            del global_requirements[rid]
        messagebox.showinfo(
            "Requirements", f"Deleted {len(obsolete)} obsolete requirements."
        )

    @staticmethod
    def _collect_requirements(gov: GovernanceDiagram) -> list[str]:
        """Return sanitized requirements from ``gov``.

        Each requirement must be a non-empty string; otherwise a :class:`TypeError`
        is raised to signal a model problem to the caller.
        """
        reqs: list[str] = []
        for r in gov.generate_requirements():
            if not isinstance(r, str):
                raise TypeError(
                    f"Requirement must be a string, got {type(r).__name__}"
                )
            text = r.strip()
            if text:
                reqs.append(text)
        return reqs
