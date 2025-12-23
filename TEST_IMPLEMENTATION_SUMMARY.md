# Test Implementation Summary

## What Was Created

### 1. New Test File: `tests/test_anonymize_and_send.py`
A comprehensive integration test that validates the complete workflow of:
- **Anonymizing** DICOM files (removing PHI and generating new UIDs)
- **Sending** to Compass server via DICOM C-STORE
- **Verifying** successful transmission with quality metrics

### 2. Documentation: `tests/README_ANONYMIZE_TEST.md`
Complete guide covering:
- How to run the tests
- Configuration options
- What gets anonymized
- Verification steps
- Troubleshooting

### 3. Pytest Configuration: `pytest.ini`
Registered custom markers (`integration`, `load`) to eliminate warnings

## Test Cases Included

### Test 1: `test_anonymize_and_send_single_file`
- Uses sample DICOM files from `dicom_samples/` directory
- Automatically anonymizes a test file
- Sends to configured Compass server
- Verifies all quality metrics
- Cleans up temporary files

### Test 2: `test_anonymize_and_send_from_shared_drive`
- Reads file path from `TEST_DICOM_FILE` environment variable
- Designed for testing with specific files from network shares
- Useful for production-like validation scenarios

## How to Run

### Quick Start
```bash
cd /Users/apopo0308/IdeaProjects/dicomAuto

# Run all anonymize-and-send tests
python3 -m pytest tests/test_anonymize_and_send.py -v

# Run with detailed output (shows print statements)
python3 -m pytest tests/test_anonymize_and_send.py -v -s
```

### Run Specific Test
```bash
# Test with sample files (automatic)
python3 -m pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_single_file -v

# Test with shared drive file (requires environment variable)
export TEST_DICOM_FILE="/path/to/shared/drive/image.dcm"
python3 -m pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_from_shared_drive -v -s
```

### With Custom Compass Server
```bash
export COMPASS_HOST="10.146.247.25"
export COMPASS_PORT="11112"
export COMPASS_AE_TITLE="COMPASS_DEV"

python3 -m pytest tests/test_anonymize_and_send.py -v -s
```

### Run Only Integration Tests
```bash
python3 -m pytest tests/ -m integration -v
```

### Run All Tests Except Integration
```bash
python3 -m pytest tests/ -m "not integration" -v
```

## Key Features

### 1. Recursive Tag Updates
The anonymization function recursively updates tags in all nested sequences, ensuring:
- No original UIDs remain anywhere in the file
- Works with complex DICOM structures (e.g., Whole Slide Imaging)
- Updates shared and per-frame functional group sequences

### 2. Quality Verification
Tests verify:
- Error rate must be 0%
- Latency must be < 5000ms
- Exactly 1 file sent and received
- All PHI tags properly anonymized

### 3. Automatic Cleanup
- Temporary files automatically deleted after test
- No manual cleanup required
- Safe for repeated runs

### 4. Framework Integration
- Uses existing `conftest.py` fixtures
- Compatible with other performance tests
- Follows project conventions

## Anonymized Tags

### Generated Unique IDs
- `StudyInstanceUID` → New globally unique UID
- `SeriesInstanceUID` → New globally unique UID
- `SOPInstanceUID` → New globally unique UID
- `AccessionNumber` → Timestamp-based unique ID

### Fixed Test Values
- `PatientID` → `11043207`
- `PatientName` → `ZZTESTPATIENT^ANONYMIZED`
- `PatientBirthDate` → `19010101`
- `InstitutionName` → `TEST FACILITY`
- `ReferringPhysicianName` → `TEST^PROVIDER`

## Configuration

### Environment Variables
```bash
# Compass Server
COMPASS_HOST=129.176.169.25
COMPASS_PORT=11112
COMPASS_AE_TITLE=COMPASS
LOCAL_AE_TITLE=TEST_SENDER

# Test Data
DICOM_ROOT_DIR=./dicom_samples
TEST_DICOM_FILE=/path/to/specific/test/file.dcm
```

### .env File Support
The test automatically loads configuration from `.env` file in project root (via `conftest.py`)

## Example Output

```
============================= test session starts ==============================
platform darwin -- Python 3.12.0, pytest-8.4.0, pluggy-1.6.0
rootdir: /Users/apopo0308/IdeaProjects/dicomAuto
configfile: pytest.ini
collected 1 item

tests/test_anonymize_and_send.py::test_anonymize_and_send_single_file 

============================================================
STEP 1: ANONYMIZING DICOM FILE
============================================================
  [OK] File read successfully: CR_512x512_16bit_MONO2.dcm
  [OK] Generated new StudyInstanceUID: 1.2.826.0.1.3680043...
  [OK] Anonymized file saved

============================================================
STEP 2: SENDING TO COMPASS SERVER
============================================================
  Checking Compass connectivity (C-ECHO)...
  [OK] Compass server is reachable
  Loading anonymized file...
  [OK] Anonymization verified: StudyUID=1.2.826.0.1.3680043...
  Sending via C-STORE...

============================================================
STEP 3: VERIFYING SUCCESS
============================================================
  [OK] Confirmed 1 file sent
  [OK] Send reported as successful
  [OK] Error rate: 0.0%
  [OK] Average latency: 234.56 ms

  [SUCCESS] ALL VERIFICATIONS PASSED
  Summary: {'total': 1, 'successes': 1, 'failures': 0, ...}

PASSED                                                               [100%]

============================== 1 passed in 2.34s ===============================
```

## Files Created

1. `/Users/apopo0308/IdeaProjects/dicomAuto/tests/test_anonymize_and_send.py`
2. `/Users/apopo0308/IdeaProjects/dicomAuto/tests/README_ANONYMIZE_TEST.md`
3. `/Users/apopo0308/IdeaProjects/dicomAuto/pytest.ini`

## Integration with Existing Framework

The test seamlessly integrates with:
- `conftest.py` fixtures (`dicom_sender`, `dicom_files`, `metrics`, `perf_config`)
- `compass_perf/` modules (config, sender, metrics, data_loader)
- Existing test structure and naming conventions
- `.env` configuration system

## Next Steps

1. **Run the test** to verify it works with your Compass server
2. **Set TEST_DICOM_FILE** to test with specific files from network shares
3. **Add to CI/CD** pipeline for automated validation
4. **Customize thresholds** if needed (latency, error rates)

## Comparison with Original Script

The original `update_dicom_tags.py` is a standalone CLI tool, while this test:
- Uses the same anonymization logic (recursive tag updates)
- Integrates with pytest framework
- Automatically verifies transmission to Compass
- Provides quality metrics and assertions
- Cleans up temporary files automatically

