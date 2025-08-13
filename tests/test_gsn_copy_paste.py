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
from gsn import GSNNode, GSNDiagram
from gui import messagebox


class DummyTree:
    def selection(self):
        return ()
    def item(self, iid, attr):
        return None


class GSNCopyPasteTests(unittest.TestCase):
    def setUp(self):
        self.app = FaultTreeApp.__new__(FaultTreeApp)
        self.app.root_node = FaultTreeNode("root", "TOP EVENT")
        self.app.analysis_tree = DummyTree()
        self.app.top_events = []
        self.app.update_views = lambda: None

        root = GSNNode("G1", "Goal")
        child = GSNNode("S1", "Strategy")
        root.add_child(child)
        other = GSNNode("G2", "Goal")
        diagram = GSNDiagram(root)
        diagram.add_node(child)
        diagram.add_node(other)
        self.diagram = diagram
        self.child = child
        self.other = other

        self.app.gsn_diagrams = [diagram]
        self.app.gsn_modules = []
        self.app.selected_node = child

        # suppress message boxes during tests
        self._orig_info = messagebox.showinfo
        self._orig_warn = messagebox.showwarning
        messagebox.showinfo = lambda *a, **k: None
        messagebox.showwarning = lambda *a, **k: None

    def tearDown(self):
        messagebox.showinfo = self._orig_info
        messagebox.showwarning = self._orig_warn

    def test_pasted_node_added_to_diagram(self):
        self.app.copy_node()
        self.app.selected_node = self.other  # paste into a different goal
        self.app.paste_node()
        self.assertEqual(len(self.diagram.nodes), 4)
        self.assertEqual(len(self.other.children), 1)
        cloned = self.other.children[0]
        self.assertIsNot(cloned, self.child)
        self.assertIn(cloned, self.diagram.nodes)


if __name__ == "__main__":
    unittest.main()
