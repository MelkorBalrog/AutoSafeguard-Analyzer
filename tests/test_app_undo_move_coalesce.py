import unittest
import json

from AutoML import AutoMLApp


class AppUndoMoveCoalesceTests(unittest.TestCase):
    def _make_app(self):
        app = AutoMLApp.__new__(AutoMLApp)
        app._undo_stack = []
        app._redo_stack = []
        state = {"diagrams": [{"objects": [{"x": 0.0, "y": 0.0}]}]}
        app._state = state

        def export_model_data(include_versions: bool = False):
            return json.loads(json.dumps(app._state))

        app.export_model_data = export_model_data
        app.push_undo_state = AutoMLApp.push_undo_state.__get__(app)
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


if __name__ == "__main__":
    unittest.main()
