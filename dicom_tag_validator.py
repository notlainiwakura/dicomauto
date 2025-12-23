"""
DICOM tag validator script that reads Excel files and validates DICOM metadata
against BigQuery data.

This script processes Excel files containing expected DICOM tag values, fetches
actual values from BigQuery, and performs validation using the validation
functions module.

NOTE: This script was created early in the project to automate DICOM tag validation
workflows. It integrates the BigQuery data fetching and validation functions to
provide comprehensive validation reports. This was essential for ensuring data
quality and correctness before building the performance testing suite.
"""

import os
import pandas as pd
import argparse
from datetime import datetime
from BQData import fetch_and_flatten_bigquery_data
import json
from dcm_tag_validator_functions import *

# Define constants for column indexes
BARCODE_COLUMN = 5
PATIENT_NAME_COLUMN = 6
STUDY_INSTANCE_UID_COLUMN = 58
SPECIMEN_UID_COLUMN = 59


def validate_dicom_tags(input_excel, output_csv):
    """
    Validate DICOM tags by comparing Excel data with BigQuery data.
    
    Args:
        input_excel: Path to input Excel file containing expected values
        output_csv: Path to output CSV file (base name, timestamp will be added)
    """
    # Read the input Excel file
    sheet_name = "Raw Output Data"
    df = pd.read_excel(input_excel, sheet_name=sheet_name, header=None, skiprows=2) # Skip the first 2 rows
    
    # Extract columns 3 through 60
    columns_to_read = df.columns[2:60]
    
    # Add a new column for results if it doesn't exist
    if 'ValidationResult' not in df.columns:
        df['ValidationResult'] = ''
    
    # Initialize high-level and detailed results
    high_level_results = []
    detailed_results = []
    
    # Consolidate logic into a single loop
    for index, row in df.iterrows():
        barcode_value = row.iloc[BARCODE_COLUMN]
        # print(barcode_value)
        
        ## Only validate rows where the barcode value starts with "FF-25-22-A1"
        # if not (pd.notna(barcode_value) and barcode_value.startswith("FF-25-22")): 
        #     continue
        
        if pd.notna(barcode_value):
            # Fetch data from BigQuery using the barcode value
            flattened_data = fetch_and_flatten_bigquery_data(barcode_value)
            
            # print(f"Processing BarcodeValue: {barcode_value}")
            # print(f"Flattened Data: {flattened_data}")
            
            if not flattened_data:
                #print(f"Data is not available for BarcodeValue: {barcode_value}")
                high_level_results.append({"Barcode": barcode_value, "Result": "Fail"})
                continue
            
            # Load the mapping from the JSON file
            mapping_file = os.path.join(os.getcwd(), "key_to_column_mapping.json")
            with open(mapping_file, "r") as f:
                key_to_column_mapping = json.load(f)
            
            # Initialize an error log
            error_log = []
            
            # Remove redundant validation logic and replace it with calls to the imported functions
            validate_row(row, flattened_data, key_to_column_mapping, detailed_results, error_log, barcode_value)
            
            # Ensure the correct barcode_value is used for each result
            current_barcode_value = barcode_value
            
            # Append errors to the ValidationResult column
            if error_log:
                df.at[index, 'ValidationResult'] = "; ".join(error_log)
                high_level_results.append({"Barcode": current_barcode_value, "Result": "Fail"})
            else:
                df.at[index, 'ValidationResult'] = "All Good"
                high_level_results.append({"Barcode": current_barcode_value, "Result": "Pass"})
    
    # Save the updated DataFrame to a CSV file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    high_level_file = f"ValidationResults_{timestamp}.csv"
    detailed_file = f"ValidationResultDetails_{timestamp}.csv"
    
    # Write high-level results
    high_level_df = pd.DataFrame(high_level_results)
    high_level_df.to_csv(high_level_file, index=False)
    #print(f"High-level validation results written to {high_level_file}")
    
    # Write detailed results
    detailed_df = pd.DataFrame(detailed_results)
    detailed_df.to_csv(detailed_file, index=False)
    #print(f"Detailed validation results written to {detailed_file}")


# Example usage
if __name__ == "__main__":
    # NOTE: Update these paths for your environment
    # Example paths (original):
    input_excel = "AutomationLBIngestTesting.xlsx"
    output_csv = "ValidationResults.csv"
    # For your environment, use: input_excel = "./input/AutomationLBIngestTesting.xlsx"
    # output_csv = "./output/ValidationResults.csv"
    
    validate_dicom_tags(input_excel, output_csv)

