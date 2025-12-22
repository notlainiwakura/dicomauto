# Windows Usage Guide for update_dicom_tags.py

## Test Results

The script has been tested and verified to work correctly. A test run successfully updated a DICOM file with:
- ✅ Unique StudyInstanceUID
- ✅ Unique AccessionNumber (timestamp-based)
- ✅ Unique SeriesInstanceUID
- ✅ Test tags (PatientID, PatientName, PatientBirthDate, InstitutionName, ReferringPhysicianName)

## Running on Windows Command Line

### Basic Usage

```cmd
python update_dicom_tags.py "X:\TEST\Test Data\Data"
```

### With Verbose Output (Recommended for troubleshooting)

```cmd
python update_dicom_tags.py "X:\TEST\Test Data\Data" --verbose
```

### Dry Run (Preview changes without modifying files)

```cmd
python update_dicom_tags.py "X:\TEST\Test Data\Data" --dry-run
```

### Important Notes for Windows Paths

1. **Always use quotes** around paths with spaces:
   ```cmd
   "X:\TEST\Test Data\Data"
   ```

2. **Trailing backslash is optional**:
   ```cmd
   "X:\TEST\Test Data\Data"     ✓ Works
   "X:\TEST\Test Data\Data\"    ✓ Also works
   ```

3. **Forward slashes also work**:
   ```cmd
   python update_dicom_tags.py "X:/TEST/Test Data/Data"
   ```

4. **UNC paths work too**:
   ```cmd
   python update_dicom_tags.py "\\server\share\TEST\Test Data\Data"
   ```

## Troubleshooting: Script Runs But No Updates

If the script runs but doesn't update files, check the following:

### 1. Check Script Output

Run with `--verbose` flag to see detailed information:
```cmd
python update_dicom_tags.py "X:\TEST\Test Data\Data" --verbose
```

Look for:
- "Found X DICOM file(s) to process" - confirms files were found
- "[1/X] Processing: filename.dcm" - shows each file being processed
- "Verification: All verifications passed" - confirms updates worked

### 2. Verify Files Are Actually DICOM Files

The script only processes files with `.dcm` or `.dicom` extensions. Check:
- Are your files actually `.dcm` files?
- Are they in subdirectories? (script searches recursively)

### 3. Check File Permissions

On network drives, ensure:
- You have **write permissions** to the folder
- Files are not **read-only**
- Network connection is stable

To check file permissions:
```cmd
attrib "X:\TEST\Test Data\Data\*.dcm"
```

If files are read-only, remove the attribute:
```cmd
attrib -R "X:\TEST\Test Data\Data\*.dcm"
```

### 4. Test with a Single File First

Create a test folder with one DICOM file:
```cmd
mkdir C:\test_dicom
copy "X:\TEST\Test Data\Data\sample.dcm" C:\test_dicom\
python update_dicom_tags.py C:\test_dicom --verbose
```

### 5. Check for Hidden Errors

The script should print errors, but check:
- Are files being skipped silently?
- Are there permission errors?
- Is the path correct?

### 6. Verify Network Drive is Mapped

Ensure the network drive is properly mapped:
```cmd
net use X:
```

If not mapped, map it:
```cmd
net use X: \\server\share
```

### 7. Check Script Can Write to Files

Test write permissions:
```cmd
echo test > "X:\TEST\Test Data\Data\test.txt"
del "X:\TEST\Test Data\Data\test.txt"
```

If this fails, you don't have write permissions.

## Expected Output

When working correctly, you should see:

```
Processing folder: X:\TEST\Test Data\Data
Absolute path: X:\TEST\Test Data\Data
Found 5 DICOM file(s) to process

[1/5] Processing: file1.dcm
  Full path: X:\TEST\Test Data\Data\file1.dcm
  Original StudyInstanceUID: 1.2.826.0.1.3680043.8.498.123456789
  New StudyInstanceUID: 1.2.826.0.1.3680043.8.498.987654321
  Original AccessionNumber: None
  New AccessionNumber: 20251222-120000-123456
  Verification: All verifications passed

[2/5] Processing: file2.dcm
...

============================================================
SUMMARY
============================================================
Total files processed: 5
Successfully updated: 5
Failed: 0
Verification failed: 0
============================================================
```

## Common Issues and Solutions

### Issue: "No DICOM files found in folder"

**Solutions:**
- Verify files have `.dcm` or `.dicom` extension
- Check the path is correct
- Use `--verbose` to see what files are in the directory
- Ensure you're pointing to the correct folder

### Issue: "Folder does not exist"

**Solutions:**
- Check the path spelling
- Verify the network drive is mapped
- Try using UNC path instead: `\\server\share\path`
- Check if path has trailing backslash issues

### Issue: Files found but not updated

**Solutions:**
- Check file permissions (not read-only)
- Check network connection
- Verify you have write access
- Try with `--dry-run` first to see what would happen

### Issue: "Verification failed"

**Solutions:**
- File might be corrupted
- File might be locked by another process
- Check disk space
- Try processing one file at a time

## Example: Complete Workflow

```cmd
REM 1. Navigate to script directory
cd C:\path\to\dicomAuto

REM 2. Test with dry-run first
python update_dicom_tags.py "X:\TEST\Test Data\Data" --dry-run --verbose

REM 3. If dry-run looks good, run for real
python update_dicom_tags.py "X:\TEST\Test Data\Data" --verbose

REM 4. Verify a file was updated
python -c "from pydicom import dcmread; ds = dcmread('X:/TEST/Test Data/Data/sample.dcm'); print('PatientID:', ds.PatientID); print('AccessionNumber:', ds.AccessionNumber)"
```

## Getting Help

If the script still doesn't work:
1. Run with `--verbose` flag and save output
2. Check file permissions
3. Test with a local folder first
4. Verify Python and pydicom are installed correctly

