import unittest

from gui.architecture import format_control_flow_label


class ControlFlowLabelTests(unittest.TestCase):
    def test_format_with_name_and_guard(self):
        self.assertEqual(
            format_control_flow_label("Do", ["g1", "g2"]),
            "[g1 and g2] {Do}",
        )

    def test_format_with_only_guard(self):
        self.assertEqual(
            format_control_flow_label("", ["cond"]),
            "[cond]",
        )

    def test_format_with_only_name(self):
        self.assertEqual(
            format_control_flow_label("Act", []),
            "{Act}",
        )


if __name__ == "__main__":
    unittest.main()

