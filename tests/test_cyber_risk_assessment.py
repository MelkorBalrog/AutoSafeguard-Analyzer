import unittest

from analysis.models import (
    CyberRiskEntry,
    HaraDoc,
    HaraEntry,
    CybersecurityGoal,
)
from AutoML import FaultTreeApp


class CyberRiskEntryTests(unittest.TestCase):
    def test_computations(self):
        entry = CyberRiskEntry(
            damage_scenario="Damage",
            threat_scenario="Threat",
            attack_vector="Network",
            feasibility="Medium",
            financial_impact="Moderate",
            safety_impact="Major",
            operational_impact="Negligible",
            privacy_impact="Moderate",
        )
        # Highest impact among inputs should be Major
        self.assertEqual(entry.overall_impact, "Major")
        # Medium feasibility with Major impact yields Medium risk
        self.assertEqual(entry.risk_level, "Medium")
        # Network attack vector with Major impact yields CAL3
        self.assertEqual(entry.cal, "CAL3")

    def test_sync_to_goals(self):
        app = FaultTreeApp.__new__(FaultTreeApp)
        cyber = CyberRiskEntry(
            damage_scenario="D",
            threat_scenario="T",
            attack_vector="Network",
            feasibility="High",
            financial_impact="Negligible",
            safety_impact="Moderate",
            operational_impact="Major",
            privacy_impact="Severe",
            cybersecurity_goal="CG1",
        )
        cyber.attack_paths = [{"path": "p1", "vector": "Network", "feasibility": "High"}]
        entry = HaraEntry("T", "", "", 1, "", 1, "", 1, "", "QM", "", cyber)
        doc = HaraDoc("RA1", [], [entry])
        app.hara_docs = [doc]
        app.cybersecurity_goals = [CybersecurityGoal("CG1", "desc"), CybersecurityGoal("CG2", "d2")]
        FaultTreeApp.sync_cyber_risk_to_goals(app)
        self.assertEqual(app.cybersecurity_goals[0].risk_assessments[0]["name"], "RA1")
        self.assertEqual(app.cybersecurity_goals[0].cal, cyber.cal)

    def test_get_cyber_goal_cal(self):
        app = FaultTreeApp.__new__(FaultTreeApp)
        cyber1 = CyberRiskEntry(
            damage_scenario="D1",
            threat_scenario="T1",
            attack_vector="Network",
            feasibility="High",
            financial_impact="Major",
            safety_impact="Negligible",
            operational_impact="Negligible",
            privacy_impact="Negligible",
            cybersecurity_goal="CG",
        )
        entry1 = HaraEntry("M1", "", "", 1, "", 1, "", 1, "", "QM", "", cyber1)
        cyber2 = CyberRiskEntry(
            damage_scenario="D2",
            threat_scenario="T2",
            attack_vector="Physical",
            feasibility="Low",
            financial_impact="Negligible",
            safety_impact="Negligible",
            operational_impact="Negligible",
            privacy_impact="Negligible",
            cybersecurity_goal="CG",
        )
        entry2 = HaraEntry("M2", "", "", 1, "", 1, "", 1, "", "QM", "", cyber2)
        doc = HaraDoc("RA", [], [entry1, entry2])
        app.hara_docs = [doc]
        self.assertEqual(app.get_cyber_goal_cal("CG"), cyber1.cal)

if __name__ == "__main__":
    unittest.main()
