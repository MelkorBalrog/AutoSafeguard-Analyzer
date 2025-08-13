import unittest
import types
import os
import sys

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import FaultTreeApp, FaultTreeNode
from gui import messagebox


class DummyTree:
    def __init__(self, node):
        self._sel = ("item1",)
        self._meta = {"item1": {"tags": (str(node.unique_id),)}}
    def selection(self):
        return self._sel
    def item(self, iid, attr):
        return self._meta[iid][attr]


class CopyPasteSelectionTests(unittest.TestCase):
    def setUp(self):
        self.app = FaultTreeApp.__new__(FaultTreeApp)
        self.app.root_node = FaultTreeNode("root", "TOP EVENT")
        child = FaultTreeNode("child", "GATE", parent=self.app.root_node)
        self.app.root_node.children.append(child)
        self.child = child
        self.app.selected_node = None
        self.app.clipboard_node = None
        self.app.analysis_tree = DummyTree(child)
        self.app.find_node_by_id = FaultTreeApp.find_node_by_id.__get__(self.app)
        self.app.top_events = []
        self.app.update_views = lambda: None
        self.app.cut_mode = False

    def test_copy_uses_tree_selection_when_no_selected_node(self):
        self.app.copy_node()
        self.assertIs(self.app.clipboard_node, self.child)

    def test_cut_uses_tree_selection_when_no_selected_node(self):
        self.app.cut_node()
        self.assertIs(self.app.clipboard_node, self.child)
        self.assertTrue(self.app.cut_mode)

    def test_copy_prefers_tree_selection_over_root(self):
        self.app.selected_node = self.app.root_node
        self.app.copy_node()
        self.assertIs(self.app.clipboard_node, self.child)

    def test_cut_prefers_tree_selection_over_root(self):
        self.app.selected_node = self.app.root_node
        self.app.cut_node()
        self.assertIs(self.app.clipboard_node, self.child)
        self.assertTrue(self.app.cut_mode)

    def test_paste_warns_when_clipboard_empty_first(self):
        warnings = []
        orig = messagebox.showwarning
        messagebox.showwarning = lambda title, msg: warnings.append((title, msg))
        try:
            self.app.paste_node()
        finally:
            messagebox.showwarning = orig
        self.assertEqual(warnings[0][1], "Clipboard is empty.")


if __name__ == "__main__":
    unittest.main()

