import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sysml.sysml_repository import SysMLRepository
from analysis.user_config import set_current_user

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

if __name__ == '__main__':
    unittest.main()
