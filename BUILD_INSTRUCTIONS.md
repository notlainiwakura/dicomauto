# Building Executable Version

This branch contains the executable version of `update_dicom_tags.py`.

## Prerequisites

1. Python 3.7 or higher
2. PyInstaller: `pip install pyinstaller`
3. All dependencies from `requirements.txt`

## Building the Executable

### Windows

**Option 1: Using the build script (Recommended)**
```cmd
build.bat
```

**Option 2: Manual build**
```cmd
# Install PyInstaller
python -m pip install pyinstaller

# Build executable using the spec file
python -m PyInstaller build_executable.spec

# The executable will be in: dist/DICOMTagUpdater.exe
```

**Note**: Use `python -m PyInstaller` instead of just `pyinstaller` if the command is not recognized.

### Alternative: One-line build (Recommended if spec file fails)

**For GUI version (Windows):**
```cmd
python -m PyInstaller --onefile --windowed --name "DICOMTagUpdater" --add-data "dcmutl.py;." update_dicom_tags_gui.py
```

**For CLI version (Windows):**
```cmd
python -m PyInstaller --onefile --console --name "DICOMTagUpdater" --add-data "dcmutl.py;." update_dicom_tags.py
```

**For macOS/Linux (use : instead of ;):**
```bash
python3 -m PyInstaller --onefile --windowed --name "DICOMTagUpdater" --add-data "dcmutl.py:." update_dicom_tags_gui.py
```

### macOS/Linux

**Option 1: Using the build script (Recommended)**
```bash
./build.sh
```

**Option 2: Manual build**
```bash
# Install PyInstaller
python3 -m pip install pyinstaller

# Build executable
python3 -m PyInstaller build_executable.spec

# The executable will be in: dist/DICOMTagUpdater
```

**Note**: Use `python3 -m PyInstaller` instead of just `pyinstaller` if the command is not recognized.

## Usage

After building, you can run the executable directly. The GUI version will open automatically:

### Windows
```cmd
DICOMTagUpdater.exe
```

The GUI will allow you to:
- Browse and select a DICOM file or folder
- Edit tag values (defaults are preselected)
- Process files with progress indication
- View output and results

### Features
- **File/Folder Selection**: Choose either a single DICOM file or a folder containing multiple DICOM files
- **Editable Tag Values**: All tag values are preselected with defaults but can be edited:
  - Patient ID: `11043207`
  - Patient Name: `ZZTESTPATIENT^MIDIA THREE`
  - Patient Birth Date: `19010101`
  - Institution Name: `TEST FACILITY`
  - Referring Physician Name: `TEST PROVIDER`
- **Automatic Unique Values**: StudyInstanceUID, AccessionNumber, and SeriesInstanceUID are automatically generated with unique timestamp-based values
- **Progress Tracking**: Real-time progress updates and output log

## Building Options

### Single File Executable (Recommended)
- **Pros**: Single file, easy to distribute
- **Cons**: Slower startup time
- Command: `pyinstaller --onefile build_executable.spec`

### Directory Distribution
- **Pros**: Faster startup
- **Cons**: Multiple files to distribute
- Command: `pyinstaller --onedir build_executable.spec`

### With Icon (Windows)
```cmd
python -m PyInstaller --onefile --console --name "DICOMTagUpdater" --icon=icon.ico --add-data "dcmutl.py;." update_dicom_tags.py
```

## Troubleshooting

### Import Errors
If you get import errors, add missing modules to `hiddenimports` in `build_executable.spec`:
```python
hiddenimports=['pydicom', 'dcmutl', 'missing_module'],
```

### Missing dcmutl.py
Ensure `dcmutl.py` is in the same directory as `update_dicom_tags.py` when building.

### File Not Found Errors
The executable needs `dcmutl.py` to be included. The spec file includes it in the `datas` section.

## Distribution

After building:
1. Test the executable on a clean system (without Python installed)
2. Include `dcmutl.py` if using `--onedir` mode
3. Provide usage instructions to end users

