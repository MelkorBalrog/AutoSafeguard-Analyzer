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

from __future__ import annotations

"""AutoML package exposing application classes lazily."""


import importlib
from types import ModuleType

_module: ModuleType | None = None


def __getattr__(name: str):
    global _module
    if name == "FMEARowDialog":
        from .fmea_row_dialog import FMEARowDialog as dlg
        return dlg
    if name == "ReqDialog":
        from .req_dialog import ReqDialog as dlg
        return dlg
    if name == "SelectBaseEventDialog":
        from .select_base_event_dialog import SelectBaseEventDialog as dlg
        return dlg
    if _module is None:
        _module = importlib.import_module("mainappsrc.automl_core")
    return getattr(_module, name)


__all__ = ["FMEARowDialog", "ReqDialog", "SelectBaseEventDialog"]
