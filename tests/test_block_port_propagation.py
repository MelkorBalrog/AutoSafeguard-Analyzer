import unittest
from gui.architecture import (
    add_composite_aggregation_part,
    propagate_block_port_changes,
)
from sysml.sysml_repository import SysMLRepository

class BlockPortPropagationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_port_propagates_to_parts(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part", properties={"ports": "a"})
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        part.properties["ports"] = "a, b"
        propagate_block_port_changes(repo, part.elem_id)
        part_obj = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        ports = [
            o["properties"]["name"]
            for o in ibd.objects
            if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(part_obj["obj_id"])
        ]
        self.assertEqual(set(ports), {"a", "b"})

    def test_remove_port_propagates_to_parts(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part", properties={"ports": "a, b"})
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        part.properties["ports"] = "b"
        propagate_block_port_changes(repo, part.elem_id)
        part_obj = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        ports = [
            o["properties"]["name"]
            for o in ibd.objects
            if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(part_obj["obj_id"])
        ]
        self.assertEqual(ports, ["b"])

if __name__ == "__main__":
    unittest.main()
