import unittest
import sys
import types
import os
import importlib.util
from pathlib import Path

try:  # pragma: no cover - only executed when tkinter missing
    import tkinter  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for headless envs
    class _Frame:
        pass

    class _Canvas:
        pass

    tk_stub = types.SimpleNamespace(
        Canvas=_Canvas, Frame=_Frame, LEFT=0, BOTH=0, ttk=types.SimpleNamespace(), font=types.SimpleNamespace()
    )
    sys.modules["tkinter"] = tk_stub

module_path = Path(__file__).resolve().parents[1] / "gui" / "metrics_tab.py"
spec = importlib.util.spec_from_file_location("metrics_tab", module_path)
metrics_tab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_tab)
MetricsTab = metrics_tab.MetricsTab


class DummyCanvas:
    def __getitem__(self, key):
        return {"width": 300, "height": 200}[key]

    def delete(self, *args, **kwargs):
        pass

    def create_line(self, *args, **kwargs):
        pass

    def create_text(self, *args, **kwargs):
        pass

    def create_rectangle(self, *args, **kwargs):
        pass


class MetricsTabZeroDivisionTests(unittest.TestCase):
    def test_line_chart_variants_handle_zero_max(self):
        canvas = DummyCanvas()
        data = [0, 0, 0]
        for name in [
            "_draw_line_chart_v1",
            "_draw_line_chart_v2",
            "_draw_line_chart_v3",
            "_draw_line_chart_v4",
        ]:
            getattr(MetricsTab, name)(None, canvas, data)


if __name__ == "__main__":
    unittest.main()
