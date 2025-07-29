import unittest
from gui.architecture import (
    add_composite_aggregation_part,
    rename_block,
    inherit_block_properties,
)
from sysml.sysml_repository import SysMLRepository


class RenameBlockTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_rename_block_updates_part_usage(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        rename_block(repo, part.elem_id, "NewPart")
        self.assertIn(
            "NewPart",
            repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )
        self.assertTrue(
            any(
                repo.elements[o["element_id"]].name == "NewPart"
                for o in ibd.objects
                if o.get("obj_type") == "Part"
                and o.get("properties", {}).get("definition") == part.elem_id
            )
        )

    def test_rename_block_propagates_to_generalization(self):
        repo = self.repo
        parent = repo.create_element(
            "Block",
            name="Parent",
            properties={"valueProperties": "a"},
        )
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        inherit_block_properties(repo, child.elem_id)
        parent.properties["valueProperties"] = "b"
        rename_block(repo, parent.elem_id, "ParentNew")
        self.assertIn(
            "b",
            repo.elements[child.elem_id].properties.get("valueProperties", ""),
        )

    def test_rename_propagates_through_generalization_chain(self):
        repo = self.repo
        base = repo.create_element("Block", name="Base", properties={"valueProperties": "a"})
        mid = repo.create_element("Block", name="Mid")
        leaf = repo.create_element("Block", name="Leaf")
        repo.create_relationship("Generalization", mid.elem_id, base.elem_id)
        repo.create_relationship("Generalization", leaf.elem_id, mid.elem_id)
        inherit_block_properties(repo, leaf.elem_id)
        base.properties["valueProperties"] = "b"
        rename_block(repo, base.elem_id, "BaseNew")
        self.assertIn(
            "b",
            repo.elements[leaf.elem_id].properties.get("valueProperties", ""),
        )

    def test_rename_part_updates_generalization_children(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="Part")
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id)
        inherit_block_properties(repo, child.elem_id)
        rename_block(repo, part.elem_id, "PartNew")
        self.assertIn(
            "PartNew",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )


if __name__ == "__main__":
    unittest.main()
