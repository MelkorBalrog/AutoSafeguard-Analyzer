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

import types

from AutoML import AutoMLApp


class DummyVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class DummyLabel:
    def __init__(self):
        self.text = ""

    def config(self, **kwargs):
        self.text = kwargs.get("text", self.text)


class DummyToolbox:
    def __init__(self):
        self.phase = None

    def set_active_module(self, phase):
        self.phase = phase


def test_active_phase_label_updates():
    app = types.SimpleNamespace(
        lifecycle_var=DummyVar(),
        safety_mgmt_toolbox=DummyToolbox(),
        update_views=lambda: None,
        active_phase_lbl=DummyLabel(),
    )
    app.on_lifecycle_selected = AutoMLApp.on_lifecycle_selected.__get__(app, AutoMLApp)

    app.lifecycle_var.set("Phase1")
    app.on_lifecycle_selected()

    assert app.active_phase_lbl.text == "Active phase: Phase1"
