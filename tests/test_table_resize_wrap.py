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
import unittest
from types import SimpleNamespace

from gui.safety_case_table import SafetyCaseTable
from analysis.safety_case import SafetyCase


class SafetyCaseTableResizeTests(unittest.TestCase):
    def test_description_wrap_updates_on_column_resize(self):
        try:
            root = tk.Tk()
        except tk.TclError:  # pragma: no cover - skip if display is unavailable
            self.skipTest("Tkinter requires a display")
        sol = SimpleNamespace(
            unique_id="1",
            user_name="Solution",
            description="This description is long enough to require wrapping when displayed in the table.",
            work_product="",
            evidence_link="",
            manager_notes="",
            evidence_sufficient=False,
        )
        case = SafetyCase("Case", None, solutions=[sol])
        table = SafetyCaseTable(root, case)
        root.update_idletasks()

        item = table.tree.get_children()[0]
        initial_lines = table.tree.set(item, "description").count("\n")

        table.tree.column("description", width=400)
        table._adjust_text()
        updated_lines = table.tree.set(item, "description").count("\n")

        self.assertLess(updated_lines, initial_lines)
        root.destroy()


if __name__ == "__main__":
    unittest.main()

