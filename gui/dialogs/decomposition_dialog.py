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

"""Dialog for selecting requirement decomposition schemes.

This module defines :class:`DecompositionDialog`, which allows a user to
choose a decomposition scheme based on the ASIL level.  It was moved out of
``mainappsrc.automl_core`` to improve modularity and reduce cyclomatic complexity
of the main application file.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog

from analysis.models import ASIL_DECOMP_SCHEMES


class DecompositionDialog(simpledialog.Dialog):
    """Dialog prompting the user to select an ASIL decomposition scheme."""

    def __init__(self, parent: tk.Widget, asil: str) -> None:
        self.asil = asil
        super().__init__(parent, title="Requirement Decomposition")

    def body(self, master: tk.Widget) -> ttk.Widget:  # type: ignore[override]
        ttk.Label(master, text="Select decomposition scheme:").pack(padx=5, pady=5)
        schemes = ASIL_DECOMP_SCHEMES.get(self.asil, [])
        self.scheme_var = tk.StringVar()
        options = [f"{self.asil} -> {a}+{b}" for a, b in schemes] or ["None"]
        self.combo = ttk.Combobox(
            master, textvariable=self.scheme_var, values=options, state="readonly"
        )
        if options:
            self.combo.current(0)
        self.combo.pack(padx=5, pady=5)
        return self.combo

    def apply(self) -> None:  # type: ignore[override]
        val = self.scheme_var.get()
        if "->" in val:
            parts = val.split("->", 1)[1].split("+")
            self.result = (parts[0].strip(), parts[1].strip())
        else:
            self.result = None
