import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest
from dataclasses import dataclass, field
from analysis.models import ReliabilityComponent

@dataclass
class SimpleNode:
    user_name: str
    node_type: str
    description: str = ""
    parents: list = field(default_factory=list)
    fmea_component: str = ""
    fmeda_fit: float = 0.0
    failure_mode_ref: int | None = None
    fault_ref: str = ""
    unique_id: int = field(default_factory=lambda: SimpleNode._next_id())

    _id_counter = 1

    @classmethod
    def _next_id(cls):
        i = cls._id_counter
        cls._id_counter += 1
        return i

class DummyApp:
    def __init__(self):
        self.reliability_components = []
        self._basic_events = []

    def get_all_basic_events(self):
        return self._basic_events

    def get_all_failure_modes(self):
        return self._basic_events

    def get_all_fmea_entries(self):
        return self._basic_events

    def get_failure_mode_node(self, node):
        ref = getattr(node, "failure_mode_ref", None)
        if ref:
            for n in self._basic_events:
                if n.unique_id == ref:
                    return n
        return node

    def get_component_name_for_node(self, node):
        parent = node.parents[0] if node.parents else None
        if parent and parent.node_type.upper() not in {"GATE", "TOP EVENT", "RIGOR LEVEL"}:
            return parent.user_name
        return getattr(node, "fmea_component", "")

    def format_failure_mode_label(self, node):
        comp = self.get_component_name_for_node(node)
        label = node.description if node.description else node.user_name
        return f"{comp}: {label}" if comp else label

    def is_passive_component(self, comp_name):
        return any(c.name == comp_name and c.is_passive for c in self.reliability_components)

    def find_passive_failure_mode(self, label):
        target = label.lower().strip()
        for fm in self.get_all_failure_modes():
            comp = self.get_component_name_for_node(fm)
            if self.is_passive_component(comp):
                if self.format_failure_mode_label(fm).lower() == target:
                    return fm
        return None

    # Methods under test - simplified versions of AutoML logic
    def get_faults_for_failure_mode(self, failure_mode_node):
        fm_node = self.get_failure_mode_node(failure_mode_node)
        fm_id = fm_node.unique_id
        faults = []
        for be in self.get_all_basic_events():
            if getattr(be, "failure_mode_ref", None) == fm_id:
                fault = getattr(be, "fault_ref", "") or getattr(be, "description", "")
                if fault:
                    faults.append(fault)
        comp = self.get_component_name_for_node(fm_node)
        if self.is_passive_component(comp):
            label = self.format_failure_mode_label(fm_node)
            if label:
                faults.append(label)
        return sorted(set(faults))

    def get_fit_for_fault(self, fault_name):
        for fm in self.get_all_failure_modes():
            comp = self.get_component_name_for_node(fm)
            if self.is_passive_component(comp):
                if self.format_failure_mode_label(fm).lower() == fault_name.lower():
                    return fm.fmeda_fit
        return 0.0

class PassiveFailureModeTests(unittest.TestCase):
    def test_passive_mode_returns_as_fault(self):
        app = DummyApp()
        comp = ReliabilityComponent("C1", "resistor", is_passive=True)
        app.reliability_components.append(comp)
        fm = SimpleNode("FM", "Basic Event", description="open", fmea_component="C1")
        app._basic_events.append(fm)
        faults = app.get_faults_for_failure_mode(fm)
        self.assertEqual(faults, [app.format_failure_mode_label(fm)])

    def test_get_fit_for_passive_label(self):
        app = DummyApp()
        comp = ReliabilityComponent("C1", "resistor", is_passive=True)
        app.reliability_components.append(comp)
        fm = SimpleNode("FM", "Basic Event", description="open", fmea_component="C1", fmeda_fit=5.0)
        app._basic_events.append(fm)
        label = app.format_failure_mode_label(fm)
        fit = app.get_fit_for_fault(label)
        self.assertEqual(fit, 5.0)

    def test_active_mode_no_extra_fault(self):
        app = DummyApp()
        comp = ReliabilityComponent("C1", "ic", is_passive=False)
        app.reliability_components.append(comp)
        fm = SimpleNode("FM", "Basic Event", description="stuck", fmea_component="C1")
        fault_event = SimpleNode("Fault", "Basic Event", description="short", fault_ref="short")
        fault_event.failure_mode_ref = fm.unique_id
        app._basic_events.extend([fm, fault_event])
        faults = app.get_faults_for_failure_mode(fm)
        self.assertEqual(faults, ["short"])

if __name__ == '__main__':
    unittest.main()
