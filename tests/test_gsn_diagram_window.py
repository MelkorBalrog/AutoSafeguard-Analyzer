from gui.gsn_diagram_window import GSNDiagramWindow


def test_gsn_diagram_window_button_labels():
    labels = GSNDiagramWindow.TOOLBOX_BUTTONS
    assert "Goal" in labels
    assert "Solved By" in labels
    assert "In Context Of" in labels
    assert "Zoom In" in labels


def test_zoom_methods_adjust_factor():
    win = GSNDiagramWindow.__new__(GSNDiagramWindow)
    win.zoom = 1.0
    win.refresh = lambda: None
    GSNDiagramWindow.zoom_in(win)
    assert win.zoom > 1.0
    GSNDiagramWindow.zoom_out(win)
    assert abs(win.zoom - 1.0) < 1e-6
