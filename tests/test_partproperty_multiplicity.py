import unittest
from gui.architecture import _sync_ibd_partproperty_parts
from sysml.sysml_repository import SysMLRepository

class PartPropertyMultiplicityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_duplicates_ignored(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B, B"})
        repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        _sync_ibd_partproperty_parts(repo, blk.elem_id, visible=True)
        parts = [o for o in ibd.objects if o.get("obj_type") == "Part"]
        self.assertEqual(len(parts), 1)

    def test_multiplicity_limit(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole", properties={"partProperties": "P, P"})
        part = repo.create_element("Block", name="P")
        repo.create_relationship("Composite Aggregation", whole.elem_id, part.elem_id, properties={"multiplicity": "1"})
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        _sync_ibd_partproperty_parts(repo, whole.elem_id, visible=True)
        parts = [o for o in ibd.objects if o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part.elem_id]
        self.assertEqual(len(parts), 1)

if __name__ == "__main__":
    unittest.main()
