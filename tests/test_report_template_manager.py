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
    (tmp_path / "report_template.json").write_text("{}")
    (tmp_path / "custom_template.json").write_text("{}")
    (tmp_path / "diagram_rules.json").write_text("{}")
    mgr = object.__new__(ReportTemplateManager)
    mgr.templates_dir = tmp_path
    mgr.listbox = DummyListbox()
    ReportTemplateManager._refresh_list(mgr)
    names = [mgr.listbox.get(i) for i in range(mgr.listbox.size())]
    assert "report_template.json" in names
    assert "custom_template.json" in names
    assert "diagram_rules.json" not in names


def test_report_template_manager_add_delete(tmp_path, monkeypatch):
    mgr = object.__new__(ReportTemplateManager)
    mgr.templates_dir = tmp_path
    mgr.listbox = DummyListbox()
    ReportTemplateManager._refresh_list(mgr)
    monkeypatch.setattr(rtm.simpledialog, "askstring", lambda *a, **k: "new")
    mgr._add_template()
    new_path = tmp_path / "new_template.json"
    assert new_path.exists()
    idx = list(mgr.listbox.get(i) for i in range(mgr.listbox.size())).index("new_template.json")
    mgr.listbox.selection_set(idx)
    monkeypatch.setattr(rtm.messagebox, "askyesno", lambda *a, **k: True)
    mgr._delete_template()
    assert not new_path.exists()


def test_report_template_manager_edit_uses_editor(tmp_path, monkeypatch):
    file = tmp_path / "a_template.json"
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
    mgr.templates_dir = tmp_path
    mgr.listbox = DummyListbox()
    mgr.app = DummyApp()
    ReportTemplateManager._refresh_list(mgr)
    idx = list(mgr.listbox.get(i) for i in range(mgr.listbox.size())).index("a_template.json")
    mgr.listbox.selection_set(idx)
    mgr._edit_template()
    mgr._edit_template()
    assert DummyEditor.called == 1
    assert mgr.app.titles == [f"Report Template: {file.stem}", f"Report Template: {file.stem}"]
