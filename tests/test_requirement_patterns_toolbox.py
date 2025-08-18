import sys
from pathlib import Path
import types

sys.path.append(str(Path(__file__).resolve().parents[1]))

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
import tkinter as tk
import pytest
from gui.requirement_patterns_toolbox import RequirementPatternsEditor


def test_requirement_patterns_toolbox_single_instance():
    """Opening requirement patterns toolbox twice doesn't duplicate editor."""

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

    import gui.requirement_patterns_toolbox as rpt

    rpt.RequirementPatternsEditor = DummyEditor

    class DummyApp:
        open_requirement_patterns_toolbox = FaultTreeApp.open_requirement_patterns_toolbox

        def __init__(self):
            self.doc_nb = DummyNotebook()

        def _new_tab(self, title):
            return DummyTab()

    app = DummyApp()
    app.open_requirement_patterns_toolbox()
    app.open_requirement_patterns_toolbox()
    assert DummyEditor.created == 1


def test_pattern_tree_wraps_text(tmp_path):
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")

    cfg = tmp_path / "patterns.json"
    cfg.write_text("[]")

    editor = RequirementPatternsEditor(root, object(), cfg)
    editor.data = [{"Trigger": "A " * 30, "Template": "B " * 30}]
    editor._populate_pattern_tree()
    vals = editor.tree.item(editor.tree.get_children()[0], "values")
    assert "\n" in vals[0]
    assert "\n" in vals[1]
    root.destroy()
