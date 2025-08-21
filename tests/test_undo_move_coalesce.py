import unittest
from sysml.sysml_repository import SysMLRepository, SysMLDiagram


class UndoMoveCoalesceTests(unittest.TestCase):
    def _prepare_repo(self):
        SysMLRepository.reset_instance()
        repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Use Case Diagram")
        repo.diagrams[diag.diag_id] = diag
        diag.objects.append({"obj_id": 1, "obj_type": "Block", "x": 0.0, "y": 0.0})
        return repo, diag

    def test_strategies_only_store_first_and_last(self):
        for strat in ("v1", "v2", "v3", "v4"):
            with self.subTest(strategy=strat):
                repo, diag = self._prepare_repo()
                base_len = len(repo._undo_stack)
                repo.push_undo_state(strategy=strat)
                for i in range(1, 5):
                    repo.push_undo_state(strategy=strat)
                    diag.objects[0]["x"] = float(i)
                    diag.objects[0]["y"] = float(i)
                self.assertEqual(len(repo._undo_stack), base_len + 2)


if __name__ == '__main__':
    unittest.main()

