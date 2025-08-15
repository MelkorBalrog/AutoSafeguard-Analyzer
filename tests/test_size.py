import unittest
from gui.architecture import SysMLObject, SysMLDiagramWindow
from sysml.sysml_repository import SysMLRepository

class DummyFont:
    def measure(self, text: str) -> int:
        return len(text)

    def metrics(self, name: str) -> int:
        return 1

class DummyWindow:
    def __init__(self):
        self.repo = SysMLRepository.get_instance()
        self.zoom = 1.0
        self.font = DummyFont()

    ensure_text_fits = SysMLDiagramWindow.ensure_text_fits
    _object_label_lines = SysMLDiagramWindow._object_label_lines
    _min_block_size = SysMLDiagramWindow._min_block_size
    _min_action_size = SysMLDiagramWindow._min_action_size
    _min_data_acquisition_size = SysMLDiagramWindow._min_data_acquisition_size
    _wrap_text_to_width = SysMLDiagramWindow._wrap_text_to_width

class EnsureTextFitsTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository._instance = None
        self.repo = SysMLRepository.get_instance()

    def test_part_width_expands_for_properties(self):
        win = DummyWindow()
        part = SysMLObject(
            1,
            "Part",
            0,
            0,
            width=10,
            height=10,
            properties={"name": "P", "fit": "123456789"},
        )
        part.requirements = []
        win.ensure_text_fits(part)
        self.assertGreater(part.width, 10)

    def test_action_width_does_not_expand_for_name(self):
        win = DummyWindow()
        action = SysMLObject(
            1,
            "Action",
            0,
            0,
            width=10,
            height=10,
            properties={"name": "LongActionName"},
        )
        action.requirements = []
        win.ensure_text_fits(action)
        self.assertEqual(action.width, 10)

    def test_action_min_size(self):
        win = DummyWindow()
        elem = win.repo.create_element("Action", name="Act")
        action = SysMLObject(
            1,
            "Action",
            0,
            0,
            element_id=elem.elem_id,
            width=10,
            height=10,
            properties={"name": "Act"},
        )
        action.requirements = []
        min_w, min_h = win._min_action_size(action)
        self.assertEqual(min_w, len("Act") + 6)
        self.assertEqual(min_h, 7)

    def test_decision_and_merge_sizes_remain_fixed(self):
        win = DummyWindow()
        decision = SysMLObject(
            1,
            "Decision",
            0,
            0,
            width=40,
            height=40,
            properties={"name": "Decide"},
        )
        merge = SysMLObject(
            2,
            "Merge",
            0,
            0,
            width=40,
            height=40,
            properties={"name": "MergeNode"},
        )
        for obj in (decision, merge):
            obj.requirements = []
            win.ensure_text_fits(obj)
            self.assertEqual(obj.width, 40)
            self.assertEqual(obj.height, 40)

    def test_data_acquisition_sizes_to_text(self):
        win = DummyWindow()
        obj = SysMLObject(
            1,
            "Data acquisition",
            0,
            0,
            width=120,
            height=80,
            properties={"compartments": "abc;de"},
        )
        obj.requirements = []
        win.ensure_text_fits(obj)
        self.assertEqual(obj.width, len("abc") + 8)
        self.assertEqual(obj.height, 2 + 8)

if __name__ == "__main__":
    unittest.main()
