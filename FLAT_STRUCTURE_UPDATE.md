# Updated Test Implementation - Flat Structure

## Changes Made

The test suite has been updated to work with a **flat project structure** (without the `compass_perf` module).

### Files Modified

1. **`tests/conftest.py`** - Simplified fixtures for flat structure
2. **`tests/test_anonymize_and_send.py`** - Updated to use new fixtures

### New Fixtures (conftest.py)

```python
@pytest.fixture(scope="session")
def compass_config()
    # Returns dict with Compass server configuration from environment

@pytest.fixture(scope="session")
def dicom_root_dir()
    # Returns Path to DICOM samples directory

@pytest.fixture(scope="session")
def dicom_files(dicom_root_dir)
    # Returns list of DICOM files using dcmutl.get_dcm_files()

@pytest.fixture
def send_dicom_func()
    # Returns the send_dicom function from dicomsourceeval_send_dicom_cstore
```

### Test Functions

Both tests now use the new fixtures:

1. **`test_anonymize_and_send_single_file`**
   - Uses: `temp_anonymized_file`, `compass_config`, `send_dicom_func`
   - Anonymizes a sample file from `dicom_samples/`
   - Sends to Compass server
   - Verifies successful transmission

2. **`test_anonymize_and_send_from_shared_drive`**
   - Uses: `compass_config`, `send_dicom_func`
   - Reads file from `TEST_DICOM_FILE` environment variable
   - Anonymizes it
   - Sends to Compass server

## How to Run

### Basic test with sample files:
```bash
cd /Users/apopo0308/IdeaProjects/dicomAuto
python3 -m pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_single_file -v -s
```

### Test with shared drive file:
```bash
export TEST_DICOM_FILE="/path/to/shared/drive/image.dcm"
python3 -m pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_from_shared_drive -v -s
```

### Windows (Command Prompt):
```cmd
set TEST_DICOM_FILE=\\server\share\folder\image.dcm
python -m pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_from_shared_drive -v -s
```

### Windows (.env file - Recommended):
Create `.env` file:
```bash
TEST_DICOM_FILE=//server/share/folder/image.dcm
COMPASS_HOST=129.176.169.25
COMPASS_PORT=11112
DICOM_ROOT_DIR=./dicom_samples
```

Then run:
```cmd
python -m pytest tests/test_anonymize_and_send.py -v -s
```

## Configuration

All configuration comes from environment variables or `.env` file:

- `COMPASS_HOST` - Compass server hostname (default: 129.176.169.25)
- `COMPASS_PORT` - Compass server port (default: 11112)
- `COMPASS_AE_TITLE` - Compass AE title (default: COMPASS)
- `LOCAL_AE_TITLE` - Local AE title (default: TEST_SENDER)
- `DICOM_ROOT_DIR` - Directory with sample files (default: ./dicom_samples)
- `TEST_DICOM_FILE` - Specific file from shared drive (no default)

## Dependencies

The tests now depend on your existing project modules:
- `dcmutl.get_dcm_files()` - Find DICOM files
- `dicomsourceeval_send_dicom_cstore.send_dicom()` - Send files to Compass

## Benefits

✅ Works with flat project structure (no compass_perf module needed)  
✅ Uses pytest fixtures for clean test organization  
✅ Configuration via environment variables or .env file  
✅ Integrates with existing project code  
✅ No external framework dependencies  
✅ Compatible with Windows network shares (UNC paths)  

## Verification

Tests collected successfully:
```
collected 2 items
  test_anonymize_and_send_single_file
  test_anonymize_and_send_from_shared_drive[TEST_DICOM_FILE]
```

No linting errors found.

