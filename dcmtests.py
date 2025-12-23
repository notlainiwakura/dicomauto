"""
DICOM test and element extraction utilities.

This script provides functions for extracting DICOM elements and converting
DICOM datasets to dictionary structures for testing and analysis.

NOTE: This script was created early in the project as a testing utility for
extracting and examining DICOM elements. It was useful for understanding
DICOM structure and debugging metadata issues before building the performance
testing suite.
"""

from dcmutl import *
import os
import pydicom
from pydicom.datadict import tag_for_keyword
import json

# Note: ds_to_dict is now imported from dcmutl


if __name__ == "__main__":
    # Set your test DICOM directory and output folder here
    # NOTE: Update these paths for your environment
    # Windows network path example (original):
    dicom_dir = r"\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 1.5."
    #dicom_dir = r"\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 2.0."
    # For macOS/Linux, use: dicom_dir = '/path/to/dicom/files'
    # Recommended for this project: dicom_dir = './dicom_samples'
    
    dest_folder = r"\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\Metadata"
    #dest_folder = r"\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\Metadata2"
    # For macOS/Linux, use: dest_folder = '/path/to/output'
    # Recommended for this project: dest_folder = './dicom_elements'
    
    os.makedirs(dest_folder, exist_ok=True)
    dcm_files = get_dcm_files(dicom_dir)
    
    for dcm_file in dcm_files:
        print(f"Processing DICOM file: {dcm_file}")
        get_dicom_elements_file_nested(dcm_file, dest_folder)
        
        # Alternative: Convert to dictionary and save as JSON
        # ds = pydicom.dcmread(dcm_file)
        # ds_dict = ds_to_dict(ds)
        # metadata_file_name = os.path.join(dest_folder, os.path.basename(dcm_file) + "_metadata.txt")
        # with open(metadata_file_name, "w", encoding="utf-8") as f:
        #     json.dump(ds_dict, f, indent=2, ensure_ascii=False)
    
    # Example: Test specific DICOM tag existence
    # dcm_file = r"\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT450 1.5.\sample.dcm"
    # ds = pydicom.dcmread(dcm_file)
    # if (0x0002,0x0003) in ds:
    #     print("Tag 0x0002,0x0003 exists in the DICOM file.")
    # else:
    #     print("Tag 0x0002,0x0003 does not exist in the DICOM file.")

