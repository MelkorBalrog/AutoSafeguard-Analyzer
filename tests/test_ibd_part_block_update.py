import unittest
from gui.architecture import _sync_block_parts_from_ibd
from sysml.sysml_repository import SysMLRepository

class IBDPartBlockUpdateTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_part_definition_adds_block_part(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part_blk = repo.create_element("Block", name="Inner")
        ibd = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(whole.elem_id, ibd.diag_id)
        part_elem = repo.create_element(
            "Part", name="Inner", properties={"definition": part_blk.elem_id}
        )
        ibd.objects.append(
            {
                "obj_id": 1,
                "obj_type": "Part",
                "x": 0,
                "y": 0,
                "element_id": part_elem.elem_id,
                "properties": {"definition": part_blk.elem_id},
            }
        )
        _sync_block_parts_from_ibd(repo, ibd.diag_id)
        self.assertIn(
            "Inner",
            repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )

if __name__ == "__main__":
    unittest.main()
