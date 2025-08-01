import unittest
from gui import architecture
from gui.architecture import SysMLObject
from sysml.sysml_repository import SysMLRepository

class MultiplicityDefaultTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_default_multiplicity_enforced(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id)
        elem = repo.create_element("Part")
        repo.add_element_to_diagram(ibd.diag_id, elem.elem_id)
        obj = SysMLObject(99, "Part", 0, 0, element_id=elem.elem_id, properties={})
        ibd.objects.append(obj.__dict__)
        exceeded = architecture._multiplicity_limit_exceeded(
            repo,
            a.elem_id,
            b.elem_id,
            ibd.objects,
            obj.element_id,
        )
        self.assertTrue(exceeded)
