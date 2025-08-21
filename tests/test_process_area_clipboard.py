import unittest
import types
import sys

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

import tkinter as tk
from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class ProcessAreaClipboardTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk not available")
        self.root.withdraw()
        self.win1 = SysMLDiagramWindow(self.root, "Diag1", [])
        self.win2 = SysMLDiagramWindow(self.root, "Diag2", [])
        self.boundary = SysMLObject(obj_id=1, obj_type="System Boundary", x=0, y=0)
        self.wp1 = SysMLObject(
            obj_id=2,
            obj_type="Work Product",
            x=-10,
            y=0,
            properties={"boundary": "1"},
        )
        self.wp2 = SysMLObject(
            obj_id=3,
            obj_type="Work Product",
            x=10,
            y=0,
            properties={"boundary": "1"},
        )
        self.win1.objects.extend([self.boundary, self.wp1, self.wp2])

    def tearDown(self):
        self.root.destroy()

    def test_copy_work_product_copies_boundary(self):
        self.win1.selected_obj = self.wp1
        self.win1.copy_selected()
        self.win2.paste_selected()
        self.assertEqual(len(self.win2.objects), 2)
        types = {o.obj_type for o in self.win2.objects}
        self.assertEqual(types, {"System Boundary", "Work Product"})

    def test_cut_work_product_cuts_boundary_and_children(self):
        self.win1.selected_obj = self.wp1
        self.win1.cut_selected()
        self.assertEqual(self.win1.objects, [])
        self.win2.paste_selected()
        types = [o.obj_type for o in self.win2.objects]
        self.assertEqual(types.count("System Boundary"), 1)
        self.assertEqual(types.count("Work Product"), 2)


if __name__ == "__main__":
    unittest.main()
