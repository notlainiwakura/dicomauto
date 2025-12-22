# Distribution Guide for DICOM Tag Updater Executable

## Can I Share Just the .exe File?

**Yes!** When built with PyInstaller using the provided `build_executable.spec`, the executable is **standalone** and includes all dependencies.

## What's Included in the Executable

The `.exe` file contains:
- ✅ All Python dependencies (pydicom, etc.)
- ✅ The GUI application code
- ✅ The `dcmutl.py` module (embedded)
- ✅ All required libraries

## Distribution Requirements

### Single File Distribution (Recommended)

**What to share:**
- Just `DICOMTagUpdater.exe` - that's it!

**Requirements for end users:**
- Windows 7 or later
- No Python installation needed
- No additional files needed

### Testing Before Distribution

1. **Test on a clean Windows machine** (without Python installed)
2. **Test with both single file and folder** selection
3. **Verify all tags are updated correctly**

## File Size

The executable will be approximately:
- **20-50 MB** (includes Python runtime and all dependencies)
- This is normal for PyInstaller executables

## Distribution Methods

### Option 1: Direct Share
- Share `DICOMTagUpdater.exe` via:
  - Email attachment
  - Network share
  - USB drive
  - Cloud storage (OneDrive, Google Drive, etc.)

### Option 2: ZIP Archive
- Create a ZIP file containing:
  - `DICOMTagUpdater.exe`
  - `README.txt` (usage instructions)
- Share the ZIP file

### Option 3: Installer (Advanced)
- Use Inno Setup or NSIS to create an installer
- Provides professional installation experience

## Usage Instructions for End Users

Create a simple `README.txt` to include:

```
DICOM Tag Updater
=================

1. Double-click DICOMTagUpdater.exe to start

2. Click "Browse File..." to select a single DICOM file
   OR
   Click "Browse Folder..." to select a folder containing DICOM files

3. (Optional) Edit the tag values if needed:
   - Patient ID
   - Patient Name
   - Patient Birth Date
   - Institution Name
   - Referring Physician Name

4. Click "Process DICOM Files"

5. Wait for processing to complete

6. Check the output log for results

Note: StudyInstanceUID, AccessionNumber, and SeriesInstanceUID
are automatically generated with unique values.
```

## Troubleshooting for End Users

### "Windows protected your PC" Warning
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- Or: Right-click → Properties → Unblock → OK

### Antivirus False Positives
- Some antivirus software may flag PyInstaller executables
- This is a known issue with PyInstaller
- Solution: Add exception or use code signing (advanced)

### File Won't Run
- Ensure Windows 7 or later
- Try running as Administrator
- Check Windows Event Viewer for errors

## Building for Distribution

```cmd
# Build the executable
python -m PyInstaller build_executable.spec

# Test it
dist\DICOMTagUpdater.exe

# Share dist\DICOMTagUpdater.exe
```

## Important Notes

1. **One executable per OS**: Windows .exe won't work on macOS/Linux
2. **Architecture**: 64-bit Windows executable works on 64-bit Windows
3. **No Python needed**: End users don't need Python installed
4. **Standalone**: Everything is bundled in the .exe file

