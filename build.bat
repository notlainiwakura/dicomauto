@echo off
REM Windows batch script to build the executable

echo Building DICOM Tag Updater executable...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

echo.
echo Building executable...
pyinstaller build_executable.spec

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable location: dist\DICOMTagUpdater.exe
echo.
pause

