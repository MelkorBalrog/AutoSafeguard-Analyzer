import sys
from types import SimpleNamespace
from unittest.mock import MagicMock
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mainappsrc.AutoML import AutoMLApp


def test_opening_fta_sets_mode_to_fta(monkeypatch):
    app = AutoMLApp.__new__(AutoMLApp)
    te = SimpleNamespace(unique_id=1)
    app.top_events = [te]
    app.diagram_mode = "PAA"
    app.ensure_fta_tab = MagicMock()
    app.doc_nb = MagicMock()
    app.canvas_tab = object()
    app.open_page_diagram = MagicMock()

    app.analysis_tree = MagicMock()
    app.analysis_tree.identify_row.return_value = "item1"
    app.analysis_tree.item.return_value = ("fta", "1")

    event = SimpleNamespace(y=0)
    app.on_analysis_tree_double_click(event)

    assert app.diagram_mode == "FTA"
    app.ensure_fta_tab.assert_called_once()
    app.open_page_diagram.assert_called_once_with(te)
