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
    _block_compartments = SysMLDiagramWindow._block_compartments
    _min_block_size = SysMLDiagramWindow._min_block_size
    _min_action_size = SysMLDiagramWindow._min_action_size
    _min_data_acquisition_size = SysMLDiagramWindow._min_data_acquisition_size
    _wrap_text_to_width = SysMLDiagramWindow._wrap_text_to_width
    _resize_block_to_content = SysMLDiagramWindow._resize_block_to_content

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

    def test_data_acquisition_default_and_resize(self):
        win = DummyWindow()
        obj = SysMLObject(
            1,
            "Data acquisition",
            0,
            0,
            width=120,
            height=80,
            properties={"compartments": ""},
        )
        obj.requirements = []
        win.ensure_text_fits(obj)
        self.assertEqual(obj.width, 120)
        self.assertEqual(obj.height, 80)
        obj.properties["compartments"] = "a" * 200 + ";de"
        win.ensure_text_fits(obj)
        self.assertGreater(obj.width, 120)
        obj.properties["compartments"] = ";".join(f"line{i}" for i in range(100))
        win.ensure_text_fits(obj)
        self.assertGreater(obj.height, 80)

    def test_block_resizes_when_compartments_toggle(self):
        win = DummyWindow()
        block = SysMLObject(
            1,
            "Block",
            0,
            0,
            width=10,
            height=10,
            properties={"name": "B", "partProperties": "p1,p2"},
        )
        block.requirements = []
        win._resize_block_to_content(block)
        expanded_h = block.height
        block.collapsed["Parts"] = True
        win._resize_block_to_content(block)
        collapsed_h = block.height
        self.assertLess(collapsed_h, expanded_h)
        block.collapsed["Parts"] = False
        win._resize_block_to_content(block)
        self.assertGreater(block.height, collapsed_h)

if __name__ == "__main__":
    unittest.main()
