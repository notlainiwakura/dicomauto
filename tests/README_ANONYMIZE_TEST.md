# Anonymize and Send Integration Test

## Overview

The `test_anonymize_and_send.py` test validates the complete end-to-end workflow of:
1. **Anonymizing** a non-anonymized DICOM file (removing PHI)
2. **Sending** it to the Compass server via DICOM C-STORE
3. **Verifying** successful transmission with quality metrics

## Test Structure

### Test 1: `test_anonymize_and_send_single_file`
- Uses sample DICOM files from the configured `DICOM_ROOT_DIR`
- Automatically creates and cleans up temporary anonymized files
- Validates all steps including latency and error rates

### Test 2: `test_anonymize_and_send_from_shared_drive`
- Designed for testing with specific files from network shares
- Requires setting the `TEST_DICOM_FILE` environment variable
- Useful for validating production-like scenarios

## Running the Tests

### Basic Usage

Run all anonymize-and-send tests:
```bash
cd /Users/apopo0308/IdeaProjects/dicomAuto
pytest tests/test_anonymize_and_send.py -v
```

### Run Specific Test

```bash
# Test with sample files
pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_single_file -v

# Test with shared drive file
pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_from_shared_drive -v
```

### Using a File from Shared Drive

```bash
# Set environment variable pointing to your test file
export TEST_DICOM_FILE="/path/to/shared/drive/image.dcm"

# Or for Windows network path:
export TEST_DICOM_FILE="//server/share/images/test.dcm"

# Run the test
pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_from_shared_drive -v -s
```

### With Custom Compass Configuration

```bash
export COMPASS_HOST="10.146.247.25"
export COMPASS_PORT="11112"
export COMPASS_AE_TITLE="COMPASS_DEV"
export TEST_DICOM_FILE="/mnt/shared/test_image.dcm"

pytest tests/test_anonymize_and_send.py -v -s
```

## Configuration

### Via Environment Variables

```bash
# Compass server settings
export COMPASS_HOST="129.176.169.25"
export COMPASS_PORT="11112"
export COMPASS_AE_TITLE="COMPASS"

# Test data location
export DICOM_ROOT_DIR="./dicom_samples"
export TEST_DICOM_FILE="/path/to/specific/test/file.dcm"
```

### Via .env File

Create a `.env` file in the project root:

```bash
# .env
COMPASS_HOST=129.176.169.25
COMPASS_PORT=11112
COMPASS_AE_TITLE=COMPASS
LOCAL_AE_TITLE=TEST_SENDER
DICOM_ROOT_DIR=./dicom_samples

# For shared drive testing
TEST_DICOM_FILE=/mnt/shared/dicom/test_image.dcm
```

## What Gets Anonymized

The test anonymizes the following DICOM tags:

### Unique Identifiers (Generated)
- **StudyInstanceUID** - New globally unique ID
- **SeriesInstanceUID** - New globally unique ID
- **SOPInstanceUID** - New globally unique ID
- **AccessionNumber** - Timestamp-based unique number

### Patient Demographics (Fixed Values)
- **PatientID** → `11043207`
- **PatientName** → `ZZTESTPATIENT^ANONYMIZED`
- **PatientBirthDate** → `19010101`

### Institutional Information
- **InstitutionName** → `TEST FACILITY`
- **ReferringPhysicianName** → `TEST^PROVIDER`

### Nested Sequences
The anonymization function recursively updates tags in all nested sequences (e.g., `SharedFunctionalGroupsSequence`, `PerFrameFunctionalGroupsSequence`), ensuring no original identifiers remain anywhere in the file.

## Verification Steps

The test performs the following verifications:

1. **Anonymization Check**
   - Confirms new UIDs were generated and applied
   - Validates PHI tags are replaced with test values

2. **Connectivity Check**
   - C-ECHO ping to verify Compass is reachable
   - Fails early if server is unavailable

3. **Transmission Check**
   - Confirms exactly 1 file was sent
   - Validates C-STORE completed successfully

4. **Quality Metrics**
   - Error rate must be 0%
   - Latency must be < 5000ms
   - All samples must report success

## Expected Output

```
============================================================
STEP 1: ANONYMIZING DICOM FILE
============================================================
  [OK] File read successfully: CR_512x512_16bit_MONO2.dcm
  [OK] Generated new StudyInstanceUID: 1.2.826.0.1.3680043.8.498...
  [OK] Anonymized file saved

============================================================
STEP 2: SENDING TO COMPASS SERVER
============================================================
  Checking Compass connectivity (C-ECHO)...
  [OK] Compass server is reachable
  Loading anonymized file...
  [OK] Anonymization verified: StudyUID=1.2.826.0.1.3680043.8.498...
  Sending via C-STORE...

============================================================
STEP 3: VERIFYING SUCCESS
============================================================
  [OK] Confirmed 1 file sent
  [OK] Send reported as successful
  [OK] Error rate: 0.0%
  [OK] Average latency: 234.56 ms

  [SUCCESS] ALL VERIFICATIONS PASSED
  Summary: {'total': 1, 'successes': 1, 'failures': 0, 'error_rate': 0.0, ...}

PASSED
```

## Integration with CI/CD

This test can be integrated into automated pipelines:

```bash
# Run as part of integration test suite
pytest tests/test_anonymize_and_send.py -v --junitxml=results.xml

# Or run all integration tests
pytest tests/ -m integration -v
```

## Troubleshooting

### Test Skipped: "No DICOM files available"
- Ensure `DICOM_ROOT_DIR` points to a directory with .dcm files
- Check that the path exists and contains valid DICOM files

### Test Skipped: "Environment variable TEST_DICOM_FILE not set"
- For the shared drive test, you must set the environment variable
- Use `export TEST_DICOM_FILE=/path/to/file.dcm` before running

### Assertion Failed: "Compass did not respond to C-ECHO ping"
- Verify Compass server is running and accessible
- Check network connectivity and firewall rules
- Confirm `COMPASS_HOST` and `COMPASS_PORT` are correct

### Assertion Failed: "Latency exceeds threshold"
- Review network conditions between test machine and Compass
- Check Compass server load
- Consider adjusting the 5000ms threshold if needed

## See Also

- `tests/test_load_stability.py` - Load testing with sustained throughput
- `tests/test_routing_throughput.py` - Throughput and routing tests
- `update_dicom_tags.py` - Standalone CLI tool for anonymization
- `compass_perf/` - Performance testing framework modules

