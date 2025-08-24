import types
import os
import sys
import unittest

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

# Ensure repository root is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from AutoML import AutoMLApp, FaultTreeNode
from gui import messagebox


class DummyTree:
    def selection(self):
        return ()

    def item(self, iid, attr):
        return None


class FTACopyPasteTests(unittest.TestCase):
    def setUp(self):
        self.app = AutoMLApp.__new__(AutoMLApp)
        self.app.root_node = FaultTreeNode("root", "TOP EVENT")
        self.app.analysis_tree = DummyTree()
        self.app.top_events = []
        self.app.update_views = lambda: None

        self.child = FaultTreeNode("child", "Basic Event", parent=self.app.root_node)
        self.app.root_node.children.append(self.child)
        self.app.selected_node = self.child

        self._orig_info = messagebox.showinfo
        self._orig_warn = messagebox.showwarning
        messagebox.showinfo = lambda *a, **k: None
        messagebox.showwarning = lambda *a, **k: None

    def tearDown(self):
        messagebox.showinfo = self._orig_info
        messagebox.showwarning = self._orig_warn

    def test_copy_paste_creates_clone(self):
        self.app.copy_node()
        self.app.selected_node = self.app.root_node
        self.app.paste_node()
        self.assertEqual(len(self.app.root_node.children), 2)
        clone = self.app.root_node.children[-1]
        self.assertIsNot(clone, self.child)
        self.assertIs(clone.original, self.child)
        self.assertFalse(clone.is_primary_instance)


if __name__ == "__main__":
    unittest.main()
