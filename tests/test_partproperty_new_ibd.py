import unittest
from gui.architecture import link_block_to_ibd, _ensure_ibd_boundary
from sysml.sysml_repository import SysMLRepository

class PartPropertyNewIBDTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_parts_visible_when_ibd_created_later(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        link_block_to_ibd(repo, blk.elem_id, ibd.diag_id)
        self.assertTrue(any(
            o.get("obj_type") == "Part" and repo.elements[o.get("element_id")].name.startswith("B")
            for o in ibd.objects
        ))
        part = next(o for o in ibd.objects if repo.elements[o.get("element_id")].name.startswith("B"))
        self.assertFalse(part.get("hidden", False))

    def test_boundary_receives_parts_on_creation(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child", properties={"partProperties": "P"})
        repo.create_element("Block", name="P")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(parent.elem_id, ibd.diag_id)
        ibd.objects.append({
            "obj_id": 1,
            "obj_type": "Block Boundary",
            "x": 50.0,
            "y": 50.0,
            "width": 200.0,
            "height": 120.0,
            "element_id": child.elem_id,
            "properties": {"name": "Child"},
        })
        _ensure_ibd_boundary(repo, ibd, child.elem_id)
        self.assertTrue(any(
            o.get("obj_type") == "Part" and repo.elements[o.get("element_id")].name.startswith("P")
            for o in ibd.objects
        ))

if __name__ == "__main__":
    unittest.main()
