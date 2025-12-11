# Compass Performance / Load Testing Suite

This project implements a pytest-based performance and load testing suite for Laurel Bridge Compass, aligned with the "UltraRAD to Compass Routing Migration" test plan.

## Contents

- `0_dcm_read_studyids.py`: **Original cataloging script** - One of the first tools created for this project. Scans DICOM directories and creates CSV catalogs with Study/Series Instance UIDs and metadata. Useful for understanding dataset structure before running performance tests.
- `1_dicomsourceval_setup_studies.py`: **Study organization script** - Early script that reads the CSV catalog and organizes DICOM files into folders grouped by Study Instance UID. Useful for preparing datasets in a structured format before testing.
- `2_dicomsourceeval_create_loadtestdata.py`: **Load test data generator** - Early script that transforms organized DICOM datasets into load test data by updating DICOM tags (StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID, DeviceSerialNumber, etc.) and creating multiple test scenarios. Essential for preparing diverse test datasets.
- `BQData.py`: **BigQuery metadata fetcher** - Early script for querying Google BigQuery to fetch DICOM metadata, flatten nested data structures, and export to JSON. Useful for validating metadata and understanding data structures from production databases.
- `dcm_tag_validator_functions.py`: **DICOM tag validation module** - Early validation module providing functions to compare expected DICOM tag values (from Excel/CSV) with actual values (from BigQuery or DICOM files). Validates patient names, birth dates, referring physician names, StudyInstanceUIDs, and SpecimenUIDs. Essential for data quality assurance.
- `dicom_tag_validator.py`: **Automated DICOM tag validator** - Early script that automates the validation workflow by reading Excel files with expected values, fetching actual values from BigQuery, and generating comprehensive validation reports. Integrates BigQuery data fetching and validation functions.
- `dcmtests.py`: **DICOM element extraction utility** - Early testing script for extracting DICOM elements and converting datasets to dictionary structures. Useful for understanding DICOM structure and debugging metadata issues.
- `CountFiles.py`: **File counting utility** - Simple early utility script that counts DICOM files (`.dcm`) across directory trees. Useful for quickly understanding dataset sizes before processing.
- `dcmutl.py`: Utility module for DICOM file operations, used by all the cataloging, organization, load test data generation, and testing scripts.
- `compass_perf/`
  - `config.py`: Configuration model driven by environment variables or `.env`.
  - `data_loader.py`: Discovers and loads DICOM datasets from a directory (evolved from the cataloging approach).
  - `dicom_sender.py`: Uses pynetdicom to send C-STORE requests to Compass.
  - `metrics.py`: Thread-safe metrics collection (latency, throughput, error rate).
- `tests/`
  - `conftest.py`: Global fixtures, automatic `.env` loading, wiring for sender and datasets.
  - `test_load_stability.py`: TS_04-style load stability test at approximately 3x peak.
  - `test_routing_throughput.py`: Throughput tests at 150 and 200 percent of peak.
- `.env`: Example environment configuration.
- `requirements.txt`: Python dependencies.

## Prerequisites

- Python 3.9 or later
- Network connectivity from the test host to the Compass DICOM listener
- A directory containing anonymized or synthetic DICOM files for testing

**Optional for BigQuery scripts:**
- Google Cloud credentials configured (for `BQData.py`)
- Access to the specified BigQuery datasets

Install dependencies:

```bash
pip install -r requirements.txt
```

**Note:** Some early scripts (like `0_dcm_read_studyids.py`, `1_dicomsourceval_setup_studies.py`, `2_dicomsourceeval_create_loadtestdata.py`) also require `pandas`, which should be installed separately if needed:
```bash
pip install pandas
```

## Project History and Workflow

This project evolved from initial DICOM dataset exploration tools. The workflow typically follows:

1. **Catalog existing datasets** (optional): Use `0_dcm_read_studyids.py` to create CSV catalogs of DICOM files, understanding their structure and metadata.
2. **Organize by Study Instance UID** (optional): Use `1_dicomsourceval_setup_studies.py` to organize DICOM files into folders grouped by Study Instance UID, based on the CSV catalog.
3. **Create load test data** (optional): Use `2_dicomsourceeval_create_loadtestdata.py` to transform organized datasets into load test data by updating DICOM tags and creating multiple test scenarios.
4. **Fetch metadata from BigQuery** (optional): Use `BQData.py` to query Google BigQuery for DICOM metadata, validate data structures, and export flattened results to JSON.
5. **Generate test samples**: Use `create_diverse_dicom_samples.py` to create diverse DICOM samples for testing.
6. **Run performance tests**: Use the pytest-based test suite to validate Compass performance.

## Cataloging DICOM Datasets

The original cataloging script (`0_dcm_read_studyids.py`) scans DICOM directories and creates CSV files with metadata:

```bash
# Update paths in the script, then run:
python 0_dcm_read_studyids.py
```

This creates a timestamped CSV file with:
- Source paths and filenames
- Study Instance UIDs
- Series Instance UIDs  
- Directory names
- Custom barcode values (if present)

The CSV output helps understand dataset composition before running performance tests. This script was one of the first tools created for the project and remains useful for dataset analysis.

## Organizing DICOM Files by Study Instance UID

After cataloging DICOM files, you can organize them into folders grouped by Study Instance UID using `1_dicomsourceval_setup_studies.py`:

```bash
# Update paths in the script to point to your catalog CSV and destination folder, then run:
python 1_dicomsourceval_setup_studies.py
```

This script:
- Reads the CSV catalog created by `0_dcm_read_studyids.py`
- Groups files by their Study Instance UID
- Creates a folder for each Study Instance UID
- Copies all files belonging to each study into their respective folders

This organization step was useful for preparing datasets in a structured format before running performance tests. The script was created early in the project workflow, following the cataloging step.

## Creating Load Test Data

After organizing DICOM files, you can transform them into load test data using `2_dicomsourceeval_create_loadtestdata.py`:

```bash
# Update paths in the script to point to your input CSV and image folders, then run:
python 2_dicomsourceeval_create_loadtestdata.py
```

This script:
- Reads an input CSV file with test parameters (BarCodeValue, ContainerIdentifier, StudyInstanceUIDPrefix, SeriesInstanceUIDPrefix, DeviceSerialNumber, LabelText)
- Copies image folders from the organized datasets
- Updates DICOM tags in each file (StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID, DeviceSerialNumber, LabelText, etc.)
- Generates unique identifiers for each study, series, and instance
- Creates metadata files for each processed DICOM file
- Outputs a CSV file with all the generated values for tracking

This transformation step was essential for creating diverse test scenarios with different device serial numbers, barcodes, and UIDs before building the automated performance testing suite. The script was created early in the project workflow, following the organization step.

## Fetching DICOM Metadata from BigQuery

For projects that need to validate metadata against production BigQuery databases, `BQData.py` provides utilities to query and process DICOM metadata:

```bash
# Update the barcode_value in the script, then run:
python BQData.py
```

This script:
- Queries Google BigQuery for DICOM metadata filtered by BarcodeValue
- Automatically selects the appropriate dataset based on barcode prefix (AR prefix vs others)
- Flattens nested dictionary structures for easier analysis
- Exports results to timestamped JSON files with proper date serialization

**Prerequisites:**
- Google Cloud credentials configured (via `GOOGLE_APPLICATION_CREDENTIALS` environment variable or default credentials)
- Access to the BigQuery datasets specified in the script

This script was useful for validating metadata structures and understanding data formats from production databases before building the performance testing suite. It was created early in the project workflow as a data validation tool.

## Validating DICOM Tags

The `dcm_tag_validator_functions.py` module provides validation functions for comparing expected DICOM tag values with actual values from BigQuery or DICOM files:

```python
from dcm_tag_validator_functions import validate_patient_name, validate_patient_birth_date
from BQData import fetch_and_flatten_bigquery_data

# Fetch data from BigQuery
flattened_data = fetch_and_flatten_bigquery_data(barcode_value)

# Validate patient name (expected format: "Family^Given^Middle")
validate_patient_name(flattened_data, "Doe^John^A", detailed_results, error_log, barcode)
```

The module provides validation functions for:
- **Patient Name** - Validates FamilyName, GivenName, and MiddleName components
- **Patient Birth Date** - Normalizes and compares date formats (YYYYMMDD)
- **Referring Physician Name** - Validates all name components including prefix and suffix
- **StudyInstanceUID** - Validates UID prefix matching
- **SpecimenUID** - Validates UID prefix matching
- **Generic tag comparison** - For other DICOM tags

This validation module was created early in the project to ensure data quality and correctness, working with flattened BigQuery data and providing detailed validation results. It was essential for validating metadata before building the performance testing suite.

## Automated DICOM Tag Validation

The `dicom_tag_validator.py` script automates the validation workflow by processing Excel files and generating validation reports:

```bash
# Update paths in the script, then run:
python dicom_tag_validator.py
```

This script:
- Reads Excel files containing expected DICOM tag values
- Processes rows based on barcode values
- Fetches actual values from BigQuery for each barcode
- Validates tags using the validation functions module
- Generates two CSV output files:
  - **High-level results** - Summary with Pass/Fail status per barcode
  - **Detailed results** - Comprehensive validation details for each tag

**Prerequisites:**
- Excel file with expected values (format: "Raw Output Data" sheet, starting at row 3)
- `key_to_column_mapping.json` file in the current directory (maps DICOM tag keys to Excel column indexes)
- Google Cloud credentials configured (for BigQuery access)

This automated validator was created early in the project to streamline the validation process, integrating BigQuery data fetching and validation functions into a single workflow. It was essential for batch validation of DICOM metadata before building the performance testing suite.

## Extracting DICOM Elements

The `dcmtests.py` script provides utilities for extracting DICOM elements and converting datasets to dictionary structures:

```bash
# Update paths in the script, then run:
python dcmtests.py
```

This script:
- Extracts DICOM elements from files in a directory
- Converts DICOM datasets to nested dictionary structures
- Saves extracted elements as JSON files for analysis
- Provides a `ds_to_dict()` function for converting DICOM datasets to dictionaries

This testing utility was created early in the project for understanding DICOM structure and debugging metadata issues. It was useful for examining DICOM elements before building the performance testing suite.

## Counting DICOM Files

For a quick assessment of dataset sizes, `CountFiles.py` provides a simple utility to count DICOM files:

```bash
# Update the path in the script, then run:
python CountFiles.py
```

This script:
- Recursively scans a directory tree for `.dcm` files
- Reports the count of DICOM files in each directory
- Provides a total count across all directories

This simple utility was one of the earliest scripts created for the project, useful for quickly understanding dataset sizes before running more intensive processing operations.

## DICOM Utility Functions (`dcmutl.py`)

The `dcmutl.py` module has been expanded with comprehensive utility functions for DICOM file manipulation:

### Tag Operations
- **`update_tags(dcm_file, tag_name, value)`** - Update a single tag in a DICOM file
- **`update_tags_ds(ds, tag_name, value)`** - Update a tag in a DICOM dataset object
- **`update_tags_all_files(dir, tag_name, value)`** - Update a tag in all files in a directory
- **`add_tags(dcm_file, tag_name, value)`** - Add a new tag to a DICOM file
- **`remove_tags(dcm_file, tag_name)`** - Remove a tag from a DICOM file
- **`get_tag_value(dcm_file, tag_name)`** - Get a tag value from a DICOM file
- **`is_valid_tag(keyword)`** - Check if a DICOM tag keyword is valid

### Specific Tag Updates
- **`update_bar_code_file(dcm_file, new_bar_code)`** - Update barcode value
- **`update_bar_code_all_files(dir, new_bar_code)`** - Update barcode in all files
- **`update_image_type_file(dcm_file, new_image_type)`** - Update ImageType tag
- **`update_dim_org_type(dcm_file, new_dim_org_type)`** - Update DimensionOrganizationType

### De-identification Utilities
- **`get_not_deidentified_list(deid_tags, dcm_file, dest_folder)`** - Check de-identification status of a file
- **`get_not_deidentified_list_dir(deid_tags, dcm_dir, dest_folder)`** - Check de-identification for all files in a directory

### Element Extraction
- **`get_dicom_elements_file(file, dest_folder, attrs=None)`** - Extract elements to text file
- **`get_dicom_elements_file_nested_text(file, dest_folder, attrs=None)`** - Extract nested elements to text
- **`get_dicom_dataset_text(file, dest_folder, metadata_file_name=None)`** - Save dataset as text
- **`extract_all_elements(ds, elements, indent=0, attrs=None, path="")`** - Recursive element extraction helper

These utility functions were developed early in the project and provide comprehensive DICOM file manipulation capabilities for testing, data preparation, and validation tasks.

## Generating Sample DICOM Files

The project includes a script to generate diverse DICOM sample files for comprehensive testing:

```bash
python create_diverse_dicom_samples.py
```

This script creates a comprehensive set of DICOM files in the `dicom_samples/` directory with descriptive filenames that indicate:
- **Modality** (CR, CT, MR, US, PET, MG, NM)
- **Image dimensions** (e.g., 512x512, 2048x2048)
- **Bit depth** (8-bit, 12-bit, 14-bit, 16-bit)
- **Photometric interpretation** (MONO1, MONO2)

Example filenames:
- `CR_512x512_12bit_MONO2.dcm` - Computed Radiography, 512x512, 12-bit, MONOCHROME2
- `CT_512x512_16bit_MONO2.dcm` - CT scan, 512x512, 16-bit, MONOCHROME2
- `MR_256x256_16bit_MONO1.dcm` - MRI, 256x256, 16-bit, MONOCHROME1 (inverted)
- `US_512x512_8bit_MONO2.dcm` - Ultrasound, 512x512, 8-bit
- `PET_128x128_16bit_MONO2.dcm` - PET scan, 128x128, 16-bit

The script generates files covering:
- 7 different modalities (CR, CT, MR, US, PET, MG, NM)
- Multiple image sizes (from 128x128 to 4096x4096)
- Different bit depths (8, 12, 14, 16 bits)
- Both MONOCHROME1 and MONOCHROME2 photometric interpretations
- Different patient IDs for routing tests
- Small and large file variants for performance testing

Note: The `dicom_samples/` directory is excluded from git (see `.gitignore`).

## Configuration

The suite reads configuration primarily from environment variables or from the `.env` file in the project root.

Key variables:

- `COMPASS_HOST`: Hostname or IP of the Compass DICOM listener.
- `COMPASS_PORT`: DICOM port (for example, 11112).
- `COMPASS_AE_TITLE`: AE Title of Compass.
- `LOCAL_AE_TITLE`: AE Title used by the load generator (sender).
- `DICOM_ROOT_DIR`: Directory containing DICOM files to replay.
- `PEAK_IMAGES_PER_SECOND`: Historical peak rate (images per second).
- `LOAD_MULTIPLIER`: Multiplicative factor for stress testing (for example, 3.0 for TS_04).
- `LOAD_CONCURRENCY`: Number of worker threads.
- `TEST_DURATION_SECONDS`: Duration of each test in seconds.
- `MAX_ERROR_RATE`: Allowed error rate fraction (for example, 0.02).
- `MAX_P95_LATENCY_MS_SHORT`: p95 latency bound for throughput tests (milliseconds).
- `MAX_P95_LATENCY_MS`: p95 latency bound for long stability tests (milliseconds).

You can edit `.env` directly:

```env
COMPASS_HOST=compass-test.example.org
COMPASS_PORT=11112
COMPASS_AE_TITLE=COMPASS_TEST
LOCAL_AE_TITLE=PERF_SENDER

DICOM_ROOT_DIR=/path/to/anonymized/dicom

PEAK_IMAGES_PER_SECOND=50
LOAD_MULTIPLIER=3.0
LOAD_CONCURRENCY=16
TEST_DURATION_SECONDS=60

MAX_ERROR_RATE=0.02
MAX_P95_LATENCY_MS_SHORT=1500
MAX_P95_LATENCY_MS=2000
```

`tests/conftest.py` automatically loads this file using `python-dotenv`.

## Running the tests

### Step 0: Catalog Existing Datasets (Optional)

If you have existing DICOM files you want to analyze before testing:

```bash
# Edit 0_dcm_read_studyids.py to set your input/output paths
python 0_dcm_read_studyids.py
```

This will create a CSV catalog that helps you understand your dataset structure.

### Step 0.5: Organize Files by Study Instance UID (Optional)

If you want to organize your cataloged files into folders grouped by Study Instance UID:

```bash
# Edit 1_dicomsourceval_setup_studies.py to set your CSV path and destination folder
python 1_dicomsourceval_setup_studies.py
```

This will create organized folder structures that can be useful for structured testing scenarios.

### Step 0.75: Create Load Test Data (Optional)

If you want to transform your organized datasets into load test data with updated DICOM tags:

```bash
# Edit 2_dicomsourceeval_create_loadtestdata.py to set your CSV path and folder paths
python 2_dicomsourceeval_create_loadtestdata.py
```

This will create load test datasets with updated metadata, ready for performance testing.

### Step 1: Generate Sample DICOM Files

First, generate diverse DICOM sample files:

```bash
python3 create_diverse_dicom_samples.py
```

This creates a comprehensive set of DICOM files in `dicom_samples/` with descriptive filenames.

### Step 2: Configure Environment

Create a `.env` file in the project root (or use environment variables). The tests will use defaults if no `.env` file exists:

```env
COMPASS_HOST=127.0.0.1
COMPASS_PORT=11112
COMPASS_AE_TITLE=COMPASS
LOCAL_AE_TITLE=PERF_SENDER

DICOM_ROOT_DIR=./dicom_samples

PEAK_IMAGES_PER_SECOND=50
LOAD_MULTIPLIER=3.0
LOAD_CONCURRENCY=8
TEST_DURATION_SECONDS=60

MAX_ERROR_RATE=0.02
MAX_P95_LATENCY_MS_SHORT=1500
MAX_P95_LATENCY_MS=2000
```

**Important:** Make sure `COMPASS_HOST` and `COMPASS_PORT` point to your actual Compass server, or the tests will fail when trying to connect.

### Step 3: Run the Tests

From the project root, use Python module syntax (recommended):

```bash
# Run all load tests (use python3 on Mac/Linux, python on Windows)
python3 -m pytest -m load -vv

# Or on Windows PowerShell:
python -m pytest -m load -vv
```

**Note:** If the `pytest` command doesn't work in your terminal, always use `python -m pytest` or `python3 -m pytest` instead.

**Alternative: Use the test runner script:**
```bash
# Run all load tests
python3 run_tests.py

# Quick test (10 seconds)
python3 run_tests.py --quick

# Run only stability test
python3 run_tests.py --stability

# Run only throughput test
python3 run_tests.py --throughput
```

This runs the tests marked with `@pytest.mark.load`, which include:

- `test_load_stability_3x_peak` - Load stability test at 3x peak
- `test_routing_throughput_under_peak_plus` - Throughput tests at 150% and 200% of peak (runs twice)

### Step 4: Override Settings (Optional)

You can override specific settings at runtime by exporting environment variables before running pytest:

```bash
# Quick test with shorter duration
export TEST_DURATION_SECONDS=10
export LOAD_CONCURRENCY=4
python3 -m pytest -m load -vv

# Or run a specific test
python3 -m pytest tests/test_load_stability.py::test_load_stability_3x_peak -vv
```

### Running Individual Tests

```bash
# Just the load stability test
python3 -m pytest tests/test_load_stability.py -vv

# Just the throughput test
python3 -m pytest tests/test_routing_throughput.py -vv

# With verbose output to see what's happening
python3 -m pytest -m load -vv -s
```

## Scaling to long soak tests

For a TS_04-style 48-hour stability run:

```bash
export TEST_DURATION_SECONDS=172800
export LOAD_MULTIPLIER=3.0
pytest tests/test_load_stability.py::test_load_stability_3x_peak -vv
```

It is recommended to run long tests in a dedicated staging environment and monitor Compass server metrics (CPU, memory, disk, and Lighthouse alerts) in parallel.

## Notes

- This suite focuses on non-functional behavior: throughput, latency, and stability.
- Functional validation of routing rules (AE Title, DICOM tags, time-based rules, tag coercion) should be covered in separate test cases built on top of the same sender and dataset loader.
