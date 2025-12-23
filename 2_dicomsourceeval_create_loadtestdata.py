# Script created to help with creating DICOM files
# for DICOM@Source evaluation.
# Given the input CSV file that contains the BarCodeValue, ContainerIdentifier, Study Instance UID Prefix,
# Series Instance UID Prefix, DeviceSerialNumber, LabelText
# This script creates dicom study folders based on the images in input_images location and copies to
# each study will have the given barcode, and unique study instance UID and Series Instance UID.
# This script generates an Output file with the values of
# BarCodeValue ContainerIdentifier StudyInstanceUIDPrefix SeriesInstanceUIDPrefix StudyInstanceUID
# SeriesInstanceUID OutputImageFolderName
# This output file is later used to send the dicom files to the host and port for LaurelBridge
#
# NOTE: This script was created early in the project workflow, following the cataloging and organization steps.
# It transforms organized DICOM datasets into load test data by updating DICOM tags (StudyInstanceUID,
# SeriesInstanceUID, SOPInstanceUID, etc.) and creating multiple test scenarios. This was essential for
# preparing diverse test datasets before building the automated performance testing suite.

import zipfile
from dcmutl import *
import time
import os
import pandas as pd
import shutil
import gc
from datetime import datetime
from pydicom import dcmread

def generate_unique_id():
    timestamp = time.time_ns()
    timestamp_str = str(timestamp)
    unique_id = timestamp_str
    return unique_id

def get_image_index(n, t):
    if t < n:
        return t
    # Recursively evaluate by subtracting n from t
    return get_image_index(n, t - n)

def get_folders(folder_path):
    # List all folders in the directory and return the full path.
    folders = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    return folders

# CSV file with input parameters
#csv_file = r'C:\Temp\DICOMSource\DicomSourceInputInvalidSerialNumber.csv'
#csv_file = r'C:\Temp\DICOMSource\DicomSourceInputs_FuncAutomation.csv'
# csv_file = r'C:\Temp\DICOMSource\DicomSourceInputs_DuplicateScan.csv'
csv_file = r'C:\Temp\DICOMSource\DicomSourceInputs_LoadTest600_10142025.csv'
# NOTE: Update this path for your environment
# For macOS/Linux, use: csv_file = './input/DicomSourceInputs_LoadTest600.csv'

input_images = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 1.5.'
# NOTE: Update this path for your environment
# For macOS/Linux, use: input_images = '/path/to/input/images'
# Recommended for this project: input_images = './organized_studies'

output_folder = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 2.0.'
#output_folder = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 2.0.'
# NOTE: Update this path for your environment
# For macOS/Linux, use: output_folder = '/path/to/output'
# Recommended for this project: output_folder = './load_test_data'

metadata_folder = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\Metadata'
#metadata_folder = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\Metadata'
# NOTE: Update this path for your environment
# For macOS/Linux, use: metadata_folder = '/path/to/metadata'
# Recommended for this project: metadata_folder = './metadata'

df = pd.read_csv(csv_file)

#add new columns for outputs.
df['StudyInstanceUID'] = 'New StudyInstanceUID'
df['SeriesInstanceUID'] = 'New SeriesInstanceUID'
df['OutputImageFolderName'] = 'New Output Image Folder'

from_row = 0
to_row = df.shape[0] #1
#to_row = 1

image_folders = get_folders(input_images)
image_count = len(image_folders)

print("Number of images is: " + str(image_count))
#print(image_folders)

# Define output CSV path once at the top, before the loop
output_csv_path = os.path.join(output_folder, f'Outputs_incremental_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
# If the file does not exist, write the header first
if not os.path.exists(output_csv_path):
    df.iloc[0:0].to_csv(output_csv_path, mode='w', header=True, index=False)

# loop through csv rows.
# Given row number, get the image index (which image to retrieve?)
#from_row = 132

# from_row = 20
# to_row = 30

for index,row in df[from_row:to_row].iterrows():
    # Only process if both prefixes are present and not empty/NaN
    if not row['StudyInstanceUIDPrefix'] or not row['SeriesInstanceUIDPrefix'] or pd.isna(row['StudyInstanceUIDPrefix']) or pd.isna(row['SeriesInstanceUIDPrefix']):
        print(f"Skipping row {index}: missing StudyInstanceUIDPrefix or SeriesInstanceUIDPrefix")
        continue
    
    # Convert to string, but write blank if value is NaN or empty
    def safe_str(val):
        if pd.isna(val) or val == 'nan':
            return ''
        return str(val)
    
    bar_code_value = safe_str(row['BarCodeValue'])
    container_identifier = safe_str(row['ContainerIdentifier'])
    device_serial_number = safe_str(row['DeviceSerialNumber'])
    label_text = safe_str(row['LabelText'])
    study_instance_uid_prefix = safe_str(row['StudyInstanceUIDPrefix'])
    series_instance_uid_prefix = safe_str(row['SeriesInstanceUIDPrefix'])
    stuunique_id = generate_unique_id()
    study_instance_uid = study_instance_uid_prefix + '.' + stuunique_id
    #time.sleep(1)
    
    series_unique_id = generate_unique_id()
    series_instance_uid = series_instance_uid_prefix + '.' + series_unique_id
    df.at[index, 'StudyInstanceUID'] = study_instance_uid
    df.at[index, 'SeriesInstanceUID'] = series_instance_uid
    
    #Same study instance uid and series instance uid for all images.
    #Unique sop instance uid for each image.
    
    #get the associated image.
    print('image_count is: ' + str(image_count))
    print('index is: ' + str(index))
    image_index = get_image_index(image_count, index)
    print('image index is: ' + str(image_index))
    image_folder = image_folders[image_index]
    print(os.path.basename(image_folder) + "_" + str(index))
    df.at[index, 'OutputImageFolderName'] = os.path.basename(image_folder) + "_" + str(index)
    
    #Copy the image folder to Outputs.
    new_folder = os.path.join(output_folder, os.path.basename(image_folder) + "_" + str(index))
    if os.path.exists(new_folder):
        shutil.rmtree(new_folder)
    shutil.copytree(image_folder, new_folder)
    # Small delay and garbage collection after copying folder
    time.sleep(1)
    gc.collect()
    
    # for all dicom files in the folder, update attributes as needed.
    dcm_files = get_dcm_files(new_folder)
    print('The number of dcm files is: ' + str(len(dcm_files)))
    file_counter = 1
    for dcm_file in dcm_files:
        sop_instance_id = study_instance_uid + '.' + generate_unique_id()
        ds = dcmread(dcm_file)
        update_tags_ds(ds, "BarcodeValue", bar_code_value)
        update_tags_ds(ds, "ContainerIdentifier", container_identifier)
        update_tags_ds(ds, "StudyInstanceUID", study_instance_uid)
        update_tags_ds(ds, "SeriesInstanceUID", series_instance_uid)
        update_tags_ds(ds, "SOPInstanceUID", sop_instance_id)
        update_tags_ds(ds, "DeviceSerialNumber", device_serial_number)
        update_tags_ds(ds, "LabelText", label_text)
        ds.save_as(dcm_file)
        
        #Save metadata.
        metadata_file_name = study_instance_uid + '_' + str(file_counter) + ".txt"
        get_dicom_dataset(dcm_file, metadata_folder, metadata_file_name)
        file_counter = file_counter + 1
        # Small delay and garbage collection after each DICOM file
        time.sleep(1)
        gc.collect()
        
        # Write the updated row to CSV after processing each study (append, no new file each time)
        df.iloc[[index]].to_csv(output_csv_path, mode='a', header=False, index=False)

print(f"Processing complete. Load test data created in: {output_folder}")
print(f"Output CSV saved to: {output_csv_path}")

