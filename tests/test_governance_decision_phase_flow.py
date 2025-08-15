import sys
from pathlib import Path
import unittest
from dataclasses import asdict

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.architecture import GovernanceDiagramWindow, SysMLObject, SysMLDiagramWindow
from sysml.sysml_repository import SysMLRepository


class GovernanceDecisionPhaseFlowTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def _window(self, diag):
        class Win:
            _decision_used_corners = SysMLDiagramWindow._decision_used_corners

            def __init__(self, repo, diagram_id):
                self.repo = repo
                self.diagram_id = diagram_id
                self.connections = []

        return Win(self.repo, diag.diag_id)

    def test_decision_to_phase_flow_allowed(self):
        repo = self.repo
        dec_elem = repo.create_element("Decision", name="Gate")
        diag = repo.create_diagram("Governance Diagram", name="Gov")
        repo.add_element_to_diagram(diag.diag_id, dec_elem.elem_id)
        decision = SysMLObject(
            1,
            "Decision",
            0.0,
            0.0,
            element_id=dec_elem.elem_id,
            properties={"name": "Gate"},
        )
        phase = SysMLObject(2, "Lifecycle Phase", 0.0, 100.0, properties={"name": "P2"})
        diag.objects = [asdict(decision), asdict(phase)]
        win = self._window(diag)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, decision, phase, "Flow")
        self.assertTrue(valid)
        valid, _ = GovernanceDiagramWindow.validate_connection(win, phase, decision, "Flow")
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()

