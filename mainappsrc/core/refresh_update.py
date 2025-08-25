"""Model and view refresh helpers extracted from AutoML core."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from analysis.constants import CHECK_MARK
from analysis.requirement_rule_generator import regenerate_requirement_patterns
from analysis.safety_management import SafetyManagementToolbox
from config.automl_constants import PMHF_TARGETS
from gui.styles.style_manager import StyleManager
from mainappsrc.managers.sotif_manager import SOTIFManager
from mainappsrc.models.sysml.sysml_repository import SysMLRepository

if TYPE_CHECKING:  # pragma: no cover - circular import guard
    from .automl_core import AutoMLApp


class Refresh_Update:
    """Collection of model and UI refresh helpers."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    def __getattr__(self, name):  # pragma: no cover - simple delegation
        return getattr(self.app, name)

    # ------------------------------------------------------------------
    # Methods migrated from ``AutoMLApp``
    # ------------------------------------------------------------------
    def refresh_all(self):
        """Synchronize model elements and refresh all open views."""
        # Update the main explorer and propagate model changes
        self.update_views()
        # Regenerate requirement patterns for any model change
        regenerate_requirement_patterns()
        # Refresh GSN views separately via the manager
        self.gsn_manager.refresh()
        # Refresh any secondary windows that may be open
        for attr in dir(self.app):
            if attr.endswith("_window"):
                win = getattr(self.app, attr)
                if hasattr(win, "winfo_exists") and win.winfo_exists():
                    if hasattr(win, "refresh_docs"):
                        win.refresh_docs()
                    if hasattr(win, "refresh"):
                        win.refresh()

    def refresh_model(self):
        """Recalculate derived values across the entire model."""
        # Ensure safety-related data is consistent first
        self.ensure_asil_consistency()
        # Propagate FMEDA attributes to any linked basic events
        for fm in self.get_all_failure_modes():
            self.propagate_failure_mode_attributes(fm)

        def iter_analysis_events():
            for be in self.get_all_basic_events():
                yield be
            for e in self.fmea_entries:
                yield e
            for doc in self.fmeas:
                for e in doc.get("entries", []):
                    yield e
            for doc in self.fmedas:
                for e in doc.get("entries", []):
                    yield e

        for entry in iter_analysis_events():
            mals = [m.strip() for m in getattr(entry, "fmeda_malfunction", "").split(";") if m.strip()]
            goals = self.get_safety_goals_for_malfunctions(mals) or self.get_top_event_safety_goals(entry)
            if goals:
                sg = ", ".join(goals)
                entry.fmeda_safety_goal = sg
                first = goals[0]
                te = next((t for t in self.top_events if first in [t.user_name, t.safety_goal_description]), None)
                if te:
                    entry.fmeda_dc_target = getattr(te, "sg_dc_target", 0.0)
                    entry.fmeda_spfm_target = getattr(te, "sg_spfm_target", 0.0)
                    entry.fmeda_lpfm_target = getattr(te, "sg_lpfm_target", 0.0)

        # Recalculate probabilities for all basic events
        self.update_basic_event_probabilities()
        # Synchronize cybersecurity risk assessments with goal CAL values
        self.sync_cyber_risk_to_goals()

    def refresh_styles(self, event=None):
        """Redraw all open diagram windows using current styles."""
        if getattr(self, 'canvas', None):
            self.canvas.config(bg=StyleManager.get_instance().canvas_bg)
        for tab in getattr(self, 'diagram_tabs', {}).values():
            for child in tab.winfo_children():
                if hasattr(child, 'redraw'):
                    child.redraw()

    def refresh_tool_enablement(self) -> None:
        self.governance_manager.refresh_tool_enablement()

    def update_lifecycle_cb(self) -> None:
        self.governance_manager.update_lifecycle_cb()

    def update_hara_statuses(self):
        return self.risk_app.update_hara_statuses(self)

    def refresh_safety_performance_indicators(self):
        """Populate the SPI explorer table."""
        tree = getattr(self, "_spi_tree", None)
        if not tree or not getattr(tree, "winfo_exists", lambda: True)():
            return
        for iid in list(tree.get_children("")):
            tree.delete(iid)
        self._spi_lookup = {}

        manager = getattr(self, "sotif_manager", None)
        if manager is None:
            manager = SOTIFManager(self)
            self.sotif_manager = manager
        for sg, values in manager.iter_spi_rows():
            iid = tree.insert("", "end", values=values)
            self._spi_lookup[iid] = (sg, "SOTIF")

        for sg in getattr(self, "top_events", []):
            asil = getattr(sg, "safety_goal_asil", "")
            if asil in PMHF_TARGETS:
                target = PMHF_TARGETS[asil]
                v_str = f"{target:.2e}"
                fusa_prob = getattr(sg, "probability", "")
                p_str = f"{fusa_prob:.2e}" if fusa_prob not in ("", None) else ""
                spi_val = ""
                try:
                    if fusa_prob not in ("", None):
                        p_val = float(fusa_prob)
                        if target > 0 and p_val > 0:
                            spi_val = f"{math.log10(target / p_val):.2f}"
                except Exception:
                    spi_val = ""
                iid = tree.insert(
                    "",
                    "end",
                    values=[
                        sg.user_name or f"SG {sg.unique_id}",
                        v_str,
                        p_str,
                        spi_val,
                        "Target PMHF",
                        getattr(sg, "acceptance_criteria", ""),
                    ],
                )
                self._spi_lookup[iid] = (sg, "FUSA")

    def refresh_safety_case_table(self):
        """Populate the Safety & Security Case table with solution nodes."""
        tree = getattr(self, "_safety_case_tree", None)
        if not tree or not getattr(tree, "winfo_exists", lambda: True)():
            return
        for iid in list(tree.get_children("")):
            tree.delete(iid)
        self._solution_lookup = {}
        for diag in getattr(self, "all_gsn_diagrams", []):
            for node in getattr(diag, "nodes", []):
                if (
                    getattr(node, "node_type", "").lower() == "solution"
                    and getattr(node, "is_primary_instance", True)
                ):
                    self._solution_lookup[node.unique_id] = (node, diag)
                    prob = ""
                    v_target = ""
                    spi_val = ""
                    p_val = None
                    vt_val = None
                    target = getattr(node, "spi_target", "")
                    if target:
                        pg_name, spi_type = self._parse_spi_target(target)
                        te = None
                        for candidate in getattr(self, "top_events", []):
                            if self._product_goal_name(candidate) == pg_name:
                                te = candidate
                                break
                        if te:
                            if spi_type == "FUSA":
                                p = getattr(te, "probability", "")
                                vt = PMHF_TARGETS.get(getattr(te, "safety_goal_asil", ""), "")
                            else:
                                p = getattr(te, "spi_probability", "")
                                vt = getattr(te, "validation_target", "")
                            if p not in ("", None):
                                try:
                                    p_val = float(p)
                                    prob = f"{p_val:.2e}"
                                except Exception:
                                    prob = ""
                                    p_val = None
                            if vt not in ("", None):
                                try:
                                    vt_val = float(vt)
                                    v_target = f"{vt_val:.2e}"
                                except Exception:
                                    v_target = ""
                                    vt_val = None
                            try:
                                if vt_val not in (None, 0) and p_val not in (None, 0):
                                    spi_val = f"{math.log10(vt_val / p_val):.2f}"
                            except Exception:
                                spi_val = ""
                    tree.insert(
                        "",
                        "end",
                        values=[
                            node.user_name,
                            node.description,
                            node.work_product,
                            node.evidence_link,
                            v_target,
                            prob,
                            spi_val,
                            CHECK_MARK if getattr(node, "evidence_sufficient", False) else "",
                            getattr(node, "manager_notes", ""),
                        ],
                        tags=(node.unique_id,),
                    )

    def update_views(self):
        self.refresh_model()
        # Compute occurrence counts from the current tree
        self.occurrence_counts = self.compute_occurrence_counts()

        if hasattr(self, "analysis_tree"):
            tree = self.analysis_tree
            tree.delete(*tree.get_children())

            repo = SysMLRepository.get_instance()
            global_enabled = getattr(self, "enabled_work_products", set())
            smt = getattr(self, "safety_mgmt_toolbox", None)
            if smt and getattr(smt, "work_products", None):
                phase_enabled = smt.enabled_products()
            else:
                phase_enabled = global_enabled
            enabled = global_enabled & phase_enabled

            # --- Safety & Security Management Section ---
            self.management_diagrams = sorted(
                [
                    d
                    for d in repo.visible_diagrams().values()
                    if "safety-management" in getattr(d, "tags", [])
                ],
                key=lambda d: d.name or d.diag_id,
            )
            mgmt_root = tree.insert("", "end", text="Safety & Security Management", open=True)
            gov_root = tree.insert(
                mgmt_root,
                "end",
                text="Safety & Security Governance Diagrams",
                open=True,
            )
            self.safety_mgmt_toolbox = getattr(
                self, "safety_mgmt_toolbox", SafetyManagementToolbox()
            )
            toolbox = self.safety_mgmt_toolbox
            self.governance_manager.attach_toolbox(toolbox)
            toolbox.list_diagrams()
            self.update_lifecycle_cb()
            self.refresh_tool_enablement()

            def _visible(analysis_name: str, doc_name: str) -> bool:
                return toolbox.document_visible(analysis_name, doc_name)

            index_map = {
                (d.name or d.diag_id): idx
                for idx, d in enumerate(self.management_diagrams)
            }

            def _in_any_module(name, modules):
                for mod in modules:
                    if name in mod.diagrams or _in_any_module(name, mod.modules):
                        return True
                return False

            def _add_module(mod, parent):
                node = tree.insert(
                    parent,
                    "end",
                    text=mod.name,
                    open=True,
                    image=getattr(self, "pkg_icon", None),
                )
                for sub in sorted(mod.modules, key=lambda m: m.name):
                    _add_module(sub, node)
                for name in sorted(mod.diagrams):
                    idx = index_map.get(name)
                    if idx is not None:
                        tree.insert(
                            node,
                            "end",
                            text=name,
                            tags=("gov", str(idx)),
                            image=getattr(self, "gsn_diagram_icon", None),
                        )

            for mod in sorted(toolbox.modules, key=lambda m: m.name):
                _add_module(mod, gov_root)

            for name in sorted(toolbox.diagrams.keys()):
                if not _in_any_module(name, toolbox.modules):
                    idx = index_map.get(name)
                    if idx is not None:
                        tree.insert(
                            gov_root,
                            "end",
                            text=name,
                            tags=("gov", str(idx)),
                            image=getattr(self, "gsn_diagram_icon", None),
                        )

            # --- GSN Diagrams Section ---
            def _collect_gsn_diagrams(module):
                diagrams = list(module.diagrams)
                for sub in module.modules:
                    diagrams.extend(_collect_gsn_diagrams(sub))
                return diagrams

            self.all_gsn_diagrams = sorted(
                list(getattr(self, "gsn_diagrams", []))
                + [
                    d
                    for diag in repo.visible_diagrams().values()
                    for d in diag.diagrams
                    if "gsn" in getattr(diag, "tags", [])
                    and _visible(diag.name, d.name)
                ]
            , key=lambda d: d.name or d.diag_id)

            gsn_root = tree.insert(
                mgmt_root,
                "end",
                text="GSN Diagrams",
                open=True,
            )
            for idx, diag in enumerate(self.all_gsn_diagrams):
                tree.insert(
                    gsn_root,
                    "end",
                    text=diag.name or diag.diag_id,
                    tags=("gsn", str(idx)),
                    image=getattr(self, "gsn_diagram_icon", None),
                )

            # --- Analysis Documents Section ---
            analyses_root = tree.insert(
                "",
                "end",
                text="Analyses",
                open=True,
            )

            # Helper to add documents if visible
            def _add_docs(category, docs, doc_type, icon):
                if not docs:
                    return
                cat_node = tree.insert(analyses_root, "end", text=category, open=True)
                for idx, doc in enumerate(docs):
                    if _visible(doc_type, getattr(doc, "name", "")):
                        tree.insert(
                            cat_node,
                            "end",
                            text=getattr(doc, "name", f"{doc_type} {idx}") or f"{doc_type} {idx}",
                            tags=(doc_type.lower(), str(idx)),
                            image=icon,
                        )

            icons = getattr(self, "diagram_icons", {})
            _add_docs("HAZOP", self.hazop_docs, "Hazop", icons.get("Activity Diagram"))
            _add_docs("Risk Assessment", self.hara_docs, "Hara", icons.get("Activity Diagram"))
            _add_docs("STPA", self.stpa_docs, "Stpa", icons.get("Activity Diagram"))
            _add_docs("Threat Analysis", self.threat_docs, "Threat", icons.get("Activity Diagram"))
            _add_docs(
                "Risk Controls",
                self.risk_control_docs,
                "RiskControl",
                icons.get("Activity Diagram"),
            )
            _add_docs("FI → TC", self.fi2tc_docs, "Fi2Tc", icons.get("Activity Diagram"))
            _add_docs("TC → FI", self.tc2fi_docs, "Tc2Fi", icons.get("Activity Diagram"))
            _add_docs("Mission Profiles", self.mission_profiles, "MissionProfile", icons.get("Activity Diagram"))
            _add_docs("Reliability", self.reliability_analyses, "Reliability", icons.get("Activity Diagram"))

            # --- Product Goals Section ---
            pg_root = tree.insert(
                "",
                "end",
                text="Product Goals",
                open=True,
            )
            for idx, te in enumerate(getattr(self, "top_events", [])):
                tree.insert(
                    pg_root,
                    "end",
                    text=te.user_name or f"SG {te.unique_id}",
                    tags=("te", str(idx)),
                    image=getattr(self, "diagram_icons", {}).get("Activity Diagram"),
                )

    def update_failure_list(self):
        """Aggregate failure effects from FMEA and FMEDA entries."""
        failures: list[str] = []
        for entry in self.get_all_fmea_entries():
            eff = getattr(entry, "fmea_effect", "").strip()
            if eff and eff not in failures:
                failures.append(eff)
        self.failures = failures

    def update_triggering_condition_list(self):
        """Aggregate triggering conditions from docs and FTAs."""
        names: list[str] = []
        for n in self.get_all_triggering_conditions():
            nm = n.user_name or f"TC {n.unique_id}"
            if nm not in names:
                names.append(nm)
        for doc in self.fi2tc_docs + self.tc2fi_docs:
            for e in doc.entries:
                val = e.get("triggering_conditions", "")
                for part in val.split(";"):
                    p = part.strip()
                    if p and p not in names:
                        names.append(p)
        self.triggering_conditions = names

    def update_functional_insufficiency_list(self):
        """Aggregate functional insufficiencies from docs and FTAs."""
        names: list[str] = []
        for n in self.get_all_functional_insufficiencies():
            nm = n.user_name or f"FI {n.unique_id}"
            if nm not in names:
                names.append(nm)
        for doc in self.fi2tc_docs + self.tc2fi_docs:
            for e in doc.entries:
                val = e.get("functional_insufficiencies", "")
                for part in val.split(";"):
                    p = part.strip()
                    if p and p not in names:
                        names.append(p)
        self.functional_insufficiencies = names

    def update_hazard_list(self):
        """Aggregate hazards from risk assessment and HAZOP documents."""
        hazards: list[str] = []
        severity_map: dict[str, int] = {}
        for doc in self.hara_docs:
            for e in doc.entries:
                h = getattr(e, "hazard", "").strip()
                if not h:
                    continue
                if h not in hazards:
                    hazards.append(h)
                sev = getattr(e, "severity", None)
                if sev is not None:
                    try:
                        severity_map[h] = int(sev)
                    except Exception:
                        severity_map[h] = 1
        for doc in self.hazop_docs:
            for e in doc.entries:
                h = getattr(e, "hazard", "").strip()
                if not h:
                    continue
                if h not in hazards:
                    hazards.append(h)
                sev = getattr(e, "severity", None)
                if sev is not None and h not in severity_map:
                    try:
                        severity_map[h] = int(sev)
                    except Exception:
                        severity_map[h] = 1
        for h in hazards:
            if h in severity_map:
                self.hazard_severity[h] = severity_map[h]
            elif h not in self.hazard_severity:
                self.hazard_severity[h] = 1
        self.hazards = hazards
