"""Analysis utilities for AutoML."""

from .sotif_validation import acceptance_rate, hazardous_behavior_rate, validation_time
from .confusion_matrix import compute_metrics, compute_metrics_from_target
from .safety_management import SafetyManagementToolbox

__all__ = [
    "acceptance_rate",
    "hazardous_behavior_rate",
    "validation_time",
    "compute_metrics",
    "SafetyManagementToolbox",
]


def __getattr__(name):
    if name == "SafetyManagementToolbox":
        from .safety_management import SafetyManagementToolbox as _SMT

        return _SMT
    raise AttributeError(name)
