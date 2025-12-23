# tests/test_anonymize_and_send.py

"""
Test case: Anonymize and send single DICOM file to Compass

This test validates the end-to-end workflow:
1. Anonymize a non-anonymized DICOM file
2. Send it to Compass via C-STORE
3. Verify successful transmission
"""

import os
import shutil
import tempfile
from datetime import datetime
from typing import Tuple

import pytest
from pydicom import dcmread
from pydicom.uid import generate_uid


def generate_accession_number() -> str:
    """Generate a unique accession number based on current timestamp."""
    now = datetime.now()
    microseconds = now.microsecond
    return f"{now.strftime('%Y%m%d-%H%M%S')}-{microseconds:06d}"


def update_tag_recursively(ds, tag_tuple: Tuple, value, vr: str = None) -> int:
    """
    Recursively update a tag in the dataset and all nested sequences.
    
    Args:
        ds: pydicom Dataset object
        tag_tuple: Tuple of (group, element) for the tag
        value: Value to set for the tag
        vr: Value Representation (e.g., 'PN', 'LO', 'DA')
        
    Returns:
        Count of how many times the tag was updated
    """
    count = 0
    
    if tag_tuple in ds:
        ds[tag_tuple].value = value
        count += 1
    
    for elem in ds:
        if elem.VR == "SQ" and elem.value:
            for seq_item in elem.value:
                count += update_tag_recursively(seq_item, tag_tuple, value, vr)
    
    return count


def anonymize_dicom_file(input_file: str, output_file: str) -> Tuple[bool, str, dict]:
    """
    Anonymize a DICOM file by updating all PHI tags.
    
    Returns:
        Tuple of (success, message, new_uids_dict)
    """
    try:
        print(f"\n{'='*60}")
        print("STEP 1: ANONYMIZING DICOM FILE")
        print(f"{'='*60}")
        
        ds = dcmread(input_file)
        print(f"  [OK] File read successfully: {os.path.basename(input_file)}")
        
        # Generate new unique identifiers
        new_study_uid = generate_uid()
        new_accession_number = generate_accession_number()
        new_series_uid = generate_uid()
        new_sop_instance_uid = generate_uid()
        
        print(f"  [OK] Generated new StudyInstanceUID: {new_study_uid}")
        
        # Update UIDs (including nested sequences)
        if (0x0020, 0x000d) not in ds:
            ds.add_new((0x0020, 0x000d), 'UI', new_study_uid)
        update_tag_recursively(ds, (0x0020, 0x000d), new_study_uid, 'UI')
        
        if (0x0008, 0x0050) not in ds:
            ds.add_new((0x0008, 0x0050), 'SH', new_accession_number)
        update_tag_recursively(ds, (0x0008, 0x0050), new_accession_number, 'SH')
        
        if (0x0020, 0x000e) not in ds:
            ds.add_new((0x0020, 0x000e), 'UI', new_series_uid)
        update_tag_recursively(ds, (0x0020, 0x000e), new_series_uid, 'UI')
        
        if (0x0008, 0x0018) not in ds:
            ds.add_new((0x0008, 0x0018), 'UI', new_sop_instance_uid)
        update_tag_recursively(ds, (0x0008, 0x0018), new_sop_instance_uid, 'UI')
        
        # Anonymize patient demographics
        if (0x0010, 0x0020) not in ds:
            ds.add_new((0x0010, 0x0020), 'LO', "11043207")
        update_tag_recursively(ds, (0x0010, 0x0020), "11043207", 'LO')
        
        if (0x0010, 0x0010) not in ds:
            ds.add_new((0x0010, 0x0010), 'PN', "ZZTESTPATIENT^ANONYMIZED")
        update_tag_recursively(ds, (0x0010, 0x0010), "ZZTESTPATIENT^ANONYMIZED", 'PN')
        
        if (0x0010, 0x0030) not in ds:
            ds.add_new((0x0010, 0x0030), 'DA', "19010101")
        update_tag_recursively(ds, (0x0010, 0x0030), "19010101", 'DA')
        
        if (0x0008, 0x0080) not in ds:
            ds.add_new((0x0008, 0x0080), 'LO', "TEST FACILITY")
        update_tag_recursively(ds, (0x0008, 0x0080), "TEST FACILITY", 'LO')
        
        if (0x0008, 0x0090) not in ds:
            ds.add_new((0x0008, 0x0090), 'PN', "TEST^PROVIDER")
        update_tag_recursively(ds, (0x0008, 0x0090), "TEST^PROVIDER", 'PN')
        
        # Save anonymized file
        ds.save_as(output_file, write_like_original=False)
        print(f"  [OK] Anonymized file saved")
        
        new_uids = {
            'study_uid': new_study_uid,
            'accession_number': new_accession_number,
            'series_uid': new_series_uid,
            'sop_instance_uid': new_sop_instance_uid
        }
        
        return True, "Successfully anonymized", new_uids
        
    except Exception as e:
        return False, f"Error during anonymization: {e}", {}


@pytest.fixture
def temp_anonymized_file(dicom_files):
    """
    Fixture that creates an anonymized copy of the first DICOM file.
    Cleans up after test completes.
    """
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="test_anon_")
    anonymized_path = os.path.join(temp_dir, "anonymized.dcm")
    
    # Anonymize the first file
    success, message, uids = anonymize_dicom_file(str(dicom_files[0]), anonymized_path)
    
    if not success:
        shutil.rmtree(temp_dir)
        pytest.fail(f"Failed to create anonymized file: {message}")
    
    yield anonymized_path, uids
    
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.mark.integration
def test_anonymize_and_send_single_file(
    temp_anonymized_file,
    compass_config,
    send_dicom_func
):
    """
    Integration test: Anonymize a file and send to Compass.
    
    This test validates:
    - Anonymization removes/replaces PHI correctly
    - Compass accepts the anonymized file
    - Transmission completes successfully
    """
    anonymized_path, new_uids = temp_anonymized_file
    
    print(f"\n{'='*60}")
    print("STEP 2: SENDING TO COMPASS SERVER")
    print(f"{'='*60}")
    
    # Load and verify the anonymized dataset
    print(f"  Loading anonymized file...")
    ds = dcmread(anonymized_path)
    
    # Verify anonymization was successful
    assert str(ds.StudyInstanceUID) == new_uids['study_uid'], "StudyInstanceUID mismatch"
    assert str(ds.PatientName) == "ZZTESTPATIENT^ANONYMIZED", "PatientName not anonymized"
    assert str(ds.PatientID) == "11043207", "PatientID not anonymized"
    print(f"  [OK] Anonymization verified: StudyUID={ds.StudyInstanceUID}")
    
    # Get Compass configuration from fixture
    print(f"  Target: {compass_config['host']}:{compass_config['port']}")
    
    # Create a temporary directory for this send operation
    temp_send_dir = tempfile.mkdtemp(prefix="test_send_")
    try:
        # Copy anonymized file to a temporary folder (send_dicom expects directory)
        temp_file = os.path.join(temp_send_dir, "anonymized.dcm")
        shutil.copy(anonymized_path, temp_file)
        
        # Send to Compass using fixture function
        print("  Sending via C-STORE...")
        send_dicom_func(compass_config['host'], compass_config['port'], temp_send_dir)
        
        print(f"\n{'='*60}")
        print("STEP 3: VERIFYING SUCCESS")
        print(f"{'='*60}")
        print("  [OK] Send completed without errors")
        print("\n  [SUCCESS] ALL STEPS COMPLETED")
        
    finally:
        # Cleanup temp send directory
        if os.path.exists(temp_send_dir):
            shutil.rmtree(temp_send_dir)


@pytest.mark.integration
@pytest.mark.parametrize("input_file_env_var", ["TEST_DICOM_FILE"])
def test_anonymize_and_send_from_shared_drive(
    compass_config,
    send_dicom_func,
    input_file_env_var: str,
):
    """
    Integration test using a file path from environment variable.
    
    Usage:
        export TEST_DICOM_FILE="/path/to/shared/drive/image.dcm"
        pytest tests/test_anonymize_and_send.py::test_anonymize_and_send_from_shared_drive -v -s
    
    This test is useful for testing with specific files from network shares.
    """
    input_file = os.getenv(input_file_env_var)
    
    if not input_file:
        pytest.skip(f"Environment variable {input_file_env_var} not set")
    
    if not os.path.exists(input_file):
        pytest.fail(f"Input file does not exist: {input_file}")
    
    # Create temp directory for anonymized file
    temp_dir = tempfile.mkdtemp(prefix="test_shared_")
    anonymized_path = os.path.join(temp_dir, "anonymized.dcm")
    
    try:
        # Step 1: Anonymize
        success, message, new_uids = anonymize_dicom_file(input_file, anonymized_path)
        assert success, f"Anonymization failed: {message}"
        
        print(f"\n{'='*60}")
        print("STEP 2: SENDING TO COMPASS SERVER")
        print(f"{'='*60}")
        print(f"  Target: {compass_config['host']}:{compass_config['port']}")
        
        # Send to Compass using fixture function
        print("  Sending via C-STORE...")
        send_dicom_func(compass_config['host'], compass_config['port'], temp_dir)
        
        print(f"\n{'='*60}")
        print("STEP 3: VERIFYING SUCCESS")
        print(f"{'='*60}")
        print("  [OK] Send completed without errors")
        print("\n  [SUCCESS] TEST PASSED")
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

