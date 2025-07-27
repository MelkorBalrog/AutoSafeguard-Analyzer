@echo off
REM Helper to run the AutoML executable

setlocal

set "BIN_DIR=%~dp0"

if not exist "%BIN_DIR%AutoML.exe" (
    echo Executable not found. Run bin\build_exe.bat first.
    exit /b 1
)

"%BIN_DIR%AutoML.exe" %*
