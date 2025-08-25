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

import sys, types, json
from unittest.mock import MagicMock

# Stub PIL modules for AutoML import
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("PIL.ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("PIL.ImageFont"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from AutoML import AutoMLApp
import AutoML


def _no_history_clear_v1(mock):
    return mock.call_count == 0


def _no_history_clear_v2(mock):
    return not mock.called


def _no_history_clear_v3(mock):
    return mock.mock_calls == []


def _no_history_clear_v4(mock):
    mock.assert_not_called()
    return True


def _no_history_clear(mock):
    return _no_history_clear_v3(mock)


def test_load_model_preserves_history(tmp_path, monkeypatch):
    model = tmp_path / "model.json"
    model.write_text("{}")

    app = AutoMLApp.__new__(AutoMLApp)
    app._loaded_model_paths = []
    app.apply_model_data = MagicMock()
    app.set_last_saved_state = MagicMock()
    app._reset_on_load = MagicMock()
    app.has_unsaved_changes = lambda: False

    cuh = MagicMock()
    app.clear_undo_history = cuh

    monkeypatch.setattr(AutoML.filedialog, "askopenfilename", lambda **k: str(model))
    monkeypatch.setattr(AutoML.messagebox, "showerror", lambda *a, **k: None)

    app.load_model()

    assert _no_history_clear(cuh)

