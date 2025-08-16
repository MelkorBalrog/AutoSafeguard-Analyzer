import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import SAFETY_AI_RELATIONS, GovernanceDiagramWindow
from gui.style_manager import StyleManager


def test_safety_ai_relations_have_icons_and_colors():
    win = GovernanceDiagramWindow.__new__(GovernanceDiagramWindow)
    style = StyleManager.get_instance()
    for rel in SAFETY_AI_RELATIONS:
        assert win._shape_for_tool(rel) == "relation"
        assert style.get_color(rel) != "#FFFFFF"
