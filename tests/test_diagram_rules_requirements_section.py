import sys
from pathlib import Path
import tkinter as tk
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.diagram_rules_toolbox import DiagramRulesEditor


def test_requirement_rules_section_loaded():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    root.withdraw()
    editor = DiagramRulesEditor(root, app=None)
    roots = set(editor.tree.get_children(""))
    root.destroy()
    assert "requirement_rules" in roots
    assert "node_roles" in roots
