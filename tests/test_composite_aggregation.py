import unittest
from gui.architecture import (
    add_composite_aggregation_part,
    remove_aggregation_part,
)
from sysml.sysml_repository import SysMLRepository


class CompositeAggregationTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_add_composite_part_to_ibd(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        self.assertIn("Part", repo.elements[whole.elem_id].properties.get("partProperties", ""))
        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd.objects
            )
        )

    def test_remove_composite_part_from_ibd(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id)
        remove_aggregation_part(repo, whole.elem_id, part.elem_id, remove_object=True)
        self.assertNotIn("Part", repo.elements[whole.elem_id].properties.get("partProperties", ""))
        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
                for o in ibd.objects
            )
        )


if __name__ == "__main__":
    unittest.main()
