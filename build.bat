@echo off
REM Windows batch script to build the executable

echo Building DICOM Tag Updater executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher and try again.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install PyInstaller
        echo Please run manually: python -m pip install pyinstaller
        pause
        exit /b 1
    )
)

echo.
echo Building executable...
python -m PyInstaller build_executable.spec

if errorlevel 1 (
    echo.
    echo Build failed!
    echo Check the error messages above for details.
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable location: dist\DICOMTagUpdater.exe
echo.
pause

