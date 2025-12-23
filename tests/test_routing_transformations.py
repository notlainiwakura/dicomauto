# tests/test_routing_transformations.py

"""
Compass Routing and Transformation Tests

Tests that validate Compass correctly applies transformation rules based on:
- Source AE Title (sending system)
- DICOM attributes (Modality, SeriesDescription, etc.)

These tests send DICOM files with specific attributes and verify that
Compass applies the expected transformations.

NOTE: These tests send to Compass but do not automatically verify the output.
      Manual verification is required unless C-FIND query support is added.
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest

from data_loader import load_dataset
from metrics import PerfMetrics


# ============================================================================
# Test Case Definitions
# ============================================================================

# Define transformation test cases here
# Each test case specifies input attributes and expected output
TRANSFORMATION_TEST_CASES = [
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
    },
    # Add more test cases here following the same pattern:
    # {
    #     'name': 'TestCaseName',
    #     'description': 'Human-readable description',
    #     'aet': 'SOURCE_AE_TITLE',
    #     'input': {
    #         'modality': 'CT',
    #         'series_description': 'BRAIN',
    #         # Add any other DICOM attributes in snake_case
    #     },
    #     'expected': {
    #         'study_description': 'Expected Study Description',
    #         # Add other expected transformations
    #     }
    # },
]


# ============================================================================
# Test Implementation
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("test_case", TRANSFORMATION_TEST_CASES, ids=lambda tc: tc['name'])
def test_routing_transformation(
    test_case: dict,
    test_dicom_with_attributes,
    dicom_sender,
    metrics: PerfMetrics
):
    """
    Test Compass routing transformations based on input attributes.
    
    This test:
    1. Creates a DICOM file with specified input attributes
    2. Sends it to Compass using the specified AE Title
    3. Verifies the send was successful
    4. Documents expected output for manual verification
    
    To add new test cases:
    - Add entries to TRANSFORMATION_TEST_CASES list above
    - Run: pytest tests/test_routing_transformations.py -v
    
    For automated verification (requires C-FIND support):
    - Uncomment the query_and_verify() function below
    - Add C-FIND query implementation
    """
    test_name = test_case['name']
    test_desc = test_case['description']
    
    print(f"\n{'='*70}")
    print(f"TEST CASE: {test_name}")
    print(f"{'='*70}")
    print(f"Description: {test_desc}")
    
    # Create test file with input attributes
    test_file_path, test_dataset = test_dicom_with_attributes(**test_case['input'])
    
    try:
        # Display test configuration
        print(f"\n[CONFIGURATION]")
        print(f"  Source AE Title: {test_case['aet']}")
        print(f"\n[INPUT ATTRIBUTES]")
        for attr_name, attr_value in test_case['input'].items():
            display_name = ''.join(word.capitalize() for word in attr_name.split('_'))
            print(f"  {display_name}: {attr_value}")
        
        print(f"\n[EXPECTED TRANSFORMATIONS]")
        for attr_name, attr_value in test_case['expected'].items():
            display_name = ''.join(word.capitalize() for word in attr_name.split('_'))
            print(f"  {display_name}: '{attr_value}'")
        
        print(f"\n[TEST IDENTIFIERS]")
        print(f"  StudyInstanceUID: {test_dataset.StudyInstanceUID}")
        print(f"  SeriesInstanceUID: {test_dataset.SeriesInstanceUID}")
        print(f"  SOPInstanceUID: {test_dataset.SOPInstanceUID}")
        
        # Override AE title for this test
        original_ae_title = dicom_sender.endpoint.local_ae_title
        dicom_sender.endpoint.local_ae_title = test_case['aet']
        
        try:
            # Send to Compass
            print(f"\n[STEP 1: SENDING TO COMPASS]")
            print(f"  Compass Host: {dicom_sender.endpoint.host}")
            print(f"  Compass Port: {dicom_sender.endpoint.port}")
            
            ds = load_dataset(test_file_path)
            dicom_sender._send_single_dataset(ds, metrics)
            
            # Verify send was successful
            assert metrics.successes == 1, \
                f"Send failed: {metrics.failures} failures, error rate: {metrics.error_rate:.1%}"
            
            print(f"  Status: SUCCESS")
            print(f"  Latency: {metrics.avg_latency_ms:.2f}ms")
            
            # Manual verification instructions
            print(f"\n[STEP 2: VERIFICATION]")
            print(f"  Manual verification required:")
            print(f"  1. Query Compass for StudyInstanceUID: {test_dataset.StudyInstanceUID}")
            print(f"  2. Verify the following transformations were applied:")
            for attr_name, expected_value in test_case['expected'].items():
                display_name = ''.join(word.capitalize() for word in attr_name.split('_'))
                print(f"     - {display_name} = '{expected_value}'")
            
            # TODO: Automated verification via C-FIND
            # Uncomment if C-FIND query support is available:
            # query_and_verify(dicom_sender, test_dataset.StudyInstanceUID, test_case['expected'])
            
            print(f"\n[RESULT: SEND SUCCESSFUL - MANUAL VERIFICATION PENDING]")
            
        finally:
            # Restore original AE title
            dicom_sender.endpoint.local_ae_title = original_ae_title
    
    finally:
        # Cleanup temp file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


# ============================================================================
# Optional: Automated Verification via C-FIND
# ============================================================================

def query_and_verify(dicom_sender, study_uid: str, expected_attributes: dict):
    """
    Query Compass via C-FIND and verify transformations were applied.
    
    NOTE: This requires Compass to support C-FIND queries.
    Uncomment and adapt this function if automated verification is desired.
    
    Args:
        dicom_sender: DicomSender instance
        study_uid: StudyInstanceUID to query
        expected_attributes: Dict of expected attribute values
    """
    print(f"\n  [AUTOMATED VERIFICATION]")
    print(f"  Querying Compass for study: {study_uid}")
    
    # TODO: Implement C-FIND query
    # from pynetdicom import AE, QueryRetrievePresentationContexts
    # from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
    # from pydicom.dataset import Dataset
    
    # ae = AE(ae_title='TEST_QUERY')
    # ae.requested_contexts = QueryRetrievePresentationContexts
    
    # query_ds = Dataset()
    # query_ds.QueryRetrieveLevel = 'STUDY'
    # query_ds.StudyInstanceUID = study_uid
    # query_ds.StudyDescription = ''  # Request this attribute
    
    # assoc = ae.associate(dicom_sender.endpoint.host, dicom_sender.endpoint.port)
    # if assoc.is_established:
    #     responses = assoc.send_c_find(query_ds, StudyRootQueryRetrieveInformationModelFind)
    #     for (status, identifier) in responses:
    #         if status and identifier:
    #             # Verify each expected attribute
    #             for attr_name, expected_value in expected_attributes.items():
    #                 dicom_attr = ''.join(word.capitalize() for word in attr_name.split('_'))
    #                 actual_value = getattr(identifier, dicom_attr, None)
    #                 assert actual_value == expected_value, \
    #                     f"{dicom_attr} mismatch: expected '{expected_value}', got '{actual_value}'"
    #     assoc.release()
    # ae.shutdown()
    
    print(f"  Status: Automated verification not implemented")
    print(f"  Action: Manual verification required")


# ============================================================================
# Summary Test - Run All Transformation Tests
# ============================================================================

@pytest.mark.integration
def test_all_transformations_summary(
    test_dicom_with_attributes,
    dicom_sender,
):
    """
    Summary test that displays all configured transformation test cases.
    
    This test doesn't send anything - it just documents what will be tested.
    Run this first to see what transformation rules are being validated.
    """
    print(f"\n{'='*70}")
    print(f"COMPASS ROUTING TRANSFORMATION TEST SUITE")
    print(f"{'='*70}")
    print(f"\nTotal test cases configured: {len(TRANSFORMATION_TEST_CASES)}")
    print(f"\nTest cases:")
    
    for i, test_case in enumerate(TRANSFORMATION_TEST_CASES, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        print(f"   AE Title: {test_case['aet']}")
        print(f"   Input: {', '.join(f'{k}={v}' for k, v in test_case['input'].items())}")
        print(f"   Expected: {', '.join(f'{k}={v}' for k, v in test_case['expected'].items())}")
    
    print(f"\n{'='*70}")
    print(f"To run all transformation tests:")
    print(f"  pytest tests/test_routing_transformations.py::test_routing_transformation -v")
    print(f"\nTo run a specific test case:")
    print(f"  pytest tests/test_routing_transformations.py::test_routing_transformation[OPV_GPA_VisualFields] -v")
    print(f"{'='*70}\n")


# ============================================================================
# Helper: Add New Test Case Interactively
# ============================================================================

def add_test_case_template():
    """
    Template for adding new test cases.
    
    Copy this structure and add to TRANSFORMATION_TEST_CASES list:
    """
    new_test_case = {
        'name': 'YourTestCaseName',  # Short identifier (no spaces)
        'description': 'Human-readable description of what this tests',
        'aet': 'SOURCE_AE_TITLE',  # The sending AE title
        'input': {
            # Input DICOM attributes (snake_case)
            'modality': 'XX',
            'series_description': 'Description',
            'institution_name': 'Hospital Name',
            # Add more attributes as needed
        },
        'expected': {
            # Expected output after Compass transformation (snake_case)
            'study_description': 'Expected Study Description',
            # Add more expected transformations
        }
    }
    return new_test_case

