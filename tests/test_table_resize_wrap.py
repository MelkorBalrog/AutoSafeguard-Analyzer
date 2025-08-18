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

