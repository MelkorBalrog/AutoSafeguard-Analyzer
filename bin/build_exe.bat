@echo off
REM Build AutoML executable using PyInstaller

setlocal

REM Determine important paths
set "BIN_DIR=%~dp0"
set "REPO_ROOT=%~dp0.."

REM Warn if running a pre-release Python build which may cause PyInstaller errors
for /f "delims=" %%V in ('python -c "import sys;print(sys.version)"') do set "PYVER=%%V"
echo %PYVER% | findstr /I "alpha beta candidate rc" >nul
if not errorlevel 1 (
    echo Warning: pre-release Python builds can fail with PyInstaller. Use a stable release.
)

REM Verify required Python packages are installed using pip show
python -m pip show pillow >NUL 2>&1 || (
    echo Missing required package 'pillow'. Install with: pip install pillow
    exit /b 1
)

for %%P in (openpyxl networkx matplotlib reportlab adjustText) do (
    python -m pip show %%P >NUL 2>&1 || (
        echo Missing required package '%%P'. Install with: pip install %%P
        exit /b 1
    )
)

REM Ask the user for an optional icon to embed in the executable
set "ICON_ARG="
set /P "ICON_PATH=Enter path to .ico icon file (leave blank for none): "
if defined ICON_PATH (
    if exist "%ICON_PATH%" (
        set "ICON_ARG=--icon \"%ICON_PATH%\""
    ) else (
        echo Icon not found: %ICON_PATH%
        echo Continuing without a custom icon.
    )
)

REM Run PyInstaller from the repository root so it can locate launcher.py
cd /d "%REPO_ROOT%"
if exist AutoML.spec del AutoML.spec
pyinstaller --noconfirm --onefile --windowed --name AutoML ^
    --exclude-module scipy ^
    --hidden-import=PIL.ImageTk ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.simpledialog ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=tkinter.ttk ^
    --add-data "styles;styles" ^
    --add-data "AutoML.py;." ^
    %ICON_ARG% launcher.py
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
