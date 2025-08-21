import unittest
import types
import os
import sys

# Provide dummy PIL modules
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp, FaultTreeNode
from gsn import GSNNode, GSNDiagram
from gui import messagebox

class DummyTree:
    def selection(self):
        return ()
    def item(self, iid, attr):
        return None

class GSNMultiDiagramCopyPasteTests(unittest.TestCase):
    def setUp(self):
        self.app = AutoMLApp.__new__(AutoMLApp)
        self.app.analysis_tree = DummyTree()
        self.app.top_events = []
        self.app.update_views = lambda: None
        self.app.root_node = FaultTreeNode("root", "TOP EVENT")
        self.app.clipboard_node = None
        self.app.cut_mode = False

        root1 = GSNNode("G1", "Goal")
        child1 = GSNNode("S1", "Strategy")
        root1.add_child(child1)
        diag1 = GSNDiagram(root1)
        diag1.add_node(child1)

        root2 = GSNNode("G2", "Goal")
        target2 = GSNNode("S2", "Strategy")
        root2.add_child(target2)
        diag2 = GSNDiagram(root2)
        diag2.add_node(target2)

        self.app.gsn_diagrams = [diag1, diag2]
        self.diag1 = diag1
        self.diag2 = diag2
        self.child1 = child1
        self.target2 = target2
        self.app.selected_node = child1

        # suppress message boxes
        self._orig_info = messagebox.showinfo
        self._orig_warn = messagebox.showwarning
        messagebox.showinfo = lambda *a, **k: None
        messagebox.showwarning = lambda *a, **k: None

    def tearDown(self):
        messagebox.showinfo = self._orig_info
        messagebox.showwarning = self._orig_warn

    def test_copy_between_same_type_diagrams(self):
        self.app.copy_node()
        self.app.selected_node = self.target2
        self.app.paste_node()
        self.assertEqual(len(self.diag2.nodes), 3)

if __name__ == '__main__':
    unittest.main()
