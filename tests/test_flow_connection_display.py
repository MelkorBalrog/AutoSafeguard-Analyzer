import unittest
from gui.architecture import DiagramConnection, _arrow_forward_types, format_control_flow_label
from sysml.sysml_repository import SysMLRepository


class FlowConnectionDisplayTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_flow_arrow_and_label(self):
        arrow_default = "forward" if "Flow" in _arrow_forward_types() else "none"
        conn = DiagramConnection(1, 2, "Flow", name="<<flow>>", arrow=arrow_default)
        label = format_control_flow_label(conn, self.repo, "Governance Diagram")
        self.assertEqual(label, "<<flow>>")
        self.assertEqual(conn.arrow, "forward")


if __name__ == "__main__":
    unittest.main()
