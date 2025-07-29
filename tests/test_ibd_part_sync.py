import unittest
from gui.architecture import set_ibd_father, update_block_parts_from_ibd
from sysml.sysml_repository import SysMLRepository

class IBDPartSyncTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_ibd_part_addition_updates_block_parts(self):
        repo = self.repo
        whole = repo.create_element("Block", name="Whole")
        part = repo.create_element("Block", name="Part")
        ibd = repo.create_diagram("Internal Block Diagram")
        set_ibd_father(repo, ibd, whole.elem_id)
        elem = repo.create_element("Part", name="Part", properties={"definition": part.elem_id})
        repo.add_element_to_diagram(ibd.diag_id, elem.elem_id)
        ibd.objects.append({
            "obj_id": 1,
            "obj_type": "Part",
            "x": 0,
            "y": 0,
            "element_id": elem.elem_id,
            "properties": {"definition": part.elem_id},
        })
        update_block_parts_from_ibd(repo, ibd)
        props = repo.elements[whole.elem_id].properties.get("partProperties", "")
        self.assertIn("Part", props)

if __name__ == "__main__":
    unittest.main()
