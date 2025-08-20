import unittest
import tkinter as tk
from AutoML import AutoMLApp


class MetricsTabMissingBackendTests(unittest.TestCase):
    def test_open_metrics_tab_without_matplotlib_backend(self):
        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("Tk not available")
        app = AutoMLApp(root)
        app.open_metrics_tab()
        tabs = [app.doc_nb.tab(tid, "text") for tid in app.doc_nb.tabs()]
        self.assertNotIn("Metrics", tabs)
        root.destroy()


if __name__ == "__main__":
    unittest.main()
