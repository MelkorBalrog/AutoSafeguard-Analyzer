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

import time

import importlib


# Import core package for testing user data utilities
automl = importlib.import_module("mainappsrc.core")


def test_load_user_data_parallel(monkeypatch):
    def fake_load_all_users():
        time.sleep(0.2)
        return {"u": "e"}

    def fake_load_user_config():
        time.sleep(0.2)
        return "name", "email"

    monkeypatch.setattr(automl, "load_all_users", fake_load_all_users)
    monkeypatch.setattr(automl, "load_user_config", fake_load_user_config)

    start = time.time()
    users, config = automl.load_user_data()
    elapsed = time.time() - start
    assert users == {"u": "e"}
    assert config == ("name", "email")
    assert elapsed < 0.35
