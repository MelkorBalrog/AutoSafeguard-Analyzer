@echo off
REM Build AutoML executable using PyInstaller
pyinstaller --noconfirm --onefile --windowed --name AutoML AutoML.py
if errorlevel 1 (
    echo Failed to build executable.
    exit /b %errorlevel%
)

if not exist bin mkdir bin
move /Y dist\AutoML.exe bin\AutoML.exe >nul
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
if exist AutoML.spec del AutoML.spec

echo Executable created at bin\AutoML.exe
