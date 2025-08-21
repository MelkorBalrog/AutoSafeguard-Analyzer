import unittest
from sysml.sysml_repository import SysMLRepository, SysMLDiagram

class UndoMoveCoalesceTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()
        diag = SysMLDiagram(diag_id="d", diag_type="Use Case Diagram")
        self.repo.diagrams[diag.diag_id] = diag
        diag.objects.append({"obj_id": 1, "obj_type": "Block", "x": 0.0, "y": 0.0})
        self.diag = diag

    def test_multiple_moves_coalesce_to_single_state(self):
        # simulate several incremental moves, each pushing an undo state
        for i in range(5):
            self.repo.push_undo_state()
            self.diag.objects[0]["x"] = float(i)
            self.diag.objects[0]["y"] = float(i)
        # The initial creation of the diagram stores one state. All subsequent
        # pushes during the drag are merged, leaving only a single additional
        # entry for the final position.
        self.assertEqual(len(self.repo._undo_stack), 2)

if __name__ == '__main__':
    unittest.main()
