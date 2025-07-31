import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow, add_composite_aggregation_part
from sysml.sysml_repository import SysMLRepository

class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)
    def metrics(self, name: str) -> int:
        return 1

class DummyWindow:
    _object_label_lines = SysMLDiagramWindow._object_label_lines
    def __init__(self, diag_id):
        self.repo = SysMLRepository.get_instance()
        self.zoom = 1.0
        self.font = DummyFont()
        self.diagram_id = diag_id

class AggregationLinkTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_renamed_part_keeps_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part_blk = repo.create_element("Block", name="Part")
        repo.create_relationship(
            "Composite Aggregation",
            whole.elem_id,
            part_blk.elem_id,
            properties={"multiplicity": "2"},
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part_blk.elem_id, "2")
        obj = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        repo.elements[obj["element_id"]].name = "Renamed"
        win = DummyWindow(ibd.diag_id)
        label_lines = win._object_label_lines(SysMLObject(**obj))
        joined = " ".join(label_lines)
        self.assertIn("Renamed : Part [1..2]", joined)

if __name__ == "__main__":
    unittest.main()
