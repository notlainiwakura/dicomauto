"""
DICOM tag validation functions for comparing expected values with actual DICOM metadata.

This module provides validation functions for various DICOM tags including patient names,
birth dates, referring physician names, StudyInstanceUIDs, and SpecimenUIDs.

NOTE: This script was created early in the project to validate DICOM metadata against
expected values, typically from Excel spreadsheets or other data sources. It works with
flattened BigQuery data and provides detailed validation results. This was essential for
ensuring data quality and correctness before building the performance testing suite.
"""

import os
import pandas as pd
import argparse
from datetime import datetime
from BQData import fetch_and_flatten_bigquery_data
import json

# Define constants for column indexes
BARCODE_COLUMN = 5
PATIENT_NAME_COLUMN = 6
STUDY_INSTANCE_UID_COLUMN = 58
SPECIMEN_UID_COLUMN = 59


# Function to validate Patient Name
def validate_patient_name(flattened_data, expected_value, detailed_results, error_log, barcode):
    # Compare PatientName components from BigQuery with Excel values
    if pd.notna(expected_value):
        family_name = next((item.get("PatientName.Alphabetic.FamilyName", "") for item in flattened_data), "")
        given_name = next((item.get("PatientName.Alphabetic.GivenName", "") for item in flattened_data), "")
        middle_name = next((item.get("PatientName.Alphabetic.MiddleName", "") for item in flattened_data), "")
        
        # Extract expected components from the Excel value
        name_parts = expected_value.split('^')
        expected_family_name = name_parts[0] if len(name_parts) > 0 else ""
        expected_given_name = name_parts[1] if len(name_parts) > 1 else ""
        expected_middle_name = name_parts[2] if len(name_parts) > 2 else ""
        
        # Normalize None to empty string for all values
        family_name = family_name or ""
        given_name = given_name or ""
        middle_name = middle_name or ""
        expected_family_name = expected_family_name or ""
        expected_given_name = expected_given_name or ""
        expected_middle_name = expected_middle_name or ""
        
        # Compare each component
        if family_name != expected_family_name:
            log_error("PatientName.Alphabetic.FamilyName", expected_family_name, family_name, detailed_results, error_log, barcode)
        else:
            log_success("PatientName.Alphabetic.FamilyName", expected_family_name, family_name, detailed_results, error_log, barcode)
        
        if given_name != expected_given_name:
            log_error("PatientName.Alphabetic.GivenName", expected_given_name, given_name, detailed_results, error_log, barcode)
        else:
            log_success("PatientName.Alphabetic.GivenName", expected_given_name, given_name, detailed_results, error_log, barcode)
        
        if middle_name != expected_middle_name:
            log_error("PatientName.Alphabetic.MiddleName", expected_middle_name, middle_name, detailed_results, error_log, barcode)
        else:
            log_success("PatientName.Alphabetic.MiddleName", expected_middle_name, middle_name, detailed_results, error_log, barcode)


# Function to validate StudyInstanceUID
def validate_study_instance_uid(flattened_data, expected_prefix, detailed_results, error_log, barcode):
    # Capture the distinct actual StudyInstanceUID values
    actual_study_instance_uids = list(set(item.get('StudyInstanceUID', '') for item in flattened_data))
    
    # Check if any StudyInstanceUID starts with the expected prefix
    if not any(str(uid).startswith(str(expected_prefix)) for uid in actual_study_instance_uids):
        log_error("StudyInstanceUID", expected_prefix, actual_study_instance_uids, detailed_results, error_log, barcode)
    else:
        log_success("StudyInstanceUID", expected_prefix, actual_study_instance_uids, detailed_results, error_log, barcode)


# Function to validate SpecimenUID
def validate_specimen_uid(flattened_data, expected_prefix, detailed_results, error_log, barcode):
    # Capture the distinct actual SpecimenUID values
    actual_specimen_uids = list(set(item.get('SpecimenUID', '') for item in flattened_data))
    
    # Check if any SpecimenUID starts with the expected prefix
    if not any(str(uid).startswith(str(expected_prefix)) for uid in actual_specimen_uids):
        log_error("SpecimenUID", expected_prefix, actual_specimen_uids, detailed_results, error_log, barcode)
    else:
        log_success("SpecimenUID", expected_prefix, actual_specimen_uids, detailed_results, error_log, barcode)


def log_error(key, expected, found, detailed_results, error_log, barcode):
    error_message = f"Barcode: {barcode}, Key: {key}, Expected: {expected}, Found: {found}"
    error_log.append(error_message)
    detailed_results.append({
        "Key": key,
        "Expected": expected,
        "Found": found,
        "Result Status": "Fail"
    })


def log_success(key, expected, found, detailed_results, error_log, barcode):
    detailed_results.append({
        "Key": key,
        "Expected": expected,
        "Found": found,
        "Result Status": "Pass"
    })


# Function to compare values
def compare_values(key, expected, found, detailed_results, error_log, barcode):
    # Normalize 'BLANK' to empty string for comparison
    expected = "" if expected == "BLANK" else expected
    found = "" if found == "BLANK" else found
    
    # Normalize None, blank, and NaN to empty string for comparison
    expected = "" if pd.isna(expected) else expected or ""
    found = "" if pd.isna(found) else found or ""
    
    # Debug prints (commented out)
    # print(f"Comparing {key}: Expected: {expected} (type: {type(expected)}), Found: {found} (type: {type(found)})")
    # print(f"String comparison: '{str(found)}' == '{str(expected)}'")
    
    if pd.notna(expected) and str(found) == str(expected):
        log_success(key, expected, found, detailed_results, error_log, barcode)
    else:
        log_error(key, expected, found, detailed_results, error_log, barcode)


# Function to validate a single row
def validate_row(row, flattened_data, key_to_column_mapping, detailed_results, error_log, barcode):
    for key, column_index in key_to_column_mapping.items():
        if column_index is not None:
            expected_value = row.iloc[column_index - 1]
            value = next((item.get(key, "") for item in flattened_data), "")
            
            if key in ["StudyInstanceUID"]:
                validate_study_instance_uid(flattened_data, expected_value, detailed_results, error_log, barcode)
            elif key in ["SpecimenUID"]:
                validate_specimen_uid(flattened_data, expected_value, detailed_results, error_log, barcode)
            elif key.startswith("PatientName"):
                validate_patient_name(flattened_data, expected_value, detailed_results, error_log, barcode)
            elif key == "PatientBirthDate":
                validate_patient_birth_date(flattened_data, expected_value, detailed_results, error_log, barcode)
            elif key.startswith("ReferringPhysicianName"):
                validate_referring_physician_name(flattened_data, expected_value, detailed_results, error_log, barcode)
            else:
                compare_values(key, expected_value, value, detailed_results, error_log, barcode)


# Function to validate PatientBirthDate
def validate_patient_birth_date(flattened_data, expected_value, detailed_results, error_log, barcode):
    if pd.notna(expected_value):
        found_value = next((item.get("PatientBirthDate", "") for item in flattened_data), "")
        
        # Normalize expected and found values to comparable formats
        if isinstance(expected_value, int):
            expected_value = str(expected_value)
        
        if isinstance(found_value, str) and "/" in found_value:
            try:
                found_value = pd.to_datetime(found_value).strftime("%Y%m%d")
            except ValueError:
                pass
        
        # Ensure found_value is converted to YYYYMMDD format if it is a datetime object or string
        try:
            found_value = pd.to_datetime(found_value).strftime("%Y%m%d")
        except (ValueError, TypeError):
            pass
        
        print(f"Validating PatientBirthDate: Expected: {expected_value}, Found: {found_value}")
        print(f"Normalized Expected: {expected_value}, Normalized Found: {found_value}")
        
        if str(found_value) == str(expected_value):
            log_success("PatientBirthDate", expected_value, found_value, detailed_results, error_log, barcode)
        else:
            log_error("PatientBirthDate", expected_value, found_value, detailed_results, error_log, barcode)


# Function to validate Referring Physician Name
def validate_referring_physician_name(flattened_data, expected_value, detailed_results, error_log, barcode):
    # Compare ReferringPhysicianName components from BigQuery with Excel values
    if pd.notna(expected_value):
        family_name = next((item.get("ReferringPhysicianName.Alphabetic.FamilyName", "") for item in flattened_data), "")
        given_name = next((item.get("ReferringPhysicianName.Alphabetic.GivenName", "") for item in flattened_data), "")
        middle_name = next((item.get("ReferringPhysicianName.Alphabetic.MiddleName", "") for item in flattened_data), "")
        
        # Extract expected components from the Excel value
        name_parts = expected_value.split('^')
        expected_family_name = name_parts[0] if len(name_parts) > 0 else ""
        expected_given_name = name_parts[1] if len(name_parts) > 1 else ""
        expected_middle_name = name_parts[2] if len(name_parts) > 2 else ""
        expected_name_prefix = name_parts[3] if len(name_parts) > 3 else ""
        expected_name_suffix = name_parts[4] if len(name_parts) > 4 else ""
        
        # Normalize None to empty string for all values
        family_name = family_name or ""
        given_name = given_name or ""
        middle_name = middle_name or ""
        # Add logic to fetch NamePrefix if needed
        name_prefix = ""
        # Add logic to fetch NameSuffix if needed
        name_suffix = ""
        expected_family_name = expected_family_name or ""
        expected_given_name = expected_given_name or ""
        expected_middle_name = expected_middle_name or ""
        expected_name_prefix = expected_name_prefix or ""
        expected_name_suffix = expected_name_suffix or ""
        
        # Compare each component
        if family_name != expected_family_name:
            log_error("ReferringPhysicianName.Alphabetic.FamilyName", expected_family_name, family_name, detailed_results, error_log, barcode)
        else:
            log_success("ReferringPhysicianName.Alphabetic.FamilyName", expected_family_name, family_name, detailed_results, error_log, barcode)
        
        if given_name != expected_given_name:
            log_error("ReferringPhysicianName.Alphabetic.GivenName", expected_given_name, given_name, detailed_results, error_log, barcode)
        else:
            log_success("ReferringPhysicianName.Alphabetic.GivenName", expected_given_name, given_name, detailed_results, error_log, barcode)
        
        if middle_name != expected_middle_name:
            log_error("ReferringPhysicianName.Alphabetic.MiddleName", expected_middle_name, middle_name, detailed_results, error_log, barcode)
        else:
            log_success("ReferringPhysicianName.Alphabetic.MiddleName", expected_middle_name, middle_name, detailed_results, error_log, barcode)
        
        if name_prefix != expected_name_prefix:
            log_error("ReferringPhysicianName.Alphabetic.NamePrefix", expected_name_prefix, name_prefix, detailed_results, error_log, barcode)
        else:
            log_success("ReferringPhysicianName.Alphabetic.NamePrefix", expected_name_prefix, name_prefix, detailed_results, error_log, barcode)
        
        if name_suffix != expected_name_suffix:
            log_error("ReferringPhysicianName.Alphabetic.NameSuffix", expected_name_suffix, name_suffix, detailed_results, error_log, barcode)
        else:
            log_success("ReferringPhysicianName.Alphabetic.NameSuffix", expected_name_suffix, name_suffix, detailed_results, error_log, barcode)

