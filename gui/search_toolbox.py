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
        # each result is a mapping with keys: 'label' and 'open'
        self.results: list[dict[str, object]] = []

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(frame, text="Find:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.search_var)
        entry.grid(row=0, column=1, sticky="ew")
        entry.focus_set()

        btn = ttk.Button(frame, text="Search", command=self._run_search)
        btn.grid(row=0, column=2, padx=(4, 0))

        opts = ttk.Frame(frame)
        opts.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))
        ttk.Checkbutton(opts, text="Case sensitive", variable=self.case_var).pack(
            side=tk.LEFT
        )
        ttk.Checkbutton(opts, text="Regular expression", variable=self.regex_var).pack(
            side=tk.LEFT
        )

        self.results_box = tk.Listbox(frame, height=10)
        self.results_box.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        self.results_box.bind("<Double-1>", self._open_selected)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

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

        # --- search fault tree / GSN nodes
        for node in getattr(self.app, "get_all_nodes_in_model", lambda: [])():
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

        # --- search FMEA/FMDA entries
        for entry in getattr(self.app, "get_all_fmea_entries", lambda: [])():
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

    # ------------------------------------------------------------------
    def _open_selected(self, _event=None) -> None:
        if not self.results_box.curselection():
            return
        result = self.results[self.results_box.curselection()[0]]
        try:  # pragma: no cover - GUI integration
            open_cb = result.get("open")
            if callable(open_cb):
                open_cb()
        except Exception:
            pass
