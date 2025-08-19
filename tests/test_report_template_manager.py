import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.report_template_manager import ReportTemplateManager
from gui import report_template_manager as rtm
import gui.report_template_toolbox as rtt


class DummyListbox:
    def __init__(self):
        self.items: list[str] = []
        self._sel: tuple[int, ...] = ()

    def delete(self, *args):
        self.items.clear()

    def insert(self, index, value):
        self.items.append(value)

    def size(self):
        return len(self.items)

    def get(self, index):
        return self.items[index]

    def curselection(self):
        return self._sel

    def selection_set(self, index):
        self._sel = (index,)


def test_report_template_manager_lists_templates(tmp_path):
    builtin = tmp_path / "builtin"
    builtin.mkdir()
    (builtin / "report_template.json").write_text("{}")
    nested = builtin / "nested"
    nested.mkdir()
    (nested / "nested_template.json").write_text("{}")

    user = tmp_path / "user"
    user.mkdir()
    (user / "custom_template.json").write_text("{}")
    deep = user / "deep"
    deep.mkdir()
    (deep / "deep_template.json").write_text("{}")

    (builtin / "diagram_rules.json").write_text("{}")

    mgr = object.__new__(ReportTemplateManager)
    mgr.builtin_dir = builtin
    mgr.user_dir = user
    mgr.listbox = DummyListbox()
    ReportTemplateManager._refresh_list(mgr)
    names = [mgr.listbox.get(i) for i in range(mgr.listbox.size())]
    assert {"report_template.json", "custom_template.json", "nested_template.json", "deep_template.json"} <= set(names)
    assert "diagram_rules.json" not in names


def test_report_template_manager_add_delete(tmp_path, monkeypatch):
    builtin = tmp_path / "builtin"
    builtin.mkdir()
    mgr = object.__new__(ReportTemplateManager)
    mgr.builtin_dir = builtin
    mgr.user_dir = tmp_path / "user"
    mgr.user_dir.mkdir()
    mgr.listbox = DummyListbox()
    ReportTemplateManager._refresh_list(mgr)
    monkeypatch.setattr(rtm.simpledialog, "askstring", lambda *a, **k: "new")
    mgr._add_template()
    new_path = mgr.user_dir / "new_template.json"
    assert new_path.exists()
    idx = list(mgr.listbox.get(i) for i in range(mgr.listbox.size())).index("new_template.json")
    mgr.listbox.selection_set(idx)
    monkeypatch.setattr(rtm.messagebox, "askyesno", lambda *a, **k: True)
    mgr._delete_template()
    assert not new_path.exists()


def test_report_template_manager_load(tmp_path, monkeypatch):
    builtin = tmp_path / "builtin"
    builtin.mkdir()
    user = tmp_path / "user"
    user.mkdir()
    external = tmp_path / "external_template.json"
    external.write_text("{}")

    mgr = object.__new__(ReportTemplateManager)
    mgr.builtin_dir = builtin
    mgr.user_dir = user
    mgr.listbox = DummyListbox()
    ReportTemplateManager._refresh_list(mgr)

    monkeypatch.setattr(rtm.filedialog, "askopenfilename", lambda **kw: str(external))
    mgr._load_template()

    assert (user / external.name).exists()
    names = [mgr.listbox.get(i) for i in range(mgr.listbox.size())]
    assert external.name in names


def test_report_template_manager_edit_uses_editor(tmp_path, monkeypatch):
    user = tmp_path / "user"
    user.mkdir()
    file = user / "a_template.json"
    file.write_text("{}")

    class DummyTab:
        def __init__(self):
            self.children = []

        def winfo_children(self):
            return self.children

    class DummyApp:
        def __init__(self):
            self.titles = []
            self.tabs = {}

        def _new_tab(self, title):
            self.titles.append(title)
            if title not in self.tabs:
                self.tabs[title] = DummyTab()
            return self.tabs[title]

    class DummyEditor:
        called = 0

        def __init__(self, master, app, path):
            DummyEditor.called += 1
            master.children.append(self)

        def pack(self, **kw):
            pass

    monkeypatch.setattr(rtt, "ReportTemplateEditor", DummyEditor)

    mgr = object.__new__(ReportTemplateManager)
    mgr.builtin_dir = tmp_path / "builtin"
    mgr.builtin_dir.mkdir()
    mgr.user_dir = user
    mgr.listbox = DummyListbox()
    mgr.app = DummyApp()
    ReportTemplateManager._refresh_list(mgr)
    idx = list(mgr.listbox.get(i) for i in range(mgr.listbox.size())).index("a_template.json")
    mgr.listbox.selection_set(idx)
    mgr._edit_template()
    mgr._edit_template()
    assert DummyEditor.called == 1
    assert mgr.app.titles == [f"Report Template: {file.stem}", f"Report Template: {file.stem}"]


def test_report_template_manager_meipass_default(monkeypatch, tmp_path):
    """Templates bundled in executables are discovered via sys._MEIPASS."""

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "nested_template.json").write_text("{}")
    (tmp_path / "top_template.json").write_text("{}")
    monkeypatch.setattr(sys, "_MEIPASS", tmp_path, raising=False)
    mgr = object.__new__(ReportTemplateManager)
    mgr.builtin_dir = ReportTemplateManager._default_templates_dir()
    mgr.user_dir = tmp_path / "user"
    mgr.user_dir.mkdir()
    mgr.listbox = DummyListbox()
    ReportTemplateManager._refresh_list(mgr)
    names = [mgr.listbox.get(i) for i in range(mgr.listbox.size())]
    assert "nested_template.json" in names
    assert "top_template.json" in names
