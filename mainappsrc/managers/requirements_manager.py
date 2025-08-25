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

from __future__ import annotations

"""Requirement management utilities for AutoML."""

import json
from typing import Dict, Any, Set

try:  # pragma: no cover - optional dependency
    from mainappsrc.models.sysml.sysml_repository import SysMLRepository
except Exception:  # pragma: no cover
    SysMLRepository = None  # type: ignore


class RequirementsManagerSubApp:
    """Encapsulate requirement traceability helpers."""

    def __init__(self, app: Any) -> None:
        self.app = app

    # ------------------------------------------------------------------
    def export_state(self) -> Dict[str, Any]:
        """Serialize requirement editor state for project export.

        The requirements manager currently stores no mutable state beyond what
        is held in the main application model. The export therefore returns an
        empty mapping, acting as a placeholder for future requirement editor
        data.
        """
        return {}

    # ------------------------------------------------------------------
    def get_requirement_allocation_names(self, req_id: str) -> list[str]:
        """Return names of model elements linked to ``req_id``."""
        names: list[str] = []
        repo = SysMLRepository.get_instance() if SysMLRepository else None
        if repo:
            for diag_id, obj_id in repo.find_requirements(req_id):
                diag = repo.diagrams.get(diag_id)
                obj = next((o for o in getattr(diag, "objects", []) if o.get("obj_id") == obj_id), None)
                dname = diag.name if diag else ""
                oname = obj.get("properties", {}).get("name", "") if obj else ""
                if dname and oname:
                    names.append(f"{dname}:{oname}")
                elif dname or oname:
                    names.append(dname or oname)
            for diag in repo.diagrams.values():
                for obj in getattr(diag, "objects", []):
                    reqs = obj.get("requirements", [])
                    if any(r.get("id") == req_id for r in reqs):
                        name = obj.get("properties", {}).get("name") or obj.get("obj_type", "")
                        names.append(name)
        for n in self.app.get_all_nodes(self.app.root_node):
            reqs = getattr(n, "safety_requirements", [])
            if any((r.get("id") if isinstance(r, dict) else getattr(r, "id", None)) == req_id for r in reqs):
                names.append(n.user_name or f"Node {n.unique_id}")
        for fmea in self.app.fmeas:
            for e in fmea.get("entries", []):
                reqs = e.get("safety_requirements", []) if isinstance(e, dict) else getattr(e, "safety_requirements", [])
                if any((r.get("id") if isinstance(r, dict) else getattr(r, "id", None)) == req_id for r in reqs):
                    if isinstance(e, dict):
                        name = e.get("description") or e.get("user_name", f"BE {e.get('unique_id','')}")
                    else:
                        name = getattr(e, "description", "") or getattr(e, "user_name", f"BE {getattr(e, 'unique_id', '')}")
                    names.append(f"{fmea['name']}:{name}")
        return names

    # ------------------------------------------------------------------
    def _collect_goal_names(self, node: Any, acc: Set[str]) -> None:
        if node.node_type.upper() == "TOP EVENT":
            acc.add(node.safety_goal_description or (node.user_name or f"SG {node.unique_id}"))
        for p in getattr(node, "parents", []):
            self._collect_goal_names(p, acc)

    def get_requirement_goal_names(self, req_id: str) -> list[str]:
        """Return a list of safety goal names linked to ``req_id``."""
        goals: Set[str] = set()
        for n in self.app.get_all_nodes(self.app.root_node):
            reqs = getattr(n, "safety_requirements", [])
            if any((r.get("id") if isinstance(r, dict) else getattr(r, "id", None)) == req_id for r in reqs):
                self._collect_goal_names(n, goals)
        for fmea in self.app.fmeas:
            for e in fmea.get("entries", []):
                reqs = e.get("safety_requirements", []) if isinstance(e, dict) else getattr(e, "safety_requirements", [])
                if any((r.get("id") if isinstance(r, dict) else getattr(r, "id", None)) == req_id for r in reqs):
                    parent_list = e.get("parents") if isinstance(e, dict) else getattr(e, "parents", None)
                    parent = parent_list[0] if parent_list else None
                    if isinstance(parent, dict) and "unique_id" in parent:
                        node = self.app.find_node_by_id_all(parent["unique_id"])
                    else:
                        node = parent if hasattr(parent, "unique_id") else None
                    if node:
                        self._collect_goal_names(node, goals)
        return sorted(goals)

    # ------------------------------------------------------------------
    def format_requirement_with_trace(self, req: Dict[str, Any]) -> str:
        from .AutoML import format_requirement  # local import to avoid circular
        rid = req.get("id", "")
        alloc = ", ".join(self.get_requirement_allocation_names(rid))
        goals = ", ".join(self.get_requirement_goal_names(rid))
        base = format_requirement(req)
        return f"{base} (Alloc: {alloc}; SGs: {goals})"

    # ------------------------------------------------------------------
    def collect_reqs(self, node_dict: Dict[str, Any], target: Dict[str, Any]) -> None:
        for r in node_dict.get("safety_requirements", []):
            rid = r.get("id")
            if rid and rid not in target:
                target[rid] = r
        for ch in node_dict.get("children", []):
            self.collect_reqs(ch, target)

    # ------------------------------------------------------------------
    def build_requirement_diff_html(self, review: Any) -> str:
        if not self.app.versions:
            return ""
        base_data = self.app.versions[-1]["data"]
        current = self.app.export_model_data(include_versions=False)

        def filter_data(data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "top_events": [t for t in data.get("top_events", []) if t["unique_id"] in review.fta_ids],
                "fmeas": [f for f in data.get("fmeas", []) if f["name"] in review.fmea_names],
                "fmedas": [d for d in data.get("fmedas", []) if d.get("name") in getattr(review, "fmeda_names", [])],
            }

        data1 = filter_data(base_data)
        data2 = filter_data(current)
        map1 = self.app.node_map_from_data(data1["top_events"])
        map2 = self.app.node_map_from_data(data2["top_events"])

        reqs1: Dict[str, Any] = {}
        reqs2: Dict[str, Any] = {}
        for nid in review.fta_ids:
            if nid in map1:
                self.collect_reqs(map1[nid], reqs1)
            if nid in map2:
                self.collect_reqs(map2[nid], reqs2)

        fmea1 = {f["name"]: f for f in data1.get("fmeas", [])}
        fmea2 = {f["name"]: f for f in data2.get("fmeas", [])}
        for name in review.fmea_names:
            for e in fmea1.get(name, {}).get("entries", []):
                for r in e.get("safety_requirements", []):
                    rid = r.get("id")
                    if rid and rid not in reqs1:
                        reqs1[rid] = r
            for e in fmea2.get(name, {}).get("entries", []):
                for r in e.get("safety_requirements", []):
                    rid = r.get("id")
                    if rid and rid not in reqs2:
                        reqs2[rid] = r
        for f in data1.get("fmedas", []):
            for e in f.get("entries", []):
                for r in e.get("safety_requirements", []):
                    rid = r.get("id")
                    if rid and rid not in reqs1:
                        reqs1[rid] = r
        for f in data2.get("fmedas", []):
            for e in f.get("entries", []):
                for r in e.get("safety_requirements", []):
                    rid = r.get("id")
                    if rid and rid not in reqs2:
                        reqs2[rid] = r

        import difflib, html

        def html_diff(a: str, b: str) -> str:
            matcher = difflib.SequenceMatcher(None, a, b)
            parts: list[str] = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    parts.append(html.escape(a[i1:i2]))
                elif tag == "delete":
                    parts.append(f"<span style='color:red'>{html.escape(a[i1:i2])}</span>")
                elif tag == "insert":
                    parts.append(f"<span style='color:blue'>{html.escape(b[j1:j2])}</span>")
                elif tag == "replace":
                    parts.append(f"<span style='color:red'>{html.escape(a[i1:i2])}</span>")
                    parts.append(f"<span style='color:blue'>{html.escape(b[j1:j2])}</span>")
            return "".join(parts)

        lines: list[str] = []
        all_ids = sorted(set(reqs1) | set(reqs2))
        for rid in all_ids:
            r1 = reqs1.get(rid)
            r2 = reqs2.get(rid)
            if r1 and not r2:
                lines.append(f"Removed: {html.escape(self.format_requirement_with_trace(r1))}")
            elif r2 and not r1:
                lines.append(f"Added: {html.escape(self.format_requirement_with_trace(r2))}")
            elif json.dumps(r1, sort_keys=True) != json.dumps(r2, sort_keys=True):
                lines.append("Updated: " + html_diff(self.format_requirement_with_trace(r1), self.format_requirement_with_trace(r2)))

        for nid in review.fta_ids:
            n1 = map1.get(nid, {})
            n2 = map2.get(nid, {})
            sg_old = f"{n1.get('safety_goal_description','')} [{n1.get('safety_goal_asil','')}]"
            sg_new = f"{n2.get('safety_goal_description','')} [{n2.get('safety_goal_asil','')}]"
            label = n2.get('user_name') or n1.get('user_name') or f"Node {nid}"
            if sg_old != sg_new:
                lines.append(f"Safety Goal for {html.escape(label)}: " + html_diff(sg_old, sg_new))
            if n1.get('safe_state','') != n2.get('safe_state',''):
                lines.append(f"Safe State for {html.escape(label)}: " + html_diff(n1.get('safe_state',''), n2.get('safe_state','')))
        return "<br>".join(lines)
