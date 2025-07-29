import unittest
from gui.architecture import (
    add_composite_aggregation_part,
    add_aggregation_part,
    inherit_block_properties,
)
from sysml.sysml_repository import SysMLRepository

class AggregationGeneralizationRestrictTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_prevent_duplicate_aggregation_via_generalization(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        # parent aggregates part
        add_composite_aggregation_part(repo, parent.elem_id, part.elem_id)
        # child generalizes parent
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        inherit_block_properties(repo, child.elem_id)
        before = repo.elements[child.elem_id].properties.get("partProperties", "")
        # attempt to aggregate same part in child
        add_composite_aggregation_part(repo, child.elem_id, part.elem_id)
        after = repo.elements[child.elem_id].properties.get("partProperties", "")
        self.assertEqual(before, after)

    def test_prevent_duplicate_regular_aggregation_via_generalization(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent")
        child = repo.create_element("Block", name="Child")
        part = repo.create_element("Block", name="Part")
        add_aggregation_part(repo, parent.elem_id, part.elem_id)
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        inherit_block_properties(repo, child.elem_id)
        before = repo.elements[child.elem_id].properties.get("partProperties", "")
        add_aggregation_part(repo, child.elem_id, part.elem_id)
        after = repo.elements[child.elem_id].properties.get("partProperties", "")
        self.assertEqual(before, after)

if __name__ == "__main__":
    unittest.main()
