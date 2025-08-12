import unittest

from AutoML import FaultTreeApp, FaultTreeNode
from analysis.models import HazopDoc, HazopEntry, HaraDoc, HaraEntry


class OddValidationTargetTests(unittest.TestCase):
    def test_traces_validation_targets_from_scenario_description(self):
        app = FaultTreeApp.__new__(FaultTreeApp)
        app.scenario_libraries = [
            {
                "name": "Default",
                "scenarios": [
                    {
                        "name": "Pedestrians crossing",
                        "description": "Vehicle approaches [[Intersection]]",
                    }
                ],
            }
        ]
        hazop_entry = HazopEntry(
            function="F", malfunction="M", mtype="No/Not", scenario="Pedestrians crossing",
            conditions="", hazard="H", safety=True, rationale="", covered=False, covered_by=""
        )
        app.hazop_docs = [HazopDoc("HZ", [hazop_entry])]
        hara_entry = HaraEntry(
            malfunction="M", hazard="H", scenario="Pedestrians crossing", severity=1,
            sev_rationale="", controllability=1, cont_rationale="", exposure=1,
            exp_rationale="", asil="QM", safety_goal="PG1"
        )
        app.hara_docs = [HaraDoc("RA", [], [hara_entry])]
        node = FaultTreeNode("PG1", "TOP EVENT")
        node.safety_goal_description = "PG1"
        node.validation_target = 0.5
        node.validation_desc = "desc"
        node.acceptance_criteria = "criteria"
        app.top_events = [node]
        goals = app.get_validation_targets_for_odd("Intersection")
        self.assertEqual(goals, [node])


if __name__ == "__main__":
    unittest.main()
