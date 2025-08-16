import sys
from pathlib import Path
import types

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Stub out Pillow dependencies so importing the main app doesn't require Pillow
PIL_stub = types.ModuleType("PIL")
PIL_stub.Image = types.SimpleNamespace()
PIL_stub.ImageTk = types.SimpleNamespace()
PIL_stub.ImageDraw = types.SimpleNamespace()
PIL_stub.ImageFont = types.SimpleNamespace()
sys.modules.setdefault("PIL", PIL_stub)
sys.modules.setdefault("PIL.Image", PIL_stub.Image)
sys.modules.setdefault("PIL.ImageTk", PIL_stub.ImageTk)
sys.modules.setdefault("PIL.ImageDraw", PIL_stub.ImageDraw)
sys.modules.setdefault("PIL.ImageFont", PIL_stub.ImageFont)

from AutoML import FaultTreeApp


def test_report_template_toolbox_single_instance():
    """Opening report template toolbox twice doesn't duplicate editor."""

    class DummyTab:
        def winfo_exists(self):
            return True

    class DummyNotebook:
        def add(self, tab, text):
            pass

        def select(self, tab):
            pass

    class DummyEditor:
        created = 0

        def __init__(self, master, app, path):
            DummyEditor.created += 1

        def pack(self, **kwargs):
            pass

        def winfo_exists(self):
            return True

    import gui.report_template_toolbox as rtt

    rtt.ReportTemplateEditor = DummyEditor

    class DummyApp:
        open_report_template_toolbox = FaultTreeApp.open_report_template_toolbox

        def __init__(self):
            self.doc_nb = DummyNotebook()

        def _new_tab(self, title):
            return DummyTab()

    app = DummyApp()
    app.open_report_template_toolbox()
    app.open_report_template_toolbox()
    assert DummyEditor.created == 1
