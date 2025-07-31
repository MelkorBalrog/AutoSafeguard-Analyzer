import unittest
from gui.architecture import (
    add_aggregation_part,
    add_composite_aggregation_part,
    _sync_ibd_aggregation_parts,
    remove_aggregation_part,
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

    def test_remove_aggregation_clears_child_ibd(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        part = repo.create_element("Block", name="PartD")
        repo.create_relationship("Aggregation", parent.elem_id, part.elem_id)
        add_aggregation_part(repo, parent.elem_id, part.elem_id)

        ibd_c = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd_c.diag_id)

        _sync_ibd_aggregation_parts(repo, child.elem_id)

        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd_c.objects
            )
        )

        remove_aggregation_part(repo, parent.elem_id, part.elem_id, remove_object=True)

        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd_c.objects
            )
        )


if __name__ == "__main__":
    unittest.main()
