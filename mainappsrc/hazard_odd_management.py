from __future__ import annotations

"""Encapsulate hazard and ODD management helpers for :class:`AutoMLApp`.

This thin wrapper groups together routines dealing with hazards and
operational design domains (ODD).  The heavy lifting remains implemented on
``AutoMLApp`` or in the risk assessment sub-application; the methods here
simply delegate to those implementations.  Centralising the entry points
makes future refactoring or replacement straightforward.
"""

from typing import List, Tuple


class Hazard_ODD_Management:
    """Provide facade methods for hazard and ODD management."""

    # Risk assessment integration -------------------------------------------------
    def add_hazard(self, app, name: str, severity: int | str = 1) -> None:
        return app.risk_app.add_hazard(app, name, severity)

    def add_malfunction(self, app, name: str) -> None:
        return app.risk_app.add_malfunction(app, name)

    def add_functional_insufficiency(self, app, name: str) -> None:
        return app.risk_app.add_functional_insufficiency(app, name)

    def delete_functional_insufficiency(self, app, name: str) -> None:
        return app.risk_app.delete_functional_insufficiency(app, name)

    def add_triggering_condition(self, app, name: str) -> None:
        return app.risk_app.add_triggering_condition(app, name)

    def delete_triggering_condition(self, app, name: str) -> None:
        return app.risk_app.delete_triggering_condition(app, name)

    def edit_severity(self, app) -> None:
        return app._edit_severity()

    def get_hazards_for_malfunction(self, app, malfunction: str, hazop_names=None) -> List[str]:
        return app._get_hazards_for_malfunction(malfunction, hazop_names)

    def get_hara_by_name(self, app, name):
        return app.risk_app.get_hara_by_name(app, name)

    def get_hazop_by_name(self, app, name):
        return app.risk_app.get_hazop_by_name(app, name)

    def get_safety_goal_asil(self, app, sg_name):
        return app.risk_app.get_safety_goal_asil(app, sg_name)

    def get_hara_goal_asil(self, app, sg_name):
        return app.risk_app.get_hara_goal_asil(app, sg_name)

    def sync_hara_to_safety_goals(self, app) -> None:
        return app.risk_app.sync_hara_to_safety_goals(app)

    def show_hazard_editor(self, app) -> None:
        return app.risk_app.show_hazard_editor(app)

    def show_hazard_explorer(self, app) -> None:
        return app.risk_app.show_hazard_explorer(app)

    def show_hazard_list(self, app) -> None:
        return app.risk_app.show_hazard_list(app)

    def show_malfunction_editor(self, app) -> None:
        return app._show_malfunction_editor()

    def show_malfunctions_editor(self, app) -> None:
        return app._show_malfunctions_editor()

    def show_functional_insufficiency_list(self, app) -> None:
        return app._show_functional_insufficiency_list()

    def update_hazard_list(self, app) -> None:
        return app._update_hazard_list()

    def update_hazard_severity(self, app, hazard: str, severity: int | str) -> None:
        return app.risk_app.update_hazard_severity(app, hazard, severity)

    def is_malfunction_used(self, app, name: str) -> bool:
        return app._is_malfunction_used(name)

    def create_top_event_for_malfunction(self, app, name: str) -> None:
        return app._create_top_event_for_malfunction(name)

    # ODD management --------------------------------------------------------------
    def manage_scenario_libraries(self, app) -> None:
        return app._manage_scenario_libraries()

    def manage_mission_profiles(self, app) -> None:
        return app._manage_mission_profiles()

    def manage_odd_libraries(self, app) -> None:
        return app._manage_odd_libraries()

    def update_odd_elements(self, app) -> None:
        return app._update_odd_elements()

    def get_validation_targets_for_odd(self, app, element_name):
        return app._get_validation_targets_for_odd(element_name)

    def on_lifecycle_selected(self, app, _event=None) -> None:
        return app._on_lifecycle_selected(_event)

    def get_spi_targets(self, app) -> List[str]:
        return app._get_spi_targets()

    def _parse_spi_target(self, app, target: str) -> Tuple[str, str]:
        return app._parse_spi_target_impl(target)

    def refresh_safety_performance_indicators(self, app) -> None:
        return app._refresh_safety_performance_indicators()

    def show_safety_performance_indicators(self, app) -> None:
        return app._show_safety_performance_indicators()
