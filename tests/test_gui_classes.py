import unittest
import os
import sys
import inspect
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui.toolboxes import TC2FIWindow, RiskAssessmentWindow
from AutoML import FaultTreeApp
try:
    from gui.faults_gui import FaultsWindow
except Exception:  # pragma: no cover - optional dependency
    FaultsWindow = None

class RowDialogMethodTests(unittest.TestCase):
    def test_rowdialog_has_add_func_existing(self):
        self.assertTrue(hasattr(TC2FIWindow.RowDialog, 'add_func_existing'))


class FaultsGuiTests(unittest.TestCase):
    @unittest.skipIf(FaultsWindow is None, "faults_gui dependencies not available")
    def test_faults_window_has_double_click_handler(self):
        self.assertTrue(hasattr(FaultsWindow, 'on_table_double_clicked'))


class DoubleClickBindingTests(unittest.TestCase):
    def test_risk_assessment_double_click_binding(self):
        src = inspect.getsource(RiskAssessmentWindow.__init__)
        self.assertIn('bind("<Double-1>"', src)

    def test_product_goals_editor_double_click_binding(self):
        src = inspect.getsource(FaultTreeApp.show_product_goals_editor)
        self.assertIn('bind("<Double-1>"', src)


class ProductGoalsMatrixTests(unittest.TestCase):
    def test_matrix_has_all_columns_and_scrollbars(self):
        src = inspect.getsource(FaultTreeApp.show_safety_goals_matrix)
        for col in [
            'FTTI',
            'Acc Rate',
            'On Hours',
            'Val Target',
            'Profile',
            'Val Desc',
            'Acceptance',
            'Description',
        ]:
            self.assertIn(col, src)
        self.assertIn('xscrollcommand', src)
        self.assertIn('yscrollcommand', src)

if __name__ == '__main__':
    unittest.main()
