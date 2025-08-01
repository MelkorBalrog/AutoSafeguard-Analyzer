import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sysml.sysml_repository import SysMLRepository
from analysis.user_config import set_current_user
from gui.architecture import rename_block, add_aggregation_part

class UndoTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        set_current_user("Tester", "tester@example.com")
        self.repo = SysMLRepository.get_instance()

    def test_undo_creation(self):
        elem = self.repo.create_element("Actor", name="User")
        self.assertIn(elem.elem_id, self.repo.elements)
        self.assertTrue(self.repo.undo())
        self.assertNotIn(elem.elem_id, self.repo.elements)

    def test_undo_rename_block(self):
        blk = self.repo.create_element("Block", name="A")
        rename_block(self.repo, blk.elem_id, "B")
        self.assertEqual(self.repo.elements[blk.elem_id].name, "B")
        self.assertTrue(self.repo.undo())
        self.assertEqual(self.repo.elements[blk.elem_id].name, "A")

    def test_undo_add_aggregation(self):
        whole = self.repo.create_element("Block", name="Whole")
        part = self.repo.create_element("Block", name="Part")
        add_aggregation_part(self.repo, whole.elem_id, part.elem_id)
        self.assertIn(
            "Part",
            self.repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )
        self.assertTrue(self.repo.undo())
        self.assertNotIn(
            "Part",
            self.repo.elements[whole.elem_id].properties.get("partProperties", ""),
        )

    def test_redo_creation(self):
        elem = self.repo.create_element("Actor", name="User")
        self.repo.undo()
        self.assertNotIn(elem.elem_id, self.repo.elements)
        self.assertTrue(self.repo.redo())
        self.assertIn(elem.elem_id, self.repo.elements)

    def test_redo_rename_block(self):
        blk = self.repo.create_element("Block", name="A")
        rename_block(self.repo, blk.elem_id, "B")
        self.repo.undo()
        self.assertEqual(self.repo.elements[blk.elem_id].name, "A")
        self.assertTrue(self.repo.redo())
        self.assertEqual(self.repo.elements[blk.elem_id].name, "B")

if __name__ == '__main__':
    unittest.main()
