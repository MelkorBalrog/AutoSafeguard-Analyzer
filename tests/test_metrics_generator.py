from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.metrics_generator import collect_metrics


def test_collect_metrics_returns_data():
    metrics = collect_metrics(Path("analysis"))
    assert metrics["total_files"] > 0
    assert metrics["total_loc"] > 0
    assert metrics["total_functions"] >= 0
