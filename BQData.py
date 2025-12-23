"""
BigQuery data fetching and processing utilities for DICOM metadata.

This module provides functions to query Google BigQuery for DICOM metadata,
flatten nested data structures, and export results to JSON files.

NOTE: This script was created early in the project to fetch and process DICOM metadata
from BigQuery databases. It was useful for validating metadata and understanding
data structures before building the performance testing suite.
"""

from google.cloud import bigquery
import json
import os
from datetime import datetime, date


def fetch_bigquery_data(query):
    """
    Fetch data from BigQuery and return it as a list of dictionaries.
    
    Args:
        query (str): SQL query string to execute in BigQuery
        
    Returns:
        list: A list of dictionaries containing the query results
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Execute the query
    query_job = client.query(query)
    
    # Fetch results
    results = []
    for row in query_job:
        row_dict = dict(row)
        
        # Parse JSON strings into Python objects if applicable
        for key, value in row_dict.items():
            if isinstance(value, str):
                try:
                    row_dict[key] = json.loads(value)
                except json.JSONDecodeError:
                    pass # Keep the value as-is if it's not a JSON string
        
        results.append(row_dict)
    
    return results


def flatten_dict(d, parent_key='', sep='.'):
    """
    Recursively flattens a nested dictionary.
    
    Args:
        d (dict): The dictionary to flatten.
        parent_key (str): The base key string for recursion.
        sep (str): Separator to use for flattened keys.
        
    Returns:
        dict: A flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)


def write_to_json_file(data, output_file):
    """
    Write data to a JSON file with pretty formatting.
    
    Args:
        data (list): The data to write.
        output_file (str): The path to the output JSON file.
    """
    import json
    from datetime import date
    
    def custom_serializer(obj):
        if isinstance(obj, date):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4, default=custom_serializer)


def fetch_and_flatten_bigquery_data(barcode_value):
    """
    Fetch data from BigQuery for a given BarcodeValue, flatten it, and return as a list of dictionaries.
    
    Args:
        barcode_value (str): The BarcodeValue to filter the BigQuery data.
        
    Returns:
        list: A list of flattened dictionaries containing the query results.
    """
    # Determine the dataset based on the barcode prefix
    if barcode_value.startswith("AR"):
        dataset = "ml-mps-ad1-dpp-ndsa-ar-t-deb2.phi_ndsa_ar_dicom_stream_us_t.ndsa_ar_dicom_metadata"
    else:
        dataset = "ml-mps-ad1-dpp-ndsa-t-8bb1.phi_ndsa_dicom_stream_us_t.ndsa_dicom_metadataView"
    
    query = f"""
    SELECT
        SOPInstanceUID,
        AccessionNumber,
        InstitutionName,
        ReferringPhysicianName,
        StationName,
        InstitutionalDepartmentName,
        PatientName,
        PatientID,
        PatientBirthDate,
        PatientSex,
        DeviceSerialNumber,
        StudyInstanceUID,
        SeriesInstanceUID,
        AdmissionID,
        ContainerIdentifier,
        SpecimenDescriptionSequence,
        BarcodeValue,
        SpecimenUID,
        OtherPatientIDsSequence
    FROM `{dataset}`
    WHERE BarcodeValue = '{barcode_value}'
    """
    
    # Fetch data from BigQuery
    data = fetch_bigquery_data(query)
    
    # Flatten the data
    flattened_data = [flatten_dict(item) for item in data]
    
    return flattened_data


if __name__ == "__main__":
    # Define the BarcodeValue
    barcode_value = 'FF-25-22-A1-1'
    
    # Fetch and flatten data from BigQuery
    flattened_data = fetch_and_flatten_bigquery_data(barcode_value)
    
    # Write the flattened data to a JSON file
    output_file = os.path.join(os.getcwd(), f"FlattenedData_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
    write_to_json_file(flattened_data, output_file)
    
    print(f"Flattened data written to {output_file}")

