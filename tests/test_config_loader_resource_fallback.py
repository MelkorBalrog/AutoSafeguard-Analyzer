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
