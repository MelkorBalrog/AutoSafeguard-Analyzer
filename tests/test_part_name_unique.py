import unittest
from gui import architecture
from sysml.sysml_repository import SysMLRepository


class PartNameUniqueTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_detect_duplicate_name_across_diagrams(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)
        ibd_a = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd_a.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id)
        obj = next(o for o in ibd_a.objects if o.get("obj_type") == "Part")
        repo.elements[obj["element_id"]].name = "P"

        ibd_b = repo.create_diagram("Internal Block Diagram")
        boundary = {
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 0,
            "y": 0,
            "width": 80.0,
            "height": 40.0,
            "element_id": a.elem_id,
            "properties": {},
        }
        ibd_b.objects.append(boundary)

        exists = architecture._part_name_exists(repo, a.elem_id, "P")
        self.assertTrue(exists)


if __name__ == "__main__":
    unittest.main()

