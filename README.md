# Compass Performance / Load Testing Suite

This project implements a pytest-based performance and load testing suite for Laurel Bridge Compass, aligned with the "UltraRAD to Compass Routing Migration" test plan.

## Contents

- `compass_perf/`
  - `config.py`: Configuration model driven by environment variables or `.env`.
  - `data_loader.py`: Discovers and loads DICOM datasets from a directory.
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

Install dependencies:

```bash
pip install -r requirements.txt
```

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

From the project root:

```bash
pytest -m load -vv
```

This runs the tests marked with `@pytest.mark.load`, which include:

- `test_load_stability_3x_peak`
- `test_routing_throughput_under_peak_plus`

You can override specific settings at runtime by exporting environment variables before running pytest, for example:

```bash
export TEST_DURATION_SECONDS=300
export LOAD_CONCURRENCY=32
pytest -m load -vv
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
