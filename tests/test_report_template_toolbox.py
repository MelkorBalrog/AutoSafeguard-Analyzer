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


def test_validate_report_template_allows_sysml_diagrams():
    cfg = {
        "elements": {"sys": "sysml_diagrams"},
        "sections": [{"title": "Intro", "content": "<sys>"}],
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


def test_layout_report_template_sysml_diagrams_placeholder():
    data = {
        "elements": {"sys": "sysml_diagrams"},
        "sections": [{"title": "Diagrams", "content": "<sys>"}],
    }
    items, _ = layout_report_template(data)
    assert any(i["type"] == "element" and i["name"] == "sys" for i in items)


def test_validate_report_template_requirement_elements():
    cfg = {
        "elements": {"req_vehicle": "req_vehicle"},
        "sections": [{"title": "Vehicle Reqs", "content": "<req_vehicle>"}],
    }
    assert validate_report_template(cfg) == cfg


def test_report_template_editor_section_crud(tmp_path, monkeypatch):
    import tkinter as tk
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tk not available")

    import gui.report_template_toolbox as rtt

    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text("{\n  \"elements\": {},\n  \"sections\": []\n}")
    editor = rtt.ReportTemplateEditor(root, None, cfg_path)

    class AddDlg:
        def __init__(self, parent, section):
            self.result = {"title": "New", "content": "C"}

    monkeypatch.setattr(rtt, "SectionDialog", AddDlg)
    editor._add_section()
    assert [s["title"] for s in editor.data["sections"]] == ["New"]

    class EditDlg:
        def __init__(self, parent, section):
            self.result = {"title": "Updated", "content": section["content"]}

    monkeypatch.setattr(rtt, "SectionDialog", EditDlg)
    editor.tree.selection_set("sec|0")
    editor._edit_section()
    assert editor.data["sections"][0]["title"] == "Updated"

    editor.tree.selection_set("sec|0")
    editor._delete_section()
    assert editor.data["sections"] == []

    root.destroy()
