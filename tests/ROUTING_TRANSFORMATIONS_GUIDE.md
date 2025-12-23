# Routing Transformation Tests Guide

## Overview

The `test_routing_transformations.py` test suite validates that Compass correctly applies transformation rules based on input DICOM attributes and source AE Title.

## Purpose

When DICOM studies are sent to Compass, routing rules may transform certain attributes based on:
- **Source AE Title** - Which system is sending the study
- **Modality** - Type of imaging (CT, MR, OPV, etc.)
- **Series Description** - Description of the imaging series
- **Other DICOM attributes** - Institution, procedure codes, etc.

This test suite ensures these transformations work as expected.

---

## Test Case Structure

Each test case defines:
1. **Input attributes** - What the DICOM file contains when sent
2. **Expected transformations** - What Compass should change
3. **Source AE Title** - Which system is sending

---

## Example Test Case

```python
{
    'name': 'OPV_GPA_VisualFields',
    'description': 'OPV modality with GPA series description should set Visual Fields study description',
    'aet': 'ULTRA_MCR_FORUM',
    'input': {
        'modality': 'OPV',
        'series_description': 'GPA',
    },
    'expected': {
        'study_description': 'Visual Fields (VF) GPA',
    }
}
```

**What this tests:**
- When a study with `Modality=OPV` and `SeriesDescription=GPA` is sent from AE Title `ULTRA_MCR_FORUM`
- Compass should set `StudyDescription='Visual Fields (VF) GPA'`

---

## Adding New Test Cases

### Step 1: Define Your Test Case

Add to the `TRANSFORMATION_TEST_CASES` list in `test_routing_transformations.py`:

```python
TRANSFORMATION_TEST_CASES = [
    # ... existing test cases ...
    {
        'name': 'CT_Brain_Protocol',  # Unique identifier
        'description': 'CT Brain imaging should use standard brain protocol description',
        'aet': 'CT_SCANNER_1',  # Source AE Title
        'input': {
            'modality': 'CT',
            'series_description': 'BRAIN',
            'institution_name': 'TEST HOSPITAL',
        },
        'expected': {
            'study_description': 'CT Brain Protocol',
            'procedure_code_sequence': '12345',  # If applicable
        }
    },
]
```

### Step 2: Run the Test

```bash
# Run all transformation tests
pytest tests/test_routing_transformations.py::test_routing_transformation -v -s

# Run specific test case
pytest tests/test_routing_transformations.py::test_routing_transformation[CT_Brain_Protocol] -v -s

# See summary of all test cases
pytest tests/test_routing_transformations.py::test_all_transformations_summary -v -s
```

### Step 3: Verify Results

The test will output:
```
===========================================================
TEST CASE: CT_Brain_Protocol
===========================================================
Description: CT Brain imaging should use standard brain protocol description

[CONFIGURATION]
  Source AE Title: CT_SCANNER_1

[INPUT ATTRIBUTES]
  Modality: CT
  SeriesDescription: BRAIN
  InstitutionName: TEST HOSPITAL

[EXPECTED TRANSFORMATIONS]
  StudyDescription: 'CT Brain Protocol'
  ProcedureCodeSequence: '12345'

[TEST IDENTIFIERS]
  StudyInstanceUID: 1.2.840.113619.2.55.3.1234567890.123
  SeriesInstanceUID: 1.2.840.113619.2.55.3.1234567890.124
  SOPInstanceUID: 1.2.840.113619.2.55.3.1234567890.125

[STEP 1: SENDING TO COMPASS]
  Compass Host: 129.176.169.25
  Compass Port: 11112
  Status: SUCCESS
  Latency: 45.23ms

[STEP 2: VERIFICATION]
  Manual verification required:
  1. Query Compass for StudyInstanceUID: 1.2.840.113619.2.55.3.1234567890.123
  2. Verify the following transformations were applied:
     - StudyDescription = 'CT Brain Protocol'
     - ProcedureCodeSequence = '12345'

[RESULT: SEND SUCCESSFUL - MANUAL VERIFICATION PENDING]
```

---

## Available DICOM Attributes

You can use any DICOM attribute in `input` or `expected` sections. Use **snake_case** format:

| Snake Case | DICOM Attribute | Example |
|------------|-----------------|---------|
| `modality` | Modality | `'CT'` |
| `series_description` | SeriesDescription | `'BRAIN'` |
| `study_description` | StudyDescription | `'CT Head'` |
| `institution_name` | InstitutionName | `'Hospital Name'` |
| `referring_physician_name` | ReferringPhysicianName | `'Dr. Smith'` |
| `patient_id` | PatientID | `'12345'` |
| `accession_number` | AccessionNumber | `'ACC001'` |
| `procedure_code_sequence` | ProcedureCodeSequence | `'70450'` |

---

## Running Tests

### Run All Transformation Tests
```bash
pytest tests/test_routing_transformations.py -v -s
```

### Run Specific Test Case
```bash
pytest tests/test_routing_transformations.py::test_routing_transformation[OPV_GPA_VisualFields] -v -s
```

### See Test Summary
```bash
pytest tests/test_routing_transformations.py::test_all_transformations_summary -v -s
```

### Run Only Integration Tests
```bash
pytest tests/ -m integration -v
```

---

## Configuration

Set your Compass connection in `.env`:

```env
COMPASS_HOST=129.176.169.25
COMPASS_PORT=11112
COMPASS_AE_TITLE=COMPASS
LOCAL_AE_TITLE=TEST_SENDER  # Will be overridden by test case 'aet'
```

**Note:** The `LOCAL_AE_TITLE` in `.env` is the default, but each test case can override it using the `'aet'` field.

---

## Manual Verification Steps

Since automated verification requires C-FIND support, follow these steps after running tests:

1. **Note the StudyInstanceUID** from test output
2. **Query Compass** using your PACS viewer or DICOM query tool
3. **Verify transformations** match expected values
4. **Document results** in test tracking system

---

## Automated Verification (Future Enhancement)

To enable automated verification, implement the `query_and_verify()` function in `test_routing_transformations.py`.

Requirements:
- Compass must support C-FIND queries
- Add Query/Retrieve presentation contexts
- Implement StudyRootQueryRetrieveInformationModelFind

Example implementation is commented out in the test file.

---

## Test Case Examples

### Visual Fields Test (OPV Modality)
```python
{
    'name': 'OPV_GPA_VisualFields',
    'aet': 'ULTRA_MCR_FORUM',
    'input': {'modality': 'OPV', 'series_description': 'GPA'},
    'expected': {'study_description': 'Visual Fields (VF) GPA'}
}
```

### CT Brain Protocol
```python
{
    'name': 'CT_Brain_Standard',
    'aet': 'CT_SCANNER_1',
    'input': {'modality': 'CT', 'series_description': 'BRAIN'},
    'expected': {'study_description': 'CT Brain Protocol'}
}
```

### MR Spine Routing
```python
{
    'name': 'MR_Spine_Routing',
    'aet': 'MR_SCANNER_A',
    'input': {
        'modality': 'MR',
        'series_description': 'T2 SPINE',
        'body_part_examined': 'SPINE'
    },
    'expected': {
        'study_description': 'MR Spine T2 Weighted',
        'series_description': 'Sagittal T2'
    }
}
```

---

## Troubleshooting

### Test Fails at Send Step
- Check Compass connection in `.env`
- Verify Compass is running and accessible
- Check AE Title is recognized by Compass

### Cannot Verify Transformations
- Query Compass PACS directly using StudyInstanceUID from test output
- Use DICOM viewer or query tool (e.g., dcmtk's `findscu`)
- Check Compass routing rules configuration

### Need Different Source AE Title
- Update the `'aet'` field in your test case
- Ensure Compass recognizes this AE Title

---

## Best Practices

1. **One transformation rule per test case** - Keep test cases focused
2. **Descriptive names** - Use clear, meaningful test case names
3. **Document expected behavior** - Write good descriptions
4. **Test edge cases** - Include unusual modality/description combinations
5. **Group related tests** - Use similar naming for related transformations
6. **Verify manually** - Until automated verification is implemented

---

## Integration with CI/CD

Add to your test pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Transformation Tests
  run: |
    pytest tests/test_routing_transformations.py -v --tb=short
  env:
    COMPASS_HOST: ${{ secrets.COMPASS_HOST }}
    COMPASS_PORT: ${{ secrets.COMPASS_PORT }}
```

**Note:** These tests require a running Compass instance, so they're best suited for:
- Integration test environments
- Scheduled regression tests
- Pre-release validation

---

## Future Enhancements

- [ ] Automated verification via C-FIND queries
- [ ] Load test cases from CSV/JSON file
- [ ] Take screenshots of Compass PACS for documentation
- [ ] Compare before/after DICOM dumps
- [ ] Integration with Compass API for verification
- [ ] Test case generator UI

