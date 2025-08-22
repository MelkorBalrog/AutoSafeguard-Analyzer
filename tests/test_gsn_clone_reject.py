import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gsn.nodes import GSNNode
from gsn.diagram import GSNDiagram
from AutoML import AutoMLApp, AutoML_Helper
from gui import messagebox


def test_clone_rejects_unsupported_types():
    strategy = GSNNode("S", "Strategy")
    with pytest.raises(ValueError):
        strategy.clone()
    module = GSNNode("M", "Module")
    with pytest.raises(ValueError):
        module.clone()


def test_paste_rejects_disallowed_clone():
    root = GSNNode("Root", "Goal")
    strat = GSNNode("Strat", "Strategy")
    root.add_child(strat)
    diag = GSNDiagram(root)
    app = AutoMLApp.__new__(AutoMLApp)
    app.root_node = root
    app.top_events = []
    app.clipboard_node = strat
    app.selected_node = root
    app.analysis_tree = type("T", (), {"selection": lambda self: [], "item": lambda *a, **k: {}})()
    app.cut_mode = False
    app.update_views = lambda: None
    app._find_gsn_diagram = lambda n: diag
    AutoML_Helper.calculate_assurance_recursive = lambda *a, **k: None
    called = {}
    messagebox.showwarning = lambda *a, **k: called.setdefault("msg", a[1] if len(a) > 1 else "")
    app.paste_node()
    assert len(root.children) == 1
    assert called