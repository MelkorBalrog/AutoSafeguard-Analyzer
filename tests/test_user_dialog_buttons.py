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

import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import AutoML as automl


def _collect_button_styles(dialog_cls, monkeypatch):
    styles = []
    applied = {"called": 0}

    class DummyButton:
        def __init__(self, master, **kwargs):
            styles.append(kwargs.get("style"))
        def pack(self, *a, **k):
            pass

    class DummyFrame:
        def __init__(self, *a, **k):
            pass
        def pack(self, *a, **k):
            pass

    class DummyDialog:
        def bind(self, *a, **k):
            pass
        ok = lambda self, *a, **k: None
        cancel = lambda self, *a, **k: None

    def fake_apply(style=None):
        applied["called"] += 1

    import gui.controls.mac_button_style as mbs

    monkeypatch.setattr(automl.ttk, "Button", DummyButton)
    monkeypatch.setattr(automl.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(mbs.ttk, "Button", DummyButton)
    monkeypatch.setattr(mbs.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(automl, "apply_purplish_button_style", fake_apply)
    monkeypatch.setattr(mbs, "apply_purplish_button_style", fake_apply)

    dlg = DummyDialog()
    dialog_cls.buttonbox(dlg)
    return styles, applied["called"]


def test_user_info_dialog_purplish_buttons(monkeypatch):
    styles, called = _collect_button_styles(automl.UserInfoDialog, monkeypatch)
    assert styles == ["Purple.TButton", "Purple.TButton"]
    assert called == 1


def test_user_select_dialog_purplish_buttons(monkeypatch):
    styles, called = _collect_button_styles(automl.UserSelectDialog, monkeypatch)
    assert styles == ["Purple.TButton", "Purple.TButton"]
    assert called == 1


def test_base_dialog_purplish_buttons(monkeypatch):
    styles, called = _collect_button_styles(automl.simpledialog.Dialog, monkeypatch)
    assert styles == ["Purple.TButton", "Purple.TButton"]
    assert called == 1
