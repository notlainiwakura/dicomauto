# Script created to help with creating DICOM files
# for DICOM@Source evaluation
# This script just loops through and creates a spreadsheet out with Source Path, Source File Name, Source Study Instance UID,
# Source Series Instance UID, Directory Name, and Barcode Value
# This file is later used to just group input studies into folders for further use.
#
# NOTE: This was one of the first scripts created for this project, used to catalog and understand
# DICOM datasets before building the performance testing suite. The data_loader.py module later
# evolved from the patterns established here, but this script remains useful for initial dataset
# exploration and cataloging.

from dcmutl import *
import time
import os
import pandas as pd
import gc
from datetime import datetime
from pydicom import dcmread

# Updated columns to include all used fields
columns = ['Source Path', 'Source File Name', 'Source Study Instance UID', 'Source Series Instance UID', 'Directory Name', 'Barcode Value']

# NOTE: Update these paths for your environment
# Windows network path example (original):
input_source_location = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 1.5.'
# For macOS/Linux, use: input_source_location = '/path/to/dicom/files'
# Or use local test directory (recommended for this project):
# input_source_location = './dicom_samples'

output_folder = r'C:\Temp\DICOMSource'
# For macOS/Linux, use: output_folder = '/tmp/DICOMSource' or './output'
# Recommended for this project: output_folder = './output'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Create CSV file with a timestamp and write header
csv_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_path = os.path.join(output_folder, f'StudyInstances_{csv_timestamp}.csv')
with open(csv_path, 'w', newline='') as f:
    pd.DataFrame(columns=columns).to_csv(f, index=False)

if os.path.exists(input_source_location):
    # Loop through items in the network path
    for root, dirs, _ in os.walk(input_source_location):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # For each directory, process and get dicom files in the directory and for each file, get the study instance UID
            print("Processing: " + dir_path)
            dcm_files = get_dcm_files(dir_path)
            for dcm_file in dcm_files:
                try:
                    print("Processing: " + dcm_file)
                    ds = dcmread(dcm_file)
                    study_instance_uid = ds.StudyInstanceUID
                    series_instance_uid = ds.SeriesInstanceUID
                    # Extract barcode value from custom tag [0x2200, 0x0005]
                    try:
                        bar_code_value = ds[0x2200, 0x0005].value
                    except (KeyError, AttributeError):
                        bar_code_value = ""
                    
                    new_data = {
                        'Source Path': dir_path,
                        'Source File Name': dcm_file,
                        'Source Study Instance UID': study_instance_uid,
                        'Source Series Instance UID': series_instance_uid,
                        'Directory Name': dir_name,
                        'Barcode Value': bar_code_value
                    }
                    # Append row to CSV immediately
                    pd.DataFrame([new_data]).to_csv(csv_path, mode='a', header=False, index=False)
                except Exception as e:
                    print(f"Error processing {dcm_file}: {e}")
                # Small delay to reduce CPU usage
                time.sleep(0.1)
                # Encourage garbage collection
                gc.collect()
                # Optional: delay after each directory
                #time.sleep(0.2)

print(f"Processing complete. CSV saved to: {csv_path}")
print(f"Note: You can use 1_dicomsourceval_setup_studies.py to organize files by Study Instance UID using this CSV.")

