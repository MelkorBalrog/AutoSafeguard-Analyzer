import types
import unittest

from AutoML import AutoMLApp


class DummyWindow:
    def __init__(self):
        self.copied = False
        self.cut = False
        self.pasted = False

    def copy_selected(self):
        self.copied = True

    def cut_selected(self):
        self.cut = True

    def paste_selected(self):
        self.pasted = True


class DiagramClipboardDelegationTests(unittest.TestCase):
    def setUp(self):
        self.app = AutoMLApp.__new__(AutoMLApp)
        self.win = DummyWindow()
        self.app.root = types.SimpleNamespace(focus_get=lambda: self.win)
        self.app.selected_node = None
        self.app.clipboard_node = None
        self.app.root_node = None

    def test_copy_cut_paste_delegate_to_window(self):
        self.app.copy_node()
        self.app.cut_node()
        # Put something on clipboard for paste
        self.app.clipboard_node = object()
        self.app.paste_node()
        assert self.win.copied and self.win.cut and self.win.pasted


if __name__ == "__main__":
    unittest.main()
