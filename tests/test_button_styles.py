import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from gui.mac_button_style import (
    apply_purplish_button_style,
    apply_translucid_button_style,
)
from gui import toolboxes


class DummyStyle:
    def __init__(self):
        self.configured = {}
        self.mapped = {}

    def configure(self, style, **kwargs):
        self.configured[style] = kwargs

    def map(self, style, **kwargs):
        self.mapped[style] = kwargs


def test_apply_purplish_button_style_configures_background():
    style = DummyStyle()
    apply_purplish_button_style(style)
    assert style.configured["Purple.TButton"]["background"] == "#9b59b6"


def test_apply_translucid_button_style_sets_flat_relief():
    style = DummyStyle()
    apply_translucid_button_style(style)
    assert style.configured["Translucid.TButton"]["relief"] == "flat"


def test_configure_table_style_uses_translucid(monkeypatch):
    called = {}
    
    class DummyStyle:
        def theme_use(self, *a, **k):
            pass

        def configure(self, *a, **k):
            pass

        def map(self, *a, **k):
            pass

    def fake_apply(style):
        called["ok"] = isinstance(style, DummyStyle)

    monkeypatch.setattr(toolboxes.ttk, "Style", lambda: DummyStyle())
    monkeypatch.setattr(toolboxes, "apply_translucid_button_style", fake_apply)
    toolboxes.configure_table_style("TestStyle")
    assert called.get("ok")
