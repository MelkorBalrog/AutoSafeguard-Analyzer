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


class CrossDiagramClipboardTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk not available")
        self.root.withdraw()
        self.win1 = SysMLDiagramWindow(self.root, "Diag1", [])
        self.win2 = SysMLDiagramWindow(self.root, "Diag2", [])
        boundary = SysMLObject(obj_id=1, obj_type="System Boundary", x=0, y=0)
        block = SysMLObject(obj_id=2, obj_type="Block", x=0, y=0)
        self.win1.objects.extend([boundary, block])
        self.win1.selected_obj = block

    def tearDown(self):
        self.root.destroy()

    def test_copy_between_diagrams(self):
        self.win1.copy_selected()
        self.win2.paste_selected()
        self.assertEqual(len(self.win2.objects), 1)

    def test_cut_between_diagrams(self):
        self.win1.cut_selected()
        self.assertEqual(len(self.win1.objects), 1)
        self.win2.paste_selected()
        self.assertEqual(len(self.win2.objects), 1)

if __name__ == "__main__":
    unittest.main()
