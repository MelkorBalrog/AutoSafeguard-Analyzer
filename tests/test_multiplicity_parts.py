import unittest
from gui.architecture import add_composite_aggregation_part, add_multiplicity_parts
from sysml.sysml_repository import SysMLRepository

class MultiplicityPartTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_exact_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "3")
        objs = [
            o for o in ibd.objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 3)
        names = {repo.elements[o["element_id"]].name for o in objs}
        self.assertIn("Part[1]", names)
        self.assertIn("Part[3]", names)

    def test_unbounded_multiplicity(self):
        repo = self.repo
        whole = repo.create_element("Block", name="W")
        part = repo.create_element("Block", name="P")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        add_composite_aggregation_part(repo, whole.elem_id, part.elem_id, "1..*")
        add_multiplicity_parts(repo, whole.elem_id, part.elem_id, "1..*", count=3)
        objs = [
            o for o in ibd.objects
            if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id
        ]
        self.assertEqual(len(objs), 4)

if __name__ == "__main__":
    unittest.main()
