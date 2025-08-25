import json
from pathlib import Path

from mainappsrc.core import config_utils


def test_reload_local_config_updates_gate_types(tmp_path, monkeypatch):
    cfg_path = tmp_path / "diagram_rules.json"
    cfg_path.write_text(json.dumps({"gate_node_types": ["NEW_GATE"]}))
    monkeypatch.setattr(config_utils, "_CONFIG_PATH", cfg_path)

    called = {"val": False}

    def fake_regen(*args, **kwargs):
        called["val"] = True

    monkeypatch.setattr(config_utils, "regenerate_requirement_patterns", fake_regen)
    config_utils._reload_local_config()
    assert config_utils.GATE_NODE_TYPES == {"NEW_GATE"}
    assert called["val"]


def test_unique_id_generation(monkeypatch):
    config_utils.AutoML_Helper.unique_node_id_counter = 1
    first = config_utils.AutoML_Helper.get_next_unique_id()
    second = config_utils.AutoML_Helper.get_next_unique_id()
    assert (first, second) == (1, 2)
    assert config_utils.AutoML_Helper.unique_node_id_counter == 3
