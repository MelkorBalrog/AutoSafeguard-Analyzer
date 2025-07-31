import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow
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

class PartMultiplicityLabelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_label_shows_index_and_range(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part_blk = repo.create_element("Block", name="PartB")
        repo.create_relationship(
            "Composite Aggregation",
            whole.elem_id,
            part_blk.elem_id,
            properties={"multiplicity": "1..*"},
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        elem = repo.create_element(
            "Part", name="Part[1]", properties={"definition": part_blk.elem_id}
        )
        repo.add_element_to_diagram(ibd.diag_id, elem.elem_id)
        obj_data = {
            "obj_id": 1,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": elem.elem_id,
            "width": 80.0,
            "height": 40.0,
            "properties": {"definition": part_blk.elem_id},
        }
        win = DummyWindow(ibd.diag_id)
        obj = SysMLObject(**obj_data)
        lines = win._object_label_lines(obj)
        self.assertIn("Part 1 : PartB [1..*]", lines)

    def test_multiple_parts_show_incrementing_range(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part_blk = repo.create_element("Block", name="PartB")
        repo.create_relationship(
            "Composite Aggregation",
            whole.elem_id,
            part_blk.elem_id,
            properties={"multiplicity": "1..*"},
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)

        objs = []
        for idx in range(3):
            elem = repo.create_element(
                "Part",
                name=f"Part[{idx + 1}]",
                properties={"definition": part_blk.elem_id},
            )
            repo.add_element_to_diagram(ibd.diag_id, elem.elem_id)
            obj_data = {
                "obj_id": idx + 1,
                "obj_type": "Part",
                "x": 0,
                "y": 0,
                "element_id": elem.elem_id,
                "width": 80.0,
                "height": 40.0,
                "properties": {"definition": part_blk.elem_id},
            }
            objs.append(obj_data)

        win = DummyWindow(ibd.diag_id)
        for idx, data in enumerate(objs):
            obj = SysMLObject(**data)
            lines = win._object_label_lines(obj)
            self.assertIn(f"Part {idx + 1} : PartB [{idx + 1}..*]", lines)

if __name__ == "__main__":
    unittest.main()
