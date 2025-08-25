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

from gui.controls import messagebox


def test_showinfo_does_not_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):  # pragma: no cover - simple flag setter
        nonlocal called
        called = True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    messagebox.showinfo("T", "M")
    assert called is False


def test_showwarning_does_not_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):  # pragma: no cover - simple flag setter
        nonlocal called
        called = True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    messagebox.showwarning("T", "M")
    assert called is False


def test_showerror_does_not_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):  # pragma: no cover - simple flag setter
        nonlocal called
        called = True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    messagebox.showerror("T", "M")
    assert called is False


def test_askyesno_displays_popup(monkeypatch):
    called = False

    def fake(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr(messagebox, "_create_dialog", fake)
    assert messagebox.askyesno("T", "M") is True
    assert called is True
