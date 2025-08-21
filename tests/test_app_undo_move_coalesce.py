import unittest
import json

from AutoML import AutoMLApp


class AppUndoMoveCoalesceTests(unittest.TestCase):
    def _make_app(self):
        from sysml.sysml_repository import SysMLRepository

        class DummyRepo:
            def push_undo_state(self, *a, **k):
                pass

            def undo(self):
                pass

            def redo(self):
                pass

        SysMLRepository._instance = DummyRepo()
        self.addCleanup(SysMLRepository.reset_instance)

        app = AutoMLApp.__new__(AutoMLApp)
        app._undo_stack = []
        app._redo_stack = []
        state = {"diagrams": [{"objects": [{"x": 0.0, "y": 0.0}]}]}
        app._state = state

        def export_model_data(include_versions: bool = False):
            return json.loads(json.dumps(app._state))

        def apply_model_data(data):
            app._state = json.loads(json.dumps(data))

        app.export_model_data = export_model_data
        app.apply_model_data = apply_model_data
        app.refresh_all = lambda: None
        app.diagram_tabs = {}
        app.push_undo_state = AutoMLApp.push_undo_state.__get__(app)
        app.undo = AutoMLApp.undo.__get__(app)
        app.redo = AutoMLApp.redo.__get__(app)
        return app

    def test_strategies_only_store_first_and_last(self):
        for strat in ("v1", "v2", "v3", "v4"):
            with self.subTest(strategy=strat):
                app = self._make_app()
                base_len = len(app._undo_stack)
                app.push_undo_state(strategy=strat)
                for i in range(1, 5):
                    app._state["diagrams"][0]["objects"][0]["x"] = float(i)
                    app._state["diagrams"][0]["objects"][0]["y"] = float(i)
                    app.push_undo_state(strategy=strat)
                self.assertEqual(len(app._undo_stack), base_len + 2)

    def test_undo_redo_restores_positions(self):
        for strat in ("v1", "v2", "v3", "v4"):
            with self.subTest(strategy=strat):
                app = self._make_app()
                app.push_undo_state(strategy=strat)
                for i in range(1, 5):
                    app._state["diagrams"][0]["objects"][0]["x"] = float(i)
                    app._state["diagrams"][0]["objects"][0]["y"] = float(i)
                    app.push_undo_state(strategy=strat)
                app.undo()
                self.assertEqual(app._state["diagrams"][0]["objects"][0]["x"], 0.0)
                self.assertEqual(app._state["diagrams"][0]["objects"][0]["y"], 0.0)
                app.redo()
                self.assertEqual(app._state["diagrams"][0]["objects"][0]["x"], 4.0)
                self.assertEqual(app._state["diagrams"][0]["objects"][0]["y"], 4.0)


if __name__ == "__main__":
    unittest.main()
