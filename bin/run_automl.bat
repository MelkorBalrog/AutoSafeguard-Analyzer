REM # Author: Miguel Marina <karel.capek.robotics@gmail.com>
REM # SPDX-License-Identifier: GPL-3.0-or-later
REM #
REM # Copyright (C) 2025 Capek System Safety & Robotic Solutions
REM #
REM # This program is free software: you can redistribute it and/or modify
REM # it under the terms of the GNU General Public License as published by
REM # the Free Software Foundation, either version 3 of the License, or
REM # (at your option) any later version.
REM #
REM # This program is distributed in the hope that it will be useful,
REM # but WITHOUT ANY WARRANTY; without even the implied warranty of
REM # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM # GNU General Public License for more details.
REM #
REM # You should have received a copy of the GNU General Public License
REM # along with this program.  If not, see <https://www.gnu.org/licenses/>.

@echo off
REM Helper to run the AutoML executable

setlocal

set "BIN_DIR=%~dp0"

if not exist "%BIN_DIR%AutoML.exe" (
    echo Executable not found. Run bin\build_exe.bat first.
    exit /b 1
)

"%BIN_DIR%AutoML.exe" %*
