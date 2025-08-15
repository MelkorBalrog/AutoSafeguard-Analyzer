import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
import json
from config import load_diagram_rules, validate_diagram_rules
from gui import messagebox

class DiagramRulesEditor(tk.Frame):
    """Visual editor for diagram rule configuration."""

    def __init__(self, master, app, config_path: Path | None = None):
        super().__init__(master)
        self.app = app
        self.config_path = Path(
            config_path or Path(__file__).resolve().parents[1] / "config/diagram_rules.json"
        )
        try:
            self.data = load_diagram_rules(self.config_path)
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
        self.tree.heading("value", text="Details")
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
        # Connection rules
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

        # Safety & AI relation rules
        ai_root = self.tree.insert(
            "", "end", "safety_ai_relation_rules", text="safety_ai_relation_rules"
        )
        ai_rules = self.data.get("safety_ai_relation_rules", {})
        if not ai_rules:
            self.tree.insert(ai_root, "end", "no_ai_rules", text="(no rules defined)")
        for rel, sources in sorted(ai_rules.items()):
            r_id = self.tree.insert(ai_root, "end", f"rel|{rel}", text=rel)
            for src, dests in sorted(sources.items()):
                item_id = f"sar|{rel}|{src}"
                dest_text = ", ".join(sorted(dests))
                self.tree.insert(r_id, "end", item_id, text=src, values=(dest_text,))

        # Requirement generation rules
        req_root = self.tree.insert(
            "", "end", "requirement_rules", text="requirement_rules"
        )
        req_rules = self.data.get("requirement_rules", {})
        if not req_rules:
            self.tree.insert(req_root, "end", "no_req_rules", text="(no rules defined)")
        for label, info in sorted(req_rules.items()):
            parts = [info.get("action", "")]
            subject = info.get("subject")
            if subject:
                parts.append(f"subject: {subject}")
            if info.get("constraint"):
                parts.append("constraint")
            self.tree.insert(
                req_root,
                "end",
                f"req|{label}",
                text=label,
                values=(", ".join(parts),),
            )

        # Node roles
        role_root = self.tree.insert("", "end", "node_roles", text="node_roles")
        roles = self.data.get("node_roles", {})
        if not roles:
            self.tree.insert(role_root, "end", "no_node_roles", text="(no roles defined)")
        for node, role in sorted(roles.items()):
            self.tree.insert(
                role_root, "end", f"role|{node}", text=node, values=(role,)
            )

    def _on_select(self, _event=None):
        item = self.tree.selection()
        if not item:
            return
        item = item[0]
        if item.startswith("rule|"):
            _, diag, conn, src = item.split("|", 3)
            self._draw_rule(diag, conn, src)
        elif item.startswith("sar|"):
            _, rel, src = item.split("|", 2)
            self._draw_rule(None, rel, src)
        else:
            self.canvas.delete("all")

    def _edit_item(self, _event=None):
        item = self.tree.focus()
        if item.startswith("rule|"):
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
        elif item.startswith("sar|"):
            _, rel, src = item.split("|", 2)
            cur = self.data["safety_ai_relation_rules"][rel][src]
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
            self.data["safety_ai_relation_rules"][rel][src] = dest_list
            self.tree.set(item, "value", ", ".join(dest_list))
            self._draw_rule(None, rel, src)
        elif item.startswith("req|"):
            _, label = item.split("|", 1)
            rule = self.data.setdefault("requirement_rules", {}).get(label, {})
            action = simpledialog.askstring(
                "Edit Action",
                f"Action for {label}",
                initialvalue=rule.get("action", ""),
                parent=self,
            )
            if action is None:
                return
            subject = simpledialog.askstring(
                "Edit Subject",
                f"Subject for {label} (optional)",
                initialvalue=rule.get("subject", ""),
                parent=self,
            )
            if subject is None:
                return
            constraint = simpledialog.askstring(
                "Constraint",
                f"Is {label} a constraint? (true/false)",
                initialvalue=str(rule.get("constraint", False)).lower(),
                parent=self,
            )
            if constraint is None:
                return
            new_rule = {"action": action.strip()}
            if subject.strip():
                new_rule["subject"] = subject.strip()
            if constraint.strip().lower() in {"true", "1", "yes"}:
                new_rule["constraint"] = True
            self.data.setdefault("requirement_rules", {})[label] = new_rule
            parts = [new_rule.get("action", "")]
            if new_rule.get("subject"):
                parts.append(f"subject: {new_rule['subject']}")
            if new_rule.get("constraint"):
                parts.append("constraint")
            self.tree.set(item, "value", ", ".join(parts))
        elif item.startswith("role|"):
            _, node = item.split("|", 1)
            cur = self.data.setdefault("node_roles", {}).get(node, "")
            new_role = simpledialog.askstring(
                "Edit Role",
                f"Role for {node}",
                initialvalue=cur,
                parent=self,
            )
            if new_role is None:
                return
            self.data.setdefault("node_roles", {})[node] = new_role
            self.tree.set(item, "value", new_role)
        else:
            return

    def _draw_rule(self, diagram, connection, source):
        self.canvas.delete("all")
        if diagram is None:
            dests = self.data["safety_ai_relation_rules"][connection].get(source, [])
            title = connection
        else:
            dests = self.data["connection_rules"][diagram][connection].get(source, [])
            title = f"{diagram} - {connection}"
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
        self.canvas.create_text((src_x + dest_x) / 2, 20, text=title)

    def save(self):
        try:
            validate_diagram_rules(self.data)
        except ValueError as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror("Diagram Rules", f"Invalid configuration:\n{exc}")
            return
        self.config_path.write_text(json.dumps(self.data, indent=2) + "\n")
        if hasattr(self.app, "reload_config"):
            self.app.reload_config()
        messagebox.showinfo("Diagram Rules", "Configuration saved")
        self._populate_tree()
