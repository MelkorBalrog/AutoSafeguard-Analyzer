import types

from AutoML import AutoMLApp


class DummyStyle:
    def __init__(self):
        self.configured = {}
        self.mapped = {}

    def configure(self, style, **kwargs):
        self.configured[style] = kwargs

    def map(self, style, **kwargs):
        self.mapped[style] = kwargs


def test_nav_button_style_has_active_and_pressed_background():
    app = AutoMLApp.__new__(AutoMLApp)
    app.style = DummyStyle()
    AutoMLApp._init_nav_button_style(app)
    mapping = app.style.mapped["Nav.TButton"]
    assert ("active", "#f2f6fa") in mapping.get("background", [])
    assert ("pressed", "#dae2ea") in mapping.get("background", [])

