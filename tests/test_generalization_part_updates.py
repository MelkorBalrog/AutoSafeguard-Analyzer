import unittest
from gui.architecture import (
    add_aggregation_part,
    add_composite_aggregation_part,
    remove_aggregation_part,
    SysMLDiagramWindow,
    SysMLObject,
)
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class GeneralizationPartUpdateTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    class DummyBlockWindow:
        def __init__(self):
            self.repo = SysMLRepository.get_instance()
            diag = SysMLDiagram(diag_id="d", diag_type="Block Diagram")
            self.repo.diagrams[diag.diag_id] = diag
            self.diagram_id = diag.diag_id

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

    def test_child_cannot_duplicate_aggregation(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="PartD")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        repo.create_relationship("Aggregation", parent.elem_id, part.elem_id)
        add_aggregation_part(repo, parent.elem_id, part.elem_id)

        win = self.DummyBlockWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=child.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=part.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Aggregation")
        self.assertFalse(valid)
        before = repo.elements[child.elem_id].properties.get("partProperties", "")
        add_aggregation_part(repo, child.elem_id, part.elem_id)
        after = repo.elements[child.elem_id].properties.get("partProperties", "")
        self.assertEqual(before, after)

    def test_child_cannot_duplicate_composite(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="PartE")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        repo.create_relationship("Composite Aggregation", parent.elem_id, part.elem_id)
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id)

        win = self.DummyBlockWindow()
        src = SysMLObject(1, "Block", 0, 0, element_id=child.elem_id)
        dst = SysMLObject(2, "Block", 0, 0, element_id=part.elem_id)
        valid, _ = SysMLDiagramWindow.validate_connection(win, src, dst, "Composite Aggregation")
        self.assertFalse(valid)
        before = repo.elements[child.elem_id].properties.get("partProperties", "")
        add_composite_aggregation_part(repo, child.elem_id, part.elem_id)
        after = repo.elements[child.elem_id].properties.get("partProperties", "")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
