#!/usr/bin/env bash
# Run the AutoML executable. Build it first if not present.

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

# Determine repository root (parent directory of this script)
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

if [ ! -f "bin/AutoML.exe" ]; then
    echo "Executable not found. Run bin/build_exe.sh first." >&2
    exit 1
fi

./bin/AutoML.exe "$@"
