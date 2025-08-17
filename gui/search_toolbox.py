import tkinter as tk
from tkinter import ttk
import re
from sysml.sysml_repository import SysMLRepository


def search_repository(repo: SysMLRepository, pattern: str, *, case_sensitive: bool = False,
                      use_regex: bool = False, in_names: bool = True,
                      in_descriptions: bool = True):
    """Return list of repo items matching *pattern*.

    Parameters
    ----------
    repo: SysMLRepository
        Repository to search.
    pattern: str
        Text or regular expression to look for.
    case_sensitive: bool
        Whether matching should be case sensitive.
    use_regex: bool
        Interpret *pattern* as a regular expression.
    in_names: bool
        Search element and diagram names.
    in_descriptions: bool
        Search element properties["description"] and diagram descriptions.
    """
    results = []
    if not pattern:
        return results
    flags = 0 if case_sensitive else re.IGNORECASE
    if use_regex:
        try:
            regex = re.compile(pattern, flags)
        except re.error:
            return results
        matcher = lambda text: bool(regex.search(text))
    else:
        comp = pattern if case_sensitive else pattern.lower()
        def matcher(text):
            target = text if case_sensitive else text.lower()
            return comp in target
    for elem_id, elem in repo.elements.items():
        texts = []
        if in_names:
            texts.append(elem.name or "")
        if in_descriptions:
            texts.append(elem.properties.get("description", ""))
        if any(matcher(t) for t in texts if t):
            results.append(("element", elem_id, elem.display_name()))
    for diag_id, diag in repo.diagrams.items():
        texts = []
        if in_names:
            texts.append(diag.name or "")
        if in_descriptions:
            texts.append(diag.description or "")
        if any(matcher(t) for t in texts if t):
            results.append(("diagram", diag_id, diag.display_name()))
    return results


class SearchToolbox(tk.Frame):
    """Simple toolbox providing repository search similar to IDE search."""

    def __init__(self, master=None, app=None):
        super().__init__(master)
        self.app = app
        self.repo = SysMLRepository.get_instance()

        opts = tk.Frame(self)
        opts.pack(fill=tk.X, padx=4, pady=4)

        tk.Label(opts, text="Find:").pack(side=tk.LEFT)
        self.pattern_var = tk.StringVar()
        tk.Entry(opts, textvariable=self.pattern_var, width=30).pack(side=tk.LEFT, padx=4)
        tk.Button(opts, text="Search", command=self.perform_search).pack(side=tk.LEFT)

        self.case_var = tk.BooleanVar()
        self.regex_var = tk.BooleanVar()
        self.names_var = tk.BooleanVar(value=True)
        self.desc_var = tk.BooleanVar(value=True)

        tk.Checkbutton(opts, text="Match case", variable=self.case_var).pack(side=tk.LEFT, padx=4)
        tk.Checkbutton(opts, text="Regex", variable=self.regex_var).pack(side=tk.LEFT)
        tk.Checkbutton(opts, text="Names", variable=self.names_var).pack(side=tk.LEFT, padx=4)
        tk.Checkbutton(opts, text="Descriptions", variable=self.desc_var).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self, columns=("type", "name"), show="headings")
        self.tree.heading("type", text="Type")
        self.tree.heading("name", text="Name")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def perform_search(self):
        pattern = self.pattern_var.get()
        results = search_repository(
            self.repo,
            pattern,
            case_sensitive=self.case_var.get(),
            use_regex=self.regex_var.get(),
            in_names=self.names_var.get(),
            in_descriptions=self.desc_var.get(),
        )
        self.tree.delete(*self.tree.get_children())
        for typ, _id, name in results:
            self.tree.insert("", tk.END, values=(typ, name))
