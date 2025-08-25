# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import asdict
from AutoML import AutoMLApp
from analysis.models import HaraEntry, CyberRiskEntry

def test_cyber_risk_entry_persistence():
    cyber = CyberRiskEntry(
        damage_scenario="D",
        threat_scenario="T",
        attack_vector="Network",
        feasibility="High",
        financial_impact="Major",
        safety_impact="Moderate",
        operational_impact="Negligible",
        privacy_impact="Moderate",
        cybersecurity_goal="CG1",
    )
    cyber.attack_paths = [{"path": "p1", "vector": "Network", "feasibility": "High"}]
    entry = HaraEntry("M", "H", "S", 1, "", 1, "", 1, "", "QM", "SG", cyber)
    data = {
        "haras": [
            {
                "name": "RA",
                "hazops": [],
                "entries": [asdict(entry)],
                "approved": False,
                "status": "draft",
                "stpa": "",
                "threat": "",
            }
        ]
    }
    app = AutoMLApp.__new__(AutoMLApp)
    app.top_events = []
    app.fmea_entries = []
    app.fmeas = []
    app.fmedas = []
    app.mechanism_libraries = []
    app.selected_mechanism_libraries = []
    app.mission_profiles = []
    app.reliability_analyses = []
    app.faults = []
    app.malfunctions = []
    app.hazards = []
    app.hazard_severity = {}
    app.failures = []
    app.triggering_conditions = []
    app.functional_insufficiencies = []
    app.hazop_docs = []
    app.hara_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.cybersecurity_goals = []
    app.reviews = []
    app.project_properties = {}
    app.apply_model_data(data)
    loaded = app.hara_docs[0].entries[0].cyber
    assert loaded.damage_scenario == "D"
    assert loaded.attack_paths == [{"path": "p1", "vector": "Network", "feasibility": "High"}]
    assert loaded.cybersecurity_goal == "CG1"
