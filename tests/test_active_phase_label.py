import types

from AutoML import AutoMLApp


class DummyVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class DummyLabel:
    def __init__(self):
        self.text = ""

    def config(self, **kwargs):
        self.text = kwargs.get("text", self.text)


class DummyToolbox:
    def __init__(self):
        self.phase = None

    def set_active_module(self, phase):
        self.phase = phase


def test_active_phase_label_updates():
    app = types.SimpleNamespace(
        lifecycle_var=DummyVar(),
        safety_mgmt_toolbox=DummyToolbox(),
        update_views=lambda: None,
        active_phase_lbl=DummyLabel(),
    )
    app.on_lifecycle_selected = AutoMLApp.on_lifecycle_selected.__get__(app, AutoMLApp)

    app.lifecycle_var.set("Phase1")
    app.on_lifecycle_selected()

    assert app.active_phase_lbl.text == "Active phase: Phase1"
