@echo off
REM Helper to run the AutoML executable

REM Locate repository root (parent of this script)
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%.." >nul

if not exist bin\AutoML.exe (
    echo Executable not found. Run bin\build_exe.bat first.
    popd
    exit /b 1
)

bin\AutoML.exe %*
popd >nul
