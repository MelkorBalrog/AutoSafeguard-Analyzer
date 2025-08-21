import unittest

from AutoML import AutoMLApp


class DummyRoot:
    def __init__(self):
        self.bindings = {}

    def bind_all(self, sequence, func, add=None):
        self.bindings[sequence] = func

    def event_generate(self, sequence):
        func = self.bindings[sequence]
        return func(None)


class HotkeyUndoRedoTests(unittest.TestCase):
    def test_ctrl_z_y_trigger_actions(self):
        root = DummyRoot()
        app = AutoMLApp.__new__(AutoMLApp)
        called = []

        def undo(strategy="v4"):
            called.append(("undo", strategy))

        def redo(strategy="v4"):
            called.append(("redo", strategy))

        app.undo = undo
        app.redo = redo
        app._undo_hotkey = AutoMLApp._undo_hotkey.__get__(app)
        app._redo_hotkey = AutoMLApp._redo_hotkey.__get__(app)

        root.bind_all("<Control-z>", app._undo_hotkey)
        root.bind_all("<Control-y>", app._redo_hotkey)

        res1 = root.event_generate("<Control-z>")
        res2 = root.event_generate("<Control-y>")

        self.assertEqual(called, [("undo", "v4"), ("redo", "v4")])
        self.assertEqual(res1, "break")
        self.assertEqual(res2, "break")


if __name__ == "__main__":
    unittest.main()
