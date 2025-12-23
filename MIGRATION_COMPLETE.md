# Flat Structure Migration Complete

## Summary

Successfully migrated the project to a **flat structure** matching the setup on your other computer.

## What Was Done

### 1. Moved compass_perf modules to root
- `config.py` - Configuration management
- `data_loader.py` - DICOM file discovery and loading
- `dicom_sender.py` - C-STORE sender with concurrency support
- `metrics.py` - Performance metrics tracking

### 2. Updated imports
- Changed `from .config` to `from config` (absolute imports)
- Updated all test files to import from root instead of `compass_perf.`

### 3. Full framework integration
Tests now use the complete framework with:
- ✅ **C-ECHO ping** - Verify Compass connectivity before sending
- ✅ **Metrics tracking** - Track latency, throughput, error rates
- ✅ **Quality assertions** - Verify error rate < 0%, latency < 5000ms
- ✅ **Fixtures** - Clean pytest integration with proper setup/teardown

## Project Structure

```
dicomAuto/
├── config.py                          # Framework config (moved from compass_perf/)
├── data_loader.py                     # DICOM file loading (moved from compass_perf/)
├── dicom_sender.py                    # C-STORE sender (moved from compass_perf/)
├── metrics.py                         # Performance metrics (moved from compass_perf/)
├── dcmutl.py                          # DICOM utilities
├── dicomsourceeval_send_dicom_cstore.py  # Legacy sender
├── update_dicom_tags.py               # CLI anonymization tool
├── tests/
│   ├── conftest.py                    # Pytest fixtures (updated for flat structure)
│   └── test_anonymize_and_send.py     # Integration tests (updated)
└── dicom_samples/                     # Test DICOM files
```

## How to Run Tests

### Test with sample files:
```bash
python3 -m pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_single_file -v -s
```

### Test with shared drive file:
```bash
export TEST_DICOM_FILE="/path/to/shared/drive/image.dcm"
python3 -m pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_from_shared_drive -v -s
```

### Windows (UNC path):
```cmd
set TEST_DICOM_FILE=\\\\server\\share\\folder\\image.dcm
python -m pytest tests/test_anonymize_and_send.py -v -s
```

## Configuration (.env file)

```bash
# Compass server
COMPASS_HOST=129.176.169.25
COMPASS_PORT=11112
COMPASS_AE_TITLE=COMPASS
LOCAL_AE_TITLE=TEST_SENDER

# Test data
DICOM_ROOT_DIR=./dicom_samples
TEST_DICOM_FILE=/path/to/shared/drive/image.dcm

# Performance thresholds
MAX_ERROR_RATE=0.02
MAX_P95_LATENCY_MS=2000
```

## Test Features

### test_anonymize_and_send_single_file
1. Takes first file from `DICOM_ROOT_DIR`
2. Anonymizes it (removes PHI, generates new UIDs)
3. **Pings Compass server (C-ECHO)**
4. Sends via C-STORE using framework sender
5. **Tracks metrics** (latency, throughput, errors)
6. **Verifies quality**:
   - Error rate = 0%
   - Latency < 5000ms
   - Exactly 1 file sent successfully

### test_anonymize_and_send_from_shared_drive
1. Reads file from `TEST_DICOM_FILE` environment variable
2. Anonymizes it
3. **Pings Compass server (C-ECHO)**
4. Sends via C-STORE
5. **Tracks and verifies metrics**

## Commits

1. `5662090` - Initial test implementation
2. `5231a8b` - Updated for flat structure (simplified fixtures)
3. `8659266` - Removed compass_perf dependent tests
4. `9ee2c99` - **Moved compass_perf modules to root (THIS COMMIT)**

## Benefits

✅ Works on both computers (same flat structure)  
✅ Full framework capabilities (metrics, C-ECHO, concurrency support)  
✅ Clean pytest integration with fixtures  
✅ Configuration via environment variables or .env file  
✅ Compatible with Windows UNC paths  
✅ Detailed metrics and quality verification  

## Note

The `compass_perf/` directory still exists but its contents have been duplicated to the root.
You can delete `compass_perf/` if desired (it's no longer used).

To delete it:
```bash
git rm -r compass_perf/
git commit -m "Remove empty compass_perf directory"
git push origin main
```

