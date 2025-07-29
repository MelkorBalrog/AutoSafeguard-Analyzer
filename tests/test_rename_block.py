import unittest
from gui.architecture import (
    add_composite_aggregation_part,
    add_aggregation_part,
    remove_aggregation_part,
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
            properties={"partProperties": "a"},
        )
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        inherit_block_properties(repo, child.elem_id)
        parent.properties["partProperties"] = "b"
        rename_block(repo, parent.elem_id, "ParentNew")
        self.assertIn(
            "b",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_rename_block_updates_aggregation_without_ibd(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Aggregation", whole.elem_id, part.elem_id)
        add_aggregation_part(repo, whole.elem_id, part.elem_id)
        rename_block(repo, part.elem_id, "NewPart")
        self.assertIn(
            "NewPart",
            repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )
        rel = next(
            r
            for r in repo.relationships
            if r.rel_type == "Aggregation"
            and r.source == whole.elem_id
            and r.target == part.elem_id
        )
        pid = rel.properties.get("part_elem")
        self.assertIsNotNone(pid)
        self.assertEqual(repo.elements[pid].name, "NewPart")

    def test_rename_aggregated_block_updates_generalized_parent(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="Part")
        repo.create_relationship("Composite Aggregation", parent.elem_id, part.elem_id)
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id)
        inherit_block_properties(repo, child.elem_id)
        rename_block(repo, part.elem_id, "Renamed")
        self.assertIn(
            "Renamed",
            repo.elements[parent.elem_id].properties.get("partProperties", ""),
        )
        self.assertIn(
            "Renamed",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_rename_empty_block_syncs_and_removes(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="")
        repo.create_relationship("Aggregation", whole.elem_id, part.elem_id)
        add_aggregation_part(repo, whole.elem_id, part.elem_id)
        rename_block(repo, part.elem_id, "Renamed")
        self.assertIn(
            "Renamed",
            repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )
        remove_aggregation_part(repo, whole.elem_id, part.elem_id)
        self.assertNotIn(
            "Renamed",
            repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )


if __name__ == "__main__":
    unittest.main()
