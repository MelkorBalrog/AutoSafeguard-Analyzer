@echo off
REM Build AutoML executable using PyInstaller

setlocal

REM Determine important paths
set "BIN_DIR=%~dp0"
set "REPO_ROOT=%~dp0.."

REM Abort if running a pre-release Python build which is known to break PyInstaller
for /f "delims=" %%V in ('python -c "import sys;print(sys.version)"') do set "PYVER=%%V"
echo %PYVER% | findstr /I "alpha beta candidate rc" >nul
if not errorlevel 1 (
    echo Error: pre-release Python builds can fail with PyInstaller. Use a stable release.
    exit /b 1
)

REM Run PyInstaller from the repository root so it can locate AutoML.py
cd /d "%REPO_ROOT%"
if exist AutoML.spec del AutoML.spec
pyinstaller --noconfirm --onefile --windowed --name AutoML ^
    --exclude-module scipy AutoML.py
if errorlevel 1 (
    echo Failed to build executable.
    exit /b %errorlevel%
)

if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
move /Y dist\AutoML.exe "%BIN_DIR%AutoML.exe" >nul
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
if exist AutoML.spec del AutoML.spec

echo Executable created at %BIN_DIR%AutoML.exe
