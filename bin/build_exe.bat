@echo off
REM Build AutoML executable using PyInstaller

REM Determine the repository root (parent of this script)
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%.." >nul

pyinstaller --noconfirm --onefile --windowed --name AutoML AutoML.py
if errorlevel 1 (
    echo Failed to build executable.
    popd
    exit /b %errorlevel%
)

if not exist bin mkdir bin
move /Y dist\AutoML.exe bin\AutoML.exe >nul
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
if exist AutoML.spec del AutoML.spec

popd >nul
echo Executable created at bin\AutoML.exe
