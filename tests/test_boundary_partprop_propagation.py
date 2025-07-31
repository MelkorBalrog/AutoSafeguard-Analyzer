import unittest
from gui.architecture import _sync_ibd_partproperty_parts, _propagate_boundary_parts
from sysml.sysml_repository import SysMLRepository

class BoundaryPartPropagationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_new_parts_show_in_boundary_diagrams(self):
        repo = self.repo
        block_a = repo.create_element("Block", name="A")
        block_b = repo.create_element("Block", name="B")
        block_c = repo.create_element("Block", name="C")
        ibd_b = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block_b.elem_id, ibd_b.diag_id)
        ibd_a = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(block_a.elem_id, ibd_a.diag_id)
        ibd_a.objects.append({
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 100.0,
            "y": 80.0,
            "width": 200.0,
            "height": 120.0,
            "element_id": block_b.elem_id,
            "properties": {"name": "B"},
        })
        block_b.properties["partProperties"] = "C"
        added = _sync_ibd_partproperty_parts(repo, block_b.elem_id, visible=True)
        _propagate_boundary_parts(repo, block_b.elem_id, added)
        self.assertTrue(any(
            o.get("obj_type") == "Part" and o.get("element_id") == added[0]["element_id"]
            for o in ibd_a.objects
        ))
        part = next(o for o in ibd_a.objects if o.get("element_id") == added[0]["element_id"])
        self.assertFalse(part.get("hidden", False))

if __name__ == "__main__":
    unittest.main()
