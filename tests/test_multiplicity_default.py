import unittest
from gui import architecture
from gui.architecture import SysMLObject, InternalBlockDiagramWindow
from sysml.sysml_repository import SysMLRepository

class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)
    def metrics(self, name: str) -> int:
        return 1

class DummyWin:
    _get_part_name = InternalBlockDiagramWindow._get_part_name
    def __init__(self, diag):
        self.repo = SysMLRepository.get_instance()
        self.diagram_id = diag.diag_id
        self.font = DummyFont()
        self.zoom = 1.0

class MultiplicityDefaultTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_default_multiplicity_enforced_and_displayed(self):
        repo = self.repo
        a = repo.create_element("Block", name="A")
        b = repo.create_element("Block", name="B")
        repo.create_relationship("Composite Aggregation", a.elem_id, b.elem_id)  # no multiplicity
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(a.elem_id, ibd.diag_id)
        architecture.add_composite_aggregation_part(repo, a.elem_id, b.elem_id)
        obj_dict = next(o for o in ibd.objects if o.get("obj_type") == "Part")
        obj = SysMLObject(**obj_dict)
        win = DummyWin(ibd)
        label = win._get_part_name(obj)
        self.assertIn("B [1..1]", label)
        exceeded = architecture._multiplicity_limit_exceeded(repo, a.elem_id, b.elem_id, [obj_dict])
        self.assertTrue(exceeded)

if __name__ == '__main__':
    unittest.main()
