import csv
import time
import math
from datetime import datetime, timedelta
from dicomsourceeval_send_dicom_cstore import *
import gc


def perftest(csv_file, total_runtime_seconds, dcm_root_dir):

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=total_runtime_seconds)
    remaining_time = total_runtime_seconds

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        records = list(reader) # Read all rows at once

    # Calculate the initial pacing delay
    total_records = len(records)


    print(f"Starting perftest with total runtime: {total_runtime_seconds} seconds")
    print(f"Total records to process: {total_records}")
    # Only process rows 2 through 5 (1-based, so indices 1 to 4)
    for i, record in enumerate(records, start=1):

        # Process the record (simulated with a print statement for this example)
        print(f"Processing record {i}: {record}")
        dcm_dir_path = os.path.join(dcm_root_dir, record["OutputImageFolderName"])

        # Print the barcode value being sent
        barcode = record.get("BarCodeValue", "<no barcode>")
        print(f"Sending barcode: {barcode}")

        # Determine host and port based on second character of barcode
        if len(barcode) > 1:
            second_char = barcode[1]
        else:
            second_char = ''
        if second_char == 'F':
            host, port = '10.226.12.82', 11112
        elif second_char == 'A':
            host, port = '10.239.12.148', 11112
        else:
            host, port = '129.176.169.25', 11112

        host, port = '129.176.169.25', 11112
        #if barcode == 'CR-25-389-A-1':
        # host, port = '10.146.247.25', 11112
        host, port = '129.176.169.25', 11112
        send_dicom(host, port, dcm_dir_path)

        # Calculate the time left after processing
        elapsed_time = (datetime.now() - start_time).total_seconds()
        remaining_time = total_runtime_seconds - elapsed_time

        # Adjust the pacing delay based on remaining records and time
        remaining_records = total_records - i
        if remaining_records > 0:
            pacing_delay = remaining_time / remaining_records
        else:
            pacing_delay = 0 # No delay needed after the last record

        # Wait for the calculated delay to keep the pacing consistent
        if pacing_delay > 0:
            time.sleep(pacing_delay)

        # Print status for debugging (optional)
        print(f"Remaining time: {remaining_time:.2f} seconds, Pacing delay: {pacing_delay:.2f} second")
        gc.collect()

        # if remaining_time < 0:
        #     break

if __name__ == "__main__":
    print(datetime.now())
    # csv_file = r'C:\Temp\DICOMSource\LoadTestDatatoSend_600.csv'
    csv_file = r'C:\Temp\DICOMSource\Outputs_LoadTest260_20251014.csv'
    #csv_file = r'C:\Temp\DICOMSource\FunctionalAutomationDataToSend.csv'
    # dcm_root_dir = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\G'
    dcm_root_dir = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\GT4'
    # dcm_root_dir = r'\\mfad.mfroot.org\rchapp\Digpath\Drop\TEST-IMAGES\LeicaGT450DICOM\PowerToolsTest\G'
    #dcm_root_dir = r'C:\Temp\DICOMSource\DuplicateScan'
    total_runtime_seconds = 3600
    #total_runtime_seconds = 100
    perftest(csv_file, total_runtime_seconds, dcm_root_dir)
    print("Sending messages complete")
    print(datetime.now())

