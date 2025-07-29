import unittest
from gui.architecture import (
    add_aggregation_part,
    add_composite_aggregation_part,
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


if __name__ == "__main__":
    unittest.main()
