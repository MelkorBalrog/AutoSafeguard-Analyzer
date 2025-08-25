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

import tkinter as tk
from tkinter import ttk, simpledialog

from gui.controls.mac_button_style import apply_purplish_button_style


class UserInfoDialog(simpledialog.Dialog):
    """Prompt for the user's name and email."""

    def __init__(self, parent, name: str = "", email: str = ""):
        self._name = name
        self._email = email
        super().__init__(parent, title="User Information")

    def body(self, master):
        # Disable resizing to keep the dialog size fixed
        self.resizable(False, False)
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e")
        self.name_var = tk.StringVar(value=self._name)
        name_entry = ttk.Entry(master, textvariable=self.name_var)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(master, text="Email:").grid(row=1, column=0, sticky="e")
        self.email_var = tk.StringVar(value=self._email)
        ttk.Entry(master, textvariable=self.email_var).grid(
            row=1, column=1, padx=5, pady=5
        )
        return name_entry

    def apply(self):
        self.result = (
            self.name_var.get().strip(),
            self.email_var.get().strip(),
        )

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
