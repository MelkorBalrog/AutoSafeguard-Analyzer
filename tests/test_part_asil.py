# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import unittest
from gui.architecture import (
    calculate_allocated_asil,
    SysMLObject,
    SysMLDiagramWindow,
)
from analysis.models import global_requirements
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)

    def metrics(self, name: str) -> int:
        return 1


class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        self.zoom = 1.0
        self.font = DummyFont()

    _object_label_lines = SysMLDiagramWindow._object_label_lines

class PartASILTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()
        global_requirements.clear()

    def test_highest_asil(self):
        global_requirements["R1"] = {"id": "R1", "asil": "B"}
        global_requirements["R2"] = {"id": "R2", "asil": "D"}
        reqs = [global_requirements["R1"], global_requirements["R2"]]
        self.assertEqual(calculate_allocated_asil(reqs), "D")

    def test_missing_asil_defaults_qm(self):
        global_requirements["R3"] = {"id": "R3"}
        reqs = [global_requirements["R3"]]
        self.assertEqual(calculate_allocated_asil(reqs), "QM")

    def test_part_asil_visible_without_dialog(self):
        global_requirements["R1"] = {"id": "R1", "asil": "C"}
        elem = self.repo.create_element("Part", name="P")
        diag = self.repo.create_diagram("Block Diagram", name="BD")
        self.repo.add_element_to_diagram(diag.diag_id, elem.elem_id)
        obj_data = {
            "obj_id": 1,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": elem.elem_id,
            "width": 80.0,
            "height": 40.0,
            "properties": {},
            "requirements": [global_requirements["R1"]],
        }
        diag.objects = [obj_data]
        win = DummyWindow()
        # load objects into window (simulating SysMLDiagramWindow init)
        win.objects = [SysMLObject(**obj_data)]
        lines = win._object_label_lines(win.objects[0])
        self.assertIn("ASIL: C", lines)
        self.assertEqual(win.objects[0].properties.get("asil"), "C")

if __name__ == "__main__":
    unittest.main()
