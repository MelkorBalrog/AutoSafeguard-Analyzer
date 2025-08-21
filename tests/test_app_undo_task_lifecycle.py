import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp
from sysml.sysml_repository import SysMLRepository


class AppUndoTaskLifecycleTests(unittest.TestCase):
    def _make_app_repo(self):
        SysMLRepository.reset_instance()
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        app = AutoMLApp.__new__(AutoMLApp)
        app._undo_stack = []
        app._redo_stack = []
        app.export_model_data = lambda include_versions=False: repo.to_dict()
        app.apply_model_data = lambda data: repo.from_dict(data)
        app.push_undo_state = AutoMLApp.push_undo_state.__get__(app)
        app.undo = AutoMLApp.undo.__get__(app)
        app.redo = AutoMLApp.redo.__get__(app)
        app.diagram_tabs = {}
        app.refresh_all = lambda: None
        return app, repo, diag

    def test_task_add_move_rename_resize_undo_redo(self):
        for strat in ("v1", "v2", "v3", "v4"):
            with self.subTest(strategy=strat):
                app, repo, diag = self._make_app_repo()

                # Baseline before adding the task
                app.push_undo_state(strategy=strat)

                # Add task
                obj = {
                    "obj_id": 1,
                    "obj_type": "Task",
                    "user_name": "T1",
                    "x": 1.0,
                    "y": 1.0,
                    "width": 10.0,
                    "height": 10.0,
                }
                diag.objects.append(obj)

                # Prepare to move
                app.push_undo_state(strategy=strat)
                obj["x"], obj["y"] = 5.0, 5.0

                # Prepare to rename
                app.push_undo_state(strategy=strat)
                obj["user_name"] = "Renamed"

                # Prepare to resize
                app.push_undo_state(strategy=strat)
                obj["width"], obj["height"] = 20.0, 20.0

                # Undo size
                app.undo(strategy=strat)
                obj = repo.diagrams[diag.diag_id].objects[0]
                self.assertEqual((obj["width"], obj["height"]), (10.0, 10.0))

                # Undo rename
                app.undo(strategy=strat)
                obj = repo.diagrams[diag.diag_id].objects[0]
                self.assertEqual(obj["user_name"], "T1")

                # Undo move
                app.undo(strategy=strat)
                obj = repo.diagrams[diag.diag_id].objects[0]
                self.assertEqual((obj["x"], obj["y"]), (1.0, 1.0))

                # Undo addition
                app.undo(strategy=strat)
                self.assertEqual(len(repo.diagrams[diag.diag_id].objects), 0)

                # Redo addition
                app.redo(strategy=strat)
                obj = repo.diagrams[diag.diag_id].objects[0]
                self.assertEqual((obj["x"], obj["y"]), (1.0, 1.0))
                self.assertEqual((obj["width"], obj["height"]), (10.0, 10.0))
                self.assertEqual(obj["user_name"], "T1")

                # Redo move
                app.redo(strategy=strat)
                obj = repo.diagrams[diag.diag_id].objects[0]
                self.assertEqual((obj["x"], obj["y"]), (5.0, 5.0))

                # Redo rename
                app.redo(strategy=strat)
                obj = repo.diagrams[diag.diag_id].objects[0]
                self.assertEqual(obj["user_name"], "Renamed")

                # Redo resize
                app.redo(strategy=strat)
                obj = repo.diagrams[diag.diag_id].objects[0]
                self.assertEqual((obj["width"], obj["height"]), (20.0, 20.0))


if __name__ == "__main__":
    unittest.main()
