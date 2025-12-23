import zipfile
from dcmutl import *
import time
import os
import pandas as pd

if __name__ == "__main__":
    heme_fish_folder = r'\\mfad.mfroot.org\rchapp\NEON\Neon_Test\Techcyte_Uploader\archive\25-21723_CLLDF'
    dcm_files = get_dcm_files(heme_fish_folder)
    file_counter = 1

    print('The number of dcm files is: ' + str(len(dcm_files)))

    for dcm_file in dcm_files:
        metadata_file_name = os.path.basename(dcm_file) + "_metadata" + ".txt"
        metadata_folder = r'\\mfad.mfroot.org\rchapp\NEON\Neon_Test\Techcyte_Uploader\archive\Metadata'
        get_dicom_dataset(dcm_file, metadata_folder, metadata_file_name)
        file_counter = file_counter + 1

