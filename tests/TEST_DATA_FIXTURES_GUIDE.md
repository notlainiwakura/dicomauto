# Test Data Fixtures Guide

This guide explains how to use the test data selection fixtures in `conftest.py` for writing effective tests.

## Overview

The framework provides reusable fixtures that intelligently select test data based on various criteria. All fixtures **gracefully skip** tests when required data is not available.

---

## Available Fixtures

### Size-Based Selection

#### `large_dicom_file`
Selects a single large file (>10MB).

```python
def test_large_file(dicom_sender, large_dicom_file, metrics):
    """Test with a large file."""
    ds = load_dataset(large_dicom_file)
    dicom_sender._send_single_dataset(ds, metrics)
```

**Skips if:** No file >10MB found

---

#### `small_dicom_files`
Selects up to 10 small files (<1MB).

```python
def test_batch(dicom_sender, small_dicom_files, metrics):
    """Test with small files."""
    for file in small_dicom_files:
        ds = load_dataset(file)
        dicom_sender._send_single_dataset(ds, metrics)
```

**Skips if:** Fewer than 3 small files available

---

#### `medium_dicom_files`
Selects medium-sized files (1-10MB).

```python
def test_medium_files(dicom_sender, medium_dicom_files, metrics):
    """Test with medium files."""
    # Use first 5 medium files
    for file in medium_dicom_files[:5]:
        ...
```

**Skips if:** No medium files found

---

### Categorical Selection

#### `dicom_by_size_category`
Organizes files into size categories: `small`, `medium`, `large`.

```python
@pytest.mark.parametrize("category", ["small", "medium", "large"])
def test_by_size(dicom_by_size_category, category):
    """Test each size category."""
    files = dicom_by_size_category.get(category, [])
    if not files:
        pytest.skip(f"No {category} files")
    # Test with files from this category
```

**Returns:** `{'small': [...], 'medium': [...], 'large': [...]}`

---

#### `dicom_by_modality`
Organizes files by modality (CT, MR, CR, etc.).

```python
@pytest.mark.parametrize("modality", ["CT", "MR", "CR"])
def test_by_modality(dicom_by_modality, modality):
    """Test each modality."""
    from tests.conftest import get_files_by_modality
    files = get_files_by_modality(dicom_by_modality, modality, count=3)
    # Test with 3 files of this modality
```

**Returns:** `{'CT': [...], 'MR': [...], ...}`

**Helper function:** `get_files_by_modality(dict, modality, count)` - Gracefully skips if modality not available

---

### Simple Selection

#### `single_dicom_file`
Selects any single file - simplest fixture.

```python
def test_basic_send(dicom_sender, single_dicom_file, metrics):
    """Basic smoke test with any file."""
    ds = load_dataset(single_dicom_file)
    dicom_sender._send_single_dataset(ds, metrics)
```

**Skips if:** No files available at all

---

### Parametrizable Selection

#### `dicom_file_subset`
Select N files via parametrization.

```python
@pytest.mark.parametrize("dicom_file_subset", [1, 5, 10], indirect=True)
def test_variable_batch(dicom_file_subset):
    """Test with 1, 5, and 10 files."""
    print(f"Testing with {len(dicom_file_subset)} files")
    # Test logic here
```

**Skips if:** Fewer files than requested count

---

## Usage Patterns

### Pattern 1: Test Across Multiple Modalities

```python
@pytest.mark.integration
@pytest.mark.parametrize("modality", ["CT", "MR", "CR", "US", "XA"])
def test_all_modalities(dicom_sender, dicom_by_modality, modality, metrics):
    """Test sending each modality type."""
    from tests.conftest import get_files_by_modality
    
    # This will skip if modality not available
    files = get_files_by_modality(dicom_by_modality, modality, count=3)
    
    for file in files:
        ds = load_dataset(file)
        dicom_sender._send_single_dataset(ds, metrics)
    
    assert metrics.successes == len(files)
```

**Result:** Creates separate test for each modality; skips those not available.

---

### Pattern 2: Test Different Batch Sizes

```python
@pytest.mark.integration
@pytest.mark.parametrize("dicom_file_subset", [1, 5, 10, 25], indirect=True)
def test_batch_sizes(dicom_sender, dicom_file_subset, metrics):
    """Test with increasing batch sizes."""
    batch_size = len(dicom_file_subset)
    
    for file in dicom_file_subset:
        ds = load_dataset(file)
        dicom_sender._send_single_dataset(ds, metrics)
    
    print(f"Batch {batch_size}: avg latency {metrics.avg_latency_ms:.2f}ms")
```

**Result:** Tests with 1, 5, 10, and 25 files; skips if dataset too small.

---

### Pattern 3: Size-Specific Performance Thresholds

```python
@pytest.mark.integration
def test_latency_by_size(dicom_by_size_category, dicom_sender):
    """Different latency expectations for different sizes."""
    
    thresholds = {
        'small': 1000,   # 1 second max
        'medium': 3000,  # 3 seconds max
        'large': 10000   # 10 seconds max
    }
    
    for category, max_latency_ms in thresholds.items():
        files = dicom_by_size_category.get(category, [])
        if not files:
            continue  # Skip this category
        
        metrics = PerfMetrics()
        for file in files[:3]:  # Test first 3
            ds = load_dataset(file)
            dicom_sender._send_single_dataset(ds, metrics)
        
        assert metrics.avg_latency_ms < max_latency_ms, \
            f"{category}: latency {metrics.avg_latency_ms}ms > {max_latency_ms}ms"
```

---

### Pattern 4: Conditional Testing

```python
@pytest.mark.integration
def test_whatever_is_available(dicom_by_modality, dicom_sender):
    """Adapts to whatever data is present."""
    
    if not dicom_by_modality:
        pytest.skip("No categorizable DICOM files available")
    
    print(f"Testing {len(dicom_by_modality)} available modalities:")
    
    for modality, files in dicom_by_modality.items():
        print(f"  - {modality}: {len(files)} files")
        # Test with first file of each modality
        ds = load_dataset(files[0])
        # ... test logic
```

---

## Graceful Skipping Examples

### Automatic Skipping (Fixture-Level)

```python
def test_with_large_file(large_dicom_file):
    """Fixture automatically skips if no large file."""
    # This only runs if large file is available
    print(f"Testing with: {large_dicom_file.name}")
```

---

### Manual Skipping (Test-Level)

```python
def test_specific_modality(dicom_by_modality):
    """Manual skip for specific requirements."""
    if 'CT' not in dicom_by_modality:
        pytest.skip("This test specifically requires CT files")
    
    ct_files = dicom_by_modality['CT']
    if len(ct_files) < 5:
        pytest.skip("Need at least 5 CT files for this test")
    
    # Test logic here
```

---

### Helper Function Skipping

```python
def test_using_helper(dicom_by_modality):
    """Helper function handles skipping."""
    from tests.conftest import get_files_by_modality
    
    # This will skip if 'MR' not available or fewer than 10 files
    mr_files = get_files_by_modality(dicom_by_modality, 'MR', count=10)
    
    # Test logic here
```

---

## Best Practices

### 1. Use Fixtures for Common Patterns
Don't manually filter files in tests - use fixtures:

**Bad:**
```python
def test_large_files(dicom_files):
    large = [f for f in dicom_files if f.stat().st_size > 10*1024*1024]
    if not large:
        pytest.skip("No large files")
```

**Good:**
```python
def test_large_files(large_dicom_file):
    # Fixture handles filtering and skipping
```

---

### 2. Parametrize for Variations
Test multiple scenarios without duplication:

**Bad:**
```python
def test_ct_files(dicom_by_modality): ...
def test_mr_files(dicom_by_modality): ...
def test_cr_files(dicom_by_modality): ...
```

**Good:**
```python
@pytest.mark.parametrize("modality", ["CT", "MR", "CR"])
def test_modality_files(dicom_by_modality, modality): ...
```

---

### 3. Skip Gracefully
Always explain why a test is skipped:

**Bad:**
```python
if not files:
    pytest.skip("No files")
```

**Good:**
```python
if len(files) < required_count:
    pytest.skip(f"Need {required_count} files, only {len(files)} available. "
                f"Add more files to {data_dir} to run this test.")
```

---

### 4. Document Requirements
Add docstrings explaining what data is needed:

```python
def test_high_resolution_images(large_dicom_file):
    """
    Test high-resolution image handling.
    
    Requirements:
    - At least one DICOM file >10MB in DICOM_ROOT_DIR
    - File should contain pixel data
    
    To enable: Add large DICOM files to your test data directory
    """
```

---

## Running Tests

### Run all tests (skips where data unavailable)
```bash
pytest tests/ -v
```

### See what gets skipped
```bash
pytest tests/ -v -rs
```

### Run only specific category
```bash
pytest tests/ -k "large_file" -v
```

### Run with specific modality parameter
```bash
pytest tests/ -k "CT" -v
```

---

## Configuration

Set your test data location in `.env`:

```env
# Use local samples
DICOM_ROOT_DIR=./dicom_samples

# Or use shared drive
DICOM_ROOT_DIR=X:/TEST/Test Data/Data
```

Organize your data for best coverage:

```
dicom_samples/
  small/          # <1MB files
  medium/         # 1-10MB files
  large/          # >10MB files
  by_modality/
    CT/
    MR/
    CR/
    US/
```

---

## Example Test Suite Output

```
tests/test_data_selection_examples.py::test_send_large_file PASSED
tests/test_data_selection_examples.py::test_send_batch_small_files PASSED
tests/test_data_selection_examples.py::test_send_by_modality[CT] PASSED
tests/test_data_selection_examples.py::test_send_by_modality[MR] SKIPPED (No MR files available)
tests/test_data_selection_examples.py::test_send_by_modality[CR] PASSED
tests/test_data_selection_examples.py::test_send_variable_batch_sizes[1] PASSED
tests/test_data_selection_examples.py::test_send_variable_batch_sizes[5] PASSED
tests/test_data_selection_examples.py::test_send_variable_batch_sizes[10] SKIPPED (Need 10 files, only 7 available)
```

Tests adapt to available data automatically!

