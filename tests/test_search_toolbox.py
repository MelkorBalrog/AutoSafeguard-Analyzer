import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gui import search_toolbox, messagebox  # noqa: E402


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class DummyListbox:
    def delete(self, *_args):
        pass

    def insert(self, *_args):
        pass

    def select_clear(self, *_args):
        pass

    def selection_set(self, *_args):
        pass

    def activate(self, *_args):
        pass

    def see(self, *_args):
        pass

    def curselection(self):
        return []


class DummyApp:
    hazards: list[str] = []

    def get_all_nodes_in_model(self):
        return []

    def get_all_fmea_entries(self):
        return []

    def get_all_connections(self):
        return []


class SearchToolboxTests(unittest.TestCase):
    def _make_tb(self, app):
        tb = search_toolbox.SearchToolbox.__new__(search_toolbox.SearchToolbox)
        tb.app = app
        tb.search_var = DummyVar()
        tb.case_var = DummyVar(False)
        tb.regex_var = DummyVar(False)
        tb.nodes_var = DummyVar(True)
        tb.connections_var = DummyVar(True)
        tb.failures_var = DummyVar(True)
        tb.hazards_var = DummyVar(True)
        tb.results_box = DummyListbox()
        tb.results = []
        tb.current_index = -1
        return tb

    def test_notifies_on_no_results(self):
        tb = self._make_tb(DummyApp())
        tb.search_var.set("missing")
        infos = []
        with patch.object(messagebox, "showinfo", lambda *a: infos.append(a)):
            tb._run_search()
        self.assertTrue(infos, "User was not notified when no results found")
        self.assertIn("No matches found", infos[0][1])

    def test_search_hazards(self):
        class HazardApp(DummyApp):
            hazards = ["Fire", "Collision"]

        tb = self._make_tb(HazardApp())
        tb.nodes_var.set(False)
        tb.connections_var.set(False)
        tb.failures_var.set(False)
        tb.hazards_var.set(True)
        tb.search_var.set("Fire")
        tb._run_search()
        self.assertEqual(len(tb.results), 1)
        self.assertIn("Hazard - Fire", tb.results[0]["label"])

    def test_search_connection_guard(self):
        class Conn:
            def __init__(self):
                self.name = "linkA"
                self.conn_type = "Flow"
                self.guard = ["g1"]

        class ConnApp(DummyApp):
            def __init__(self):
                self._conns = [Conn()]

            def get_all_connections(self):
                return self._conns

        tb = self._make_tb(ConnApp())
        tb.nodes_var.set(False)
        tb.connections_var.set(True)
        tb.failures_var.set(False)
        tb.hazards_var.set(False)
        tb.search_var.set("g1")
        tb._run_search()
        self.assertEqual(len(tb.results), 1)
        self.assertIn("linkA", tb.results[0]["label"])

if __name__ == "__main__":
    unittest.main()
