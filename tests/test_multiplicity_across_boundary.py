import unittest
from gui import architecture
from gui.architecture import SysMLObject
from sysml.sysml_repository import SysMLRepository


class MultiplicityAcrossBoundaryTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_limit_counts_parts_in_all_diagrams(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship(
            "Composite Aggregation",
            a.elem_id,
            b.elem_id,
            properties={"multiplicity": "1"},
        )
        ibd_a = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd_a.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id, "1")

        ibd_b = repo.create_diagram("Internal Block Diagram")
        boundary = {
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 0,
            "y": 0,
            "width": 100.0,
            "height": 80.0,
            "element_id": a.elem_id,
            "properties": {},
        }
        ibd_b.objects.append(boundary)

        new_elem = repo.create_element("Part", name="X")
        repo.add_element_to_diagram(ibd_b.diag_id, new_elem.elem_id)
        obj = {
            "obj_id": 2,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": new_elem.elem_id,
            "properties": {"definition": b.elem_id},
        }

        exceeded = architecture._multiplicity_limit_exceeded(
            repo,
            a.elem_id,
            b.elem_id,
            [obj],
            new_elem.elem_id,
        )
        self.assertTrue(exceeded)


if __name__ == "__main__":
    unittest.main()

