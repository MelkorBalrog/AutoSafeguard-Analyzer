import types

from gui.tooltip import ToolTip


class DummyWidget:
    def __init__(self):
        self.bound = {}

    def bind(self, event, func):
        self.bound[event] = func

    def after_cancel(self, _id):
        pass


class DummyTipWindow:
    def __init__(self):
        self.destroyed = False

    def destroy(self):
        self.destroyed = True


def test_manual_tooltip_hides_on_leave():
    widget = DummyWidget()
    tip = ToolTip(widget, "tip", automatic=False)
    tip.tipwindow = DummyTipWindow()
    # Simulate the pointer leaving the widget
    widget.bound["<Leave>"]()
    assert tip.tipwindow is None
