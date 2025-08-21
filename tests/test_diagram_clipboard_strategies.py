import unittest
import types

# Provide dummy PIL modules to satisfy imports when AutoML modules are imported
import sys
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from gui.diagram_clipboard import (
    ModuleClipboardStrategy,
    ClassClipboardStrategy,
    RepositoryClipboardStrategy,
    TkClipboardStrategy,
)


class Dummy:
    pass


class DummyRepo:
    pass


class ClipboardStrategyTests(unittest.TestCase):
    def setUp(self):
        self.obj = Dummy()

    def _assert_copy_paste(self, strategy):
        strategy.copy(self.obj)
        pasted = strategy.paste()
        self.assertIsInstance(pasted, Dummy)
        self.assertIsNot(pasted, self.obj)

    def test_module_strategy(self):
        self._assert_copy_paste(ModuleClipboardStrategy())

    def test_class_strategy(self):
        self._assert_copy_paste(ClassClipboardStrategy())

    def test_repository_strategy(self):
        self._assert_copy_paste(RepositoryClipboardStrategy(DummyRepo()))

    def test_tk_strategy(self):
        import tkinter as tk

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk not available")
        root.withdraw()
        try:
            self._assert_copy_paste(TkClipboardStrategy(root))
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
