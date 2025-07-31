import unittest
from gui.architecture import (
    set_ibd_father,
    link_block_to_ibd,
    rename_block,
    propagate_block_port_changes,
)
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

    def test_rename_block_updates_boundary_name(self):
        repo = self.repo
        block = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, ibd, block.elem_id)
        rename_block(repo, block.elem_id, "B2")
        boundary = next(o for o in ibd.objects if o.get("obj_type") == "Block Boundary")
        self.assertEqual(boundary.get("properties", {}).get("name"), "B2")

    def test_add_port_updates_block_and_boundary(self):
        repo = self.repo
        block = repo.create_element("Block", name="B", properties={"ports": "p1"})
        ibd = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, ibd, block.elem_id)
        boundary = next(o for o in ibd.objects if o.get("obj_type") == "Block Boundary")
        boundary.setdefault("properties", {})["ports"] = "p1, p2"
        block.properties["ports"] = "p1, p2"
        propagate_block_port_changes(repo, block.elem_id)
        names = [
            o["properties"]["name"]
            for o in ibd.objects
            if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(boundary["obj_id"])
        ]
        self.assertIn("p2", names)

    def test_edit_boundary_name_updates_block(self):
        repo = self.repo
        block = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, ibd, block.elem_id)
        boundary = next(o for o in ibd.objects if o.get("obj_type") == "Block Boundary")
        boundary.setdefault("properties", {})["name"] = "B2"
        rename_block(repo, boundary["element_id"], "B2")
        self.assertEqual(block.name, "B2")

    def test_edit_boundary_name_updates_block_object(self):
        repo = self.repo
        block = repo.create_element("Block", name="B")
        diag = repo.create_diagram("Block Diagram")
        repo.add_element_to_diagram(diag.diag_id, block.elem_id)
        diag.objects.append(
            {
                "obj_id": 1,
                "obj_type": "Block",
                "x": 0,
                "y": 0,
                "element_id": block.elem_id,
                "properties": {"name": "B"},
            }
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, ibd, block.elem_id)
        boundary = next(o for o in ibd.objects if o.get("obj_type") == "Block Boundary")
        boundary.setdefault("properties", {})["name"] = "B2"
        rename_block(repo, boundary["element_id"], "B2")
        self.assertEqual(diag.objects[0]["properties"].get("name"), "B2")

if __name__ == "__main__":
    unittest.main()
