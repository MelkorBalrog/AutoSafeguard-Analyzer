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
from AutoML import AutoMLApp, FaultTreeNode
from gui import messagebox


class DummyTree:
    def __init__(self, node, selection=("item1",)):
        self._sel = selection
        self._meta = {"item1": {"tags": (str(node.unique_id),)}} if selection else {}

    def selection(self):
        return self._sel

    def item(self, iid, attr):
        return self._meta[iid][attr]


class CopyPasteSelectionTests(unittest.TestCase):
    def setUp(self):
        self.app = AutoMLApp.__new__(AutoMLApp)
        self.app.root_node = FaultTreeNode("root", "TOP EVENT")
        child = FaultTreeNode("child", "GATE", parent=self.app.root_node)
        self.app.root_node.children.append(child)
        self.child = child
        self.app.selected_node = None
        self.app.clipboard_node = None
        self.app.analysis_tree = DummyTree(child)
        self.app.find_node_by_id = AutoMLApp.find_node_by_id.__get__(self.app)
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

    def test_copy_uses_selected_node_when_tree_empty(self):
        self.app.analysis_tree = DummyTree(self.child, selection=())
        self.app.selected_node = self.child
        self.app.copy_node()
        self.assertIs(self.app.clipboard_node, self.child)

    def test_cut_uses_selected_node_when_tree_empty(self):
        self.app.analysis_tree = DummyTree(self.child, selection=())
        self.app.selected_node = self.child
        self.app.cut_node()
        self.assertIs(self.app.clipboard_node, self.child)
        self.assertTrue(self.app.cut_mode)

    def test_paste_uses_selected_node_when_tree_empty(self):
        self.app.analysis_tree = DummyTree(self.child, selection=())
        self.app.selected_node = self.child
        self.app.clipboard_node = self.child
        warnings = []
        orig_warn = messagebox.showwarning
        orig_info = getattr(messagebox, "showinfo", lambda *args, **kwargs: None)
        messagebox.showwarning = lambda title, msg: warnings.append((title, msg))
        messagebox.showinfo = lambda *args, **kwargs: None
        try:
            self.app.paste_node()
        finally:
            messagebox.showwarning = orig_warn
            messagebox.showinfo = orig_info
        self.assertEqual(warnings[0][1], "Cannot paste a node onto itself.")

    def test_copy_prefers_selected_node_over_tree(self):
        other = FaultTreeNode("other", "GATE", parent=self.app.root_node)
        self.app.root_node.children.append(other)
        self.app.analysis_tree = DummyTree(other)
        self.app.selected_node = self.child
        self.app.copy_node()
        self.assertIs(self.app.clipboard_node, self.child)

    def test_cut_prefers_selected_node_over_tree(self):
        other = FaultTreeNode("other", "GATE", parent=self.app.root_node)
        self.app.root_node.children.append(other)
        self.app.analysis_tree = DummyTree(other)
        self.app.selected_node = self.child
        self.app.cut_node()
        self.assertIs(self.app.clipboard_node, self.child)
        self.assertTrue(self.app.cut_mode)

    def test_paste_prefers_selected_node_over_tree(self):
        other = FaultTreeNode("other", "GATE", parent=self.app.root_node)
        self.app.root_node.children.append(other)
        self.app.analysis_tree = DummyTree(other)
        self.app.selected_node = self.child
        self.app.clipboard_node = self.child
        warnings = []
        orig_warn = messagebox.showwarning
        orig_info = getattr(messagebox, "showinfo", lambda *args, **kwargs: None)
        messagebox.showwarning = lambda title, msg: warnings.append((title, msg))
        messagebox.showinfo = lambda *args, **kwargs: None
        try:
            self.app.paste_node()
        finally:
            messagebox.showwarning = orig_warn
            messagebox.showinfo = orig_info
        self.assertEqual(warnings[0][1], "Cannot paste a node onto itself.")


if __name__ == "__main__":
    unittest.main()

