import unittest
import types
import os
import sys
import copy

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp
from gsn.nodes import GSNNode


class GSNCloneRelationshipTests(unittest.TestCase):
    def test_reset_clone_clears_relationships(self):
        app = AutoMLApp.__new__(AutoMLApp)
        parent = GSNNode("parent", "Goal")
        child = GSNNode("child", "Goal")
        parent.add_child(child)
        clone = copy.deepcopy(parent)
        old_child = clone.children[0]
        app._reset_gsn_clone(clone)
        self.assertEqual(clone.children, [])
        self.assertEqual(clone.parents, [])
        self.assertEqual(clone.context_children, [])
        self.assertEqual(old_child.children, [])
        self.assertEqual(old_child.parents, [])
        self.assertEqual(old_child.context_children, [])

    def test_reset_clone_preserves_away_properties(self):
        app = AutoMLApp.__new__(AutoMLApp)
        orig = GSNNode("orig", "Goal")
        clone = orig.clone()
        deep_clone = copy.deepcopy(clone)
        app._reset_gsn_clone(deep_clone)
        self.assertIsNot(deep_clone.original, deep_clone)
        self.assertFalse(deep_clone.is_primary_instance)

    def test_paste_node_clones_gsn_nodes(self):
        import types
        import AutoML as automl_module

        automl_module.messagebox = types.SimpleNamespace(
            showwarning=lambda *a, **k: None,
            showinfo=lambda *a, **k: None,
        )
        automl_module.AutoML_Helper = types.SimpleNamespace(
            calculate_assurance_recursive=lambda *a, **k: None
        )

        app = AutoMLApp.__new__(AutoMLApp)
        app.analysis_tree = types.SimpleNamespace(selection=lambda: [])
        parent1 = GSNNode("p1", "Goal")
        parent2 = GSNNode("p2", "Goal")
        child = GSNNode("c", "Goal")
        parent1.add_child(child)
        app.clipboard_node = child
        app.clipboard_relation = "solved"
        app.selected_node = parent2
        app.root_node = parent1
        app.top_events = []
        app.update_views = lambda: None
        app.cut_mode = False

        class Diagram:
            def __init__(self, nodes):
                self.nodes = nodes

            def add_node(self, n):
                if n not in self.nodes:
                    self.nodes.append(n)

        diagram_a = Diagram([child])
        diagram_b = Diagram([])

        def fake_find(node):
            return diagram_a if node is app.clipboard_node else diagram_b

        app._find_gsn_diagram = fake_find

        app.paste_node()

        self.assertEqual(len(parent2.children), 1)
        pasted = parent2.children[0]
        self.assertIsNot(pasted, child)
        self.assertFalse(pasted.is_primary_instance)
        self.assertIs(pasted.original, child.original)

if __name__ == "__main__":
    unittest.main()
