# Troubleshooting: "No module named 'config'" Error

## Problem
When running tests, you get:
```
ImportError: No module named 'config'
```

## Root Cause
The required Python modules (`config.py`, `metrics.py`, etc.) are not in your project root directory.

## Solution

### Step 1: Check Your Location
Make sure you're in the project root:
```bash
cd /path/to/dicomAuto
pwd  # Should show: /path/to/dicomAuto
```

### Step 2: Pull Latest Changes
```bash
git pull origin main
```

This will download:
- `config.py`
- `data_loader.py`
- `dicom_sender.py`
- `metrics.py`
- Updated `tests/conftest.py` with path fixes

### Step 3: Run Diagnostic Script
```bash
python3 check_structure.py
```

This will show you:
- ✓ Which files are present
- ✗ Which files are missing
- Whether imports work correctly

### Step 4: Verify Structure
Your project should look like:
```
dicomAuto/
├── config.py                    ← Must be in root
├── data_loader.py               ← Must be in root
├── dicom_sender.py              ← Must be in root
├── metrics.py                   ← Must be in root
├── dcmutl.py
├── dicomsourceeval_send_dicom_cstore.py
├── update_dicom_tags.py
├── tests/
│   ├── conftest.py
│   ├── test_anonymize_and_send.py
│   ├── test_load_stability.py
│   └── test_routing_throughput.py
└── dicom_samples/
```

### Step 5: Run Tests
```bash
# From project root
python3 -m pytest tests/ -v

# Or from tests directory
cd tests
python3 -m pytest -v
```

## Common Issues

### Issue 1: Files in Wrong Location
**Problem:** You have a `compass_perf/` directory but modules aren't in root.

**Solution:**
```bash
# Copy modules to root
cp compass_perf/config.py .
cp compass_perf/data_loader.py .
cp compass_perf/dicom_sender.py .
cp compass_perf/metrics.py .

# Fix imports in dicom_sender.py
# Change: from .config import PerfConfig
# To:     from config import PerfConfig
```

### Issue 2: Running from Wrong Directory
**Problem:** Running pytest from somewhere other than project root.

**Solution:** Always run from project root:
```bash
cd /path/to/dicomAuto
python3 -m pytest tests/
```

### Issue 3: Python Can't Find Modules
**Problem:** Python path doesn't include project root.

**Solution:** The `tests/conftest.py` now automatically adds project root to path:
```python
# This is already in conftest.py (latest version)
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

Make sure you have the latest `conftest.py`:
```bash
git pull origin main
```

## Still Having Issues?

Run the diagnostic and share the output:
```bash
python3 check_structure.py > structure_check.txt
cat structure_check.txt
```

## Quick Fix Commands

```bash
# 1. Navigate to project
cd /path/to/dicomAuto

# 2. Pull latest
git pull origin main

# 3. Check structure
python3 check_structure.py

# 4. Run tests
python3 -m pytest tests/ -v
```

## Windows-Specific Notes

On Windows, use:
```cmd
cd C:\path\to\dicomAuto
git pull origin main
python check_structure.py
python -m pytest tests/ -v
```

Make sure Python is in your PATH:
```cmd
python --version
```

If not found, use full path:
```cmd
C:\Python312\python.exe -m pytest tests/ -v
```

