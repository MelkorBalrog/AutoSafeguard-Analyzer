import sys
from pathlib import Path
import types
import pytest

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
from config import validate_report_template
from gui.report_template_toolbox import layout_report_template


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


def test_validate_report_template_with_elements():
    cfg = {
        "elements": {"diag": "diagram"},
        "sections": [{"title": "Intro", "content": "See <diag>"}],
    }
    assert validate_report_template(cfg) == cfg


def test_validate_report_template_unknown_element():
    cfg = {
        "elements": {"diag": "diagram"},
        "sections": [{"title": "Intro", "content": "<missing>"}],
    }
    with pytest.raises(ValueError):
        validate_report_template(cfg)


def test_validate_report_template_ignores_html_tags():
    cfg = {
        "elements": {"diag": "diagram"},
        "sections": [
            {
                "title": "Intro",
                "content": "<b>Bold</b><br/><diag>",
            }
        ],
    }
    assert validate_report_template(cfg) == cfg


def test_layout_report_template_basic():
    data = {
        "elements": {"img": "diagram"},
        "sections": [{"title": "Intro", "content": "Hello\n<img>World"}],
    }
    items, height = layout_report_template(data)
    assert height > 0
    types = [i["type"] for i in items]
    assert "title" in types and "element" in types and "text" in types


def test_layout_report_template_ignores_html_tags():
    data = {
        "elements": {"diag": "diagram"},
        "sections": [
            {"title": "Intro", "content": "<b>Bold</b><br/><diag>"}
        ],
    }
    items, _ = layout_report_template(data)
    names = [i.get("name") for i in items if i["type"] == "element"]
    assert names == ["diag"]
