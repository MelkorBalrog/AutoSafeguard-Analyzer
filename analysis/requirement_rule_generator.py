#!/usr/bin/env python3
"""Utilities to derive requirement patterns from diagram rule configuration.

This module inspects the diagram rules configuration and generates requirement
pattern definitions for Safety & AI links, governance element relations and
several predefined templates. Each base pattern is expanded to include
conditional and constraint variants so that ``analysis.governance`` can pick up
new rules automatically whenever the configuration changes.
"""

from __future__ import annotations

from copy import deepcopy
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from config import load_diagram_rules

# ---------------------------------------------------------------------------
# Template variant helpers (adapted from generate_project_compatible_patterns.py)

def _normalize_base_template(tmpl: str) -> str:
    """Return canonical form of ``tmpl`` without condition/constraint clauses."""
    t = tmpl.strip()
    cond_prefix = "When <condition>, "
    if t.startswith(cond_prefix):
        t = t[len(cond_prefix) :]
    constrained_phrase = " constrained by <constraint>."
    if t.endswith(constrained_phrase):
        t = t[: -len(constrained_phrase)]
        t = t.rstrip()
        if t.endswith("."):
            t = t[:-1]
        t = t + "."
    t = t.strip()
    if not t.endswith("."):
        t += "."
    return t

def _build_cond_template(base_tmpl: str) -> str:
    base = base_tmpl.strip()
    if not base.endswith("."):
        base += "."
    return f"When <condition>, {base[0].upper()}{base[1:]}"

def _build_const_template(base_tmpl: str) -> str:
    base = base_tmpl.strip()
    if base.endswith("."):
        base = base[:-1]
    return f"{base} constrained by <constraint>."

def _build_cond_const_template(base_tmpl: str) -> str:
    return _build_const_template(_build_cond_template(base_tmpl))

def _ensure_variables(base_vars: Iterable[str], need_cond: bool, need_const: bool) -> List[str]:
    out = list(base_vars)
    if need_cond and "<condition>" not in out:
        out.append("<condition>")
    if need_const and "<constraint>" not in out:
        out.append("<constraint>")
    seen = set()
    result = []
    for v in out:
        if v not in seen:
            result.append(v)
            seen.add(v)
    return result

_SUFFIXES = [
    ("", False, False),
    ("-COND", True, False),
    ("-COND-CONST", True, True),
    ("-CONST", False, True),
]

def _pattern_id_base(pid: str) -> str:
    for suff in ("-COND-CONST", "-COND", "-CONST"):
        if pid.endswith(suff):
            return pid[: -len(suff)]
    return pid

def _expand_variants(pat: Dict[str, Any]) -> List[Dict[str, Any]]:
    pid = pat.get("Pattern ID", "").strip()
    base_id = _pattern_id_base(pid)
    base_tmpl = _normalize_base_template(pat.get("Template", ""))
    vars_ = list(pat.get("Variables", []))
    trig = pat.get("Trigger", "")
    notes = pat.get("Notes", "")

    result: List[Dict[str, Any]] = []
    for suffix, need_cond, need_const in _SUFFIXES:
        vid = base_id + suffix
        tmpl = (
            _build_cond_const_template(base_tmpl)
            if need_cond and need_const
            else _build_cond_template(base_tmpl)
            if need_cond
            else _build_const_template(base_tmpl)
            if need_const
            else base_tmpl
        )
        vars_needed = _ensure_variables(vars_, need_cond, need_const)
        result.append(
            {
                "Pattern ID": vid,
                "Trigger": trig,
                "Template": tmpl,
                "Variables": vars_needed,
                "Notes": notes,
            }
        )
    return result

STATIC_BASE_PATTERNS: List[Dict[str, Any]] = [
    {
        "Pattern ID": "AVD-implement-Driving_Function-Software_Component",
        "Trigger": "AV Dev: Driving Function --[Implement]--> Software Component",
        "Template": (
            "Engineering team shall implement the <target_id> (<target_class>) "
            "for the <source_id> (<source_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "For autonomous vehicle functionality development.",
    },
    {
        "Pattern ID": "EARS-EVENT",
        "Trigger": "Event-driven behavior",
        "Template": "the shall within, verified by.",
        "Variables": ["<condition>"],
        "Notes": "Suitable for automotive timing/latency requirements.",
    },
    {
        "Pattern ID": "EARS-STATE",
        "Trigger": "State-dependent behavior",
        "Template": "While, the shall and maintain.",
        "Variables": [],
        "Notes": "Operational modes (e.g., Manual, Automated, Degraded).",
    },
    {
        "Pattern ID": "EARS-UBIQ",
        "Trigger": "Generic (roles identifiable)",
        "Template": "The shall to achieve, verified by and recorded in.",
        "Variables": [],
        "Notes": "Operation/engineering-aligned ubiquitous requirement.",
    },
    {
        "Pattern ID": "EARS-UNWANTED",
        "Trigger": "Fault/HAZARD response",
        "Template": "If occurs, the shall within and transition to, logging evidence in.",
        "Variables": [],
        "Notes": "Undesired scenario handling requirement.",
    },
    {
        "Pattern ID": "IMP-improve-Field_Data-Model",
        "Trigger": "Improvement: Field Data --[Improve]--> Model",
        "Template": (
            "Engineering team shall improve the <target_id> (<target_class>) "
            "using the <source_id> (<source_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "Post-deployment improvement requirement.",
    },
    {
        "Pattern ID": "INSP-inspect-Vehicle-Safety_Compliance",
        "Trigger": "Inspection: Vehicle --[Inspect]--> Safety Compliance",
        "Template": (
            "Inspection team shall inspect the <source_id> (<source_class>) "
            "for <target_id> (<target_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "Periodic inspection requirement.",
    },
    {
        "Pattern ID": "NFR-COMPLIANCE",
        "Trigger": "Constraint node via Constrained by / Governed by",
        "Template": "The shall comply with and retain objective evidence in.",
        "Variables": [],
        "Notes": "Compliance requirement with auditable trail.",
    },
    {
        "Pattern ID": "NFR-METRIC-PERF",
        "Trigger": "Metric linked to Process/Activity (Monitors/Produces/Uses)",
        "Template": (
            "The shall achieve ≤ measured over with ≥ confidence; measurement "
            "recorded in."
        ),
        "Variables": [],
        "Notes": "Performance KPI in engineering terms.",
    },
    {
        "Pattern ID": "OP-operate-Fleet-Vehicle",
        "Trigger": "Operation: Fleet --[Operate]--> Vehicle",
        "Template": (
            "Operations team shall operate the <target_id> (<target_class>) "
            "within the <source_id> (<source_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "Operational requirement.",
    },
    {
        "Pattern ID": "ORG-establish-Organization-Process",
        "Trigger": "Organization: Organization --[Establish]--> Process",
        "Template": "shall establish the and record evidence in.",
        "Variables": ["<due_date>"],
        "Notes": "Organizational process definition requirement.",
    },
    {
        "Pattern ID": "PROD-manufacture-Manufacturing_Process-Vehicle",
        "Trigger": "Production: Manufacturing Process --[Manufacture]--> Vehicle",
        "Template": (
            "Manufacturing team shall manufacture the <target_id> (<target_class>) "
            "using the <source_id> (<source_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "Production requirement.",
    },
    {
        "Pattern ID": "TRI-triage-Incident-Safety_Issue",
        "Trigger": "Triage: Incident --[Triage]--> Safety Issue",
        "Template": (
            "Support team shall triage the <target_id> (<target_class>) from "
            "the <source_id> (<source_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "Incident triage requirement.",
    },
    {
        "Pattern ID": "VAL-validate-Test_Suite-System",
        "Trigger": "Validation: Test Suite --[Validate]--> System",
        "Template": (
            "Validation team shall validate the <target_id> (<target_class>) "
            "using the <source_id> (<source_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "Validation coverage requirement.",
    },
    {
        "Pattern ID": "VER-verify-Verification_Plan-Component",
        "Trigger": "Verification: Verification Plan --[Verify]--> Component",
        "Template": (
            "Verification team shall verify the <target_id> (<target_class>) "
            "according to the <source_id> (<source_class>)."
        ),
        "Variables": [
            "<source_id>",
            "<source_class>",
            "<target_id>",
            "<target_class>",
            "<acceptance_criteria>",
        ],
        "Notes": "Verification requirement.",
    },
]


# ---------------------------------------------------------------------------
# Pattern generation from diagram rules

def _slug(name: str) -> str:
    """Return a filesystem-friendly identifier component."""
    return re.sub(r"\W+", "_", name).strip("_")

def generate_patterns_from_config(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate requirement pattern definitions from ``cfg``.

    Safety & AI relation rules, governance connections and predefined templates
    are expanded into project-compatible requirement patterns. Each allowed
    ``(source, relation, target)`` combination yields four variants (base,
    ``-COND``, ``-CONST`` and ``-COND-CONST``).
    """

    req_rules = {k.lower(): v for k, v in cfg.get("requirement_rules", {}).items()}
    sa_rules = cfg.get("safety_ai_relation_rules", {})
    conn_rules = cfg.get("connection_rules", {})
    patterns: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()

    def add_pattern(prefix: str, relation: str, src: str, dst: str, trig_prefix: str) -> None:
        rule = req_rules.get(relation.lower())
        if not rule:
            return
        action = rule.get("action", "")
        subject = rule.get("subject", "Engineering team")
        notes = "Instantiate on detected edge; add measurable criteria."
        pid = f"{prefix}-{_slug(relation.lower())}-{_slug(src)}-{_slug(dst)}"
        if pid in seen_ids:
            return
        seen_ids.add(pid)
        trig = f"{trig_prefix}: {src} --[{relation}]--> {dst}"
        tmpl = (
            f"{subject} shall {action} the <target_id> (<target_class>) "
            f"using the <source_id> (<source_class>)."
        )
        base_pat = {
            "Pattern ID": pid,
            "Trigger": trig,
            "Template": tmpl,
            "Variables": [
                "<source_id>",
                "<source_class>",
                "<target_id>",
                "<target_class>",
                "<acceptance_criteria>",
            ],
            "Notes": notes,
        }
        patterns.extend(_expand_variants(base_pat))

    for relation, sources in sa_rules.items():
        for src, targets in sources.items():
            for dst in targets:
                add_pattern("SA", relation, src, dst, "Safety&AI")

    gov_conn = conn_rules.get("Governance Diagram", {})
    for relation, sources in gov_conn.items():
        for src, targets in sources.items():
            for dst in targets:
                add_pattern("GOV", relation, src, dst, "Governance")

    gov_nodes = cfg.get("governance_element_nodes", [])
    gov_relations = cfg.get("governance_element_relations", [])
    for relation in gov_relations:
        for dst in gov_nodes:
            if dst == "Role":
                continue
            add_pattern("GOV", relation, "Role", dst, "Governance")

    for base in STATIC_BASE_PATTERNS:
        patterns.extend(_expand_variants(base))

    # Deterministic ordering for stability
    return sorted(patterns, key=lambda p: p["Pattern ID"])

# Convenience CLI ------------------------------------------------------------

def main(argv: Iterable[str] | None = None) -> int:
    """Command line entry point."""
    import argparse

    ap = argparse.ArgumentParser(description="Generate requirement patterns from diagram rules")
    ap.add_argument("--config", default=Path("config/diagram_rules.json"), type=Path, help="Diagram rules JSON path")
    ap.add_argument("--out", default=Path("config/requirement_patterns.json"), type=Path, help="Output JSON path")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = ap.parse_args(list(argv) if argv is not None else None)

    cfg = load_diagram_rules(args.config)
    pats = generate_patterns_from_config(cfg)
    if args.pretty:
        args.out.write_text(json.dumps(pats, ensure_ascii=False, indent=2) + "\n")
    else:
        args.out.write_text(json.dumps(pats, ensure_ascii=False))
    print(f"Wrote {len(pats)} patterns to {args.out}")
    return 0

if __name__ == "__main__":  # pragma: no cover - CLI utility
    raise SystemExit(main())
