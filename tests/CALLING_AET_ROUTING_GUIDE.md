# Calling AE Title Routing Tests Guide

## Overview

The `test_calling_aet_routing.py` test suite validates that Compass correctly accepts and processes DICOM studies from different calling AE Titles (source systems).

## Purpose

The **Calling AE Title** identifies which system is sending DICOM data to Compass. Compass may:
- Apply different routing rules based on source
- Record the calling AET for audit/tracking
- Enforce security policies per source
- Apply source-specific transformations

This test suite ensures all expected sources work correctly.

---

## What is a Calling AE Title?

In DICOM networking:
- **Calling AE Title (Calling AET)** = The sender (e.g., "CT_SCANNER_1")
- **Called AE Title (Called AET)** = The receiver (e.g., "COMPASS")

Think of it like caller ID - Compass needs to know who is sending each study.

---

## Test Suite Structure

### 1. **Individual AET Tests** (`test_calling_aet_routing`)
Tests each calling AE Title independently:
- Sends one study from each source
- Verifies send succeeds
- Documents study UID for verification

### 2. **Batch Test** (`test_multiple_aets_batch_send`)
Tests multiple sources sending together:
- Rotates through calling AETs
- Sends multiple files
- Simulates realistic multi-source environment

### 3. **Unknown AET Test** (`test_unknown_calling_aet`)
Tests Compass behavior with unregistered sources:
- Documents whether Compass accepts or rejects
- No assertion failure - just documents behavior

### 4. **AET + Modality Combinations** (`test_calling_aet_with_modality_combinations`)
Tests all calling AETs with different modalities:
- Validates CT, MR, CR, US, OPV from each source
- Ensures routing works for all combinations

---

## Configuration

### Adding Calling AE Titles

Edit the `CALLING_AET_TEST_CASES` list in `test_calling_aet_routing.py`:

```python
CALLING_AET_TEST_CASES = [
    {
        'name': 'CT_SCANNER_1',      # Test name (no spaces)
        'description': 'CT Scanner Room 1',  # Human-readable
        'aet': 'CT_SCANNER_1',       # Actual AE Title
    },
    {
        'name': 'MR_SCANNER_A',
        'description': 'MR Scanner A - Building 2',
        'aet': 'MR_SCANNER_A',
    },
    # Add your calling AE Titles here...
]
```

---

## Running Tests

### See Summary of All Calling AETs
```bash
pytest tests/test_calling_aet_routing.py::test_all_calling_aets_summary -v -s
```

Output:
```
===========================================================
CALLING AE TITLE TEST SUITE
===========================================================
Total calling AE Titles configured: 5

Calling AE Titles:
1. ULTRA_MCR_FORUM
   Description: Ultra OCT imaging device
2. CT_SCANNER_1
   Description: CT Scanner #1
...
```

---

### Test All Calling AETs
```bash
pytest tests/test_calling_aet_routing.py::test_calling_aet_routing -v -s
```

Output:
```
===========================================================
TEST: Calling AET = ULTRA_MCR_FORUM
===========================================================
Description: Ultra OCT imaging device

[TEST IDENTIFIERS]
  StudyInstanceUID: 1.2.840.113619...
  StudyDescription: AET_TEST_ULTRA_MCR_FORUM
  Calling AE Title: ULTRA_MCR_FORUM

[SENDING]
  From (Calling AET): ULTRA_MCR_FORUM
  To (Called AET): COMPASS
  Host: 129.176.169.25:11112
  Status: SUCCESS
  Latency: 45.23ms

[MANUAL VERIFICATION]
  1. Query Compass for StudyInstanceUID: 1.2.840.113619...
  2. Verify calling AE Title is: ULTRA_MCR_FORUM
  3. Verify study was routed/processed correctly for this source

[RESULT: SEND SUCCESSFUL - MANUAL VERIFICATION PENDING]
```

---

### Test Specific Calling AET
```bash
pytest tests/test_calling_aet_routing.py::test_calling_aet_routing[ULTRA_MCR_FORUM] -v -s
```

---

### Run Batch Test (Multiple AETs)
```bash
pytest tests/test_calling_aet_routing.py::test_multiple_aets_batch_send -v -s
```

Output:
```
===========================================================
BATCH TEST: Multiple Files with Rotating Calling AETs
===========================================================
  Files to send: 10
  Calling AETs: 5

[SENDING]
  [ 1/10] ULTRA_MCR_FORUM      -> OK   (45ms) | StudyUID: 1.2.840...
  [ 2/10] CT_SCANNER_1         -> OK   (32ms) | StudyUID: 1.2.840...
  [ 3/10] MR_SCANNER_A         -> OK   (38ms) | StudyUID: 1.2.840...
  ...

[RESULTS SUMMARY]
  Total sent: 10
  Successful: 10
  Failed: 0

  Sends per calling AET:
    CT_SCANNER_1         : 2/2 succeeded, avg 33ms
    CR_ROOM_1           : 2/2 succeeded, avg 41ms
    MR_SCANNER_A        : 2/2 succeeded, avg 37ms
    ULTRA_MCR_FORUM     : 2/2 succeeded, avg 44ms
    US_PORTABLE         : 2/2 succeeded, avg 29ms

[SUCCESS: All 10 sends completed successfully]
```

---

### Test Unknown Calling AET
```bash
pytest tests/test_calling_aet_routing.py::test_unknown_calling_aet -v -s
```

---

### Test AET + Modality Combinations
```bash
pytest tests/test_calling_aet_routing.py::test_calling_aet_with_modality_combinations -v -s
```

Output:
```
===========================================================
TEST: All Calling AETs with Modality CT
===========================================================
  ULTRA_MCR_FORUM      + CT  -> OK   (45ms)
  CT_SCANNER_1         + CT  -> OK   (32ms)
  MR_SCANNER_A         + CT  -> OK   (38ms)
  CR_ROOM_1           + CT  -> OK   (41ms)
  US_PORTABLE         + CT  -> OK   (29ms)

  Results: 5/5 succeeded for modality CT
```

---

## Manual Verification

After running tests, verify in Compass:

### 1. Query by StudyInstanceUID
Use the StudyInstanceUID printed in test output to find the study in Compass.

### 2. Verify Calling AET
Check that the calling AE Title was recorded correctly:
- In Compass PACS viewer
- In Compass logs
- In database queries

### 3. Verify Routing
Confirm the study was routed according to rules for that calling AET:
- Correct destination
- Correct transformations applied
- Correct workflow assignments

---

## Use Cases

### Test Case 1: Verify All Sources Are Configured
**Goal:** Ensure Compass recognizes all imaging devices

```bash
# Test all calling AETs
pytest tests/test_calling_aet_routing.py::test_calling_aet_routing -v -s
```

**Expected:** All tests pass
**If fails:** Calling AET may not be configured in Compass

---

### Test Case 2: Verify Multi-Source Environment
**Goal:** Test realistic scenario with multiple devices sending

```bash
# Run batch test
pytest tests/test_calling_aet_routing.py::test_multiple_aets_batch_send -v -s
```

**Expected:** All sends succeed, grouped by AET
**If fails:** May indicate routing conflicts or resource issues

---

### Test Case 3: Test Security Policy
**Goal:** Verify Compass rejects unknown sources

```bash
# Test unknown AET
pytest tests/test_calling_aet_routing.py::test_unknown_calling_aet -v -s
```

**Expected:** Depends on Compass security configuration
- **Strict mode:** Should reject unknown AET
- **Open mode:** May accept with default routing

---

### Test Case 4: Test Modality-Specific Routing
**Goal:** Verify CT from Scanner A routes differently than CT from Scanner B

```bash
# Test AET + modality combinations
pytest tests/test_calling_aet_routing.py::test_calling_aet_with_modality_combinations[CT] -v -s
```

**Expected:** All combinations succeed
**Verify manually:** Each AET routes CT studies to correct destination

---

## Configuration

Set Compass connection in `.env`:

```env
COMPASS_HOST=129.176.169.25
COMPASS_PORT=11112
COMPASS_AE_TITLE=COMPASS
LOCAL_AE_TITLE=DEFAULT_AET  # Overridden by tests
```

**Note:** `LOCAL_AE_TITLE` is the default calling AET, but tests override it with specific values from `CALLING_AET_TEST_CASES`.

---

## Adding New Calling AE Titles

### Step 1: Add to Test Cases List

```python
CALLING_AET_TEST_CASES.append({
    'name': 'NEW_DEVICE',           # Unique name
    'description': 'New X-Ray Room 3',  # Description
    'aet': 'XRAY_ROOM_3',           # Actual AE Title
})
```

### Step 2: Run Summary Test

```bash
pytest tests/test_calling_aet_routing.py::test_all_calling_aets_summary -v -s
```

Verify your new AET appears in the list.

### Step 3: Test New AET

```bash
pytest tests/test_calling_aet_routing.py::test_calling_aet_routing[NEW_DEVICE] -v -s
```

### Step 4: Verify in Compass

Query Compass for the StudyInstanceUID from test output and verify calling AET was recorded.

---

## Troubleshooting

### Test Fails: "Send failed from [AET]"
**Cause:** Compass rejected the calling AET

**Solutions:**
1. Verify AET is configured in Compass
2. Check Compass accepts associations from this AET
3. Verify network connectivity
4. Check Compass logs for rejection reason

---

### Test Passes But Can't Find Study in Compass
**Cause:** Study may have been routed to unexpected destination

**Solutions:**
1. Query all Compass destinations
2. Check routing rules for this calling AET
3. Verify study wasn't quarantined
4. Check Compass routing logs

---

### Unknown AET Test Unexpectedly Succeeds
**Cause:** Compass may accept all sources

**Note:** This documents actual behavior
- May be intentional (open configuration)
- May need security review
- Document this finding for Compass administrators

---

### Batch Test Shows Uneven Distribution
**Observation:** Some AETs get more sends than others

**Explanation:** The batch test cycles through AETs
- With 10 files and 5 AETs: each gets 2 sends
- With 11 files and 5 AETs: some get 3, others get 2
- This is expected behavior

---

## Integration with Other Tests

### Combine with Transformation Tests

Test that calling AET affects transformations:

```python
# In test_routing_transformations.py
{
    'name': 'CT_Scanner1_Protocol',
    'aet': 'CT_SCANNER_1',  # Specific calling AET
    'input': {'modality': 'CT'},
    'expected': {'study_description': 'CT from Scanner 1'}
}
```

### Combine with Load Tests

Use different calling AETs in load tests:

```python
# In test_load_stability.py
# Rotate through calling AETs during load test
```

---

## Best Practices

1. **Test all production sources** - Every device that sends to Compass
2. **Test before deployment** - Verify new devices before production
3. **Document routing rules** - Note what each AET should do
4. **Regular regression testing** - Ensure AET routing doesn't break
5. **Monitor for unknown AETs** - Alert when unexpected sources appear

---

## Future Enhancements

- [ ] Automated verification via C-FIND queries
- [ ] Load CSV of calling AE Titles from config file
- [ ] Test concurrent sends from multiple AETs
- [ ] Verify routing destinations automatically
- [ ] Integration with Compass API for verification
- [ ] Performance comparison across different calling AETs

---

## Example Test Output

```bash
$ pytest tests/test_calling_aet_routing.py -v

tests/test_calling_aet_routing.py::test_all_calling_aets_summary PASSED
tests/test_calling_aet_routing.py::test_calling_aet_routing[ULTRA_MCR_FORUM] PASSED
tests/test_calling_aet_routing.py::test_calling_aet_routing[CT_SCANNER_1] PASSED
tests/test_calling_aet_routing.py::test_calling_aet_routing[MR_SCANNER_A] PASSED
tests/test_calling_aet_routing.py::test_calling_aet_routing[CR_ROOM_1] PASSED
tests/test_calling_aet_routing.py::test_calling_aet_routing[US_PORTABLE] PASSED
tests/test_calling_aet_routing.py::test_multiple_aets_batch_send PASSED
tests/test_calling_aet_routing.py::test_unknown_calling_aet PASSED
tests/test_calling_aet_routing.py::test_calling_aet_with_modality_combinations[CT] PASSED
tests/test_calling_aet_routing.py::test_calling_aet_with_modality_combinations[MR] SKIPPED (No MR files)
tests/test_calling_aet_routing.py::test_calling_aet_with_modality_combinations[CR] PASSED
tests/test_calling_aet_routing.py::test_calling_aet_with_modality_combinations[US] SKIPPED (No US files)
tests/test_calling_aet_routing.py::test_calling_aet_with_modality_combinations[OPV] PASSED

========== 11 passed, 2 skipped in 45.23s ==========
```

