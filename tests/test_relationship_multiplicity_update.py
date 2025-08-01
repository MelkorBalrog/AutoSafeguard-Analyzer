import unittest
from gui import architecture
from sysml.sysml_repository import SysMLRepository

class RelationMultiplicityUpdateTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_update_relationship_multiplicity(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        rel = repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id, "2")
        self.assertEqual(rel.properties.get("multiplicity"), "2")
