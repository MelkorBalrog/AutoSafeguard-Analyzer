# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

"""Scenario library management helpers."""

import re
import tkinter as tk
from tkinter import ttk, simpledialog

from gui.controls import messagebox
from analysis.safety_management import ACTIVE_TOOLBOX


class ScenarioLibraryManager:
    """Manage scenario libraries for :class:`AutoMLApp`."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # ------------------------------------------------------------------
    def manage_scenario_libraries(self) -> None:
        app = self.app
        if hasattr(app, "_scen_tab") and app._scen_tab.winfo_exists():
            app.doc_nb.select(app._scen_tab)
            return
        app._scen_tab = app.lifecycle_ui._new_tab("Scenario Libraries")
        win = app._scen_tab
        lib_lb = tk.Listbox(win, height=8, width=25)
        lib_lb.grid(row=0, column=0, rowspan=4, sticky="nsew")
        scen_tree = ttk.Treeview(
            win,
            columns=("cls", "beh", "sce", "tc", "fi", "exp", "desc"),
            show="tree headings",
        )
        scen_tree.heading("#0", text="Name")
        scen_tree.column("#0", width=150)
        scen_tree.heading("cls", text="Class")
        scen_tree.column("cls", width=100)
        scen_tree.heading("beh", text="Other Users")
        scen_tree.column("beh", width=140)
        scen_tree.heading("sce", text="Scenery")
        scen_tree.column("sce", width=140)
        scen_tree.heading("tc", text="TC")
        scen_tree.column("tc", width=80)
        scen_tree.heading("fi", text="FI")
        scen_tree.column("fi", width=80)
        scen_tree.heading("exp", text="Exposure")
        scen_tree.column("exp", width=80)
        scen_tree.heading("desc", text="Description")
        scen_tree.column("desc", width=200)
        scen_tree.grid(row=0, column=1, columnspan=3, sticky="nsew")
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(1, weight=1)

        if not hasattr(app, "scenario_icon"):
            app.scenario_icon = app._create_icon("circle", "#1e90ff")

        def refresh_libs():
            lib_lb.delete(0, tk.END)
            for lib in app.scenario_libraries:
                lib_lb.insert(tk.END, lib.get("name", ""))
            refresh_scenarios()

        def refresh_scenarios(*_):
            scen_tree.delete(*scen_tree.get_children())
            sel = lib_lb.curselection()
            if not sel:
                return
            lib = app.scenario_libraries[sel[0]]
            for sc in lib.get("scenarios", []):
                if isinstance(sc, dict):
                    name = sc.get("name", "")
                    cls = sc.get("class", "")
                    beh = sc.get("behavior", "")
                    sce = sc.get("scenery", "")
                    tc = sc.get("tc", "")
                    fi = sc.get("fi", "")
                    exp = sc.get("exposure", "")
                    desc = sc.get("description", "")
                else:
                    name = str(sc)
                    cls = beh = sce = tc = fi = exp = desc = ""
                scen_tree.insert(
                    "",
                    tk.END,
                    text=name,
                    values=(cls, beh, sce, tc, fi, exp, desc),
                    image=app.scenario_icon,
                )

        class LibraryDialog(simpledialog.Dialog):
            def __init__(self, parent, app, data=None):
                self.app = app
                self.data = data or {"name": "", "odds": []}
                super().__init__(parent, title="Edit Library")

            def body(self, master):
                ttk.Label(master, text="Name").grid(row=0, column=0, sticky="e")
                self.name_var = tk.StringVar(value=self.data.get("name", ""))
                ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, sticky="ew")
                ttk.Label(master, text="ODD Libraries").grid(row=1, column=0, sticky="ne")
                toolbox = getattr(self.app, "safety_mgmt_toolbox", None) or ACTIVE_TOOLBOX
                self.allowed_inputs = bool(
                    toolbox and "ODD" in toolbox.analysis_inputs("Scenario Library")
                )
                self.lb = tk.Listbox(master, selectmode=tk.MULTIPLE, height=5)
                if self.allowed_inputs:
                    for i, lib in enumerate(self.app.odd_libraries):
                        self.lb.insert(tk.END, lib.get("name", ""))
                        if lib.get("name", "") in self.data.get("odds", []):
                            self.lb.selection_set(i)
                else:
                    self.lb.configure(state=tk.DISABLED)
                self.lb.grid(row=1, column=1, sticky="nsew")
                master.grid_rowconfigure(1, weight=1)
                master.grid_columnconfigure(1, weight=1)

            def apply(self):
                self.data["name"] = self.name_var.get()
                sels = self.lb.curselection() if self.allowed_inputs else []
                self.data["odds"] = [
                    self.app.odd_libraries[i].get("name", "") for i in sels
                ]

        class ScenarioDialog(simpledialog.Dialog):
            def __init__(self, parent, app, lib, data=None):
                self.app = app
                self.lib = lib
                self.data = data or {
                    "name": "",
                    "class": "",
                    "behavior": "",
                    "action": "",
                    "scenery": "",
                    "tc": "",
                    "fi": "",
                    "exposure": 1,
                    "description": "",
                }
                self.tag_counter = 0
                super().__init__(parent, title="Edit Scenario")

            def body(self, master):
                ttk.Label(master, text="Name").grid(row=0, column=0, sticky="e")
                self.name_var = tk.StringVar(value=self.data.get("name", ""))
                ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, sticky="ew")

                ttk.Label(master, text="Scenario Class").grid(row=1, column=0, sticky="e")
                self.cls_var = tk.StringVar(value=self.data.get("class", ""))
                ttk.Entry(master, textvariable=self.cls_var).grid(row=1, column=1, sticky="ew")

                ttk.Label(master, text="Other Users").grid(row=2, column=0, sticky="e")
                self.beh_var = tk.StringVar(value=self.data.get("behavior", ""))
                ttk.Entry(master, textvariable=self.beh_var).grid(row=2, column=1, sticky="ew")

                ttk.Label(master, text="Action").grid(row=3, column=0, sticky="e")
                self.act_var = tk.StringVar(value=self.data.get("action", ""))
                ttk.Entry(master, textvariable=self.act_var).grid(row=3, column=1, sticky="ew")

                ttk.Label(master, text="Scenery Elements").grid(row=4, column=0, sticky="ne")
                self.elem_list = tk.Listbox(master, selectmode=tk.MULTIPLE, height=5)
                for lib_name in lib.get("odds", []):
                    for l in app.odd_libraries:
                        if l.get("name") == lib_name:
                            for el in l.get("elements", []):
                                val = el.get("name") or el.get("element") or el.get("id")
                                self.elem_list.insert(tk.END, val)
                names = [n.strip() for n in self.data.get("scenery", "").split(",") if n.strip()]
                for i in range(self.elem_list.size()):
                    if self.elem_list.get(i) in names:
                        self.elem_list.selection_set(i)
                self.elem_list.grid(row=4, column=1, sticky="nsew")
                master.grid_rowconfigure(4, weight=1)

                ttk.Label(master, text="TC").grid(row=5, column=0, sticky="e")
                self.tc_var = tk.StringVar(value=self.data.get("tc", ""))
                ttk.Entry(master, textvariable=self.tc_var).grid(row=5, column=1, sticky="ew")

                ttk.Label(master, text="FI").grid(row=6, column=0, sticky="e")
                self.fi_var = tk.StringVar(value=self.data.get("fi", ""))
                ttk.Entry(master, textvariable=self.fi_var).grid(row=6, column=1, sticky="ew")

                ttk.Label(master, text="Exposure").grid(row=7, column=0, sticky="e")
                self.exp_var = tk.StringVar(value=str(self.data.get("exposure", 1)))
                ttk.Entry(master, textvariable=self.exp_var).grid(row=7, column=1, sticky="ew")

                ttk.Label(master, text="Description").grid(row=8, column=0, sticky="ne")
                self.desc = tk.Text(master, width=30, height=5, wrap="word")
                self.desc.grid(row=8, column=1, sticky="nsew")
                master.grid_rowconfigure(8, weight=1)
                self.load_desc_links()

                ttk.Button(master, text="Insert Template", command=self.insert_template).grid(
                    row=9, column=0, columnspan=2, pady=5
                )

            def insert_template(self):
                phrases = []
                cls = self.cls_var.get()
                beh = self.beh_var.get()
                act = self.act_var.get()
                scen = ", ".join(
                    self.elem_list.get(i) for i in self.elem_list.curselection()
                )
                if cls:
                    phrases.append(f"A {cls}")
                if beh:
                    phrases.append(f"with {beh}")
                if act:
                    phrases.append(f"that {act}")
                if scen:
                    phrases.append(f"in {scen}")
                text = " ".join(phrases)
                self.desc.delete("1.0", "end")
                self.desc.insert("1.0", text)
                for m in re.finditer(r"\[\[(.+?)\]\]", text):
                    name = m.group(1)
                    start = f"1.0+{m.start()}c"
                    end = f"1.0+{m.end()}c"
                    tag = f"link{self.tag_counter}"
                    self.tag_counter += 1
                    self.desc.tag_add(tag, start, end)
                    self.desc.tag_config(tag, foreground="blue", underline=1)
                    self.desc.tag_bind(tag, "<Button-1>", lambda e, n=name: self.show_elem(n))

            def load_desc_links(self):
                desc = self.data.get("description", "")
                self.desc.insert("1.0", desc)
                for m in re.finditer(r"\[\[(.+?)\]\]", desc):
                    name = m.group(1)
                    start = f"1.0+{m.start()}c"
                    end = f"1.0+{m.end()}c"
                    tag = f"link{self.tag_counter}"
                    self.tag_counter += 1
                    self.desc.tag_add(tag, start, end)
                    self.desc.tag_config(tag, foreground="blue", underline=1)
                    self.desc.tag_bind(tag, "<Button-1>", lambda e, n=name: self.show_elem(n))

            def show_elem(self, name):
                for lib_name in self.lib.get("odds", []):
                    for l in self.app.odd_libraries:
                        if l.get("name") == lib_name:
                            for el in l.get("elements", []):
                                val = el.get("name") or el.get("element") or el.get("id")
                                if val == name:
                                    msg = "\n".join(f"{k}: {v}" for k, v in el.items())
                                    messagebox.showinfo("ODD Element", msg)
                                    return
                messagebox.showinfo("ODD Element", f"{name}")

            def apply(self):
                self.data["name"] = self.name_var.get()
                self.data["class"] = self.cls_var.get()
                self.data["behavior"] = self.beh_var.get()
                self.data["action"] = self.act_var.get()
                names = [self.elem_list.get(i) for i in self.elem_list.curselection()]
                self.data["scenery"] = ", ".join(names)
                self.data["tc"] = self.tc_var.get()
                self.data["fi"] = self.fi_var.get()
                try:
                    self.data["exposure"] = int(self.exp_var.get())
                except (TypeError, ValueError):
                    self.data["exposure"] = 1
                self.data["description"] = self.desc.get("1.0", "end-1c")

        def add_lib():
            dlg = LibraryDialog(win, self)
            if dlg.data.get("name"):
                app.scenario_libraries.append({"name": dlg.data["name"], "scenarios": [], "odds": dlg.data["odds"]})
                refresh_libs()

        def edit_lib():
            sel = lib_lb.curselection()
            if not sel:
                return
            lib = app.scenario_libraries[sel[0]]
            dlg = LibraryDialog(win, self, lib)
            lib.update(dlg.data)
            refresh_libs()

        def delete_lib():
            sel = lib_lb.curselection()
            if sel:
                idx = sel[0]
                del app.scenario_libraries[idx]
                refresh_libs()

        def add_scen():
            sel = lib_lb.curselection()
            if not sel:
                return
            lib = app.scenario_libraries[sel[0]]
            dlg = ScenarioDialog(win, self, lib)
            if dlg.data.get("name"):
                lib.setdefault("scenarios", []).append(dlg.data)
                refresh_scenarios()

        def edit_scen():
            sel_lib = lib_lb.curselection()
            sel_sc = scen_tree.selection()
            if not sel_lib or not sel_sc:
                return
            lib = app.scenario_libraries[sel_lib[0]]
            idx = scen_tree.index(sel_sc[0])
            data = lib.get("scenarios", [])[idx]
            dlg = ScenarioDialog(win, self, lib, data)
            lib["scenarios"][idx] = dlg.data
            refresh_scenarios()

        def del_scen():
            sel_lib = lib_lb.curselection()
            sel_sc = scen_tree.selection()
            if not sel_lib or not sel_sc:
                return
            lib = app.scenario_libraries[sel_lib[0]]
            idx = scen_tree.index(sel_sc[0])
            del lib.get("scenarios", [])[idx]
            refresh_scenarios()

        btnf = ttk.Frame(win)
        btnf.grid(row=1, column=1, columnspan=3, sticky="ew")
        ttk.Button(btnf, text="Add Lib", command=add_lib).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Edit Lib", command=edit_lib).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Del Lib", command=delete_lib).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Add Scen", command=add_scen).pack(side=tk.LEFT, padx=5)
        ttk.Button(btnf, text="Edit Scen", command=edit_scen).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Del Scen", command=del_scen).pack(side=tk.LEFT)

        lib_lb.bind("<<ListboxSelect>>", refresh_scenarios)
        refresh_libs()
