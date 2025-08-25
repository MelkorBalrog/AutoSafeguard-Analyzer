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

import pytest
from unittest import mock

import automl as launcher


def test_ensure_ghostscript_non_windows():
    with mock.patch.object(launcher, "os") as m_os:
        m_os.name = "posix"
        launcher.ensure_ghostscript()


def test_ensure_ghostscript_already_present():
    with mock.patch.object(launcher, "os") as m_os:
        m_os.name = "nt"
        with mock.patch.object(launcher, "GS_PATH") as gs_path:
            gs_path.exists.return_value = True
            launcher.ensure_ghostscript()
            gs_path.exists.assert_called_once()


def test_ensure_ghostscript_installs():
    with mock.patch.object(launcher, "os") as m_os:
        m_os.name = "nt"
        with mock.patch.object(launcher, "GS_PATH") as gs_path:
            gs_path.exists.side_effect = [False, True]
            calls = []

            def fake_check_call(cmd, *args, **kwargs):
                calls.append(cmd)
                if cmd and cmd[0] == "winget":
                    return 0
                raise FileNotFoundError

            with mock.patch.object(launcher, "subprocess") as m_sub:
                m_sub.check_call.side_effect = fake_check_call
                launcher.ensure_ghostscript()
            assert calls[0][0] == "winget"


def test_ensure_ghostscript_failure():
    with mock.patch.object(launcher, "os") as m_os:
        m_os.name = "nt"
        with mock.patch.object(launcher, "GS_PATH") as gs_path:
            gs_path.exists.return_value = False
            def fail(*args, **kwargs):
                raise FileNotFoundError
            with mock.patch.object(launcher.subprocess, "check_call", side_effect=fail):
                with pytest.raises(RuntimeError):
                    launcher.ensure_ghostscript()
