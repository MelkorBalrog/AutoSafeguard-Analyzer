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

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AutoML import AutoMLApp
from analysis.safety_management import SafetyManagementToolbox
from mainappsrc.core.reporting_export import Reporting_Export
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def _minimal_app():
    """Return a barebones ``AutoMLApp`` suitable for export tests."""

    app = AutoMLApp.__new__(AutoMLApp)
    app.top_events = []
    app.root_node = None
    dummy_sa = types.SimpleNamespace(fmeas=[], fmedas=[])
    app.safety_analysis = dummy_sa
    app.fmea_entries = []
    app.fmeas = []
    app.fmedas = []
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
    app.review_data = types.SimpleNamespace(name=None)
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
    app.safety_mgmt_toolbox = SafetyManagementToolbox()
    app.tool_listboxes = {}
    app.work_product_menus = {}
    app.tool_actions = {}
    app.enabled_work_products = set()
    app.enable_process_area = lambda area: None
    app.refresh_tool_enablement = lambda: None
    return app


def test_export_uses_sysml_repository_key():
    """Exported model data includes the expected SysML repository key."""
    SysMLRepository._instance = None
    SysMLRepository.get_instance()

    app = _minimal_app()
    app.current_user = ""
    app.reliability_components = []
    app.reliability_total_fit = 0.0
    app.spfm = 0.0
    app.lpfm = 0.0
    app.reliability_dc = 0.0
    app.item_definition = {}
    app.safety_concept = {}
    app.fmeda_components = []
    app.selected_mechanism_libraries = []
    app.arch_diagrams = []
    app.management_diagrams = []
    app.gsn_modules = []
    app.gsn_diagrams = []
    app.odd_elements = []
    app.fmea_service = types.SimpleNamespace(
        get_settings_dict=lambda: {}, load_fmeas=lambda data: None
    )
    app.probability_reliability = types.SimpleNamespace(
        update_probability_tables=lambda *args, **kwargs: None
    )
    app.governance_manager = types.SimpleNamespace(
        attach_toolbox=lambda tb: None,
        set_active_module=lambda m: None,
        freeze_governance_diagrams=lambda f: None,
    )
    app._refresh_phase_requirements_menu = lambda: None
    app.requirements_manager = types.SimpleNamespace(export_state=lambda: {})
    app.reporting_export = Reporting_Export(app)

    data = app.export_model_data(include_versions=False)
    assert "sysml_repository" in data
