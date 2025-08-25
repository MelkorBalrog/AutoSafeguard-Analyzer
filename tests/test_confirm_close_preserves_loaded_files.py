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

import os
import tempfile
from unittest.mock import MagicMock

from AutoML import AutoMLApp


class DummyRoot:
    def __init__(self):
        self.quit = MagicMock()
        self.destroy = MagicMock()


def test_confirm_close_preserves_loaded_files():
    fd, path = tempfile.mkstemp(suffix=".autml")
    os.close(fd)
    try:
        app = AutoMLApp.__new__(AutoMLApp)
        app.root = DummyRoot()
        app.has_unsaved_changes = lambda: False
        app._loaded_model_paths = [path]

        app.confirm_close()

        assert os.path.exists(path)
        app.root.quit.assert_called()
        app.root.destroy.assert_called()
    finally:
        if os.path.exists(path):
            os.remove(path)
