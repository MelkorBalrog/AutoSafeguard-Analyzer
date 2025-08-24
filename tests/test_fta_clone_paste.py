import importlib.util
import os
import sys
import types
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "AutoML", repo_root / "__init__.py", submodule_search_locations=[str(repo_root)]
)
automl = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = automl
spec.loader.exec_module(automl)
AutoMLApp = automl.AutoMLApp
FaultTreeNode = automl.FaultTreeNode
messagebox = automl.messagebox


def _make_app_with_nodes():
    app = AutoMLApp.__new__(AutoMLApp)
    app.top_events = []
    app.root_node = None
    app.selected_node = None
    app.analysis_tree = types.SimpleNamespace(selection=lambda: ())
    app.update_views = lambda: None
    app._diagram_copy_strategy1 = app._diagram_copy_strategy2 = lambda: False
    app._diagram_copy_strategy3 = app._diagram_copy_strategy4 = lambda: False
    app._find_gsn_diagram = lambda node: None
    app._focused_gsn_window = lambda: None
    app._focused_cbn_window = lambda: None
    app._find_cbn_diagram = lambda node: None
    app._focused_arch_window = lambda t=None: None
    messagebox.showinfo = lambda *a, **k: None
    messagebox.showwarning = lambda *a, **k: None
    return app


def test_fta_copy_paste_creates_clone():
    app = _make_app_with_nodes()
    root = FaultTreeNode("Root", "TOP EVENT")
    child = FaultTreeNode("Child", "GATE", parent=root)
    root.children.append(child)
    app.root_node = root
    app.top_events.append(root)
    app.selected_node = child

    app.copy_node()
    assert app.clipboard_node is child

    app.selected_node = root
    app.paste_node()

    assert len(root.children) == 2
    pasted = root.children[-1]
    assert pasted is not child
    assert pasted.original is child
    assert not pasted.is_primary_instance


def test_fta_copy_paste_clone_across_module():
    app = _make_app_with_nodes()

    alt_spec = importlib.util.spec_from_file_location(
        "alt_fault_tree_node", repo_root / "mainappsrc/models/fault_tree_node.py"
    )
    alt_module = importlib.util.module_from_spec(alt_spec)
    alt_spec.loader.exec_module(alt_module)
    AltFaultTreeNode = alt_module.FaultTreeNode

    root = AltFaultTreeNode("Root", "TOP EVENT")
    child = AltFaultTreeNode("Child", "GATE", parent=root)
    root.children.append(child)
    app.root_node = root
    app.top_events.append(root)
    app.selected_node = child

    app.copy_node()
    app.selected_node = root
    app.paste_node()

    assert len(root.children) == 2
    first, second = root.children
    assert first is child
    assert second is not child
    assert second.original is child
