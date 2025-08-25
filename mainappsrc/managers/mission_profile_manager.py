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

"""Mission profile management helpers."""

import tkinter as tk
from tkinter import ttk, simpledialog

from analysis.models import MissionProfile


class MissionProfileManager:
    """Manage mission profiles for :class:`AutoMLApp`."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # ------------------------------------------------------------------
    def manage_mission_profiles(self) -> None:
        app = self.app
        if hasattr(app, "_mp_tab") and app._mp_tab.winfo_exists():
            app.doc_nb.select(app._mp_tab)
            return
        app._mp_tab = app.lifecycle_ui._new_tab("Mission Profiles")
        win = app._mp_tab
        listbox = tk.Listbox(win, height=8, width=40)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)

        def refresh():
            listbox.delete(0, tk.END)
            for mp in app.mission_profiles:
                if mp is None:
                    continue
                info = (
                    f"{mp.name} (on: {mp.tau_on}h, off: {mp.tau_off}h, "
                    f"board: {mp.board_temp}\u00b0C, ambient: {mp.ambient_temp}\u00b0C)"
                )
                listbox.insert(tk.END, info)

        class MPDialog(simpledialog.Dialog):
            def __init__(self, master, mp=None):
                self.mp = mp
                super().__init__(master)

            def body(self, master):
                self.vars = {}
                fields = [
                    ("Name", "name"),
                    ("TAU On (h)", "tau_on"),
                    ("TAU Off (h)", "tau_off"),
                    ("Board Temp (\u00b0C)", "board_temp"),
                    ("Board Temp Min (\u00b0C)", "board_temp_min"),
                    ("Board Temp Max (\u00b0C)", "board_temp_max"),
                    ("Ambient Temp (\u00b0C)", "ambient_temp"),
                    ("Ambient Temp Min (\u00b0C)", "ambient_temp_min"),
                    ("Ambient Temp Max (\u00b0C)", "ambient_temp_max"),
                    ("Humidity (%)", "humidity"),
                    ("Duty Cycle", "duty_cycle"),
                    ("Notes", "notes"),
                ]
                self.entries = {}
                for row, (label, key) in enumerate(fields):
                    ttk.Label(master, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
                    var = tk.StringVar()
                    if self.mp:
                        var.set(str(getattr(self.mp, key)))
                    state = "readonly" if key == "duty_cycle" else "normal"
                    entry = ttk.Entry(master, textvariable=var, state=state)
                    entry.grid(row=row, column=1, padx=5, pady=5)
                    self.vars[key] = var
                    self.entries[key] = entry

                def update_dc(*_):
                    try:
                        on = float(self.vars["tau_on"].get() or 0)
                        off = float(self.vars["tau_off"].get() or 0)
                        total = on + off
                        dc = on / total if total else 0.0
                    except ValueError:
                        dc = 0.0
                    self.vars["duty_cycle"].set(str(dc))

                self.vars["tau_on"].trace_add("write", update_dc)
                self.vars["tau_off"].trace_add("write", update_dc)
                update_dc()

            def apply(self):
                vals = {k: v.get() for k, v in self.vars.items()}
                tau_on = float(vals.get("tau_on") or 0.0)
                tau_off = float(vals.get("tau_off") or 0.0)
                total = tau_on + tau_off
                dc = tau_on / total if total else 0.0
                if self.mp is None:
                    mp = MissionProfile(
                        vals["name"],
                        tau_on,
                        tau_off,
                        float(vals["board_temp"] or 25.0),
                        float(vals["board_temp_min"] or 25.0),
                        float(vals["board_temp_max"] or 25.0),
                        float(vals["ambient_temp"] or 25.0),
                        float(vals["ambient_temp_min"] or 25.0),
                        float(vals["ambient_temp_max"] or 25.0),
                        float(vals["humidity"] or 50.0),
                        dc,
                        vals["notes"],
                    )
                    self.result = mp
                else:
                    self.mp.name = vals["name"]
                    self.mp.tau_on = tau_on
                    self.mp.tau_off = tau_off
                    self.mp.board_temp = float(vals["board_temp"] or 25.0)
                    self.mp.board_temp_min = float(vals["board_temp_min"] or 25.0)
                    self.mp.board_temp_max = float(vals["board_temp_max"] or 25.0)
                    self.mp.ambient_temp = float(vals["ambient_temp"] or 25.0)
                    self.mp.ambient_temp_min = float(vals["ambient_temp_min"] or 25.0)
                    self.mp.ambient_temp_max = float(vals["ambient_temp_max"] or 25.0)
                    self.mp.humidity = float(vals["humidity"] or 50.0)
                    self.mp.duty_cycle = dc
                    self.mp.notes = vals["notes"]
                    self.result = self.mp

        def add_profile():
            dlg = MPDialog(win)
            if getattr(dlg, "result", None) is not None:
                app.mission_profiles.append(dlg.result)
                refresh()
                if hasattr(app, "_rel_window") and app._rel_window.winfo_exists():
                    app._rel_window.refresh_tree()

        def edit_profile():
            sel = listbox.curselection()
            if not sel:
                return
            mp = app.mission_profiles[sel[0]]
            dlg = MPDialog(win, mp)
            if getattr(dlg, "result", None) is not None:
                refresh()
                if hasattr(app, "_rel_window") and app._rel_window.winfo_exists():
                    app._rel_window.refresh_tree()

        def delete_profile():
            sel = listbox.curselection()
            if not sel:
                return
            del app.mission_profiles[sel[0]]
            refresh()
            if hasattr(app, "_rel_window") and app._rel_window.winfo_exists():
                app._rel_window.refresh_tree()

        ttk.Button(btn_frame, text="Add", command=add_profile).pack(fill=tk.X)
        ttk.Button(btn_frame, text="Edit", command=edit_profile).pack(fill=tk.X)
        ttk.Button(btn_frame, text="Delete", command=delete_profile).pack(fill=tk.X)

        refresh()

