import unittest
from gui.architecture import _sync_ibd_partproperty_parts
from sysml.sysml_repository import SysMLRepository

class PartPropertyVisibilityTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_partproperty_hidden_by_default(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id)
        part = next(o for o in ibd.objects if o.get("properties", {}).get("definition") == part_blk.elem_id)
        self.assertTrue(part.get("hidden", False))
        self.assertTrue(any(d.get("hidden", False) for d in added))

    def test_partproperty_default_size(self):
        repo = self.repo
        blk = repo.create_element("Block", name="A", properties={"partProperties": "B"})
        repo.create_element("Block", name="B")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(blk.elem_id, ibd.diag_id)
        added = _sync_ibd_partproperty_parts(repo, blk.elem_id)
        part = added[0]
        self.assertIn("width", part)
        self.assertIn("height", part)
        self.assertGreater(part["width"], 0)
        self.assertGreater(part["height"], 0)

if __name__ == "__main__":
    unittest.main()
