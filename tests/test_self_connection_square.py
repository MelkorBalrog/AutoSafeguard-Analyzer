import tkinter as tk

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gui.drawing_helper import GSNDrawingHelper
from gui.architecture import SysMLDiagramWindow, SysMLObject, DiagramConnection
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class DummyCanvas:
    def __init__(self):
        self.lines = []

    def create_line(self, *args, **kwargs):
        self.lines.append(args)
        return len(self.lines)

    def create_polygon(self, *args, **kwargs):
        return 0

    def create_text(self, *args, **kwargs):
        return 0

    def create_rectangle(self, *args, **kwargs):
        return 0


def test_gsn_self_connection_square():
    helper = GSNDrawingHelper()
    canvas = DummyCanvas()
    pt = (50, 50)
    helper.draw_solved_by_connection(canvas, pt, pt)
    assert canvas.lines[0] == (50, 50, 50, 30, 70, 30, 70, 50, 50, 50)


def test_relationship_self_connection_square():
    repo = SysMLRepository.reset_instance()
    diag = SysMLDiagram(diag_id="d", diag_type="Block Definition Diagram")
    repo.diagrams["d"] = diag
    window = SysMLDiagramWindow.__new__(SysMLDiagramWindow)
    window.canvas = DummyCanvas()
    window.zoom = 1.0
    window.repo = repo
    window.diagram_id = "d"
    window.font = None
    obj = SysMLObject(1, "Block", 0, 0)
    conn = DiagramConnection(1, 1, "Association")
    window.draw_connection(obj, obj, conn)
    assert window.canvas.lines[0] == (
        40.0,
        0.0,
        80.0,
        0.0,
        80.0,
        -40.0,
        40.0,
        -40.0,
        40.0,
        0.0,
    )
