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

import zipfile
import tarfile
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from tools import create_installer as ci


def setup_files(tmp_path: Path):
    exe = tmp_path / "AutoML.exe"
    exe.write_text("exe")
    extra = tmp_path / "README.md"
    extra.write_text("readme")
    return exe, [extra]


def test_create_installer_zip(tmp_path, monkeypatch):
    exe, extras = setup_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "installer.zip"
    ci.create_installer_zip(exe, output, extras)
    with zipfile.ZipFile(output) as zf:
        assert "AutoML.exe" in zf.namelist()
        assert "README.md" in zf.namelist()


def test_create_installer_tar(tmp_path, monkeypatch):
    exe, extras = setup_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "installer.tar.gz"
    ci.create_installer_tar(exe, output, extras)
    with tarfile.open(output) as tf:
        names = tf.getnames()
        assert "AutoML.exe" in names
        assert "README.md" in names


def test_create_installer_shutil_zip(tmp_path, monkeypatch):
    exe, extras = setup_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    archive = ci.create_installer_shutil_zip(exe, tmp_path, extras)
    with zipfile.ZipFile(archive) as zf:
        assert "AutoML.exe" in zf.namelist()
        assert "README.md" in zf.namelist()


def test_create_installer_shutil_targz(tmp_path, monkeypatch):
    exe, extras = setup_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    archive = ci.create_installer_shutil_targz(exe, tmp_path, extras)
    with tarfile.open(archive) as tf:
        names = [Path(n).name for n in tf.getnames()]
        assert "AutoML.exe" in names
        assert "README.md" in names
