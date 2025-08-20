import inspect
import unittest
from AutoML import AutoMLApp


class MetricsTabMenuTests(unittest.TestCase):
    def test_app_has_open_metrics_tab(self):
        self.assertTrue(hasattr(AutoMLApp, "open_metrics_tab"))

    def test_view_menu_includes_metrics_option(self):
        src = inspect.getsource(AutoMLApp.__init__)
        self.assertIn('label="Metrics"', src)
        self.assertIn('open_metrics_tab', src)


if __name__ == "__main__":
    unittest.main()
