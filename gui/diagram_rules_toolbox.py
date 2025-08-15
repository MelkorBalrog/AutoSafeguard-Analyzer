import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
import json
from config_loader import load_json_with_comments
from gui import messagebox

class DiagramRulesEditor(tk.Frame):
    """Visual editor for diagram rule configuration."""

    def __init__(self, master, app, config_path: Path | None = None):
        super().__init__(master)
        self.app = app
        self.config_path = Path(
            config_path or Path(__file__).resolve().parents[1] / "diagram_rules.json"
        )
        try:
            self.data = load_json_with_comments(self.config_path)
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror(
                "Diagram Rules", f"Failed to load configuration:\n{exc}"
            )
            self.data = {"connection_rules": {}}

        # Make both columns expandable so the tree and canvas resize with window
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Container for the rule tree so we can attach scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("value",), show="tree headings")
        self.tree.heading("#0", text="Item")
        self.tree.heading("value", text="Allowed Targets")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._edit_item)
        self.tree.column("#0", width=200, stretch=True)
        self.tree.column("value", width=200, stretch=True)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Add scrollbars to the treeview
        ybar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")

        self.canvas = tk.Canvas(self, background="white")
        self.canvas.grid(row=0, column=1, sticky="nsew")

        btn = ttk.Button(self, text="Save", command=self.save)
        btn.grid(row=1, column=1, sticky="e", padx=4, pady=4)

        self._populate_tree()

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children(""))
        root = self.tree.insert("", "end", "connection_rules", text="connection_rules")
        rules = self.data.get("connection_rules", {})
        if not rules:
            self.tree.insert(root, "end", "no_rules", text="(no rules defined)")
        for diag, conns in sorted(rules.items()):
            d_id = self.tree.insert(root, "end", f"diag|{diag}", text=diag)
            for conn, sources in sorted(conns.items()):
                c_id = self.tree.insert(d_id, "end", f"conn|{diag}|{conn}", text=conn)
                for src, dests in sorted(sources.items()):
                    item_id = f"rule|{diag}|{conn}|{src}"
                    dest_text = ", ".join(sorted(dests))
                    self.tree.insert(c_id, "end", item_id, text=src, values=(dest_text,))
        # Ensure all top-level items are visible
        self.tree.item(root, open=True)
        for child in self.tree.get_children(root):
            self.tree.item(child, open=True)

    def _on_select(self, _event=None):
        item = self.tree.selection()
        if not item:
            return
        item = item[0]
        if item.startswith("rule|"):
            _, diag, conn, src = item.split("|", 3)
            self._draw_rule(diag, conn, src)
        else:
            self.canvas.delete("all")

    def _edit_item(self, _event=None):
        item = self.tree.focus()
        if not item.startswith("rule|"):
            return
        _, diag, conn, src = item.split("|", 3)
        cur = self.data["connection_rules"][diag][conn][src]
        initial = ", ".join(cur)
        new_val = simpledialog.askstring(
            "Edit Targets",
            f"Allowed targets for {src}",
            initialvalue=initial,
            parent=self,
        )
        if new_val is None:
            return
        dest_list = [s.strip() for s in new_val.split(",") if s.strip()]
        self.data["connection_rules"][diag][conn][src] = dest_list
        self.tree.set(item, "value", ", ".join(dest_list))
        self._draw_rule(diag, conn, src)

    def _draw_rule(self, diagram, connection, source):
        self.canvas.delete("all")
        dests = self.data["connection_rules"][diagram][connection].get(source, [])
        w = int(self.canvas.winfo_width()) or 400
        h = int(self.canvas.winfo_height()) or 300
        src_x, src_y = 80, h // 2
        self.canvas.create_rectangle(src_x - 40, src_y - 20, src_x + 40, src_y + 20, fill="#eef")
        self.canvas.create_text(src_x, src_y, text=source)
        dest_x = 300
        spacing = 60
        if dests:
            start_y = src_y - spacing * (len(dests) - 1) / 2
        else:
            start_y = src_y
        for i, dst in enumerate(dests):
            y = start_y + i * spacing
            self.canvas.create_rectangle(dest_x - 40, y - 20, dest_x + 40, y + 20, fill="#efe")
            self.canvas.create_text(dest_x, y, text=dst)
            self.canvas.create_line(src_x + 40, src_y, dest_x - 40, y, arrow=tk.LAST)
        self.canvas.create_text((src_x + dest_x) / 2, 20, text=f"{diagram} - {connection}")

    def save(self):
        self.config_path.write_text(json.dumps(self.data, indent=2) + "\n")
        if hasattr(self.app, "reload_config"):
            self.app.reload_config()
        messagebox.showinfo("Diagram Rules", "Configuration saved")
        self._populate_tree()
