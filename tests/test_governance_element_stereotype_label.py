import unittest

from gui.architecture import SysMLDiagramWindow, SysMLObject
from sysml.sysml_repository import SysMLRepository


class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)

    def metrics(self, name: str) -> int:
        return 1


class DummyWindow:
    _object_label_lines = SysMLDiagramWindow._object_label_lines

    def __init__(self, diag_id):
        self.repo = SysMLRepository.get_instance()
        self.zoom = 1.0
        self.font = DummyFont()
        self.diagram_id = diag_id

    def _wrap_text_to_width(self, text: str, _width: float) -> list[str]:
        return [text]


class GovernanceElementStereotypeTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None

    def test_task_label_includes_stereotype(self):
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Governance Diagram")
        elem = repo.create_element("Action", name="Draft Plan")
        obj = SysMLObject(1, "Action", 0.0, 0.0, element_id=elem.elem_id, properties={"name": "Draft Plan"})
        win = DummyWindow(diag.diag_id)
        lines = win._object_label_lines(obj)
        self.assertEqual("<<task>>", lines[0])
        self.assertEqual("Draft Plan", lines[1])

    def test_decision_label_includes_stereotype(self):
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Governance Diagram")
        elem = repo.create_element("Decision", name="Gate")
        obj = SysMLObject(2, "Decision", 0.0, 0.0, element_id=elem.elem_id, properties={"name": "Gate"})
        win = DummyWindow(diag.diag_id)
        lines = win._object_label_lines(obj)
        self.assertEqual("<<decision>>", lines[0])
        self.assertEqual("Gate", lines[1])


if __name__ == "__main__":
    unittest.main()
