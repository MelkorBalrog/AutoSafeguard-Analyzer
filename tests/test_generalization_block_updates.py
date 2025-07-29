import unittest
from gui.architecture import (
    add_aggregation_part,
    propagate_block_port_changes,
    propagate_block_changes,
    parse_operations,
)
from sysml.sysml_repository import SysMLRepository


class BlockChangePropagationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_block_change_propagates_to_children(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)

        ibd_parent = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(parent.elem_id, ibd_parent.diag_id)
        ibd_child = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd_child.diag_id)

        ibd_parent.objects.append({
            "obj_id": 1,
            "obj_type": "Block",
            "x": 0,
            "y": 0,
            "element_id": parent.elem_id,
            "properties": {},
            "requirements": [{"id": "R1"}],
        })
        ibd_child.objects.append({
            "obj_id": 2,
            "obj_type": "Block",
            "x": 0,
            "y": 0,
            "element_id": child.elem_id,
            "properties": {},
            "requirements": [],
        })

        parent.properties["operations"] = '[{"name":"opA"}]'
        parent.properties["ports"] = "p1"
        part = repo.create_element("Block", name="Part")
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        propagate_block_port_changes(repo, parent.elem_id)

        propagate_block_changes(repo, parent.elem_id)

        ops = parse_operations(child.properties.get("operations", ""))
        self.assertTrue(any(o.name == "opA" for o in ops))
        self.assertIn("p1", child.properties.get("ports", ""))
        self.assertIn("Part", child.properties.get("partProperties", ""))
        self.assertEqual(ibd_child.objects[0]["requirements"][0]["id"], "R1")


if __name__ == "__main__":
    unittest.main()
