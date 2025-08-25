# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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


def test_cli_writes_metrics_and_plots(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    analysis_dir = repo_root / "analysis"
    script = repo_root / "tools" / "metrics_generator.py"
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--path",
            str(analysis_dir),
            "--plots",
        ],
        cwd=tmp_path,
        check=True,
    )
    metrics_path = tmp_path / "metrics.json"
    assert metrics_path.exists()
    data = json.loads(metrics_path.read_text())
    assert data["total_files"] > 0
    assert (tmp_path / "metrics_loc.png").exists()
    assert (tmp_path / "metrics_complexity.png").exists()
