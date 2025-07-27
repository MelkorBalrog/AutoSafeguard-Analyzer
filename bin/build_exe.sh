#!/usr/bin/env bash
# Script to build AutoML executable using PyInstaller
set -e
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "PyInstaller is required. Install with: pip install pyinstaller" >&2
    exit 1
fi

# Use PyInstaller to create a single-file executable
pyinstaller --noconfirm --onefile --windowed \
    --name AutoML AutoML.py

# Move the resulting executable to the bin directory
mkdir -p bin
mv -f dist/AutoML.exe bin/
# Clean up build artifacts
rm -rf build dist __pycache__ AutoML.spec

echo "Executable created at bin/AutoML.exe"
