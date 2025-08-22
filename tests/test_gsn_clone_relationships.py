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


if __name__ == "__main__":
    unittest.main()
