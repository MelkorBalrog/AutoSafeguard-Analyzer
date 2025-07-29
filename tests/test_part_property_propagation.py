import unittest
from gui.architecture import (
    add_composite_aggregation_part,
    propagate_block_part_changes,
    OperationDefinition,
    operations_to_json,
)
from sysml.sysml_repository import SysMLRepository

class PartPropertyPropagationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_block_property_propagates_to_part(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element(
            "Block",
            name="Part",
            properties={
                "ports": "a",
                "operations": operations_to_json([OperationDefinition("op")]),
                "behaviors": "b1",
                "partProperties": "p1",
            },
        )
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        # modify block properties
        part.properties["ports"] = "a, b"
        part.properties["operations"] = operations_to_json([OperationDefinition("op"), OperationDefinition("op2")])
        part.properties["behaviors"] = "b1, b2"
        part.properties["partProperties"] = "p1, p2"
        propagate_block_part_changes(repo, part.elem_id)
        part_obj = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        # check port objects
        ports = [
            o["properties"]["name"]
            for o in ibd.objects
            if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(part_obj["obj_id"])
        ]
        self.assertEqual(set(ports), {"a", "b"})
        # check other properties
        self.assertIn("op2", repo.elements[part_obj["element_id"]].properties.get("operations"))
        self.assertEqual(part_obj["properties"].get("behaviors"), "b1, b2")
        self.assertEqual(part_obj["properties"].get("partProperties"), "p1, p2")

if __name__ == "__main__":
    unittest.main()
