from pathlib import Path
from config.config_loader import load_json_with_comments

def test_resource_fallback(monkeypatch):
    cfg_path = Path(__file__).resolve().parents[1] / "config" / "rules" / "diagram_rules.json"
    original = Path.read_text
    call_count = {"count": 0}

    def mock_read_text(self, *args, **kwargs):
        if self == cfg_path and call_count["count"] == 0:
            call_count["count"] += 1
            raise FileNotFoundError
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", mock_read_text)
    data = load_json_with_comments(cfg_path)
    assert "ai_nodes" in data
