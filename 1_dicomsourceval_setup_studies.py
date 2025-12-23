# Given the input dcm file path and study instance UID values, loop through and create a folder
# at the destination and group all the dcm files belonging to the same study together.

# Script created to help with creating DICOM files
# for DICOM@Source evaluation
#
# NOTE: This script was created early in the project, following the cataloging script (0_dcm_read_studyids.py).
# It reads the CSV catalog created by that script and organizes DICOM files into folders grouped by
# Study Instance UID. This organization step was useful for preparing datasets before performance testing.

import zipfile
from dcmutl import *
import time
import os
import pandas as pd
import shutil
import gc

# This is the input image location where images are stored with Study Instance UID folder.
# NOTE: Update these paths for your environment
# Windows network path example (original):
dest_folder = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 1.5.'
# For macOS/Linux, use: dest_folder = '/path/to/destination'
# Recommended for this project: dest_folder = './organized_studies'

# CSV file created by 0_dcm_read_studyids.py
# Update this to point to your most recent catalog CSV file
input_csv_file = r'C:\Temp\DICOMSource\StudyInstances_20250728_192654.csv'
# For macOS/Linux, use: input_csv_file = './output/StudyInstances_YYYYMMDD_HHMMSS.csv'
# Or find the latest CSV: input_csv_file = './output/StudyInstances_*.csv'

df = pd.read_csv(input_csv_file)

from_row = 0
to_row = df.shape[0] #1

files_dict = {}

for index,row in df[from_row:to_row].iterrows():
    source_file_name = row['Source File Name']
    source_study_inst_id = row['Source Study Instance UID']
    if source_study_inst_id not in files_dict:
        files_dict[source_study_inst_id] = []
    files_dict[source_study_inst_id].append(source_file_name)

# Loop through dictionary and for each Study Instance UID, create a folder under dest_folder
# For each file path for that study instance uid, copy the file to destination.
for file_key in files_dict:
    print("Processing Study Instance UID: " + file_key)
    dest_study_folder = os.path.join(dest_folder, file_key)
    os.makedirs(dest_study_folder, exist_ok=True)
    dcm_files = files_dict[file_key]
    for dcm_file in dcm_files:
        print("Copying file: " + dcm_file)
        shutil.copy(dcm_file, dest_study_folder)
        # Small delay to reduce CPU usage
        time.sleep(0.1)
        # Encourage garbage collection
        gc.collect()

print(f"Processing complete. Files organized by Study Instance UID in: {dest_folder}")
print(f"Note: You can use 2_dicomsourceeval_create_loadtestdata.py to transform these organized files into load test data.")

