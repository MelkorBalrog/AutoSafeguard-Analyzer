"""Search toolbox for finding objects within the AutoML model."""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

from gui import messagebox

# Additional model sections that can be searched.  Each tuple contains a
# human-readable category name, the name of a method on the ``app`` object
# returning the elements for that category and a method name used to open a
# result.  The app does not need to implement every function; missing ones
# simply yield no results.
EXTRA_CATEGORIES = [
    ("SysML Elements", "get_all_sysml_elements", "open_sysml_element"),
    ("SysML Relationships", "get_all_sysml_relationships", "open_sysml_relationship"),
    ("GSN Elements", "get_all_gsn_elements", "open_gsn_element"),
    ("FTA Elements", "get_all_fta_elements", "open_fta_element"),
    ("Governance Elements", "get_all_governance_elements", "open_governance_element"),
    ("Hazard Analysis Cells", "get_all_hazard_analysis_cells", "open_hazard_analysis_cell"),
    ("FI2TC Cells", "get_all_fi2tc_cells", "open_fi2tc_cell"),
    ("TC2FI Cells", "get_all_tc2fi_cells", "open_tc2fi_cell"),
    ("STPA Cells", "get_all_stpa_cells", "open_stpa_cell"),
    ("Risk Assessments", "get_all_risk_assessments", "open_risk_assessment"),
    ("Threat Analyses", "get_all_threat_analyses", "open_threat_analysis"),
    ("Product Goals", "get_all_product_goals", "open_product_goal"),
    ("Requirements", "get_all_requirements", "open_requirement"),
    ("FMEDA Entries", "get_all_fmeda_entries", "show_fmeda_table"),
    ("Reliability Analyses", "get_all_reliability_analyses", "open_reliability_analysis"),
    ("Mission Profiles", "get_all_mission_profiles", "open_mission_profile"),
    ("ODD Libraries", "get_all_odd_libraries", "open_odd_library"),
    ("Scenario Libraries", "get_all_scenario_libraries", "open_scenario_library"),
    ("SPI Metrics", "get_all_spi_metrics", "open_spi_metric"),
    ("Reviews", "get_all_reviews", "open_review"),
    ("Fault Prioritization", "get_all_fault_prioritizations", "open_fault_prioritization"),
]


class SearchToolbox(ttk.Frame):
    """Provide text-based search across model objects.

    The search entry accepts optional *category* prefixes so users can issue
    compact queries such as ``"nodes,connections: motor"``.  Results show the
    object's class and origin.  Double-clicking a match navigates to the
    corresponding diagram or table entry.
    """

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.search_var = tk.StringVar()
        self.case_var = tk.BooleanVar(value=False)
        self.regex_var = tk.BooleanVar(value=False)
        # each result is a mapping with keys: 'label' and 'open'
        self.results: list[dict[str, object]] = []
        self.current_index: int = -1

        self._init_handlers()

        ttk.Label(self, text="Query:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(self, textvariable=self.search_var)
        entry.grid(row=0, column=1, sticky="ew")
        entry.focus_set()

        ttk.Button(self, text="Find", command=self._run_search).grid(
            row=0, column=2, padx=(4, 0)
        )
        ttk.Button(self, text="Next", command=self._find_next).grid(
            row=0, column=3, padx=(4, 0)
        )
        ttk.Button(self, text="Prev", command=self._find_prev).grid(
            row=0, column=4, padx=(4, 0)
        )

        opts = ttk.Frame(self)
        opts.grid(row=1, column=0, columnspan=5, sticky="w", pady=(4, 0))
        ttk.Checkbutton(opts, text="Case sensitive", variable=self.case_var).pack(
            side=tk.LEFT
        )
        ttk.Checkbutton(opts, text="Regular expression", variable=self.regex_var).pack(
            side=tk.LEFT
        )

        ttk.Label(
            self,
            text="Use 'category: text' to limit search. Separate multiple categories with commas.",
        ).grid(row=2, column=0, columnspan=5, sticky="w", pady=(4, 0))

        self.results_box = tk.Listbox(self, height=10)
        self.results_box.grid(row=3, column=0, columnspan=5, sticky="nsew", pady=(8, 0))
        self.results_box.bind("<Double-1>", self._open_selected)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

    # ------------------------------------------------------------------
    def _node_path(self, node) -> str:
        """Return a simple parent chain for *node*."""
        parts = [getattr(node, "user_name", "") or getattr(node, "name", "")]
        parent = node.parents[0] if getattr(node, "parents", None) else None
        visited = set()
        while parent and parent.unique_id not in visited:
            parts.append(getattr(parent, "user_name", "") or getattr(parent, "name", ""))
            visited.add(parent.unique_id)
            parent = parent.parents[0] if parent.parents else None
        return " > ".join(reversed(parts))

    # ------------------------------------------------------------------
    def _obj_label(self, obj) -> str:
        """Return a readable label for *obj*."""
        if isinstance(obj, str):
            return obj
        return getattr(obj, "user_name", "") or getattr(obj, "name", "") or str(obj)

    # ------------------------------------------------------------------
    def _obj_text(self, obj) -> str:
        """Return concatenated text fields for generic searches."""
        if isinstance(obj, str):
            return obj
        parts = []
        for attr in ("user_name", "name", "description", "label", "title"):
            val = getattr(obj, attr, "")
            if isinstance(val, (list, tuple)):
                val = " ".join(str(v) for v in val)
            if val:
                parts.append(str(val))
        return "\n".join(parts)

    # ------------------------------------------------------------------
    def _init_handlers(self) -> None:
        """Initialise search handlers for each supported category."""
        self.handlers: dict[str, callable] = {
            "nodes": self._search_nodes,
            "connections": self._search_connections,
            "failures": self._search_failures,
            "hazards": self._search_hazards,
            "faults": self._search_faults,
            "malfunctions": self._search_malfunctions,
            "failureslist": self._search_failure_list,
            "triggers": self._search_triggers,
            "funcins": self._search_funcins,
        }
        for name, fetcher, opener in EXTRA_CATEGORIES:
            parts = name.split()
            key = parts[0].lower()
            if key in self.handlers and len(parts) > 1:
                key = (parts[0] + parts[1]).lower()
            elif key in self.handlers:
                key = f"{key}{len(self.handlers)}"
            self.handlers[key] = self._make_extra_handler(name, fetcher, opener)

    # ------------------------------------------------------------------
    def _make_extra_handler(self, name: str, fetcher: str, opener: str):
        def handler(regex):
            items = getattr(self.app, fetcher, lambda: [])()
            for item in items:
                text = self._obj_text(item)
                if regex.search(text):
                    prefix = name[:-1] if name.endswith("s") else name
                    label = f"{prefix} - {self._obj_label(item)}"

                    def _open(it=item, meth=opener):
                        func = getattr(self.app, meth, lambda *_: None)
                        try:
                            func(it)
                        except Exception:  # pragma: no cover - best effort
                            func()

                    self._add_result(label, _open)

        return handler

    # ------------------------------------------------------------------
    def _add_result(self, label: str, open_cb) -> None:
        self.results_box.insert(tk.END, label)
        self.results.append({"label": label, "open": open_cb})

    # ------------------------------------------------------------------
    def _search_nodes(self, regex) -> None:
        nodes = getattr(self.app, "get_all_nodes_in_model", lambda: [])()
        for node in nodes:
            text = f"{node.user_name}\n{getattr(node, 'description', '')}"
            if regex.search(text):
                label = (
                    f"{type(node).__name__} ({getattr(node, 'node_type', '')}) - "
                    f"{node.user_name} [{self._node_path(node)}]"
                )
                self._add_result(
                    label,
                    lambda n=node: self.app.open_page_diagram(getattr(n, "original", n)),
                )

    # ------------------------------------------------------------------
    def _search_connections(self, regex) -> None:
        connections = getattr(self.app, "get_all_connections", lambda: [])()
        for conn in connections:
            fields = [
                getattr(conn, "name", ""),
                getattr(conn, "conn_type", ""),
                " ".join(getattr(conn, "guard", []) or []),
            ]
            if regex.search("\n".join(fields)):
                label = f"{type(conn).__name__} - {getattr(conn, 'name', '')}"
                self._add_result(
                    label,
                    lambda c=conn: getattr(self.app, "open_connection", lambda *_: None)(c),
                )

    # ------------------------------------------------------------------
    def _search_failures(self, regex) -> None:
        entries = getattr(self.app, "get_all_fmea_entries", lambda: [])()
        for entry in entries:
            fields = [
                getattr(entry, "user_name", ""),
                getattr(entry, "description", ""),
                getattr(entry, "fmea_effect", ""),
                getattr(entry, "fmea_cause", ""),
            ]
            if regex.search("\n".join(fields)):
                doc_name = ""
                is_fmeda = False
                target_doc = None
                for doc in getattr(self.app, "fmeas", []):
                    if entry in doc.get("entries", []):
                        doc_name = doc.get("name", "FMEA")
                        target_doc = doc
                        break
                else:
                    for doc in getattr(self.app, "fmedas", []):
                        if entry in doc.get("entries", []):
                            doc_name = doc.get("name", "FMEDA")
                            target_doc = doc
                            is_fmeda = True
                            break
                label = (
                    f"{type(entry).__name__} - {entry.user_name or entry.description}"
                    f" [FMEA: {doc_name or 'Global'}]"
                )

                def _open(entry=entry, doc=target_doc, fmeda=is_fmeda):
                    self.app.show_fmea_table(doc, fmeda=fmeda)
                    tree = getattr(self.app, "_fmea_tree", None)
                    node_map = getattr(self.app, "_fmea_node_map", {})
                    if tree and node_map:
                        for iid, node in node_map.items():
                            if node is entry:
                                tree.selection_set(iid)
                                tree.focus(iid)
                                tree.see(iid)
                                break

                self._add_result(label, _open)

    # ------------------------------------------------------------------
    def _search_hazards(self, regex) -> None:
        for hazard in getattr(self.app, "hazards", []):
            if regex.search(hazard):
                label = f"Hazard - {hazard}"
                self._add_result(
                    label,
                    lambda h=hazard: getattr(self.app, "show_hazard_list", lambda *_: None)(),
                )

    # ------------------------------------------------------------------
    def _search_faults(self, regex) -> None:
        for fault in getattr(self.app, "faults", []):
            if regex.search(fault):
                label = f"Fault - {fault}"
                self._add_result(
                    label,
                    lambda f=fault: getattr(self.app, "show_fault_list", lambda *_: None)(),
                )

    # ------------------------------------------------------------------
    def _search_malfunctions(self, regex) -> None:
        malfunc_cb = getattr(
            self.app,
            "show_malfunction_editor",
            getattr(self.app, "show_malfunctions_editor", lambda *_: None),
        )
        for mal in getattr(self.app, "malfunctions", []):
            if regex.search(mal):
                label = f"Malfunction - {mal}"
                self._add_result(label, lambda m=mal: malfunc_cb())

    # ------------------------------------------------------------------
    def _search_failure_list(self, regex) -> None:
        for failure in getattr(self.app, "failures", []):
            if regex.search(failure):
                label = f"Failure - {failure}"
                self._add_result(
                    label,
                    lambda f=failure: getattr(
                        self.app, "show_failure_list", lambda *_: None
                    )(),
                )

    # ------------------------------------------------------------------
    def _search_triggers(self, regex) -> None:
        for tc in getattr(self.app, "triggering_conditions", []):
            if regex.search(tc):
                label = f"Triggering Condition - {tc}"
                self._add_result(
                    label,
                    lambda t=tc: getattr(
                        self.app, "show_triggering_condition_list", lambda *_: None
                    )(),
                )

    # ------------------------------------------------------------------
    def _search_funcins(self, regex) -> None:
        for fi in getattr(self.app, "functional_insufficiencies", []):
            if regex.search(fi):
                label = f"Functional Insufficiency - {fi}"
                self._add_result(
                    label,
                    lambda f=fi: getattr(
                        self.app, "show_functional_insufficiency_list", lambda *_: None
                    )(),
                )

    # ------------------------------------------------------------------
    def _run_search(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            return

        categories = None
        pattern = query
        if ":" in query:
            cat_part, pattern = query.split(":", 1)
            categories = [c.strip().lower() for c in cat_part.split(",") if c.strip()]
            pattern = pattern.strip()

        flags = 0 if self.case_var.get() else re.IGNORECASE
        try:
            regex = re.compile(
                pattern if self.regex_var.get() else re.escape(pattern), flags
            )
        except re.error as exc:  # pragma: no cover - user feedback path
            messagebox.showerror("Search", f"Invalid pattern: {exc}")
            return

        self.results_box.delete(0, tk.END)
        self.results.clear()
        self.current_index = -1

        keys = categories if categories else list(self.handlers.keys())
        for key in keys:
            handler = self.handlers.get(key)
            if handler:
                handler(regex)

        if self.results:
            self.current_index = 0
            self._open_index(0)
        else:
            messagebox.showinfo("Search", "No matches found.")

    # ------------------------------------------------------------------
    def _open_index(self, index: int) -> None:
        self.results_box.select_clear(0, tk.END)
        self.results_box.selection_set(index)
        self.results_box.activate(index)
        self.results_box.see(index)
        result = self.results[index]
        try:  # pragma: no cover - GUI integration
            open_cb = result.get("open")
            if callable(open_cb):
                open_cb()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _find_next(self) -> None:
        if not self.results:
            self._run_search()
            return
        self.current_index = (self.current_index + 1) % len(self.results)
        self._open_index(self.current_index)

    # ------------------------------------------------------------------
    def _find_prev(self) -> None:
        if not self.results:
            self._run_search()
            return
        self.current_index = (self.current_index - 1) % len(self.results)
        self._open_index(self.current_index)

    # ------------------------------------------------------------------
    def _open_selected(self, _event=None) -> None:
        if not self.results_box.curselection():
            return
        self.current_index = self.results_box.curselection()[0]
        self._open_index(self.current_index)
