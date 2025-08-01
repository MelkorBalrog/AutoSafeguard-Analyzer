#!/usr/bin/env bash
# Script to build AutoML executable using PyInstaller
set -e
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "PyInstaller is required. Install with: pip install pyinstaller" >&2
    exit 1
fi

# Ensure Pillow and other dependencies are installed so PyInstaller bundles them
python -m pip show pillow >/dev/null 2>&1 || {
    echo "Missing required package 'pillow'. Install with: pip install pillow" >&2
    exit 1
}
for pkg in openpyxl networkx matplotlib reportlab adjustText; do
    python -m pip show "$pkg" >/dev/null 2>&1 || {
        echo "Missing required package '$pkg'. Install with: pip install $pkg" >&2
        exit 1
    }
done

# Warn if running a pre-release Python build which may cause PyInstaller errors
if python -c "import sys, re; v=sys.version; print('pre' if re.search('(alpha|beta|candidate|rc)', v) else '')" | grep -q pre; then
    echo "Warning: pre-release Python builds can fail with PyInstaller. Use a stable release." >&2
fi

# Ensure commands run from repository root (parent directory of this script)
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

# Remove leftover spec file so our options are respected even after a failed build
rm -f AutoML.spec

# Use PyInstaller to create a single-file executable
pyinstaller --noconfirm --onefile --windowed \
    --name AutoML \
    --exclude-module scipy \
    --hidden-import=PIL.ImageTk \
    --add-data "styles:styles" AutoML.py

# Move the resulting executable to the bin directory
mkdir -p bin
mv -f dist/AutoML.exe bin/
# Clean up build artifacts
rm -rf build dist __pycache__ AutoML.spec

echo "Executable created at bin/AutoML.exe"
