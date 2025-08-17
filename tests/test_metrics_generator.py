from pathlib import Path
import sys
import subprocess
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.metrics_generator import collect_metrics


def test_collect_metrics_returns_data():
    metrics = collect_metrics(Path("analysis"))
    assert metrics["total_files"] > 0
    assert metrics["total_loc"] > 0
    assert metrics["total_functions"] >= 0


def test_cli_writes_metrics_file(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    analysis_dir = repo_root / "analysis"
    script = repo_root / "tools" / "metrics_generator.py"
    subprocess.run(
        ["python", str(script), "--path", str(analysis_dir)],
        cwd=tmp_path,
        check=True,
    )
    metrics_path = tmp_path / "metrics.json"
    assert metrics_path.exists()
    data = json.loads(metrics_path.read_text())
    assert data["total_files"] > 0
