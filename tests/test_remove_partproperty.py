import unittest
from gui.architecture import (
    _sync_ibd_partproperty_parts,
    propagate_block_changes,
    remove_partproperty_entry,
)
from sysml.sysml_repository import SysMLRepository

class RemovePartPropertyTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_remove_partproperty_updates_child_ibds(self):
        repo = self.repo
        parent = repo.create_element("Block", name="Parent", properties={"partProperties": "B"})
        part_blk = repo.create_element("Block", name="B")
        child = repo.create_element("Block", name="Child")
        repo.create_relationship("Generalization", child.elem_id, parent.elem_id)
        ibd_p = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(parent.elem_id, ibd_p.diag_id)
        ibd_c = repo.create_diagram("Internal Block Diagram")
        repo.link_diagram(child.elem_id, ibd_c.diag_id)

        _sync_ibd_partproperty_parts(repo, parent.elem_id)
        propagate_block_changes(repo, parent.elem_id)

        self.assertTrue(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd_c.objects
            )
        )

        remove_partproperty_entry(repo, parent.elem_id, "B")

        self.assertFalse(
            any(
                o.get("obj_type") == "Part" and o.get("properties", {}).get("definition") == part_blk.elem_id
                for o in ibd_c.objects
            )
        )

if __name__ == "__main__":
    unittest.main()
