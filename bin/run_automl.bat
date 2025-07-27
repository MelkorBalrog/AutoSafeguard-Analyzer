@echo off
REM Helper to run the AutoML executable
if not exist bin\AutoML.exe (
    echo Executable not found. Run bin\build_exe.bat first.
    exit /b 1
)

bin\AutoML.exe %*
