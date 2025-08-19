import unittest
import types, sys
sys.modules.setdefault('PIL', types.ModuleType('PIL'))
sys.modules.setdefault('PIL.Image', types.ModuleType('PIL.Image'))
sys.modules.setdefault('PIL.ImageDraw', types.ModuleType('PIL.ImageDraw'))
sys.modules.setdefault('PIL.ImageFont', types.ModuleType('PIL.ImageFont'))
sys.modules.setdefault('PIL.ImageTk', types.ModuleType('PIL.ImageTk'))

from AutoML import AutoMLApp, FaultTreeNode


class FunctionalInsufficiencySubtypeTests(unittest.TestCase):
    def test_subtype_nodes_listed(self):
        app = AutoMLApp.__new__(AutoMLApp)
        top = FaultTreeNode("TE", "TOP EVENT")

        fi_type = FaultTreeNode("FI1", "Functional Insufficiency")
        fi_subtype = FaultTreeNode("FI2", "RIGOR LEVEL")
        fi_subtype.input_subtype = "Functional Insufficiency"

        fi_type.parents.append(top)
        fi_subtype.parents.append(top)
        top.children.extend([fi_type, fi_subtype])
        app.top_events = [top]

        fi_nodes = app.get_all_functional_insufficiencies()
        self.assertEqual({fi_type, fi_subtype}, set(fi_nodes))


if __name__ == "__main__":
    unittest.main()
