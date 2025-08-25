"""Data access helper queries for :class:`AutoMLApp`.

This module centralises database and model lookup helpers that were
previously methods on ``AutoMLApp``.  Separating them keeps the main
application class focused on orchestration and UI responsibilities while
these functions provide read-only views over the underlying model.
"""
from __future__ import annotations

from typing import List

from gui.windows.architecture import parse_behaviors
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


class DataAccess_Queries:
    """Collection of query helpers used by :class:`AutoMLApp`."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # ------------------------------------------------------------------
    # Delegated lookups from analysis applications
    # ------------------------------------------------------------------
    def get_top_level_nodes(self):
        return self.app.fta_app.get_top_level_nodes(self.app)

    def get_all_nodes_no_filter(self, node):
        return self.app.fta_app.get_all_nodes_no_filter(self.app, node)

    def get_all_nodes_table(self, root_node):
        return self.app.fta_app.get_all_nodes_table(self.app, root_node)

    def get_all_nodes_in_model(self):
        return self.app.fta_app.get_all_nodes_in_model(self.app)

    def get_all_basic_events(self):
        return self.app.fta_app.get_all_basic_events(self.app)

    def get_all_gates(self):
        return self.app.fta_app.get_all_gates(self.app)

    def get_extra_recommendations_list(self, description, level):
        return self.app.fta_app.get_extra_recommendations_list(
            self.app, description, level
        )

    def get_extra_recommendations_from_level(self, description, level):
        return self.app.fta_app.get_extra_recommendations_from_level(
            self.app, description, level
        )

    def get_recommendation_from_description(self, description, level):
        return self.app.fta_app.get_recommendation_from_description(
            self.app, description, level
        )

    def get_top_event_safety_goals(self, node):
        return self.app.risk_app.get_top_event_safety_goals(self.app, node)

    def get_cyber_goal_cal(self, goal_id):
        return self.app.risk_app.get_cyber_goal_cal(self.app, goal_id)

    # ------------------------------------------------------------------
    # Basic traversals and lookups
    # ------------------------------------------------------------------
    def get_page_nodes(self, node):
        result = []
        if getattr(node, "is_page", False) and node != self.app.root_node:
            result.append(node)
        for child in getattr(node, "children", []):
            result.extend(self.get_page_nodes(child))
        return result

    def get_all_triggering_conditions(self):
        nodes = [
            n
            for n in self.get_all_nodes_in_model()
            if n.node_type.upper() == "TRIGGERING CONDITION"
        ]
        nodes.extend(self.app.triggering_condition_nodes)
        unique = {n.unique_id: n for n in nodes}
        return list(unique.values())

    def get_all_functional_insufficiencies(self):
        nodes = [
            n
            for n in self.get_all_nodes_in_model()
            if n.node_type.upper() == "FUNCTIONAL INSUFFICIENCY"
            or (getattr(n, "input_subtype", "") or "").lower()
            == "functional insufficiency"
        ]
        nodes.extend(self.app.functional_insufficiency_nodes)
        unique = {n.unique_id: n for n in nodes}
        return list(unique.values())

    def get_all_scenario_names(self):
        names: List[str] = []
        for lib in self.app.scenario_libraries:
            for sc in lib.get("scenarios", []):
                if isinstance(sc, dict):
                    name = sc.get("name", "")
                else:
                    name = sc
                if name:
                    names.append(name)
        return names

    def get_scenario_exposure(self, name: str) -> int:
        name = (name or "").strip()
        for lib in self.app.scenario_libraries:
            for sc in lib.get("scenarios", []):
                if isinstance(sc, dict):
                    sc_name = (sc.get("name", "") or "").strip()
                    if sc_name == name:
                        try:
                            return int(sc.get("exposure", 1))
                        except (TypeError, ValueError):
                            return 1
                else:
                    if str(sc).strip() == name:
                        return 1
        return 1

    def get_all_scenery_names(self):
        names = []
        for lib in self.app.odd_libraries:
            for el in lib.get("elements", []):
                if isinstance(el, dict):
                    name = el.get("name") or el.get("element") or el.get("id")
                else:
                    name = str(el)
                if name:
                    names.append(name)
        return names

    def get_all_function_names(self):
        names = set()
        for doc in getattr(self.app, "hazop_docs", []):
            for e in doc.entries:
                if getattr(e, "function", ""):
                    names.add(e.function)
        return sorted(names)

    def get_all_action_names(self):
        repo = SysMLRepository.get_instance()
        return repo.get_activity_actions()

    def get_all_action_labels(self) -> list[str]:
        repo = SysMLRepository.get_instance()
        diag_block: dict[str, str] = {}

        for diag in repo.visible_diagrams().values():
            if diag.diag_type != "Internal Block Diagram":
                continue
            blk_id = getattr(diag, "father", None) or next(
                (eid for eid, did in repo.element_diagrams.items() if did == diag.diag_id),
                None,
            )
            if blk_id and blk_id in repo.elements:
                diag_block[diag.diag_id] = repo.elements[blk_id].name or blk_id

        for elem in repo.elements.values():
            if elem.elem_type != "Block":
                continue
            for beh in parse_behaviors(elem.properties.get("behaviors", "")):
                if repo.diagram_visible(beh.diagram) and beh.diagram not in diag_block:
                    diag_block[beh.diagram] = elem.name or elem.elem_id

        labels: set[str] = set()
        for diag in repo.visible_diagrams().values():
            if diag.diag_type != "Activity Diagram":
                continue
            blk = diag_block.get(diag.diag_id, "")
            name = diag.name or diag.diag_id
            labels.add(f"{name} : {blk}" if blk else name)
            for obj in getattr(diag, "objects", []):
                typ = obj.get("obj_type") or obj.get("type")
                if typ not in ("Action Usage", "Action", "CallBehaviorAction"):
                    continue
                action_name = obj.get("properties", {}).get("name", "")
                elem_id = obj.get("element_id")
                if not action_name and elem_id and elem_id in repo.elements:
                    action_name = repo.elements[elem_id].name
                if not action_name:
                    continue
                view_id = None
                if elem_id and elem_id in repo.elements:
                    view_id = repo.elements[elem_id].properties.get("view")
                if not view_id:
                    view_id = obj.get("properties", {}).get("view")
                blk_name = diag_block.get(view_id, "")
                if not blk_name and elem_id:
                    linked = repo.get_linked_diagram(elem_id)
                    blk_name = diag_block.get(linked, "")
                labels.add(f"{action_name} : {blk_name}" if blk_name else action_name)

        return sorted(labels)

    def get_use_case_for_function(self, func: str) -> str:
        repo = SysMLRepository.get_instance()
        for diag in repo.visible_diagrams().values():
            if diag.diag_type != "Activity Diagram":
                continue
            if diag.name == func:
                return diag.name
            for obj in diag.objects:
                name = obj.get("properties", {}).get("name", "")
                if not name:
                    elem_id = obj.get("element_id")
                    if elem_id and elem_id in repo.elements:
                        name = repo.elements[elem_id].name
                if name == func:
                    return diag.name
            for elem_id in getattr(diag, "elements", []):
                elem = repo.elements.get(elem_id)
                if elem and elem.name == func:
                    return diag.name
        return ""

    def get_all_component_names(self):
        names = set()
        for doc in getattr(self.app, "hazop_docs", []):
            names.update(
                e.component for e in doc.entries if getattr(e, "component", "")
            )
        names.update(c.name for c in self.app.reliability_components)
        names.update(self.get_all_part_names())
        for be in self.get_all_basic_events():
            comp = self.get_component_name_for_node(be)
            if comp:
                names.add(comp)
        for entry in self.app.fmea_entries:
            comp = getattr(entry, "fmea_component", "")
            if comp:
                names.add(comp)
        for doc in self.app.fmeas:
            for e in doc.get("entries", []):
                comp = getattr(e, "fmea_component", "")
                if comp:
                    names.add(comp)
        for doc in self.app.fmedas:
            for e in doc.get("entries", []):
                comp = getattr(e, "fmea_component", "")
                if comp:
                    names.add(comp)
        return sorted(n for n in names if n)

    def get_all_part_names(self) -> list[str]:
        repo = SysMLRepository.get_instance()
        names = set()
        for diag in repo.visible_diagrams().values():
            if diag.diag_type != "Internal Block Diagram":
                continue
            for obj in getattr(diag, "objects", []):
                if obj.get("obj_type") != "Part":
                    continue
                comp = obj.get("properties", {}).get("component", "")
                if not comp:
                    eid = obj.get("element_id")
                    if eid and eid in repo.elements:
                        comp = repo.elements[eid].properties.get("component", "")
                if comp:
                    names.add(comp)
        return sorted(names)

    def get_all_malfunction_names(self):
        names = set()
        for doc in getattr(self.app, "hazop_docs", []):
            names.update(
                e.malfunction for e in doc.entries if getattr(e, "malfunction", "")
            )
        return sorted(names)

    def get_entry_field(self, entry, field, default=""):
        if isinstance(entry, dict):
            return entry.get(field, default)
        return getattr(entry, field, default)

    def get_all_failure_modes(self):
        modes = list(self.get_all_basic_events())
        for doc in self.app.fmea_entries:
            modes.append(doc)
        for f in self.app.fmeas:
            modes.extend(f.get("entries", []))
        for d in self.app.fmedas:
            modes.extend(d.get("entries", []))
        unique = {}
        for m in modes:
            unique[getattr(m, "unique_id", id(m))] = m
        return list(unique.values())

    def get_all_fmea_entries(self):
        entries = list(self.app.fmea_entries)
        for f in self.app.fmeas:
            entries.extend(f.get("entries", []))
        for d in self.app.fmedas:
            entries.extend(d.get("entries", []))
        return entries

    def get_non_basic_failure_modes(self):
        from .automl_core import GATE_NODE_TYPES  # local import avoids circular

        modes = [
            g
            for g in self.get_all_gates()
            if (
                g.node_type.upper() != "TOP EVENT"
                and not g.is_page
                and not any(p.is_page for p in getattr(g, "parents", []))
                and getattr(g, "description", "").strip()
            )
        ]
        for entry in self.app.fmea_entries:
            if getattr(entry, "description", "").strip():
                modes.append(entry)
        for f in self.app.fmeas:
            modes.extend(
                [e for e in f.get("entries", []) if getattr(e, "description", "").strip()]
            )
        for d in self.app.fmedas:
            modes.extend(
                [e for e in d.get("entries", []) if getattr(e, "description", "").strip()]
            )
        unique = {getattr(m, "unique_id", id(m)): m for m in modes}
        return list(unique.values())

    def get_failure_mode_node(self, node):
        ref = getattr(node, "failure_mode_ref", None)
        if ref:
            n = self.app.find_node_by_id_all(ref)
            if n:
                return n
        return node

    def get_component_name_for_node(self, node):
        from .automl_core import GATE_NODE_TYPES  # local import avoids circular

        src = self.get_failure_mode_node(node)
        parent = src.parents[0] if src.parents else None
        if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES:
            if getattr(parent, "user_name", ""):
                return parent.user_name
        return getattr(src, "fmea_component", "")

    def format_failure_mode_label(self, node):
        comp = self.get_component_name_for_node(node)
        label = (
            node.description
            if node.description
            else (node.user_name or f"Node {node.unique_id}")
        )
        return f"{comp}: {label}" if comp else label

    def get_failure_modes_for_malfunction(self, malfunction: str) -> list[str]:
        result = []
        for be in self.get_all_basic_events():
            mals = [
                m.strip()
                for m in getattr(be, "fmeda_malfunction", "").split(";")
                if m.strip()
            ]
            if malfunction in mals:
                result.append(self.format_failure_mode_label(be))
        return result

    def get_all_nodes(self, node=None):
        if node is None:
            result = []
            for te in self.app.top_events:
                result.extend(self.get_all_nodes(te))
            return result

        visited = set()

        def rec(n):
            if n.unique_id in visited:
                return []
            visited.add(n.unique_id)
            if n != self.app.root_node and any(parent.is_page for parent in n.parents):
                return []
            result = [n]
            for c in getattr(n, "children", []):
                result.extend(rec(c))
            return result

        return rec(node)

    def get_current_user_role(self):
        return self.app.user_manager.get_current_user_role()
