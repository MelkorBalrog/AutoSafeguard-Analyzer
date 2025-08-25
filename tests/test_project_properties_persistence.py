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

import os
import sys
import types

# Stub out PIL modules to avoid dependency
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AutoML import AutoMLApp
from analysis.utils import (
    CONTROLLABILITY_PROBABILITIES,
    EXPOSURE_PROBABILITIES,
    SEVERITY_PROBABILITIES,
    update_probability_tables,
)


def _minimal_app():
    app = AutoMLApp.__new__(AutoMLApp)
    app.top_events = []
    app.safety_analysis = types.SimpleNamespace(
        fmeas=[], fmedas=[], _load_fault_tree_events=lambda *a, **k: None
    )
    app.fmeas = []
    app.fmedas = []
    app.fmea_entries = []
    app.fmeda_entries = []
    app.mechanism_libraries = []
    app.selected_mechanism_libraries = []
    app.mission_profiles = []
    app.reliability_analyses = []
    app.hazop_docs = []
    app.hara_docs = []
    app.stpa_docs = []
    app.threat_docs = []
    app.fi2tc_docs = []
    app.tc2fi_docs = []
    app.hazop_entries = []
    app.fi2tc_entries = []
    app.tc2fi_entries = []
    app.scenario_libraries = []
    app.odd_libraries = []
    app.faults = []
    app.malfunctions = []
    app.hazards = []
    app.failures = []
    app.project_properties = {}
    app.reviews = []
    app.review_data = None
    app.versions = {}
    app.safety_analysis = types.SimpleNamespace(fmeas=[], fmedas=[])
    app.update_odd_elements = lambda: None
    app.update_failure_list = lambda: None
    app.load_default_mechanisms = lambda: None
    app.update_hazard_list = lambda: None
    app.update_hara_statuses = lambda: None
    app.update_fta_statuses = lambda: None
    app.get_all_basic_events = lambda: []
    app.get_all_nodes = lambda te: []
    app.get_all_fmea_entries = lambda: []
    app.update_global_requirements_from_nodes = lambda *args, **kwargs: None
    app.sync_hara_to_safety_goals = lambda: None
    app.close_page_diagram = lambda: None
    app.update_views = lambda: None
    app.reporting_export = types.SimpleNamespace(
        export_model_data=lambda include_versions=True: {}
    )
    app.probability_reliability = types.SimpleNamespace(
        update_probability_tables=lambda *a, **k: None
    )
    return app


def test_project_properties_probabilities_roundtrip():
    exp_default = EXPOSURE_PROBABILITIES.copy()
    ctrl_default = CONTROLLABILITY_PROBABILITIES.copy()
    sev_default = SEVERITY_PROBABILITIES.copy()

    app = _minimal_app()
    app.project_properties = {
        "exposure_probabilities": {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.4},
        "controllability_probabilities": {1: 0.5, 2: 0.6, 3: 0.7},
        "severity_probabilities": {1: 0.8, 2: 0.9, 3: 1.0},
    }
    data = app.export_model_data(include_versions=False)
    new_app = _minimal_app()
    new_app.apply_model_data(data, ensure_root=False)
    try:
        assert new_app.project_properties["exposure_probabilities"][1] == 0.1
        assert new_app.project_properties["controllability_probabilities"][2] == 0.6
        assert new_app.project_properties["severity_probabilities"][3] == 1.0
        assert set(new_app.project_properties["exposure_probabilities"].keys()) == {1, 2, 3, 4}
    finally:
        update_probability_tables(exp_default, ctrl_default, sev_default)
