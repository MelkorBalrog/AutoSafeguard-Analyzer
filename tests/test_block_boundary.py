import unittest
from gui.architecture import set_ibd_father, link_block_to_ibd
from sysml.sysml_repository import SysMLRepository

class BlockBoundaryTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_boundary_created_with_ports(self):
        repo = self.repo
        block = repo.create_element("Block", name="B", properties={"ports": "a, b"})
        ibd = repo.create_diagram("Internal Block Diagram")
        added = set_ibd_father(repo, ibd, block.elem_id)
        boundary = next(o for o in ibd.objects if o.get("obj_type") == "Block Boundary")
        self.assertEqual(boundary.get("element_id"), block.elem_id)
        port_names = {
            o["properties"]["name"]
            for o in ibd.objects
            if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(boundary["obj_id"])
        }
        self.assertEqual(port_names, {"a", "b"})
        self.assertTrue(any(d.get("obj_type") == "Block Boundary" for d in added))

    def test_boundary_created_via_block_link(self):
        repo = self.repo
        block = repo.create_element("Block", name="B", properties={"ports": "p"})
        ibd = repo.create_diagram("Internal Block Diagram")
        link_block_to_ibd(repo, block.elem_id, ibd.diag_id)
        boundary = next(o for o in ibd.objects if o.get("obj_type") == "Block Boundary")
        self.assertEqual(boundary.get("element_id"), block.elem_id)

if __name__ == "__main__":
    unittest.main()
