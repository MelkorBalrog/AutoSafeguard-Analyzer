from .core import *

class DecompositionDialog(simpledialog.Dialog):
    def __init__(self, parent, asil):
        self.asil = asil
        super().__init__(parent, title="Requirement Decomposition")

    def body(self, master):
        ttk.Label(master, text="Select decomposition scheme:").pack(padx=5, pady=5)
        schemes = ASIL_DECOMP_SCHEMES.get(self.asil, [])
        self.scheme_var = tk.StringVar()
        options = [f"{self.asil} -> {a}+{b}" for a, b in schemes] or ["None"]
        self.combo = ttk.Combobox(master, textvariable=self.scheme_var, values=options, state="readonly")
        if options:
            self.combo.current(0)
        self.combo.pack(padx=5, pady=5)
        return self.combo

    def apply(self):
        val = self.scheme_var.get()
        if "->" in val:
            parts = val.split("->", 1)[1].split("+")
            self.result = (parts[0].strip(), parts[1].strip())
        else:
            self.result = None
