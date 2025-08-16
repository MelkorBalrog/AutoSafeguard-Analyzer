import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import (
    SAFETY_AI_RELATIONS,
    GOV_ELEMENT_RELATIONS,
    GovernanceDiagramWindow,
)
from unittest.mock import patch


def test_relation_icons_are_black():
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    with patch("gui.architecture.draw_icon") as draw:
        draw.return_value = object()
        for rel in set(SAFETY_AI_RELATIONS + GOV_ELEMENT_RELATIONS):
            assert win._shape_for_tool(rel) == "relation"
            win._icon_for(rel)
            draw.assert_called_with("relation", "black")
            draw.reset_mock()
