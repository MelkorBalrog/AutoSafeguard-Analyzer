#!/usr/bin/env bash
# Run the AutoML executable. Build it first if not present.
if [ ! -f "bin/AutoML.exe" ]; then
    echo "Executable not found. Run bin/build_exe.sh first." >&2
    exit 1
fi
./bin/AutoML.exe "$@"
