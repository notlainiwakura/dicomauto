# Script created to help with creating DICOM files
# for DICOM@Source evaluation

import zipfile
from dcmutl import *
import time
import os
import pandas as pd
import shutil
from pynetdicom import debug_logger
from pydicom import dcmread
from pynetdicom import AE
from pynetdicom.sop_class import VLWholeSlideMicroscopyImageStorage
from pynetdicom.sop_class import Verification
from pynetdicom.presentation import PresentationContext
from pynetdicom import AllStoragePresentationContexts
from pydicom.uid import (
    ImplicitVRLittleEndian,
    ExplicitVRLittleEndian,
    ExplicitVRBigEndian,
    JPEGBaseline8Bit,  # Updated from JPEGBaseline
    JPEGExtended12Bit,  # Updated from JPEGExtended
    JPEGLossless,
    JPEGLSLossless,
    JPEG2000Lossless,
    JPEG2000
)
import sys
import logging


def send_dicom(host, port, dcm_dir):
    debug_logger()
    pynetdicom_logger = logging.getLogger("pynetdicom")
    log_file = "pynetdicom_debug.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    pynetdicom_logger.addHandler(file_handler)

    # Initialize the Application Entity with a specific AE title
    ae = AE(ae_title='KALYAN_TST_2')

    # transfer_syntaxes = [
    #     '1.2.840.10008.1.2', # Implicit VR Little Endian
    #     '1.2.840.10008.1.2.1', # Explicit VR Little Endian
    #     '1.2.840.10008.1.2.2', # Explicit VR Big Endian
    # ]

    # transfer_syntaxes = [
    #     ImplicitVRLittleEndian
    # ]

    # Add the requested Presentation Context
    #ae.add_requested_context(VLWholeSlideMicroscopyImageStorage, transfer_syntaxes)
    #ae.add_supported_context(VLWholeSlideMicroscopyImageStorage, transfer_syntaxes)

    sop_class_uid = '1.2.840.10008.5.1.4.1.1.77.1.6'

    # transfer_syntax_uids = [
    #     '1.2.840.10008.1.2', # Implicit VR Little Endian
    #     '1.2.840.10008.1.2.1', # Explicit VR Little Endian
    #     '1.2.840.10008.1.2.2', # Explicit VR Big Endian
    #     '1.2.840.10008.1.2.4.50', # JPEG Baseline (Process 1)
    #     '1.2.840.10008.1.2.4.51', # JPEG Extended (Process 2 & 4)
    #     '1.2.840.10008.1.2.4.57', # JPEG Lossless, Non-Hierarchical (Process 14)
    #     '1.2.840.10008.1.2.4.70', # JPEG Lossless, Non-Hierarchical, First-Order Prediction
    #     '1.2.840.10008.1.2.4.80', # JPEG-LS Lossless Image Compression
    #     '1.2.840.10008.1.2.4.90', # JPEG 2000 Lossless
    #     '1.2.840.10008.1.2.4.91', # JPEG 2000
    # ]

    # transfer_syntax_uids = [
    #     '1.2.840.10008.1.2.2',
    #     '1.2.840.10008.1.2.4.50', # JPEG Baseline (Process 1)
    # ]

    # Read the DICOM file
    dicom_dir_path = dcm_dir
    dcm_files = get_dcm_files(dcm_dir)
    for dcm_file in dcm_files:
        print("Processing file: " + dcm_file)
        dataset = dcmread(dcm_file)
        pynetdicom_logger.info("Study Instance UID: " + dataset.StudyInstanceUID)
        pynetdicom_logger.info("Series Instance UID: " + dataset.SeriesInstanceUID)
        pynetdicom_logger.info("Transfer Syntax UID: " + dataset.file_meta.TransferSyntaxUID)
        pynetdicom_logger.info("File: " + dcm_file)
        #pynetdicom_logger.info("Barcode: " + dataset.BarCodeValue)
        print([dataset.file_meta.TransferSyntaxUID])

        presentation_context = PresentationContext()
        presentation_context.abstract_syntax = sop_class_uid
        presentation_context.transfer_syntax = [dataset.file_meta.TransferSyntaxUID]
        ae.requested_contexts = [presentation_context]

        # dataset.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
        # dataset.save_as(r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsT')
        # new_dataset = dcmread(r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\Power')

        #-------COMMENTING FOR TESTING PURPOSES-------
        # Define the target host and port
        target_host = host #'10.146.247.173' # Replace with the actual IP address
        target_port = port #11112 # Replace with the actual port number
        # Establish an association with the target AE
        assoc = ae.associate(target_host, target_port, ae_title = 'COMPASS')
        if assoc.is_established:
            pynetdicom_logger.info("connection established successfully.")
            #sys.exit()
            # Send the DICOM file using the C-STORE service
            status = assoc.send_c_store(dataset)
            # Check the status of the storage request
            if status:
                if status.Status == 0x0000:
                    pynetdicom_logger.info('DICOM file sent successfully.')
                else:
                    pynetdicom_logger.info(f'ERROR --- C-STORE request failed with status: 0x{status.Status:04x}')
            else:
                pynetdicom_logger.info('ERROR --- C-STORE request failed with status: None')
                pynetdicom_logger.info(' ERROR -- Connection timed out or was aborted.')
            # Release the association
            assoc.release()
        else:
            pynetdicom_logger.info(' ERROR -- Failed to establish association with the target AE.')
        # ----------COMMENTING FOR TESTING PURPOSES----------
        # # Add the Verification SOP Class to the requested contexts
        # ae.add_requested_context(VLWholeSlideMicroscopyImageStorage)
        # ae.add_requested_context(Verification)

        # # Attempt to associate with the remote AE
        # assoc = ae.associate(target_host, target_port)

        # if assoc.is_established:
        #     # Send a C-ECHO request to verify communication
        #     status = assoc.send_c_echo()
        #     if status.Status == 0x0000:
        #         print('Verification successful.')
        #     else:
        #         print(f'Verification failed with status: 0x{status.Status:04x}')
        #         assoc.release()
        # else:
        #     print('Failed to establish association with the target AE.')

