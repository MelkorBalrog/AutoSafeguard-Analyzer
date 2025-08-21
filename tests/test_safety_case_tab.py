import types
import gui.safety_case_explorer as safety_case_explorer


def test_open_case_uses_app_tab(monkeypatch):
    case = types.SimpleNamespace(name="MyCase", solutions=[])
    explorer = safety_case_explorer.SafetyCaseExplorer.__new__(
        safety_case_explorer.SafetyCaseExplorer
    )
    explorer.tree = types.SimpleNamespace(selection=lambda: ("i1",))
    explorer.item_map = {"i1": ("case", case)}
    called = {}

    class DummyTab:
        def __init__(self):
            self.packed = False
        def pack(self, **kwargs):
            self.packed = True

    def fake_new_tab(title):
        called["title"] = title
        return DummyTab()

    explorer.app = types.SimpleNamespace(_new_tab=fake_new_tab)

    class DummyTable:
        def __init__(self, master, case, app=None):
            called["master"] = master
            called["case"] = case
        def pack(self, **kwargs):
            called["packed"] = True

    monkeypatch.setattr(safety_case_explorer, "SafetyCaseTable", DummyTable)
    monkeypatch.setattr(
        safety_case_explorer.tk,
        "Toplevel",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Toplevel called")),
    )

    safety_case_explorer.SafetyCaseExplorer.open_item(explorer)

    assert called["title"] == "Safety & Security Report: MyCase"
    assert called["master"].packed is False
    assert called["case"] is case
    assert called.get("packed") is True
