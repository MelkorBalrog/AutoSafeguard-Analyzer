import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis import SafetyManagementToolbox


def test_work_product_registration():
    toolbox = SafetyManagementToolbox()
    toolbox.add_work_product("Activity Diagram", "HAZOP", "Link action to hazard")

    products = toolbox.get_work_products()
    assert len(products) == 1
    assert products[0].diagram == "Activity Diagram"
    assert products[0].analysis == "HAZOP"
    assert products[0].rationale == "Link action to hazard"


def test_lifecycle_and_workflow_storage():
    toolbox = SafetyManagementToolbox()
    toolbox.build_lifecycle(["concept", "development", "operation"])
    toolbox.define_workflow("risk", ["identify", "assess", "mitigate"])

    assert [stage.name for stage in toolbox.lifecycle] == [
        "concept",
        "development",
        "operation",
    ]
    assert toolbox.get_workflow("risk") == ["identify", "assess", "mitigate"]
    assert toolbox.get_workflow("missing") == []
