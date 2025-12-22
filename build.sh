#!/bin/bash
# Build script for macOS/Linux

echo "Building DICOM Tag Updater executable..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

# Check if PyInstaller is installed
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    python3 -m pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo
        echo "ERROR: Failed to install PyInstaller"
        echo "Please run manually: python3 -m pip install pyinstaller"
        exit 1
    fi
fi

echo
echo "Building executable..."
python3 -m PyInstaller build_executable.spec

if [ $? -eq 0 ]; then
    echo
    echo "Build successful!"
    echo "Executable location: dist/DICOMTagUpdater"
    echo
else
    echo
    echo "Build failed!"
    echo "Check the error messages above for details."
    exit 1
fi

