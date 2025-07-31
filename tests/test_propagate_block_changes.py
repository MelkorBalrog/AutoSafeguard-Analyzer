import unittest
from gui.architecture import (
    propagate_block_changes,
    inherit_block_properties,
    propagate_block_port_changes,
    OperationDefinition,
    operations_to_json,
    parse_operations,
)
from sysml.sysml_repository import SysMLRepository
from analysis.models import global_requirements


class PropagateBlockChangesTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()
        global_requirements.clear()
        global_requirements["R1"] = {"id": "R1", "text": "Req1"}
        global_requirements["R2"] = {"id": "R2", "text": "Req2"}

    def test_changes_propagate_to_children(self):
        repo = self.repo
        parent = repo.create_element(
            "Block",
            name="Parent",
            properties={
                "operations": operations_to_json([OperationDefinition("op1")]),
                "ports": "p",
            },
        )
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)

        # create diagrams with block objects and requirements
        d_parent = repo.create_diagram("Block Diagram")
        repo.add_element_to_diagram(d_parent.diag_id, parent.elem_id)
        d_parent.objects = [
            {
                "obj_id": 1,
                "obj_type": "Block",
                "x": 0,
                "y": 0,
                "element_id": parent.elem_id,
                "requirements": [global_requirements["R1"]],
            }
        ]
        d_child = repo.create_diagram("Block Diagram")
        repo.add_element_to_diagram(d_child.diag_id, child.elem_id)
        d_child.objects = [
            {
                "obj_id": 2,
                "obj_type": "Block",
                "x": 0,
                "y": 0,
                "element_id": child.elem_id,
                "requirements": [],
            }
        ]

        inherit_block_properties(repo, child.elem_id)
        propagate_block_port_changes(repo, child.elem_id)

        # modify parent
        parent.properties["ports"] = "p, q"
        parent.properties["operations"] = operations_to_json(
            [OperationDefinition("op1"), OperationDefinition("op2")]
        )
        d_parent.objects[0]["requirements"].append(global_requirements["R2"])

        propagate_block_changes(repo, parent.elem_id)

        child_props = repo.elements[child.elem_id].properties
        self.assertIn("q", child_props.get("ports", ""))
        ops = [o.name for o in parse_operations(child_props.get("operations", ""))]
        self.assertIn("op2", ops)
        req_ids = [r["id"] for r in d_child.objects[0].get("requirements", [])]
        self.assertIn("R2", req_ids)

    def test_part_changes_propagate_to_child_ibd(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent", properties={"partProperties": "P"})
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part_blk = repo.create_element("Block", name="P")
        ibd_child = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd_child.diag_id)

        inherit_block_properties(repo, child.elem_id)
        propagate_block_changes(repo, parent.elem_id)

        obj = next(
            o for o in ibd_child.objects if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id
        )
        self.assertFalse(obj.get("hidden", True))


if __name__ == "__main__":
    unittest.main()
