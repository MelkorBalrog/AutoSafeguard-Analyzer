import unittest
from gui.architecture import DiagramConnection, format_control_flow_label
from sysml.sysml_repository import SysMLRepository


class ConnectionStereotypeLabelTests(unittest.TestCase):
    def setUp(self):
        SysMLRepository.reset_instance()
        self.repo = SysMLRepository.get_instance()

    def test_association_label_stereotype(self):
        conn = DiagramConnection(1, 2, "Association")
        label = format_control_flow_label(conn, self.repo, None)
        self.assertEqual(label, "<<association>>")

    def test_association_label_with_name(self):
        conn = DiagramConnection(1, 2, "Association", name="rel")
        label = format_control_flow_label(conn, self.repo, None)
        self.assertEqual(label, "<<association>> rel")

    def test_propagate_label_stereotype(self):
        conn = DiagramConnection(1, 2, "Propagate")
        label = format_control_flow_label(conn, self.repo, "Governance Diagram")
        self.assertEqual(label, "<<propagate>>")


if __name__ == "__main__":
    unittest.main()
