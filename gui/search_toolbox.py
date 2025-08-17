"""Search toolbox for finding objects within the AutoML model."""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

from gui import messagebox


class SearchToolbox(tk.Toplevel):
    """Provide text-based search across model objects.

    Results show the object's class and origin.  Double-clicking a match
    navigates to the corresponding diagram or table entry.
    """

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.title("Search")

        self.search_var = tk.StringVar()
        self.case_var = tk.BooleanVar(value=False)
        self.regex_var = tk.BooleanVar(value=False)
        self.nodes_var = tk.BooleanVar(value=True)
        self.connections_var = tk.BooleanVar(value=True)
        self.failures_var = tk.BooleanVar(value=True)
        self.hazards_var = tk.BooleanVar(value=True)
        # each result is a mapping with keys: 'label' and 'open'
        self.results: list[dict[str, object]] = []
        self.current_index: int = -1

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(frame, text="Find:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.search_var)
        entry.grid(row=0, column=1, sticky="ew")
        entry.focus_set()

        ttk.Button(frame, text="Find", command=self._run_search).grid(
            row=0, column=2, padx=(4, 0)
        )
        ttk.Button(frame, text="Next", command=self._find_next).grid(
            row=0, column=3, padx=(4, 0)
        )
        ttk.Button(frame, text="Prev", command=self._find_prev).grid(
            row=0, column=4, padx=(4, 0)
        )

        opts = ttk.Frame(frame)
        opts.grid(row=1, column=0, columnspan=5, sticky="w", pady=(4, 0))
        ttk.Checkbutton(opts, text="Case sensitive", variable=self.case_var).pack(
            side=tk.LEFT
        )
        ttk.Checkbutton(opts, text="Regular expression", variable=self.regex_var).pack(
            side=tk.LEFT
        )

        sources = ttk.Frame(frame)
        sources.grid(row=2, column=0, columnspan=5, sticky="w", pady=(4, 0))
        ttk.Checkbutton(sources, text="Nodes", variable=self.nodes_var).pack(side=tk.LEFT)
        ttk.Checkbutton(sources, text="Connections", variable=self.connections_var).pack(side=tk.LEFT)
        ttk.Checkbutton(sources, text="Failures", variable=self.failures_var).pack(side=tk.LEFT)
        ttk.Checkbutton(sources, text="Hazards", variable=self.hazards_var).pack(side=tk.LEFT)

        self.results_box = tk.Listbox(frame, height=10)
        self.results_box.grid(row=3, column=0, columnspan=5, sticky="nsew", pady=(8, 0))
        self.results_box.bind("<Double-1>", self._open_selected)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

        self.transient(master)
        self.grab_set()

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
    def _run_search(self) -> None:
        pattern = self.search_var.get().strip()
        if not pattern:
            return
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

        if self.nodes_var.get():
            nodes = getattr(self.app, "get_all_nodes_in_model", lambda: [])()
            for node in nodes:
                text = f"{node.user_name}\n{getattr(node, 'description', '')}"
                if regex.search(text):
                    label = (
                        f"{type(node).__name__} ({getattr(node, 'node_type', '')}) - "
                        f"{node.user_name} [{self._node_path(node)}]"
                    )
                    self.results_box.insert(tk.END, label)
                    self.results.append(
                        {
                            "label": label,
                            "open": lambda n=node: self.app.open_page_diagram(
                                getattr(n, "original", n)
                            ),
                        }
                    )

        if self.connections_var.get():
            connections = getattr(self.app, "get_all_connections", lambda: [])()
            for conn in connections:
                fields = [
                    getattr(conn, "name", ""),
                    getattr(conn, "conn_type", ""),
                    " ".join(getattr(conn, "guard", []) or []),
                ]
                if regex.search("\n".join(fields)):
                    label = f"{type(conn).__name__} - {getattr(conn, 'name', '')}"
                    self.results_box.insert(tk.END, label)
                    self.results.append(
                        {
                            "label": label,
                            "open": lambda c=conn: getattr(
                                self.app, "open_connection", lambda *_: None
                            )(c),
                        }
                    )

        if self.failures_var.get():
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
                    self.results_box.insert(tk.END, label)

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

                    self.results.append({"label": label, "open": _open})

        if self.hazards_var.get():
            for hazard in getattr(self.app, "hazards", []):
                if regex.search(hazard):
                    label = f"Hazard - {hazard}"
                    self.results_box.insert(tk.END, label)
                    self.results.append(
                        {
                            "label": label,
                            "open": lambda h=hazard: getattr(
                                self.app, "show_hazard_list", lambda *_: None
                            )(),
                        }
                    )

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
