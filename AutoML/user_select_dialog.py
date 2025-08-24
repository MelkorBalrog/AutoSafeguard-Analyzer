from .core import *

class UserSelectDialog(simpledialog.Dialog):
    """Prompt to select a user from a list."""

    def __init__(self, parent, users, last_user=""):
        self._users = users
        self._last_user = last_user
        super().__init__(parent, title="Select User")

    def body(self, master):
        self.resizable(False, False)
        ttk.Label(master, text="User:").grid(row=0, column=0, sticky="e")
        names = list(self._users.keys()) + ["New User..."]
        self.name_var = tk.StringVar(value=self._last_user if self._last_user in self._users else names[0])
        self.name_cb = ttk.Combobox(master, textvariable=self.name_var, values=names, state="readonly")
        self.name_cb.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(master, text="Email:").grid(row=1, column=0, sticky="e")
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(master, textvariable=self.email_var, state="disabled")
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        self.name_cb.bind("<<ComboboxSelected>>", self._on_select)
        self._on_select()
        return self.name_cb

    def _on_select(self, event=None):
        name = self.name_var.get()
        if name in self._users:
            self.email_var.set(self._users[name])
            self.email_entry.config(state="disabled")
        else:
            self.email_var.set("")
            self.email_entry.config(state="normal")

    def apply(self):
        self.result = (self.name_var.get(), self.email_var.get().strip())

    def buttonbox(self):
        box = ttk.Frame(self)
        apply_purplish_button_style()
        ttk.Button(
            box,
            text="OK",
            width=10,
            command=self.ok,
            style="Purple.TButton",
        ).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(
            box,
            text="Cancel",
            width=10,
            command=self.cancel,
            style="Purple.TButton",
        ).pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()
