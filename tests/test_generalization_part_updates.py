import unittest
from gui.architecture import (
    add_aggregation_part,
    add_composite_aggregation_part,
    remove_aggregation_part,
    _sync_ibd_composite_parts,
    inherit_block_properties,
)
from sysml.sysml_repository import SysMLRepository


class GeneralizationPartUpdateTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_aggregation_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="PartA")
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertIn(
            "PartA",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_add_composite_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="PartB")
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertIn(
            "PartB",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_remove_aggregation_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="PartC")
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertIn(
            "PartC",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )
        remove_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertNotIn(
            "PartC",
            repo.elements[child.elem_id].properties.get("partProperties", ""),
        )

    def test_multiplicity_change_updates_child(self):
        repo = self.repo
        parent = repo.create_element("Block", name="P")
        child = repo.create_element("Block", name="C")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="B")
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id, "1")
        self.assertEqual(
            repo.elements[child.elem_id].properties.get("partProperties"),
            "B[1]",
        )
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id, "3")
        self.assertEqual(
            repo.elements[child.elem_id].properties.get("partProperties"),
            "B[3]",
        )

    def test_remove_part_propagates_to_grandchildren(self):
        repo = self.repo
        parent = repo.create_element("Block", name="P")
        child = repo.create_element("Block", name="C1")
        grand = repo.create_element("Block", name="C2")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        repo.create_relationship("Generalization", grand.elem_id, child.elem_id)
        part = repo.create_element("Block", name="X")
        repo.create_relationship("Aggregation", parent.elem_id, part.elem_id)
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        inherit_block_properties(repo, grand.elem_id)
        self.assertIn("X", repo.elements[grand.elem_id].properties.get("partProperties", ""))
        remove_aggregation_part(repo, parent.elem_id, part.elem_id)
        self.assertNotIn("X", repo.elements[grand.elem_id].properties.get("partProperties", ""))

    def test_remove_object_updates_descendant_ibds(self):
        repo = self.repo
        parent = repo.create_element("Block", name="P")
        child = repo.create_element("Block", name="C1")
        grand = repo.create_element("Block", name="C2")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        repo.create_relationship("Generalization", grand.elem_id, child.elem_id)
        part = repo.create_element("Block", name="Q")
        repo.create_relationship("Composite Aggregation", parent.elem_id, part.elem_id)
        ibd_p = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(parent.elem_id, ibd_p.diag_id)
        ibd_c = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd_c.diag_id)
        ibd_g = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(grand.elem_id, ibd_g.diag_id)
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id)
        _sync_ibd_composite_parts(repo, child.elem_id)
        _sync_ibd_composite_parts(repo, grand.elem_id)
        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd_g.objects
            )
        )
        remove_aggregation_part(repo, parent.elem_id, part.elem_id, remove_object=True)
        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd_c.objects
            )
        )
        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd_g.objects
            )
        )


if __name__ == "__main__":
    unittest.main()
