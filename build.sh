#!/bin/bash
# Build script for macOS/Linux

echo "Building DICOM Tag Updater executable..."
echo

# Check if PyInstaller is installed
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    python3 -m pip install pyinstaller
fi

echo
echo "Building executable..."
pyinstaller build_executable.spec

if [ $? -eq 0 ]; then
    echo
    echo "Build successful!"
    echo "Executable location: dist/DICOMTagUpdater"
    echo
else
    echo
    echo "Build failed!"
    exit 1
fi

