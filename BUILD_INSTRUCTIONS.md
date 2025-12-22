# Building Executable Version

This branch contains the executable version of `update_dicom_tags.py`.

## Prerequisites

1. Python 3.7 or higher
2. PyInstaller: `pip install pyinstaller`
3. All dependencies from `requirements.txt`

## Building the Executable

### Windows

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable using the spec file
pyinstaller build_executable.spec

# The executable will be in: dist/DICOMTagUpdater.exe
```

### Alternative: One-line build

```bash
pyinstaller --onefile --console --name "DICOMTagUpdater" --add-data "dcmutl.py;." update_dicom_tags.py
```

### macOS/Linux

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller build_executable.spec

# The executable will be in: dist/DICOMTagUpdater (or dist/DICOMTagUpdater.exe on Windows)
```

## Usage

After building, you can run the executable directly:

### Windows
```cmd
DICOMTagUpdater.exe "X:\TEST\Test Data\Data"
DICOMTagUpdater.exe "X:\TEST\Test Data\Data" --verbose
DICOMTagUpdater.exe "X:\TEST\Test Data\Data" --dry-run
```

### macOS/Linux
```bash
./DICOMTagUpdater "/path/to/dicom/folder"
./DICOMTagUpdater "/path/to/dicom/folder" --verbose
./DICOMTagUpdater "/path/to/dicom/folder" --dry-run
```

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
```bash
pyinstaller --onefile --console --name "DICOMTagUpdater" --icon=icon.ico --add-data "dcmutl.py;." update_dicom_tags.py
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

