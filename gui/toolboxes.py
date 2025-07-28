# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import csv
import copy
import textwrap
import uuid

from gui.tooltip import ToolTip
from analysis.models import (
    ReliabilityComponent,
    ReliabilityAnalysis,
    HazopEntry,
    HaraEntry,
    HazopDoc,
    HaraDoc,
    FI2TCDoc,
    TC2FIDoc,
    QUALIFICATIONS,
    COMPONENT_ATTR_TEMPLATES,
    RELIABILITY_MODELS,
    PASSIVE_QUAL_FACTORS,
    component_fit_map,
    calc_asil,
    global_requirements,
    REQUIREMENT_TYPE_OPTIONS,
    ASIL_LEVEL_OPTIONS,
    CAL_LEVEL_OPTIONS,
)
from analysis.fmeda_utils import compute_fmeda_metrics
from analysis.constants import CHECK_MARK, CROSS_MARK


def configure_table_style(style_name: str, rowheight: int = 60) -> None:
    """Apply a consistent look to ttk.Treeview widgets used in analysis tables."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    border_opts = {"bordercolor": "black", "borderwidth": 1, "relief": "solid"}
    style.configure(
        style_name,
        font=("Segoe UI", 10),
        rowheight=rowheight,
        borderwidth=1,
        relief="solid",
        bordercolor="black",
    )
    style.configure(
        f"{style_name}.Heading",
        font=("Segoe UI", 10, "bold"),
        background="#d0d0d0",
        borderwidth=1,
        relief="raised",
        bordercolor="black",
    )


class EditableTreeview(ttk.Treeview):
    """Treeview with in-place cell editing support.

    Parameters
    ----------
    column_options : dict[str, list[str]]
        Mapping of column name to list of single-select options.
    edit_callback : callable
        Called with ``(row_index, column_name, new_value)`` after an edit.
    requirement_columns : dict[str, str]
        Mapping of column name to requirement type. When editing these columns
        a requirement selection dialog allowing multiple selections is shown.
    """
    def __init__(self, master=None, *, column_options=None, edit_callback=None, requirement_columns=None, **kwargs):
        super().__init__(master, **kwargs)
        self._col_options = column_options or {}
        self._edit_cb = edit_callback
        self._req_cols = requirement_columns or {}
        self._edit_widget = None
        self.bind("<Double-1>", self._begin_edit, add="+")

    def _begin_edit(self, event):
        if self._edit_widget:
            return
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            return
        rowid = self.identify_row(event.y)
        col = self.identify_column(event.x)
        if not rowid or not col:
            return
        col_index = int(col.replace("#", "")) - 1
        col_name = self.cget("columns")[col_index]
        value = self.set(rowid, col_name)
        req_type = self._req_cols.get(col_name)
        if req_type is not None:
            current = [v for v in map(str.strip, value.split(";")) if v]
            dlg = _SelectRequirementsDialog(self, req_type=req_type, initial=current)
            if getattr(dlg, "result", None):
                ids = [s.split("]",1)[0][1:] for s in dlg.result]
                new_val = ";".join(ids)
                self.set(rowid, col_name, new_val)
                if self._edit_cb:
                    row_index = self.index(rowid)
                    self._edit_cb(row_index, col_name, new_val)
            return
        x, y, w, h = self.bbox(rowid, col)
        opts = self._col_options.get(col_name)
        var = tk.StringVar(value=value)
        if opts:
            widget = ttk.Combobox(self, textvariable=var, values=opts, state="readonly")
        else:
            widget = tk.Entry(self, textvariable=var)
        widget.place(x=x, y=y, width=w, height=h)
        widget.focus_set()
        def save(event=None):
            self.set(rowid, col_name, var.get())
            widget.destroy()
            self._edit_widget = None
            if self._edit_cb:
                row_index = self.index(rowid)
                self._edit_cb(row_index, col_name, var.get())
        widget.bind("<Return>", save)
        widget.bind("<FocusOut>", save)
        self._edit_widget = widget
def stripe_rows(tree: ttk.Treeview) -> None:
    """Apply alternating background colors to rows for visual separation."""
    tree.tag_configure("even", background="#f0f0f0")
    tree.tag_configure("odd", background="#ffffff")
    for i, item in enumerate(tree.get_children("")):
        tree.item(item, tags=("even" if i % 2 else "odd",))


def _total_fit_from_boms(boms):
    """Return the aggregated FIT of all components in ``boms``.

    Each element of ``boms`` is a list of :class:`ReliabilityComponent` objects.
    The stored ``fit`` values of the components are used so pre-calculated
    analyses can be combined without a mission profile.
    """

    total = 0.0
    for bom in boms:
        total += sum(component_fit_map(bom).values())
    return total


def _wrap_val(val, width=30):
    """Return text wrapped value for tree view cells."""
    if val is None:
        return ""
    return textwrap.fill(str(val), width)


class _RequirementDialog(simpledialog.Dialog):
    """Simple dialog to create or edit a requirement."""

    def __init__(self, parent, req=None, req_type="functional modification"):
        self.req_type = req_type
        self.req = req or {}
        super().__init__(parent, title="Requirement")

    def body(self, master):
        ttk.Label(master, text="ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.id_var = tk.StringVar(value=self.req.get("id", ""))
        tk.Entry(master, textvariable=self.id_var, width=20).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(master, text="Text:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.text_var = tk.Entry(master, width=40)
        self.text_var.insert(0, self.req.get("text", ""))
        self.text_var.grid(row=1, column=1, padx=5, pady=5)
        return self.text_var

    def apply(self):
        rid = self.id_var.get().strip() or str(uuid.uuid4())
        self.result = {
            "id": rid,
            "custom_id": rid,
            "req_type": self.req_type,
            "text": self.text_var.get().strip(),
            "asil": self.req.get("asil", "QM"),
            "cal": self.req.get("cal", ""),
            "status": "draft",
            "parent_id": self.req.get("parent_id", ""),
        }


class _SelectRequirementsDialog(simpledialog.Dialog):
    """Dialog to choose one or more existing requirements of a given type."""

    def __init__(self, parent, req_type="functional modification", initial=None):
        self.selected = initial or []
        self.req_type = req_type
        super().__init__(parent, title="Select Requirements")

    def body(self, master):
        self.lb = tk.Listbox(master, selectmode="extended", height=8, exportselection=False)
        for req in global_requirements.values():
            if req.get("req_type") == self.req_type:
                self.lb.insert(tk.END, f"[{req['id']}] {req['text']}")
        self.lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for idx, req in enumerate(global_requirements.values()):
            if req.get("req_type") == self.req_type and req["id"] in self.selected:
                self.lb.selection_set(idx)
        return self.lb

    def apply(self):
        self.result = [self.lb.get(i) for i in self.lb.curselection()]


class _SelectTriggeringConditionsDialog(simpledialog.Dialog):
    """Dialog to choose one or more existing triggering conditions."""

    def __init__(self, parent, names):
        self.names = names
        self.selected = []
        super().__init__(parent, title="Select Triggering Conditions")

    def body(self, master):
        self.lb = tk.Listbox(master, selectmode="extended", height=8, exportselection=False)
        for name in self.names:
            self.lb.insert(tk.END, name)
        self.lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return self.lb

    def apply(self):
        self.result = [self.lb.get(i) for i in self.lb.curselection()]


class _SelectFunctionsDialog(simpledialog.Dialog):
    """Dialog to choose one or more existing functions."""

    def __init__(self, parent, names):
        self.names = names
        super().__init__(parent, title="Select Functions")

    def body(self, master):
        self.lb = tk.Listbox(master, selectmode="extended", height=8, exportselection=False)
        for name in sorted(self.names):
            self.lb.insert(tk.END, name)
        self.lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return self.lb

    def apply(self):
        self.result = [self.lb.get(i) for i in self.lb.curselection()]


class _SelectHazardsDialog(simpledialog.Dialog):
    """Dialog to choose one or more existing hazards."""

    def __init__(self, parent, names):
        self.names = names
        super().__init__(parent, title="Select Hazards")

    def body(self, master):
        self.lb = tk.Listbox(master, selectmode="extended", height=8, exportselection=False)
        for name in sorted(self.names):
            self.lb.insert(tk.END, name)
        self.lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return self.lb

    def apply(self):
        self.result = [self.lb.get(i) for i in self.lb.curselection()]


class _SelectFIsDialog(simpledialog.Dialog):
    """Dialog to choose one or more existing functional insufficiencies."""

    def __init__(self, parent, names):
        self.names = names
        super().__init__(parent, title="Select Functional Insufficiencies")

    def body(self, master):
        self.lb = tk.Listbox(master, selectmode="extended", height=8, exportselection=False)
        for name in sorted(self.names):
            self.lb.insert(tk.END, name)
        self.lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return self.lb

    def apply(self):
        self.result = [self.lb.get(i) for i in self.lb.curselection()]


class ReliabilityWindow(tk.Frame):
    def __init__(self, master, app):
        if isinstance(master, tk.Toplevel):
            container = master
        else:
            container = master
        super().__init__(container)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("Reliability Analysis")
            master.geometry("600x400")
            self.pack(fill=tk.BOTH, expand=True)
        self.components = []

        std_lbl = ttk.Label(self, text="Standard:")
        std_lbl.pack(anchor="w")
        ToolTip(std_lbl, "Choose the reliability standard used for FIT calculations.")
        self.standard_var = tk.StringVar(value="IEC 62380")
        std_cb = ttk.Combobox(
            self,
            textvariable=self.standard_var,
            values=["IEC 62380", "SN 29500"],
            state="readonly",
        )
        std_cb.pack(anchor="w")
        ToolTip(std_cb, "Values are applied when calculating component failure rates.")

        mp_lbl = ttk.Label(self, text="Mission Profile:")
        mp_lbl.pack(anchor="w")
        ToolTip(mp_lbl, "Select operating conditions that influence FIT values.")
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            self,
            textvariable=self.profile_var,
            values=[mp.name for mp in app.mission_profiles],
            state="readonly",
        )
        self.profile_combo.pack(anchor="w", fill="x")
        ToolTip(
            self.profile_combo, "Mission profiles define temperature and usage factors."
        )

        ttk.Label(self, text="Analysis:").pack(anchor="w")
        self.analysis_var = tk.StringVar()
        self.analysis_combo = ttk.Combobox(
            self,
            textvariable=self.analysis_var,
            state="readonly",
        )
        self.analysis_combo.pack(anchor="w", fill="x")
        self.analysis_combo.bind("<<ComboboxSelected>>", self.load_selected_analysis)
        self.refresh_analysis_list()

        configure_table_style("Reliability.Treeview")
        column_opts = {
            "type": list(COMPONENT_ATTR_TEMPLATES.keys()),
            "qualification": QUALIFICATIONS,
        }
        self.tree = EditableTreeview(
            self,
            columns=("name", "type", "qty", "fit", "qualification"),
            show="headings",
            style="Reliability.Treeview",
            column_options=column_opts,
            edit_callback=self.on_cell_edit,
        )
        for col in ("name", "type", "qty", "fit", "qualification"):
            heading = "Qualification" if col == "qualification" else col.capitalize()
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=120 if col == "qualification" else 100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.show_formula)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X)
        load_btn = ttk.Button(btn_frame, text="Load CSV", command=self.load_csv)
        load_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(load_btn, "Import components from a CSV Bill of Materials.")
        add_btn = ttk.Button(
            btn_frame, text="Add Component", command=self.add_component
        )
        add_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(add_btn, "Create a new component entry manually.")
        cfg_btn = ttk.Button(
            btn_frame, text="Configure Component", command=self.configure_component
        )
        cfg_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(cfg_btn, "Edit parameters of the selected component.")
        calc_btn = ttk.Button(
            btn_frame, text="Calculate FIT", command=self.calculate_fit
        )
        calc_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(
            calc_btn,
            "Compute total FIT rate using the selected model and mission profile.",
        )
        save_btn = ttk.Button(
            btn_frame, text="Save Analysis", command=self.save_analysis
        )
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(save_btn, "Store the current analysis in the project file.")
        load_an_btn = ttk.Button(
            btn_frame, text="Load Analysis", command=self.load_analysis
        )
        load_an_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(load_an_btn, "Reload a previously saved reliability analysis.")
        del_btn = ttk.Button(
            btn_frame, text="Delete Analysis", command=self.delete_analysis
        )
        del_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(del_btn, "Remove the selected analysis from the project.")
        self.formula_label = ttk.Label(self, text="")
        self.formula_label.pack(anchor="w", padx=5, pady=5)

    def add_component(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Component")
        ttk.Label(dialog, text="Name").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Type").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        type_var = tk.StringVar(value="capacitor")
        type_cb = ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=list(COMPONENT_ATTR_TEMPLATES.keys()),
            state="readonly",
        )
        type_cb.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Quantity").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        qty_var = tk.IntVar(value=1)
        ttk.Entry(dialog, textvariable=qty_var).grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Qualification").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        qual_var = tk.StringVar(value="None")
        ttk.Combobox(
            dialog, textvariable=qual_var, values=QUALIFICATIONS, state="readonly"
        ).grid(row=3, column=1, padx=5, pady=5)
        passive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Passive", variable=passive_var).grid(
            row=4, column=0, columnspan=2, pady=5
        )

        attr_frame = ttk.Frame(dialog)
        attr_frame.grid(row=5, column=0, columnspan=2)
        attr_vars = {}

        def refresh_attr_fields(*_):
            for child in attr_frame.winfo_children():
                child.destroy()
            attr_vars.clear()
            template = COMPONENT_ATTR_TEMPLATES.get(type_var.get(), {})
            for i, (k, v) in enumerate(template.items()):
                ttk.Label(attr_frame, text=k).grid(
                    row=i, column=0, padx=5, pady=5, sticky="e"
                )
                if isinstance(v, list):
                    var = tk.StringVar(value=v[0])
                    ttk.Combobox(
                        attr_frame, textvariable=var, values=v, state="readonly"
                    ).grid(row=i, column=1, padx=5, pady=5)
                else:
                    var = tk.StringVar(value=str(v))
                    ttk.Entry(attr_frame, textvariable=var).grid(
                        row=i, column=1, padx=5, pady=5
                    )
                attr_vars[k] = var

        type_cb.bind("<<ComboboxSelected>>", refresh_attr_fields)
        refresh_attr_fields()

        def ok():
            comp = ReliabilityComponent(
                name_var.get(),
                type_var.get(),
                qty_var.get(),
                {},
                qual_var.get(),
                is_passive=passive_var.get(),
            )
            for k, var in attr_vars.items():
                comp.attributes[k] = var.get()
            self.components.append(comp)
            self.refresh_tree()
            dialog.destroy()

        ttk.Button(dialog, text="Add", command=ok).grid(
            row=6, column=0, columnspan=2, pady=5
        )
        dialog.grab_set()
        dialog.wait_window()

    def show_formula(self, event=None):
        sel = self.tree.focus()
        if not sel:
            self.formula_label.config(text="")
            return
        idx = self.tree.index(sel)
        if idx >= len(self.components):
            return
        comp = self.components[idx]
        std = self.standard_var.get()
        info = RELIABILITY_MODELS.get(std, {}).get(comp.comp_type)
        if info:
            self.formula_label.config(text=f"Formula: {info['text']}")
        else:
            self.formula_label.config(text="Formula: N/A")

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for comp in self.components:
            self.tree.insert(
                "",
                "end",
                values=(
                    comp.name,
                    comp.comp_type,
                    comp.quantity,
                    f"{comp.fit:.2f}",
                    comp.qualification,
                ),
            )
        self.profile_combo.config(values=[mp.name for mp in self.app.mission_profiles])
        # keep application level components updated so property dialogs see them
        self.app.reliability_components = list(self.components)

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        if row >= len(self.components):
            return
        comp = self.components[row]
        if column == "name":
            comp.name = value
        elif column == "type":
            comp.comp_type = value
        elif column == "qty":
            try:
                comp.quantity = int(value)
            except ValueError:
                pass
        elif column == "qualification":
            comp.qualification = value
        self.refresh_tree()

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        self.components.clear()
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            mapping = self.ask_mapping(fields)
            if not mapping:
                return
            for row in reader:
                try:
                    name = row.get(mapping["name"], "")
                    ctype = row.get(mapping["type"], "")
                    qty = int(row.get(mapping["qty"], 1) or 1)
                    qual = (
                        row.get(mapping.get("qualification"), "")
                        if mapping.get("qualification")
                        else ""
                    )
                    comp = ReliabilityComponent(name, ctype, qty, {}, qual)
                    template = COMPONENT_ATTR_TEMPLATES.get(ctype, {})
                    for k, v in template.items():
                        comp.attributes[k] = v[0] if isinstance(v, list) else v
                    # store any extra columns as attributes
                    for key, val in row.items():
                        if key not in mapping.values():
                            comp.attributes[key] = val
                    self.components.append(comp)
                except Exception:
                    continue
        self.refresh_tree()

    def ask_mapping(self, fields):
        if not fields:
            return None
        win = tk.Toplevel(self)
        win.title("Map Columns")
        vars = {}
        targets = ["name", "type", "qty", "qualification"]
        for i, tgt in enumerate(targets):
            ttk.Label(win, text=tgt.capitalize()).grid(
                row=i, column=0, padx=5, pady=5, sticky="e"
            )
            var = tk.StringVar()
            cb = ttk.Combobox(win, textvariable=var, values=fields, state="readonly")
            if i < len(fields):
                var.set(fields[i])
            cb.grid(row=i, column=1, padx=5, pady=5)
            vars[tgt] = var

        result = {}

        def ok():
            for k, v in vars.items():
                result[k] = v.get()
            win.destroy()

        def cancel():
            result.clear()
            win.destroy()

        ttk.Button(win, text="OK", command=ok).grid(row=len(targets), column=0, pady=5)
        ttk.Button(win, text="Cancel", command=cancel).grid(
            row=len(targets), column=1, pady=5
        )
        win.grab_set()
        win.wait_window()
        if not result:
            return None
        return result

    def configure_component(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Configure", "Select a component")
            return
        idx = self.tree.index(sel)
        comp = self.components[idx]

        template = COMPONENT_ATTR_TEMPLATES.get(comp.comp_type, {})
        for k, v in template.items():
            comp.attributes.setdefault(k, v[0] if isinstance(v, list) else v)

        class ParamDialog(simpledialog.Dialog):
            def body(self, master):
                self.resizable(False, False)
                self.vars = {}
                nb = ttk.Notebook(master)
                nb.pack(fill=tk.BOTH, expand=True)
                gen_tab = ttk.Frame(nb)
                attr_tab = ttk.Frame(nb)
                nb.add(gen_tab, text="General")
                nb.add(attr_tab, text="Attributes")

                row = 0
                ttk.Label(gen_tab, text="Quantity").grid(
                    row=row, column=0, padx=5, pady=5, sticky="e"
                )
                qty_var = tk.IntVar(value=comp.quantity)
                ttk.Entry(gen_tab, textvariable=qty_var).grid(
                    row=row, column=1, padx=5, pady=5
                )
                self.vars["__qty__"] = qty_var
                row += 1
                ttk.Label(gen_tab, text="Qualification").grid(
                    row=row, column=0, padx=5, pady=5, sticky="e"
                )
                qual_var = tk.StringVar(value=comp.qualification)
                ttk.Combobox(
                    gen_tab,
                    textvariable=qual_var,
                    values=QUALIFICATIONS,
                    state="readonly",
                ).grid(row=row, column=1, padx=5, pady=5)
                self.vars["__qual__"] = qual_var

                row = 0
                for k, v in comp.attributes.items():
                    ttk.Label(attr_tab, text=k).grid(
                        row=row, column=0, padx=5, pady=5, sticky="e"
                    )
                    if isinstance(template.get(k), list):
                        var = tk.StringVar(value=str(v))
                        ttk.Combobox(
                            attr_tab,
                            textvariable=var,
                            values=template[k],
                            state="readonly",
                        ).grid(row=row, column=1, padx=5, pady=5)
                    else:
                        var = tk.StringVar(value=str(v))
                        ttk.Entry(attr_tab, textvariable=var).grid(
                            row=row, column=1, padx=5, pady=5
                        )
                    self.vars[k] = var
                    row += 1

            def apply(self):
                comp.quantity = int(self.vars["__qty__"].get())
                comp.qualification = self.vars["__qual__"].get()
                for k, v in self.vars.items():
                    if k.startswith("__"):
                        continue
                    comp.attributes[k] = v.get()

        ParamDialog(self)
        self.refresh_tree()

    def calculate_fit(self):
        prof_name = self.profile_var.get()
        mp = next((m for m in self.app.mission_profiles if m.name == prof_name), None)
        needs_profile = any(not c.sub_boms for c in self.components)
        if mp is None and needs_profile:
            messagebox.showwarning("FIT", "Select a mission profile")
            return
        std = self.standard_var.get()
        total = 0.0
        for comp in self.components:
            if comp.sub_boms:
                # Aggregate FIT from the referenced BOMs without recomputation
                comp.fit = _total_fit_from_boms(comp.sub_boms)
            else:
                info = RELIABILITY_MODELS.get(std, {}).get(comp.comp_type)
                if info:
                    qf = (
                        PASSIVE_QUAL_FACTORS.get(comp.qualification, 1.0)
                        if comp.is_passive
                        else 1.0
                    )
                    if mp is not None:
                        comp.fit = info["formula"](comp.attributes, mp) * mp.tau * qf
                    else:
                        comp.fit = 0.0
                else:
                    comp.fit = 0.0
            total += comp.fit * comp.quantity

        sg_targets = {
            sg.user_name: {
                "dc": getattr(sg, "sg_dc_target", 0.0),
                "spfm": getattr(sg, "sg_spfm_target", 0.0),
                "lpfm": getattr(sg, "sg_lpfm_target", 0.0),
            }
            for sg in self.app.top_events
        }
        for be in self.app.fmea_entries:
            sg = getattr(be, "fmeda_safety_goal", "")
            if sg and sg not in sg_targets:
                sg_targets[sg] = {
                    "dc": getattr(be, "fmeda_dc_target", 0.0),
                    "spfm": getattr(be, "fmeda_spfm_target", 0.0),
                    "lpfm": getattr(be, "fmeda_lpfm_target", 0.0),
                }

        metrics = compute_fmeda_metrics(
            self.app.fmea_entries,
            self.components,
            self.app.get_safety_goal_asil,
            sg_targets=sg_targets,
        )
        self.app.reliability_components = list(self.components)
        self.app.reliability_total_fit = metrics["total"]
        self.app.spfm = metrics["spfm_raw"]
        self.app.lpfm = metrics["lpfm_raw"]
        self.app.reliability_dc = metrics["dc"]
        self.refresh_tree()
        goal_res = []
        for sg, gm in metrics.get("goal_metrics", {}).items():
            ok = gm["ok_dc"] and gm["ok_spfm"] and gm["ok_lpfm"]
            symbol = CHECK_MARK if ok else CROSS_MARK
            goal_res.append(f"{sg}:{symbol}")
        extra = f"  [{' ; '.join(goal_res)}]" if goal_res else ""
        self.formula_label.config(
            text=(
                f"Total FIT: {metrics['total']:.2f}  DC: {metrics['dc']:.2f}  "
                f"SPFM: {metrics['spfm_raw']:.2f}  LPFM: {metrics['lpfm_raw']:.2f}"
                + extra
            )
        )

    def save_analysis(self):
        if not self.components:
            messagebox.showwarning("Save", "No components defined")
            return
        current = self.analysis_var.get()
        if current:
            # Update existing analysis without asking for a name
            ra = next(
                (r for r in self.app.reliability_analyses if r.name == current),
                None,
            )
            if ra is None:
                ra = ReliabilityAnalysis(current, "", "", [], 0.0, 0.0, 0.0, 0.0)
                self.app.reliability_analyses.append(ra)
        else:
            name = simpledialog.askstring("Save Analysis", "Enter analysis name:")
            if not name:
                return
            ra = ReliabilityAnalysis(name, "", "", [], 0.0, 0.0, 0.0, 0.0)
            self.app.reliability_analyses.append(ra)
            current = name

        ra.name = current
        ra.standard = self.standard_var.get()
        ra.profile = self.profile_var.get()
        ra.components = copy.deepcopy(self.components)
        ra.total_fit = self.app.reliability_total_fit
        ra.spfm = self.app.spfm
        ra.lpfm = self.app.lpfm
        ra.dc = self.app.reliability_dc

        self.refresh_analysis_list()
        self.analysis_var.set(current)
        messagebox.showinfo("Save", "Analysis saved")

    def load_analysis(self):
        """Load a previously saved reliability analysis."""
        if not self.app.reliability_analyses:
            messagebox.showwarning("Load", "No saved analyses")
            return
        win = tk.Toplevel(self)
        win.title("Select Analysis")
        lb = tk.Listbox(win, height=8, width=40)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for ra in self.app.reliability_analyses:
            lb.insert(tk.END, ra.name)

        def do_load():
            sel = lb.curselection()
            if not sel:
                return
            ra = self.app.reliability_analyses[sel[0]]
            self._populate_from_analysis(ra)
            win.destroy()

        ttk.Button(win, text="Load", command=do_load).pack(
            side=tk.RIGHT, padx=5, pady=5
        )

    def load_selected_analysis(self, *_):
        """Load analysis chosen from the combo box."""
        name = self.analysis_var.get()
        ra = next((r for r in self.app.reliability_analyses if r.name == name), None)
        if ra:
            self._populate_from_analysis(ra)

    def delete_analysis(self):
        name = self.analysis_var.get()
        if not name:
            messagebox.showwarning("Delete", "Select an analysis")
            return
        if not messagebox.askyesno("Delete", f"Delete analysis '{name}'?"):
            return
        self.app.reliability_analyses = [
            r for r in self.app.reliability_analyses if r.name != name
        ]
        self.analysis_var.set("")
        self.refresh_analysis_list()
        self.components.clear()
        self.refresh_tree()
        self.formula_label.config(text="")

    def refresh_analysis_list(self):
        names = [ra.name for ra in self.app.reliability_analyses]
        self.analysis_combo.configure(values=names)
        if not self.analysis_var.get() and names:
            self.analysis_var.set(names[0])
            self.load_selected_analysis()

    def _populate_from_analysis(self, ra):
        self.analysis_var.set(ra.name)
        self.standard_var.set(ra.standard)
        self.profile_var.set(ra.profile)
        self.components = copy.deepcopy(ra.components)
        self.app.reliability_total_fit = ra.total_fit
        self.app.spfm = ra.spfm
        self.app.lpfm = ra.lpfm
        self.app.reliability_dc = ra.dc
        self.refresh_tree()
        self.formula_label.config(
            text=f"Total FIT: {ra.total_fit:.2f}  DC: {ra.dc:.2f}  SPFM: {ra.spfm:.2f}  LPFM: {ra.lpfm:.2f}"
        )


class FI2TCWindow(tk.Frame):
    COLS = [
        "id",
        "system_function",
        "allocation",
        "interfaces",
        "functional_insufficiencies",
        "scene",
        "scenario",
        "driver_behavior",
        "occurrence",
        "vehicle_effect",
        "severity",
        "design_measures",
        "verification",
        "measure_effectiveness",
        "triggering_conditions",
        "mitigation",
        "acceptance",
    ]

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("FI2TC Analysis")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="FI2TC:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        configure_table_style("FI2TC.Treeview", rowheight=80)
        self.tree = EditableTreeview(
            tree_frame,
            columns=self.COLS,
            show="headings",
            style="FI2TC.Treeview",
            height=4,
            edit_callback=self.on_cell_edit,
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in self.COLS:
            self.tree.heading(c, text=c.replace("_", " ").title())
            width = 200 if c == "hazard" else 120
            self.tree.column(c, width=width)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self.edit_row())
        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        add_row_btn = ttk.Button(btn, text="Add", command=self.add_row)
        add_row_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(add_row_btn, "Insert a new HAZOP entry in the table.")
        edit_row_btn = ttk.Button(btn, text="Edit", command=self.edit_row)
        edit_row_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(edit_row_btn, "Edit the selected HAZOP entry.")
        del_row_btn = ttk.Button(btn, text="Delete", command=self.del_row)
        del_row_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(del_row_btn, "Remove the selected HAZOP entry from the table.")
        ttk.Button(btn, text="Export CSV", command=self.export_csv).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.fi2tc_entries:
            vals = [_wrap_val(row.get(k, "")) for k in self.COLS]
            self.tree.insert("", "end", values=vals)
        stripe_rows(self.tree)

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, app, data=None):
            self.app = app
            self.parent_win = parent
            default = {k: "" for k in parent.COLS}
            self.data = data or default
            self.selected = {}
            super().__init__(parent, title="Edit Row")

        def body(self, master):
            self.resizable(False, False)
            self.geometry("700x500")
            fi_names = [
                n.user_name or f"FI {n.unique_id}"
                for n in self.app.get_all_functional_insufficiencies()
            ]
            tc_names = [
                n.user_name or f"TC {n.unique_id}"
                for n in self.app.get_all_triggering_conditions()
            ]
            func_names = self.app.get_all_function_names()
            comp_names = self.app.get_all_component_names()
            scen_names = self.app.get_all_scenario_names()
            scene_names = self.app.get_all_scenery_names()
            req_opts = sorted(
                (
                    f"[{r['id']}] {r['text']}"
                    for r in global_requirements.values()
                    if r.get("req_type") == "functional modification"
                ),
                key=str.lower,
            )
            self.widgets = {}
            nb = ttk.Notebook(master)
            nb.pack(fill=tk.BOTH, expand=True)
            categories = {
                "Known Functional Weakness": [
                    "id",
                    "system_function",
                    "allocation",
                    "interfaces",
                    "scene",
                    "scenario",
                    "driver_behavior",
                    "occurrence",
                    "functional_insufficiencies",
                    "vehicle_effect",
                    "severity",
                ],
                "Design Measures": [
                    "design_measures",
                    "verification",
                    "measure_effectiveness",
                ],
                "Triggering Condition Identification": ["triggering_conditions"],
                "Mitigations": ["mitigation", "acceptance"],
            }
            tabs = {name: ttk.Frame(nb) for name in categories}
            for name, frame in tabs.items():
                nb.add(frame, text=name)
            rows = {name: 0 for name in categories}

            def get_frame(col):
                for name, cols in categories.items():
                    if col in cols:
                        r = rows[name]
                        rows[name] += 1
                        return tabs[name], r
                return master, 0

            def refresh_funcs(*_):
                comp = self.widgets.get("allocation")
                if isinstance(comp, tk.StringVar):
                    func_opts = sorted(
                        {
                            e.function
                            for e in self.app.hazop_entries
                            if not comp.get() or e.component == comp.get()
                        }
                    )
                else:
                    func_opts = func_names
                if "system_function" in self.widgets:
                    w = self.widgets["system_function_widget"]
                    w["values"] = func_opts

            for col in self.parent_win.COLS:
                frame, r = get_frame(col)
                ttk.Label(frame, text=col.replace("_", " ").title()).grid(
                    row=r, column=0, sticky="e", padx=5, pady=2
                )
                if col == "triggering_conditions":
                    tc_frame = ttk.Frame(frame)
                    tc_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.tc_lb = tk.Listbox(tc_frame, selectmode="extended", height=5, exportselection=False)
                    self.tc_lb.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
                    existing = [e.strip() for e in self.data.get(col, "").split(";") if e.strip()]
                    for val in existing:
                        self.tc_lb.insert(tk.END, val)
                    ttk.Button(tc_frame, text="Add", command=self.add_tc).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(tc_frame, text="Edit", command=self.edit_tc).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(tc_frame, text="Delete", command=self.del_tc).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(tc_frame, text="Add Existing", command=self.add_tc_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.tc_lb
                elif col == "functional_insufficiencies":
                    fi_frame = ttk.Frame(frame)
                    fi_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.fi_lb = tk.Listbox(fi_frame, selectmode="extended", height=4, exportselection=False)
                    self.fi_lb.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
                    existing = [e.strip() for e in self.data.get(col, "").split(";") if e.strip()]
                    for val in existing:
                        self.fi_lb.insert(tk.END, val)
                    ttk.Button(fi_frame, text="Add New", command=self.add_fi_new).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(fi_frame, text="Edit", command=self.edit_fi).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(fi_frame, text="Delete", command=self.del_fi).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(fi_frame, text="Add Existing", command=self.add_fi_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.fi_lb
                    self.fi_options = fi_names
                elif col == "design_measures":
                    self.req_opts = list(req_opts)
                    dm_frame = ttk.Frame(frame)
                    dm_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.dm_lb = tk.Listbox(dm_frame, selectmode="extended", height=5, exportselection=False)
                    self.dm_lb.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
                    existing = [e.strip() for e in self.data.get(col, "").split(",") if e.strip()]
                    for val in existing:
                        self.dm_lb.insert(tk.END, val)
                    ttk.Button(dm_frame, text="Add New", command=self.add_dm_new).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(dm_frame, text="Add Existing", command=self.add_dm_existing).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(dm_frame, text="Edit", command=self.edit_dm).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(dm_frame, text="Delete", command=self.del_dm).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.dm_lb
                elif col == "mitigation":
                    mit_frame = ttk.Frame(frame)
                    mit_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.mit_lb = tk.Listbox(mit_frame, height=4, width=50)
                    self.mit_lb.grid(row=0, column=0, columnspan=4, sticky="w")
                    existing = [e.strip() for e in self.data.get(col, "").split(",") if e.strip()]
                    for rid in existing:
                        req = global_requirements.get(rid, {"id": rid, "text": ""})
                        self.mit_lb.insert(tk.END, f"[{req['id']}] {req.get('text','')}")
                    ttk.Button(mit_frame, text="Add New", command=self.add_mit_new).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(mit_frame, text="Edit", command=self.edit_mit).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(mit_frame, text="Delete", command=self.del_mit).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(mit_frame, text="Add Existing", command=self.add_mit_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.mit_lb
                elif col == "system_function":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame, textvariable=var, values=func_names, state="readonly"
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                    self.widgets["system_function_widget"] = cb
                elif col == "allocation":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame, textvariable=var, values=comp_names, state="readonly"
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    cb.bind("<<ComboboxSelected>>", refresh_funcs)
                    self.widgets[col] = var
                elif col == "vehicle_effect":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    frame2 = ttk.Frame(frame)
                    frame2.grid(row=r, column=1, padx=5, pady=2)
                    cb = ttk.Combobox(frame2, textvariable=var, values=sorted(self.app.hazards), state="readonly")
                    cb.pack(side=tk.LEFT)
                    def new_hazard():
                        name = simpledialog.askstring("New Hazard", "Name:")
                        if not name:
                            return
                        sev_widget = self.widgets.get("severity")
                        sev = sev_widget.get() if isinstance(sev_widget, tk.StringVar) else "1"
                        self.app.add_hazard(name)
                        self.app.update_hazard_severity(name, sev)
                        cb["values"] = sorted(self.app.hazards)
                        var.set(name)
                    ttk.Button(frame2, text="New", command=new_hazard).pack(side=tk.LEFT, padx=2)
                    self.widgets[col] = var
                elif col == "scene":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame, textvariable=var, values=scene_names, state="readonly"
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "scenario":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame, textvariable=var, values=scen_names, state="readonly"
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "severity":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame,
                        textvariable=var,
                        values=["1", "2", "3"],
                        state="readonly",
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                else:
                    txt = tk.Text(frame, width=25, height=2, wrap="word")
                    txt.insert("1.0", self.data.get(col, ""))
                    if col == "known_use_case":
                        self.kuc_widget = txt
                        txt.configure(state="disabled")
                    txt.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = txt
                    if col == "known_use_case":
                        self.kuc_widget = txt
            refresh_funcs()
            self.update_known_use_case()

        def apply(self):
            for col, widget in self.widgets.items():
                if isinstance(widget, tk.Entry):
                    self.data[col] = widget.get()
                elif isinstance(widget, tk.Text):
                    self.data[col] = widget.get("1.0", "end-1c")
                elif isinstance(widget, tk.Listbox):
                    items = list(widget.get(0, tk.END))
                    if col == "triggering_conditions" or col == "functional_insufficiencies":
                        self.data[col] = ";".join(items)
                    else:
                        self.data[col] = ",".join(items)
                else:
                    val = widget.get()
                    orig = self.selected.get(col, "")
                    if col == "triggering_conditions" and orig and val != orig:
                        self.app.rename_triggering_condition(orig, val)
                    elif col == "vehicle_effect" and orig and val != orig:
                        self.app.rename_hazard(orig, val)
                    self.data[col] = val
            veh = self.data.get("vehicle_effect", "").strip()
            sev = self.data.get("severity", "1").strip()
            if veh:
                self.app.add_hazard(veh)
                self.app.update_hazard_severity(veh, sev)
            self.result = True

        def add_dm_new(self):
            dlg = _RequirementDialog(self, req_type="functional modification")
            if dlg.result:
                req = dlg.result
                global_requirements[req["id"]] = req
                text = f"[{req['id']}] {req['text']}"
                self.dm_lb.insert(tk.END, text)

        def add_dm_existing(self):
            dlg = _SelectRequirementsDialog(self, req_type="functional modification")
            if dlg.result:
                for val in dlg.result:
                    if val not in self.dm_lb.get(0, tk.END):
                        self.dm_lb.insert(tk.END, val)

        def edit_dm(self):
            sel = self.dm_lb.curselection()
            if not sel:
                return
            text = self.dm_lb.get(sel[0])
            rid = text.split("]", 1)[0][1:]
            req = global_requirements.get(rid, {"id": rid, "text": text})
            dlg = _RequirementDialog(self, req, req_type="functional modification")
            if dlg.result:
                new_req = dlg.result
                global_requirements[new_req["id"]] = new_req
                new_text = f"[{new_req['id']}] {new_req['text']}"
                self.dm_lb.delete(sel[0])
                self.dm_lb.insert(sel[0], new_text)

        def del_dm(self):
            sel = list(self.dm_lb.curselection())
            for idx in reversed(sel):
                self.dm_lb.delete(idx)

        def add_tc_existing(self):
            dlg = _SelectTriggeringConditionsDialog(self, self.app.triggering_conditions)
            if dlg.result:
                for val in dlg.result:
                    if val not in self.tc_lb.get(0, tk.END):
                        self.tc_lb.insert(tk.END, val)

        def add_tc(self):
            name = simpledialog.askstring("Triggering Condition", "Name:")
            if name:
                if name not in self.tc_lb.get(0, tk.END):
                    self.tc_lb.insert(tk.END, name)

        def edit_tc(self):
            sel = self.tc_lb.curselection()
            if not sel:
                return
            current = self.tc_lb.get(sel[0])
            name = simpledialog.askstring("Triggering Condition", "Name:", initialvalue=current)
            if name and name != current:
                self.app.rename_triggering_condition(current, name)
                self.tc_lb.delete(sel[0])
                self.tc_lb.insert(sel[0], name)

        def del_tc(self):
            sel = list(self.tc_lb.curselection())
            for idx in reversed(sel):
                self.tc_lb.delete(idx)

        def add_mit_new(self):
            dlg = _RequirementDialog(self, req_type="operational")
            if dlg.result:
                req = dlg.result
                global_requirements[req["id"]] = req
                text = f"[{req['id']}] {req['text']}"
                self.mit_lb.insert(tk.END, text)

        def add_mit_existing(self):
            dlg = _SelectRequirementsDialog(self, req_type="operational")
            if dlg.result:
                for val in dlg.result:
                    if val not in self.mit_lb.get(0, tk.END):
                        self.mit_lb.insert(tk.END, val)

        def add_fi_new(self):
            name = simpledialog.askstring("Functional Insufficiency", "Name:")
            if name:
                if name not in self.fi_lb.get(0, tk.END):
                    self.fi_lb.insert(tk.END, name)
                self.update_known_use_case()

        def add_fi_existing(self):
            dlg = _SelectFIsDialog(self, self.fi_options)
            if getattr(dlg, "result", None):
                for val in dlg.result:
                    if val not in self.fi_lb.get(0, tk.END):
                        self.fi_lb.insert(tk.END, val)
                self.update_known_use_case()

        def edit_fi(self):
            sel = self.fi_lb.curselection()
            if not sel:
                return
            current = self.fi_lb.get(sel[0])
            name = simpledialog.askstring("Functional Insufficiency", "Name:", initialvalue=current)
            if name and name != current:
                self.app.rename_functional_insufficiency(current, name)
                self.fi_lb.delete(sel[0])
                self.fi_lb.insert(sel[0], name)
            self.update_known_use_case()

        def del_fi(self):
            sel = list(self.fi_lb.curselection())
            for idx in reversed(sel):
                self.fi_lb.delete(idx)
            self.update_known_use_case()

        def edit_mit(self):
            sel = self.mit_lb.curselection()
            if not sel:
                return
            text = self.mit_lb.get(sel[0])
            rid = text.split("]", 1)[0][1:]
            req = global_requirements.get(rid, {"id": rid, "text": text})
            dlg = _RequirementDialog(self, req, req_type="operational")
            if dlg.result:
                new_req = dlg.result
                global_requirements[new_req["id"]] = new_req
                new_text = f"[{new_req['id']}] {new_req['text']}"
                self.mit_lb.delete(sel[0])
                self.mit_lb.insert(sel[0], new_text)

        def del_mit(self):
            sel = list(self.mit_lb.curselection())
            for idx in reversed(sel):
                self.mit_lb.delete(idx)


        def update_known_use_case(self):
            if not hasattr(self, "kuc_widget"):
                return
            funcs = []
            fis = list(self.fi_lb.get(0, tk.END)) if hasattr(self, "fi_lb") else []
            ucs = []
            for f in funcs + fis:
                uc = self.app.get_use_case_for_function(f)
                if uc and uc not in ucs:
                    ucs.append(uc)
            self.kuc_widget.config(state="normal")
            self.kuc_widget.delete("1.0", tk.END)
            self.kuc_widget.insert("1.0", ";".join(ucs))
            self.kuc_widget.config(state="disabled")


    def add_row(self):
        dlg = self.RowDialog(self, self.app)
        if getattr(dlg, "result", None):
            self.app.fi2tc_entries.append(dlg.data)
            self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        data = self.app.fi2tc_entries[idx]
        dlg = self.RowDialog(self, self.app, data)
        if getattr(dlg, "result", None):
            self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.fi2tc_entries):
                del self.app.fi2tc_entries[idx]
        self.refresh()

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        if row >= len(self.app.fi2tc_entries):
            return
        self.app.fi2tc_entries[row][column] = value

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(self.COLS)
            for r in self.app.fi2tc_entries:
                w.writerow([r.get(k, "") for k in self.COLS])
        messagebox.showinfo("Export", "FI2TC exported")

    def refresh_docs(self):
        names = [d.name for d in self.app.fi2tc_docs]
        self.doc_cb.configure(values=names)
        if self.app.active_fi2tc:
            self.doc_var.set(self.app.active_fi2tc.name)
        elif names:
            self.doc_var.set(names[0])

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.fi2tc_docs:
            if d.name == name:
                self.app.active_fi2tc = d
                self.app.fi2tc_entries = d.entries
                break
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New FI2TC", "Name:")
        if not name:
            return
        doc = FI2TCDoc(name, [])
        self.app.fi2tc_docs.append(doc)
        self.app.active_fi2tc = doc
        self.app.fi2tc_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_fi2tc:
            return
        name = simpledialog.askstring(
            "Rename FI2TC", "Name:", initialvalue=self.app.active_fi2tc.name
        )
        if not name:
            return
        self.app.active_fi2tc.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_fi2tc
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete FI2TC '{doc.name}'?"):
            return
        self.app.fi2tc_docs.remove(doc)
        if self.app.fi2tc_docs:
            self.app.active_fi2tc = self.app.fi2tc_docs[0]
        else:
            self.app.active_fi2tc = None
        self.app.fi2tc_entries = (
            self.app.active_fi2tc.entries if self.app.active_fi2tc else []
        )
        self.refresh_docs()
        self.refresh()
        self.app.update_views()


class HazopWindow(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("HAZOP Analysis")
            master.geometry("600x400")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        doc_lbl = ttk.Label(top, text="HAZOP:")
        doc_lbl.pack(side=tk.LEFT)
        ToolTip(doc_lbl, "Select a HAZOP document to edit or view.")
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ToolTip(
            self.doc_cb, "All HAZOP analyses stored in the project are listed here."
        )
        new_btn = ttk.Button(top, text="New", command=self.new_doc)
        new_btn.pack(side=tk.LEFT)
        ToolTip(new_btn, "Create a new HAZOP document.")
        edit_btn = ttk.Button(top, text="Rename", command=self.rename_doc)
        edit_btn.pack(side=tk.LEFT)
        del_btn = ttk.Button(top, text="Delete", command=self.delete_doc)
        del_btn.pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        columns = ("function", "malfunction", "type", "safety", "rationale")
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True)
        configure_table_style("Hazop.Treeview")
        self.tree = EditableTreeview(
            content,
            columns=columns,
            show="headings",
            style="Hazop.Treeview",
            edit_callback=self.on_cell_edit,
        )
        vsb = ttk.Scrollbar(content, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(content, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            if col in ("rationale", "hazard"):
                width = 200
            else:
                width = 120
            self.tree.column(col, width=width)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        hara_add_btn = ttk.Button(btn, text="Add", command=self.add_row)
        hara_add_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(hara_add_btn, "Insert a new HARA entry.")
        hara_edit_btn = ttk.Button(btn, text="Edit", command=self.edit_row)
        hara_edit_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(hara_edit_btn, "Edit the selected HARA row.")
        hara_del_btn = ttk.Button(btn, text="Delete", command=self.del_row)
        hara_del_btn.pack(side=tk.LEFT, padx=2, pady=2)
        ToolTip(hara_del_btn, "Delete the selected HARA row.")

        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh_docs(self):
        names = [d.name for d in self.app.hazop_docs]
        self.doc_cb["values"] = names
        if self.app.active_hazop:
            self.doc_var.set(self.app.active_hazop.name)
        elif names:
            self.doc_var.set(names[0])

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.hazop_docs:
            if d.name == name:
                self.app.active_hazop = d
                self.app.hazop_entries = d.entries
                break
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New HAZOP", "Name:")
        if not name:
            return
        doc = HazopDoc(name, [])
        self.app.hazop_docs.append(doc)
        self.app.active_hazop = doc
        self.app.hazop_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_hazop:
            return
        name = simpledialog.askstring(
            "Rename HAZOP", "Name:", initialvalue=self.app.active_hazop.name
        )
        if not name:
            return
        self.app.active_hazop.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_hazop
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete HAZOP '{doc.name}'?"):
            return
        self.app.hazop_docs.remove(doc)
        if self.app.hazop_docs:
            self.app.active_hazop = self.app.hazop_docs[0]
        else:
            self.app.active_hazop = None
        self.app.hazop_entries = (
            self.app.active_hazop.entries if self.app.active_hazop else []
        )
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.hazop_entries:
            vals = [
                row.function,
                row.malfunction,
                row.mtype,
                row.scenario,
                row.conditions,
                row.hazard,
                "Yes" if row.safety else "No",
                row.rationale,
                "Yes" if row.covered else "No",
                row.covered_by,
            ]
            self.tree.insert("", "end", values=vals)
        stripe_rows(self.tree)

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, row=None):
            self.app = parent.app
            self.row = row or HazopEntry(
                "",
                "",
                "No/Not",
                "",
                "",
                "",
                False,
                "",
                False,
                "",
            )
            super().__init__(parent, title="Edit HAZOP Row")

        def body(self, master):
            func_lbl = ttk.Label(master, text="Function")
            func_lbl.grid(row=0, column=0, sticky="e", padx=5, pady=5)
            ToolTip(func_lbl, "Select the vehicle function under analysis.")
            funcs = self.app.get_all_action_names()
            self.func = tk.StringVar(value=self.row.function)
            func_cb = ttk.Combobox(
                master, textvariable=self.func, values=funcs, state="readonly"
            )
            func_cb.grid(row=0, column=1, padx=5, pady=5)
            ToolTip(
                func_cb, "Functions come from activity diagrams or architecture blocks."
            )

            mal_lbl = ttk.Label(master, text="Malfunction")
            mal_lbl.grid(row=1, column=0, sticky="e", padx=5, pady=5)
            ToolTip(
                mal_lbl,
                "Choose an existing malfunction or type a new one.\n"
                "Create malfunctions via the Malfunctions editor or by\n"
                "building an activity diagram that defines vehicle level\n"
                "functions, then running a HAZOP on the diagram activities.",
            )
            self.mal = tk.StringVar(value=self.row.malfunction)
            mal_cb = ttk.Combobox(
                master,
                textvariable=self.mal,
                values=sorted(self.app.malfunctions),
            )
            mal_cb.grid(row=1, column=1, padx=5, pady=5)
            ToolTip(mal_cb, "Type a new malfunction to add it to the project.")

            typ_lbl = ttk.Label(master, text="Type")
            typ_lbl.grid(row=2, column=0, sticky="e", padx=5, pady=5)
            ToolTip(
                typ_lbl,
                "Guideword describing how the malfunction deviates from the intended function.",
            )
            self.typ = tk.StringVar(value=self.row.mtype)
            typ_cb = ttk.Combobox(
                master,
                textvariable=self.typ,
                values=["No/Not", "Unintended", "Excessive", "Insufficient", "Reverse"],
                state="readonly",
            )
            typ_cb.grid(row=2, column=1, padx=5, pady=5)
            ToolTip(typ_cb, "Select the malfunction guideword.")

            scen_lbl = ttk.Label(master, text="Scenario")
            scen_lbl.grid(row=3, column=0, sticky="e", padx=5, pady=5)
            ToolTip(scen_lbl, "Operational scenario associated with this function.")
            scenarios = []
            for lib in self.app.scenario_libraries:
                scenarios.extend(lib.get("scenarios", []))
            self.scen = tk.StringVar(value=self.row.scenario)
            scen_cb = ttk.Combobox(
                master, textvariable=self.scen, values=scenarios, state="readonly"
            )
            scen_cb.grid(row=3, column=1, padx=5, pady=5)
            ToolTip(scen_cb, "Scenarios come from imported scenario libraries.")

            cond_lbl = ttk.Label(master, text="Driving Conditions")
            cond_lbl.grid(row=4, column=0, sticky="e", padx=5, pady=5)
            ToolTip(cond_lbl, "Optional free text describing environmental conditions.")
            self.cond = tk.StringVar(value=self.row.conditions)
            cond_entry = ttk.Entry(master, textvariable=self.cond)
            cond_entry.grid(row=4, column=1, padx=5, pady=5)
            ToolTip(cond_entry, "Example: rain, snow, gravel road, etc.")

            haz_lbl = ttk.Label(master, text="Hazard")
            haz_lbl.grid(row=5, column=0, sticky="e", padx=5, pady=5)
            ToolTip(haz_lbl, "Consequence of the malfunction under the given scenario.")
            haz_frame = ttk.Frame(master)
            haz_frame.grid(row=5, column=1, padx=5, pady=5, sticky="w")
            self.haz_var = tk.StringVar(value=self.row.hazard)
            self.haz_cb = ttk.Combobox(
                haz_frame,
                textvariable=self.haz_var,
                values=sorted(self.app.hazards),
                width=30,
            )
            self.haz_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ToolTip(
                self.haz_cb,
                "Select an existing hazard or type a new one.",
            )
            new_haz_btn = ttk.Button(haz_frame, text="New", command=self.new_hazard)
            new_haz_btn.pack(side=tk.LEFT, padx=2)
            ToolTip(new_haz_btn, "Create a new hazard and select it.")

            safety_lbl = ttk.Label(master, text="Safety Relevant")
            safety_lbl.grid(row=6, column=0, sticky="e", padx=5, pady=5)
            ToolTip(
                safety_lbl, "Mark 'Yes' if the malfunction can lead to a safety hazard."
            )
            self.safety = tk.StringVar(value="Yes" if self.row.safety else "No")
            safety_cb = ttk.Combobox(
                master, textvariable=self.safety, values=["Yes", "No"], state="readonly"
            )
            safety_cb.grid(row=6, column=1, padx=5, pady=5)
            ToolTip(
                safety_cb,
                "Only safety relevant malfunctions are used in HARA analyses.",
            )

            rat_lbl = ttk.Label(master, text="Rationale")
            rat_lbl.grid(row=7, column=0, sticky="ne", padx=5, pady=5)
            ToolTip(rat_lbl, "Reasoning for the safety relevance decision.")
            self.rat = tk.Text(master, width=30, height=3)
            self.rat.insert("1.0", self.row.rationale)
            self.rat.grid(row=7, column=1, padx=5, pady=5)
            ToolTip(self.rat, "Provide justification or references for this entry.")

            cov_lbl = ttk.Label(master, text="Covered")
            cov_lbl.grid(row=8, column=0, sticky="e", padx=5, pady=5)
            ToolTip(cov_lbl, "Indicate whether the malfunction is already mitigated.")
            self.cov = tk.StringVar(value="Yes" if self.row.covered else "No")
            cov_cb = ttk.Combobox(
                master, textvariable=self.cov, values=["Yes", "No"], state="readonly"
            )
            cov_cb.grid(row=8, column=1, padx=5, pady=5)
            ToolTip(
                cov_cb,
                "Select 'Yes' if another function or feature prevents the hazard.",
            )

            covby_lbl = ttk.Label(master, text="Covered By")
            covby_lbl.grid(row=9, column=0, sticky="e", padx=5, pady=5)
            ToolTip(covby_lbl, "Reference the malfunction providing mitigation.")
            malfs = [e.malfunction for e in self.app.hazop_entries]
            self.cov_by = tk.StringVar(value=self.row.covered_by)
            covby_cb = ttk.Combobox(
                master, textvariable=self.cov_by, values=malfs, state="readonly"
            )
            covby_cb.grid(row=9, column=1, padx=5, pady=5)
            ToolTip(
                covby_cb, "Choose a malfunction that covers this one if applicable."
            )

        def new_hazard(self):
            name = simpledialog.askstring("New Hazard", "Name:")
            if not name:
                return
            self.app.add_hazard(name)
            self.haz_var.set(name)
            self.haz_cb.configure(values=sorted(self.app.hazards))

        def apply(self):
            self.row.function = self.func.get()
            old_mal = self.row.malfunction
            self.row.malfunction = self.mal.get()
            if old_mal and old_mal != self.row.malfunction:
                self.app.rename_malfunction(old_mal, self.row.malfunction)
            # When a new malfunction is introduced from a HAZOP entry,
            # automatically create a corresponding top level event.
            # Register the malfunction globally; AutoML will create a
            # corresponding top level event if it's new.
            self.app.add_malfunction(self.row.malfunction)
            self.row.mtype = self.typ.get()
            self.row.scenario = self.scen.get()
            self.row.conditions = self.cond.get()
            old_haz = self.row.hazard
            self.row.hazard = self.haz_var.get().strip()
            if old_haz and old_haz != self.row.hazard:
                self.app.rename_hazard(old_haz, self.row.hazard)
            self.app.add_hazard(self.row.hazard)
            self.haz_cb.configure(values=sorted(self.app.hazards))
            self.app.update_hazard_list()
            self.row.safety = self.safety.get() == "Yes"
            self.row.rationale = self.rat.get("1.0", "end-1c")
            self.row.covered = self.cov.get() == "Yes"
            self.row.covered_by = self.cov_by.get()

    def add_row(self):
        if not self.app.active_hazop:
            messagebox.showwarning("Add", "Create a HAZOP first")
            return
        dlg = self.RowDialog(self)
        if dlg.row.function:
            self.app.hazop_entries.append(dlg.row)
            self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        row = self.app.hazop_entries[idx]
        dlg = self.RowDialog(self, row)
        self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.hazop_entries):
                del self.app.hazop_entries[idx]
        self.refresh()

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        if row >= len(self.app.hazop_entries):
            return
        entry = self.app.hazop_entries[row]
        mapping = {
            "function": "function",
            "malfunction": "malfunction",
            "type": "mtype",
            "safety": "safety",
            "rationale": "rationale",
        }
        attr = mapping.get(column)
        if not attr:
            return
        if attr == "safety":
            setattr(entry, attr, value.lower() in ("yes", "true", "1"))
        else:
            setattr(entry, attr, value)
        self.refresh()

    def load_analysis(self):
        if not self.app.reliability_analyses:
            messagebox.showwarning("Load", "No saved analyses")
            return
        win = tk.Toplevel(self)
        win.title("Select Analysis")
        lb = tk.Listbox(win, height=8, width=40)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for ra in self.app.reliability_analyses:
            lb.insert(tk.END, ra.name)

        def do_load():
            sel = lb.curselection()
            if not sel:
                return
            ra = self.app.reliability_analyses[sel[0]]
            self.standard_var.set(ra.standard)
            self.profile_var.set(ra.profile)
            self.components = copy.deepcopy(ra.components)
            self.app.reliability_total_fit = ra.total_fit
            self.app.spfm = ra.spfm
            self.app.lpfm = ra.lpfm
            self.app.reliability_dc = ra.dc
            win.destroy()
            self.refresh_tree()
            self.formula_label.config(
                text=f"Total FIT: {ra.total_fit:.2f}  DC: {ra.dc:.2f}  SPFM: {ra.spfm:.2f}  LPFM: {ra.lpfm:.2f}"
            )

        ttk.Button(win, text="Load", command=do_load).pack(
            side=tk.RIGHT, padx=5, pady=5
        )

    def save_analysis(self):
        if not self.components:
            messagebox.showwarning("Save", "No components defined")
            return
        name = simpledialog.askstring("Save Analysis", "Enter analysis name:")
        if not name:
            return
        ra = ReliabilityAnalysis(
            name,
            self.standard_var.get(),
            self.profile_var.get(),
            copy.deepcopy(self.components),
            self.app.reliability_total_fit,
            self.app.spfm,
            self.app.lpfm,
            self.app.reliability_dc,
        )
        self.app.reliability_analyses.append(ra)
        messagebox.showinfo("Save", "Analysis saved")


class HaraWindow(tk.Frame):
    COLS = [
        "malfunction",
        "hazard",
        "severity",
        "sev_rationale",
        "controllability",
        "cont_rationale",
        "exposure",
        "exp_rationale",
        "asil",
        "safety_goal",
    ]

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("HARA Analysis")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        hara_lbl = ttk.Label(top, text="HARA:")
        hara_lbl.pack(side=tk.LEFT)
        ToolTip(hara_lbl, "Select a HARA document to work on.")
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ToolTip(self.doc_cb, "Only HARAs defined in the project appear here.")
        new_hara_btn = ttk.Button(top, text="New", command=self.new_doc)
        new_hara_btn.pack(side=tk.LEFT)
        ToolTip(new_hara_btn, "Create a new HARA document.")
        edit_btn = ttk.Button(top, text="Rename", command=self.rename_doc)
        edit_btn.pack(side=tk.LEFT)
        del_btn = ttk.Button(top, text="Delete", command=self.delete_doc)
        del_btn.pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)
        self.hazop_lbl = ttk.Label(top, text="")
        self.hazop_lbl.pack(side=tk.LEFT, padx=10)
        self.status_lbl = ttk.Label(top, text="")
        self.status_lbl.pack(side=tk.LEFT, padx=10)

        configure_table_style("Hara.Treeview")
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = EditableTreeview(
            table_frame,
            columns=self.COLS,
            show="headings",
            style="Hara.Treeview",
            edit_callback=self.on_cell_edit,
        )
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in self.COLS:
            self.tree.heading(c, text=c.replace("_", " ").title())
            width = 200 if c == "hazard" else 120
            self.tree.column(c, width=width)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        btn = ttk.Frame(self)
        btn.pack(fill=tk.X)
        ttk.Button(btn, text="Add", command=self.add_row).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn, text="Edit", command=self.edit_row).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn, text="Delete", command=self.del_row).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh_docs(self):
        self.app.update_hara_statuses()
        names = [d.name for d in self.app.hara_docs]
        # Explicitly configure the combobox values to ensure Tkinter updates
        self.doc_cb.configure(values=names)
        if self.app.active_hara:
            self.doc_var.set(self.app.active_hara.name)
            hazops = ", ".join(getattr(self.app.active_hara, "hazops", []))
            self.hazop_lbl.config(text=f"HAZOPs: {hazops}")
            self.status_lbl.config(
                text=f"Status: {getattr(self.app.active_hara, 'status', 'draft')}"
            )

        elif names:
            self.doc_var.set(names[0])
            doc = self.app.hara_docs[0]
            hazops = ", ".join(getattr(doc, "hazops", []))
            self.hazop_lbl.config(text=f"HAZOPs: {hazops}")
            self.app.active_hara = doc
            self.app.hara_entries = doc.entries
            self.status_lbl.config(text=f"Status: {getattr(doc, 'status', 'draft')}")

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.hara_docs:
            if d.name == name:
                self.app.active_hara = d
                self.app.hara_entries = d.entries
                hazops = ", ".join(getattr(d, "hazops", []))
                self.hazop_lbl.config(text=f"HAZOPs: {hazops}")
                self.status_lbl.config(text=f"Status: {getattr(d, 'status', 'draft')}")
                break
        self.refresh()

    class NewHaraDialog(simpledialog.Dialog):
        def __init__(self, parent, app):
            self.app = app
            super().__init__(parent, title="New HARA")

        def body(self, master):
            ttk.Label(master, text="Name").grid(row=0, column=0, sticky="e")
            self.name_var = tk.StringVar()
            ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1)
            ttk.Label(master, text="HAZOPs").grid(row=1, column=0, sticky="ne")
            names = [d.name for d in self.app.hazop_docs]
            self.hazop_lb = tk.Listbox(master, selectmode="extended", height=5)
            for n in names:
                self.hazop_lb.insert(tk.END, n)
            self.hazop_lb.grid(row=1, column=1)

        def apply(self):
            sel = [self.hazop_lb.get(i) for i in self.hazop_lb.curselection()]
            self.result = (self.name_var.get(), sel)

    def new_doc(self):
        dlg = self.NewHaraDialog(self, self.app)
        if not getattr(dlg, "result", None):
            return
        name, hazops = dlg.result
        doc = HaraDoc(name, hazops, [], False, "draft")
        self.app.hara_docs.append(doc)
        self.app.active_hara = doc
        self.app.hara_entries = doc.entries
        self.status_lbl.config(text=f"Status: {doc.status}")
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_hara:
            return
        name = simpledialog.askstring(
            "Rename HARA", "Name:", initialvalue=self.app.active_hara.name
        )
        if not name:
            return
        self.app.active_hara.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_hara
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete HARA '{doc.name}'?"):
            return
        self.app.hara_docs.remove(doc)
        if self.app.hara_docs:
            self.app.active_hara = self.app.hara_docs[0]
        else:
            self.app.active_hara = None
        self.app.hara_entries = (
            self.app.active_hara.entries if self.app.active_hara else []
        )
        self.status_lbl.config(
            text=f"Status: {getattr(self.app.active_hara, 'status', 'draft')}"
        )
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.hara_entries:
            vals = [
                row.malfunction,
                row.hazard,
                row.severity,
                row.sev_rationale,
                row.controllability,
                row.cont_rationale,
                row.exposure,
                row.exp_rationale,
                row.asil,
                row.safety_goal,
            ]
            self.tree.insert("", "end", values=vals)
        stripe_rows(self.tree)
        self.app.sync_hara_to_safety_goals()

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, app, row=None):
            self.app = app
            self.row = row or HaraEntry("", "", 1, "", 1, "", 1, "", "QM", "")
            super().__init__(parent, title="Edit HARA Row")

        def body(self, master):
            hazop_names = []
            if self.app.active_hara:
                hazop_names = getattr(self.app.active_hara, "hazops", []) or []
            malfs = set()
            hazards_map = {}
            if not hazop_names:
                hazop_names = [d.name for d in self.app.hazop_docs]
            for hz_name in hazop_names:
                hz = self.app.get_hazop_by_name(hz_name)
                if hz:
                    for e in hz.entries:
                        if getattr(e, "safety", False):
                            malfs.add(e.malfunction)
                            if e.hazard:
                                hazards_map.setdefault(e.malfunction, []).append(
                                    e.hazard
                                )
            malfs = sorted(malfs)
            goals = [
                te.safety_goal_description or (te.user_name or f"SG {te.unique_id}")
                for te in self.app.top_events
            ]
            ttk.Label(master, text="Malfunction").grid(row=0, column=0, sticky="e")
            self.mal_var = tk.StringVar(value=self.row.malfunction)
            mal_cb = ttk.Combobox(
                master, textvariable=self.mal_var, values=malfs, state="readonly"
            )
            mal_cb.grid(row=0, column=1)
            ttk.Label(master, text="Hazard").grid(row=1, column=0, sticky="ne")
            self.haz = tk.Text(master, width=30, height=3)
            self.haz.insert("1.0", self.row.hazard)
            self.haz.grid(row=1, column=1)
            ttk.Label(master, text="Severity").grid(row=2, column=0, sticky="e")
            sev_val = str(self.app.hazard_severity.get(self.row.hazard.strip(), self.row.severity))
            self.sev_var = tk.StringVar(value=sev_val)
            sev_cb = ttk.Combobox(
                master,
                textvariable=self.sev_var,
                values=["1", "2", "3"],
                state="disabled",
            )
            sev_cb.grid(row=2, column=1)
            ttk.Label(master, text="Severity Rationale").grid(
                row=3, column=0, sticky="e"
            )
            self.sev_rat = tk.Entry(master)
            self.sev_rat.insert(0, self.row.sev_rationale)
            self.sev_rat.grid(row=3, column=1)
            ttk.Label(master, text="Controllability").grid(row=4, column=0, sticky="e")
            self.cont_var = tk.StringVar(value=str(self.row.controllability))
            cont_cb = ttk.Combobox(
                master,
                textvariable=self.cont_var,
                values=["1", "2", "3"],
                state="readonly",
            )
            cont_cb.grid(row=4, column=1)
            ttk.Label(master, text="Controllability Rationale").grid(
                row=5, column=0, sticky="e"
            )
            self.cont_rat = tk.Entry(master)
            self.cont_rat.insert(0, self.row.cont_rationale)
            self.cont_rat.grid(row=5, column=1)
            ttk.Label(master, text="Exposure").grid(row=6, column=0, sticky="e")
            self.exp_var = tk.StringVar(value=str(self.row.exposure))
            exp_cb = ttk.Combobox(
                master,
                textvariable=self.exp_var,
                values=["1", "2", "3", "4"],
                state="readonly",
            )
            exp_cb.grid(row=6, column=1)
            ttk.Label(master, text="Exposure Rationale").grid(
                row=7, column=0, sticky="e"
            )
            self.exp_rat = tk.Entry(master)
            self.exp_rat.insert(0, self.row.exp_rationale)
            self.exp_rat.grid(row=7, column=1)
            ttk.Label(master, text="ASIL").grid(row=8, column=0, sticky="e")
            self.asil_var = tk.StringVar(value=self.row.asil)
            asil_lbl = ttk.Label(master, textvariable=self.asil_var)
            asil_lbl.grid(row=8, column=1)
            ttk.Label(master, text="Safety Goal").grid(row=9, column=0, sticky="e")
            self.sg_var = tk.StringVar(value=self.row.safety_goal)
            ttk.Combobox(
                master, textvariable=self.sg_var, values=goals, state="readonly"
            ).grid(row=9, column=1)

            def auto_hazard(_=None):
                mal = self.mal_var.get()
                if not mal:
                    return
                hazard_list = hazards_map.get(mal)
                if hazard_list:
                    current = self.haz.get("1.0", "end-1c").strip()
                    if not current:
                        self.haz.delete("1.0", "end")
                        self.haz.insert("1.0", hazard_list[0])

            mal_cb.bind("<<ComboboxSelected>>", auto_hazard)
            auto_hazard()

            def recalc(_=None):
                try:
                    s = int(self.sev_var.get())
                    c = int(self.cont_var.get())
                    e = int(self.exp_var.get())
                except ValueError:
                    self.asil_var.set("QM")
                    return
                self.asil_var.set(calc_asil(s, c, e))

            sev_cb.bind("<<ComboboxSelected>>", recalc)
            cont_cb.bind("<<ComboboxSelected>>", recalc)
            exp_cb.bind("<<ComboboxSelected>>", recalc)
            recalc()

        def apply(self):
            old_mal = self.row.malfunction
            self.row.malfunction = self.mal_var.get()
            if old_mal and old_mal != self.row.malfunction:
                self.app.rename_malfunction(old_mal, self.row.malfunction)
            old_haz = self.row.hazard
            self.row.hazard = self.haz.get("1.0", "end-1c")
            if old_haz and old_haz != self.row.hazard:
                self.app.rename_hazard(old_haz, self.row.hazard)
            self.app.add_hazard(self.row.hazard)
            self.app.update_hazard_severity(self.row.hazard, self.sev_var.get())
            self.row.severity = int(self.app.hazard_severity.get(self.row.hazard, self.sev_var.get()))
            self.row.sev_rationale = self.sev_rat.get()
            self.row.controllability = int(self.cont_var.get())
            self.row.cont_rationale = self.cont_rat.get()
            self.row.exposure = int(self.exp_var.get())
            self.row.exp_rationale = self.exp_rat.get()
            self.row.asil = self.asil_var.get()
            self.row.safety_goal = self.sg_var.get()

    def add_row(self):
        if not self.app.active_hara:
            messagebox.showwarning("Add", "Create a HARA first")
            return
        dlg = self.RowDialog(self, self.app)
        self.app.hara_entries.append(dlg.row)
        if self.app.active_hara:
            self.app.active_hara.status = "draft"
            self.app.active_hara.approved = False
            self.app.invalidate_reviews_for_hara(self.app.active_hara.name)
            self.status_lbl.config(text=f"Status: {self.app.active_hara.status}")
        self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        dlg = self.RowDialog(self, self.app, self.app.hara_entries[idx])
        if self.app.active_hara:
            self.app.active_hara.status = "draft"
            self.app.active_hara.approved = False
            self.app.invalidate_reviews_for_hara(self.app.active_hara.name)
            self.status_lbl.config(text=f"Status: {self.app.active_hara.status}")
        self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.hara_entries):
                del self.app.hara_entries[idx]
        if self.app.active_hara:
            self.app.active_hara.status = "draft"
            self.app.active_hara.approved = False
            self.app.invalidate_reviews_for_hara(self.app.active_hara.name)
            self.status_lbl.config(text=f"Status: {self.app.active_hara.status}")
        self.refresh()

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        if row >= len(self.app.hara_entries):
            return
        entry = self.app.hara_entries[row]
        if column in self.COLS:
            if column in {"severity", "controllability", "exposure"}:
                try:
                    setattr(entry, column, int(value))
                except ValueError:
                    return
            else:
                setattr(entry, column, value)
        self.refresh()

    def approve_doc(self):
        if not self.app.active_hara:
            return
        self.app.active_hara.status = "closed"
        self.app.active_hara.approved = True
        self.app.update_hara_statuses()
        self.app.ensure_asil_consistency()
        self.app.update_views()
        messagebox.showinfo("HARA", "HARA approved")


class TC2FIWindow(tk.Frame):
    COLS = [
        "id",
        "known_use_case",
        "occurrence",
        "impacted_function",
        "arch_elements",
        "interfaces",
        "functional_insufficiencies",
        "vehicle_effect",
        "severity",
        "design_measures",
        "verification",
        "measure_effectiveness",
        "scene",
        "scenario",
        "driver_behavior",
        "triggering_conditions",
        "mitigation",
        "acceptance",
    ]

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("TC2FI Analysis")
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="TC2FI:").pack(side=tk.LEFT)
        self.doc_var = tk.StringVar()
        self.doc_cb = ttk.Combobox(top, textvariable=self.doc_var, state="readonly")
        self.doc_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="New", command=self.new_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Rename", command=self.rename_doc).pack(side=tk.LEFT)
        ttk.Button(top, text="Delete", command=self.delete_doc).pack(side=tk.LEFT)
        self.doc_cb.bind("<<ComboboxSelected>>", self.select_doc)

        if isinstance(master, tk.Toplevel):
            master.geometry("800x400")
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        configure_table_style("TC2FI.Treeview", rowheight=80)
        self.tree = EditableTreeview(
            tree_frame,
            columns=self.COLS,
            show="headings",
            style="TC2FI.Treeview",
            height=4,
            edit_callback=self.on_cell_edit,
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in self.COLS:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=120)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self.edit_row())
        btn = ttk.Frame(self)
        btn.pack()
        ttk.Button(btn, text="Add", command=self.add_row).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn, text="Edit", command=self.edit_row).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn, text="Delete", command=self.del_row).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        ttk.Button(btn, text="Export CSV", command=self.export_csv).pack(
            side=tk.LEFT, padx=2, pady=2
        )
        self.refresh_docs()
        self.refresh()
        if not isinstance(master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.app.tc2fi_entries:
            vals = [_wrap_val(row.get(k, "")) for k in self.COLS]
            self.tree.insert("", "end", values=vals)
        stripe_rows(self.tree)

    class RowDialog(simpledialog.Dialog):
        def __init__(self, parent, app, data=None):
            self.app = app
            default = {k: "" for k in TC2FIWindow.COLS}
            self.data = data or default
            self.selected = {}
            super().__init__(parent, title="Edit Row")

        def body(self, master):
            self.resizable(False, False)
            self.geometry("700x500")
            tc_names = [
                n.user_name or f"TC {n.unique_id}"
                for n in self.app.get_all_triggering_conditions()
            ]
            fi_names = [
                n.user_name or f"FI {n.unique_id}"
                for n in self.app.get_all_functional_insufficiencies()
            ]
            func_names = self.app.get_all_function_names()
            comp_names = self.app.get_all_component_names()
            scen_names = self.app.get_all_scenario_names()
            scene_names = self.app.get_all_scenery_names()
            req_opts = sorted(
                (
                    f"[{r['id']}] {r['text']}"
                    for r in global_requirements.values()
                    if r.get("req_type") == "functional modification"
                ),
                key=str.lower,
            )
            self.widgets = {}
            nb = ttk.Notebook(master)
            nb.pack(fill=tk.BOTH, expand=True)
            categories = {
                "Known Env/Operational Condition": [
                    "id",
                    "known_use_case",
                    "arch_elements",
                    "interfaces",
                    "scene",
                    "scenario",
                    "driver_behavior",
                    "occurrence",
                    "triggering_conditions",
                ],
                "Mitigations": ["mitigation", "acceptance"],
                "Affected Functions Identification": [
                    "impacted_function",
                    "functional_insufficiencies",
                ],
                "Effects": ["vehicle_effect", "severity"],
                "Design Measures": [
                    "design_measures",
                    "verification",
                    "measure_effectiveness",
                ],
            }
            tabs = {name: ttk.Frame(nb) for name in categories}
            for name, frame in tabs.items():
                nb.add(frame, text=name)
            rows = {name: 0 for name in categories}

            def get_frame(col):
                for name, cols in categories.items():
                    if col in cols:
                        r = rows[name]
                        rows[name] += 1
                        return tabs[name], r
                return master, 0

            def refresh_funcs(*_):
                comp = self.widgets.get("arch_elements")
                if isinstance(comp, tk.StringVar):
                    opts = sorted(
                        {
                            e.function
                            for e in self.app.hazop_entries
                            if not comp.get() or e.component == comp.get()
                        }
                    )
                else:
                    opts = func_names
                self.func_options = opts

            for col in TC2FIWindow.COLS:
                frame, r = get_frame(col)
                ttk.Label(frame, text=col.replace("_", " ").title()).grid(
                    row=r, column=0, sticky="e", padx=5, pady=2
                )
                if col == "functional_insufficiencies":
                    fi_frame = ttk.Frame(frame)
                    fi_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.fi_lb = tk.Listbox(fi_frame, selectmode="extended", height=4, exportselection=False)
                    self.fi_lb.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
                    existing = [e.strip() for e in self.data.get(col, "").split(";") if e.strip()]
                    for val in existing:
                        self.fi_lb.insert(tk.END, val)
                    ttk.Button(fi_frame, text="Add New", command=self.add_fi_new).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(fi_frame, text="Edit", command=self.edit_fi).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(fi_frame, text="Delete", command=self.del_fi).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(fi_frame, text="Add Existing", command=self.add_fi_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.fi_lb
                    self.fi_options = fi_names
                elif col == "design_measures":
                    self.dm_ids = [e.strip() for e in self.data.get(col, "").split(",") if e.strip()]
                    dm_frame = ttk.Frame(frame)
                    dm_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.dm_lb = tk.Listbox(dm_frame, height=4, width=50)
                    self.dm_lb.grid(row=0, column=0, columnspan=4, sticky="w")
                    for rid in self.dm_ids:
                        req = global_requirements.get(rid, {"id": rid, "text": ""})
                        self.dm_lb.insert(tk.END, f"[{req['id']}] {req.get('text','')}")
                    ttk.Button(dm_frame, text="Add New", command=self.add_dm_new).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(dm_frame, text="Edit", command=self.edit_dm).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(dm_frame, text="Delete", command=self.del_dm).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(dm_frame, text="Add Existing", command=self.add_dm_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.dm_lb
                elif col == "mitigation":
                    mit_frame = ttk.Frame(frame)
                    mit_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.mit_lb = tk.Listbox(mit_frame, height=4, width=50)
                    self.mit_lb.grid(row=0, column=0, columnspan=4, sticky="w")
                    self.mit_ids = [e.strip() for e in self.data.get(col, "").split(",") if e.strip()]
                    for rid in self.mit_ids:
                        req = global_requirements.get(rid, {"id": rid, "text": ""})
                        self.mit_lb.insert(tk.END, f"[{req['id']}] {req.get('text','')}")
                    ttk.Button(mit_frame, text="Add New", command=self.add_mit_new).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(mit_frame, text="Edit", command=self.edit_mit).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(mit_frame, text="Delete", command=self.del_mit).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(mit_frame, text="Add Existing", command=self.add_mit_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.mit_lb
                elif col == "triggering_conditions":
                    tc_frame = ttk.Frame(frame)
                    tc_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.tc_lb = tk.Listbox(tc_frame, selectmode="extended", height=5, exportselection=False)
                    self.tc_lb.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
                    existing = [e.strip() for e in self.data.get(col, "").split(";") if e.strip()]
                    for val in existing:
                        self.tc_lb.insert(tk.END, val)
                    ttk.Button(tc_frame, text="Add", command=self.add_tc).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(tc_frame, text="Edit", command=self.edit_tc).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(tc_frame, text="Delete", command=self.del_tc).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(tc_frame, text="Add Existing", command=self.add_tc_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.tc_lb
                elif col == "impacted_function":
                    func_frame = ttk.Frame(frame)
                    func_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.func_lb = tk.Listbox(func_frame, selectmode="extended", height=4, exportselection=False)
                    self.func_lb.grid(row=0, column=0, columnspan=3, padx=2, pady=2)
                    existing = [f.strip() for f in self.data.get(col, "").split(",") if f.strip()]
                    for val in existing:
                        self.func_lb.insert(tk.END, val)
                    ttk.Button(func_frame, text="Add Existing", command=self.add_func_existing).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(func_frame, text="Remove", command=self.del_func).grid(row=1, column=1, padx=2, pady=2)
                    self.widgets[col] = self.func_lb
                elif col == "vehicle_effect":
                    haz_frame = ttk.Frame(frame)
                    haz_frame.grid(row=r, column=1, padx=5, pady=2, sticky="w")
                    self.haz_lb = tk.Listbox(haz_frame, selectmode="extended", height=4, exportselection=False)
                    self.haz_lb.grid(row=0, column=0, columnspan=4, padx=2, pady=2)
                    existing = [h.strip() for h in self.data.get(col, "").split(",") if h.strip()]
                    for val in existing:
                        self.haz_lb.insert(tk.END, val)
                    ttk.Button(haz_frame, text="Add New", command=self.add_haz_new).grid(row=1, column=0, padx=2, pady=2)
                    ttk.Button(haz_frame, text="Edit", command=self.edit_haz).grid(row=1, column=1, padx=2, pady=2)
                    ttk.Button(haz_frame, text="Delete", command=self.del_haz).grid(row=1, column=2, padx=2, pady=2)
                    ttk.Button(haz_frame, text="Add Existing", command=self.add_haz_existing).grid(row=1, column=3, padx=2, pady=2)
                    self.widgets[col] = self.haz_lb
                elif col == "arch_elements":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame, textvariable=var, values=comp_names, state="readonly"
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    cb.bind("<<ComboboxSelected>>", refresh_funcs)
                    self.widgets[col] = var
                elif col == "scene":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame, textvariable=var, values=scene_names, state="readonly"
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "scenario":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame, textvariable=var, values=scen_names, state="readonly"
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                elif col == "severity":
                    var = tk.StringVar(value=self.data.get(col, ""))
                    cb = ttk.Combobox(
                        frame,
                        textvariable=var,
                        values=["1", "2", "3"],
                        state="readonly",
                    )
                    cb.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = var
                else:
                    txt = tk.Text(frame, width=25, height=2, wrap="word")
                    txt.insert("1.0", self.data.get(col, ""))
                    if col == "known_use_case":
                        self.kuc_widget = txt
                        txt.configure(state="disabled")
                    txt.grid(row=r, column=1, padx=5, pady=2)
                    self.widgets[col] = txt
                    if col == "known_use_case":
                        self.kuc_widget = txt
            refresh_funcs()
            self.update_known_use_case()

        def apply(self):
            for col, widget in self.widgets.items():
                if isinstance(widget, tk.Entry):
                    self.data[col] = widget.get()
                elif isinstance(widget, tk.Text):
                    self.data[col] = widget.get("1.0", "end-1c")
                elif isinstance(widget, tk.Listbox):
                    items = list(widget.get(0, tk.END))
                    if col in ("triggering_conditions", "functional_insufficiencies"):
                        self.data[col] = ";".join(items)
                    else:
                        self.data[col] = ",".join(items)
                else:
                    val = widget.get()
                    orig = self.selected.get(col, "")
                    if col == "triggering_conditions" and orig and val != orig:
                        self.app.rename_triggering_condition(orig, val)
                    elif col == "vehicle_effect" and orig and val != orig:
                        self.app.rename_hazard(orig, val)
                    self.data[col] = val
            veh = self.data.get("vehicle_effect", "").strip()
            sev = self.data.get("severity", "1").strip()
            if veh:
                self.app.add_hazard(veh)
                self.app.update_hazard_severity(veh, sev)
            self.result = True

        def add_dm_new(self):
            dlg = _RequirementDialog(self, req_type="functional modification")
            if dlg.result:
                req = dlg.result
                global_requirements[req["id"]] = req
                text = f"[{req['id']}] {req['text']}"
                self.dm_lb.insert(tk.END, text)

        def add_dm_existing(self):
            dlg = _SelectRequirementsDialog(self, req_type="functional modification")
            if dlg.result:
                for val in dlg.result:
                    if val not in self.dm_lb.get(0, tk.END):
                        self.dm_lb.insert(tk.END, val)

        def edit_dm(self):
            sel = self.dm_lb.curselection()
            if not sel:
                return
            text = self.dm_lb.get(sel[0])
            rid = text.split("]", 1)[0][1:]
            req = global_requirements.get(rid, {"id": rid, "text": text})
            dlg = _RequirementDialog(self, req, req_type="functional modification")
            if dlg.result:
                new_req = dlg.result
                global_requirements[new_req["id"]] = new_req
                new_text = f"[{new_req['id']}] {new_req['text']}"
                self.dm_lb.delete(sel[0])
                self.dm_lb.insert(sel[0], new_text)

        def del_dm(self):
            sel = list(self.dm_lb.curselection())
            for idx in reversed(sel):
                self.dm_lb.delete(idx)

        def add_tc_existing(self):
            dlg = _SelectTriggeringConditionsDialog(self, self.app.triggering_conditions)
            if dlg.result:
                for val in dlg.result:
                    if val not in self.tc_lb.get(0, tk.END):
                        self.tc_lb.insert(tk.END, val)

        def add_tc(self):
            name = simpledialog.askstring("Triggering Condition", "Name:")
            if name:
                if name not in self.tc_lb.get(0, tk.END):
                    self.tc_lb.insert(tk.END, name)

        def edit_tc(self):
            sel = self.tc_lb.curselection()
            if not sel:
                return
            current = self.tc_lb.get(sel[0])
            name = simpledialog.askstring("Triggering Condition", "Name:", initialvalue=current)
            if name and name != current:
                self.app.rename_triggering_condition(current, name)
                self.tc_lb.delete(sel[0])
                self.tc_lb.insert(sel[0], name)

        def del_tc(self):
            sel = list(self.tc_lb.curselection())
            for idx in reversed(sel):
                self.tc_lb.delete(idx)

        def add_mit_new(self):
            dlg = _RequirementDialog(self, req_type="operational")
            if dlg.result:
                req = dlg.result
                global_requirements[req["id"]] = req
                text = f"[{req['id']}] {req['text']}"
                self.mit_lb.insert(tk.END, text)

        def add_mit_existing(self):
            dlg = _SelectRequirementsDialog(self, req_type="operational")
            if dlg.result:
                for val in dlg.result:
                    if val not in self.mit_lb.get(0, tk.END):
                        self.mit_lb.insert(tk.END, val)
        def add_fi_new(self):
            name = simpledialog.askstring("Functional Insufficiency", "Name:")
            if name:
                if name not in self.fi_lb.get(0, tk.END):
                    self.fi_lb.insert(tk.END, name)
                self.update_known_use_case()

        def add_fi_existing(self):
            dlg = _SelectFIsDialog(self, self.fi_options)
            if getattr(dlg, "result", None):
                for val in dlg.result:
                    if val not in self.fi_lb.get(0, tk.END):
                        self.fi_lb.insert(tk.END, val)
                self.update_known_use_case()

        def edit_fi(self):
            sel = self.fi_lb.curselection()
            if not sel:
                return
            current = self.fi_lb.get(sel[0])
            name = simpledialog.askstring("Functional Insufficiency", "Name:", initialvalue=current)
            if name and name != current:
                self.app.rename_functional_insufficiency(current, name)
                self.fi_lb.delete(sel[0])
                self.fi_lb.insert(sel[0], name)
            self.update_known_use_case()

        def del_fi(self):
            sel = list(self.fi_lb.curselection())
            for idx in reversed(sel):
                self.fi_lb.delete(idx)
            self.update_known_use_case()

        def edit_mit(self):
            sel = self.mit_lb.curselection()
            if not sel:
                return
            text = self.mit_lb.get(sel[0])
            rid = text.split("]", 1)[0][1:]
            req = global_requirements.get(rid, {"id": rid, "text": text})
            dlg = _RequirementDialog(self, req, req_type="operational")
            if dlg.result:
                new_req = dlg.result
                global_requirements[new_req["id"]] = new_req
                new_text = f"[{new_req['id']}] {new_req['text']}"
                self.mit_lb.delete(sel[0])
                self.mit_lb.insert(sel[0], new_text)

        def del_mit(self):
            sel = list(self.mit_lb.curselection())
            for idx in reversed(sel):
                self.mit_lb.delete(idx)

        def add_func_existing(self):
            dlg = _SelectFunctionsDialog(self, self.func_options)
            if getattr(dlg, "result", None):
                for val in dlg.result:
                    if val not in self.func_lb.get(0, tk.END):
                        self.func_lb.insert(tk.END, val)
                self.update_known_use_case()

        def del_func(self):
            sel = list(self.func_lb.curselection())
            for idx in reversed(sel):
                self.func_lb.delete(idx)
            self.update_known_use_case()

        def add_haz_new(self):
            name = simpledialog.askstring("Hazard", "Name:")
            if name:
                if name not in self.haz_lb.get(0, tk.END):
                    self.haz_lb.insert(tk.END, name)
                sev_widget = self.widgets.get("severity")
                sev = sev_widget.get() if isinstance(sev_widget, tk.StringVar) else "1"
                self.app.add_hazard(name)
                self.app.update_hazard_severity(name, sev)

        def add_haz_existing(self):
            dlg = _SelectHazardsDialog(self, self.app.hazards)
            if getattr(dlg, "result", None):
                for val in dlg.result:
                    if val not in self.haz_lb.get(0, tk.END):
                        self.haz_lb.insert(tk.END, val)

        def edit_haz(self):
            sel = self.haz_lb.curselection()
            if not sel:
                return
            current = self.haz_lb.get(sel[0])
            name = simpledialog.askstring("Hazard", "Name:", initialvalue=current)
            if name and name != current:
                self.app.rename_hazard(current, name)
                self.haz_lb.delete(sel[0])
                self.haz_lb.insert(sel[0], name)

        def del_haz(self):
            sel = list(self.haz_lb.curselection())
            for idx in reversed(sel):
                self.haz_lb.delete(idx)

        def update_known_use_case(self):
            if not hasattr(self, "kuc_widget"):
                return
            funcs = list(self.func_lb.get(0, tk.END)) if hasattr(self, "func_lb") else []
            fis = list(self.fi_lb.get(0, tk.END)) if hasattr(self, "fi_lb") else []
            ucs = []
            for f in funcs + fis:
                uc = self.app.get_use_case_for_function(f)
                if uc and uc not in ucs:
                    ucs.append(uc)
            self.kuc_widget.delete("1.0", tk.END)
            self.kuc_widget.insert("1.0", ";".join(ucs))

    def add_row(self):
        dlg = self.RowDialog(self, self.app)
        if getattr(dlg, "result", None):
            self.app.tc2fi_entries.append(dlg.data)
            self.refresh()

    def edit_row(self):
        sel = self.tree.focus()
        if not sel:
            return
        idx = self.tree.index(sel)
        data = self.app.tc2fi_entries[idx]
        dlg = self.RowDialog(self, self.app, data)
        if getattr(dlg, "result", None):
            self.refresh()

    def del_row(self):
        sel = self.tree.selection()
        for iid in sel:
            idx = self.tree.index(iid)
            if idx < len(self.app.tc2fi_entries):
                del self.app.tc2fi_entries[idx]
        self.refresh()

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        if row >= len(self.app.tc2fi_entries):
            return
        self.app.tc2fi_entries[row][column] = value
        self.refresh()

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(self.COLS)
            for r in self.app.tc2fi_entries:
                w.writerow([r.get(k, "") for k in self.COLS])
        messagebox.showinfo("Export", "TC2FI exported")

    def refresh_docs(self):
        names = [d.name for d in self.app.tc2fi_docs]
        self.doc_cb.configure(values=names)
        if self.app.active_tc2fi:
            self.doc_var.set(self.app.active_tc2fi.name)
        elif names:
            self.doc_var.set(names[0])

    def select_doc(self, *_):
        name = self.doc_var.get()
        for d in self.app.tc2fi_docs:
            if d.name == name:
                self.app.active_tc2fi = d
                self.app.tc2fi_entries = d.entries
                break
        self.refresh()

    def new_doc(self):
        name = simpledialog.askstring("New TC2FI", "Name:")
        if not name:
            return
        doc = TC2FIDoc(name, [])
        self.app.tc2fi_docs.append(doc)
        self.app.active_tc2fi = doc
        self.app.tc2fi_entries = doc.entries
        self.refresh_docs()
        self.refresh()
        self.app.update_views()

    def rename_doc(self):
        if not self.app.active_tc2fi:
            return
        name = simpledialog.askstring(
            "Rename TC2FI", "Name:", initialvalue=self.app.active_tc2fi.name
        )
        if not name:
            return
        self.app.active_tc2fi.name = name
        self.refresh_docs()
        self.app.update_views()

    def delete_doc(self):
        doc = self.app.active_tc2fi
        if not doc:
            return
        if not messagebox.askyesno("Delete", f"Delete TC2FI '{doc.name}'?"):
            return
        self.app.tc2fi_docs.remove(doc)
        if self.app.tc2fi_docs:
            self.app.active_tc2fi = self.app.tc2fi_docs[0]
        else:
            self.app.active_tc2fi = None
        self.app.tc2fi_entries = (
            self.app.active_tc2fi.entries if self.app.active_tc2fi else []
        )
        self.refresh_docs()
        self.refresh()
        self.app.update_views()


class HazardExplorerWindow(tk.Toplevel):
    """Read-only list of hazards per HARA."""

    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("Hazard Explorer")

        columns = ("HARA", "Malfunction", "Hazard", "Severity")
        configure_table_style("HazExp.Treeview")
        self.tree = EditableTreeview(
            self,
            columns=columns,
            show="headings",
            style="HazExp.Treeview",
            edit_callback=self.on_cell_edit,
        )
        for c in columns:
            self.tree.heading(c, text=c)
            width = 200 if c == "Hazard" else 120
            self.tree.column(c, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self, text="Export CSV", command=self.export_csv).pack(pady=5)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for doc in self.app.hara_docs:
            for e in doc.entries:
                haz = getattr(e, "hazard", "")
                sev = self.app.hazard_severity.get(haz, "")
                self.tree.insert(
                    "",
                    "end",
                    values=(doc.name, e.malfunction, haz, sev),
                )

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["HARA", "Malfunction", "Hazard", "Severity"])
            for iid in self.tree.get_children():
                w.writerow(self.tree.item(iid, "values"))
        messagebox.showinfo("Export", "Hazards exported")

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        values = list(self.tree.item(self.tree.get_children()[row], "values"))
        idx = ("HARA", "Malfunction", "Hazard", "Severity").index(column)
        values[idx] = value
        self.tree.item(self.tree.get_children()[row], values=values)


class RequirementsExplorerWindow(tk.Toplevel):
    """Read-only list of global requirements with filter options."""

    STATUSES = ["", "draft", "in review", "peer reviewed", "pending approval", "approved"]

    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("Requirements Explorer")

        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(filter_frame, text="Text:").grid(row=0, column=0, sticky="e")
        self.query_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.query_var, width=20).grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Type:").grid(row=0, column=2, sticky="e")
        self.type_var = tk.StringVar()
        ttk.Combobox(
            filter_frame,
            textvariable=self.type_var,
            values=[""] + REQUIREMENT_TYPE_OPTIONS,
            state="readonly",
            width=18,
        ).grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="ASIL:").grid(row=0, column=4, sticky="e")
        self.asil_var = tk.StringVar()
        ttk.Combobox(
            filter_frame,
            textvariable=self.asil_var,
            values=[""] + ASIL_LEVEL_OPTIONS,
            state="readonly",
            width=6,
        ).grid(row=0, column=5, padx=5)

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=6, sticky="e")
        self.status_var = tk.StringVar()
        ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=self.STATUSES,
            state="readonly",
            width=15,
        ).grid(row=0, column=7, padx=5)

        tk.Button(filter_frame, text="Apply", command=self.refresh).grid(row=0, column=8, padx=5)

        columns = ("ID", "ASIL", "Type", "Status", "Parent", "Text")
        configure_table_style("ReqExp.Treeview")
        self.tree = EditableTreeview(
            self,
            columns=columns,
            show="headings",
            style="ReqExp.Treeview",
            edit_callback=self.on_cell_edit,
        )
        for c in columns:
            self.tree.heading(c, text=c)
            width = 100 if c != "Text" else 300
            self.tree.column(c, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self, text="Export CSV", command=self.export_csv).pack(pady=5)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        query = self.query_var.get().strip().lower()
        rtype = self.type_var.get().strip()
        asil = self.asil_var.get().strip()
        status = self.status_var.get().strip()
        for req in global_requirements.values():
            if query and query not in req.get("id", "").lower() and query not in req.get("text", "").lower():
                continue
            if rtype and req.get("req_type") != rtype:
                continue
            if asil and req.get("asil") != asil:
                continue
            if status and req.get("status", "") != status:
                continue
            self.tree.insert(
                "",
                "end",
                values=(
                    req.get("id", ""),
                    req.get("asil", ""),
                    req.get("req_type", ""),
                    req.get("status", ""),
                    req.get("parent_id", ""),
                    req.get("text", ""),
                ),
            )

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ID", "ASIL", "Type", "Status", "Parent", "Text"])
            for iid in self.tree.get_children():
                w.writerow(self.tree.item(iid, "values"))
        messagebox.showinfo("Export", "Requirements exported")

    def on_cell_edit(self, row: int, column: str, value: str) -> None:
        values = list(self.tree.item(self.tree.get_children()[row], "values"))
        idx_map = {"ID":0, "ASIL":1, "Type":2, "Status":3, "Parent":4, "Text":5}
        if column in idx_map:
            values[idx_map[column]] = value
            self.tree.item(self.tree.get_children()[row], values=values)
