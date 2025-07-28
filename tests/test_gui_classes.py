import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui.toolboxes import TC2FIWindow

class RowDialogMethodTests(unittest.TestCase):
    def test_rowdialog_has_add_func_existing(self):
        self.assertTrue(hasattr(TC2FIWindow.RowDialog, 'add_func_existing'))

if __name__ == '__main__':
    unittest.main()
