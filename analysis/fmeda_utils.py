# Author: Miguel Marina <karel.capek.robotics@gmail.com>
from analysis.models import ASIL_ORDER, ASIL_TARGETS, component_fit_map
from pathlib import Path
from config import load_diagram_rules

# Node types treated as gates when determining component names
_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config/diagram_rules.json"
_CONFIG = load_diagram_rules(_CONFIG_PATH)
GATE_NODE_TYPES = set(_CONFIG.get("gate_node_types", []))


def reload_config() -> None:
    """Reload gate node types from configuration."""
    global _CONFIG, GATE_NODE_TYPES
    _CONFIG = load_diagram_rules(_CONFIG_PATH)
    GATE_NODE_TYPES = set(_CONFIG.get("gate_node_types", []))


def _aggregate_goal_metrics(entries, components, sg_to_asil, sg_targets=None, get_node=lambda x: x):
    """Return metrics per safety goal."""
    comp_fit = component_fit_map(components)
    goals = {}
    for be in entries:
        src = get_node(be)
        sg = getattr(src, "fmeda_safety_goal", "")
        data = goals.setdefault(
            sg,
            {
                "total": 0.0,
                "spf": 0.0,
                "lpf": 0.0,
                "asil": sg_to_asil(sg),
            },
        )
        parent = src.parents[0] if src.parents else None
        if parent and getattr(parent, "node_type", "").upper() not in GATE_NODE_TYPES:
            comp_name = getattr(parent, "user_name", "")
        else:
            comp_name = getattr(src, "fmea_component", "")
        fit = comp_fit.get(comp_name)
        frac = getattr(src, "fmeda_fault_fraction", 0.0)
        if frac > 1.0:
            frac /= 100.0
        value = fit * frac if fit is not None else getattr(src, "fmeda_fit", 0.0)
        data["total"] += value
        if getattr(src, "fmeda_fault_type", "permanent") == "permanent":
            data["spf"] += value * (1 - getattr(src, "fmeda_diag_cov", 0.0))
        else:
            data["lpf"] += value * (1 - getattr(src, "fmeda_diag_cov", 0.0))

    result = {}
    for sg, vals in goals.items():
        total = vals["total"]
        spf = vals["spf"]
        lpf = vals["lpf"]
        asil = vals["asil"]
        dc = (total - (spf + lpf)) / total if total else 0.0
        spfm_metric = 1 - spf / total if total else 0.0
        lpfm_metric = 1 - lpf / (total - spf) if total > spf else 0.0
        target = None
        if sg_targets and sg in sg_targets:
            target = sg_targets[sg]
        else:
            target = ASIL_TARGETS.get(asil, ASIL_TARGETS["QM"])
        result[sg] = {
            "total": total,
            "spfm_raw": spf,
            "lpfm_raw": lpf,
            "dc": dc,
            "spfm_metric": spfm_metric,
            "lpfm_metric": lpfm_metric,
            "asil": asil,
            "ok_dc": dc >= target["dc"],
            "ok_spfm": spfm_metric >= target["spfm"],
            "ok_lpfm": lpfm_metric >= target["lpfm"],
        }
    return result


def compute_fmeda_metrics(entries, components, sg_to_asil, sg_targets=None, get_node=lambda x: x):
    """Return aggregate and per-goal FMEDA metrics."""
    goal_metrics = _aggregate_goal_metrics(entries, components, sg_to_asil, sg_targets, get_node)

    total = sum(m["total"] for m in goal_metrics.values())
    spf = sum(m["spfm_raw"] for m in goal_metrics.values())
    lpf = sum(m["lpfm_raw"] for m in goal_metrics.values())
    asil = "QM"
    for m in goal_metrics.values():
        if ASIL_ORDER.get(m["asil"], 0) > ASIL_ORDER.get(asil, 0):
            asil = m["asil"]
    dc = (total - (spf + lpf)) / total if total else 0.0
    spfm_metric = 1 - spf / total if total else 0.0
    lpfm_metric = 1 - lpf / (total - spf) if total > spf else 0.0
    thresh = ASIL_TARGETS.get(asil, ASIL_TARGETS["QM"])
    return {
        "total": total,
        "spfm_raw": spf,
        "lpfm_raw": lpf,
        "dc": dc,
        "spfm_metric": spfm_metric,
        "lpfm_metric": lpfm_metric,
        "asil": asil,
        "ok_dc": dc >= thresh["dc"],
        "ok_spfm": spfm_metric >= thresh["spfm"],
        "ok_lpfm": lpfm_metric >= thresh["lpfm"],
        "goal_metrics": goal_metrics,
    }
