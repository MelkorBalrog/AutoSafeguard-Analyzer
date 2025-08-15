import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.safety_management import (
    SAFETY_ANALYSIS_WORK_PRODUCTS,
    SafetyManagementToolbox,
    SafetyWorkProduct,
)
from analysis.governance import GovernanceDiagram


def test_causal_bayesian_network_work_product():
    name = "Causal Bayesian Network Analysis"
    assert name in SAFETY_ANALYSIS_WORK_PRODUCTS
    toolbox = SafetyManagementToolbox()
    toolbox.work_products.append(SafetyWorkProduct("Gov", name, ""))
    diagram = GovernanceDiagram.default_from_work_products([name])
    assert diagram.tasks() == [name]
